from __future__ import annotations

"""Bounded/resumable wrapper around the frozen Spider P0-P5 benchmark.

This module does not alter policy logic, datasets, evaluator semantics, metrics,
or model configuration. It adds runtime observability, per-policy wall-clock
bounds, and durable checkpoints so a pathological inference cannot hold an
entire partition indefinitely.
"""

import argparse
import json
import os
import signal
import time
from dataclasses import asdict
from pathlib import Path

from research.spider_benchmark import (
    POLICIES,
    BenchmarkEnvironment,
    Example,
    SecondaryExecutionEvaluator,
    SpiderDataset,
    Trace,
    summarize,
)
from research.deterministic_solver import RuleBasedDeterministicSolver
from research.experiment import State, query_complexity
from research.spider_official_eval import evaluate_traces
from app.services.llm import AzureOpenAIProvider, OllamaProvider


class PolicyTimeout(TimeoutError):
    pass


def _alarm_handler(signum, frame):
    raise PolicyTimeout("policy_wall_clock_timeout")


def run_bounded(env: BenchmarkEnvironment, example: Example, policy: str, timeout_seconds: int) -> Trace:
    started = time.perf_counter()
    old_handler = signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(timeout_seconds)
    try:
        trace = env.run(example, policy)
    except PolicyTimeout as exc:
        trace = Trace(example.question, example.db_id, policy)
        trace.termination_reason = "policy_wall_clock_timeout"
        trace.error = str(exc)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
    elapsed = (time.perf_counter() - started) * 1000
    trace.latency_ms = max(trace.latency_ms, elapsed)
    if elapsed >= timeout_seconds * 1000 and trace.termination_reason == "runtime_error":
        trace.termination_reason = "policy_wall_clock_timeout"
    return trace


def load_checkpoint(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("traces", [])


def write_checkpoint(path: Path, traces: list[dict], question_count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "checkpoint",
        "benchmark": "Spider 1.0 development",
        "question_count": question_count,
        "policies": list(POLICIES),
        "provider": os.getenv("LLM_PROVIDER", "").lower() or "none",
        "trace_count": len(traces),
        "traces": traces,
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--spider-eval-dir", type=Path, required=True)
    ap.add_argument("--tables-file", type=Path, required=True)
    ap.add_argument("--policy-timeout-seconds", type=int, default=150)
    args = ap.parse_args()

    dataset = SpiderDataset(args.questions, args.database_dir)
    evaluator = SecondaryExecutionEvaluator(dataset)
    deterministic = RuleBasedDeterministicSolver(args.database_dir)
    provider_name = os.getenv("LLM_PROVIDER", "").lower()
    if provider_name == "ollama":
        provider = OllamaProvider(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), os.getenv("OLLAMA_MODEL", "llama3.2:1b"))
    elif provider_name == "azure_openai":
        provider = AzureOpenAIProvider(os.getenv("AZURE_OPENAI_ENDPOINT", ""), os.getenv("AZURE_OPENAI_API_KEY", ""), os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"), os.getenv("AZURE_OPENAI_DEPLOYMENT", ""))
    else:
        provider = None
    env = BenchmarkEnvironment(dataset, evaluator, provider, deterministic)
    examples = dataset.examples

    traces = load_checkpoint(args.checkpoint)
    done = {(r.get("question"), r.get("db_id"), r.get("policy")) for r in traces}
    print(f"RESUME: {len(traces)} traces already checkpointed", flush=True)

    for index, example in enumerate(examples):
        print(f"CASE {index + 1}/{len(examples)} db={example.db_id} question={example.question!r}", flush=True)
        for policy in POLICIES:
            key = (example.question, example.db_id, policy)
            if key in done:
                print(f"  {policy}: checkpointed", flush=True)
                continue
            print(f"  {policy}: START timeout={args.policy_timeout_seconds}s", flush=True)
            trace = run_bounded(env, example, policy, args.policy_timeout_seconds)
            row = asdict(trace)
            traces.append(row)
            done.add(key)
            write_checkpoint(args.checkpoint, traces, len(examples))
            print(f"  {policy}: END termination={trace.termination_reason} latency_ms={trace.latency_ms:.1f} llm_calls={trace.llm_calls} error={trace.error!r}", flush=True)

    payload = {
        "status": "external_benchmark_run",
        "benchmark": "Spider 1.0 development",
        "question_count": len(examples),
        "policies": list(POLICIES),
        "provider": provider_name or "none",
        "dataset_manifest": dataset.checksum_manifest(),
        "secondary_custom_results": summarize([Trace(**r) for r in traces], "custom_execution_correct"),
        "official_spider_execution": None,
        "traces": traces,
        "runtime_controls": {"policy_timeout_seconds": args.policy_timeout_seconds, "checkpoint": str(args.checkpoint), "resume_enabled": True},
        "warning": "Official Spider execution evaluation is primary. Runtime timeouts are recorded as failures and are not silently excluded.",
    }
    official = evaluate_traces(payload, args.database_dir, args.tables_file, args.spider_eval_dir)
    payload["official_spider_execution"] = official
    payload["results"] = {}
    for policy in POLICIES:
        rows = [r for r in traces if r["policy"] == policy]
        n = len(rows)
        rel = sum(bool(r.get("official_execution_correct")) for r in rows) / n if n else 0.0
        payload["results"][policy] = {
            "n": n,
            "execution_correctness": rel,
            "coverage": sum(bool(r.get("generated_sql")) for r in rows) / n if n else 0.0,
            "mean_cost": sum(r.get("cost", 0.0) for r in rows) / n if n else None,
            "median_latency_ms": sorted(r.get("latency_ms", 0.0) for r in rows)[n // 2] if n else None,
            "mean_llm_calls": sum(r.get("llm_calls", 0) for r in rows) / n if n else None,
            "targets": {str(x): rel >= x for x in (.90, .95, .97, .99)},
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["results"], indent=2))


if __name__ == "__main__":
    main()
