import re
from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisStep:
    name: str
    sql: str
    purpose: str


@dataclass(frozen=True)
class AnalysisPlan:
    intent: str
    assumption: str
    steps: tuple[AnalysisStep, ...]


DECLINE_PATTERNS = (
    "why did sales decline",
    "why did sales drop",
    "why have sales declined",
    "why have sales dropped",
    "what caused sales decline",
    "what caused the sales decline",
    "what caused sales to decline",
    "what drove the sales decline",
    "what drove sales decline",
    "why is sales declining",
)


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", question.lower()).strip(" ?.!\n\t")


def plan_analytical_question(question: str) -> AnalysisPlan | None:
    """Return a conservative multi-step analytical plan for causal/comparison questions.

    The planner does not claim causal inference. For the demo dataset, "why did
    sales decline?" is operationalized as latest available week vs previous
    available week, followed by store-level contribution analysis.
    """
    q = _normalise(question)
    if not any(pattern in q for pattern in DECLINE_PATTERNS):
        return None

    comparison_sql = """
WITH base AS (
    SELECT week_start, sales
    FROM store_week
),
periods AS (
    SELECT
        MAX(week_start) AS latest_week,
        MAX(CASE
            WHEN week_start < (SELECT MAX(week_start) FROM base) THEN week_start
        END) AS previous_week
    FROM base
),
weekly AS (
    SELECT week_start, SUM(sales) AS total_sales
    FROM base
    GROUP BY week_start
)
SELECT
    p.latest_week,
    p.previous_week,
    l.total_sales AS latest_sales,
    pr.total_sales AS previous_sales,
    ROUND(l.total_sales - pr.total_sales, 2) AS sales_change,
    ROUND(
        (l.total_sales - pr.total_sales) * 100.0 / NULLIF(pr.total_sales, 0),
        2
    ) AS pct_change
FROM periods p
JOIN weekly l ON l.week_start = p.latest_week
JOIN weekly pr ON pr.week_start = p.previous_week
""".strip()

    contributor_sql = """
WITH base AS (
    SELECT store_id, week_start, sales
    FROM store_week
),
periods AS (
    SELECT
        MAX(week_start) AS latest_week,
        MAX(CASE
            WHEN week_start < (SELECT MAX(week_start) FROM base) THEN week_start
        END) AS previous_week
    FROM base
),
deltas AS (
    SELECT
        b.store_id,
        SUM(CASE WHEN b.week_start = p.latest_week THEN b.sales ELSE 0 END) AS latest_sales,
        SUM(CASE WHEN b.week_start = p.previous_week THEN b.sales ELSE 0 END) AS previous_sales
    FROM base b
    CROSS JOIN periods p
    GROUP BY b.store_id
)
SELECT
    store_id,
    latest_sales,
    previous_sales,
    ROUND(latest_sales - previous_sales, 2) AS sales_change,
    ROUND(
        (latest_sales - previous_sales) * 100.0 / NULLIF(previous_sales, 0),
        2
    ) AS pct_change
FROM deltas
ORDER BY sales_change ASC
LIMIT 5
""".strip()

    return AnalysisPlan(
        intent="sales_decline_analysis",
        assumption=(
            "For this weekly dataset, compare the latest available week with the "
            "immediately preceding available week; then rank store-level changes."
        ),
        steps=(
            AnalysisStep(
                name="period_comparison",
                sql=comparison_sql,
                purpose="Determine whether the latest available week actually declined versus the previous week.",
            ),
            AnalysisStep(
                name="store_contributors",
                sql=contributor_sql,
                purpose="Identify the stores contributing most negatively or positively to the change.",
            ),
        ),
    )
