from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from research.spider_official_eval import OfficialSpiderExecutionEvaluator


RESULT_FILENAMES = {"p0_p5_dev.json", "p0_p5_unseen.json"}


def _chunk_key(path: Path) -> tuple[int, str]:
    match = re.search(r"chunk-(\d+)", str(path))
    return (int(match.group(1)) if match else 10**9, str(path))


def load_traces(root: Path, result_filename: str) -> list[dict[str, Any]]:
    """Load only the requested benchmark result file, never dev+holdout together."""
    if result_filename not in RESULT_FILENAMES:
        raise ValueError(f"Unsupported P0 result filename: {result_filename}")
    traces: list[dict[str, Any]] = []
    paths = sorted(
        (p for p in root.rglob("*.json") if p.name == result_filename),
        key=_chunk_key,
    )
    if not paths:
        raise ValueError(f"No P0 benchmark result artifacts named {result_filename} found under {root}")
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid benchmark artifact: {path}: {exc}") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("traces"), list):
            raise ValueError(f"Benchmark artifact has no trace list: {path}")
        traces.extend(t for t in payload["traces"] if t.get("policy") == "P0")
    if not traces:
        raise ValueError(f"No P0 traces found in {result_filename} artifacts under {root}")
    return traces


def main() -> None:
    ap = argparse.ArgumentParser(description="Recompute official Spider correctness for frozen P0 SQL")
    ap.add_argument("--p0-root", type=Path, required=True)
    ap.add_argument("--question-file", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--tables-file", type=Path, required=True)
    ap.add_argument("--spider-eval-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--result-filename", choices=sorted(RESULT_FILENAMES), help="Frozen benchmark artifact family to recompute")
    args = ap.parse_args()

    result_filename = args.result_filename
    if result_filename is None:
        result_filename = "p0_p5_unseen.json" if "unseen" in args.question_file.name else "p0_p5_dev.json"

    traces = load_traces(args.p0_root, result_filename)
    questions = json.loads(args.question_file.read_text(encoding="utf-8"))
    if not isinstance(questions, list):
        raise ValueError("Question file must contain a JSON list")

    gold_by_key: dict[tuple[str, str], list[str]] = {}
    for row in questions:
        key = (row["question"], row["db_id"])
        gold_by_key.setdefault(key, []).append(row["query"])

    evaluator = OfficialSpiderExecutionEvaluator(args.spider_eval_dir, args.tables_file)
    occurrence: dict[tuple[str, str], int] = {}
    corrected: list[dict[str, Any]] = []
    for trace in traces:
        key = (trace["question"], trace["db_id"])
        idx = occurrence.get(key, 0)
        occurrence[key] = idx + 1
        gold_options = gold_by_key.get(key)
        if not gold_options or idx >= len(gold_options):
            raise KeyError(f"P0 case occurrence missing from question file: {key} occurrence={idx}")
        db_path = args.database_dir / trace["db_id"] / f"{trace['db_id']}.sqlite"
        updated = dict(trace)
        updated["official_execution_correct"] = evaluator.correct(
            db_path, trace["db_id"], trace.get("generated_sql"), gold_options[idx]
        )
        updated["recomputed_case_occurrence"] = idx
        corrected.append(updated)

    expected = len(questions)
    if len(corrected) != expected:
        raise ValueError(f"P0 denominator mismatch after recomputation: {len(corrected)} != {expected}")
    for key, gold_options in gold_by_key.items():
        if occurrence.get(key, 0) != len(gold_options):
            raise ValueError(
                f"P0 occurrence mismatch for {key}: observed={occurrence.get(key, 0)} expected={len(gold_options)}"
            )

    payload = {
        "schema_version": "p0-official-recompute-v3",
        "source_root": str(args.p0_root),
        "source_result_filename": result_filename,
        "question_file": str(args.question_file),
        "trace_count": len(corrected),
        "case_key": "(question, db_id, occurrence_in_dataset_order)",
        "traces": corrected,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "recomputed",
        "result_filename": result_filename,
        "traces": len(corrected),
        "official_correct": sum(bool(r["official_execution_correct"]) for r in corrected),
        "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, indent=2))


if __name__ == "__main__":
    main()
