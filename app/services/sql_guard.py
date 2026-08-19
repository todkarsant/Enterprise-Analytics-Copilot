import re

import sqlglot
from sqlglot import exp

from app.services.schema_catalog import ALLOWED_COLUMNS, ALLOWED_TABLES

FORBIDDEN = {
    "insert", "update", "delete", "drop", "alter", "create", "attach", "detach",
    "pragma", "replace", "vacuum", "reindex", "truncate", "grant", "revoke",
}


def _table_alias_map(tree: exp.Expression) -> tuple[dict[str, str], set[str]]:
    physical_aliases: dict[str, str] = {}
    derived_aliases: set[str] = set()

    # First collect CTE names. A later FROM periods AS p is a reference to a
    # derived relation, not a physical table in the allow-listed schema.
    cte_names: set[str] = set()
    for cte in tree.find_all(exp.CTE):
        name = cte.alias_or_name
        if name:
            cte_names.add(name)
            derived_aliases.add(name)

    for table in tree.find_all(exp.Table):
        name = table.name
        alias = table.alias_or_name
        if name in ALLOWED_TABLES:
            physical_aliases[name] = name
            if alias:
                physical_aliases[alias] = name
        elif name in cte_names:
            # Both the CTE name and its table alias are valid qualifiers.
            derived_aliases.add(name)
            if alias:
                derived_aliases.add(alias)

    # Derived subqueries are validated internally; their aliases are valid
    # outer-scope relation qualifiers.
    for subquery in tree.find_all(exp.Subquery):
        alias = subquery.alias_or_name
        if alias:
            derived_aliases.add(alias)

    return physical_aliases, derived_aliases


def _derived_output_columns(tree: exp.Expression) -> set[str]:
    """Collect columns projected by CTEs/derived SELECTs.

    These names are valid in outer query scopes even though they are not physical
    columns in the base schema. This is used only for trusted deterministic
    analytical plans.
    """
    outputs: set[str] = set()
    for cte in tree.find_all(exp.CTE):
        query = cte.this
        if isinstance(query, exp.Subquery):
            query = query.this
        if isinstance(query, exp.Select):
            for expression in query.expressions:
                if isinstance(expression, exp.Alias):
                    outputs.add(expression.alias)
                elif isinstance(expression, exp.Column):
                    outputs.add(expression.name)
    for subquery in tree.find_all(exp.Subquery):
        query = subquery.this
        if isinstance(query, exp.Select):
            for expression in query.expressions:
                if isinstance(expression, exp.Alias):
                    outputs.add(expression.alias)
                elif isinstance(expression, exp.Column):
                    outputs.add(expression.name)
    return outputs


def validate_sql(
    sql: str,
    max_length: int = 4000,
    *,
    allow_repeated_table_references: bool = False,
) -> tuple[bool, str, str | None]:
    """Validate one read-only SQL statement against the known schema.

    The default path is intentionally strict for LLM-generated SQL and rejects
    repeated references to the single demo fact table. Trusted deterministic
    analytical plans can opt into repeated references while remaining subject
    to parsing, allow-list, and read-only checks.
    """
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
    if not lowered.startswith(("select", "with")):
        return False, "Only read-only SELECT statements are accepted.", None

    try:
        tree = sqlglot.parse_one(sql, read="sqlite")
    except Exception as exc:
        return False, f"SQL parser rejected the statement: {exc}", None

    select = tree.find(exp.Select)
    if select is None:
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
        if table.name not in ALLOWED_TABLES and table.name not in derived_aliases
    }
    if unknown_physical_tables:
        return False, f"Unknown table(s): {', '.join(sorted(unknown_physical_tables))}.", None

    physical_table_occurrences = [
        table.name for table in tree.find_all(exp.Table) if table.name in ALLOWED_TABLES
    ]
    if (
        not allow_repeated_table_references
        and len(physical_table_occurrences) > 1
        and len(physical_tables) == 1
    ):
        return (
            False,
            "Unnecessary self-join or repeated store_week reference detected. "
            "Use a direct aggregation over store_week without joining store_week to itself.",
            None,
        )

    select_aliases = {
        alias.alias for alias in tree.find_all(exp.Alias) if alias.alias
    }
    derived_output_columns = _derived_output_columns(tree) if allow_repeated_table_references else set()

    for column in tree.find_all(exp.Column):
        if column.table:
            qualifier = column.table
            if qualifier in physical_aliases:
                physical_table = physical_aliases[qualifier]
                if column.name != "*" and column.name not in ALLOWED_COLUMNS[physical_table]:
                    return False, f"Unknown column: {qualifier}.{column.name}.", None
                continue
            if qualifier in derived_aliases:
                continue
            return False, f"Unknown table reference: {qualifier}.", None

        if column.name in select_aliases or column.name in derived_output_columns:
            continue
        if column.name != "*" and column.name not in ALLOWED_COLUMNS["store_week"]:
            # Columns belonging to CTEs/subqueries are handled through their
            # qualified aliases. Unqualified names still need base-schema checks.
            return False, f"Unknown column: {column.name}.", None

    normalized = tree.sql(dialect="sqlite")
    return True, "Read-only SELECT accepted.", normalized
