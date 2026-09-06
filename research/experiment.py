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
    # Evaluator-only reference label. Policies must not inspect it.
    answerable: bool = True
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
    terminated: bool = False
    termination_reason: str | None = None

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
    """Deterministic mechanics fixture, not a model-quality benchmark."""
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


def p0_always_llm(state: State) -> Action:
    """Reference policy: always attempt generation, with mandatory governance checks."""
    if not state.actions:
        return "abstain" if not state.governance_ok else "generate_sql"
    if state.sql_valid is False:
        return "repair_sql"
    if state.execution_ok is None and state.sql_valid:
        return "execute_sql"
    if state.execution_ok is True:
        return "abstain"
    return "abstain"


def p1_deterministic_only(state: State) -> Action:
    if not state.actions:
        return "deterministic_execute" if state.governance_ok else "abstain"
    return "abstain"


def p2_static_hybrid(state: State) -> Action:
    if not state.actions:
        if not state.governance_ok:
            return "abstain"
        return "deterministic_execute" if state.semantic_risk < 0.25 and state.ambiguity < 0.25 else "generate_sql"
    if state.sql_valid is False:
        return "repair_sql"
    if state.execution_ok is None and state.sql_valid:
        return "execute_sql"
    return "abstain"


def p3_query_complexity_router(state: State) -> Action:
    if not state.actions:
        if not state.governance_ok:
            return "abstain"
        return "generate_sql" if query_complexity(state) >= 0.45 else "deterministic_execute"
    if state.sql_valid is False:
        return "repair_sql"
    if state.execution_ok is None and state.sql_valid:
        return "execute_sql"
    return "abstain"


def p4_query_confidence_router(state: State) -> Action:
    if not state.actions:
        if not state.governance_ok:
            return "abstain"
        confidence = 1.0 - min(1.0, 0.5 * state.semantic_risk + 0.5 * state.ambiguity)
        return "deterministic_execute" if confidence >= 0.75 else "generate_sql"
    if state.sql_valid is False:
        return "repair_sql"
    if state.execution_ok is None and state.sql_valid:
        return "execute_sql"
    return "abstain"


def p5_post_evidence_cascade(state: State) -> Action:
    """Strongest pre-P6 reference: cheap action, inspect resulting evidence, then escalate."""
    if not state.actions:
        return "deterministic_execute" if state.governance_ok else "abstain"
    if state.execution_ok is True and state.ambiguity < 0.25 and state.semantic_risk < 0.25:
        return "abstain"
    if state.sql_valid is False:
        return "repair_sql"
    if state.verification_confidence is None:
        return "verify_sql"
    if state.semantic_risk >= 0.55 or state.ambiguity >= 0.50:
        return "agentic_escalation"
    return "abstain"


def run_policy(initial: State, policy: PolicyFn, env: ActionEnvironment, max_steps: int = 8) -> State:
    """Execute a policy until explicit abstention, budget exhaustion, or step limit."""
    state = initial
    for _ in range(max_steps):
        if state.terminated:
            break
        action = policy(state)
        if action == "abstain":
            state.actions.append("abstain")
            state.cost += env.profiles["abstain"].cost
            state.latency_ms += env.profiles["abstain"].latency_ms
            state.terminated = True
            state.termination_reason = "policy_abstain"
            break
        if state.budget < env.profiles[action].cost:
            state.actions.append("abstain")
            state.terminated = True
            state.termination_reason = "budget_exhausted"
            break
        env.apply(state, action)
    if not state.terminated:
        state.terminated = True
        state.termination_reason = "step_limit"
    return state
