from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.analyze_p6_ip import intervention, load_p0


def write_payload(path: Path, label) -> None:
    path.write_text(json.dumps({"traces": [{"question": "q", "db_id": "db", "official_execution_correct": label}]}))


def test_missing_official_label_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "p0.json"
    write_payload(path, None)
    with pytest.raises(ValueError, match="refusing to coerce"):
        load_p0(path)


def test_boolean_official_label_is_accepted(tmp_path: Path) -> None:
    path = tmp_path / "p0.json"
    write_payload(path, True)
    rows = load_p0(path)
    assert rows[("q", "db")]["official_execution_correct"] is True


def test_non_boolean_official_label_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "p0.json"
    write_payload(path, "1")
    with pytest.raises(ValueError, match="refusing to coerce"):
        load_p0(path)


def test_intervention_uses_intervention_flag_and_final_decision() -> None:
    p0 = {
        ("q1", "db"): {"official_execution_correct": True},
        ("q2", "db"): {"official_execution_correct": False},
        ("q3", "db"): {"official_execution_correct": False},
    }
    p6 = {
        ("q1", "db"): {"official_execution_correct": False},
        ("q2", "db"): {"official_execution_correct": True},
        ("q3", "db"): {"official_execution_correct": False},
    }
    records = [
        {
            "case_id": "db:q1",
            "intervention": True,
            "decision": "REPLACE",
            "outcome_class": "REPLACE_CHALLENGER",
        },
        {
            "case_id": "db:q2",
            "intervention": True,
            "decision": "REJECT_CHALLENGER",
            "outcome_class": "PRESERVE_INCUMBENT",
        },
        {
            "case_id": "db:q3",
            "intervention": False,
            "decision": "KEEP",
            "outcome_class": "KEEP_INCUMBENT",
        },
    ]
    result = intervention(records, p6, p0)
    assert result["eligible"] == 2
    assert result["p0_correct_eligible"] == 1
    assert result["p0_wrong_eligible"] == 1
    assert result["harm"] == 1
    assert result["rescue"] == 1
    assert result["net_intervention_gain"] == 0
    assert result["decision_counts"] == {"REPLACE": 1, "REJECT_CHALLENGER": 1}


def test_intervention_rejects_invalid_final_decision() -> None:
    p0 = {("q", "db"): {"official_execution_correct": False}}
    p6 = {("q", "db"): {"official_execution_correct": True}}
    records = [{"case_id": "db:q", "intervention": True, "decision": "INTERVENE"}]
    with pytest.raises(ValueError, match="invalid final decision"):
        intervention(records, p6, p0)
