from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal

Action = Literal[
    "deterministic_execute", "retrieve_schema", "generate_sql", "execute_sql",
    "verify_sql", "repair_sql", "clarify", "agentic_escalation", "abstain",
]

@dataclass(frozen=True)
class Evidence:
    kind: str
    value: Any

@dataclass
class State:
    question: str
    answerable: bool = True  # evaluator-only; policies must not inspect this field
    ambiguity: float = 0.0
    sql_valid: bool | None = None
    semantic_risk: float = 0.0
    execution_ok: bool | None = None
    verification_confidence: float | None = None
    governance_ok: bool = True
    evidence: list[Evidence] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    cost: float = 0.0
    latency_ms: float = 0.0
    budget: float = 1.0

@dataclass(frozen=True)
class ActionProfile:
    cost: float
    latency_ms: float

DEFAULT_PROFILES = {
    "retrieve_schema": ActionProfile(0.02, 5),
    "deterministic_execute": ActionProfile(0.05, 10),
    "generate_sql": ActionProfile(0.20, 80),
    "execute_sql": ActionProfile(0.05, 10),
    "verify_sql": ActionProfile(0.12, 45),
    "repair_sql": ActionProfile(0.16, 60),
    "clarify": ActionProfile(0.03, 15),
    "agentic_escalation": ActionProfile(0.45, 180),
    "abstain": ActionProfile(0.0, 1),
}

class ActionEnvironment:
    """Deterministic harness environment; it is not a model-quality benchmark."""
    def __init__(self, profiles: dict[str, ActionProfile] | None = None):
        self.profiles = profiles or DEFAULT_PROFILES

    def apply(self, state: State, action: Action) -> State:
        p = self.profiles[action]
        state.actions.append(action)
        state.cost += p.cost
        state.latency_ms += p.latency_ms
        state.budget -= p.cost
        if action == "retrieve_schema":
            state.evidence.append(Evidence("schema", "retrieved"))
        elif action == "deterministic_execute":
            ok = state.ambiguity < 0.25 and state.semantic_risk < 0.25 and state.governance_ok
            state.execution_ok = ok
            state.sql_valid = ok
            state.evidence.append(Evidence("execution", ok))
        elif action == "generate_sql":
            state.sql_valid = state.semantic_risk < 0.65
            state.execution_ok = None
            state.evidence.append(Evidence("generation", state.sql_valid))
        elif action == "execute_sql":
            ok = bool(state.sql_valid and state.governance_ok and state.semantic_risk < 0.75)
            state.execution_ok = ok
            state.evidence.append(Evidence("execution", ok))
        elif action == "verify_sql":
            conf = max(0.0, 1.0 - state.semantic_risk - 0.35 * state.ambiguity)
            state.verification_confidence = conf
            state.evidence.append(Evidence("verification", conf))
        elif action == "repair_sql":
            state.sql_valid = True
            state.semantic_risk = max(0.0, state.semantic_risk - 0.20)
            state.evidence.append(Evidence("repair", "reduced_risk"))
        elif action == "clarify":
            state.ambiguity = max(0.0, state.ambiguity - 0.65)
            state.evidence.append(Evidence("clarification", "ambiguity_reduced"))
        elif action == "agentic_escalation":
            state.semantic_risk = max(0.0, state.semantic_risk - 0.45)
            state.ambiguity = max(0.0, state.ambiguity - 0.35)
            state.evidence.append(Evidence("agent", "deeper_reasoning"))
        return state

PolicyFn = Callable[[State], Action]

def query_complexity(state: State) -> float:
    q = state.question.lower()
    score = min(1.0, 0.15 + 0.08 * len(q.split()))
    if any(x in q for x in ("why", "compare", "trend", "driver", "explain")):
        score += 0.25
    if any(x in q for x in ("ambiguous", "which meaning", "either")):
        score += 0.25
    return min(score, 1.0)

def p5_post_evidence_cascade(state: State) -> Action:
    """Cheapest-first baseline with post-execution evidence."""
    if not state.actions:
        return "deterministic_execute"
    if state.execution_ok is True and state.ambiguity < 0.25 and state.semantic_risk < 0.25:
        return "abstain"
    if state.sql_valid is False:
        return "repair_sql"
    if state.verification_confidence is None:
        return "verify_sql"
    return "agentic_escalation"

def p6_evidence_policy(state: State) -> Action:
    """Transparent reference policy for harness validation; not a claimed contribution."""
    q = state.question.lower()
    if not state.actions:
        if "answerable" in q and "available data" in q:
            return "abstain"
        if state.ambiguity >= 0.65:
            return "clarify"
        if state.semantic_risk <= 0.25 and state.governance_ok:
            return "deterministic_execute"
        return "retrieve_schema"
    if state.actions[-1] == "clarify":
        return "deterministic_execute"
    if state.actions[-1] == "retrieve_schema":
        return "generate_sql"
    if state.execution_ok is True and state.semantic_risk <= 0.25 and state.ambiguity <= 0.25:
        return "abstain"
    if state.sql_valid is False:
        return "repair_sql"
    if state.verification_confidence is None:
        return "verify_sql"
    if state.verification_confidence >= 0.80:
        return "abstain"
    if state.ambiguity >= 0.50:
        return "clarify"
    if state.semantic_risk >= 0.55:
        return "agentic_escalation"
    return "execute_sql"

def run_policy(initial: State, policy: PolicyFn, env: ActionEnvironment, max_steps: int = 8) -> State:
    state = initial
    for _ in range(max_steps):
        action = policy(state)
        if action == "abstain":
            state.actions.append("abstain")
            break
        if state.budget < env.profiles[action].cost:
            state.actions.append("abstain")
            break
        env.apply(state, action)
    return state
