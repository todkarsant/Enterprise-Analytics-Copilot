from app.db import init_database
from app.agent import run_agent

init_database()
for q in ["Which stores have the highest sales?","Show sales by region","What is the average promo spend by region?"]:
    print("\nQUESTION:",q)
    print(run_agent(q))
