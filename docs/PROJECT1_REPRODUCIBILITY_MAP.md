# Project 1 — Reproducibility and Provenance Map

**Audit date:** 2026-09-14  
**Repository:** `todkarsant/Enterprise-Analytics-Copilot`  
**Primary manuscript branch:** `research/paper-lit-integration`

## Purpose

This document is the reviewer-facing navigation map for Project 1. It separates the readable manuscript from the immutable research provenance needed to reproduce or audit the reported experiments.

The preferred reproducibility chain is:

`manuscript → repository → immutable commit → experiment/run → artifact → evaluator → analysis`

A branch name is navigation metadata only; a commit SHA or immutable run/artifact identifier is the stronger reproducibility anchor.

## Canonical manuscript

- **File:** `paper/PROJECT1_JAI_FINAL_MANUSCRIPT.md`
- **Branch:** `research/paper-lit-integration`
- **Latest manuscript commit:** `01aababc52e0036a22ececf83faec3d12e2834d2`
- **Latest manuscript blob SHA at audit:** `691ae0172a57f43e1240ac028520d4b8d75d6d16`
- **Status:** single-column plagiarism/originality-stage manuscript; final JAI production layout is intentionally deferred.

## Research design and handoffs

| Purpose | Repository location | Provenance anchor |
|---|---|---|
| Project research handoff | `docs/PROJECT1_HANDOFF.md` | repository history; historical handoff records frozen baseline methodology |
| P6-IP research design | `docs/PROJECT1_P6_IP_DESIGN.md` | blob SHA `98f04ecfdb12bf143e37b81d8d8c84624cd9ea65` at audit |
| P6-IP execution handoff | `docs/PROJECT1_P6_IP_EXECUTION_HANDOFF.md` | blob SHA `32d0e641e37f053ed3fdec99e7837cf9fd9348b3` at audit |
| Defensibility Layer design | `docs/PROJECT1_DEFENSIBILITY_LAYER.md` | repository history |
| Architecture decisions | `docs/ARCHITECTURE_DECISIONS.md` | repository history |
| Research state machine | `docs/RESEARCH_STATE_MACHINE.md` and `research/research_state.json` | repository history |

## Frozen baseline evidence

- **Policies:** P0–P5 are frozen; P5 is the mandatory strongest post-evidence comparator.
- **Benchmark artifact:** 1,034 Spider cases.
- **Development partition:** 780 cases from 16 non-holdout schemas.
- **Held-out-schema partition:** 254 cases from four schemas: `car_1`, `flight_2`, `real_estate_properties`, `student_transcripts_tracking`.
- **Holdout seed:** 1729.
- **Official Spider evaluator commit:** `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`.
- **Primary correctness metric:** official Spider execution accuracy.
- **Diagnostic only:** custom row-set equality.
- **Iteration model:** local Ollama `llama3.2:1b`.
- **Paid/Azure inference:** not used for the reported controlled experiment.

## P5R mechanism forensics

P5R is a mechanism-forensics challenger and does not replace the frozen P0–P5 baselines.

Key repository components:

- `research/p5_selector.py`
- `research/spider_benchmark_challenger.py`
- `tests/test_p5_selector.py`
- `.github/workflows/p5-mechanism-forensic.yml`

Clean forensic execution previously recorded in the project history: GitHub Actions run `34219674022`.

## P6-IP controlled experiment

P6-IP is the final controlled challenger. It starts from the P0 incumbent and can replace it only after the predefined intervention and verification gates.

Key components:

- `research/p6_ip.py`
- `research/p6_ip_runner.py`
- `research/defensibility.py`
- `research/spider_official_eval.py`
- `.github/workflows/p6-ip-controlled.yml`

Controlled execution:

- **GitHub Actions run:** `34252265013`
- **Branch:** `research/p6-ip-defensibility`
- **Controlled-run head:** `ffb4cc5ecf8b762af03ddb42ecf401c1957e640`
- **Workflow:** `P6-IP Controlled Experiment`
- **Inference:** local Ollama only
- **Execution contract:** process-isolated benchmark, 12 chunks, fixed timeout, frozen evaluator.

### Artifact-integrity repair

The controlled run exposed an artifact-integrity issue in the frozen P0 per-trace official-correctness fields. No LLM inference was rerun. P0 correctness was recomputed post-hoc from the frozen P0 SQL using the pinned official evaluator.

Repair components:

- `scripts/recompute_official_p0.py`
- `scripts/analyze_p6_ip.py`
- `tests/test_p6_analysis_integrity.py`
- `.github/workflows/p6-ip-analysis-repair.yml`

Important repair commits recorded in project history:

- `8b93b99d33839370e22bb60f52b73d20bf727a6b` — P0 recomputation split/occurrence integrity fix.
- `48ff2fb5326086add53d1094346efab08726a9e8` — P6 analyzer intervention-label fix.
- `4fc689e0d698355e91229d8f4e6ee0f4aff59df4` — analyzer regression tests.
- `ff2aec3553a29a194772a1973e1d560fa63240a7` — scientific result documentation.

Corrected P0 artifacts:

- `p0_official_dev.json` — 1,034 cases.
- `p0_official_holdout.json` — 254 cases.
- Manifest records source P6 run `34252265013`, source frozen P0 run `34206500727`, evaluator commit `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`, and `inference_rerun: false`.

The historical holdout execution ordering deviation is disclosed in the manuscript and should be treated as locked observational corroboration rather than a fully prospective confirmatory test. The development result independently triggered the scientific stop rule.

## Primary P6-IP evidence anchor

Development:

- P0: 254/1,034 ≈ 24.6%.
- P6-IP: 234/1,034 ≈ 22.6%.
- Paired difference: approximately −1.93 percentage points.
- Exact McNemar p ≈ 0.00119.
- Mean cost increase: approximately 25.8%.
- Intervention-eligible cases: 330.
- Harm: 21/62 ≈ 33.87% among P0-correct intervention-eligible cases.
- Rescue: 2/268 ≈ 0.75% among P0-wrong intervention-eligible cases.

Held-out schemas:

- P0: 60/254 ≈ 23.6%.
- P6-IP: 55/254 ≈ 21.7%.
- Paired difference: approximately −1.97 percentage points.
- Mean cost increase: approximately 29.2%.
- Intervention-eligible cases: 91.
- Harm: 5/16 = 31.25%.
- Rescue: 1/75 ≈ 1.33%.

These values are reproduced from the corrected analysis trail and are intended as navigation anchors. Final journal submission should perform one final machine-level verification against the immutable artifacts before upload.

## Decision-record provenance

P6-IP decision records capture decision-time evidence separately from post-hoc evaluator fields. The tested verification gate checks SQL validity, execution and selected structural consistency; it does not establish semantic equivalence.

The Defensibility Layer is an auditability/evidence layer. It does not establish legal compliance, institutional accountability, production readiness or universal governance.

## CI and reproducibility controls

Research CI and state-gate workflows are part of the repository evidence chain. Relevant workflow locations include:

- `.github/workflows/research-ci.yml`
- `.github/workflows/research-state-gate.yml`
- `.github/workflows/p6-ip-controlled.yml`
- `.github/workflows/p6-ip-analysis-repair.yml`

The project research state machine distinguishes design, implementation, CI validation, execution, artifact validation, analysis, scientific decision and paper-lock stages. Repairs are recorded as explicit state transitions rather than silently replacing historical artifacts.

## Reviewer navigation

A reviewer should be able to move through the project in this order:

1. `paper/PROJECT1_JAI_FINAL_MANUSCRIPT.md` — scientific argument and reported result.
2. This file — provenance map.
3. `docs/PROJECT1_P6_IP_DESIGN.md` — prespecified P6-IP gates and stop rule.
4. `docs/PROJECT1_P6_IP_EXECUTION_HANDOFF.md` — frozen execution contract.
5. `research/spider_official_eval.py` — official correctness adapter.
6. `research/p6_ip.py` / `research/p6_ip_runner.py` — challenger implementation.
7. `scripts/recompute_official_p0.py` / `scripts/analyze_p6_ip.py` — artifact-integrity and statistical analysis.
8. GitHub Actions run `34252265013` — controlled execution provenance.
9. Corrected P0 artifacts and associated manifests — case-level post-hoc evidence.
10. `docs/PROJECT1_DEFENSIBILITY_LAYER.md` — auditability architecture.

## Journal-facing principle

The manuscript should remain concise. Detailed repository navigation belongs here rather than in the body of the paper. The paper's Code Availability section should point readers to this reproducibility map and identify the repository and immutable experimental anchors; this document carries the detailed routing.

## Audit status

**P1 provenance/reproducibility audit:** substantially complete.

Remaining final-submission checks are deliberately downstream of the author's plagiarism screening and the later JAI template conversion: final bidirectional citation audit, final publication-status check, final numerical machine cross-check, final figure/table audit, and final page-limit/rendering check.
