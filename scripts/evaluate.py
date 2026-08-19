import json
from pathlib import Path

from app.db import init_database
from app.agent import run_agent


CASES = [
    {
        "question": "Which stores have the highest sales?",
        "expected_columns": ["store_id", "total_sales"],
        "expected_intent": "top_stores_by_sales",
    },
    {
        "question": "Show sales by region",
        "expected_columns": ["region", "total_sales"],
        "expected_intent": "sales_by_region",
    },
    {
        "question": "What is the average promo spend by region?",
        "expected_columns": ["region", "avg_promo_spend"],
        "expected_intent": "average_promo_spend_by_region",
    },
    {
        "question": "Why did sales decline?",
        "expected_columns": [],
        "expected_intent": "sales_decline_analysis",
    },
]


def main():
    init_database()
    results = []
    for case in CASES:
        result = run_agent(case["question"])
        columns_ok = set(case["expected_columns"]).issubset(set(result["columns"]))
        intent_ok = result["metrics"]["intent"] == case["expected_intent"]
        results.append(
            {
                "question": case["question"],
                "validation_pass": result["validation"]["valid"],
                "schema_contract_pass": columns_ok,
                "intent_pass": intent_ok,
                "rows": len(result["rows"]),
                "latency_ms": result["metrics"]["latency_ms"],
                "cache_hit": result["metrics"]["cache_hit"],
                "repair_attempts": result["metrics"]["repair_attempts"],
                "planner_used": result["metrics"]["planner_used"],
                "analysis_used": result["metrics"]["analysis_used"],
            }
        )

    out = Path("artifacts")
    out.mkdir(exist_ok=True)
    (out / "evaluation.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
