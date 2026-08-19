from fastapi import APIRouter, HTTPException

from app.schema import QueryRequest, QueryResponse, HealthResponse
from app.agent import run_agent
from app.config import get_settings
from app.db import init_database

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return {
        "status": "ok",
        "llm_provider": get_settings().llm_provider,
        "db_backend": get_settings().db_backend,
    }


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    init_database()
    result = run_agent(request.question)
    if not result["validation"]["valid"]:
        raise HTTPException(status_code=422, detail=result)
    if not request.include_sql:
        result["sql"] = ""
        if result.get("analysis"):
            for step in result["analysis"].get("steps", []):
                step["sql"] = ""
    return result
