from __future__ import annotations

"""Process-isolated/resumable Spider benchmark runner.

The default policy set remains the frozen P0-P5 benchmark. An explicit --policies
argument permits separate challenger runs without changing the frozen default.
"""

import argparse
import json
import os
import subprocess
import sys
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
from research.spider_official_eval import evaluate_traces
from app.services.llm import AzureOpenAIProvider, OllamaProvider


def build_environment(questions: Path, database_dir: Path) -> tuple[SpiderDataset, BenchmarkEnvironment]:
    dataset = SpiderDataset(questions, database_dir)
    evaluator = SecondaryExecutionEvaluator(dataset)
    deterministic = RuleBasedDeterministicSolver(database_dir)
    provider_name = os.getenv("LLM_PROVIDER", "").lower()
    if provider_name == "ollama":
        provider = OllamaProvider(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), os.getenv("OLLAMA_MODEL", "llama3.2:1b"))
    elif provider_name == "azure_openai":
        provider = AzureOpenAIProvider(os.getenv("AZURE_OPENAI_ENDPOINT", ""), os.getenv("AZURE_OPENAI_API_KEY", ""), os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"), os.getenv("AZURE_OPENAI_DEPLOYMENT", ""))
    else:
        provider = None
    return dataset, BenchmarkEnvironment(dataset, evaluator, provider, deterministic)


def worker(args: argparse.Namespace) -> None:
    dataset, env = build_environment(args.questions, args.database_dir)
    example = next(x for x in dataset.examples if x.question == args.question and x.db_id == args.db_id)
    trace = env.run(example, args.policy)
    print(json.dumps(asdict(trace), separators=(",", ":")), flush=True)


def run_policy_isolated(questions: Path, database_dir: Path, example: Example, policy: str, timeout_seconds: int) -> Trace:
    command = [sys.executable, "-m", "research.spider_benchmark_isolated", "--worker", "--questions", str(questions), "--database-dir", str(database_dir), "--question", example.question, "--db-id", example.db_id, "--policy", policy]
    started = time.perf_counter()
    try:
        completed = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=timeout_seconds, shell=False)
    except subprocess.TimeoutExpired as exc:
        elapsed = (time.perf_counter() - started) * 1000
        return Trace(example.question, example.db_id, policy, latency_ms=elapsed, termination_reason="policy_process_timeout", error=f"hard_process_timeout_{timeout_seconds}s: {exc}")
    elapsed = (time.perf_counter() - started) * 1000
    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        return Trace(example.question, example.db_id, policy, latency_ms=elapsed, termination_reason="policy_process_error", error=f"worker_exit_{completed.returncode}: {stderr[-1000:]}")
    try:
        payload = json.loads((completed.stdout or "").strip().splitlines()[-1])
        trace = Trace(**payload)
        trace.latency_ms = max(trace.latency_ms, elapsed)
        return trace
    except Exception as exc:
        return Trace(example.question, example.db_id, policy, latency_ms=elapsed, termination_reason="worker_protocol_error", error=f"invalid_worker_output: {exc}; stdout={(completed.stdout or '')[-1000:]}")


def load_checkpoint(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("traces", [])


def write_checkpoint(path: Path, traces: list[dict], question_count: int, policies: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"status": "checkpoint", "benchmark": "Spider 1.0 development", "question_count": question_count, "policies": list(policies), "provider": os.getenv("LLM_PROVIDER", "").lower() or "none", "trace_count": len(traces), "traces": traces}
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def parent(args: argparse.Namespace) -> None:
    dataset, _ = build_environment(args.questions, args.database_dir)
    examples = dataset.examples
    policies = tuple(x.strip() for x in args.policies.split(",") if x.strip())
    if not policies:
        raise SystemExit("--policies must contain at least one policy")
    traces = load_checkpoint(args.checkpoint)
    done = {(r.get("question"), r.get("db_id"), r.get("policy")) for r in traces}
    print(f"RESUME: {len(traces)} traces already checkpointed; policies={policies}", flush=True)
    for index, example in enumerate(examples):
        print(f"CASE {index + 1}/{len(examples)} db={example.db_id} question={example.question!r}", flush=True)
        for policy in policies:
            key = (example.question, example.db_id, policy)
            if key in done:
                print(f"  {policy}: checkpointed", flush=True)
                continue
            print(f"  {policy}: START hard_process_timeout={args.policy_timeout_seconds}s", flush=True)
            trace = run_policy_isolated(args.questions, args.database_dir, example, policy, args.policy_timeout_seconds)
            row = asdict(trace); traces.append(row); done.add(key)
            write_checkpoint(args.checkpoint, traces, len(examples), policies)
            print(f"  {policy}: END termination={trace.termination_reason} latency_ms={trace.latency_ms:.1f} llm_calls={trace.llm_calls} error={trace.error!r}", flush=True)

    typed_traces = [Trace(**r) for r in traces]
    payload = {
        "status": "external_benchmark_run",
        "benchmark": "Spider 1.0 development",
        "question_count": len(examples),
        "policies": list(policies),
        "provider": os.getenv("LLM_PROVIDER", "").lower() or "none",
        "dataset_manifest": dataset.checksum_manifest(),
        "secondary_custom_results": summarize(typed_traces, "custom_execution_correct") if set(policies).issubset(set(POLICIES)) else None,
        "official_spider_execution": None,
        "traces": traces,
        "runtime_controls": {"policy_timeout_seconds": args.policy_timeout_seconds, "isolation": "one OS subprocess per case-policy execution", "checkpoint": str(args.checkpoint), "resume_enabled": True, "policy_set_explicit": list(policies)},
        "warning": "Official Spider execution evaluation is primary. Runtime process timeouts and worker errors are recorded as failures and are not silently excluded.",
    }
    official = evaluate_traces(payload, args.database_dir, args.tables_file, args.spider_eval_dir)
    payload["official_spider_execution"] = official
    payload["results"] = {}
    for policy in policies:
        rows = [r for r in traces if r["policy"] == policy]
        n = len(rows); rel = sum(bool(r.get("official_execution_correct")) for r in rows) / n if n else 0.0
        ordered = sorted(r.get("latency_ms", 0.0) for r in rows)
        payload["results"][policy] = {"n": n, "execution_correctness": rel, "coverage": sum(bool(r.get("generated_sql")) for r in rows) / n if n else 0.0, "mean_cost": sum(r.get("cost", 0.0) for r in rows) / n if n else None, "median_latency_ms": ordered[n // 2] if n else None, "mean_llm_calls": sum(r.get("llm_calls", 0) for r in rows) / n if n else None, "targets": {str(x): rel >= x for x in (.90, .95, .97, .99)}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["results"], indent=2), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--questions", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--question")
    ap.add_argument("--db-id")
    ap.add_argument("--policy")
    ap.add_argument("--policies", default=",".join(POLICIES))
    ap.add_argument("--output", type=Path)
    ap.add_argument("--checkpoint", type=Path)
    ap.add_argument("--spider-eval-dir", type=Path)
    ap.add_argument("--tables-file", type=Path)
    ap.add_argument("--policy-timeout-seconds", type=int, default=150)
    args = ap.parse_args()
    if args.worker:
        if not all((args.question, args.db_id, args.policy)):
            raise SystemExit("worker requires --question, --db-id and --policy")
        worker(args); return
    if not all((args.output, args.checkpoint, args.spider_eval_dir, args.tables_file)):
        raise SystemExit("parent requires --output, --checkpoint, --spider-eval-dir and --tables-file")
    parent(args)


if __name__ == "__main__": main()
