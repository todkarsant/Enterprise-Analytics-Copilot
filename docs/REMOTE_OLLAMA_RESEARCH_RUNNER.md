# Remote Ollama Research Runner

## Purpose

Provide a reproducible remote execution path for iterative research benchmarks so P1 experiments do not depend on a developer laptop remaining powered on.

## Current baseline

The existing `spider-benchmark-local` GitHub Actions workflow already provisions Ollama on an `ubuntu-latest` runner and successfully executes the local-Ollama P0-P5 and unseen-schema benchmark pipeline. This document defines the hardening required before treating that capability as the standard unattended research runner.

## Research-integrity boundary

- Iterative research inference remains Ollama-only.
- Azure/paid LLM execution is prohibited during development and characterization.
- Azure credentials must not be available to ordinary push/PR workflows.
- This infrastructure work must not change benchmark questions, evaluator definitions, policy logic, metrics, thresholds, or exclusions to improve results.
- Full research runs must be deliberate and traceable, not accidental side effects of code pushes.

## Required provenance for every research run

Record at minimum:

- repository and exact commit SHA
- workflow/run identifier
- Python version and dependency lock/version information
- runner/OS information
- Ollama version
- model name and model identifier/digest when available
- model configuration used by the benchmark
- prompt/template version
- Spider dataset provenance and SHA-256 manifest
- unseen-schema generation seed and resulting holdout manifest hash
- pinned official evaluator commit
- benchmark limit/split
- random seeds
- start/end timestamps
- benchmark configuration and relevant environment variables (excluding secrets)
- raw traces and analysis artifact hashes

## Execution modes

### Smoke

Small representative run for code/CI validation. Not research evidence.

### Characterization

Controlled local-Ollama run used to identify failures and validate the harness. Not sufficient by itself for publication claims.

### Research

Full frozen benchmark with all required policies, unseen-schema evaluation, raw traces, statistical analysis, evaluator diagnostics, and provenance manifest. Research claims may rely on this tier only after methodology freeze and quality gates pass.

## Reproducibility protocol

1. Run the same frozen configuration twice on the remote runner.
2. Verify identical dataset/evaluator/model/prompt provenance.
3. Compare deterministic outputs where deterministic behavior is expected.
4. For stochastic model behavior, record seeds/configuration and report run-to-run variability rather than assuming bitwise identity.
5. Record infrastructure differences that could affect latency.
6. Do not collapse infrastructure variability into model-quality claims.

## Local-to-remote validation

Before the remote path becomes the authoritative execution environment, run a small paired validation using the same commit, model, prompt, dataset subset, and evaluator. Compare:

- execution accuracy
- SQL validity/result correctness diagnostics
- token counts
- LLM call counts
- latency distribution
- failure taxonomy

Material differences must be investigated before full-scale research evidence is collected remotely.

## Resource controls

- Explicit timeout and concurrency limits.
- Explicit benchmark limit for automatic workflows.
- Full research execution should require deliberate workflow dispatch or an equivalent controlled trigger.
- Artifact retention must be sufficient for the research cycle.
- No paid model fallback.
- Provider must fail closed if the configured provider is not Ollama for iterative research.

## Acceptance criteria

- Full P0-P5 and unseen-schema benchmark can run with the user's laptop offline.
- Every research run produces a provenance/reproducibility manifest.
- A second run can reconstruct the same configuration from recorded metadata.
- Local-to-remote validation is completed and documented.
- Automatic push workflows cannot launch Azure/paid inference.
- Research artifacts are linked to exact code/evaluator/dataset/model provenance.
- Research and characterization artifacts are clearly distinguished.

## Next implementation steps

1. Add a machine-readable run manifest.
2. Capture runner, Ollama, model, dependency, dataset, evaluator, prompt, and seed provenance.
3. Add fail-closed provider/cost guardrails.
4. Separate automatic smoke execution from deliberate full research execution.
5. Add local-vs-remote paired validation.
6. Add reproducibility verification workflow.
7. Document operational recovery and artifact retention.
8. Only after these gates, use the remote runner for the full P0-P5 baseline campaign.
