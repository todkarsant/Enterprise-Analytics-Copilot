from pathlib import Path
import json
import sqlite3

from research.spider_benchmark import DeterministicSolver, SpiderDataset, SpiderEvaluator, summarize
from research.spider_benchmark import Trace, POLICIES


def make_fixture(tmp_path: Path):
    q = tmp_path / "dev.json"
    q.write_text(json.dumps([{
        "question": "How many users are there?",
        "db_id": "toy",
        "query": "SELECT COUNT(*) FROM users",
    }]), encoding="utf-8")
    db_dir = tmp_path / "database" / "toy"
    db_dir.mkdir(parents=True)
    db = db_dir / "toy.sqlite"
    with sqlite3.connect(db) as con:
        con.execute("CREATE TABLE users(id INTEGER)")
        con.executemany("INSERT INTO users(id) VALUES (?)", [(1,), (2,), (3,)])
        con.commit()
    return q, db_dir.parent


def test_spider_dataset_loads_and_resolves_db(tmp_path):
    q, db_root = make_fixture(tmp_path)
    ds = SpiderDataset(q, db_root)
    assert len(ds.examples) == 1
    assert ds.db_path("toy").name == "toy.sqlite"
    assert "CREATE TABLE users" in ds.schema("toy")
    manifest = ds.checksum_manifest()
    assert len(manifest["question_sha256"]) == 64
    assert manifest["database_files"]


def test_execution_evaluator_compares_results_after_run(tmp_path):
    q, db_root = make_fixture(tmp_path)
    ds = SpiderDataset(q, db_root)
    ev = SpiderEvaluator(ds)
    assert ev.execute("toy", "SELECT COUNT(*) FROM users")[0] is True
    assert ev.correct("toy", "SELECT COUNT(*) FROM users", "SELECT COUNT(*) FROM users") is True
    assert ev.correct("toy", "SELECT COUNT(*) FROM users WHERE id > 10", "SELECT COUNT(*) FROM users") is False


def test_deterministic_solver_has_no_implicit_gold_access(tmp_path):
    solver = DeterministicSolver(None)
    assert solver.generate("How many users are there?") is None


def test_summary_exposes_all_pre_p6_policies():
    traces = [
        Trace("q", "db", p, generated_sql="SELECT 1", evaluator_correct=(p in {"P0", "P5"}), cost=0.2, latency_ms=10)
        for p in POLICIES
    ]
    result = summarize(traces)
    assert list(result) == list(POLICIES)
    assert result["P5"]["execution_correctness"] == 1.0
    assert result["P1"]["execution_correctness"] == 0.0
    assert result["P5"]["targets"]["0.9"] is True
    assert result["P1"]["targets"]["0.9"] is False
