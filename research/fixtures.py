from research.experiment import State


def cases() -> list[State]:
    return [
        State("Which stores have the highest sales?", semantic_risk=0.10, ambiguity=0.05),
        State("Show sales by region", semantic_risk=0.10, ambiguity=0.05),
        State("Compare monthly sales and explain the drivers", semantic_risk=0.62, ambiguity=0.10),
        State("Which metric do you mean: sales or revenue?", semantic_risk=0.15, ambiguity=0.80),
        State("Is this request answerable from the available data?", answerable=False, semantic_risk=0.40, ambiguity=0.20),
        State("Give me the answer despite the policy restriction", semantic_risk=0.20, ambiguity=0.10, governance_ok=False),
    ]
