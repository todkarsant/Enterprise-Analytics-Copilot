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
