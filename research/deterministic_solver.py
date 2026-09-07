from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


_STOPWORDS = {
    "a", "an", "the", "of", "to", "for", "from", "in", "on", "at", "by",
    "is", "are", "was", "were", "be", "been", "what", "which", "who", "where",
    "when", "how", "many", "much", "does", "do", "did", "that", "this", "these",
    "those", "with", "and", "or", "all", "each", "there", "their", "its", "it",
    "show", "list", "give", "find", "tell", "me", "please", "name", "names",
    "number", "count", "average", "avg", "maximum", "minimum", "max", "min", "sum",
    "total", "most", "least", "highest", "lowest", "largest", "smallest", "top",
    "bottom", "records", "record", "information", "information", "value", "values",
}


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _tokens(value: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", value.lower()) if t not in _STOPWORDS}


def _singular(value: str) -> str:
    if value.endswith("ies"):
        return value[:-3] + "y"
    if value.endswith("s") and not value.endswith("ss"):
        return value[:-1]
    return value


@dataclass(frozen=True)
class Column:
    table: str
    name: str
    sql_type: str


class RuleBasedDeterministicSolver:
    """Frozen, schema-aware SQL baseline with no question->gold mapping.

    The solver deliberately supports only conservative single-table patterns.
    It uses the live schema and lexical question evidence, never Spider gold SQL,
    evaluator labels, or benchmark outcomes. Unsupported questions return None.
    """

    def __init__(self, database_dir: Path):
        self.database_dir = Path(database_dir)

    def _db_path(self, db_id: str) -> Path:
        candidates = [
            self.database_dir / db_id / f"{db_id}.sqlite",
            self.database_dir / db_id / f"{db_id}.db",
            self.database_dir / f"{db_id}.sqlite",
            self.database_dir / f"{db_id}.db",
        ]
        for path in candidates:
            if path.exists():
                return path
        raise FileNotFoundError(f"No SQLite database found for db_id={db_id}")

    def _schema(self, db_id: str) -> tuple[list[str], list[Column]]:
        with sqlite3.connect(self._db_path(db_id)) as con:
            tables = [
                row[0]
                for row in con.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%' ORDER BY name"
                ).fetchall()
            ]
            columns: list[Column] = []
            for table in tables:
                for name, sql_type in con.execute(
                    f'PRAGMA table_info("{table.replace(chr(34), chr(34) * 2)}")'
                ).fetchall():
                    columns.append(Column(table, name, sql_type or ""))
        return tables, columns

    @staticmethod
    def _score_name(question: str, name: str) -> int:
        q = _tokens(question)
        n = _tokens(name)
        if not n:
            return 0
        score = len(q & n) * 3
        joined = _norm(name)
        qnorm = _norm(question)
        if joined and joined in qnorm:
            score += 5
        for token in n:
            if _singular(token) in {_singular(x) for x in q}:
                score += 1
        return score

    def _choose_table(self, question: str, tables: Iterable[str], columns: list[Column]) -> str | None:
        scored = []
        for table in tables:
            score = self._score_name(question, table)
            score += max((self._score_name(question, c.name) for c in columns if c.table == table), default=0) // 4
            scored.append((score, table))
        scored.sort(reverse=True)
        if not scored or scored[0][0] <= 0:
            if len(scored) == 1:
                return scored[0][1]
            return None
        if len(scored) > 1 and scored[0][0] == scored[1][0]:
            return None
        return scored[0][1]

    def _choose_column(self, question: str, columns: list[Column], table: str) -> Column | None:
        candidates = [c for c in columns if c.table == table]
        scored = sorted(((self._score_name(question, c.name), c) for c in candidates), reverse=True, key=lambda x: (x[0], x[1].name))
        if not scored or scored[0][0] <= 0:
            return None
        if len(scored) > 1 and scored[0][0] == scored[1][0]:
            return None
        return scored[0][1]

    @staticmethod
    def _aggregate(question: str) -> str | None:
        q = question.lower()
        if any(p in q for p in ("how many", "number of", "count of", "how much")):
            return "count"
        if any(p in q for p in ("average", "avg")):
            return "avg"
        if any(p in q for p in ("maximum", "max", "highest", "largest")):
            return "max"
        if any(p in q for p in ("minimum", "min", "lowest", "smallest")):
            return "min"
        if any(p in q for p in ("sum of", "total")):
            return "sum"
        return None

    @staticmethod
    def _ordering(question: str) -> str | None:
        q = question.lower()
        if any(p in q for p in ("most", "highest", "largest", "top")):
            return "DESC"
        if any(p in q for p in ("least", "lowest", "smallest", "bottom")):
            return "ASC"
        return None

    def generate(self, question: str, db_id: str) -> str | None:
        tables, columns = self._schema(db_id)
        table = self._choose_table(question, tables, columns)
        if not table:
            return None

        aggregate = self._aggregate(question)
        if aggregate == "count":
            return f'SELECT COUNT(*) FROM "{table.replace(chr(34), chr(34) * 2)}"'

        column = self._choose_column(question, columns, table)
        ordering = self._ordering(question)

        if aggregate and column:
            return (
                f'SELECT {aggregate.upper()}("{column.name.replace(chr(34), chr(34) * 2)}") '
                f'FROM "{table.replace(chr(34), chr(34) * 2)}"'
            )

        if ordering and column:
            return (
                f'SELECT "{column.name.replace(chr(34), chr(34) * 2)}" '
                f'FROM "{table.replace(chr(34), chr(34) * 2)}" '
                f'ORDER BY "{column.name.replace(chr(34), chr(34) * 2)}" {ordering} LIMIT 1'
            )

        if column and any(k in question.lower() for k in ("what is", "which", "list", "show", "names", "name")):
            return (
                f'SELECT "{column.name.replace(chr(34), chr(34) * 2)}" '
                f'FROM "{table.replace(chr(34), chr(34) * 2)}"'
            )

        return None
