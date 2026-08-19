from app.services.intent_planner import plan_question


def test_top_stores_by_sales():
    plan = plan_question("Which stores have the highest sales?")
    assert plan is not None
    assert plan.intent == "top_stores_by_sales"
    assert "SUM(sales)" in plan.sql
    assert "GROUP BY store_id" in plan.sql
    assert "ORDER BY total_sales DESC" in plan.sql
    assert plan.deterministic is True


def test_highest_number_of_orders_in_january():
    plan = plan_question("Which stores had the highest number of orders in January?")
    assert plan is not None
    assert plan.intent == "top_stores_by_orders"
    assert "SUM(orders)" in plan.sql
    assert "GROUP BY store_id" in plan.sql


def test_sales_by_region():
    plan = plan_question("Show sales by region")
    assert plan is not None
    assert plan.intent == "sales_by_region"


def test_unknown_question_falls_back_to_llm():
    assert plan_question("Explain why sales dropped") is None
