#!/usr/bin/env python3
"""Merge independent Spider benchmark chunks without changing trace semantics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def merge(paths: list[Path]) -> dict:
    if not paths:
        raise ValueError("No benchmark chunk artifacts found")
    payloads = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(paths)]
    traces = []
    manifests = []
    benchmark = payloads[0].get("benchmark")
    provider = payloads[0].get("provider")
    for payload in payloads:
        if payload.get("benchmark") != benchmark:
            raise ValueError("Benchmark names differ across chunks")
        if payload.get("provider") != provider:
            raise ValueError("Provider differs across chunks")
        traces.extend(payload.get("traces", []))
        manifests.append(payload.get("dataset_manifest", {}))

    keys = [(r.get("question"), r.get("db_id"), r.get("policy")) for r in traces]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate question/db/policy trace detected across chunks")

    policies = sorted({r.get("policy") for r in traces})
    questions = {(r.get("question"), r.get("db_id")) for r in traces}
    expected = len(questions) * len(policies)
    if expected != len(traces):
        raise ValueError(f"Incomplete chunk merge: expected {expected} traces, got {len(traces)}")

    return {
        "status": "external_benchmark_run_merged",
        "benchmark": benchmark,
        "question_count": len(questions),
        "policies": policies,
        "provider": provider,
        "chunk_count": len(payloads),
        "chunk_manifests": manifests,
        "official_spider_execution": "per-trace official evaluator results retained in traces",
        "traces": traces,
        "warning": "Official Spider execution evaluation is primary. The row-set metric is retained only as a secondary diagnostic.",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-root", type=Path, required=True)
    ap.add_argument("--pattern", default="p0_p5*.json")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    paths = sorted(args.input_root.rglob(args.pattern))
    payload = merge(paths)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"merged {len(paths)} chunks -> {len(payload['traces'])} traces / {payload['question_count']} questions")


if __name__ == "__main__":
    main()
