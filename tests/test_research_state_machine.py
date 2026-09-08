from research.research_state_machine import check_transition, validate


def test_current_state_is_explicitly_repair_required():
    state = {
        'state': 'ARTIFACT_VALIDATED',
        'execution_run': '34252265013',
        'artifact_manifest': 'p6-ip-final-analysis-34252265013',
        'scientific_decision': 'REPAIR_REQUIRED',
    }
    assert validate(state) == []


def test_missing_evidence_fails_closed():
    state = {'state': 'ANALYZED'}
    errors = validate(state)
    assert 'ANALYZED requires artifact_manifest' in errors
    assert 'ANALYZED requires analysis_artifact' in errors


def test_invalid_transition_is_rejected():
    try:
        check_transition('EXECUTED', 'PAPER_LOCKED')
    except ValueError:
        pass
    else:
        raise AssertionError('invalid research-state transition was accepted')


def test_repair_path_is_explicit():
    check_transition('ANALYZED', 'REPAIR_REQUIRED')
    check_transition('REPAIR_REQUIRED', 'REPAIR_COMMITTED')
    check_transition('REPAIR_COMMITTED', 'CI_VALIDATED')
