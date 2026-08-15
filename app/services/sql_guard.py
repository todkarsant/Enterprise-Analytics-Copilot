import re

import sqlglot
from sqlglot import exp

from app.services.schema_catalog import ALLOWED_COLUMNS, ALLOWED_TABLES

FORBIDDEN = {
    "insert", "update", "delete", "drop", "alter", "create", "attach", "detach",
    "pragma", "replace", "vacuum", "reindex", "truncate", "grant", "revoke",
}


def _table_alias_map(tree: exp.Select) -> tuple[dict[str, str], set[str]]:
    """Return physical/alias table names and derived-table aliases.

    For a physical table such as `store_week AS t1`, t1 maps to store_week.
    Derived-table aliases are tracked separately so their projected columns can
    be validated by the database/repair loop rather than being mistaken for
    physical tables.
    """
    physical_aliases: dict[str, str] = {}
    derived_aliases: set[str] = set()

    for table in tree.find_all(exp.Table):
        name = table.name
        alias = table.alias_or_name
        if name in ALLOWED_TABLES:
            physical_aliases[name] = name
            if alias:
                physical_aliases[alias] = name
        else:
            derived_aliases.add(alias or name)

    return physical_aliases, derived_aliases


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

    physical_aliases, derived_aliases = _table_alias_map(tree)

    physical_tables = {
        table.name
        for table in tree.find_all(exp.Table)
        if table.name in ALLOWED_TABLES
    }
    unknown_physical_tables = {
        table.name
        for table in tree.find_all(exp.Table)
        if table.name not in ALLOWED_TABLES
    }
    if unknown_physical_tables:
        return False, f"Unknown table(s): {', '.join(sorted(unknown_physical_tables))}.", None

    # An alias such as `store_week AS sw` creates two names for one physical
    # table, so alias count must NOT be used to detect a self-join. Count the
    # actual physical-table occurrences instead.
    physical_table_occurrences = [
        table.name
        for table in tree.find_all(exp.Table)
        if table.name in ALLOWED_TABLES
    ]

    # The current demo schema has one physical table. A self-join / derived
    # self-join adds complexity without adding information and is a common
    # failure mode for small local models. Ask the repair loop to simplify it.
    if len(physical_table_occurrences) > 1 and len(physical_tables) == 1:
        return (
            False,
            "Unnecessary self-join or repeated store_week reference detected. "
            "Use a direct aggregation over store_week without joining store_week to itself.",
            None,
        )

    select_aliases = {
        alias.alias
        for alias in tree.find_all(exp.Alias)
        if alias.alias
    }

    for column in tree.find_all(exp.Column):
        if column.table:
            qualifier = column.table
            if qualifier in physical_aliases:
                physical_table = physical_aliases[qualifier]
                if column.name != "*" and column.name not in ALLOWED_COLUMNS[physical_table]:
                    return False, f"Unknown column: {qualifier}.{column.name}.", None
                continue

            if qualifier in derived_aliases:
                return False, (
                    f"Unknown derived-table column reference: {qualifier}.{column.name}. "
                    "Use columns projected by the subquery or simplify to the base table."
                ), None

            return False, f"Unknown table reference: {qualifier}.", None

        if column.name in select_aliases:
            continue

        if column.name != "*" and column.name not in ALLOWED_COLUMNS["store_week"]:
            return False, f"Unknown column: {column.name}.", None

    normalized = tree.sql(dialect="sqlite")
    return True, "Read-only SELECT accepted.", normalized
