from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_tms_defects_list_returns_json():
    response = client.get("/api/v1/tms-defects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_smms_failures_list_returns_json():
    response = client.get("/api/v1/smms-failures")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_tdms_equipment_list_returns_json():
    response = client.get("/api/v1/tdms-equipment")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_train_schedule_list_returns_json():
    response = client.get("/api/v1/train-schedule")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
