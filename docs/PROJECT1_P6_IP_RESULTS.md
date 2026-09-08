# Project 1 — P6-IP Results and Scientific Decision

Status: **P6-IP algorithm development stopped by the prespecified stop rule.**

## 1. Evidence provenance

- P6-IP controlled inference run: `34252265013` on commit `ffb4cc5ecf8b762af03ddb42ecf401c1957e640`.
- Frozen P0–P5 benchmark source: run `34206500727`.
- P0 case-level official correctness was recomputed post hoc from the existing P0 SQL using pinned Spider evaluator commit `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`.
- Comparator repair workflow: `34281611836`, commit `8b93b99d33839370e22bb60f52b73d20bf727a6b`.
- No LLM inference was rerun for comparator repair.
- Holdout was not used for tuning.

## 2. Primary paired correctness result

### Development partition — 1034 cases

- P0: **254/1034 = 24.565%**.
- P6-IP: **234/1034 = 22.631%**.
- Paired difference: **−1.934 percentage points**.
- P6-IP only correct: 8.
- P0 only correct: 28.
- Both correct: 226.
- Neither correct: 772.
- Exact two-sided McNemar p-value: **0.001193**.
- P6-IP did not reach any predefined 90/95/97/99% reliability target.

### Held-out schemas — 254 cases

- P0: **60/254 = 23.622%**.
- P6-IP: **55/254 = 21.654%**.
- Paired difference: **−1.969 percentage points**.
- P6-IP only correct: 4.
- P0 only correct: 9.
- Both correct: 51.
- Neither correct: 190.
- Exact two-sided McNemar p-value: **0.266846**.

The held-out evaluation is retained as locked observational evidence. It is **not** treated as a fully prospective confirmatory run because the historical P6 workflow executed holdout cases before the entire development partition had been aggregated/frozen. No holdout result was used to modify the policy.

## 3. Incumbent-preservation / intervention analysis

The P6-IP decision record contains an explicit `intervention` flag. Final decisions for intervention cases are `REPLACE` or `REJECT_CHALLENGER`; `KEEP` is used for non-intervention cases.

### Development — 1034 cases

- Intervention-eligible: **330/1034 = 31.91%**.
- P0-correct among eligible: 62.
- P0-wrong among eligible: 268.
- Challenger replacements: 157.
- Challenger rejections / incumbent preserved: 173.
- **Harm:** 21 cases (P0 correct → P6-IP wrong).
- **Rescue:** 2 cases (P0 wrong → P6-IP correct).
- Neutral: 307 cases.
- Harm rate among P0-correct eligible cases: **21/62 = 33.87%** (Wilson 95% CI approximately 23.34–46.28%).
- Rescue rate among P0-wrong eligible cases: **2/268 = 0.75%** (Wilson 95% CI approximately 0.20–2.68%).
- Net intervention gain: **−19 cases**.
- Correctness-changing interventions: **23/330 = 6.97%**.

### Held-out schemas — 254 cases

- Intervention-eligible: **91/254 = 35.83%**.
- P0-correct among eligible: 16.
- P0-wrong among eligible: 75.
- Challenger replacements: 39.
- Challenger rejections / incumbent preserved: 52.
- **Harm:** 5 cases.
- **Rescue:** 1 case.
- Neutral: 85 cases.
- Harm rate among P0-correct eligible cases: **5/16 = 31.25%** (Wilson 95% CI approximately 14.16–55.60%).
- Rescue rate among P0-wrong eligible cases: **1/75 = 1.33%** (Wilson 95% CI approximately 0.24–7.17%).
- Net intervention gain: **−4 cases**.
- Correctness-changing interventions: **6/91 = 6.59%**.

## 4. Cost consequence

P6-IP did not provide a defensible cost advantage in this incumbent-preserving design because the implementation pays for the incumbent execution and challenger execution when intervention occurs.

- Development mean cost: P0 **0.26908**, P6-IP **0.33841**; P6-IP is approximately **25.8% higher**.
- Holdout mean cost: P0 **0.26941**, P6-IP **0.34795**; P6-IP is approximately **29.2% higher**.

Therefore the intervention mechanism simultaneously increased cost and introduced substantial incumbent harm while producing very few rescues.

## 5. Scientific stop-rule decision

The prespecified P6-IP stop rule was:

> If P6-IP does not materially reduce incumbent harm while retaining meaningful rescues at defensible cost/reliability, stop algorithm development and publish the empirical boundary/failure-mode study.

**Decision: FAIL / STOP algorithm development.**

The evidence is decisive on the development partition:

1. Incumbent harm among eligible P0-correct cases is **33.87%**.
2. Rescue among eligible P0-wrong cases is only **0.75%**.
3. Net intervention effect is **−19 cases**.
4. Overall P6-IP accuracy is **1.93 pp below P0**.
5. Mean cost is **25.8% above P0**.
6. No reliability target of 90% or above is remotely satisfied.

The held-out schemas show the same direction: **31.25% harm vs 1.33% rescue among eligible cases**, with higher mean cost and lower overall accuracy than P0. Because of the historical holdout-ordering protocol defect, this is treated as corroborating observational evidence rather than the basis for a confirmatory claim.

## 6. Interpretation

The experiment does **not** support the claim that intermediate evidence plus a simple incumbent-preserving verification gate is sufficient for reliable analytical intervention.

Instead, it supports a narrower and more defensible finding:

> **Intermediate evidence can trigger analytically plausible interventions, but executable and structurally valid challenger SQL is not sufficient evidence for safe incumbent replacement. In this experiment, the replacement gate produced substantially more incumbent harm than rescue and increased cost.**

This is a boundary/failure-mode result, not a failed research project. It establishes that the missing component is not simply another routing heuristic. Safe intervention requires stronger evidence of semantic equivalence/correctness than the current gate provides.

## 7. Research consequence

Do **not** create P7/P8 merely to recover the desired result.

The current study should transition from algorithm invention to:

- failure-mode characterization;
- decision-trace and Defensibility Layer analysis;
- verification-gap analysis;
- comparison against the frozen P0–P5/P5R evidence;
- literature positioning around selective prediction, cascades, adaptive tool use, and verification;
- paper formulation around the empirical boundary of evidence-dependent analytical intervention.

Any future algorithmic extension requires a separately justified research question and must not tune on the held-out schemas.
