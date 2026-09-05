from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MaintenanceRequestCreate(BaseModel):
    title: str
    department: str
    asset_id: int
    maintenance_type: str
    description: str
    window_start: datetime
    window_end: datetime
    estimated_duration_hours: float = Field(gt=0)
    required_crew: int = Field(gt=0)
    safety_risk: float = Field(ge=0, le=100)
    urgency: float = Field(ge=0, le=100)


class DecisionPayload(BaseModel):
    reviewed_by: str = "Demo Planner"
    comments: str | None = None


class OptimizationPayload(BaseModel):
    available_hours: float = Field(default=24, gt=0)
    available_crew: int = Field(default=10, gt=0)
    planning_start: datetime
    planning_end: datetime


class RequestSummary(ORMModel):
    id: int
    request_code: str
    title: str
    department: str
    maintenance_type: str
    description: str
    priority_score: float
    priority_factors: dict[str, Any]
    status: str
    estimated_duration_hours: float
    required_crew: int
    window_start: datetime
    window_end: datetime
    section_code: str
    section_name: str
    route_name: str
    asset_name: str
    asset_type: str
    conflicts: list[dict[str, Any]] = []


class RecommendationSummary(ORMModel):
    id: int
    recommendation_code: str
    section_code: str
    section_name: str
    route_name: str
    recommended_start: datetime
    recommended_end: datetime
    duration_hours: float
    priority_score: float
    operational_impact: str
    explanation: str
    status: str
    request_codes: list[str] = []
    train_count: int = 0


class OptimizationSummary(ORMModel):
    id: int
    run_code: str
    planning_start: datetime
    planning_end: datetime
    available_hours: float
    available_crew: int
    objective: str
    solver_status: str
    tasks_submitted: int
    tasks_selected: int
    priority_captured: float
    recommendations: list[RecommendationSummary]


class DashboardSummary(BaseModel):
    active_requests: int
    high_priority_requests: int
    conflicts: int
    recommended_blocks: int
    approved_plans: int
    trains_affected: int
    database_status: str
    optimization_status: str
    approval_status: str


class SectionSummary(ORMModel):
    id: int
    section_code: str
    name: str
    route_name: str
    from_station: str
    to_station: str
    length_km: float
    traffic_intensity: str
    operational_importance: str
    status: str
    asset_count: int
    active_request_count: int


class AssetSummary(ORMModel):
    id: int
    asset_code: str
    name: str
    asset_type: str
    department: str
    chainage_km: float
    condition: str
    criticality: str
    section_code: str
    section_name: str


class ConflictSummary(ORMModel):
    id: int
    request_code: str
    conflict_type: str
    severity: str
    cause: str
    suggested_resolution: str
    resolved: bool
