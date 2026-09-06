import inspect

from research.evaluator import evaluate_state
from research.experiment import ActionEnvironment, p5_post_evidence_cascade, p6_evidence_policy, run_policy
from research.fixtures import cases


def test_policy_does_not_read_evaluator_only_answerable_field():
    source = inspect.getsource(p6_evidence_policy)
    assert "state.answerable" not in source


def test_controlled_fixture_exposes_heterogeneous_action_advantage():
    env = ActionEnvironment()
    ambiguous = cases()[3]
    risky = cases()[2]

    p5_amb = evaluate_state(run_policy(ambiguous, p5_post_evidence_cascade, env))
    p6_amb = evaluate_state(run_policy(ambiguous, p6_evidence_policy, env))
    p5_risk = evaluate_state(run_policy(risky, p5_post_evidence_cascade, env))
    p6_risk = evaluate_state(run_policy(risky, p6_evidence_policy, env))

    assert p6_amb.correct is True
    assert p6_amb.cost < p5_amb.cost
    assert p6_risk.correct is True
    assert p5_risk.correct is False


def test_no_result_is_claimed_as_a_paper_result():
    source = inspect.getsource(p6_evidence_policy)
    assert "paper contribution" in source
