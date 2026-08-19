# Changelog

## 0.2.9

- Fixed SQL guard handling of aliases applied to CTE relations, e.g. `FROM periods p`.
- Added explicit support for CTE names and their outer-scope aliases in the read-only SQL guard.
- Preserved strict physical-schema validation for base-table columns.
- Fixed the V0.2.8 `sales_decline_analysis` end-to-end 422 regression.


## 0.2.8

- Fixed SQL guard handling of CTE-derived output columns in trusted analytical plans.
- Added regression coverage validating both `sales_decline_analysis` SQL steps.
- Preserved strict repeated-table rejection for LLM-generated SQL.

## 0.2.7

- Added deterministic analytical reasoning for sales-decline questions.
- Added engineering evolution documentation and ADRs.
- Added FastAPI lifespan startup handling.

## 0.2.6

- Added a conservative deterministic Intent Planner before LLM SQL generation.
