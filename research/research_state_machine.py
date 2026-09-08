"""Fail-closed research state machine for Project 1."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

STATES = ["DESIGNED", "IMPLEMENTED", "CI_VALIDATED", "EXECUTED", "ARTIFACT_VALIDATED", "ANALYZED", "SCIENTIFIC_DECISION", "PAPER_LOCKED"]
REPAIR_STATES = ["REPAIR_REQUIRED", "REPAIR_COMMITTED"]
ALL_STATES = STATES + REPAIR_STATES

REQUIRED_EVIDENCE = {
    "DESIGNED": ["design_ref"],
    "IMPLEMENTED": ["design_ref", "implementation_ref"],
    "CI_VALIDATED": ["design_ref", "implementation_ref", "ci_run"],
    "EXECUTED": ["design_ref", "implementation_ref", "ci_run", "execution_run"],
    "ARTIFACT_VALIDATED": ["execution_run", "artifact_manifest"],
    "ANALYZED": ["execution_run", "artifact_manifest", "analysis_artifact"],
    "SCIENTIFIC_DECISION": ["execution_run", "artifact_manifest", "analysis_artifact", "scientific_decision"],
    "PAPER_LOCKED": ["execution_run", "artifact_manifest", "analysis_artifact", "scientific_decision", "paper_evidence_ref"],
    "REPAIR_REQUIRED": ["repair_reason"],
    "REPAIR_COMMITTED": ["repair_reason", "repair_commit"],
}

ALLOWED = {
    "DESIGNED": {"IMPLEMENTED", "REPAIR_REQUIRED"},
    "IMPLEMENTED": {"CI_VALIDATED", "REPAIR_REQUIRED"},
    "CI_VALIDATED": {"EXECUTED", "REPAIR_REQUIRED"},
    "EXECUTED": {"ARTIFACT_VALIDATED", "REPAIR_REQUIRED"},
    "ARTIFACT_VALIDATED": {"ANALYZED", "REPAIR_REQUIRED"},
    "ANALYZED": {"SCIENTIFIC_DECISION", "REPAIR_REQUIRED"},
    "SCIENTIFIC_DECISION": {"PAPER_LOCKED", "REPAIR_REQUIRED"},
    "PAPER_LOCKED": {"REPAIR_REQUIRED"},
    "REPAIR_REQUIRED": {"REPAIR_COMMITTED"},
    "REPAIR_COMMITTED": {"CI_VALIDATED", "ARTIFACT_VALIDATED", "REPAIR_REQUIRED"},
}

RUN_ID = re.compile(r"^[0-9]+$")
SHA = re.compile(r"^[0-9a-f]{40}$")


def validate(state: dict, root: Path = Path(".")) -> list[str]:
    errors: list[str] = []
    current = state.get("state")
    if current not in ALL_STATES:
        return [f"unknown state: {current!r}"]
    for field in REQUIRED_EVIDENCE[current]:
        if state.get(field) in (None, "", [], {}):
            errors.append(f"{current} requires {field}")
    for field in ("design_ref", "implementation_ref", "paper_evidence_ref"):
        value = state.get(field)
        if value not in (None, "", [], {}) and not (root / value).exists():
            errors.append(f"{field} does not resolve in repository: {value}")
    for field in ("ci_run", "execution_run"):
        value = state.get(field)
        if value not in (None, "", [], {}) and not RUN_ID.fullmatch(str(value)):
            errors.append(f"{field} must be an immutable numeric GitHub Actions run id")
    if state.get("repair_commit") and not SHA.fullmatch(str(state["repair_commit"])):
        errors.append("repair_commit must be a 40-character commit SHA")
    if current == "SCIENTIFIC_DECISION" and state.get("scientific_decision") not in {"PROCEED", "STOP", "REFRAME", "REPAIR_REQUIRED"}:
        errors.append("scientific_decision must be PROCEED, STOP, REFRAME, or REPAIR_REQUIRED")
    if current == "PAPER_LOCKED" and state.get("scientific_decision") == "REPAIR_REQUIRED":
        errors.append("cannot lock paper while scientific decision requires repair")
    previous = state.get("previous_state")
    if previous is not None:
        if previous not in ALL_STATES:
            errors.append(f"unknown previous_state: {previous!r}")
        elif current not in ALLOWED.get(previous, set()):
            errors.append(f"invalid research-state transition: {previous} -> {current}")
    return errors


def check_transition(old: str, new: str) -> None:
    if new not in ALLOWED.get(old, set()):
        raise ValueError(f"invalid research-state transition: {old} -> {new}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-file", type=Path, required=True)
    args = ap.parse_args()
    state = json.loads(args.state_file.read_text(encoding="utf-8"))
    errors = validate(state, args.state_file.parent.parent)
    if errors:
        raise SystemExit("RESEARCH STATE INVALID\n" + "\n".join(f"- {e}" for e in errors))
    print(json.dumps({"valid": True, "state": state["state"]}, indent=2))


if __name__ == "__main__":
    main()
