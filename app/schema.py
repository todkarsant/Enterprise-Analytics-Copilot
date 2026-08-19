from typing import Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    session_id: str | None = None
    include_sql: bool = True


class QueryResponse(BaseModel):
    question: str
    sql: str
    columns: list[str]
    rows: list[list[Any]]
    answer: str
    validation: dict[str, Any]
    metrics: dict[str, Any]
    trace: list[dict[str, Any]] = Field(default_factory=list)
    schema_items: list[dict[str, Any]] = Field(default_factory=list)
    analysis: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    db_backend: str
