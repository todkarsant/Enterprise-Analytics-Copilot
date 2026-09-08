from research.p5_selector import assess_strict_evidence


def test_strict_selector_catches_missing_requested_name():
    escalate, reason = assess_strict_evidence(
        'List the names of conductors in ascending order of age.',
        'SELECT Age FROM conductor',
        12,
    )
    assert escalate is True
    assert reason == 'ordering_not_reflected'


def test_strict_selector_catches_missing_aggregate():
    escalate, reason = assess_strict_evidence(
        'What is the average age of singers?',
        'SELECT Age FROM singer',
        30,
    )
    assert escalate is True
    assert reason == 'aggregation_not_reflected'


def test_strict_selector_accepts_structurally_consistent_query():
    escalate, reason = assess_strict_evidence(
        'Which singer has the highest age?',
        'SELECT Name FROM singer ORDER BY Age DESC LIMIT 1',
        1,
    )
    assert escalate is False
    assert reason is None


def test_strict_selector_ignores_english_contractions():
    escalate, reason = assess_strict_evidence(
        "What is the singer's name?",
        'SELECT Name FROM singer',
        1,
    )
    assert escalate is False
    assert reason is None


def test_strict_selector_has_no_label_dependency():
    # The public function accepts only observable execution-time evidence.
    assert assess_strict_evidence.__code__.co_argcount == 3
