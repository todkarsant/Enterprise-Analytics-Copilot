from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from research.spider_official_eval import OfficialSpiderExecutionEvaluator


def load_traces(root: Path) -> list[dict[str, Any]]:
    traces: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and isinstance(payload.get("traces"), list):
            traces.extend(t for t in payload["traces"] if t.get("policy") == "P0")
    if not traces:
        raise ValueError(f"No P0 traces found under {root}")
    return traces


def main() -> None:
    ap = argparse.ArgumentParser(description="Recompute official Spider correctness for frozen P0 SQL")
    ap.add_argument("--p0-root", type=Path, required=True)
    ap.add_argument("--question-file", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--tables-file", type=Path, required=True)
    ap.add_argument("--spider-eval-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    traces = load_traces(args.p0_root)
    questions = json.loads(args.question_file.read_text(encoding="utf-8"))
    gold = {(r["question"], r["db_id"]): r["query"] for r in questions}
    evaluator = OfficialSpiderExecutionEvaluator(args.spider_eval_dir, args.tables_file)

    seen: set[tuple[str, str]] = set()
    corrected: list[dict[str, Any]] = []
    for trace in traces:
        key = (trace["question"], trace["db_id"])
        if key in seen:
            raise ValueError(f"Duplicate P0 case: {key}")
        seen.add(key)
        if key not in gold:
            raise KeyError(f"P0 case missing from question file: {key}")
        db_path = args.database_dir / trace["db_id"] / f"{trace['db_id']}.sqlite"
        updated = dict(trace)
        updated["official_execution_correct"] = evaluator.correct(
            db_path, trace["db_id"], trace.get("generated_sql"), gold[key]
        )
        corrected.append(updated)

    corrected.sort(key=lambda r: (r["db_id"], r["question"]))
    payload = {
        "schema_version": "p0-official-recompute-v1",
        "source_root": str(args.p0_root),
        "question_file": str(args.question_file),
        "trace_count": len(corrected),
        "traces": corrected,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "recomputed",
        "traces": len(corrected),
        "official_correct": sum(bool(r["official_execution_correct"]) for r in corrected),
        "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, indent=2))


if __name__ == "__main__":
    main()
