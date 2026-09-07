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
from typing import Any, Callable

from app.services.llm import AzureOpenAIProvider, LLMProvider, OllamaProvider
from research.experiment import State, query_complexity

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
    evaluator_correct: bool = False
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
        db_files = sorted(self.database_dir.glob("*/**/*.sqlite"))
        if not db_files:
            db_files = sorted(self.database_dir.glob("*.sqlite"))
        return {
            "question_file": str(self.question_file),
            "question_sha256": self.sha256(self.question_file),
            "database_dir": str(self.database_dir),
            "database_files": {str(p.relative_to(self.database_dir)): self.sha256(p) for p in db_files},
        }

    def db_path(self, db_id: str) -> Path:
        candidates = [
            self.database_dir / db_id / f"{db_id}.sqlite",
            self.database_dir / db_id / f"{db_id}.db",
            self.database_dir / f"{db_id}.sqlite",
            self.database_dir / f"{db_id}.db",
        ]
        for p in candidates:
            if p.exists():
                return p
        raise FileNotFoundError(f"No SQLite database found for db_id={db_id}")

    def schema(self, db_id: str) -> str:
        with sqlite3.connect(self.db_path(db_id)) as con:
            rows = con.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        return "\n".join(sql for _, sql in rows if sql)

class SpiderEvaluator:
    """Execution evaluator. Gold SQL is visible only after the system run."""
    def __init__(self, dataset: SpiderDataset):
        self.dataset = dataset

    @staticmethod
    def _result(con: sqlite3.Connection, sql: str) -> tuple[list[tuple], list[str]]:
        cur = con.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description or []]
        return rows, cols

    def execute(self, db_id: str, sql: str) -> tuple[bool, str | None]:
        try:
            with sqlite3.connect(self.dataset.db_path(db_id)) as con:
                self._result(con, sql)
            return True, None
        except Exception as exc:
            return False, str(exc)

    def correct(self, db_id: str, predicted_sql: str | None, gold_sql: str) -> bool:
        if not predicted_sql:
            return False
        try:
            with sqlite3.connect(self.dataset.db_path(db_id)) as con:
                pred_rows, _ = self._result(con, predicted_sql)
                gold_rows, _ = self._result(con, gold_sql)
            return sorted(pred_rows, key=repr) == sorted(gold_rows, key=repr)
        except Exception:
            return False

class DeterministicSolver:
    """Optional non-LLM baseline supplied as JSONL question->SQL mapping.

    It is intentionally empty unless the user provides a mapping. This prevents
    accidental leakage from Spider gold SQL into the deterministic baseline.
    """
    def __init__(self, path: Path | None):
        self.mapping: dict[str, str] = {}
        if path:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    obj = json.loads(line)
                    self.mapping[obj["question"]] = obj["sql"]

    def generate(self, question: str) -> str | None:
        return self.mapping.get(question)

class BenchmarkEnvironment:
    COSTS = {
        "retrieve_schema": 0.02,
        "deterministic_execute": 0.05,
        "generate_sql": 0.20,
        "execute_sql": 0.05,
        "verify_sql": 0.12,
        "repair_sql": 0.16,
        "agentic_escalation": 0.45,
        "abstain": 0.0,
    }

    def __init__(self, dataset: SpiderDataset, evaluator: SpiderEvaluator, provider: LLMProvider | None, deterministic: DeterministicSolver, max_cost: float = 1.0):
        self.dataset = dataset
        self.evaluator = evaluator
        self.provider = provider
        self.deterministic = deterministic
        self.max_cost = max_cost

    def _add_cost(self, t: Trace, action: str) -> bool:
        c = self.COSTS[action]
        if t.cost + c > self.max_cost:
            t.termination_reason = "budget_exhausted"
            t.actions.append("abstain")
            return False
        t.cost += c
        t.actions.append(action)
        return True

    def deterministic_sql(self, t: Trace) -> str | None:
        return self.deterministic.generate(t.question)

    def llm_sql(self, t: Trace, schema: str, repair_reason: str | None = None, escalated: bool = False) -> str | None:
        if self.provider is None:
            t.error = "No LLM provider configured; set LLM_PROVIDER and credentials."
            return None
        result = self.provider.generate_sql(
            t.question,
            schema if not escalated else schema + "\n\nThis is an escalation. Re-check joins, filters, grouping, ordering and nested-query semantics before answering.",
            repair_reason=repair_reason,
        )
        t.llm_calls += 1
        t.input_tokens += result.input_tokens
        t.output_tokens += result.output_tokens
        return result.text

    def execute(self, t: Trace, sql: str) -> bool:
        ok, err = self.evaluator.execute(t.db_id, sql)
        t.execution_ok = ok
        if not ok:
            t.error = err
        return ok

    def run(self, example: Example, policy: str) -> Trace:
        t = Trace(example.question, example.db_id, policy)
        started = time.perf_counter()
        schema = self.dataset.schema(example.db_id)
        sql: str | None = None
        try:
            # Every policy gets schema access at the same fixed cost. It is not a
            # decision point, so it cannot create an unfair advantage.
            if not self._add_cost(t, "retrieve_schema"):
                return t

            if policy == "P1":
                sql = self.deterministic_sql(t)
                if sql is not None and self._add_cost(t, "deterministic_execute"):
                    t.generated_sql = sql
                    t.sql_valid = self.execute(t, sql)
                else:
                    t.sql_valid = False

            elif policy in ("P0", "P2", "P3", "P4"):
                use_deterministic = policy == "P2" and query_complexity(State(example.question)) < 0.45
                if policy == "P3":
                    use_deterministic = query_complexity(State(example.question)) < 0.45
                if policy == "P4":
                    qconf = 1.0 - min(1.0, 0.5 * min(1.0, len(example.question) / 180) + 0.5 * (0.25 if "why" in example.question.lower() else 0.0))
                    use_deterministic = qconf >= 0.75
                if policy == "P2" and use_deterministic:
                    sql = self.deterministic_sql(t)
                    if sql is not None and self._add_cost(t, "deterministic_execute"):
                        t.generated_sql = sql
                        t.sql_valid = self.execute(t, sql)
                    else:
                        t.sql_valid = False
                else:
                    if not self._add_cost(t, "generate_sql"):
                        return t
                    sql = self.llm_sql(t, schema)
                    t.generated_sql = sql
                    t.sql_valid = bool(sql)
                    if sql and self._add_cost(t, "execute_sql"):
                        self.execute(t, sql)

            elif policy == "P5":
                # Strong pre-P6 reference: cheap deterministic attempt first;
                # only the observed result determines escalation.
                sql = self.deterministic_sql(t)
                if sql is not None and self._add_cost(t, "deterministic_execute"):
                    t.generated_sql = sql
                    t.sql_valid = self.execute(t, sql)
                    if t.execution_ok:
                        pass
                    else:
                        sql = None
                else:
                    t.sql_valid = False
                if not t.execution_ok:
                    if not self._add_cost(t, "generate_sql"):
                        return t
                    sql = self.llm_sql(t, schema)
                    t.generated_sql = sql
                    t.sql_valid = bool(sql)
                    if sql and self._add_cost(t, "execute_sql"):
                        self.execute(t, sql)
                    if not t.execution_ok and sql:
                        if self._add_cost(t, "repair_sql"):
                            repaired = self.llm_sql(t, schema, repair_reason=t.error)
                            if repaired:
                                t.generated_sql = repaired
                                t.sql_valid = True
                                if self._add_cost(t, "execute_sql"):
                                    self.execute(t, repaired)
                if not t.execution_ok and t.generated_sql:
                    if self._add_cost(t, "verify_sql"):
                        # Verification is evaluator-independent: static/execution
                        # evidence only. It never sees gold SQL.
                        t.sql_valid = t.generated_sql.strip().lower().startswith(("select", "with"))

            else:
                raise ValueError(f"Unknown policy {policy}")

            if t.termination_reason == "":
                t.actions.append("abstain")
                t.termination_reason = "policy_complete"
        except Exception as exc:
            t.error = str(exc)
            if not t.termination_reason:
                t.termination_reason = "runtime_error"
        finally:
            t.latency_ms = (time.perf_counter() - started) * 1000
            t.evaluator_correct = self.evaluator.correct(example.db_id, t.generated_sql, example.gold_sql)
        return t

def summarize(traces: list[Trace], target_reliabilities=(0.90, 0.95, 0.97, 0.99)) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for policy in POLICIES:
        rows = [t for t in traces if t.policy == policy]
        correct = sum(t.evaluator_correct for t in rows)
        n = len(rows)
        reliability = correct / n if n else 0.0
        costs = [t.cost for t in rows]
        latencies = [t.latency_ms for t in rows]
        out[policy] = {
            "n": n,
            "execution_correctness": reliability,
            "coverage": sum(bool(t.generated_sql) for t in rows) / n if n else 0.0,
            "mean_cost": statistics.mean(costs) if costs else None,
            "median_latency_ms": statistics.median(latencies) if latencies else None,
            "p95_latency_ms": sorted(latencies)[max(0, min(len(latencies) - 1, int(0.95 * len(latencies)) - 1))] if latencies else None,
            "mean_llm_calls": statistics.mean(t.llm_calls for t in rows) if rows else None,
            "targets": {str(r): (reliability >= r) for r in target_reliabilities},
        }
    return out

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--deterministic-map", type=Path)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    dataset = SpiderDataset(args.questions, args.database_dir)
    examples = dataset.examples[: args.limit] if args.limit else dataset.examples
    provider: LLMProvider | None = None
    provider_name = os.getenv("LLM_PROVIDER", "").lower()
    if provider_name == "ollama":
        provider = OllamaProvider(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), os.getenv("OLLAMA_MODEL", "llama3.2:1b"))
    elif provider_name == "azure_openai":
        provider = AzureOpenAIProvider(os.getenv("AZURE_OPENAI_ENDPOINT", ""), os.getenv("AZURE_OPENAI_API_KEY", ""), os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"), os.getenv("AZURE_OPENAI_DEPLOYMENT", ""))

    evaluator = SpiderEvaluator(dataset)
    env = BenchmarkEnvironment(dataset, evaluator, provider, DeterministicSolver(args.deterministic_map))
    traces: list[Trace] = []
    for ex in examples:
        for policy in POLICIES:
            traces.append(env.run(ex, policy))

    payload = {
        "status": "external_benchmark_run",
        "benchmark": "Spider 1.0 development",
        "question_count": len(examples),
        "policies": list(POLICIES),
        "provider": provider_name or "none",
        "dataset_manifest": dataset.checksum_manifest(),
        "results": summarize(traces),
        "traces": [asdict(t) for t in traces],
        "warning": "This artifact is benchmark evidence only for the exact recorded inputs/configuration; do not generalize beyond the evaluated split.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["results"], indent=2))

if __name__ == "__main__":
    main()
