from typing import TypedDict, Literal
from time import perf_counter
from langgraph.graph import StateGraph, START, END

from app.config import get_settings
from app.db import execute_readonly
from app.services.schema_catalog import retrieve_schema
from app.services.providers import get_provider
from app.services.sql_guard import validate_sql
from app.services.cache import TTLCache

class AgentState(TypedDict, total=False):
    question: str; schema: str; sql: str; normalized_sql: str
    validation_valid: bool; validation_reason: str
    columns: list[str]; rows: list[list]; answer: str; error: str
    repair_attempts: int; started_at: float; latency_ms: float
    trace: list[dict]; input_tokens: int; output_tokens: int; model: str
    schema_items: list[dict]; cache_hit: bool

settings = get_settings()
QUERY_CACHE = TTLCache(settings.cache_ttl_seconds)


def trace(state, node, started, **details):
    state.setdefault("trace", []).append({"node": node, "latency_ms": round((perf_counter()-started)*1000,2), **details})

def schema_context(state: AgentState):
    t=perf_counter(); retrieved=retrieve_schema(state["question"], get_settings().schema_top_k)
    trace(state,"schema_retrieval",t,items=retrieved["items"])
    return {"schema": retrieved["context"], "schema_items": retrieved["items"]}

def generate_sql(state: AgentState):
    t=perf_counter(); provider=get_provider()
    try:
        result=provider.generate_sql(state["question"], state["schema"], state.get("validation_reason"))
        trace(state,"sql_generation",t,model=result.model,input_tokens=result.input_tokens,output_tokens=result.output_tokens)
        return {"sql":result.text,"error":"","input_tokens":state.get("input_tokens",0)+result.input_tokens,"output_tokens":state.get("output_tokens",0)+result.output_tokens,"model":result.model}
    except Exception as exc:
        trace(state,"sql_generation",t,error=str(exc)); return {"sql":"","error":str(exc)}

def validate_node(state: AgentState):
    t=perf_counter(); valid,reason,normalized=validate_sql(state.get("sql",""),get_settings().max_sql_length)
    trace(state,"sql_validation",t,valid=valid,reason=reason)
    return {"validation_valid":valid,"validation_reason":reason,"normalized_sql":normalized or ""}

def route_after_validation(state: AgentState) -> Literal["execute","repair",END]:
    if state.get("validation_valid"): return "execute"
    if state.get("repair_attempts",0) < get_settings().max_repair_attempts and not state.get("error"): return "repair"
    return END

def repair_sql(state: AgentState):
    return {"repair_attempts":state.get("repair_attempts",0)+1}

def execute_node(state: AgentState):
    t=perf_counter()
    try:
        cached=QUERY_CACHE.get(state["normalized_sql"])
        if cached is not None:
            columns,rows=cached; trace(state,"sql_execution",t,cache_hit=True,rows=len(rows)); return {"columns":columns,"rows":rows,"cache_hit":True}
        columns,rows=execute_readonly(state["normalized_sql"],get_settings().max_result_rows)
        QUERY_CACHE.set(state["normalized_sql"],(columns,rows)); trace(state,"sql_execution",t,cache_hit=False,rows=len(rows)); return {"columns":columns,"rows":rows,"cache_hit":False}
    except Exception as exc:
        trace(state,"sql_execution",t,error=str(exc)); return {"error":f"SQL execution failed: {exc}"}

def answer_node(state: AgentState):
    t=perf_counter(); provider=get_provider()
    if state.get("error"): return {"answer":state["error"],"latency_ms":round((perf_counter()-state["started_at"])*1000,2)}
    try:
        result=provider.summarize(state["question"],state["columns"],state["rows"])
        trace(state,"answer_generation",t,model=result.model,input_tokens=result.input_tokens,output_tokens=result.output_tokens)
        return {"answer":result.text,"latency_ms":round((perf_counter()-state["started_at"])*1000,2),"input_tokens":state.get("input_tokens",0)+result.input_tokens,"output_tokens":state.get("output_tokens",0)+result.output_tokens,"model":result.model}
    except Exception as exc:
        trace(state,"answer_generation",t,error=str(exc)); return {"answer":f"Unable to summarize result: {exc}","latency_ms":round((perf_counter()-state["started_at"])*1000,2)}

def build_graph():
    b=StateGraph(AgentState)
    b.add_node("schema_context",schema_context); b.add_node("generate_sql",generate_sql); b.add_node("validate_sql",validate_node); b.add_node("repair_sql",repair_sql); b.add_node("execute",execute_node); b.add_node("answer",answer_node)
    b.add_edge(START,"schema_context"); b.add_edge("schema_context","generate_sql"); b.add_edge("generate_sql","validate_sql")
    b.add_conditional_edges("validate_sql",route_after_validation,{"execute":"execute","repair":"repair_sql",END:END}); b.add_edge("repair_sql","generate_sql"); b.add_edge("execute","answer"); b.add_edge("answer",END)
    return b.compile()

GRAPH=build_graph()

def run_agent(question:str)->dict:
    started=perf_counter(); result=GRAPH.invoke({"question":question,"repair_attempts":0,"started_at":started,"trace":[]})
    input_tokens=result.get("input_tokens",0); output_tokens=result.get("output_tokens",0)
    cost=(input_tokens/1000)*get_settings().cost_per_1k_input_tokens_usd+(output_tokens/1000)*get_settings().cost_per_1k_output_tokens_usd
    return {"question":question,"sql":result.get("normalized_sql") or result.get("sql", ""),"columns":result.get("columns",[]),"rows":result.get("rows",[]),"answer":result.get("answer",result.get("error","No answer generated.")),"validation":{"valid":result.get("validation_valid",False),"reason":result.get("validation_reason",result.get("error","Unknown error")),"normalized_sql":result.get("normalized_sql")},"metrics":{"latency_ms":result.get("latency_ms",round((perf_counter()-started)*1000,2)),"rows_returned":len(result.get("rows",[])),"llm_provider":get_settings().llm_provider,"model":result.get("model","unknown"),"input_tokens":input_tokens,"output_tokens":output_tokens,"estimated_cost_usd":round(cost,8),"cache_hit":result.get("cache_hit",False),"repair_attempts":result.get("repair_attempts",0)},"trace":result.get("trace",[]),"schema_items":result.get("schema_items",[])}
