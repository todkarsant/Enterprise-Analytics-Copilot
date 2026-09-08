"""Fail-closed research state machine for Project 1.

The state is an auditable repository artifact. A transition is valid only when
its required evidence exists. This prevents a conversational finding from
being treated as completed research without a commit, CI validation, artifact
validation, analysis, and scientific decision.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

STATES = [
    "DESIGNED",
    "IMPLEMENTED",
    "CI_VALIDATED",
    "EXECUTED",
    "ARTIFACT_VALIDATED",
    "ANALYZED",
    "SCIENTIFIC_DECISION",
    "PAPER_LOCKED",
]
REPAIR_STATES = ["REPAIR_REQUIRED", "REPAIR_COMMITTED"]

REQUIRED_EVIDENCE = {
    "DESIGNED": ["design_ref"],
    "IMPLEMENTED": ["design_ref", "implementation_ref"],
    "CI_VALIDATED": ["design_ref", "implementation_ref", "ci_run"],
    "EXECUTED": ["design_ref", "implementation_ref", "ci_run", "execution_run"],
    "ARTIFACT_VALIDATED": ["execution_run", "artifact_manifest"],
    "ANALYZED": ["artifact_manifest", "analysis_artifact"],
    "SCIENTIFIC_DECISION": ["analysis_artifact", "scientific_decision"],
    "PAPER_LOCKED": ["analysis_artifact", "scientific_decision", "paper_evidence_ref"],
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


def validate(state: dict) -> list[str]:
    errors = []
    current = state.get("state")
    if current not in STATES + REPAIR_STATES:
        errors.append(f"unknown state: {current!r}")
        return errors
    for field in REQUIRED_EVIDENCE.get(current, []):
        value = state.get(field)
        if value in (None, "", [], {}):
            errors.append(f"{current} requires {field}")
    if current == "SCIENTIFIC_DECISION" and state.get("scientific_decision") not in {
        "PROCEED", "STOP", "REFRAME", "REPAIR_REQUIRED"
    }:
        errors.append("scientific_decision must be PROCEED, STOP, REFRAME, or REPAIR_REQUIRED")
    if current == "PAPER_LOCKED" and state.get("scientific_decision") == "REPAIR_REQUIRED":
        errors.append("cannot lock paper while scientific decision requires repair")
    return errors


def check_transition(old: str, new: str) -> None:
    if new not in ALLOWED.get(old, set()):
        raise ValueError(f"invalid research-state transition: {old} -> {new}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-file", type=Path, required=True)
    args = ap.parse_args()
    state = json.loads(args.state_file.read_text(encoding="utf-8"))
    errors = validate(state)
    if errors:
        raise SystemExit("RESEARCH STATE INVALID\n" + "\n".join(f"- {e}" for e in errors))
    print(json.dumps({"valid": True, "state": state["state"]}, indent=2))


if __name__ == "__main__":
    main()
