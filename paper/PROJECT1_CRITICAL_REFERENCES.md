# Project 1 — Critical References for Paper Draft

This is the current **verified critical-reference set**, not a claim that all 54 reviewed papers have been fully text-verified. The broader literature audit contains 54 unique arXiv IDs after duplicate removal; full-paper verification status remains heterogeneous and must be completed before claiming exhaustive 54-paper synthesis in the manuscript.

## Correctness prediction / verification

1. Richardson, R. (2026). **What Predicts Correctness in Text-to-SQL? A Selective-Prediction Study.** arXiv:2607.06799.  
   Key relevance: evaluates black-box, structural, execution, schema-relevance, and verification signals for correctness prediction on BIRD and Spider; reports that simple executability/structural signals are materially weaker than reasoning-based verification, with cross-schema verifier generalization remaining difficult.

2. Shukla, N. K., Panda, D., Bhaduri, S., Banerjee, A., & Krishnamurthy, V. (2026). **TraceSQL: Traceable Answerability Estimation for Reference-Free Text-to-SQL Verification.** arXiv:2608.17795.  
   Key relevance: reference-free Text-to-SQL verification using explicit diagnostic features and traceable evidence. This is a direct novelty threat to any claim that traceable verification itself is novel.

3. Maleki, S. E., Pourreza, M., & Rafiei, D. (2026). **Confidence Estimation for Text-to-SQL in Large Language Models.** Proceedings of AAAI 2026, 40(38), 32474–32482. DOI: 10.1609/aaai.v40i38.40523.  
   Key relevance: confidence estimation across domains and execution-based grounding as a useful signal.

## Cascades / adaptive computation

4. Hussain, Z., & Nielbo, K. (2026). **The Coverage Illusion: From Pre-retrieval Routing Failure to Post-retrieval Cascades in a Production RAG System.** arXiv:2605.27220.  
   Key relevance: shows that the need for expensive computation can become visible only after retrieval/evidence is observed, motivating post-retrieval cascades. This strongly constrains any generic novelty claim about evidence-triggered escalation.

5. Liskowski, P., Zhao, F., Han, B., Datta, A., & Tsirogiannis, D. (2026). **Compositional Online Learning for Semantic Data Processing Systems.** arXiv:2608.27244.  
   Key relevance: online execution-time decisions, filter ordering, and semantic SQL cascade routing. This is a major novelty threat to generic cost-aware adaptive analytical execution.

## Reliability / abstention

6. Chen, K., Chen, Y., Koudas, N., & Yu, X. (2025). **Reliable Text-to-SQL with Adaptive Abstention.** Proceedings of the ACM on Management of Data, 3(1), Article 69. DOI: 10.1145/3709719.  
   Key relevance: abstention and human-in-the-loop reliability controls for Text-to-SQL.

## Enterprise analytical governance

7. Pillai, A. S. (2026). **GROUND: Reducing Hallucinations in LLM-Based Enterprise Analytics Through Governed Semantic Definitions.** arXiv:2608.26157.  
   Key relevance: governed enterprise semantics, SQL validation, security/cost rules, retry/abstain behavior. This constrains enterprise-governance novelty claims.

8. Sullutrone, G., Sala, L., Aftar, S., Koutrika, G., & Bergamaschi, S. (2026). **ABISS: Evaluating Text-to-SQL Systems Through Agent Interaction.** arXiv:2607.23340.  
   Key relevance: ambiguity/unanswerability, interactive agent evaluation, and the difficulty of resolving problematic questions even after useful user feedback.

## Positioning rule

The manuscript must position Project 1 as a **boundary/failure-mode study at the intersection of**:

- intermediate evidence;
- intervention versus replacement;
- incumbent-aware paired evaluation;
- reliability/cost trade-offs;
- cross-schema behavior;
- decision provenance and defensibility.

It must not claim novelty for adaptive routing, cascades, confidence estimation, SQL verification, abstention, or enterprise governance individually.
