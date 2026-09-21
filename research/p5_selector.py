from __future__ import annotations

import re


_PREDICATE_RE = re.compile(
    r"\b(?:whose|named|where|with\s+(?:the\s+)?(?:name|id|number|value)|"
    r"that\s+(?:has|have|is|are|contains|contain))\b"
)
_LITERAL_RE = re.compile(r"(?<![A-Za-z])['\"]([^'\"]{2,})['\"]")


def assess_strict_evidence(question: str, sql: str, row_count: int | None) -> tuple[bool, str | None]:
    """Return whether deterministic evidence is insufficient for a conservative handoff.

    This selector is deliberately label-free: it inspects only the question, the
    deterministic SQL, and observed result cardinality. It does not use gold SQL,
    evaluator outcomes, model confidence, or benchmark history. It is a challenger
    to the frozen P5 selector, not a replacement for it.
    """
    q = question.lower()
    s = sql.lower()

    clauses = {
        "where": bool(re.search(r"\bwhere\b", s)),
        "join": " join " in f" {s} ",
        "group": bool(re.search(r"\bgroup\s+by\b|\bover\s*\(", s)),
        "having": bool(re.search(r"\bhaving\b", s)),
        "order": bool(re.search(r"\border\s+by\b", s)),
    }

    if _PREDICATE_RE.search(q) and not any(clauses.values()):
        return True, "question_predicate_not_reflected"

    if _LITERAL_RE.search(question) and not any((clauses["where"], clauses["join"], clauses["having"])):
        return True, "literal_predicate_not_reflected"

    if re.search(r"\b(?:ascending|descending|in\s+ascending|in\s+descending|sort(?:ed|ing)?)\b", q):
        if not clauses["order"]:
            return True, "ordering_not_reflected"

    if re.search(r"\b(?:highest|lowest|largest|smallest|oldest|youngest|top|bottom|most|least)\b", q):
        if not clauses["order"] and not re.search(r"\b(?:max|min)\s*\(", s):
            return True, "extremum_not_reflected"

    aggregate_requested = re.search(r"\b(?:how\s+many|number\s+of|count\s+of|average|avg|maximum|minimum|sum\s+of|total)\b", q)
    if aggregate_requested and not re.search(r"\b(?:count|avg|max|min|sum)\s*\(", s):
        return True, "aggregation_not_reflected"

    if re.search(r"\b(?:per|for\s+each|each|every)\b", q) and not clauses["group"]:
        return True, "grouping_not_reflected"

    if re.search(r"\b(?:name|names|full\s+name)\b", q) and "*" not in s:
        projection = s.split(" from ", 1)[0]
        if not re.search(r"\b(?:name|_name)\b", projection):
            return True, "requested_name_not_projected"

    if row_count == 0 and re.search(r"\b(?:who|which|what|name|names)\b", q):
        return True, "empty_result"

    return False, None
