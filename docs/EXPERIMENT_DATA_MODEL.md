# Experiment Data Model

## Purpose

Define a machine-readable contract for benchmark cases, policy runs, actions, evidence, outcomes, and aggregate analysis before implementation.

## Benchmark case

```yaml
case_id: string
question: string
domain: string
schema_id: string
split: development|validation|test|unseen_schema|unseen_domain
stratum:
  - deterministic
  - schema_ambiguity
  - semantic_ambiguity
  - grain_join_risk
  - misleading_premise
  - unanswerable
  - governance
  - multi_step
  - multi_turn
  - execution_repair
expected:
  answerable: boolean
  reference_sql: optional string
  reference_result: optional structured data
  accepted_answers: optional structured data
  required_properties: optional list
  governance_constraints: optional list
metadata:
  source: public|controlled|synthetic|realistic_enterprise
  notes: optional string
```

Reference fields are evaluator-only and must never be exposed to the policy.

## Policy run

```yaml
run_id: string
case_id: string
policy_id: P0|P1|P2|P3|P4|P5|P6
model_id: string
provider_id: string
seed: optional integer
started_at: timestamp
final_status: correct|incorrect|abstain|clarification_required|policy_violation|error
final_answer: string
metrics:
  reliability_components: object
  total_latency_ms: number
  llm_latency_ms: number
  db_latency_ms: number
  deterministic_latency_ms: number
  input_tokens: integer
  output_tokens: integer
  estimated_cost_usd: number
  llm_calls: integer
  tool_calls: integer
  actions: integer
  escalations: integer
  clarifications: integer
  abstentions: integer
```

## Action event

Every action is logged in order.

```yaml
step: integer
action_id: string
action_type: string
state_features_version: string
started_at: timestamp
latency_ms: number
input_tokens: integer
output_tokens: integer
estimated_cost_usd: number
outcome: success|failure|empty|blocked|abstain
error_class: optional string
evidence_ids: list[string]
policy_score: optional number
```

## Evidence object

```yaml
evidence_id: string
kind: schema|retrieval|sql_validation|sql_execution|verification|governance|clarification|model_output
producer_action_id: string
content_hash: string
summary: string
```

Sensitive raw database results should not be duplicated into experiment logs unless required for reproducibility; prefer deterministic references/hashes for large artifacts.

## Evaluator outputs

Evaluators run after policy execution and are outside the policy state.

```yaml
sql_valid: boolean
semantic_correct: boolean
result_correct: boolean
answer_correct: boolean
evidence_grounded: boolean
governance_compliant: boolean
ambiguity_handled: boolean
unanswerable_handled: boolean
failure_class: optional string
```

## Failure taxonomy

Use one primary failure class plus optional secondary classes:

- SQL_SYNTAX
- SQL_SCHEMA
- WRONG_TABLE
- WRONG_JOIN
- WRONG_GRAIN
- WRONG_METRIC
- WRONG_FILTER
- WRONG_TIME_WINDOW
- WRONG_AGGREGATION
- UNSUPPORTED_CLAIM
- MISLEADING_PREMISE_ACCEPTED
- AMBIGUITY_NOT_RESOLVED
- UNANSWERABLE_NOT_ABSTAINED
- GOVERNANCE_VIOLATION
- RETRIEVAL_FAILURE
- VERIFICATION_FAILURE
- OVER_ESCALATION
- UNDER_ESCALATION
- TOOL_FAILURE
- MODEL_FAILURE

## Aggregation requirements

Aggregate results must retain policy/model/schema/domain identifiers. Never publish only a single global accuracy number.

Required slices:

- overall
- each workload stratum
- each schema
- seen vs unseen schema
- answerable vs unanswerable
- governance-constrained vs unconstrained
- stochastic vs deterministic route

## Reproducibility

Every aggregate result must be traceable to:

`claim_id -> experiment_id -> run_ids -> benchmark_version -> policy_version -> model/provider version -> code commit`
