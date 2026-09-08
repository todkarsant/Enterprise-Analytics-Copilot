# P5 Mechanism-Level Forensic Validation Plan

## Objective

Determine whether the P5 regression is caused primarily by (a) an inadequate deterministic solver, (b) a miscalibrated evidence/escalation selector, (c) repair/verification behavior, or (d) interaction effects. Do not implement P6 or tune against the held-out schemas until this analysis is complete.

## Frozen evidence

The P0–P5 inference traces from workflow `34206500727` are immutable evidence. The official Spider execution evaluator is the primary correctness metric. Timeouts/errors remain in the denominator.

## Analyses

1. **Paired transition matrix:** for each case, classify P0/P5 as correct/incorrect and, within P5, escalated/non-escalated. Report counts and exact paired tests.
2. **Selector diagnostics:** define the prospective target as whether an LLM escalation would improve or preserve correctness relative to deterministic output. Estimate selector precision, recall, false-positive rate, false-negative rate and calibration by development schema partition. Held-out schemas are evaluation-only.
3. **Deterministic-solver audit:** stratify cases by solver success/failure, query structure, joins, aggregation, ordering, predicates, nested queries and multi-step semantics. Identify unsupported patterns rather than attributing errors to the LLM.
4. **Escalation-path audit:** compare first LLM generation, repair, verification and final execution. Quantify rescue, destruction and no-change transitions.
5. **Threshold sensitivity:** replay the selector decision from frozen traces without new inference. Sweep structural/predicate/singleton thresholds and report decision-only counterfactuals. These are diagnostic only; no claim of causal improvement is permitted without prospective evaluation.
6. **Schema generalization:** report the 16-schema development partition separately from the four-schema holdout. Do not describe the 1,034-case artifact as a disjoint train/dev plus test split.
7. **Uncertainty:** provide exact binomial confidence intervals for proportions, paired McNemar tests for P0/P5, bootstrap confidence intervals for accuracy deltas, and effect sizes for cost/latency. Where a distributional assumption is not justified, use paired/non-parametric methods.
8. **Failure taxonomy:** create mutually exclusive primary failure categories with an auditable rule and retain an 'unclassified' category rather than forcing ambiguous cases into a bucket.

## Decision gates

- **G1:** If selector false-negative errors dominate and can be identified using information available before escalation, design a prospective selector revision.
- **G2:** If deterministic solver coverage is the dominant bottleneck, improve solver capability before claiming adaptive-routing novelty.
- **G3:** If escalation/repair destroys correct deterministic answers, introduce an explicit preservation gate rather than unconditional overwrite.
- **G4:** If no pre-execution signal yields a defensible routing advantage, stop P6 and reframe the contribution as a negative/boundary result.

## Scientific constraint

No P5/P6 rule may be tuned using the four held-out schemas. Any prospective change must be frozen on the 16-schema development partition and then evaluated once on the held-out schemas. Counterfactual replay is not a substitute for prospective validation because it cannot establish the behavior of a newly generated SQL output.
