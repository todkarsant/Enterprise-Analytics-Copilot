import json

import pytest

from scripts.analyze_p6_ip import load_p0


def test_p0_analysis_rejects_missing_official_labels(tmp_path):
    path = tmp_path / "p0.json"
    path.write_text(json.dumps({"traces": [{"question": "q", "db_id": "db", "official_execution_correct": None}]}))
    with pytest.raises(ValueError, match="without explicit official_execution_correct"):
        load_p0(path)


def test_p0_analysis_accepts_explicit_boolean_labels(tmp_path):
    path = tmp_path / "p0.json"
    path.write_text(
        json.dumps(
            {
                "traces": [
                    {"question": "q1", "db_id": "db", "official_execution_correct": True},
                    {"question": "q2", "db_id": "db", "official_execution_correct": False},
                ]
            }
        )
    )
    rows = load_p0(path)
    assert rows[("q1", "db")]["official_execution_correct"] is True
    assert rows[("q2", "db")]["official_execution_correct"] is False
