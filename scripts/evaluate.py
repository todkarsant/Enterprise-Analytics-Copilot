import json
from pathlib import Path
from app.db import init_database
from app.agent import run_agent

CASES=[
 {"question":"Which stores have the highest sales?","expected_columns":["store_id","total_sales"]},
 {"question":"Show sales by region","expected_columns":["region","total_sales"]},
 {"question":"What is the average promo spend by region?","expected_columns":["region","avg_promo_spend"]},
]

def main():
    init_database(); results=[]
    for case in CASES:
        r=run_agent(case["question"])
        schema_ok=set(case["expected_columns"]).issubset(set(r["columns"]))
        results.append({"question":case["question"],"validation_pass":r["validation"]["valid"],"schema_contract_pass":schema_ok,"rows":len(r["rows"]),"latency_ms":r["metrics"]["latency_ms"],"cache_hit":r["metrics"]["cache_hit"]})
    out=Path('artifacts'); out.mkdir(exist_ok=True); (out/'evaluation.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))

if __name__=='__main__': main()
