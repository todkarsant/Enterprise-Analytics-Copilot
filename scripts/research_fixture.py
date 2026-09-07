import json
from pathlib import Path

from research.evaluator import coverage, evaluate_state, reliability
from research.experiment import (
    ActionEnvironment,
    p0_always_llm,
    p1_deterministic_only,
    p2_static_hybrid,
    p3_query_complexity_router,
    p4_query_confidence_router,
    p5_post_evidence_cascade,
    run_policy,
)
from research.fixtures import cases

POLICIES = {
    "P0": p0_always_llm,
    "P1": p1_deterministic_only,
    "P2": p2_static_hybrid,
    "P3": p3_query_complexity_router,
    "P4": p4_query_confidence_router,
    "P5": p5_post_evidence_cascade,
}


def run():
    output = {
        "status": "baseline_characterization_only",
        "warning": "Synthetic mechanics fixture. These results are not evidence of research superiority.",
        "policies": {},
    }
    for name, policy in POLICIES.items():
        outcomes = []
        rows = []
        for case in cases():
            state = run_policy(case, policy, ActionEnvironment())
            outcome = evaluate_state(state)
            outcomes.append(outcome)
            rows.append({
                "question": state.question,
                "correct": outcome.correct,
                "covered": outcome.covered,
                "cost": round(outcome.cost, 4),
                "latency_ms": round(outcome.latency_ms, 2),
                "actions": state.actions,
                "termination_reason": state.termination_reason,
            })
        output["policies"][name] = {
            "reliability": reliability(outcomes),
            "coverage": coverage(outcomes),
            "mean_cost": sum(o.cost for o in outcomes) / len(outcomes),
            "mean_latency_ms": sum(o.latency_ms for o in outcomes) / len(outcomes),
            "cases": rows,
        }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/research_fixture.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    run()
