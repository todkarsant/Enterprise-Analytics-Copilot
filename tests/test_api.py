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
    assert body["metrics"]["input_tokens"] == 0
    assert body["metrics"]["output_tokens"] == 0
    assert body["rows"]


def test_query_rejects_too_short_question():
    response = client.post("/api/query", json={"question": "Hi"})
    assert response.status_code == 422
