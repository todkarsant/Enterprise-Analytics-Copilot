from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load official Spider evaluator from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class OfficialSpiderExecutionEvaluator:
    """Adapter around the official taoyds/spider execution evaluator.

    The evaluator is loaded from an externally cloned, pinned Spider commit in CI.
    Gold SQL is used only here, after policy execution, and is never exposed to a
    policy or routing decision.
    """

    def __init__(self, spider_eval_dir: Path, tables_file: Path):
        self.spider_eval_dir = Path(spider_eval_dir)
        self.tables_file = Path(tables_file)
        sys.path.insert(0, str(self.spider_eval_dir))
        try:
            self.process_sql = _load_module("process_sql", self.spider_eval_dir / "process_sql.py")
            self.evaluation = _load_module("official_spider_evaluation", self.spider_eval_dir / "evaluation.py")
        finally:
            sys.path.pop(0)
        self.kmaps = self.evaluation.build_foreign_key_map_from_json(str(self.tables_file))

    def correct(self, db_path: Path, db_id: str, predicted_sql: str | None, gold_sql: str) -> bool:
        if not predicted_sql or not predicted_sql.strip():
            return False
        schema = self.evaluation.Schema(self.evaluation.get_schema(str(db_path)))
        try:
            gold = self.evaluation.get_sql(schema, gold_sql)
            predicted = self.evaluation.get_sql(schema, predicted_sql)
        except Exception:
            return False

        # Match the official evaluator's preprocessing before calling its
        # execution-equivalence function. This preserves its column/FK handling.
        kmap = self.kmaps[db_id]
        g_valid = self.evaluation.build_valid_col_units(gold["from"]["table_units"], schema)
        p_valid = self.evaluation.build_valid_col_units(predicted["from"]["table_units"], schema)
        gold = self.evaluation.rebuild_sql_val(gold)
        gold = self.evaluation.rebuild_sql_col(g_valid, gold, kmap)
        predicted = self.evaluation.rebuild_sql_val(predicted)
        predicted = self.evaluation.rebuild_sql_col(p_valid, predicted, kmap)
        return bool(self.evaluation.eval_exec_match(str(db_path), predicted_sql, gold_sql, predicted, gold))


def evaluate_traces(
    payload: dict[str, Any],
    database_dir: Path,
    tables_file: Path,
    spider_eval_dir: Path,
) -> dict[str, Any]:
    dataset_rows = {
        (row["question"], row["db_id"]): row["query"]
        for row in json.loads(Path(payload["dataset_manifest"]["question_file"]).read_text(encoding="utf-8"))
    }
    evaluator = OfficialSpiderExecutionEvaluator(spider_eval_dir, tables_file)
    by_policy: dict[str, list[bool]] = {policy: [] for policy in payload["policies"]}
    for trace in payload["traces"]:
        key = (trace["question"], trace["db_id"])
        gold_sql = dataset_rows[key]
        db_path = database_dir / trace["db_id"] / f'{trace["db_id"]}.sqlite'
        result = evaluator.correct(db_path, trace["db_id"], trace.get("generated_sql"), gold_sql)
        trace["official_execution_correct"] = result
        by_policy[trace["policy"]].append(result)

    official = {}
    for policy, values in by_policy.items():
        n = len(values)
        accuracy = sum(values) / n if n else 0.0
        official[policy] = {"n": n, "execution_accuracy": accuracy}
    return official
