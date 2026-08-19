from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router
from app.db import init_database


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="Enterprise Analytics Copilot",
    version="0.2.7",
    description="Production-oriented NL2SQL and analytical reasoning assistant.",
    lifespan=lifespan,
)
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "service": "enterprise-analytics-copilot",
        "version": "0.2.7",
        "docs": "/docs",
    }
