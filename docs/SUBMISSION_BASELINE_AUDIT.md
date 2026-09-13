# Project 1 — Submission Baseline Audit

**Status:** Reference-normalization pass completed on `research/paper-lit-integration`.

## Scope

This audit verifies the manuscript-level submission baseline after integrating the four requested scientific references:

- Nisa et al. (2026), *Agentic AI: The age of reasoning—A review*.
- Song & Zhang (2026), *From black box to physically interpretable: Trustworthy computing for AI-driven decision-making and control*.
- Li et al. (2026), *G²SQL: guided & guarded Text-to-SQL generation with two-stage verification*.
- Birhane et al. (2024), *AI auditing: The Broken Bus on the Road to AI Accountability*.

## Completed

- Removed the artificial Gartner placeholder bibliography entry.
- Renumbered the bibliography into a consistent manuscript sequence: scientific references [1–28], Gartner industry-context references [29–34].
- Removed web-tool citation artifacts from the bibliography.
- Updated in-text citations to the new numbering.
- Preserved the distinction between scientific evidence, industry context, auditability and institutional accountability.
- Preserved the P6-IP negative result and the explicit holdout-ordering limitation.
- Added a manuscript-level claim-discipline ledger.

## Scientific position

The manuscript remains a conditional empirical boundary/failure-mode study. It does not claim universal impossibility, routing optimality, formal safety, legal compliance, governance completeness, or production readiness.

## Remaining pre-submission checks

The following should still be completed before an external submission is declared final:

1. Independently render the manuscript and inspect figures/tables/page breaks.
2. Run a final numerical cross-check against raw/corrected artifacts.
3. Verify every bibliography metadata field against its primary source.
4. Add/verify venue-specific Data Availability and Code Availability statements.
5. Confirm that all repository paths, commit hashes and manifests referenced by the manuscript exist.
6. Perform a final hostile-review pass focused on P0 strength, verifier weakness, Spider-to-enterprise transfer, and novelty boundary.

This document intentionally does not claim those remaining checks have already passed.
