from sqlalchemy import Boolean, DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TdmsEquipment(Base):
    __tablename__ = "tdms_equipment"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_system: Mapped[str] = mapped_column(String(50), default="TDMS")
    railway_zone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    division: Mapped[str | None] = mapped_column(String(100), nullable=True)
    section_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    route_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    equipment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    equipment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    substation_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    health_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    power_block_required: Mapped[bool | None] = mapped_column(Boolean, default=False)
    isolation_window_start: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    isolation_window_end: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_maintenance_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    criticality_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    equipment_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
