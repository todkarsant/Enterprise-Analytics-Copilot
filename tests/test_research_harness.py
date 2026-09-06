from research.evaluator import cost_at_reliability, coverage, evaluate_state, reliability
from research.experiment import ActionEnvironment, State, p5_post_evidence_cascade, run_policy
from research.fixtures import cases


def test_policy_state_never_contains_reference_outcomes():
    state = State("Show sales by region", semantic_risk=0.1)
    result = run_policy(state, p5_post_evidence_cascade, ActionEnvironment())
    assert not hasattr(result, "reference_sql")
    assert not hasattr(result, "gold_result")


def test_p5_can_terminate_after_low_risk_evidence():
    state = run_policy(cases()[0], p5_post_evidence_cascade, ActionEnvironment())
    assert state.actions == ["deterministic_execute"]
    assert evaluate_state(state).correct is True


def test_governance_violation_is_not_marked_correct():
    state = run_policy(cases()[5], p5_post_evidence_cascade, ActionEnvironment())
    assert evaluate_state(state).correct is False


def test_unanswerable_case_rewards_explicit_abstention():
    # This is a harness property only; answerability remains evaluator-only.
    state = State("unanswerable request", answerable=False)
    state.actions.append("abstain")
    outcome = evaluate_state(state)
    assert outcome.correct is True
    assert outcome.covered is False


def test_reliability_and_coverage_are_separate():
    env = ActionEnvironment()
    outcomes = [evaluate_state(run_policy(c, p5_post_evidence_cascade, env)) for c in cases()]
    assert 0.0 <= reliability(outcomes) <= 1.0
    assert 0.0 <= coverage(outcomes) <= 1.0


def test_cost_target_returns_none_when_target_is_unreachable():
    outcomes = [evaluate_state(State("q", answerable=False))]
    assert cost_at_reliability(outcomes, 1.01) is None
