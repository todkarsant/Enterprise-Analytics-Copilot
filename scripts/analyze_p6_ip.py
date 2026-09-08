from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path


def load_jsons(root: Path):
    rows = []
    for p in root.rglob("*.json"):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("traces"), list):
            rows.extend(obj["traces"])
    return rows


def wilson(x, n, z=1.959963984540054):
    if n == 0: return [None, None]
    p=x/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [c-h,c+h]


def exact_mcnemar(a_only, b_only):
    n=a_only+b_only
    if n == 0: return 1.0
    k=min(a_only,b_only); tail=sum(math.comb(n,i) for i in range(k+1))/(2**n)
    return min(1.0,2*tail)


def paired(p6, p0):
    a_only=b_only=both=neither=0
    for key, x in p6.items():
        if key not in p0: continue
        xc=bool(x.get("official_execution_correct")); yc=bool(p0[key].get("official_execution_correct"))
        if xc and yc: both+=1
        elif xc: a_only+=1
        elif yc: b_only+=1
        else: neither+=1
    n=both+a_only+b_only+neither
    return {"n":n,"p6_correct":both+a_only,"p0_correct":both+b_only,"delta_pp":100*(a_only-b_only)/n if n else None,"p6_only":a_only,"p0_only":b_only,"both_correct":both,"neither":neither,"mcnemar_exact_p":exact_mcnemar(a_only,b_only)}


def intervention(records, p6, p0):
    out={"eligible":0,"p0_correct_eligible":0,"p0_wrong_eligible":0,"harm":0,"rescue":0,"neutral":0}
    for r in records:
        if r.get("decision") != "INTERVENE": continue
        key=(r.get("case_id"))
        # case_id is db_id:question and is reconstructed below from trace keys.
        out["eligible"]+=1
    # Reconstruct by parsing case_id safely from the rightmost colon.
    for r in records:
        if r.get("decision") != "INTERVENE": continue
        cid=r.get("case_id","")
        db,q=cid.split(":",1) if ":" in cid else (None,None)
        key=(q,db)
        if key not in p0 or key not in p6: continue
        pc=bool(p0[key].get("official_execution_correct")); cc=bool(p6[key].get("official_execution_correct"))
        if pc: out["p0_correct_eligible"]+=1
        else: out["p0_wrong_eligible"]+=1
        if pc and not cc: out["harm"]+=1
        elif not pc and cc: out["rescue"]+=1
        else: out["neutral"]+=1
    out["harm_rate_among_p0_correct_eligible"]=out["harm"]/out["p0_correct_eligible"] if out["p0_correct_eligible"] else None
    out["rescue_rate_among_p0_wrong_eligible"]=out["rescue"]/out["p0_wrong_eligible"] if out["p0_wrong_eligible"] else None
    out["net_intervention_gain"]=out["rescue"]-out["harm"]
    return out


def summarize(rows):
    n=len(rows); correct=sum(bool(r.get("official_execution_correct")) for r in rows)
    costs=[float(r.get("cost",0)) for r in rows]; lats=[float(r.get("latency_ms",0)) for r in rows]
    return {"n":n,"correct":correct,"accuracy":correct/n if n else None,"wilson_95":wilson(correct,n),"coverage":sum(bool(r.get("generated_sql")) for r in rows)/n if n else None,"mean_cost":statistics.mean(costs) if costs else None,"median_latency_ms":statistics.median(lats) if lats else None,"p95_latency_ms":sorted(lats)[max(0,min(n-1,math.ceil(.95*n)-1))] if lats else None,"mean_llm_calls":statistics.mean(float(r.get("llm_calls",0)) for r in rows) if rows else None}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--p6",type=Path,required=True); ap.add_argument("--p0-root",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); args=ap.parse_args()
    p6_payload=json.loads(args.p6.read_text(encoding="utf-8")); p6_rows=p6_payload["traces"]; p6={(r["question"],r["db_id"]):r for r in p6_rows}
    frozen=load_jsons(args.p0_root); p0={}
    for r in frozen:
        if r.get("policy")=="P0": p0[(r.get("question"),r.get("db_id"))]=r
    common=set(p6)&set(p0); p6c={k:p6[k] for k in common}; p0c={k:p0[k] for k in common}
    result={"p6":summarize(list(p6c.values())),"p0":summarize(list(p0c.values())),"paired":paired(p6c,p0c),"intervention":intervention(p6_payload.get("defensibility",[]),p6c,p0c),"runtime":p6_payload.get("runtime_controls"),"question_count":len(p6_rows)}
    result["reliability_targets"]={str(x):result["p6"]["accuracy"] is not None and result["p6"]["accuracy"]>=x for x in (.90,.95,.97,.99)}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
