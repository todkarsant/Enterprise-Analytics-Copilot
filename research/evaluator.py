from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable

from research.experiment import State

@dataclass(frozen=True)
class Outcome:
    correct: bool
    coverage: bool
    cost: float
    latency_ms: float
    actions: int


def evaluate_state(state: State) -> Outcome:
    # Research harness evaluator: policy cannot see this outcome during execution.
    if not state.answerable:
        correct = state.actions[-1:] == ["abstain"]
    else:
        correct = bool(
            state.governance_ok
            and state.execution_ok is True
            and state.semantic_risk < 0.30
            and state.ambiguity < 0.30
        )
    coverage = state.actions[-1:] != ["abstain"] or correct
    return Outcome(correct, coverage, state.cost, state.latency_ms, len(state.actions))


def reliability(outcomes: Iterable[Outcome]) -> float:
    xs = list(outcomes)
    return mean(o.correct for o in xs) if xs else 0.0


def coverage(outcomes: Iterable[Outcome]) -> float:
    xs = list(outcomes)
    return mean(o.coverage for o in xs) if xs else 0.0


def cost_at_reliability(outcomes: Iterable[Outcome], target: float) -> float | None:
    xs = list(outcomes)
    if reliability(xs) < target:
        return None
    return mean(o.cost for o in xs)
