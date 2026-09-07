from pathlib import Path
import sqlite3

from research.deterministic_solver import RuleBasedDeterministicSolver


def _db(tmp_path: Path) -> Path:
    root = tmp_path / "database"
    db_dir = root / "demo"
    db_dir.mkdir(parents=True)
    path = db_dir / "demo.sqlite"
    with sqlite3.connect(path) as con:
        con.execute("CREATE TABLE singers (id INTEGER, name TEXT, age INTEGER)")
        con.executemany(
            "INSERT INTO singers VALUES (?, ?, ?)",
            [(1, "A", 20), (2, "B", 30)],
        )
    return root


def test_count_rule_uses_schema_only(tmp_path: Path):
    solver = RuleBasedDeterministicSolver(_db(tmp_path))
    sql = solver.generate("How many singers are there?", "demo")
    assert sql == 'SELECT COUNT(*) FROM "singers"'


def test_aggregate_rule_requires_column_evidence(tmp_path: Path):
    solver = RuleBasedDeterministicSolver(_db(tmp_path))
    assert solver.generate("What is the average age of singers?", "demo") == 'SELECT AVG("age") FROM "singers"'


def test_unsupported_multi_table_reasoning_abstains(tmp_path: Path):
    solver = RuleBasedDeterministicSolver(_db(tmp_path))
    assert solver.generate("Which singers joined the venue with the highest capacity?", "demo") is None
