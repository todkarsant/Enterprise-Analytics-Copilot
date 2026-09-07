# P0-P6 Baseline Specifications

## Goal

Freeze baseline behavior before implementation so comparisons cannot be tuned after observing P6 results.

## P0 — Always-LLM

- Route every supported analytical question to the same LLM SQL-generation path.
- Mandatory SQL safety/governance checks remain enabled.
- No adaptive escalation based on evidence.
- Retries only when required by the common execution contract.

## P1 — Deterministic-only

- Use repository deterministic planners/analytical plans.
- Unsupported questions abstain.
- No LLM SQL generation.
- This baseline measures the lower-cost/limited-coverage endpoint.

## P2 — Static Hybrid

- Use deterministic planner when an intent matches.
- Otherwise invoke the baseline LLM SQL path.
- No learned/query-time routing.

## P3 — Query-only Complexity Router

Features must be available before expensive execution begins, e.g.:

- question length
- lexical/intent features
- requested operation class
- number of entities/constraints
- detected temporal complexity
- detected comparative language

The router cannot use retrieved schema contents, generated SQL, execution results, verifier output, or evaluator labels.

## P4 — Query-only Confidence Router

- Estimate pre-execution probability of success.
- Route low-confidence cases to the expensive path.
- Calibrate only on training/validation data.
- Final test labels cannot influence thresholds.

## P5 — Post-Evidence Cascade

A strong cheapest-first baseline. The exact implementation must be documented before tuning and then frozen.

Recommended contract:

1. perform inexpensive schema/context processing;
2. run the cheapest eligible analytical path;
3. inspect only evidence produced by that path;
4. invoke the next expensive operation if a frozen escalation condition is met;
5. repeat until success, budget exhaustion, or abstention.

P5 may use model escalation, but it should not have access to the broader heterogeneous action policy of P6.

## P6 — Heterogeneous Evidence-Dependent Policy

The policy selects the next action from the common action registry using the current state and evidence. Candidate actions:

- retrieve_schema
- retrieve_examples
- generate_sql
- deterministic_execute
- execute_sql
- verify_sql
- repair_sql
- clarify
- agentic_escalation
- abstain

The action registry and state schema must be versioned. The policy may be rule-based initially and learned later; the experiment must clearly distinguish policy selection from action execution.

## Fairness constraints

All policies must:

- use the same benchmark cases;
- use the same database state;
- use equivalent safety constraints;
- report all model/tool calls;
- include routing/verifier costs;
- use identical test-time external information;
- run on the same hardware/environment where practical;
- publish stochastic seeds where applicable.

## Common evaluator

All P0-P6 outputs are evaluated by the same evaluator implementation. The evaluator is never available as policy state during the primary experiment.

## Frozen comparison rule

No baseline may be deliberately weakened. If a baseline requires tuning, tuning occurs only on development/validation data and its final configuration is frozen before test evaluation.
