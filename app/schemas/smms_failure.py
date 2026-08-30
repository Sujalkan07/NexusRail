from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SmmsFailureBase(BaseModel):
    source_system: str = "SMMS"
    railway_zone: Optional[str] = None
    division: Optional[str] = None
    section_code: Optional[str] = None
    route_code: Optional[str] = None
    signal_id: Optional[str] = None
    equipment_id: Optional[str] = None
    failure_type: Optional[str] = None
    failure_description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    overdue_hours: Optional[float] = None
    failure_started_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    requires_power_isolation: bool = False
    related_block_request_id: Optional[str] = None


class SmmsFailureCreate(SmmsFailureBase):
    pass


class SmmsFailureRead(SmmsFailureBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
