from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_query_mock():
    response = client.post(
        "/api/query",
        json={"question": "Which stores have the highest sales?"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["validation"]["valid"] is True
    assert body["metrics"]["llm_provider"] == "mock"
    assert body["metrics"]["planner_used"] is True
    assert body["metrics"]["repair_attempts"] == 0
    assert body["rows"]
    assert body["analysis"] is None


def test_sales_decline_analysis_is_end_to_end():
    response = client.post(
        "/api/query",
        json={"question": "Why did sales decline?"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["metrics"]["analysis_used"] is True
    assert body["metrics"]["intent"] == "sales_decline_analysis"
    assert body["metrics"]["repair_attempts"] == 0
    assert body["analysis"]["steps"]
    assert "does not support a sales decline" in body["answer"]
    assert "6.62%" in body["answer"]


def test_query_rejects_too_short_question():
    response = client.post("/api/query", json={"question": "Hi"})
    assert response.status_code == 422
