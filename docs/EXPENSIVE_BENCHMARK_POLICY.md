# Expensive Benchmark Policy

## HARD RULE — Azure LLM resources are final-run only

This repository follows a strict research execution policy:

1. **All development, debugging, unit tests, integration tests, heuristic tuning, P5 characterization, and iterative benchmark runs MUST use a local Ollama model.**
2. **Azure OpenAI / paid LLM resources MUST NOT be used during iterative development.**
3. Azure credentials MUST NOT be exposed to ordinary `push`, `pull_request`, CI, or development workflows.
4. Any benchmark intended to consume Azure LLM tokens requires **explicit user authorization immediately before the final run**.
5. Before the final Azure run, the changed code and workflow MUST first pass cheap/static validation and local Ollama validation.
6. The final Azure run is a controlled, deliberate research execution—not a CI side effect.
7. No automatic workflow trigger (`push`, `pull_request`, scheduled execution, or dependency-triggered execution) may launch an Azure-backed benchmark.
8. If an Azure-backed workflow is retained for the final run, Azure credentials must be made available only to that explicitly authorized manual execution.
9. Accidental or unauthorized Azure execution must be treated as a workflow defect and fixed before further research runs.

## Required execution ladder

```text
Code change
   ↓
Static inspection / cheap tests
   ↓
Local Ollama benchmark / characterization
   ↓
Analyze results and freeze code
   ↓
Final-run review
   ↓
EXPLICIT USER AUTHORIZATION
   ↓
Manual Azure benchmark
```

## Prohibited pattern

```text
Code push / PR sync
   ↓
GitHub Actions
   ↓
Azure credentials
   ↓
LLM benchmark
```

This policy exists specifically to prevent accidental token consumption while the research implementation is being developed.

## Remote Ollama execution boundary

Remote Ollama execution is permitted for **iterative research workloads** when it runs an Ollama model in a controlled, reproducible environment such as an isolated GitHub Actions runner. Remote execution is considered an execution-environment implementation of the local-Ollama requirement; it is **not** permission to use Azure or another paid LLM provider.

Before remote execution is accepted as research evidence, the environment must record and preserve:

- exact repository commit SHA;
- exact Ollama/model identity and version where available;
- Python/runtime and dependency versions;
- dataset and evaluator provenance/hashes;
- prompts/configuration and benchmark seed;
- raw traces and generated analysis artifacts;
- execution resource/time limits; and
- enough metadata to reproduce the run independently of the user's laptop.

A remote runner must first pass a **local-vs-remote reproducibility/equivalence check** on a fixed characterization workload. Differences must be investigated and documented before full-scale results are treated as comparable research evidence.

The remote runner must not modify the benchmark, evaluator, policies, metrics, acceptance criteria, or exclusion rules to improve scores. Its purpose is to remove laptop availability as an execution bottleneck while preserving research integrity.
