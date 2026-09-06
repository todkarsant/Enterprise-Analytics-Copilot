"""Read-only adapter for the official Spider 1.0 development split.

This module deliberately does not download or vendor benchmark data. The dataset
must be supplied locally under ``data/spider`` (or via ``SPIDER_ROOT``).

Important research boundary:
- gold SQL is carried as evaluator metadata only;
- policy code receives only the question and database/schema metadata;
- this adapter does not manufacture labels or model-quality scores;
- no benchmark result is produced until a real prediction system is connected.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Iterator


DEFAULT_ROOT = Path("data/spider")


@dataclass(frozen=True)
class SpiderCase:
    question: str
    db_id: str
    gold_sql: str
    question_index: int


@dataclass(frozen=True)
class SpiderSchema:
    db_id: str
    table_names_original: tuple[str, ...]
    column_names_original: tuple[tuple[int, str], ...]
    column_types: tuple[str, ...]
    primary_keys: tuple[int, ...]
    foreign_keys: tuple[tuple[int, int], ...]


class SpiderDataset:
    """Validated, deterministic view of a Spider 1.0 checkout."""

    def __init__(self, root: str | Path = DEFAULT_ROOT):
        self.root = Path(root)
        self.dev_path = self.root / "dev.json"
        self.tables_path = self.root / "tables.json"
        self.database_dir = self.root / "database"

    def validate(self) -> None:
        missing = [str(p) for p in (self.dev_path, self.tables_path, self.database_dir) if not p.exists()]
        if missing:
            raise FileNotFoundError(
                "Spider 1.0 is not installed. Missing: " + ", ".join(missing)
            )

        dev = json.loads(self.dev_path.read_text(encoding="utf-8"))
        tables = json.loads(self.tables_path.read_text(encoding="utf-8"))
        if not isinstance(dev, list) or not dev:
            raise ValueError("dev.json must contain a non-empty list")
        if not isinstance(tables, list) or not tables:
            raise ValueError("tables.json must contain a non-empty list")

        schema_ids = {row.get("db_id") for row in tables}
        for i, row in enumerate(dev):
            for field in ("question", "db_id", "query"):
                if field not in row:
                    raise ValueError(f"dev.json row {i} missing required field: {field}")
            if row["db_id"] not in schema_ids:
                raise ValueError(f"dev.json row {i} references unknown db_id={row['db_id']!r}")

        for db_id in sorted(schema_ids):
            db_path = self.database_dir / db_id / f"{db_id}.sqlite"
            if not db_path.exists():
                raise FileNotFoundError(f"Missing SQLite database for {db_id}: {db_path}")

    def cases(self) -> Iterator[SpiderCase]:
        self.validate()
        rows = json.loads(self.dev_path.read_text(encoding="utf-8"))
        for i, row in enumerate(rows):
            yield SpiderCase(
                question=row["question"],
                db_id=row["db_id"],
                gold_sql=row["query"],
                question_index=i,
            )

    def schemas(self) -> dict[str, SpiderSchema]:
        self.validate()
        rows = json.loads(self.tables_path.read_text(encoding="utf-8"))
        result: dict[str, SpiderSchema] = {}
        for row in rows:
            result[row["db_id"]] = SpiderSchema(
                db_id=row["db_id"],
                table_names_original=tuple(row["table_names_original"]),
                column_names_original=tuple(tuple(x) for x in row["column_names_original"]),
                column_types=tuple(row["column_types"]),
                primary_keys=tuple(row["primary_keys"]),
                foreign_keys=tuple(tuple(x) for x in row["foreign_keys"]),
            )
        return result

    def database_path(self, db_id: str) -> Path:
        path = self.database_dir / db_id / f"{db_id}.sqlite"
        if not path.exists():
            raise FileNotFoundError(path)
        return path

    def execute(self, db_id: str, sql: str) -> tuple[list[tuple], list[str]]:
        """Execute one candidate SQL in a read-only SQLite connection."""
        path = self.database_path(db_id)
        uri = f"file:{path.resolve()}?mode=ro"
        with sqlite3.connect(uri, uri=True) as conn:
            cursor = conn.execute(sql)
            columns = [d[0] for d in cursor.description or ()]
            rows = cursor.fetchall()
        return rows, columns


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_manifest(root: str | Path = DEFAULT_ROOT) -> dict:
    """Return reproducibility metadata without modifying benchmark data."""
    dataset = SpiderDataset(root)
    dataset.validate()
    files = [dataset.dev_path, dataset.tables_path]
    files.extend(sorted(dataset.database_dir.glob("*/" + "*.sqlite")))
    return {
        "benchmark": "Spider 1.0",
        "split": "dev",
        "source": "https://yale-lily.github.io/spider",
        "data_license": "CC BY-SA 4.0",
        "files": [
            {"path": str(p.relative_to(dataset.root)), "sha256": sha256_file(p), "bytes": p.stat().st_size}
            for p in files
        ],
    }
