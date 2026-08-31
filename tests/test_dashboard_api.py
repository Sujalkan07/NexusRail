from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dashboard_overview_returns_unified_snapshot():
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    payload = response.json()
    assert "system_status" in payload
    assert "overview" in payload
    assert "records" in payload
    assert "recommendations" in payload
    assert "approval" in payload


def test_dashboard_recommendations_returns_solver_data():
    response = client.get("/api/v1/dashboard/recommendations")
    assert response.status_code == 200
    payload = response.json()
    assert "feasible" in payload
    assert "blocks" in payload
    assert "selected_tasks" in payload
    assert "rejected_tasks" in payload
    assert "explanation" in payload
