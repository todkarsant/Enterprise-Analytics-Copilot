#!/usr/bin/env python3
"""PRQS-1 preflight gate for unattended research execution."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REQUIRED_FILES = [
    "docs/EXPENSIVE_BENCHMARK_POLICY.md",
    "docs/BASELINE_SPECIFICATIONS.md",
    "docs/EXPERIMENT_DATA_MODEL.md",
    "docs/PROJECT1_EVALUATOR_HARDENING.md",
    "docs/REMOTE_OLLAMA_RESEARCH_RUNNER.md",
    "research/spider_benchmark.py",
    "research/spider_official_eval.py",
    "research/spider_adapter.py",
    "research/spider_evaluator_forensics.py",
    "scripts/analyze_research_benchmark.py",
    "scripts/validate_spider.py",
]

FORBIDDEN_ENV = ("AZURE_OPENAI_API_KEY", "AZURE_API_KEY", "OPENAI_API_KEY")


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    failures: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            failures.append(f"missing required research file: {rel}")

    if os.environ.get("LLM_PROVIDER", "ollama").lower() != "ollama":
        failures.append("iterative research provider is not locked to ollama")

    for name in FORBIDDEN_ENV:
        if os.environ.get(name):
            failures.append(f"paid-provider credential is present in environment: {name}")

    workflow = root / ".github/workflows/research-orchestrator.yml"
    if workflow.is_file():
        text = workflow.read_text(encoding="utf-8")
        # The workflow may test that paid credentials are absent; it must not
        # define a paid-provider execution path.
        if "azure" in text.lower():
            failures.append("orchestrator contains a paid-provider execution path")
        if "LLM_PROVIDER: ollama" not in text:
            failures.append("orchestrator does not hard-code local Ollama provider")

    try:
        branch = run(["git", "branch", "--show-current"])
        if branch != "research/p1-evaluator-hardening":
            failures.append(f"unexpected research branch: {branch}")
    except RuntimeError as exc:
        failures.append(str(exc))

    try:
        run([sys.executable, "-m", "pytest", "-q", "tests"])
    except RuntimeError as exc:
        failures.append(f"research unit tests failed: {exc}")

    if failures:
        print("PRQS-1 GATE: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PRQS-1 GATE: PASS")
    print("- methodology/evaluator infrastructure present")
    print("- iterative provider locked to Ollama")
    print("- no paid-provider credential exposed to the job")
    print("- no paid-provider execution path in orchestrator")
    print("- research unit tests pass")
    print("- gate does not alter benchmark/evaluation logic")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
