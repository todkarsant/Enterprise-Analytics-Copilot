from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

TARGETS = (0.90, 0.95, 0.97, 0.99)
POLICIES = ("P0", "P1", "P2", "P3", "P4", "P5")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def wilson(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) / n) + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def exact_binomial_two_sided(k: int, n: int) -> float:
    if n == 0:
        return 1.0
    probs = [math.comb(n, i) / (2 ** n) for i in range(n + 1)]
    pk = probs[k]
    return min(1.0, sum(p for p in probs if p <= pk + 1e-15))


def mcnemar(a: list[bool], b: list[bool]) -> dict:
    if len(a) != len(b):
        raise ValueError("Paired McNemar inputs must have equal length")
    b01 = sum(x and not y for x, y in zip(a, b))
    b10 = sum((not x) and y for x, y in zip(a, b))
    discordant = b01 + b10
    chi2_cc = ((abs(b01 - b10) - 1) ** 2 / discordant) if discordant else 0.0
    p_exact = exact_binomial_two_sided(min(b01, b10), discordant)
    return {
        "a_only_correct": b01,
        "b_only_correct": b10,
        "discordant": discordant,
        "accuracy_delta_b_minus_a": (sum(b) - sum(a)) / len(a) if a else 0.0,
        "chi2_cc": chi2_cc,
        "exact_p": p_exact,
    }


def paired_bootstrap_accuracy(a: list[bool], b: list[bool], samples: int = 10000, seed: int = 1729) -> dict:
    if len(a) != len(b) or not a:
        return {"mean_delta": 0.0, "ci95_low": 0.0, "ci95_high": 0.0}
    rng = random.Random(seed)
    n = len(a)
    deltas = []
    for _ in range(samples):
        idx = [rng.randrange(n) for _ in range(n)]
        deltas.append(sum(bool(b[i]) - bool(a[i]) for i in idx) / n)
    deltas.sort()
    lo = deltas[int(0.025 * (samples - 1))]
    hi = deltas[int(0.975 * (samples - 1))]
    return {
        "mean_delta": sum(deltas) / samples,
        "ci95_low": lo,
        "ci95_high": hi,
        "samples": samples,
        "seed": seed,
    }


def summarize_policy(rows: list[dict], policy: str) -> dict:
    xs = [r for r in rows if r["policy"] == policy]
    n = len(xs)
    correct = sum(bool(r.get("official_execution_correct")) for r in xs)
    lo, hi = wilson(correct, n)
    return {
        "n": n,
        "official_execution_accuracy": correct / n if n else 0.0,
        "wilson95": [lo, hi],
        "coverage": sum(bool(r.get("generated_sql")) for r in xs) / n if n else 0.0,
        "mean_research_cost_units": sum(float(r.get("cost", 0.0)) for r in xs) / n if n else 0.0,
        "mean_input_tokens": sum(int(r.get("input_tokens", 0)) for r in xs) / n if n else 0.0,
        "mean_output_tokens": sum(int(r.get("output_tokens", 0)) for r in xs) / n if n else 0.0,
        "total_input_tokens": sum(int(r.get("input_tokens", 0)) for r in xs),
        "total_output_tokens": sum(int(r.get("output_tokens", 0)) for r in xs),
        "mean_llm_calls": sum(int(r.get("llm_calls", 0)) for r in xs) / n if n else 0.0,
        "median_latency_ms": sorted(float(r.get("latency_ms", 0.0)) for r in xs)[n // 2] if n else None,
        "p95_latency_ms": sorted(float(r.get("latency_ms", 0.0)) for r in xs)[max(0, math.ceil(0.95 * n) - 1)] if n else None,
        "targets": {str(t): (correct / n >= t if n else False) for t in TARGETS},
    }


def paired_analysis(rows: list[dict], left: str, right: str) -> dict:
    keyed = {(r["question"], r["db_id"], r["policy"]): r for r in rows}
    pairs = []
    for key, left_row in keyed.items():
        q, db, policy = key
        if policy != left:
            continue
        right_row = keyed.get((q, db, right))
        if right_row is not None:
            pairs.append((bool(left_row.get("official_execution_correct")), bool(right_row.get("official_execution_correct"))))
    a = [x for x, _ in pairs]
    b = [y for _, y in pairs]
    result = mcnemar(a, b)
    result["paired_bootstrap"] = paired_bootstrap_accuracy(a, b)
    result["n_pairs"] = len(pairs)
    return result


def pareto_frontier(rows: dict, target: float) -> list[dict]:
    candidates = []
    for policy, r in rows.items():
        if r.get("official_execution_accuracy", r.get("execution_correctness", 0.0)) >= target:
            candidates.append({
                "policy": policy,
                "mean_research_cost_units": r.get("mean_research_cost_units", r.get("mean_cost")),
                "p95_latency_ms": r.get("p95_latency_ms"),
                "mean_input_tokens": r.get("mean_input_tokens"),
                "mean_output_tokens": r.get("mean_output_tokens"),
            })
    return sorted(candidates, key=lambda x: (x["mean_research_cost_units"] or float("inf"), x["p95_latency_ms"] or float("inf")))


def failure_taxonomy(rows: list[dict], policy: str) -> dict:
    xs = [r for r in rows if r["policy"] == policy]
    counts = Counter()
    for r in xs:
        if not r.get("generated_sql"):
            category = "no_output"
        elif r.get("execution_ok") is False:
            err = (r.get("error") or "").lower()
            category = "execution_error_encoding" if "utf-8" in err or "decode" in err else "execution_error"
        elif r.get("official_execution_correct") is False:
            category = "executable_semantic_mismatch"
        else:
            category = "correct"
        counts[category] += 1
    return dict(counts)


def p5_characterization(rows: list[dict]) -> dict:
    result = {"vs_P0": paired_analysis(rows, "P0", "P5")}
    p5_rows = [r for r in rows if r["policy"] == "P5"]
    result["action_paths"] = Counter(">".join(r.get("actions", [])) for r in p5_rows)
    result["termination_reasons"] = Counter(r.get("termination_reason", "") for r in p5_rows)
    result["repair_cases"] = [
        {
            "question": r["question"],
            "db_id": r["db_id"],
            "error": r.get("error"),
            "official_correct": r.get("official_execution_correct"),
        }
        for r in p5_rows if "repair_sql" in r.get("actions", [])
    ]
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    payload = load(args.artifact)
    traces = payload.get("traces", [])
    if not traces:
        raise SystemExit("Artifact has no traces")

    policy_summary = {p: summarize_policy(traces, p) for p in POLICIES}
    paired = {f"P0_vs_{p}": paired_analysis(traces, "P0", p) for p in POLICIES if p != "P0"}
    failures = {p: failure_taxonomy(traces, p) for p in POLICIES}
    report = {
        "benchmark": payload.get("benchmark"),
        "question_count": payload.get("question_count"),
        "primary_metric": "official Spider execution accuracy",
        "policy_summary": policy_summary,
        "paired_statistics": paired,
        "reliability_frontiers": {str(t): pareto_frontier(policy_summary, t) for t in TARGETS},
        "failure_taxonomy": failures,
        "p5_characterization": p5_characterization(traces),
        "cost_accounting_boundary": {
            "research_cost_units": "synthetic action-budget units retained for controlled-policy comparison; not USD",
            "token_accounting": "provider-reported input/output tokens",
            "usd_cost": "must be calculated from the exact Azure model/deployment pricing applicable to the run; do not infer from action units",
        },
        "p6_gate": "BLOCKED until P0-P5 corrected results, paired statistics, cost/token accounting, P5 characterization, and unseen-schema evaluation are complete.",
    }
    text = json.dumps(report, indent=2, default=lambda x: dict(x))
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
