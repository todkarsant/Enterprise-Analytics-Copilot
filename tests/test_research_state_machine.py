from pathlib import Path

from research.research_state_machine import check_transition, validate

ROOT = Path(__file__).resolve().parents[1]


def test_current_state_is_explicitly_repair_required():
    state = {
        'state': 'REPAIR_REQUIRED',
        'previous_state': 'ARTIFACT_VALIDATED',
        'repair_reason': 'invalid comparator labels',
    }
    assert validate(state, ROOT) == []


def test_missing_evidence_fails_closed():
    state = {'state': 'ANALYZED'}
    errors = validate(state, ROOT)
    assert 'ANALYZED requires artifact_manifest' in errors
    assert 'ANALYZED requires analysis_artifact' in errors


def test_repository_references_must_resolve():
    state = {
        'state': 'IMPLEMENTED',
        'design_ref': 'does/not/exist.md',
        'implementation_ref': 'research/p6_ip_runner.py',
    }
    errors = validate(state, ROOT)
    assert any('design_ref does not resolve' in e for e in errors)


def test_invalid_transition_is_rejected():
    try:
        check_transition('EXECUTED', 'PAPER_LOCKED')
    except ValueError:
        pass
    else:
        raise AssertionError('invalid research-state transition was accepted')


def test_previous_state_transition_is_enforced():
    state = {
        'state': 'PAPER_LOCKED',
        'previous_state': 'EXECUTED',
        'execution_run': '34252265013',
        'artifact_manifest': 'manifest',
        'analysis_artifact': 'analysis',
        'scientific_decision': 'PROCEED',
        'paper_evidence_ref': 'docs/PROJECT1_P6_IP_DESIGN.md',
    }
    errors = validate(state, ROOT)
    assert any('invalid research-state transition' in e for e in errors)


def test_repair_path_is_explicit():
    check_transition('ANALYZED', 'REPAIR_REQUIRED')
    check_transition('REPAIR_REQUIRED', 'REPAIR_COMMITTED')
    check_transition('REPAIR_COMMITTED', 'CI_VALIDATED')
