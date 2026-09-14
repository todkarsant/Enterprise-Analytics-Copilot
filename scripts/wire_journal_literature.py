from pathlib import Path

PATH = Path("paper/PROJECT1_JAI_FINAL_MANUSCRIPT.md")
text = PATH.read_text(encoding="utf-8")

required_markers = [
    "[35]",
    "[36]",
    "[37]",
    "[38]",
    "[39]",
    "[40]",
]
if all(marker in text for marker in required_markers):
    raise SystemExit("Target-journal literature already appears to be wired; refusing to modify.")

replacements = [
    (
        "G²SQL is an especially important comparator because it uses a guided and guarded two-stage verification architecture with a Reviewer–Observer mechanism [27]. The verification gate tested here is deliberately much simpler: SQL validity, successful execution, and selected structural checks. Consequently, a negative result for this gate should **not** be interpreted as evidence that stronger verification is ineffective.",
        "G²SQL is an especially important comparator because it uses a guided and guarded two-stage verification architecture with a Reviewer–Observer mechanism [27]. The verification gate tested here is deliberately much simpler: SQL validity, successful execution, and selected structural checks. Consequently, a negative result for this gate should **not** be interpreted as evidence that stronger verification is ineffective. GradeSQL further illustrates a stronger test-time verification direction by using outcome reward models to rank candidate SQL queries on semantic correctness and schema alignment, reporting gains over execution-based heuristics on Spider and BIRD [35].",
    ),
    (
        "Accordingly, the present work does not claim novelty for adaptive routing, post-evidence escalation, cost-aware computation, agentic SQL, or execution-guided correction. These mechanisms form part of the prior-art boundary against which the experiment is interpreted.",
        "Accordingly, the present work does not claim novelty for adaptive routing, post-evidence escalation, cost-aware computation, agentic SQL, or execution-guided correction. These mechanisms form part of the prior-art boundary against which the experiment is interpreted. Recent Journal of Intelligent Information Systems work also shows that structured multi-agent deliberation can improve performance on some high-complexity tasks while a single agent can remain stronger when retrieval alone is sufficient, reinforcing that additional reasoning should be evaluated conditionally rather than assumed to be beneficial [36].",
    ),
    (
        "Other recent work shows that the context supplied to a Text-to-SQL system, and the way schema structure and semantics are represented, can materially affect performance [15–19]. These studies reinforce the need to distinguish the controlled benchmark question from claims about enterprise deployment.",
        "Other recent work shows that the context supplied to a Text-to-SQL system, and the way schema structure and semantics are represented, can materially affect performance [15–19]. Applied Intelligence research likewise reports that knowledge-graph-extended retrieval can improve robustness and explainability in LLM-based question answering, while weighted verification and ranking can filter generated knowledge prompts before they are supplied to an LLM [37,38]. These studies reinforce the need to distinguish the controlled benchmark question from claims about enterprise deployment.",
    ),
    (
        "Recent Journal of Automation and Intelligence work emphasizes the growing importance of agentic reasoning and trustworthy decision-making, including reliability, robustness, verifiability, safety, and explicit constraints [25,26]. These papers support the broader research framing but do not establish the specific contribution tested here. Similarly, current industry research from Gartner emphasizes reliability, evaluation, observability, defensibility, challenge, transparency, and accountability for AI agents [29–34]. These sources are used as industry-context evidence rather than as evidence of academic novelty.",
        "Recent Journal of Automation and Intelligence work emphasizes the growing importance of agentic reasoning and trustworthy decision-making, including reliability, robustness, verifiability, safety, and explicit constraints [25,26]. These papers support the broader research framing but do not establish the specific contribution tested here. IEEE Transactions on Artificial Intelligence research also highlights that benchmark integrity, evaluator diversity, implementation consistency, and measurement methodology can materially affect conclusions about LLM capability [39]. In a different verification-oriented setting, TrumorGPT uses graph-based retrieval and semantic reasoning for fact-checking, illustrating how external evidence can be incorporated to address hallucination and improve factual verification [40]. Similarly, current industry research from Gartner emphasizes reliability, evaluation, observability, defensibility, challenge, transparency, and accountability for AI agents [29–34]. These sources are used as industry-context evidence rather than as evidence of academic novelty.",
    ),
    (
        "[34] Gartner, “Observability Is a Must for Custom AI Agents and Multiagent Systems,” August 17, 2026. https://www.gartner.com/en/documents/8271421. Accessed September 14, 2026.\n\n## Submission-control note",
        "[34] Gartner, “Observability Is a Must for Custom AI Agents and Multiagent Systems,” August 17, 2026. https://www.gartner.com/en/documents/8271421. Accessed September 14, 2026.\n\n[35] M. Tritto, G. Farano, D. Di Palma, G. Rossiello, D. Subramanian, F. Narducci, and T. Di Noia, “GradeSQL: Outcome reward models for intelligent Text-to-SQL generation from LLMs,” Journal of Intelligent Information Systems, 2026, https://doi.org/10.1007/s10844-026-01071-6.\n\n[36] S. Gómez Álvarez, A. Mozo Quesada, T. Navarro, S. Gálvez Rojas, and F. López Valverde, “Multi-Agent debate system based on large language models: structured deliberation and validation in satellite communications,” Journal of Intelligent Information Systems, 2026, https://doi.org/10.1007/s10844-026-01086-z.\n\n[37] B. Gülmez, “Code generation with large language models: a survey from neural program synthesis to autonomous software development,” Applied Intelligence, vol. 56, Art. 200, 2026, https://doi.org/10.1007/s10489-026-07230-0.\n\n[38] X. Li, S. Peng, S. Yada, S. Wakamiya, and E. Aramaki, “GenKP: generative knowledge prompts for enhancing large language models,” Applied Intelligence, vol. 55, Art. 464, 2025, https://doi.org/10.1007/s10489-025-06318-3.\n\n[39] T. R. McIntosh, T. Susnjak, N. Arachchilage, T. Liu, D. Xu, P. Watters, and M. N. Halgamuge, “Inadequacies of Large Language Model Benchmarks in the Era of Generative Artificial Intelligence,” IEEE Transactions on Artificial Intelligence, vol. 7, no. 1, pp. 22–39, 2026, https://doi.org/10.1109/TAI.2025.3569516.\n\n[40] C. N. Hang, P.-D. Yu, and C. W. Tan, “TrumorGPT: Graph-Based Retrieval-Augmented Large Language Model for Fact-Checking,” IEEE Transactions on Artificial Intelligence, vol. 6, no. 11, pp. 3148–3162, 2025, https://doi.org/10.1109/TAI.2025.3567369.\n\n## Submission-control note",
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one occurrence for replacement, found {count}: {old[:120]}")
    text = text.replace(old, new)

PATH.write_text(text, encoding="utf-8")
print("Wired six verified papers: 2 Applied Intelligence, 2 Journal of Intelligent Information Systems, 2 IEEE Transactions on Artificial Intelligence.")
