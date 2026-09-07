from research.spider_benchmark import BenchmarkEnvironment


def test_p5_escalates_when_predicate_is_missing_from_sql():
    escalate, reason = BenchmarkEnvironment.needs_post_evidence_escalation(
        'What is the phone number of the student named Timmothy Ward?',
        'SELECT cell_mobile_number FROM students',
        12,
    )
    assert escalate is True
    assert reason == 'question_predicate_not_reflected'


def test_p5_escalates_multirow_singleton_request():
    escalate, reason = BenchmarkEnvironment.needs_post_evidence_escalation(
        'Which singer has the highest age?',
        'SELECT age FROM singer',
        30,
    )
    assert escalate is True
    assert reason == 'multirow_singleton_request'


def test_p5_does_not_escalate_simple_direct_result():
    escalate, reason = BenchmarkEnvironment.needs_post_evidence_escalation(
        'What is the name of the singer?',
        'SELECT name FROM singer',
        1,
    )
    assert escalate is False
    assert reason is None
