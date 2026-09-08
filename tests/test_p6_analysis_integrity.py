from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.analyze_p6_ip import load_p0


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
    write_payload(path, 1)
    with pytest.raises(ValueError, match="refusing to coerce"):
        load_p0(path)
