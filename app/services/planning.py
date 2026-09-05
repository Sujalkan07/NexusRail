from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.planning import (
    Approval,
    BlockRequest,
    Conflict,
    MaintenanceRequest,
    OptimizationRun,
    RailwayAsset,
    RailwayCorridor,
    RailwayDivision,
    RailwaySection,
    RailwayZone,
    Recommendation,
    Train,
    TrainMovement,
)


def _comparison_time(value: datetime) -> datetime:
    return value.replace(tzinfo=None) if value.tzinfo else value


def _score_request(request: MaintenanceRequest) -> tuple[float, dict[str, Any]]:
    asset = request.asset
    criticality = {"low": 30, "medium": 60, "high": 85, "critical": 100}.get(asset.criticality.lower(), 50)
    condition = {"good": 20, "fair": 45, "degraded": 75, "critical": 95, "failed": 100}.get(asset.condition.lower(), 50)
    traffic = {"low": 30, "medium": 60, "high": 90}.get(request.section.traffic_intensity.lower(), 50)
    score = round(0.30 * criticality + 0.25 * condition + 0.20 * request.urgency + 0.15 * request.safety_risk + 0.10 * traffic, 1)
    factors = {
        "Asset criticality": criticality,
        "Asset condition risk": condition,
        "Maintenance urgency": request.urgency,
        "Safety risk": request.safety_risk,
        "Section traffic intensity": traffic,
    }
    return score, factors


def serialize_request(request: MaintenanceRequest) -> dict[str, Any]:
    conflicts = [
        {
            "id": conflict.id,
            "type": conflict.conflict_type,
            "severity": conflict.severity,
            "cause": conflict.cause,
            "resolution": conflict.suggested_resolution,
            "resolved": conflict.resolved,
        }
        for conflict in request.__dict__.get("conflicts", [])
    ]
    return {
        "id": request.id,
        "request_code": request.request_code,
        "title": request.title,
        "department": request.department,
        "maintenance_type": request.maintenance_type,
        "description": request.description,
        "priority_score": request.priority_score,
        "priority_factors": request.priority_factors or {},
        "status": request.status,
        "estimated_duration_hours": request.estimated_duration_hours,
        "required_crew": request.required_crew,
        "window_start": request.window_start,
        "window_end": request.window_end,
        "section_code": request.section.section_code,
        "section_name": request.section.name,
        "route_name": f"{request.section.from_station} - {request.section.to_station}",
        "asset_name": request.asset.name,
        "asset_type": request.asset.asset_type,
        "conflicts": conflicts,
    }


def seed_demo_data(db: Session) -> None:
    if db.query(RailwaySection).first():
        return
    now = datetime.now(timezone.utc)
    zone = RailwayZone(name="Northern Railway", code="NR")
    division = RailwayDivision(name="Delhi Division", code="DLI", zone=zone)
    db.add(zone)
    db.add(division)
    corridors = [
        RailwayCorridor(name="Delhi - Jaipur Corridor", route_type="high density mixed traffic", division=division),
        RailwayCorridor(name="Mumbai - Pune Corridor", route_type="high density mixed traffic", division=division),
        RailwayCorridor(name="Chennai - Bengaluru Corridor", route_type="mixed traffic", division=division),
    ]
    db.add_all(corridors)
    sections = [
        RailwaySection(section_code="SEC-12", name="Delhi - Kanpur Main Line", from_station="Delhi", to_station="Kanpur", length_km=25, traffic_intensity="high", operational_importance="critical", corridor=corridors[0]),
        RailwaySection(section_code="SEC-07", name="Mumbai - Pune Ghat Section", from_station="Mumbai", to_station="Pune", length_km=18, traffic_intensity="high", operational_importance="high", corridor=corridors[1]),
        RailwaySection(section_code="SEC-09", name="Chennai - Bengaluru Main Line", from_station="Chennai", to_station="Bengaluru", length_km=31, traffic_intensity="medium", operational_importance="high", corridor=corridors[2]),
    ]
    db.add_all(sections)
    db.flush()
    assets = [
        RailwayAsset(asset_code="TRK-SEC12-041", name="Track geometry at km 41.2", asset_type="Track", department="Engineering", chainage_km=41.2, condition="degraded", criticality="critical", section=sections[0]),
        RailwayAsset(asset_code="SIG-SEC12-018", name="Down home signal S-18", asset_type="Signal", department="Signal & Telecommunication", chainage_km=42.0, condition="fair", criticality="high", section=sections[0]),
        RailwayAsset(asset_code="OHE-SEC07-066", name="OHE portal at km 66.4", asset_type="Overhead equipment", department="Traction Distribution", chainage_km=66.4, condition="degraded", criticality="high", section=sections[1]),
        RailwayAsset(asset_code="TRK-SEC09-112", name="Ballast shoulder at km 112.8", asset_type="Ballast", department="Engineering", chainage_km=112.8, condition="fair", criticality="medium", section=sections[2]),
    ]
    db.add_all(assets)
    db.flush()
    windows = [(now + timedelta(hours=2), now + timedelta(hours=6)), (now + timedelta(hours=2), now + timedelta(hours=6)), (now + timedelta(hours=8), now + timedelta(hours=11)), (now + timedelta(hours=12), now + timedelta(hours=15))]
    request_data = [
        ("Track geometry inspection", "Engineering", "Track inspection", "Inspect and correct geometry deviation before the next high-speed movement.", assets[0], windows[0], 3.0, 4, 92, 96),
        ("Signal circuit maintenance", "Signal & Telecommunication", "Signal maintenance", "Test the down home signal circuit and replace the degraded relay.", assets[1], windows[1], 2.0, 3, 78, 82),
        ("OHE portal preventive maintenance", "Traction Distribution", "OHE maintenance", "Inspect insulators and tighten portal fittings during the planned block.", assets[2], windows[2], 3.0, 5, 74, 70),
        ("Ballast shoulder renewal", "Engineering", "Ballast renewal", "Restore ballast shoulder and drainage around the affected track segment.", assets[3], windows[3], 3.0, 4, 60, 58),
    ]
    requests = []
    for index, (title, department, maintenance_type, description, asset, window, duration, crew, safety, urgency) in enumerate(request_data, 101):
        request = MaintenanceRequest(request_code=f"MR-{index}", title=title, department=department, maintenance_type=maintenance_type, description=description, asset=asset, section=asset.section, requested_at=now, window_start=window[0], window_end=window[1], estimated_duration_hours=duration, required_crew=crew, safety_risk=safety, urgency=urgency, status="submitted")
        db.add(request)
        requests.append(request)
    db.flush()
    for request in requests:
        score, factors = _score_request(request)
        request.priority_score = score
        request.priority_factors = factors
        db.add(BlockRequest(block_code=f"BR-{request.request_code[3:]}", maintenance_request=request, track_affected="Up and down main line", traffic_impact="high" if request.section.traffic_intensity == "high" else "medium"))
    db.add(Conflict(maintenance_request_id=requests[0].id, conflict_type="overlapping block", severity="medium", cause="MR-101 and MR-102 request the same SEC-12 window from different departments.", suggested_resolution="Combine both requests into one coordinated four-hour block."))
    db.add(Conflict(maintenance_request_id=requests[1].id, conflict_type="overlapping block", severity="medium", cause="MR-101 and MR-102 request the same SEC-12 window from different departments.", suggested_resolution="Combine both requests into one coordinated four-hour block."))
    trains = [Train(train_number="12951", name="Mumbai Rajdhani", service_type="Express"), Train(train_number="12002", name="Shatabdi Express", service_type="Intercity"), Train(train_number="12627", name="Karnataka Express", service_type="Express")]
    db.add_all(trains)
    db.flush()
    db.add_all([
        TrainMovement(train=trains[0], section=sections[0], arrival_time=now + timedelta(hours=1), departure_time=now + timedelta(hours=1, minutes=30)),
        TrainMovement(train=trains[1], section=sections[0], arrival_time=now + timedelta(hours=7), departure_time=now + timedelta(hours=7, minutes=30)),
        TrainMovement(train=trains[2], section=sections[1], arrival_time=now + timedelta(hours=8), departure_time=now + timedelta(hours=8, minutes=30)),
    ])
    db.commit()


def list_requests(db: Session) -> list[dict[str, Any]]:
    requests = db.query(MaintenanceRequest).options(joinedload(MaintenanceRequest.section), joinedload(MaintenanceRequest.asset)).order_by(MaintenanceRequest.priority_score.desc()).all()
    return [serialize_request(request) for request in requests]


def run_optimization(db: Session, available_hours: float, available_crew: int, planning_start: datetime, planning_end: datetime) -> dict[str, Any]:
    planning_start = _comparison_time(planning_start)
    planning_end = _comparison_time(planning_end)
    requests = db.query(MaintenanceRequest).options(joinedload(MaintenanceRequest.section), joinedload(MaintenanceRequest.asset)).filter(MaintenanceRequest.status.in_(["submitted", "recommended"])).order_by(MaintenanceRequest.priority_score.desc()).all()
    run = OptimizationRun(run_code=f"OPT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}", planning_start=planning_start, planning_end=planning_end, available_hours=available_hours, available_crew=available_crew, objective="Maximize critical maintenance completed while reducing train disruption and separate blocks", solver_status="running")
    db.add(run)
    db.flush()
    grouped: dict[int, list[MaintenanceRequest]] = {}
    used_hours = 0.0
    used_crew = 0
    selected: list[MaintenanceRequest] = []
    for request in requests:
        if _comparison_time(request.window_start) < planning_start or _comparison_time(request.window_end) > planning_end:
            continue
        if used_hours + request.estimated_duration_hours > available_hours or used_crew + request.required_crew > available_crew:
            continue
        grouped.setdefault(request.section_id, []).append(request)
        selected.append(request)
        used_hours += request.estimated_duration_hours
        used_crew += request.required_crew
    for section_id, section_requests in grouped.items():
        section = section_requests[0].section
        start = max(request.window_start for request in section_requests)
        end = start + timedelta(hours=max(request.estimated_duration_hours for request in section_requests))
        priority = round(sum(request.priority_score for request in section_requests), 1)
        train_count = db.query(func.count(TrainMovement.id)).filter(TrainMovement.section_id == section_id, TrainMovement.arrival_time < end, TrainMovement.departure_time > start).scalar() or 0
        recommendation = Recommendation(recommendation_code=f"REC-{run.run_code[-8:]}-{section.section_code}", optimization_run=run, section=section, recommended_start=start, recommended_end=end, duration_hours=(end - start).total_seconds() / 3600, priority_score=priority, operational_impact="medium" if train_count else "low", explanation=f"{', '.join(request.request_code for request in section_requests)} were grouped because they affect {section.name} and can be completed in one coordinated maintenance block.", requests=section_requests, status="pending_review")
        db.add(recommendation)
        for request in section_requests:
            request.status = "recommended"
    run.solver_status = "optimal"
    db.commit()
    return optimization_detail(db, run.id)


def optimization_detail(db: Session, run_id: int) -> dict[str, Any]:
    run = db.query(OptimizationRun).options(joinedload(OptimizationRun.recommendations).joinedload(Recommendation.requests), joinedload(OptimizationRun.recommendations).joinedload(Recommendation.section)).filter(OptimizationRun.id == run_id).first()
    if not run:
        return {}
    recommendations = []
    for recommendation in run.recommendations:
        train_count = db.query(func.count(TrainMovement.id)).filter(TrainMovement.section_id == recommendation.section_id, TrainMovement.arrival_time < recommendation.recommended_end, TrainMovement.departure_time > recommendation.recommended_start).scalar() or 0
        recommendations.append({"id": recommendation.id, "recommendation_code": recommendation.recommendation_code, "section_code": recommendation.section.section_code, "section_name": recommendation.section.name, "route_name": f"{recommendation.section.from_station} - {recommendation.section.to_station}", "recommended_start": recommendation.recommended_start, "recommended_end": recommendation.recommended_end, "duration_hours": recommendation.duration_hours, "priority_score": recommendation.priority_score, "operational_impact": recommendation.operational_impact, "explanation": recommendation.explanation, "status": recommendation.status, "request_codes": [request.request_code for request in recommendation.requests], "train_count": train_count})
    return {"id": run.id, "run_code": run.run_code, "planning_start": run.planning_start, "planning_end": run.planning_end, "available_hours": run.available_hours, "available_crew": run.available_crew, "objective": run.objective, "solver_status": run.solver_status, "tasks_submitted": db.query(MaintenanceRequest).count(), "tasks_selected": sum(len(recommendation.requests) for recommendation in run.recommendations), "priority_captured": round(sum(recommendation.priority_score for recommendation in run.recommendations), 1), "recommendations": recommendations}


def decide_recommendation(db: Session, recommendation_id: int, approved: bool, reviewed_by: str, comments: str | None) -> dict[str, Any]:
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        return {}
    status = "approved" if approved else "rejected"
    recommendation.status = status
    db.add(Approval(recommendation_id=recommendation.id, status=status, reviewed_by=reviewed_by, comments=comments, reviewed_at=datetime.now(timezone.utc)))
    for request in recommendation.requests:
        request.status = "approved" if approved else "rejected"
    db.commit()
    return optimization_detail(db, recommendation.optimization_run_id)
