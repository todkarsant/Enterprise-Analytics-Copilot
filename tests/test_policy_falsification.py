import inspect

from research.experiment import ActionEnvironment, State, p0_always_llm, p1_deterministic_only, p2_static_hybrid, p3_query_complexity_router, p4_query_confidence_router, p5_post_evidence_cascade, run_policy
from research.fixtures import cases


POLICIES = [
    p0_always_llm,
    p1_deterministic_only,
    p2_static_hybrid,
    p3_query_complexity_router,
    p4_query_confidence_router,
    p5_post_evidence_cascade,
]


def test_baselines_do_not_read_evaluator_only_answerable_field():
    for policy in POLICIES:
        assert "state.answerable" not in inspect.getsource(policy)


def test_baselines_are_callable_and_terminate():
    env = ActionEnvironment()
    for policy in POLICIES:
        for case in cases():
            state = run_policy(case, policy, env)
            assert state.terminated is True
            assert len(state.actions) <= 8


def test_p5_is_post_evidence_not_query_only():
    source = inspect.getsource(p5_post_evidence_cascade)
    assert "execution_ok" in source
    assert "semantic_risk" in source
    assert "ambiguity" in source


def test_p5_low_risk_case_stops_without_extra_expensive_action():
    state = run_policy(cases()[0], p5_post_evidence_cascade, ActionEnvironment())
    assert state.actions == ["deterministic_execute", "abstain"]
    assert state.cost <= 0.05


def test_no_baseline_test_asserts_future_policy_superiority():
    for policy in POLICIES:
        source = inspect.getsource(policy)
        assert "paper contribution" not in source
        assert "superiority" not in source


def test_budget_exhaustion_is_explicit_and_not_correctness():
    state = State("hard request", semantic_risk=0.9, budget=0.05)
    result = run_policy(state, p5_post_evidence_cascade, ActionEnvironment())
    assert result.termination_reason in {"budget_exhausted", "policy_abstain"}
