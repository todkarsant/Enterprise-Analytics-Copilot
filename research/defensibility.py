from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class DefensibilityTrace:
    case_id: str
    policy: str
    incumbent_policy: str = "P0"
    decision: str = "KEEP"
    evidence: dict[str, Any] = field(default_factory=dict)
    evidence_provenance: list[str] = field(default_factory=list)
    risk_reasons: list[str] = field(default_factory=list)
    verification: dict[str, Any] = field(default_factory=dict)
    authorization: dict[str, Any] = field(default_factory=dict)
    outcome_class: str | None = None
    intervention: bool = False
    replacement: bool = False
    audit_version: str = "defensibility-v1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


REQUIRED_TRACE_FIELDS = (
    "case_id", "policy", "decision", "evidence", "evidence_provenance",
    "risk_reasons", "verification", "authorization", "audit_version",
)


def validate_trace(trace: DefensibilityTrace) -> None:
    payload = trace.to_dict()
    missing = [field for field in REQUIRED_TRACE_FIELDS if field not in payload]
    if missing:
        raise ValueError(f"Incomplete defensibility trace: {missing}")
    if trace.decision not in {"KEEP", "INTERVENE", "REJECT_CHALLENGER", "REPLACE"}:
        raise ValueError(f"Unknown defensibility decision: {trace.decision}")
    if trace.replacement and trace.decision != "REPLACE":
        raise ValueError("replacement=True requires decision=REPLACE")
