# P1 Research Orchestrator Status

The unattended Project 1 research cycle is enabled on `research/p1-evaluator-hardening`.

Execution contract:

1. PRQS-1 preflight gate.
2. Remote Ollama smoke validation.
3. Full Spider development-set P0-P5 benchmark unless an explicit run limit is supplied.
4. Official evaluator analysis and forensic diagnostics.
5. Frozen unseen-schema P0-P5 benchmark.
6. Statistical/diagnostic analysis.
7. P5 research-gate artifact.
8. Stop for human research review; no automatic P6 implementation.

Iterative execution is Ollama-only. The orchestrator contains no paid-provider execution path and performs no research-score tuning.

Preflight hardening recorded on 2026-09-08: the PRQS gate now uses the GitHub Actions ref when the checkout is detached, and initializes the deterministic CSV-backed application fixture before running API tests. These are CI reproducibility fixes only; benchmark/evaluation definitions and research policies are unchanged.
