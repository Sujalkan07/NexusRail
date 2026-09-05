from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.planning import Approval, Conflict, MaintenanceRequest, RailwayAsset, RailwaySection, Recommendation, TrainMovement
from app.schemas.planning import DecisionPayload, MaintenanceRequestCreate, OptimizationPayload
from app.services.planning import decide_recommendation, list_requests, optimization_detail, run_optimization, seed_demo_data, serialize_request

router = APIRouter(tags=["planning"])


def _ensure_seeded(db: Session) -> None:
    seed_demo_data(db)


@router.get("/dashboard")
def get_product_dashboard(db: Session = Depends(get_db)) -> dict[str, Any]:
    _ensure_seeded(db)
    active = db.query(MaintenanceRequest).filter(MaintenanceRequest.status.not_in(["approved", "rejected", "completed"])).count()
    high_priority = db.query(MaintenanceRequest).filter(MaintenanceRequest.priority_score >= 75, MaintenanceRequest.status.not_in(["completed", "rejected"])).count()
    conflicts = db.query(Conflict).filter(Conflict.resolved.is_(False)).count()
    recommendations = db.query(Recommendation).filter(Recommendation.status == "pending_review").count()
    approved = db.query(Recommendation).filter(Recommendation.status == "approved").count()
    trains = db.query(func.count(TrainMovement.id)).scalar() or 0
    requests = list_requests(db)
    sections = []
    for section in db.query(RailwaySection).options(joinedload(RailwaySection.assets)).all():
        sections.append({"id": section.id, "section_code": section.section_code, "name": section.name, "route_name": f"{section.from_station} - {section.to_station}", "from_station": section.from_station, "to_station": section.to_station, "length_km": section.length_km, "traffic_intensity": section.traffic_intensity, "operational_importance": section.operational_importance, "status": section.status, "asset_count": len(section.assets), "active_request_count": sum(1 for request in requests if request["section_code"] == section.section_code and request["status"] not in ["approved", "rejected", "completed"])})
    return {"summary": {"active_requests": active, "high_priority_requests": high_priority, "conflicts": conflicts, "recommended_blocks": recommendations, "approved_plans": approved, "trains_affected": trains, "database_status": "Connected", "optimization_status": "Ready", "approval_status": "Pending Review" if recommendations else "Up to date"}, "requests": requests, "sections": sections, "recent_activity": [{"label": "Maintenance requests loaded", "detail": f"{active} active requests across the network", "timestamp": datetime.now(timezone.utc).isoformat()}, {"label": "Conflict scan completed", "detail": f"{conflicts} unresolved coordination conflicts", "timestamp": datetime.now(timezone.utc).isoformat()}]}


@router.get("/maintenance-requests")
def get_maintenance_requests(department: str | None = None, section_code: str | None = None, min_priority: float | None = Query(default=None, ge=0, le=100), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    _ensure_seeded(db)
    results = list_requests(db)
    if department:
        results = [item for item in results if item["department"] == department]
    if section_code:
        results = [item for item in results if item["section_code"] == section_code]
    if min_priority is not None:
        results = [item for item in results if item["priority_score"] >= min_priority]
    return results


@router.get("/maintenance-requests/{request_id}")
def get_maintenance_request(request_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    _ensure_seeded(db)
    request = db.query(MaintenanceRequest).options(joinedload(MaintenanceRequest.section), joinedload(MaintenanceRequest.asset), joinedload(MaintenanceRequest.conflicts)).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    return serialize_request(request)


@router.post("/maintenance-requests", status_code=status.HTTP_201_CREATED)
def create_maintenance_request(payload: MaintenanceRequestCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    asset = db.query(RailwayAsset).options(joinedload(RailwayAsset.section)).filter(RailwayAsset.id == payload.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    request = MaintenanceRequest(request_code=f"MR-{db.query(MaintenanceRequest).count() + 101}", section_id=asset.section_id, asset_id=asset.id, **payload.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    request = db.query(MaintenanceRequest).options(joinedload(MaintenanceRequest.section), joinedload(MaintenanceRequest.asset)).filter(MaintenanceRequest.id == request.id).first()
    score, factors = __import__("app.services.planning", fromlist=["_score_request"])._score_request(request)
    request.priority_score = score
    request.priority_factors = factors
    db.commit()
    return serialize_request(request)


@router.get("/sections")
def get_sections(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    _ensure_seeded(db)
    return get_product_dashboard(db)["sections"]


@router.get("/assets")
def get_assets(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    _ensure_seeded(db)
    assets = db.query(RailwayAsset).options(joinedload(RailwayAsset.section)).all()
    return [{"id": asset.id, "asset_code": asset.asset_code, "name": asset.name, "asset_type": asset.asset_type, "department": asset.department, "chainage_km": asset.chainage_km, "condition": asset.condition, "criticality": asset.criticality, "section_code": asset.section.section_code, "section_name": asset.section.name} for asset in assets]


@router.get("/conflicts")
def get_conflicts(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    _ensure_seeded(db)
    return [{"id": conflict.id, "request_code": conflict.maintenance_request.request_code, "conflict_type": conflict.conflict_type, "severity": conflict.severity, "cause": conflict.cause, "suggested_resolution": conflict.suggested_resolution, "resolved": conflict.resolved} for conflict in db.query(Conflict).options(joinedload(Conflict.maintenance_request)).all()]


@router.post("/optimization/run")
def post_optimization_run(payload: OptimizationPayload, db: Session = Depends(get_db)) -> dict[str, Any]:
    _ensure_seeded(db)
    return run_optimization(db, payload.available_hours, payload.available_crew, payload.planning_start, payload.planning_end)


@router.get("/optimization/{run_id}")
def get_optimization_run(run_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    result = optimization_detail(db, run_id)
    if not result:
        raise HTTPException(status_code=404, detail="Optimization run not found")
    return result


@router.get("/recommendations")
def get_recommendations(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    _ensure_seeded(db)
    runs = db.query(Recommendation).all()
    return [optimization_detail(db, recommendation.optimization_run_id)["recommendations"][0] for recommendation in runs]


@router.post("/recommendations/{recommendation_id}/approve")
def approve_recommendation(recommendation_id: int, payload: DecisionPayload, db: Session = Depends(get_db)) -> dict[str, Any]:
    result = decide_recommendation(db, recommendation_id, True, payload.reviewed_by, payload.comments)
    if not result:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return result


@router.post("/recommendations/{recommendation_id}/reject")
def reject_recommendation(recommendation_id: int, payload: DecisionPayload, db: Session = Depends(get_db)) -> dict[str, Any]:
    result = decide_recommendation(db, recommendation_id, False, payload.reviewed_by, payload.comments)
    if not result:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return result
