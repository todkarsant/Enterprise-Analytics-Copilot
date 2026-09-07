from research.spider_benchmark import BenchmarkEnvironment


def test_p5_does_not_escalate_for_common_relation_word_of():
    escalate, reason = BenchmarkEnvironment.needs_post_evidence_escalation(
        'What is the name of the singer?',
        'SELECT name FROM singer',
        1,
    )
    assert escalate is False
    assert reason is None


def test_p5_does_not_escalate_for_common_relation_word_in():
    escalate, reason = BenchmarkEnvironment.needs_post_evidence_escalation(
        'What is the name of the singer in the database?',
        'SELECT name FROM singer',
        1,
    )
    assert escalate is False
    assert reason is None


def test_p5_does_not_escalate_for_common_relation_word_for():
    escalate, reason = BenchmarkEnvironment.needs_post_evidence_escalation(
        'What is the phone number for the student?',
        'SELECT phone_number FROM students',
        1,
    )
    assert escalate is False
    assert reason is None


def test_p5_still_escalates_when_explicit_predicate_is_missing():
    escalate, reason = BenchmarkEnvironment.needs_post_evidence_escalation(
        'What is the phone number of the student named Timmothy Ward?',
        'SELECT cell_mobile_number FROM students',
        12,
    )
    assert escalate is True
    assert reason == 'question_predicate_not_reflected'
