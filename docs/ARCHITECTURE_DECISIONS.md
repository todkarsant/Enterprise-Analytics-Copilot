# Architecture Decisions — Enterprise Analytics Copilot

This file is an index of the important decisions. Detailed records live in `docs/decisions/`.

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | Provider abstraction | Accepted |
| ADR-002 | SQL AST guardrail | Accepted |
| ADR-003 | Bounded repair loop | Accepted |
| ADR-004 | Deterministic intent planner | Accepted |
| ADR-005 | Analytical reasoning planner | Accepted |
| ADR-006 | Keep small model as baseline before benchmarking replacement | Accepted |

The key principle is: **do not add model capability where deterministic engineering can solve the problem more reliably.**
