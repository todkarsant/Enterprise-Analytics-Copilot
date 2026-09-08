# Project 1 — P6-IP Execution Handoff

**Updated:** 2026-09-08
**Branch:** `research/p6-ip-defensibility`

## Current state

P0–P5 remain frozen. P5R is a forensic challenger only. P6-IP is the approved final controlled challenger and is implemented separately so the frozen P0–P5 runner is not modified.

The separate Defensibility Layer is also approved and must remain orthogonal to the primary correctness metric.

## P6-IP contract

P6-IP starts from the P0 incumbent answer, uses only decision-time evidence for intervention eligibility, generates a challenger only when eligible, and replaces the incumbent only after predefined verification gates pass. Any failed verification preserves the incumbent. Gold answers and official evaluator correctness are post-hoc analysis fields and must never drive a decision.

Required outcome classes:

- preserved-correct
- harm
- rescue
- preserved-wrong
- no-output/runtime failure

Primary metric remains official Spider execution accuracy. Custom row-set equality remains diagnostic only.

## Frozen evaluation contract

- Spider dev split: 1034 cases
- unseen-schema partition: 254 cases from 4 held-out schemas
- development partition: 780 cases from 16 non-holdout schemas
- holdout fraction: 20%
- holdout seed: 1729
- official evaluator commit: `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`
- runtime chunks: 12
- chunk size: 90
- policy timeout: 150 seconds
- model iteration: local Ollama only (`llama3.2:1b`)
- Azure/paid models: prohibited unless explicitly authorized immediately before a final controlled run

## Execution sequence

1. Unit-test P6-IP gates and Defensibility records.
2. Run repository CI/mechanics checks.
3. Execute full P6-IP development partition.
4. Freeze policy/gates; do not tune using holdout outcomes.
5. Execute the 254-case held-out-schema partition once.
6. Run paired statistical analysis against frozen P0/P5/P5R evidence.
7. Run prespecified ablations only after the primary run is frozen.
8. Produce final reproducibility and reviewer-threat analysis.

## Scientific stop rule

Do not force a positive result. If P6-IP does not materially reduce incumbent harm while retaining meaningful rescues at defensible cost/reliability, stop algorithm development and reframe the contribution as an empirical boundary/failure-mode study.

## Defensibility Layer

Every P6-IP decision should emit machine-readable provenance, policy reason, intervention decision, challenger/verification state, final outcome, runtime/cost/latency information, and reproducibility metadata. Decision-time fields must remain separate from post-hoc gold/evaluator fields.

The layer supports defensible engineering evidence; it does not by itself establish legal compliance, complete governance, production readiness, or human-factors explainability.
