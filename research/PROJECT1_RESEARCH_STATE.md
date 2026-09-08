# Project 1 Research State

This file is the human-readable control record for the P6-IP experiment.

## Current state

**ARTIFACT_VALIDATED → REPAIR_REQUIRED**

The P6-IP controlled execution completed in GitHub Actions run `34252265013`. The P6 artifacts were produced, but the frozen P0 comparator contained incomplete case-level `official_execution_correct` fields. The fail-closed analyzer correctly refuses to coerce missing values to false.

Therefore the experiment is **not scientifically analyzed yet**. The next permitted transition is post-hoc comparator repair and validation; this does not require new LLM inference.

## Mandatory state machine

```text
DESIGNED
  ↓
IMPLEMENTED
  ↓
CI_VALIDATED
  ↓
EXECUTED
  ↓
ARTIFACT_VALIDATED
  ↓
ANALYZED
  ↓
SCIENTIFIC_DECISION
  ↓
PAPER_LOCKED
```

If a material defect is found at any stage:

```text
REPAIR_REQUIRED → REPAIR_COMMITTED → CI_VALIDATED / ARTIFACT_VALIDATED
```

A state cannot be advanced without the required evidence fields in `research/PROJECT1_RESEARCH_STATE.json`.

## Definition of done

A scientifically material finding is not considered complete until:

`Finding → repository change → CI validation → artifact → artifact validation → analysis → scientific decision → paper evidence`

## Experimental protocol control

P6-IP is now encoded as a dependency graph:

`development → development freeze manifest → holdout → final aggregation`

The holdout is not executable from the development job and cannot start until the development freeze job succeeds. The controlled experiment is manual-only so corrective repository pushes cannot silently trigger another expensive inference run.

## Non-negotiable rules

- P0 remains the incumbent.
- Frozen P0-P5 results are not overwritten by malformed reanalysis.
- Holdout is never used for tuning.
- Missing official correctness is an error, not a negative result.
- No Azure/paid inference run without explicit authorization.
- If P6-IP fails its prespecified incumbent-preservation stop rule, algorithm development stops and the result is reported as an empirical boundary/failure-mode study.
