from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

from research.spider_benchmark import Example, Trace, SpiderDataset
from research.spider_official_eval import evaluate_traces

POLICY = "P5R"


def load_checkpoint(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("traces", [])


def write_checkpoint(path: Path, traces: list[dict], question_count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"status": "checkpoint", "benchmark": "Spider 1.0 development", "question_count": question_count, "policies": [POLICY], "trace_count": len(traces), "traces": traces}
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def run_isolated(questions: Path, database_dir: Path, example: Example, timeout_seconds: int) -> Trace:
    command = [sys.executable, "-m", "research.spider_benchmark_isolated", "--worker", "--questions", str(questions), "--database-dir", str(database_dir), "--question", example.question, "--db-id", example.db_id, "--policy", POLICY]
    started = time.perf_counter()
    try:
        completed = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=timeout_seconds, shell=False)
    except subprocess.TimeoutExpired as exc:
        elapsed = (time.perf_counter() - started) * 1000
        return Trace(example.question, example.db_id, POLICY, latency_ms=elapsed, termination_reason="policy_process_timeout", error=f"hard_process_timeout_{timeout_seconds}s: {exc}")
    elapsed = (time.perf_counter() - started) * 1000
    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        return Trace(example.question, example.db_id, POLICY, latency_ms=elapsed, termination_reason="policy_process_error", error=f"worker_exit_{completed.returncode}: {stderr[-1000:]}")
    try:
        trace = Trace(**json.loads((completed.stdout or "").strip().splitlines()[-1]))
        trace.latency_ms = max(trace.latency_ms, elapsed)
        return trace
    except Exception as exc:
        return Trace(example.question, example.db_id, POLICY, latency_ms=elapsed, termination_reason="worker_protocol_error", error=f"invalid_worker_output: {exc}; stdout={(completed.stdout or '')[-1000:]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--spider-eval-dir", type=Path, required=True)
    ap.add_argument("--tables-file", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--policy-timeout-seconds", type=int, default=150)
    args = ap.parse_args()

    dataset = SpiderDataset(args.questions, args.database_dir)
    traces = load_checkpoint(args.checkpoint)
    done = {(r.get("question"), r.get("db_id"), r.get("policy")) for r in traces}
    for index, example in enumerate(dataset.examples):
        key = (example.question, example.db_id, POLICY)
        if key in done:
            continue
        print(f"CASE {index + 1}/{len(dataset.examples)} db={example.db_id} question={example.question!r}", flush=True)
        trace = run_isolated(args.questions, args.database_dir, example, args.policy_timeout_seconds)
        traces.append(asdict(trace)); done.add(key)
        write_checkpoint(args.checkpoint, traces, len(dataset.examples))

    payload = {
        "status": "external_benchmark_run",
        "benchmark": "Spider 1.0 development",
        "question_count": len(dataset.examples),
        "policies": [POLICY],
        "provider": "ollama",
        "dataset_manifest": dataset.checksum_manifest(),
        "traces": traces,
        "runtime_controls": {"policy_timeout_seconds": args.policy_timeout_seconds, "isolation": "one OS subprocess per case-policy execution", "checkpoint": str(args.checkpoint), "resume_enabled": True, "challenger_only": True},
        "warning": "P5R is an opt-in prospective challenger. It must not alter the frozen P0-P5 benchmark evidence.",
    }
    payload["official_spider_execution"] = evaluate_traces(payload, args.database_dir, args.tables_file, args.spider_eval_dir)
    rows = traces; n = len(rows); rel = sum(bool(r.get("official_execution_correct")) for r in rows) / n if n else 0.0
    ordered = sorted(r.get("latency_ms", 0.0) for r in rows)
    payload["results"] = {POLICY: {"n": n, "execution_correctness": rel, "coverage": sum(bool(r.get("generated_sql")) for r in rows) / n if n else 0.0, "mean_cost": sum(r.get("cost", 0.0) for r in rows) / n if n else None, "median_latency_ms": ordered[n // 2] if n else None, "mean_llm_calls": sum(r.get("llm_calls", 0) for r in rows) / n if n else None, "targets": {str(x): rel >= x for x in (.90, .95, .97, .99)}}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["results"], indent=2))


if __name__ == "__main__": main()
