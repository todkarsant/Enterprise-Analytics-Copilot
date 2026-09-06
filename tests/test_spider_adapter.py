import json
import sqlite3

from research.spider_adapter import SpiderDataset, dataset_manifest


def make_dataset(tmp_path):
    root = tmp_path / "spider"
    (root / "database" / "toy").mkdir(parents=True)
    (root / "dev.json").write_text(
        json.dumps([{"question": "How many rows?", "db_id": "toy", "query": "SELECT COUNT(*) FROM items"}]),
        encoding="utf-8",
    )
    (root / "tables.json").write_text(
        json.dumps([{
            "db_id": "toy",
            "table_names_original": ["items"],
            "table_names": ["items"],
            "column_names_original": [[-1, "*"], [0, "id"]],
            "column_names": [[-1, "*"], [0, "id"]],
            "column_types": ["text", "number"],
            "foreign_keys": [],
            "primary_keys": [1],
        }]),
        encoding="utf-8",
    )
    db = root / "database" / "toy" / "toy.sqlite"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY)")
        conn.executemany("INSERT INTO items(id) VALUES (?)", [(1,), (2,)])
        conn.commit()
    return root


def test_adapter_validates_and_keeps_gold_out_of_schema(tmp_path):
    root = make_dataset(tmp_path)
    dataset = SpiderDataset(root)
    dataset.validate()
    case = next(dataset.cases())
    assert case.question == "How many rows?"
    assert case.db_id == "toy"
    assert case.gold_sql == "SELECT COUNT(*) FROM items"
    schema = dataset.schemas()["toy"]
    assert schema.table_names_original == ("items",)
    assert not hasattr(schema, "gold_sql")


def test_adapter_executes_read_only_sql_and_manifests_files(tmp_path):
    root = make_dataset(tmp_path)
    dataset = SpiderDataset(root)
    rows, columns = dataset.execute("toy", "SELECT COUNT(*) AS n FROM items")
    assert rows == [(2,)]
    assert columns == ["n"]
    manifest = dataset_manifest(root)
    assert manifest["benchmark"] == "Spider 1.0"
    assert manifest["split"] == "dev"
    assert all(len(item["sha256"]) == 64 for item in manifest["files"])
