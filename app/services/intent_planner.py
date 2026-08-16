import re
from dataclasses import dataclass
from calendar import month_name


MONTHS = {m.lower(): i for i, m in enumerate(month_name) if m}


@dataclass
class SQLPlan:
    sql: str
    intent: str
    deterministic: bool
    reason: str


def _month_filter(month_number: int) -> str:
    """Build a dataset-relative month filter using the latest dataset year."""
    next_month = month_number + 1
    if next_month <= 12:
        return (
            "week_start >= date(strftime('%Y', (SELECT MAX(week_start) FROM store_week)) "
            f"|| '-{month_number:02d}-01') "
            "AND week_start < date(strftime('%Y', (SELECT MAX(week_start) FROM store_week)) "
            f"|| '-{next_month:02d}-01')"
        )
    return (
        "week_start >= date(strftime('%Y', (SELECT MAX(week_start) FROM store_week)) "
        f"|| '-{month_number:02d}-01') "
        "AND week_start < date(strftime('%Y', (SELECT MAX(week_start) FROM store_week)) "
        "|| '-01-01', '+1 year')"
    )


def plan_question(question: str) -> SQLPlan | None:
    """Handle high-confidence analytical intents deterministically.

    The planner is intentionally conservative. If it cannot classify a question
    with high confidence, it returns None and the LLM remains responsible for
    general NL2SQL.
    """
    q = re.sub(r"\s+", " ", question.lower()).strip()

    # Top/highest sales by store.
    if (
        ("highest sales" in q)
        or ("top stores" in q and "sales" in q)
        or ("highest revenue" in q)
        or ("top stores" in q and "revenue" in q)
    ):
        return SQLPlan(
            sql=(
                "SELECT store_id, SUM(sales) AS total_sales "
                "FROM store_week "
                "GROUP BY store_id "
                "ORDER BY total_sales DESC "
                "LIMIT 10"
            ),
            intent="top_stores_by_sales",
            deterministic=True,
            reason="High-confidence top-store sales intent.",
        )

    # Top/highest orders, including "highest number of orders".
    if (
        ("highest orders" in q)
        or ("most orders" in q)
        or ("highest number of orders" in q)
        or ("highest number" in q and "order" in q)
        or ("top stores" in q and "orders" in q)
    ):
        month_number = next(
            (num for name, num in MONTHS.items() if re.search(rf"\b{name}\b", q)),
            None,
        )
        where = f" WHERE {_month_filter(month_number)}" if month_number else ""
        sql = (
            "SELECT store_id, SUM(orders) AS total_orders "
            "FROM store_week"
            f"{where} "
            "GROUP BY store_id "
            "ORDER BY total_orders DESC "
            "LIMIT 10"
        )
        return SQLPlan(
            sql=sql,
            intent="top_stores_by_orders",
            deterministic=True,
            reason="High-confidence top-store order intent.",
        )

    # Sales/revenue by region.
    if (
        ("sales by region" in q)
        or ("revenue by region" in q)
        or ("regional sales" in q)
    ):
        return SQLPlan(
            sql=(
                "SELECT region, SUM(sales) AS total_sales "
                "FROM store_week "
                "GROUP BY region "
                "ORDER BY total_sales DESC"
            ),
            intent="sales_by_region",
            deterministic=True,
            reason="High-confidence regional sales intent.",
        )

    # Total sales for the previous complete month relative to the dataset.
    if "total sales" in q and "last month" in q:
        return SQLPlan(
            sql=(
                "SELECT SUM(sales) AS total_sales "
                "FROM store_week "
                "WHERE week_start >= date((SELECT MAX(week_start) FROM store_week), "
                "'start of month', '-1 month') "
                "AND week_start < date((SELECT MAX(week_start) FROM store_week), "
                "'start of month')"
            ),
            intent="total_sales_last_month",
            deterministic=True,
            reason="High-confidence relative-month sales intent.",
        )

    # Average promotion spend by region.
    if "average promo spend" in q:
        return SQLPlan(
            sql=(
                "SELECT region, AVG(promo_spend) AS avg_promo_spend "
                "FROM store_week "
                "GROUP BY region "
                "ORDER BY avg_promo_spend DESC"
            ),
            intent="average_promo_spend_by_region",
            deterministic=True,
            reason="High-confidence promotion-spend intent.",
        )

    # Advertising spend by region.
    if "ads spend" in q or "advertising spend" in q:
        return SQLPlan(
            sql=(
                "SELECT region, SUM(ads_spend) AS total_ads_spend "
                "FROM store_week "
                "GROUP BY region "
                "ORDER BY total_ads_spend DESC"
            ),
            intent="ads_spend_by_region",
            deterministic=True,
            reason="High-confidence advertising-spend intent.",
        )

    return None
