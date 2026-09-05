from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


recommendation_requests = Table(
    "recommendation_requests",
    Base.metadata,
    Column("recommendation_id", ForeignKey("recommendations.id"), primary_key=True),
    Column("maintenance_request_id", ForeignKey("maintenance_requests.id"), primary_key=True),
)


class RailwayZone(Base):
    __tablename__ = "railway_zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    divisions: Mapped[list["RailwayDivision"]] = relationship(back_populates="zone")


class RailwayDivision(Base):
    __tablename__ = "railway_divisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("railway_zones.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    code: Mapped[str] = mapped_column(String(20), unique=True)
    zone: Mapped[RailwayZone] = relationship(back_populates="divisions")
    corridors: Mapped[list["RailwayCorridor"]] = relationship(back_populates="division")


class RailwayCorridor(Base):
    __tablename__ = "railway_corridors"

    id: Mapped[int] = mapped_column(primary_key=True)
    division_id: Mapped[int] = mapped_column(ForeignKey("railway_divisions.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    route_type: Mapped[str] = mapped_column(String(50), default="mixed traffic")
    division: Mapped[RailwayDivision] = relationship(back_populates="corridors")
    sections: Mapped[list["RailwaySection"]] = relationship(back_populates="corridor")


class RailwaySection(Base):
    __tablename__ = "railway_sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    corridor_id: Mapped[int] = mapped_column(ForeignKey("railway_corridors.id"), index=True)
    section_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    from_station: Mapped[str] = mapped_column(String(120))
    to_station: Mapped[str] = mapped_column(String(120))
    length_km: Mapped[float] = mapped_column(Float)
    traffic_intensity: Mapped[str] = mapped_column(String(20), default="medium")
    operational_importance: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(30), default="operational")
    corridor: Mapped[RailwayCorridor] = relationship(back_populates="sections")
    assets: Mapped[list["RailwayAsset"]] = relationship(back_populates="section", cascade="all, delete-orphan")
    requests: Mapped[list["MaintenanceRequest"]] = relationship(back_populates="section")


class RailwayAsset(Base):
    __tablename__ = "railway_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("railway_sections.id"), index=True)
    asset_code: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    asset_type: Mapped[str] = mapped_column(String(80))
    department: Mapped[str] = mapped_column(String(80))
    chainage_km: Mapped[float] = mapped_column(Float)
    condition: Mapped[str] = mapped_column(String(30), default="good")
    criticality: Mapped[str] = mapped_column(String(20), default="medium")
    last_maintenance_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_maintenance_due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    section: Mapped[RailwaySection] = relationship(back_populates="assets")
    requests: Mapped[list["MaintenanceRequest"]] = relationship(back_populates="asset")


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("railway_sections.id"), index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("railway_assets.id"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    department: Mapped[str] = mapped_column(String(80))
    maintenance_type: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    estimated_duration_hours: Mapped[float] = mapped_column(Float)
    required_crew: Mapped[int] = mapped_column(Integer)
    safety_risk: Mapped[float] = mapped_column(Float)
    urgency: Mapped[float] = mapped_column(Float)
    priority_score: Mapped[float] = mapped_column(Float, default=0)
    priority_factors: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="submitted")
    section: Mapped[RailwaySection] = relationship(back_populates="requests")
    asset: Mapped[RailwayAsset] = relationship(back_populates="requests")
    block_request: Mapped["BlockRequest | None"] = relationship(back_populates="maintenance_request", uselist=False)
    recommendations: Mapped[list["Recommendation"]] = relationship(secondary=recommendation_requests, back_populates="requests")
    conflicts: Mapped[list["Conflict"]] = relationship(back_populates="maintenance_request", cascade="all, delete-orphan")


class BlockRequest(Base):
    __tablename__ = "block_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    block_code: Mapped[str] = mapped_column(String(40), unique=True)
    maintenance_request_id: Mapped[int] = mapped_column(ForeignKey("maintenance_requests.id"), unique=True)
    track_affected: Mapped[str] = mapped_column(String(80))
    traffic_impact: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(30), default="requested")
    maintenance_request: Mapped[MaintenanceRequest] = relationship(back_populates="block_request")


class Train(Base):
    __tablename__ = "trains"

    id: Mapped[int] = mapped_column(primary_key=True)
    train_number: Mapped[str] = mapped_column(String(30), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    service_type: Mapped[str] = mapped_column(String(50))
    movements: Mapped[list["TrainMovement"]] = relationship(back_populates="train")


class TrainMovement(Base):
    __tablename__ = "train_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    train_id: Mapped[int] = mapped_column(ForeignKey("trains.id"), index=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("railway_sections.id"), index=True)
    arrival_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    train: Mapped[Train] = relationship(back_populates="movements")
    section: Mapped[RailwaySection] = relationship()


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_code: Mapped[str] = mapped_column(String(40), unique=True)
    planning_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    planning_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    available_hours: Mapped[float] = mapped_column(Float)
    available_crew: Mapped[int] = mapped_column(Integer)
    objective: Mapped[str] = mapped_column(String(180))
    solver_status: Mapped[str] = mapped_column(String(30), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="optimization_run")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    recommendation_code: Mapped[str] = mapped_column(String(40), unique=True)
    optimization_run_id: Mapped[int] = mapped_column(ForeignKey("optimization_runs.id"), index=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("railway_sections.id"), index=True)
    recommended_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    recommended_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_hours: Mapped[float] = mapped_column(Float)
    priority_score: Mapped[float] = mapped_column(Float)
    operational_impact: Mapped[str] = mapped_column(String(20))
    explanation: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="pending_review")
    optimization_run: Mapped[OptimizationRun] = relationship(back_populates="recommendations")
    section: Mapped[RailwaySection] = relationship()
    requests: Mapped[list[MaintenanceRequest]] = relationship(secondary=recommendation_requests, back_populates="recommendations")
    approval: Mapped["Approval | None"] = relationship(back_populates="recommendation", uselist=False)


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("recommendations.id"), unique=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    reviewed_by: Mapped[str | None] = mapped_column(String(120))
    comments: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    recommendation: Mapped[Recommendation] = relationship(back_populates="approval")


class Conflict(Base):
    __tablename__ = "conflicts"

    id: Mapped[int] = mapped_column(primary_key=True)
    maintenance_request_id: Mapped[int] = mapped_column(ForeignKey("maintenance_requests.id"), index=True)
    conflict_type: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(20))
    cause: Mapped[str] = mapped_column(Text)
    suggested_resolution: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    maintenance_request: Mapped[MaintenanceRequest] = relationship(back_populates="conflicts")
