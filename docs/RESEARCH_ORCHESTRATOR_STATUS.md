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
