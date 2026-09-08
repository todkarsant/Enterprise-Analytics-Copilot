# Research State Machine

This repository treats scientific progress as a controlled state machine. A finding is not complete because it was discussed or observed; it is complete only after the required repository and validation transitions have occurred.

## States

`DESIGNED → IMPLEMENTED → CI_VALIDATED → EXECUTED → ARTIFACT_VALIDATED → ANALYZED → SCIENTIFIC_DECISION → PAPER_LOCKED`

Repair path: `ARTIFACT_VALIDATED/ANALYZED → REPAIR_REQUIRED → REPAIR_COMMITTED → CI_VALIDATED`.

## Definition of done

Every scientifically material finding must produce a repository change, Git commit, CI validation, experiment/analysis artifact where applicable, artifact-integrity validation, and an explicit scientific decision in repository evidence. Conversation-only status does not advance the research state.

## Hard controls

- Missing/invalid official correctness is a hard failure, never `False` by coercion.
- P6 development must finish and pass a freeze gate before any P6 holdout execution.
- The state-machine checker fails CI when required repository evidence for the declared state is absent.
- Holdout data may not be used to tune policy thresholds or implementation choices.

## Required evidence by state

| State | Required evidence |
|---|---|
| DESIGNED | experiment design and frozen hypotheses |
| IMPLEMENTED | implementation + unit tests |
| CI_VALIDATED | green research CI |
| EXECUTED | immutable run ID and artifacts |
| ARTIFACT_VALIDATED | integrity checks + provenance manifest |
| ANALYZED | reproducible analysis artifact |
| SCIENTIFIC_DECISION | explicit conclusion + stop/continue decision |
| PAPER_LOCKED | paper evidence record tied to immutable artifacts |

The checker does not infer scientific conclusions. It enforces the evidence needed to claim a repository state.
