from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TmsDefectBase(BaseModel):
    source_system: str = "TMS"
    railway_zone: Optional[str] = None
    division: Optional[str] = None
    section_code: Optional[str] = None
    route_code: Optional[str] = None
    track_id: Optional[str] = None
    km_post: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    defect_type: Optional[str] = None
    defect_description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    is_critical: bool = False
    priority_score: Optional[float] = None
    reported_at: Optional[datetime] = None
    detected_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None
    estimated_repair_hours: Optional[float] = None


class TmsDefectCreate(TmsDefectBase):
    pass


class TmsDefectRead(TmsDefectBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
