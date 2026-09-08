from research.p6_ip import Verification, decide_replacement, structural_ok, verify_challenger
from research.defensibility import DefensibilityTrace, validate_trace


def test_noneligible_case_keeps_incumbent():
    assert decide_replacement(intervention_eligible=False, verification=Verification(True, True, True)) == "KEEP"


def test_failed_verification_rejects_challenger():
    assert decide_replacement(intervention_eligible=True, verification=Verification(True, True, False)) == "REJECT_CHALLENGER"


def test_all_verification_gates_required():
    assert decide_replacement(intervention_eligible=True, verification=Verification(True, True, True)) == "REPLACE"
    assert verify_challenger("highest sales", "SELECT store_id FROM t ORDER BY sales DESC LIMIT 1", True, True).passed
    assert not verify_challenger("highest sales", "SELECT store_id FROM t", True, True).passed


def test_structural_checks_are_conservative():
    assert structural_ok("list stores in ascending order", "SELECT store_id FROM t ORDER BY store_id ASC")
    assert not structural_ok("list stores in ascending order", "SELECT store_id FROM t")


def test_defensibility_trace_is_auditable():
    trace = DefensibilityTrace(case_id="c1", policy="P6-IP", evidence={"row_count": 1}, evidence_provenance=["execution"], risk_reasons=["extremum_not_reflected"], verification={"passed": True}, authorization={"status": "not_applicable"}, decision="REPLACE", intervention=True, replacement=True)
    validate_trace(trace)
