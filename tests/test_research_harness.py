from research.evaluator import cost_at_reliability, coverage, evaluate_state, reliability
from research.experiment import ActionEnvironment, State, p5_post_evidence_cascade, p6_evidence_policy, run_policy
from research.fixtures import cases


def test_policy_state_never_contains_reference_outcomes():
    state = State("Show sales by region", semantic_risk=0.1)
    result = run_policy(state, p6_evidence_policy, ActionEnvironment())
    assert not hasattr(result, "reference_sql")
    assert not hasattr(result, "gold_result")


def test_p6_uses_heterogeneous_actions_for_distinct_failure_modes():
    env = ActionEnvironment()
    ambiguous = run_policy(cases()[3], p6_evidence_policy, env)
    risky = run_policy(cases()[2], p6_evidence_policy, env)
    assert "clarify" in ambiguous.actions
    assert "agentic_escalation" in risky.actions


def test_p6_can_terminate_after_low_risk_deterministic_evidence():
    state = run_policy(cases()[0], p6_evidence_policy, ActionEnvironment())
    assert state.actions == ["deterministic_execute"]
    assert evaluate_state(state).correct is True


def test_p6_rejects_governance_violation_without_claiming_success():
    state = run_policy(cases()[5], p6_evidence_policy, ActionEnvironment())
    assert evaluate_state(state).correct is False


def test_unanswerable_case_rewards_abstention():
    state = run_policy(cases()[4], p6_evidence_policy, ActionEnvironment())
    outcome = evaluate_state(state)
    assert outcome.correct is True


def test_reliability_and_coverage_are_separate():
    env = ActionEnvironment()
    outcomes = [evaluate_state(run_policy(c, p6_evidence_policy, env)) for c in cases()]
    assert 0.0 <= reliability(outcomes) <= 1.0
    assert 0.0 <= coverage(outcomes) <= 1.0


def test_cost_target_returns_none_when_target_is_unreachable():
    outcomes = [evaluate_state(State("q", answerable=False))]
    assert cost_at_reliability(outcomes, 1.01) is None
