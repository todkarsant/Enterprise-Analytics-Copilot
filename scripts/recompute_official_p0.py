from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.spider_official_eval import OfficialSpiderExecutionEvaluator


def load_questions(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_p0_traces(root: Path):
    rows = []
    for path in sorted(root.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict) or not isinstance(payload.get("traces"), list):
            continue
        for trace in payload["traces"]:
            if trace.get("policy") == "P0":
                rows.append(trace)
    return rows


def main():
    ap = argparse.ArgumentParser(description="Recompute official Spider correctness for frozen P0 SQL only.")
    ap.add_argument("--p0-root", type=Path, required=True)
    ap.add_argument("--question-file", type=Path, required=True)
    ap.add_argument("--database-dir", type=Path, required=True)
    ap.add_argument("--tables-file", type=Path, required=True)
    ap.add_argument("--spider-eval-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    questions = load_questions(args.question_file)
    question_map = {(r["question"], r["db_id"]): r["query"] for r in questions}
    frozen = load_p0_traces(args.p0_root)
    evaluator = OfficialSpiderExecutionEvaluator(args.spider_eval_dir, args.tables_file)

    out = []
    seen = set()
    for trace in frozen:
        key = (trace.get("question"), trace.get("db_id"))
        if key not in question_map or key in seen:
            continue
        seen.add(key)
        result = dict(trace)
        result["official_execution_correct"] = evaluator.correct(
            args.database_dir / trace["db_id"] / f'{trace["db_id"]}.sqlite',
            trace["db_id"],
            trace.get("generated_sql"),
            question_map[key],
        )
        result["official_evaluation_source"] = {
            "evaluator_commit": "b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c",
            "gold_used_posthoc_only": True,
            "source": "recomputed_from_frozen_p0_sql",
        }
        out.append(result)

    if len(out) != len(questions):
        raise RuntimeError(f"P0 trace coverage mismatch: recomputed={len(out)} expected={len(questions)}")

    payload = {
        "policy": "P0",
        "question_count": len(out),
        "traces": out,
        "evaluation_contract": {
            "official_evaluator_commit": "b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c",
            "inference_rerun": False,
            "gold_used_for_policy": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"question_count": len(out), "correct": sum(r["official_execution_correct"] for r in out)}, indent=2))


if __name__ == "__main__":
    main()
