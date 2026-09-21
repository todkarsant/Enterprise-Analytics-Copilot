from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

from app.services.llm import AzureOpenAIProvider, OllamaProvider
from research.deterministic_solver import RuleBasedDeterministicSolver
from research.defensibility import DefensibilityTrace, validate_trace
from research.p5_selector import assess_strict_evidence
from research.p6_ip import decide_replacement, verify_challenger
from research.spider_benchmark import BenchmarkEnvironment, Example, SecondaryExecutionEvaluator, SpiderDataset, Trace
from research.spider_official_eval import evaluate_traces

POLICY = "P6-IP"


def build_environment(questions: Path, database_dir: Path):
    dataset = SpiderDataset(questions, database_dir)
    provider_name = os.getenv("LLM_PROVIDER", "").lower()
    provider = None
    if provider_name == "ollama":
        provider = OllamaProvider(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), os.getenv("OLLAMA_MODEL", "llama3.2:1b"))
    elif provider_name == "azure_openai":
        provider = AzureOpenAIProvider(os.getenv("AZURE_OPENAI_ENDPOINT", ""), os.getenv("AZURE_OPENAI_API_KEY", ""), os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"), os.getenv("AZURE_OPENAI_DEPLOYMENT", ""))
    return dataset, BenchmarkEnvironment(dataset, SecondaryExecutionEvaluator(dataset), provider, RuleBasedDeterministicSolver(database_dir))


def run_case(env: BenchmarkEnvironment, example: Example) -> tuple[Trace, dict]:
    started = time.perf_counter()
    incumbent = env.run(example, "P0")
    eligible, reason = assess_strict_evidence(example.question, incumbent.generated_sql or "", incumbent.evidence_row_count)
    record = DefensibilityTrace(
        case_id=f"{example.db_id}:{example.question}",
        policy=POLICY,
        evidence={"incumbent_row_count": incumbent.evidence_row_count, "incumbent_column_count": incumbent.evidence_column_count, "incumbent_execution_ok": incumbent.execution_ok},
        evidence_provenance=["incumbent_execution_trace"],
        risk_reasons=[reason] if reason else [],
        decision="INTERVENE" if eligible else "KEEP",
        intervention=eligible,
    )
    if not eligible:
        incumbent.policy = POLICY
        incumbent.actions = ["incumbent:P0"] + incumbent.actions
        record.outcome_class = "KEEP_INCUMBENT"
        record.verification = {"passed": False, "not_run": True}
        incumbent.termination_reason = "p6_keep_incumbent"
        incumbent.latency_ms = (time.perf_counter() - started) * 1000
        validate_trace(record)
        return incumbent, record.to_dict()

    challenger = Trace(example.question, example.db_id, POLICY)
    schema = env.dataset.schema(example.db_id)
    env._run_p5(challenger, example, schema, strict=False)
    verification = verify_challenger(example.question, challenger.generated_sql, challenger.sql_valid, challenger.execution_ok)
    record.verification = asdict(verification)
    decision = decide_replacement(intervention_eligible=True, verification=verification)
    record.decision = decision
    record.replacement = decision == "REPLACE"

    selected = challenger if decision == "REPLACE" else incumbent
    selected.policy = POLICY
    selected.actions = ["incumbent:P0", "risk_assessment", "INTERVENE"] + [f"challenger:{a}" for a in challenger.actions]
    record.outcome_class = "REPLACE_CHALLENGER" if decision == "REPLACE" else "PRESERVE_INCUMBENT"
    selected.termination_reason = "p6_replace_after_verification" if decision == "REPLACE" else "p6_preserve_incumbent"
    selected.cost = incumbent.cost + challenger.cost
    selected.llm_calls = incumbent.llm_calls + challenger.llm_calls
    selected.input_tokens = incumbent.input_tokens + challenger.input_tokens
    selected.output_tokens = incumbent.output_tokens + challenger.output_tokens
    selected.latency_ms = (time.perf_counter() - started) * 1000
    validate_trace(record)
    return selected, record.to_dict()


def isolated_worker(args):
    dataset, env = build_environment(args.questions, args.database_dir)
    example = next(x for x in dataset.examples if x.question == args.question and x.db_id == args.db_id)
    trace, record = run_case(env, example)
    print(json.dumps({"trace": asdict(trace), "defensibility": record}, separators=(",", ":")), flush=True)


def run_isolated(questions: Path, database_dir: Path, example: Example, timeout_seconds: int) -> tuple[Trace, dict]:
    command = [sys.executable, "-m", "research.p6_ip_runner", "--worker", "--questions", str(questions), "--database-dir", str(database_dir), "--question", example.question, "--db-id", example.db_id]
    started = time.perf_counter()
    try:
        completed = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=timeout_seconds, shell=False)
    except subprocess.TimeoutExpired as exc:
        elapsed = (time.perf_counter() - started) * 1000
        trace = Trace(example.question, example.db_id, POLICY, latency_ms=elapsed, termination_reason="policy_process_timeout", error=f"hard_process_timeout_{timeout_seconds}s: {exc}")
        return trace, {"case_id": f"{example.db_id}:{example.question}", "policy": POLICY, "decision": "KEEP", "outcome_class": "RUNTIME_FAILURE"}
    elapsed = (time.perf_counter() - started) * 1000
    if completed.returncode != 0:
        trace = Trace(example.question, example.db_id, POLICY, latency_ms=elapsed, termination_reason="policy_process_error", error=f"worker_exit_{completed.returncode}: {(completed.stderr or '')[-1000:]}")
        return trace, {"case_id": f"{example.db_id}:{example.question}", "policy": POLICY, "decision": "KEEP", "outcome_class": "RUNTIME_FAILURE"}
    try:
        payload = json.loads((completed.stdout or "").strip().splitlines()[-1])
        trace = Trace(**payload["trace"])
        trace.latency_ms = max(trace.latency_ms, elapsed)
        return trace, payload["defensibility"]
    except Exception as exc:
        trace = Trace(example.question, example.db_id, POLICY, latency_ms=elapsed, termination_reason="worker_protocol_error", error=f"invalid_worker_output: {exc}")
        return trace, {"case_id": f"{example.db_id}:{example.question}", "policy": POLICY, "decision": "KEEP", "outcome_class": "RUNTIME_FAILURE"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--questions", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--question")
    ap.add_argument("--db-id")
    ap.add_argument("--spider-eval-dir", type=Path)
    ap.add_argument("--tables-file", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--checkpoint", type=Path)
    ap.add_argument("--policy-timeout-seconds", type=int, default=150)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    if args.worker:
        if not all((args.question, args.db_id)):
            raise SystemExit("worker requires --question and --db-id")
        isolated_worker(args)
        return
    dataset, _ = build_environment(args.questions, args.database_dir)
    examples = dataset.examples[:args.limit] if args.limit else dataset.examples
    traces, records, done = [], [], set()
    if args.checkpoint and args.checkpoint.exists():
        payload = json.loads(args.checkpoint.read_text(encoding="utf-8")); traces = payload.get("traces", []); records = payload.get("defensibility", []); done = {(r.get("question"), r.get("db_id")) for r in traces}
    for index, example in enumerate(examples):
        if (example.question, example.db_id) in done:
            continue
        print(f"CASE {index + 1}/{len(examples)} db={example.db_id}", flush=True)
        trace, record = run_isolated(args.questions, args.database_dir, example, args.policy_timeout_seconds)
        traces.append(asdict(trace)); records.append(record); done.add((example.question, example.db_id))
        if args.checkpoint:
            args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
            args.checkpoint.write_text(json.dumps({"traces": traces, "defensibility": records}, indent=2) + "\n", encoding="utf-8")
    payload = {"status": "external_benchmark_run", "benchmark": "Spider 1.0", "question_count": len(examples), "policies": [POLICY], "provider": os.getenv("LLM_PROVIDER", "").lower() or "none", "dataset_manifest": dataset.checksum_manifest(), "traces": traces, "defensibility": records, "runtime_controls": {"policy_timeout_seconds": args.policy_timeout_seconds, "isolation": "one OS subprocess per case", "checkpoint": str(args.checkpoint) if args.checkpoint else None, "challenger_only": True}}
    if args.spider_eval_dir and args.tables_file:
        payload["official_spider_execution"] = evaluate_traces(payload, args.database_dir, args.tables_file, args.spider_eval_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"traces": len(traces), "defensibility_records": len(records)}, indent=2))


if __name__ == "__main__":
    main()
