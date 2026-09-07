from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from research.spider_benchmark import SecondaryExecutionEvaluator
from research.spider_official_eval import OfficialSpiderExecutionEvaluator


def _execute(db_path: Path, sql: str) -> tuple[list[tuple], list[str]]:
    with sqlite3.connect(db_path) as con:
        cur = con.execute(sql)
        return cur.fetchall(), [d[0] for d in cur.description or []]


def diagnose_trace(
    trace: dict[str, Any],
    gold_sql: str,
    db_path: Path,
    official: OfficialSpiderExecutionEvaluator,
    secondary: SecondaryExecutionEvaluator,
) -> dict[str, Any]:
    predicted_sql = trace.get("generated_sql")
    rowset_match = secondary.correct(trace["db_id"], predicted_sql, gold_sql)
    official_match = official.correct(db_path, trace["db_id"], predicted_sql, gold_sql)

    result: dict[str, Any] = {
        "question": trace["question"],
        "db_id": trace["db_id"],
        "policy": trace["policy"],
        "official_execution_correct": official_match,
        "secondary_rowset_match": rowset_match,
        "classification": "agreement",
    }
    if rowset_match and not official_match:
        result["classification"] = "official_stricter_than_rowset_diagnostic"
    elif official_match and not rowset_match:
        result["classification"] = "official_match_rowset_diagnostic_disagrees"

    # Keep the actual SQL out of aggregate benchmark metrics, but include it in
    # the forensic artifact so a human can inspect an individual discrepancy.
    result["predicted_sql"] = predicted_sql
    result["gold_sql"] = gold_sql
    if predicted_sql:
        try:
            pred_rows, pred_cols = _execute(db_path, predicted_sql)
            gold_rows, gold_cols = _execute(db_path, gold_sql)
            result["predicted_shape"] = [len(pred_rows), len(pred_cols)]
            result["gold_shape"] = [len(gold_rows), len(gold_cols)]
            result["predicted_columns"] = pred_cols
            result["gold_columns"] = gold_cols
        except Exception as exc:
            result["execution_diagnostic_error"] = str(exc)
    return result


def run(payload_path: Path, database_dir: Path, tables_file: Path, spider_eval_dir: Path) -> dict[str, Any]:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    dataset_rows = {
        (row["question"], row["db_id"]): row["query"]
        for row in json.loads(Path(payload["dataset_manifest"]["question_file"]).read_text(encoding="utf-8"))
    }
    official = OfficialSpiderExecutionEvaluator(spider_eval_dir, tables_file)
    secondary = SecondaryExecutionEvaluator(_DatasetShim(database_dir, dataset_rows))
    findings = []
    for trace in payload["traces"]:
        key = (trace["question"], trace["db_id"])
        finding = diagnose_trace(
            trace,
            dataset_rows[key],
            database_dir / trace["db_id"] / f'{trace["db_id"]}.sqlite',
            official,
            secondary,
        )
        if finding["classification"] != "agreement":
            findings.append(finding)
    return {
        "benchmark": payload.get("benchmark"),
        "question_count": payload.get("question_count"),
        "policy_scope": payload.get("policies"),
        "official_metric": "Spider execution accuracy",
        "secondary_metric": "diagnostic row-set equality only",
        "finding_count": len(findings),
        "findings": findings,
        "interpretation": (
            "A row-set match with an official mismatch is not treated as an evaluator bug. "
            "The pinned Spider execution evaluator compares result values mapped to parsed "
            "SELECT value units in corresponding positions. The row-set metric is therefore "
            "a permissive diagnostic and must never override the official metric."
        ),
    }


class _DatasetShim:
    def __init__(self, database_dir: Path, rows: dict[tuple[str, str], str]):
        self.database_dir = database_dir

    def db_path(self, db_id: str) -> Path:
        path = self.database_dir / db_id / f"{db_id}.sqlite"
        if not path.exists():
            raise FileNotFoundError(path)
        return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Forensically compare Spider official execution accuracy with the secondary row-set diagnostic.")
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--database-dir", type=Path, required=True)
    parser.add_argument("--tables-file", type=Path, required=True)
    parser.add_argument("--spider-eval-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = run(args.payload, args.database_dir, args.tables_file, args.spider_eval_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"finding_count": report["finding_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
