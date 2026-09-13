# Project 1 — JAI Reference Provenance Audit

**Date:** 2026-09-14  
**Purpose:** Convert the Project 1 literature corpus into a JAI-compliant reference set without discarding the underlying research provenance.

## 1. JAI rule applied

The Journal of Automation and Intelligence Guide for Authors states that arXiv references are not recommended when a published version can reasonably be obtained. It does **not** prohibit arXiv references: when an arXiv citation must remain, the guide specifies an arXiv identifier in the journal reference format. The guide also requires bidirectional citation/reference consistency, encourages DOI links, and requires full URL plus access date for web references.

## 2. Decision policy

Each source is classified as:

- **A — Published replacement verified:** use the journal/conference/publisher version in the JAI manuscript.
- **B — Formal publication/venue identified but no stronger bibliographic record verified:** retain the arXiv version provisionally and continue monitoring.
- **C — ArXiv/preprint only at audit time:** retain arXiv because no reasonably obtainable formal publication was verified.
- **D — Remove from final manuscript:** source is not needed for the final argument, although it remains in the research corpus/provenance record.

The research corpus and the final manuscript bibliography are intentionally different objects. The corpus records what was investigated; the final bibliography records sources directly needed to support the submitted manuscript.

## 3. Current manuscript reference audit

| Ref. | Source | Status at 2026-09-14 | JAI action |
|---:|---|---|---|
| 1 | Richardson, *What Predicts Correctness in Text-to-SQL? A Selective-Prediction Study*, arXiv:2607.06799 | C | Retain arXiv; no published version verified in this audit |
| 2 | Shukla et al., *TraceSQL: Traceable Answerability Estimation for Reference-Free Text-to-SQL Verification*, arXiv:2608.17795 | C | Retain arXiv; no published version verified |
| 3 | Maleki, Pourreza & Rafiei, *Confidence Estimation for Text-to-SQL in Large Language Models*, AAAI 2026, 40(38), 32474–32482, DOI 10.1609/aaai.v40i38.40523 | A | Use published AAAI version |
| 4 | Hussain & Nielbo, *The Coverage Illusion: From Pre-retrieval Routing Failure to Post-retrieval Cascades in a Production RAG System*, arXiv:2605.27220 | C | Retain arXiv; no formal publication verified |
| 5 | Liskowski et al., *Compositional Online Learning for Semantic Data Processing Systems*, arXiv:2608.27244 | C | Retain arXiv; no formal publication verified |
| 6 | Chen et al., *Reliable Text-to-SQL with Adaptive Abstention*, Proc. ACM Manag. Data 3(1), Article 69, DOI 10.1145/3709719 | A | Use published ACM version |
| 7 | Pillai, *GROUND: Reducing Hallucinations in LLM-Based Enterprise Analytics Through Governed Semantic Definitions*, arXiv:2608.26157 | C | Retain arXiv; no formal publication verified |
| 8 | Sullutrone et al., *ABISS: Evaluating Text-to-SQL Systems Through Agent Interaction*, arXiv:2607.23340 | C | Retain arXiv; no formal publication verified for this work |
| 9 | Zhao et al., *Agentic-SQL Revisited: Autonomy-Based Taxonomy and Empirical Benchmark Analysis for LLM Text-to-SQL* | A | **Replace arXiv with Springer/ICIC 2026 proceedings version, DOI 10.1007/978-981-92-3438-7_51, pp. 601–612** |
| 10 | Huang et al., *ACTS-SQL: Agentic and Critic-Oriented Tree-Structured SQL Correctness with Large Language Models*, arXiv:2608.15145 | C | Retain arXiv; no formal publication verified |
| 11 | Zheng, Gou & Zhang, *ZAS-SQL: Distilling Rules from Failures for Zero-Shot Text-to-SQL*, arXiv:2606.08245 | C | Retain arXiv; no formal publication verified |
| 12 | Liu et al., *TIDE-Bench: Evaluating LLMs on Conversational Text-to-SQL under Chain Ambiguity and Intent Drift*, arXiv:2608.29543 | C | Retain arXiv; no formal publication verified |
| 13 | Singh et al., *Beyond Text-to-SQL: An Agentic LLM System for Governed Enterprise Analytics APIs*, arXiv:2605.21027 | B/C | Workshop acceptance was located, but no stronger formal proceedings record was verified; retain arXiv for now |
| 14 | Fei et al., *Benchmarking Text-to-SQL under Role-Based Access Control*, arXiv:2607.22115 | C | Retain arXiv; no formal publication verified |
| 15 | Gwimm & Eisenach, *Beyond the Harness: End-to-End Optimization of Context Artifacts for Enterprise Text-to-SQL*, arXiv:2608.22830 | B/C | COLM 2026 Workshop venue information located; no stronger formal bibliographic version verified; retain arXiv |
| 16 | Su et al., *Disentangling Structure and Semantics: How Schema Representation Affects LLM-Based SQL Generation*, arXiv:2608.20356 | C | Retain arXiv; no formal publication verified |
| 17 | Lin, Luo & Tang, *Structure then Query: Enabling Precise Analytical Queries over Unstructured Documents*, arXiv:2608.13384 | C | Retain arXiv; no formal publication verified |
| 18 | *DBLifeBench: Database Lifecycle Benchmark*, arXiv:2608.03794 | C | Retain arXiv; no formal publication verified |
| 19 | Wu et al., *SQuaD-SQL: Efficient Text-to-SQL with Small Language Models via LLM-Guided Knowledge Distillation*, arXiv:2607.08161 | C | Retain arXiv; no formal publication verified |
| 20 | Chen, Song & Li, *TAHOE: Text-to-SQL with Automated Hint Optimization from Experience*, arXiv:2606.12387 | C | Retain arXiv; no formal publication verified |
| 21 | Tummalapenta & Addanki, *Memory Architectures for Multi-Turn Text-to-SQL: A Benchmark and Empirical Study* / EnterpriseMem-Bench, arXiv:2605.26394 | C | Retain arXiv; no formal publication verified |
| 22 | Ma et al., *Can AI Agents Answer Your Data Questions? A Benchmark for Data Agents* / DAB, arXiv:2603.20576 | C | Retain arXiv; no formal publication verified |
| 23 | *BUDDY: Budget-driven dynamic computation depth*, arXiv:2606.09514 | C | Retain arXiv; no formal publication verified |
| 24 | Li et al., *Knowing When Not to Reuse: Conditional Experience Transfer in Autonomous LLM Post-Training*, arXiv:2608.26730 | C | Retain arXiv; no formal publication verified |
| 25 | Nisa et al., *Agentic AI: The age of reasoning—A review*, J. Automation and Intelligence 5(1), 69–89, DOI 10.1016/j.jai.2025.08.003 | A | Use published JAI version |
| 26 | Song & Zhang, *From black box to physically interpretable: Trustworthy computing for AI-driven decision-making and control*, J. Automation and Intelligence 5(2), 91–111, DOI 10.1016/j.jai.2025.09.003 | A | Use published JAI version |
| 27 | Li et al., *G²SQL: guided & guarded Text-to-SQL generation with two-stage verification*, Expert Systems with Applications 311, 131276, DOI 10.1016/j.eswa.2026.131276 | A | Use published ScienceDirect/Elsevier version |
| 28 | Birhane et al., *AI auditing: The Broken Bus on the Road to AI Accountability* | A | **Replace arXiv with IEEE SaTML 2024 version, pp. 612–643, DOI 10.1109/SaTML59370.2024.00037** |

## 4. Web/industry references

The six Gartner sources are industry-context references rather than academic novelty evidence. They remain optional and should be retained only where they materially support the Defensibility/AI-reliability framing. If retained, they must be formatted as web references with the full URL and access date, as required by JAI.

Verified publisher URLs:

- Gartner, *From Demo to Production: Closing the AI Agent Reliability Gap*: https://www.gartner.com/en/documents/7832217
- Gartner, *Analyst Take: Designate a Defensible AI Architect Now*: https://www.gartner.com/en/documents/7887777
- Gartner, *Market Guide for AI Evaluation and Observability Platforms*: https://www.gartner.com/en/documents/7387730
- Gartner, *Engineering Trust: The New Hard Skill Essential for Leading AI*: https://www.gartner.com/en/documents/8102697
- Gartner, *Use This Framework to Evaluate AI Agents*: https://www.gartner.com/en/documents/8061133
- Gartner, *Observability Is a Must for Custom AI Agents and Multiagent Systems*: official Gartner page to be retained only after final URL verification in the submission bibliography.

**Access date for this audit:** 14 September 2026.

## 5. What this means for the original 53-paper research corpus

The repository's literature-gap audit records 53 supplied paper links and 54 unique arXiv identifiers after duplicate removal. The current manuscript did **not** use all of those items as final references; it narrowed them to the sources directly supporting the paper's final argument.

This is intentional. We do not delete the original corpus. The corpus remains the novelty-threat/provenance record. The final JAI bibliography is a curated evidentiary subset.

The current audit has independently verified the publication status of the 28 references actually used in the manuscript and identified two material arXiv-to-published replacements (Agentic-SQL Revisited and AI auditing) in addition to the published versions already used for Maleki et al., Chen et al., Nisa et al., Song & Zhang, and G²SQL.

## 6. Important limitation

I have **not** converted every one of the original 53/54 corpus items into a final bibliography entry because the repository's historical corpus contains items that were screened for novelty but are not all cited in the final manuscript. Doing so would inflate the final bibliography without evidentiary need. The original corpus should therefore remain in the research audit, while only cited sources appear in the JAI manuscript.

Before submission, this audit should be rerun once more against Crossref/Scopus/publisher metadata for any source still classified C, because 2026 publication status can change after this audit date.
