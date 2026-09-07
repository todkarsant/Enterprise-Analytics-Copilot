from __future__ import annotations

import argparse
import json
from pathlib import Path

TARGETS = (0.90, 0.95, 0.97, 0.99)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pareto_frontier(rows: dict, target: float) -> list[dict]:
    candidates = []
    for policy, r in rows.items():
        if r.get("execution_correctness", 0.0) >= target and r.get("mean_cost") is not None:
            candidates.append({"policy": policy, "mean_cost": r["mean_cost"], "p95_latency_ms": r.get("p95_latency_ms")})
    frontier = []
    for candidate in sorted(candidates, key=lambda x: (x["mean_cost"], x["p95_latency_ms"] or float("inf"))):
        if not frontier or (candidate["mean_cost"] < frontier[-1]["mean_cost"] and (candidate["p95_latency_ms"] or 0) <= (frontier[-1]["p95_latency_ms"] or float("inf"))):
            frontier.append(candidate)
    return frontier


def p5_challenge(rows: dict) -> dict:
    p5 = rows.get("P5")
    if not p5:
        return {"status": "invalid", "reason": "P5 missing"}
    competitors = {p: r for p, r in rows.items() if p != "P5"}
    result = {}
    for target in TARGETS:
        feasible = [
            (p, r["mean_cost"])
            for p, r in competitors.items()
            if r.get("execution_correctness", 0.0) >= target and r.get("mean_cost") is not None
        ]
        p5_feasible = p5.get("execution_correctness", 0.0) >= target and p5.get("mean_cost") is not None
        best = min(feasible, key=lambda x: x[1]) if feasible else None
        if not p5_feasible:
            result[str(target)] = {"status": "p5_unreachable"}
        elif best is None:
            result[str(target)] = {"status": "p5_only_reachable"}
        elif p5["mean_cost"] < best[1]:
            result[str(target)] = {"status": "p5_dominates_cost", "best_competitor": best[0], "cost_gap": best[1] - p5["mean_cost"]}
        else:
            result[str(target)] = {"status": "p5_challenged", "best_competitor": best[0], "cost_gap": p5["mean_cost"] - best[1]}
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact", type=Path)
    args = ap.parse_args()
    payload = load(args.artifact)
    rows = payload["results"]
    report = {
        "benchmark": payload.get("benchmark"),
        "question_count": payload.get("question_count"),
        "targets": {str(t): pareto_frontier(rows, t) for t in TARGETS},
        "p5_challenge": p5_challenge(rows),
        "interpretation": "No P6 claim is permitted. P5 is the pre-P6 challenge baseline; if P5 is not beaten at matched reliability, the proposed contribution must be reframed.",
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
