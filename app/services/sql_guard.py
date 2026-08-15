import re
import sqlglot
from sqlglot import exp
from app.services.schema_catalog import ALLOWED_TABLES, ALLOWED_COLUMNS

FORBIDDEN = {
    "insert", "update", "delete", "drop", "alter", "create", "attach", "detach",
    "pragma", "replace", "vacuum", "reindex", "truncate", "grant", "revoke"
}


def validate_sql(sql: str, max_length: int = 4000) -> tuple[bool, str, str | None]:
    sql = sql.strip().strip("`").strip()
    if not sql:
        return False, "SQL is empty.", None
    if len(sql) > max_length:
        return False, "SQL exceeds the configured length limit.", None
    if ";" in sql.rstrip(";"):
        return False, "Multiple SQL statements are not allowed.", None

    lowered = sql.lower()
    tokens = set(re.findall(r"[a-z_]+", lowered))
    forbidden = sorted(tokens.intersection(FORBIDDEN))
    if forbidden:
        return False, f"Forbidden SQL operation: {', '.join(forbidden)}.", None
    if not lowered.startswith("select"):
        return False, "Only SELECT statements are allowed.", None

    try:
        tree = sqlglot.parse_one(sql, read="sqlite")
    except Exception as exc:
        return False, f"SQL parser rejected the statement: {exc}", None

    if not isinstance(tree, exp.Select):
        return False, "Only SELECT statements are accepted.", None

    tables = {t.name for t in tree.find_all(exp.Table)}
    unknown_tables = tables - ALLOWED_TABLES
    if unknown_tables:
        return False, f"Unknown table(s): {', '.join(sorted(unknown_tables))}.", None

    for column in tree.find_all(exp.Column):
        table = column.table or "store_week"
        if table not in ALLOWED_COLUMNS:
            return False, f"Unknown table reference: {table}.", None
        if column.name != "*" and column.name not in ALLOWED_COLUMNS[table]:
            return False, f"Unknown column: {column.name}.", None

    normalized = tree.sql(dialect="sqlite")
    return True, "Read-only SELECT accepted.", normalized
