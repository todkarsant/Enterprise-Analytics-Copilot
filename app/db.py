from pathlib import Path
import sqlite3
from typing import Any
from app.config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS store_week (
    store_id TEXT NOT NULL,
    week_start TEXT NOT NULL,
    region TEXT NOT NULL,
    sales REAL NOT NULL,
    orders INTEGER NOT NULL,
    promo_spend REAL NOT NULL,
    ads_spend REAL NOT NULL
);
"""

def get_connection():
    settings = get_settings()
    if settings.db_backend == "postgres":
        from sqlalchemy import create_engine
        engine = create_engine(settings.postgres_dsn, pool_pre_ping=True)
        return engine.raw_connection()
    path = Path(settings.sqlite_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_database() -> None:
    conn = get_connection()
    try:
        if get_settings().db_backend == "postgres":
            cur = conn.cursor(); cur.execute(SCHEMA); conn.commit(); cur.close()
        else:
            conn.executescript(SCHEMA); conn.commit()
    finally:
        conn.close()

def execute_readonly(sql: str, max_rows: int = 50) -> tuple[list[str], list[list[Any]]]:
    conn = get_connection()
    try:
        if get_settings().db_backend == "sqlite":
            conn.execute("PRAGMA query_only = ON")
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [d[0] for d in cursor.description or []]
        rows = [list(row) for row in cursor.fetchmany(max_rows)]
        return columns, rows
    finally:
        conn.close()
