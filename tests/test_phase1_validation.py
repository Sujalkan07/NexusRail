from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.main import app
from app.models.smms_failure import SmmsFailure
from app.models.tdms_equipment import TdmsEquipment
from app.models.tms_defect import TmsDefect
from app.models.train_schedule import TrainSchedule

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "NexusRail"


def test_sqlalchemy_database_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar_one() == 1


def test_all_four_tables_exist():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    for table in [
        "tms_defects",
        "smms_failures",
        "tdms_equipment",
        "train_schedule",
    ]:
        assert table in tables


def test_crud_roundtrip_tms_defects():
    db = SessionLocal()
    try:
        defect = TmsDefect(
            source_system="TMS",
            section_code="SEC-12",
            route_code="R-71",
            track_id="TK-9",
            defect_type="track_crack",
            severity="high",
            status="open",
            is_critical=True,
            reported_at=datetime.utcnow(),
            detected_at=datetime.utcnow(),
            last_updated_at=datetime.utcnow(),
        )
        db.add(defect)
        db.commit()
        db.refresh(defect)
        assert defect.id is not None
        assert db.query(TmsDefect).filter(TmsDefect.section_code == "SEC-12").count() >= 1
    finally:
        db.close()


def test_crud_roundtrip_smms_failures():
    db = SessionLocal()
    try:
        failure = SmmsFailure(
            source_system="SMMS",
            section_code="SEC-12",
            route_code="R-71",
            signal_id="SIG-44",
            failure_type="signal_fault",
            severity="critical",
            status="active",
            requires_power_isolation=True,
            overdue_hours=6.5,
            failure_started_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
        )
        db.add(failure)
        db.commit()
        db.refresh(failure)
        assert failure.id is not None
        assert db.query(SmmsFailure).filter(SmmsFailure.signal_id == "SIG-44").count() >= 1
    finally:
        db.close()


def test_crud_roundtrip_tdms_equipment():
    db = SessionLocal()
    try:
        equipment = TdmsEquipment(
            source_system="TDMS",
            section_code="SEC-12",
            route_code="R-71",
            equipment_id="OHE-88",
            equipment_type="overhead_equipment",
            health_status="degraded",
            power_block_required=True,
            criticality_score=8.5,
            isolation_window_start=datetime.utcnow(),
            isolation_window_end=datetime.utcnow(),
        )
        db.add(equipment)
        db.commit()
        db.refresh(equipment)
        assert equipment.id is not None
        assert db.query(TdmsEquipment).filter(TdmsEquipment.equipment_id == "OHE-88").count() >= 1
    finally:
        db.close()


def test_crud_roundtrip_train_schedule():
    db = SessionLocal()
    try:
        schedule = TrainSchedule(
            source_system="COA",
            section_code="SEC-12",
            route_code="R-71",
            train_no="12615",
            service_type="passenger",
            scheduled_date=datetime.utcnow(),
            origin_station="A",
            destination_station="B",
            direction="up",
            arrival_time=datetime.utcnow(),
            departure_time=datetime.utcnow(),
            is_goods=False,
            status="on_time",
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        assert schedule.id is not None
        assert db.query(TrainSchedule).filter(TrainSchedule.train_no == "12615").count() >= 1
    finally:
        db.close()


def test_api_crud_endpoints_for_each_table():
    payloads = [
        ("/api/v1/tms-defects", {
            "source_system": "TMS",
            "section_code": "SEC-99",
            "route_code": "R-90",
            "track_id": "TK-1",
            "defect_type": "ballast",
            "severity": "medium",
            "status": "open",
            "is_critical": False,
        }),
        ("/api/v1/smms-failures", {
            "source_system": "SMMS",
            "section_code": "SEC-99",
            "route_code": "R-90",
            "signal_id": "SIG-99",
            "failure_type": "signal_fault",
            "severity": "high",
            "status": "active",
            "requires_power_isolation": True,
        }),
        ("/api/v1/tdms-equipment", {
            "source_system": "TDMS",
            "section_code": "SEC-99",
            "route_code": "R-90",
            "equipment_id": "OHE-99",
            "equipment_type": "overhead_equipment",
            "health_status": "degraded",
            "power_block_required": True,
        }),
        ("/api/v1/train-schedule", {
            "source_system": "COA",
            "section_code": "SEC-99",
            "route_code": "R-90",
            "train_no": "12901",
            "service_type": "goods",
            "scheduled_date": datetime.utcnow().date().isoformat(),
            "origin_station": "X",
            "destination_station": "Y",
            "direction": "down",
            "is_goods": True,
            "status": "on_time",
        }),
    ]

    for endpoint, payload in payloads:
        response = client.post(endpoint, json=payload)
        assert response.status_code == 201, f"POST failed for {endpoint}: {response.text}"
        body = response.json()
        assert body["source_system"] == payload["source_system"]

        list_response = client.get(endpoint)
        assert list_response.status_code == 200
        assert isinstance(list_response.json(), list)
