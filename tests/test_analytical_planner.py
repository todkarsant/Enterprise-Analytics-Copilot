from app.services.analytical_planner import plan_analytical_question


def test_sales_decline_plan_is_conservative_and_multi_step():
    plan = plan_analytical_question("Why did sales decline?")
    assert plan is not None
    assert plan.intent == "sales_decline_analysis"
    assert len(plan.steps) == 2
    assert "latest_week" in plan.steps[0].sql
    assert "store_id" in plan.steps[1].sql


def test_non_decline_question_does_not_enter_analysis_path():
    assert plan_analytical_question("Which stores have the highest sales?") is None
