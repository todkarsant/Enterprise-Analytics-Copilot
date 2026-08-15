from fastapi import FastAPI
from app.api import router
from app.db import init_database

app=FastAPI(title="Enterprise Analytics Copilot",version="0.2.0",description="Production-oriented NL2SQL and analytics assistant.")
app.include_router(router,prefix="/api")

@app.on_event("startup")
def startup():
    init_database()

@app.get("/")
def root():
    return {"service":"enterprise-analytics-copilot","version":"0.2.0","docs":"/docs"}
