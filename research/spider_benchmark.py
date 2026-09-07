from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import statistics
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from app.services.llm import AzureOpenAIProvider, LLMProvider, OllamaProvider
from research.deterministic_solver import RuleBasedDeterministicSolver
from research.experiment import State, query_complexity
from research.spider_official_eval import evaluate_traces

POLICIES = ("P0", "P1", "P2", "P3", "P4", "P5")

@dataclass
class Example:
    question: str
    db_id: str
    gold_sql: str

@dataclass
class Trace:
    question: str
    db_id: str
    policy: str
    actions: list[str] = field(default_factory=list)
    generated_sql: str | None = None
    sql_valid: bool | None = None
    execution_ok: bool | None = None
    evidence_row_count: int | None = None
    evidence_column_count: int | None = None
    evidence_escalated: bool = False
    evidence_reason: str | None = None
    custom_execution_correct: bool = False
    official_execution_correct: bool | None = None
    latency_ms: float = 0.0
    llm_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    termination_reason: str = ""
    error: str | None = None

class SpiderDataset:
    def __init__(self, question_file: Path, database_dir: Path):
        self.question_file = question_file
        self.database_dir = database_dir
        raw = json.loads(question_file.read_text(encoding="utf-8"))
        self.examples = [Example(x["question"], x["db_id"], x["query"]) for x in raw]

    @staticmethod
    def sha256(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                h.update(block)
        return h.hexdigest()

    def checksum_manifest(self) -> dict[str, Any]:
        db_files = sorted(self.database_dir.glob("*/**/*.sqlite")) or sorted(self.database_dir.glob("*.sqlite"))
        return {"question_file": str(self.question_file), "question_sha256": self.sha256(self.question_file), "database_dir": str(self.database_dir), "database_files": {str(p.relative_to(self.database_dir)): self.sha256(p) for p in db_files}}

    def db_path(self, db_id: str) -> Path:
        for path in (self.database_dir / db_id / f"{db_id}.sqlite", self.database_dir / db_id / f"{db_id}.db", self.database_dir / f"{db_id}.sqlite", self.database_dir / f"{db_id}.db"):
            if path.exists(): return path
        raise FileNotFoundError(f"No SQLite database found for db_id={db_id}")

    def schema(self, db_id: str) -> str:
        with sqlite3.connect(self.db_path(db_id)) as con:
            rows = con.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        return "\n".join(sql for _, sql in rows if sql)

class SecondaryExecutionEvaluator:
    """Row-set evaluator retained only as a secondary diagnostic metric."""
    def __init__(self, dataset: SpiderDataset): self.dataset = dataset
    @staticmethod
    def _result(con: sqlite3.Connection, sql: str) -> tuple[list[tuple], list[str]]:
        cur = con.execute(sql); rows = cur.fetchall(); return rows, [d[0] for d in cur.description or []]
    def execute(self, db_id: str, sql: str) -> tuple[bool, str | None, int | None, int | None]:
        try:
            with sqlite3.connect(self.dataset.db_path(db_id)) as con:
                rows, cols = self._result(con, sql)
            return True, None, len(rows), len(cols)
        except Exception as exc:
            return False, str(exc), None, None
    def correct(self, db_id: str, predicted_sql: str | None, gold_sql: str) -> bool:
        if not predicted_sql: return False
        try:
            with sqlite3.connect(self.dataset.db_path(db_id)) as con:
                pred_rows, _ = self._result(con, predicted_sql); gold_rows, _ = self._result(con, gold_sql)
            return sorted(pred_rows, key=repr) == sorted(gold_rows, key=repr)
        except Exception: return False

class BenchmarkEnvironment:
    COSTS = {"retrieve_schema": .02, "deterministic_execute": .05, "generate_sql": .20, "execute_sql": .05, "verify_sql": .12, "repair_sql": .16, "agentic_escalation": .45, "abstain": 0.0}
    def __init__(self, dataset, evaluator, provider, deterministic, max_cost=1.0):
        self.dataset, self.evaluator, self.provider, self.deterministic, self.max_cost = dataset, evaluator, provider, deterministic, max_cost
    def _add_cost(self, trace, action):
        if trace.cost + self.COSTS[action] > self.max_cost:
            trace.termination_reason = "budget_exhausted"; trace.actions.append("abstain"); return False
        trace.cost += self.COSTS[action]; trace.actions.append(action); return True
    def deterministic_sql(self, trace): return self.deterministic.generate(trace.question, trace.db_id)
    def llm_sql(self, trace, schema, repair_reason=None, escalated=False):
        if self.provider is None:
            trace.error = "No LLM provider configured; set LLM_PROVIDER and credentials."; return None
        prompt_schema = schema if not escalated else schema + "\n\nThis is a post-evidence escalation. Re-check joins, filters, grouping, ordering and nested-query semantics before answering."
        result = self.provider.generate_sql(trace.question, prompt_schema, repair_reason=repair_reason)
        trace.llm_calls += 1; trace.input_tokens += result.input_tokens; trace.output_tokens += result.output_tokens
        return result.text
    def execute(self, trace, sql):
        ok, err, nrows, ncols = self.evaluator.execute(trace.db_id, sql)
        trace.execution_ok, trace.evidence_row_count, trace.evidence_column_count = ok, nrows, ncols
        if not ok: trace.error = err
        return ok
    @staticmethod
    def needs_post_evidence_escalation(question, sql, row_count):
        q = question.lower(); s = sql.lower()
        predicate_cues = (" whose ", " with ", " named ", " in ", " from ", " where ", " that ", " for ", " of ")
        structural_cues = ("each", "every", "group", "average", "maximum", "minimum", "highest", "lowest", "most", "least", "before", "after", "between", "compare", "how many")
        missing_predicate = any(cue in f" {q} " for cue in predicate_cues) and not any(k in s for k in (" where ", " join ", " group by ", " having "))
        singleton_risk = row_count is not None and row_count > 1 and any(k in q for k in ("highest", "lowest", "maximum", "minimum", "most", "least", "top"))
        structural_risk = any(k in q for k in structural_cues) and ("group by" not in s and " join " not in s and " where " not in s and "order by" not in s)
        if missing_predicate: return True, "question_predicate_not_reflected"
        if singleton_risk: return True, "multirow_singleton_request"
        if structural_risk: return True, "structural_complexity_not_reflected"
        if row_count == 0 and any(k in q for k in ("who", "which", "what", "name", "names")): return True, "empty_result"
        return False, None
    def run(self, example, policy):
        trace = Trace(example.question, example.db_id, policy); started = time.perf_counter(); schema = self.dataset.schema(example.db_id); sql = None
        try:
            if not self._add_cost(trace, "retrieve_schema"): return trace
            if policy == "P1":
                sql = self.deterministic_sql(trace)
                if sql is not None and self._add_cost(trace, "deterministic_execute"):
                    trace.generated_sql = sql; trace.sql_valid = self.execute(trace, sql)
                else: trace.sql_valid = False
            elif policy in ("P0", "P2", "P3", "P4"):
                use_det = False
                if policy in ("P2", "P3"): use_det = query_complexity(State(example.question)) < .45
                elif policy == "P4":
                    qconf = 1.0 - min(1.0, .5 * min(1.0, len(example.question)/180) + .5 * (.25 if "why" in example.question.lower() else 0.0)); use_det = qconf >= .75
                if policy in ("P2", "P3", "P4") and use_det:
                    sql = self.deterministic_sql(trace)
                    if sql is not None and self._add_cost(trace, "deterministic_execute"):
                        trace.generated_sql = sql; trace.sql_valid = self.execute(trace, sql)
                    else: trace.sql_valid = False
                else:
                    if not self._add_cost(trace, "generate_sql"): return trace
                    sql = self.llm_sql(trace, schema); trace.generated_sql = sql; trace.sql_valid = bool(sql)
                    if sql and self._add_cost(trace, "execute_sql"): self.execute(trace, sql)
            elif policy == "P5":
                sql = self.deterministic_sql(trace)
                if sql is not None and self._add_cost(trace, "deterministic_execute"):
                    trace.generated_sql = sql; trace.sql_valid = self.execute(trace, sql)
                else: trace.sql_valid = False
                escalate, reason = self.needs_post_evidence_escalation(example.question, trace.generated_sql or "", trace.evidence_row_count)
                if trace.execution_ok is False: escalate, reason = True, "execution_failure"
                if escalate:
                    trace.evidence_escalated = True; trace.evidence_reason = reason
                    if not self._add_cost(trace, "generate_sql"): return trace
                    sql = self.llm_sql(trace, schema, escalated=True); trace.generated_sql = sql; trace.sql_valid = bool(sql)
                    if sql and self._add_cost(trace, "execute_sql"): self.execute(trace, sql)
                    if not trace.execution_ok and sql:
                        if self._add_cost(trace, "repair_sql"):
                            repaired = self.llm_sql(trace, schema, repair_reason=trace.error, escalated=True)
                            if repaired:
                                trace.generated_sql = repaired; trace.sql_valid = True
                                if self._add_cost(trace, "execute_sql"): self.execute(trace, repaired)
                if not trace.execution_ok and trace.generated_sql and self._add_cost(trace, "verify_sql"):
                    trace.sql_valid = trace.generated_sql.strip().lower().startswith(("select", "with"))
            else: raise ValueError(f"Unknown policy {policy}")
            if not trace.termination_reason: trace.actions.append("abstain"); trace.termination_reason = "policy_complete"
        except Exception as exc:
            trace.error = str(exc)
            if not trace.termination_reason: trace.termination_reason = "runtime_error"
        finally:
            trace.latency_ms = (time.perf_counter()-started)*1000
            trace.custom_execution_correct = self.evaluator.correct(example.db_id, trace.generated_sql, example.gold_sql)
        return trace

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--questions",type=Path,required=True); ap.add_argument("--database-dir",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); ap.add_argument("--spider-eval-dir",type=Path); ap.add_argument("--tables-file",type=Path); ap.add_argument("--limit",type=int); args=ap.parse_args()
    dataset=SpiderDataset(args.questions,args.database_dir); examples=dataset.examples[:args.limit] if args.limit else dataset.examples
    provider=None; provider_name=os.getenv("LLM_PROVIDER","").lower()
    if provider_name=="ollama": provider=OllamaProvider(os.getenv("OLLAMA_BASE_URL","http://localhost:11434"),os.getenv("OLLAMA_MODEL","llama3.2:1b"))
    elif provider_name=="azure_openai": provider=AzureOpenAIProvider(os.getenv("AZURE_OPENAI_ENDPOINT",""),os.getenv("AZURE_OPENAI_API_KEY",""),os.getenv("AZURE_OPENAI_API_VERSION","2024-10-21"),os.getenv("AZURE_OPENAI_DEPLOYMENT",""))
    evaluator=SecondaryExecutionEvaluator(dataset); deterministic=RuleBasedDeterministicSolver(args.database_dir); env=BenchmarkEnvironment(dataset,evaluator,provider,deterministic); traces=[]
    for example in examples:
        for policy in POLICIES: traces.append(env.run(example,policy))
    payload={"status":"external_benchmark_run","benchmark":"Spider 1.0 development","question_count":len(examples),"policies":list(POLICIES),"provider":provider_name or "none","deterministic_baseline":{"type":"schema_aware_rule_based","gold_mapping":False,"supported_scope":"conservative single-table aggregate/direct/order patterns"},"dataset_manifest":dataset.checksum_manifest(),"secondary_custom_results":summarize(traces,"custom_execution_correct"),"official_spider_execution":None,"traces":[asdict(t) for t in traces],"warning":"Official Spider execution evaluation is primary. The row-set metric is retained only as a secondary diagnostic. Test-suite accuracy is a separate official metric and is not claimed unless its test-suite databases are supplied."}
    if args.spider_eval_dir and args.tables_file:
        official=evaluate_traces(payload,args.database_dir,args.tables_file,args.spider_eval_dir); payload["official_spider_execution"]=official; payload["results"]={}
        for policy in POLICIES:
            rows=[t for t in payload["traces"] if t["policy"]==policy]; n=len(rows); rel=sum(bool(t["official_execution_correct"]) for t in rows)/n if n else 0.0
            payload["results"][policy]={"n":n,"execution_correctness":rel,"coverage":sum(bool(t["generated_sql"]) for t in rows)/n if n else 0.0,"mean_cost":statistics.mean(t["cost"] for t in rows) if rows else None,"median_latency_ms":statistics.median(t["latency_ms"] for t in rows) if rows else None,"mean_llm_calls":statistics.mean(t["llm_calls"] for t in rows) if rows else None,"targets":{str(r):rel>=r for r in (.90,.95,.97,.99)}}
    else: payload["status"]="benchmark_run_without_official_evaluator"; payload["results"]=payload["secondary_custom_results"]
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(payload,indent=2),encoding="utf-8"); print(json.dumps(payload["results"],indent=2))

def summarize(traces,metric="custom_execution_correct",target_reliabilities=(.90,.95,.97,.99)):
    out={}
    for policy in POLICIES:
        rows=[t for t in traces if t.policy==policy]; n=len(rows); rel=sum(bool(getattr(t,metric)) for t in rows)/n if n else 0.0; costs=[t.cost for t in rows]; lats=[t.latency_ms for t in rows]
        out[policy]={"n":n,"execution_correctness":rel,"coverage":sum(bool(t.generated_sql) for t in rows)/n if n else 0.0,"mean_cost":statistics.mean(costs) if costs else None,"median_latency_ms":statistics.median(lats) if lats else None,"p95_latency_ms":sorted(lats)[max(0,min(len(lats)-1,int(.95*len(lats))-1))] if lats else None,"mean_llm_calls":statistics.mean(t.llm_calls for t in rows) if rows else None,"targets":{str(r):rel>=r for r in target_reliabilities}}
    return out

if __name__=="__main__": main()
