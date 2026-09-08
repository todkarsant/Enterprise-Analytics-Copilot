# Hard-Control Implementation Status

Updated after the P6-IP artifact-integrity RCA.

## Control 1 — fail-closed evaluation integrity

**Implemented.** Analysis rejects missing/non-boolean official correctness. Post-hoc P0 recomputation is used instead of silent coercion.

## Control 2 — experimental protocol sequencing

**Implemented in the controlled workflow contract.** The intended execution DAG is development matrix → development freeze gate → holdout matrix → final analysis. Holdout execution is downstream of the freeze job and the controlled workflow is manual-only to prevent corrective commits from launching inference.

## Control 3 — research state / definition of done

**Implemented in CI.** `research-state-machine.yml` checks required repository evidence, validates the controlled-workflow protocol markers, verifies the experiment remains manual-only, and runs the relevant regression tests. The state-machine definition is recorded in `docs/RESEARCH_STATE_MACHINE.md`.

## Definition of done

A scientific finding is not considered complete from conversation state alone. The repository must contain the implementation/evidence, CI must validate it, and the resulting artifact must be validated before a scientific conclusion is treated as locked.
