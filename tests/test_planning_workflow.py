from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_planning_workflow_seeds_domain_and_approves_recommendation():
    dashboard = client.get("/api/v1/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["summary"]["active_requests"] >= 4
    assert dashboard.json()["sections"][0]["route_name"]

    requests = client.get("/api/v1/maintenance-requests").json()
    assert requests[0]["priority_factors"]
    assert requests[0]["asset_name"]
    assert requests[0]["section_name"]

    start = datetime.now(timezone.utc) - timedelta(hours=1)
    result = client.post("/api/v1/optimization/run", json={
        "available_hours": 24,
        "available_crew": 10,
        "planning_start": start.isoformat(),
        "planning_end": (start + timedelta(days=1)).isoformat(),
    })
    assert result.status_code == 200
    recommendation = result.json()["recommendations"][0]
    assert recommendation["request_codes"]
    assert "grouped" in recommendation["explanation"]

    approval = client.post(f"/api/v1/recommendations/{recommendation['id']}/approve", json={"reviewed_by": "Test Planner"})
    assert approval.status_code == 200
    assert any(item["status"] == "approved" for item in approval.json()["recommendations"])
