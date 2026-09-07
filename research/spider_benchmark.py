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
        for path in candidates:
            if path.exists():
                return path
        raise FileNotFoundError(f"No SQLite database found for db_id={db_id}")

    def schema(self, db_id: str) -> str:
        with sqlite3.connect(self.db_path(db_id)) as con:
            rows = con.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
        return "\n".join(sql for _, sql in rows if sql)


class SecondaryExecutionEvaluator:
    """Simple row-set evaluator retained only as a diagnostic secondary metric."""

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

    def __init__(self, dataset: SpiderDataset, evaluator: SecondaryExecutionEvaluator,
                 provider: LLMProvider | None, deterministic: RuleBasedDeterministicSolver,
                 max_cost: float = 1.0):
        self.dataset = dataset
        self.evaluator = evaluator
        self.provider = provider
        self.deterministic = deterministic
        self.max_cost = max_cost

    def _add_cost(self, trace: Trace, action: str) -> bool:
        cost = self.COSTS[action]
        if trace.cost + cost > self.max_cost:
            trace.termination_reason = "budget_exhausted"
            trace.actions.append("abstain")
            return False
        trace.cost += cost
        trace.actions.append(action)
        return True

    def deterministic_sql(self, trace: Trace) -> str | None:
        return self.deterministic.generate(trace.question, trace.db_id)

    def llm_sql(self, trace: Trace, schema: str, repair_reason: str | None = None,
                escalated: bool = False) -> str | None:
        if self.provider is None:
            trace.error = "No LLM provider configured; set LLM_PROVIDER and credentials."
            return None
        result = self.provider.generate_sql(
            trace.question,
            schema if not escalated else schema +
            "\n\nThis is an escalation. Re-check joins, filters, grouping, ordering and nested-query semantics before answering.",
            repair_reason=repair_reason,
        )
        trace.llm_calls += 1
        trace.input_tokens += result.input_tokens
        trace.output_tokens += result.output_tokens
        return result.text

    def execute(self, trace: Trace, sql: str) -> bool:
        ok, err = self.evaluator.execute(trace.db_id, sql)
        trace.execution_ok = ok
        if not ok:
            trace.error = err
        return ok

    def run(self, example: Example, policy: str) -> Trace:
        trace = Trace(example.question, example.db_id, policy)
        started = time.perf_counter()
        schema = self.dataset.schema(example.db_id)
        sql: str | None = None
        try:
            if not self._add_cost(trace, "retrieve_schema"):
                return trace

            if policy == "P1":
                sql = self.deterministic_sql(trace)
                if sql is not None and self._add_cost(trace, "deterministic_execute"):
                    trace.generated_sql = sql
                    trace.sql_valid = self.execute(trace, sql)
                else:
                    trace.sql_valid = False

            elif policy in ("P0", "P2", "P3", "P4"):
                use_deterministic = False
                if policy == "P2":
                    use_deterministic = query_complexity(State(example.question)) < 0.45
                elif policy == "P3":
                    use_deterministic = query_complexity(State(example.question)) < 0.45
                elif policy == "P4":
                    qconf = 1.0 - min(
                        1.0,
                        0.5 * min(1.0, len(example.question) / 180)
                        + 0.5 * (0.25 if "why" in example.question.lower() else 0.0),
                    )
                    use_deterministic = qconf >= 0.75

                if policy in ("P2", "P3", "P4") and use_deterministic:
                    sql = self.deterministic_sql(trace)
                    if sql is not None and self._add_cost(trace, "deterministic_execute"):
                        trace.generated_sql = sql
                        trace.sql_valid = self.execute(trace, sql)
                    else:
                        trace.sql_valid = False
                else:
                    if not self._add_cost(trace, "generate_sql"):
                        return trace
                    sql = self.llm_sql(trace, schema)
                    trace.generated_sql = sql
                    trace.sql_valid = bool(sql)
                    if sql and self._add_cost(trace, "execute_sql"):
                        self.execute(trace, sql)

            elif policy == "P5":
                # Strong pre-P6 reference: deterministic first, then the observed
                # execution result determines whether to escalate to the LLM path.
                sql = self.deterministic_sql(trace)
                if sql is not None and self._add_cost(trace, "deterministic_execute"):
                    trace.generated_sql = sql
                    trace.sql_valid = self.execute(trace, sql)
                else:
                    trace.sql_valid = False
                if not trace.execution_ok:
                    if not self._add_cost(trace, "generate_sql"):
                        return trace
                    sql = self.llm_sql(trace, schema)
                    trace.generated_sql = sql
                    trace.sql_valid = bool(sql)
                    if sql and self._add_cost(trace, "execute_sql"):
                        self.execute(trace, sql)
                    if not trace.execution_ok and sql:
                        if self._add_cost(trace, "repair_sql"):
                            repaired = self.llm_sql(trace, schema, repair_reason=trace.error)
                            if repaired:
                                trace.generated_sql = repaired
                                trace.sql_valid = True
                                if self._add_cost(trace, "execute_sql"):
                                    self.execute(trace, repaired)
                if not trace.execution_ok and trace.generated_sql:
                    if self._add_cost(trace, "verify_sql"):
                        trace.sql_valid = trace.generated_sql.strip().lower().startswith(("select", "with"))
            else:
                raise ValueError(f"Unknown policy {policy}")

            if not trace.termination_reason:
                trace.actions.append("abstain")
                trace.termination_reason = "policy_complete"
        except Exception as exc:
            trace.error = str(exc)
            if not trace.termination_reason:
                trace.termination_reason = "runtime_error"
        finally:
            trace.latency_ms = (time.perf_counter() - started) * 1000
            trace.custom_execution_correct = self.evaluator.correct(
                example.db_id, trace.generated_sql, example.gold_sql
            )
        return trace


def summarize(traces: list[Trace], metric: str = "custom_execution_correct",
              target_reliabilities=(0.90, 0.95, 0.97, 0.99)) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for policy in POLICIES:
        rows = [t for t in traces if t.policy == policy]
        values = [bool(getattr(t, metric)) for t in rows]
        n = len(rows)
        reliability = sum(values) / n if n else 0.0
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
    ap.add_argument("--spider-eval-dir", type=Path)
    ap.add_argument("--tables-file", type=Path)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    dataset = SpiderDataset(args.questions, args.database_dir)
    examples = dataset.examples[: args.limit] if args.limit else dataset.examples
    provider: LLMProvider | None = None
    provider_name = os.getenv("LLM_PROVIDER", "").lower()
    if provider_name == "ollama":
        provider = OllamaProvider(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), os.getenv("OLLAMA_MODEL", "llama3.2:1b"))
    elif provider_name == "azure_openai":
        provider = AzureOpenAIProvider(
            os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            os.getenv("AZURE_OPENAI_API_KEY", ""),
            os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
            os.getenv("AZURE_OPENAI_DEPLOYMENT", ""),
        )

    evaluator = SecondaryExecutionEvaluator(dataset)
    deterministic = RuleBasedDeterministicSolver(args.database_dir)
    env = BenchmarkEnvironment(dataset, evaluator, provider, deterministic)
    traces: list[Trace] = []
    for example in examples:
        for policy in POLICIES:
            traces.append(env.run(example, policy))

    payload = {
        "status": "external_benchmark_run",
        "benchmark": "Spider 1.0 development",
        "question_count": len(examples),
        "policies": list(POLICIES),
        "provider": provider_name or "none",
        "deterministic_baseline": {
            "type": "schema_aware_rule_based",
            "gold_mapping": False,
            "supported_scope": "conservative single-table aggregate/direct/order patterns",
        },
        "dataset_manifest": dataset.checksum_manifest(),
        "secondary_custom_results": summarize(traces, "custom_execution_correct"),
        "official_spider_execution": None,
        "traces": [asdict(t) for t in traces],
        "warning": "Official Spider execution evaluation is primary. The row-set metric is retained only as a secondary diagnostic. Test-suite accuracy is a separate official metric and is not claimed unless its test-suite databases are supplied.",
    }

    if args.spider_eval_dir and args.tables_file:
        official = evaluate_traces(payload, args.database_dir, args.tables_file, args.spider_eval_dir)
        payload["official_spider_execution"] = official
        for policy in POLICIES:
            values = [
                bool(t["official_execution_correct"])
                for t in payload["traces"]
                if t["policy"] == policy
            ]
            n = len(values)
            reliability = sum(values) / n if n else 0.0
            payload.setdefault("results", {})[policy] = {
                "n": n,
                "execution_correctness": reliability,
                "coverage": sum(bool(t["generated_sql"]) for t in payload["traces"] if t["policy"] == policy) / n if n else 0.0,
                "mean_cost": statistics.mean(t["cost"] for t in payload["traces"] if t["policy"] == policy) if n else None,
                "median_latency_ms": statistics.median(t["latency_ms"] for t in payload["traces"] if t["policy"] == policy) if n else None,
                "mean_llm_calls": statistics.mean(t["llm_calls"] for t in payload["traces"] if t["policy"] == policy) if n else None,
                "targets": {str(r): reliability >= r for r in (0.90, 0.95, 0.97, 0.99)},
            }
    else:
        payload["status"] = "benchmark_run_without_official_evaluator"
        payload["results"] = payload["secondary_custom_results"]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["results"], indent=2))


if __name__ == "__main__":
    main()
