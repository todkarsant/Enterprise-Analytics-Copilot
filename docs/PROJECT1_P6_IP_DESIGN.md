# Project 1 — P6-IP Incumbent-Preserving Evidence Policy

**Status:** Approved for controlled experiment design; P0–P5 remain frozen.

## 1. Purpose

P6-IP is the final controlled challenger after the frozen P0–P5 benchmark and the P5R mechanism-forensics study. It tests a narrower question than generic adaptive routing:

> **When intermediate evidence suggests that an incumbent analytical answer may be wrong, can a policy intervene without replacing the incumbent unless the challenger passes a predefined verification gate?**

The experiment is explicitly designed to measure **incumbent harm** (P0 correct → challenger wrong) separately from **rescue** (P0 wrong → challenger correct).

P6-IP is not claimed as a novel routing algorithm. Its scientific purpose is to test whether incumbent-preservation changes the reliability/cost trade-off observed in P5/P5R.

## 2. Frozen incumbent

P0 (Always-LLM) is the incumbent reference. Its trace and answer are computed exactly as in the frozen benchmark.

P6-IP must never use gold SQL, official evaluator outcomes, or holdout labels to decide whether to intervene or replace the incumbent.

## 3. Decision flow

```text
question
   ↓
P0 incumbent answer
   ↓
evidence / risk assessment
   ├── KEEP ───────────────────────→ incumbent
   │
   └── INTERVENE
          ↓
      challenger SQL
          ↓
      deterministic verification
          ├── FAIL → preserve incumbent
          └── PASS → compare/review
                         ↓
                    replace incumbent
                    only if all gates pass
```

## 4. Predefined gates

The initial controlled implementation uses only information available at decision time:

### Gate A — intervention eligibility

Intervene only when the post-evidence selector identifies a predefined evidence-risk condition. The selector may use the question, incumbent SQL, schema, and observed execution evidence. It may not use gold SQL or benchmark outcomes.

### Gate B — challenger validity

The challenger must:

1. produce non-empty SQL;
2. pass the existing SQL safety/validity boundary;
3. execute successfully on the same database;
4. expose complete execution evidence (row/column counts);
5. satisfy the requested structural cues used by the selector, where applicable.

Execution success alone is **not** sufficient for replacement.

### Gate C — incumbent-preservation rule

If the challenger fails any verification gate, preserve the P0 incumbent. No repair loop may silently convert a failed challenger into an accepted replacement.

### Gate D — replacement rule

A replacement is accepted only when the challenger passes every predefined verification check. Otherwise the incumbent is retained.

The experiment must record the reason for KEEP, INTERVENE, challenger rejection, or replacement.

## 5. Required outcomes

For every case, classify the final P6-IP outcome against P0:

- **preserved-correct:** P0 correct and P6-IP retains it;
- **harm:** P0 correct and P6-IP replaces it with an incorrect answer;
- **rescue:** P0 wrong and P6-IP replaces it with a correct answer;
- **preserved-wrong:** P0 wrong and P6-IP retains it;
- **no-output/runtime failure:** execution cannot complete under the fixed timeout and remains in the denominator.

Primary intervention metrics:

- harm rate among P0-correct interventions;
- rescue rate among P0-wrong interventions;
- net intervention gain = rescues − harms;
- intervention rate;
- replacement rate;
- incumbent preservation rate;
- challenger rejection rate.

Primary benchmark metrics remain official Spider execution accuracy, cost, latency, coverage, and failure taxonomy.

## 6. Reliability analysis

Evaluate P6-IP against P0 and P5/P5R using paired case-level comparisons. Report point estimates and confidence intervals. Use the same frozen 1034-case development partition and the same 254-case held-out-schema partition. Do not tune gates on the holdout.

Reliability targets remain fixed at 90%, 95%, 97%, and 99%. If a target is unreachable, report it as unreachable.

## 7. Prospective ablation plan

At minimum:

1. **No incumbent preservation:** reproduce the challenger replacement rule without the preservation gate where technically feasible, as a mechanism comparator.
2. **Evidence selector ablation:** remove individual evidence-risk classes to measure which signals affect rescue/harm.
3. **Verification ablation:** remove one verification component at a time while keeping the rest fixed.
4. **Threshold sensitivity:** if a numeric threshold is introduced, freeze a prespecified grid on development data and evaluate the chosen configuration once on holdout. No post-hoc holdout tuning.

Ablations must be specified before holdout execution.

## 8. Hard-stop criterion

P6-IP is considered unsuccessful as a reliability mechanism if it does not materially reduce incumbent harm while retaining a meaningful fraction of challenger rescues at a defensible cost.

If the hard-stop criterion is met, do not invent a more elaborate policy to obtain a positive result. Reframe the contribution around the empirical boundary/failure modes of evidence-dependent analytical execution.

## 9. Scientific boundary

P6-IP does not establish generic optimality, universal reliability, or novelty of adaptive routing. It tests one concrete reliability mechanism under the frozen enterprise/Text-to-SQL benchmark protocol.
