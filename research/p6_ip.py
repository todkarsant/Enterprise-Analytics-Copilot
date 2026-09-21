from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Verification:
    valid_sql: bool
    executable: bool
    structural_ok: bool

    @property
    def passed(self) -> bool:
        return self.valid_sql and self.executable and self.structural_ok


def structural_ok(question: str, sql: str) -> bool:
    q, s = question.lower(), sql.lower()
    if re.search(r"\b(?:ascending|descending|sort(?:ed|ing)?)\b", q) and "order by" not in s:
        return False
    if re.search(r"\b(?:highest|lowest|largest|smallest|oldest|youngest|top|bottom|most|least)\b", q):
        if "order by" not in s and not re.search(r"\b(?:max|min)\s*\(", s):
            return False
    if re.search(r"\b(?:per|for each|each|every)\b", q) and not re.search(r"\bgroup\s+by\b|\bover\s*\(", s):
        return False
    if re.search(r"\b(?:how many|number of|count of|average|avg|maximum|minimum|sum of|total)\b", q):
        if not re.search(r"\b(?:count|avg|max|min|sum)\s*\(", s):
            return False
    return True


def verify_challenger(question: str, sql: str | None, sql_valid: bool | None, execution_ok: bool | None) -> Verification:
    nonempty = bool(sql and sql.strip())
    syntactic = nonempty and bool(sql_valid)
    executable = execution_ok is True
    structural = nonempty and structural_ok(question, sql or "")
    return Verification(syntactic, executable, structural)


def decide_replacement(*, intervention_eligible: bool, verification: Verification) -> str:
    if not intervention_eligible:
        return "KEEP"
    return "REPLACE" if verification.passed else "REJECT_CHALLENGER"
