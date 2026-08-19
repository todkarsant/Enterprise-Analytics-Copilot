from app.db import init_database
from app.agent import run_agent


QUESTIONS = [
    "Which stores have the highest sales?",
    "Show sales by region",
    "What is the average promo spend by region?",
    "Why did sales decline?",
]


def main():
    init_database()
    for question in QUESTIONS:
        print("\n" + "=" * 80)
        print("QUESTION:", question)
        result = run_agent(question)
        print("ANSWER:")
        print(result["answer"])
        print("METRICS:", result["metrics"])
        if result.get("sql"):
            print("SQL:")
            print(result["sql"])
        if result.get("analysis"):
            print("ANALYSIS INTENT:", result["analysis"]["intent"])
            for step in result["analysis"]["steps"]:
                print(f"STEP {step['name']}: {step['purpose']}")


if __name__ == "__main__":
    main()
