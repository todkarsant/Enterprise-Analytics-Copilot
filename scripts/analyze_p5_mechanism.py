from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_frozen(root: Path, name: str) -> list[dict]:
    rows: list[dict] = []
    for path in root.rglob(name):
        payload = load_json(path)
        rows.extend(payload.get("traces", []))
    return rows


def metrics(rows: list[dict]) -> dict:
    n = len(rows)
    correct = sum(bool(r.get("official_execution_correct")) for r in rows)
    return {
        "n": n,
        "official_accuracy": correct / n if n else 0.0,
        "mean_cost": sum(float(r.get("cost", 0.0)) for r in rows) / n if n else None,
        "mean_llm_calls": sum(int(r.get("llm_calls", 0)) for r in rows) / n if n else None,
        "coverage": sum(bool(r.get("generated_sql")) for r in rows) / n if n else 0.0,
        "escalation_rate": sum(bool(r.get("evidence_escalated")) for r in rows) / n if n else 0.0,
    }


def paired(a: list[dict], b: list[dict]) -> dict:
    left = {(r.get("question"), r.get("db_id")): r for r in a}
    right = {(r.get("question"), r.get("db_id")): r for r in b}
    keys = sorted(set(left) & set(right))
    a_correct_b_wrong = 0
    a_wrong_b_correct = 0
    for k in keys:
        ac = bool(left[k].get("official_execution_correct"))
        bc = bool(right[k].get("official_execution_correct"))
        a_correct_b_wrong += ac and not bc
        a_wrong_b_correct += (not ac) and bc
    return {
        "paired_n": len(keys),
        "a_correct_b_wrong": a_correct_b_wrong,
        "a_wrong_b_correct": a_wrong_b_correct,
        "accuracy_delta_b_minus_a_pp": 100.0 * (a_wrong_b_correct - a_correct_b_wrong) / len(keys) if keys else None,
    }


def run(frozen_root: Path, p5r_dev: Path, p5r_unseen: Path) -> dict:
    frozen_dev = find_frozen(frozen_root, "p0_p5_dev.json")
    frozen_unseen = find_frozen(frozen_root, "p0_p5_unseen.json")
    p5r_dev_rows = load_json(p5r_dev).get("traces", [])
    p5r_unseen_rows = load_json(p5r_unseen).get("traces", [])

    frozen_dev_p0 = [r for r in frozen_dev if r.get("policy") == "P0"]
    frozen_dev_p5 = [r for r in frozen_dev if r.get("policy") == "P5"]
    frozen_unseen_p0 = [r for r in frozen_unseen if r.get("policy") == "P0"]
    frozen_unseen_p5 = [r for r in frozen_unseen if r.get("policy") == "P5"]

    result = {
        "status": "mechanism_forensic_result",
        "policy": "P5R",
        "frozen_reference_run": 34206500727,
        "development": {
            "P0": metrics(frozen_dev_p0),
            "P5": metrics(frozen_dev_p5),
            "P5R": metrics(p5r_dev_rows),
            "P5R_vs_P0": paired(frozen_dev_p0, p5r_dev_rows),
            "P5R_vs_P5": paired(frozen_dev_p5, p5r_dev_rows),
        },
        "unseen_schema": {
            "P0": metrics(frozen_unseen_p0),
            "P5": metrics(frozen_unseen_p5),
            "P5R": metrics(p5r_unseen_rows),
            "P5R_vs_P0": paired(frozen_unseen_p0, p5r_unseen_rows),
            "P5R_vs_P5": paired(frozen_unseen_p5, p5r_unseen_rows),
        },
        "interpretation_rule": "P5R is a prospective challenger only. Frozen P0/P5 traces are never modified. A positive result must be judged on the development partition first and then the untouched four-schema holdout; no holdout tuning is permitted.",
    }
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen-root", type=Path, required=True)
    ap.add_argument("--p5r-dev", type=Path, required=True)
    ap.add_argument("--p5r-unseen", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = run(args.frozen_root, args.p5r_dev, args.p5r_unseen)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
