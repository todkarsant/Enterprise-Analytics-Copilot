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
| ADR-007 | Incumbent-preserving P6-IP as final controlled reliability experiment | Accepted |
| ADR-008 | Separate Defensibility Layer for decision/control evidence | Accepted |

## ADR-007 — Incumbent-preserving P6-IP

P6-IP is retained as the final controlled challenger after P0–P5 and P5R. It treats P0 as the incumbent and explicitly separates **rescue** (P0 wrong → challenger correct) from **harm** (P0 correct → challenger wrong). A challenger may replace the incumbent only after predefined decision-time verification gates pass. Gold SQL and evaluator outcomes are prohibited from the decision path.

See `docs/PROJECT1_P6_IP_DESIGN.md`.

## ADR-008 — Separate Defensibility Layer

Defensibility is implemented as a separate observability/control-evidence layer rather than being conflated with model accuracy or the P6-IP algorithm. It records decision provenance, evidence, policy reason, verification, authorization hooks, outcome, intervention class, cost/latency and reproducibility metadata. It must not alter the frozen benchmark methodology or imply legal compliance/production readiness without separate evidence.

See `docs/PROJECT1_DEFENSIBILITY_LAYER.md`.

The key principle remains: **do not add model capability where deterministic engineering can solve the problem more reliably, and do not hide reliability failures behind aggregate metrics.**