import json
from pathlib import Path

from research.evaluator import coverage, evaluate_state, reliability
from research.experiment import ActionEnvironment, p5_post_evidence_cascade, p6_evidence_policy, run_policy
from research.fixtures import cases

POLICIES = {
    "P5": p5_post_evidence_cascade,
    "P6": p6_evidence_policy,
}


def run():
    output = {}
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
            })
        output[name] = {
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
