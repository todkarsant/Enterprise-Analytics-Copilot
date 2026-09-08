# Project 1 Handoff — Enterprise Analytics Copilot

**Purpose:** Continuation reference for a new chat. Start here before changing code or launching experiments.

**Last updated:** 2026-09-08  
**Repository:** `todkarsant/Enterprise-Analytics-Copilot`  
**Research branch:** `research/p1-evaluator-hardening`  
**PR:** #3  
**Primary goal now:** extract conclusive P0–P5 evidence from the existing/frozen benchmark artifacts; avoid another workflow-engineering loop.

---

## 1. HARD operating rules

1. Iterative development/benchmarking uses **local Ollama only**. No Azure/paid LLM during iteration.
2. Azure is permitted only for a final controlled run after **explicit user authorization immediately before execution**.
3. Never expose, print, request, or commit secrets.
4. Never reduce the Spider benchmark, unseen-schema evaluation, policy set, evaluator rigor, metrics, or denominator to improve a result.
5. Never select only successful cases or discard timeout/error cases.
6. **Official Spider execution accuracy is the primary metric.** The custom row-set metric is diagnostic only.
7. Do not implement P6 merely because P5 performs poorly. P6 is evidence-gated.
8. Infrastructure fixes must preserve the research methodology.
9. Preserve negative/inconclusive results.
10. No force-push, no unrelated changes, no automatic merge.
11. User explicitly wants acceleration through parallel/unattended execution, but **without cutting experiments or rigor**.
12. Before launching another expensive benchmark, inspect existing artifacts for completeness.

---

## 2. Research question and contribution framing

The original question — “Can deterministic decision boundaries reduce cost/latency/failure?” — was judged too generic to be the primary contribution.

Current research question:

> **Can an evidence-dependent analytical execution policy select the least expensive sufficient analytical action while maintaining a predefined reliability target, and does this outperform fixed execution strategies and strong post-evidence cascade baselines on enterprise data-agent workloads?**

The intended contribution is an empirical systems study around:

- heterogeneous analytical operators;
- decision timing based on intermediate execution evidence;
- reliability-constrained cost/latency frontiers;
- enterprise failure taxonomy;
- unseen-schema / cross-schema generalization.

Do **not** claim generic adaptive routing as novel by itself.

### Policies

- P0 — Always-LLM
- P1 — Deterministic-only
- P2 — Static Hybrid
- P3 — Query-only Complexity Router
- P4 — Query-only Confidence Router
- P5 — Post-Evidence Cascade
- P6 — Heterogeneous Evidence-Dependent Policy (**not yet implemented / gated**)

### Actions

`retrieve_schema`, `retrieve_examples`, `generate_sql`, `deterministic_execute`, `execute_sql`, `verify_sql`, `repair_sql`, `clarify`, `agentic_escalation`, `abstain`.

### Objective

`minimize E[cost] subject to P(correct) >= R_target`

Cost dimensions include latency, tokens, tool calls and compute/action units. Do not claim global MDP optimality.

### Reliability targets

90%, 95%, 97%, 99%. If unreachable, report unreachable.

---

## 3. Required evidence ladder

The intended sequence is:

1. Correct P0–P5 benchmark.
2. Official Spider execution accuracy.
3. Paired statistics.
4. Token/cost accounting.
5. Failure taxonomy.
6. P5 characterization.
7. Unseen-schema evaluation.
8. Only if scientifically justified: P6.
9. P6 ablations.
10. Final statistical analysis.
11. Reproducibility package.
12. White paper / arXiv-ready manuscript.

**Mandatory strongest comparator:** P5 post-evidence cascade.

If P6 cannot beat P5 at matched reliability, reframe rather than forcing a positive result.

---

## 4. PRQS-1 research quality standard

Final evidence must support:

### Scientific validity
- explicit RQ and falsifiable hypotheses;
- literature gap and novelty boundary;
- strong baselines;
- controlled comparison;
- ablations;
- failure analysis;
- appropriate statistics and confidence intervals;
- generalization;
- threats to validity.

### Reproducibility
Record:

- dataset provenance and hashes;
- code commit;
- environment;
- model/provider;
- prompt specification;
- seed;
- raw traces;
- analysis scripts;
- artifact manifest.

### Integrity
No oracle leakage, post-hoc metric selection, baseline weakening, split contamination, hidden exclusions, paid-resource contamination, or unsupported claims.

### Reviewer attack matrix
Expect attacks on novelty, baseline strength, benchmark difficulty, synthetic-vs-real data, threshold tuning, metric cherry-picking, statistics, contamination, model specificity, engineering-vs-science confound, oracle leakage, reproducibility, cost-vs-quality tradeoff, hardware confounds, evaluator leakage, negative cases, benchmark overfitting and unclear contribution.

---

## 5. Spider dataset/evaluator contract

Current workflow uses the official Spider 1.0 development split.

- **Dev cases:** 1034
- **Runtime partition:** 12 chunks, size 90; final chunk is partial.
- **Unseen holdout:** 20%
- **Unseen seed:** 1729
- **Official evaluator commit:** `b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`
- Official source: `taoyds/spider`

Primary metric: **official Spider execution accuracy**.

Secondary metric: custom row-set equality, diagnostic only.

### Evaluator forensic conclusion

Some SQLs matched the secondary row-set evaluator while failing official Spider execution evaluation. This is not treated as an evaluator bug. The pinned official evaluator compares result values mapped to parsed SELECT value units. The custom row-set metric is more permissive.

Therefore:

> **Never replace or override official execution accuracy with the custom row-set metric.**

Relevant code: `research/spider_evaluator_forensics.py` and `research/spider_official_eval.py`.

---

## 6. Earlier 20-case smoke results — NOT research evidence

These were mechanics/engineering characterization only.

### Development smoke

| Policy | Official accuracy | Coverage | Mean cost units | Median latency | P95 latency |
|---|---:|---:|---:|---:|---:|
| P0 | 50% | 1.00 | 0.27 | 1611.72 ms | 4189.15 ms |
| P1 | 0% | 0.70 | 0.055 | 1.057 ms | 1.286 ms |
| P2 | 55% | 1.00 | 0.27 | 1145.58 ms | 3475.27 ms |
| P3 | 55% | 1.00 | 0.27 | 1143.17 ms | 3469.30 ms |
| P4 | 0% | 0.70 | 0.055 | 1.036 ms | 1.503 ms |
| P5 | 45% | 0.90 | 0.2695 | 1882.24 ms | 7679.29 ms |

P0 vs P5: P0-only correct 4; P5-only correct 3; delta -0.05; exact p=1.0; paired bootstrap mean delta ≈ -0.05021, CI ≈ [-0.30,+0.20].

### Unseen smoke

| Policy | Official accuracy | Coverage | Mean cost units | Median latency | P95 latency |
|---|---:|---:|---:|---:|---:|
| P0 | 5% | 1.00 | 0.27 | 1810.57 ms | 4604.45 ms |
| P1 | 0% | 0.65 | 0.0525 | 1.183 ms | 7.14 ms |
| P2 | 0% | 1.00 | 0.27 | 1248.91 ms | 2533.61 ms |
| P3 | 0% | 1.00 | 0.27 | 1254.60 ms | 2513.73 ms |
| P4 | 0% | 0.65 | 0.0725 | 1.119 ms | 1252.66 ms |
| P5 | 0% | 0.85 | 0.3925 | 2981.37 ms | 11021.45 ms |

These numbers must not be presented as final research evidence.

---

## 7. Runtime incident and actual fix

### RCA

A previous full-run partition hung on WTA case 31:

> “How many total tours were there for each ranking date?”

Observed sequence: P0 completed, P1 completed, P2 START, then no P2 END for >64 minutes. Because policy/case execution was serial, one pathological Ollama execution held the partition hostage.

Precise RCA:

> **Unbounded/hung Ollama inference inside the serial Spider P2 path, combined with a timeout mechanism that did not reliably regain control.**

Do not claim a deeper Ollama cause without evidence.

### Initial attempted fix

Signal-based timeout/checkpointing was insufficient.

### Actual containment fix

`research/spider_benchmark_isolated.py` now runs every `(case, policy)` in a separate OS process using `subprocess.run(..., timeout=...)` with `shell=False`. A timeout kills the child, records a timeout/error trace in the denominator, and checkpoints after each policy.

Current timeout: **150 seconds**.

This is an infrastructure/reproducibility control; it must not change the benchmark methodology.

Key commits:

- `0fdbf5d474f28bf7aff3ff36726a1e49e9809a5b` — process-isolated runner
- `def164e66338cca2ed69dc3a4913d9dc55a42d15` — workflow switched to isolated runner
- `2e6b57dbf90a26557b42d3f64e7c895b7792ccf8` — isolated recovery launch marker

---

## 8. Current isolated workflow

Primary file:

`.github/workflows/research-orchestrator-isolated.yml`

Contract:

- local Ollama only;
- default model `llama3.2:1b`;
- 12 × 90 runtime partitions;
- 350-minute benchmark-job timeout;
- 150-second per-policy process timeout;
- 20% unseen holdout, seed 1729;
- official evaluator pinned;
- raw chunk artifacts uploaded;
- aggregate merges all chunks;
- development + unseen analyses;
- evaluator forensics;
- P5 gate.

The P5 gate deliberately reports `STOP_AT_P5` and does not authorize P6 automatically.

### Legacy workflow warning

There are multiple historical workflows. Do not accidentally launch the legacy non-isolated runner. Use `research-orchestrator-isolated.yml` and `research.spider_benchmark_isolated` for the final evidence cycle.

---

## 9. Existing isolated artifacts

A prior isolated execution produced all 12 chunk artifacts under workflow run:

`34206500727`

Artifacts observed:

- `p1-spider-isolated-chunk-0`
- `p1-spider-isolated-chunk-1`
- `p1-spider-isolated-chunk-2`
- `p1-spider-isolated-chunk-3`
- `p1-spider-isolated-chunk-4`
- `p1-spider-isolated-chunk-5`
- `p1-spider-isolated-chunk-6`
- `p1-spider-isolated-chunk-7`
- `p1-spider-isolated-chunk-8`
- `p1-spider-isolated-chunk-9`
- `p1-spider-isolated-chunk-10`
- `p1-spider-isolated-chunk-11`

**First priority in a new chat:** verify these artifacts before running another benchmark.

Verify:

- every intended development case is present;
- every intended unseen case is present;
- all six policies exist per case;
- no duplicate `(question, db_id, policy)` keys;
- timeout/error traces remain in denominator;
- chunk manifests agree on commit/model/provider/evaluator/seed/split/chunk size/timeout/runner;
- development and unseen totals match the intended frozen split.

If complete, **do not rerun inference**. Analyze the frozen evidence.

---

## 10. Analysis pipeline

Primary analyzer:

`scripts/analyze_research_benchmark.py`

It currently calculates:

- official execution accuracy;
- Wilson 95% CIs;
- coverage;
- mean research cost units;
- input/output token totals and means;
- mean LLM calls;
- median/P95 latency;
- reliability targets;
- paired McNemar statistics;
- paired bootstrap;
- reliability frontiers;
- failure taxonomy;
- P5 action paths;
- termination reasons;
- repair cases;
- P6 gate.

For final publication-grade analysis, also explicitly consider effect sizes, CIs for cost/latency, multiple-comparison control where applicable, unit of analysis, timeout sensitivity, and transparent handling of all failed cases.

Do not select a statistical test after seeing which one gives the desired result.

---

## 11. P5/P6 decision logic

The current automated P6 gate blocks when:

1. no P0–P5 policy reaches 90% reliability;
2. P5 regresses against P0 on paired official execution accuracy;
3. unseen-schema and prospective ablation evidence are still required.

Human research interpretation must go further than the automated gate.

Possible conclusions:

### A. P5 improves at matched reliability/cost
Characterize P5 deeply, then design P6 prospectively only if a defensible unresolved gap remains.

### B. P5 does not improve
Do not force P6. Reframe around the empirical boundary/failure modes of evidence-dependent execution, if the evidence supports that story.

### C. No policy reaches 90%
Report the reliability target as unreachable under the tested model/system. Do not move the target merely to create a positive result.

---

## 12. Literature/gap context already reviewed

Relevant themes/papers already examined include TIDE-Bench, GROUND, Beyond the Harness, TraceSQL, Agentic-SQL Revisited, ACTS-SQL, AnnoIndex, DBLifeBench, ABISS, RBAC Text-to-SQL, selective prediction for Text-to-SQL, TAHOE, ZAS-SQL, EnterpriseMem-Bench, governed enterprise analytics APIs, DAB, Coverage Illusion, BUDDY, and other adaptive routing/agentic systems.

The established gap conclusion is:

> Generic routing, adaptive depth, or “use a cheaper model first” is insufficient novelty. The defensible angle is the controlled empirical study of heterogeneous evidence-dependent analytical action selection under explicit reliability constraints, with strong baselines, unseen-schema transfer, and failure analysis.

Do not overstate novelty without rechecking the current literature before manuscript submission.

---

## 13. Important project documents

- `RESEARCH_ROADMAP.md`
- `docs/PROJECT1_LITERATURE_GAP_ANALYSIS.md`
- `docs/PROJECT1_RESEARCH_PROPOSAL.md`
- `docs/PROJECT1_EVALUATOR_METHODOLOGY.md`
- `docs/REMOTE_OLLAMA_RESEARCH_RUNNER.md`
- `docs/EXPENSIVE_BENCHMARK_POLICY.md`
- `docs/EVOLUTION.md`
- `docs/ARCHITECTURE_DECISIONS.md`
- `docs/HLD.md`
- `docs/LLD.md`
- `docs/EVALUATION.md`
- `docs/INTERVIEW_STORY.md`

External forensic report previously created locally:

`/mnt/data/PROJECT1_SPIDER_FORENSIC_ANALYSIS.md`

---

## 14. Useful commits

- `0e46cac3e418b3f716188afd81420265b588a681` — CI Recovery Engineer
- `b87b004538429c7ee654fbf8918739be05a978d3` — evaluator methodology
- `1b808b327b0315643c802e3bb5ab8fb4970d02ad` — remote Ollama research runner
- `ad6c0e86417a00c37a4144e980bdb4a99c775289` — PRQS-1 preflight gate
- `dcc5e573bfe19e0a01ce3cfa939c0316c2b2bd14` — unattended P1 orchestrator
- `74c40d42f2238137025b9230d587b600a24322a3` — parallel chunked benchmark
- `0fdbf5d474f28bf7aff3ff36726a1e49e9809a5b` — process isolation
- `def164e66338cca2ed69dc3a4913d9dc55a42d15` — isolated workflow integration
- `2e6b57dbf90a26557b42d3f64e7c895b7792ccf8` — isolated recovery launch

---

## 15. Immediate next-chat instruction

Start with:

> **Continue Project 1 from `docs/PROJECT1_HANDOFF.md`. First inspect run `34206500727` artifacts for completeness. Do not launch another benchmark until artifact completeness is verified. If complete, merge/analyze the frozen P0–P5 development + unseen evidence and produce the conclusive statistical/failure/cost/latency/P5 decision. Only then consider P6.**

**Priority:** results and scientific conclusion, not more automation.
