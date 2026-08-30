from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TdmsEquipmentBase(BaseModel):
    source_system: str = "TDMS"
    railway_zone: Optional[str] = None
    division: Optional[str] = None
    section_code: Optional[str] = None
    route_code: Optional[str] = None
    equipment_id: Optional[str] = None
    equipment_type: Optional[str] = None
    substation_id: Optional[str] = None
    health_status: Optional[str] = None
    power_block_required: bool = False
    isolation_window_start: Optional[datetime] = None
    isolation_window_end: Optional[datetime] = None
    last_maintenance_at: Optional[datetime] = None
    criticality_score: Optional[float] = None
    equipment_notes: Optional[str] = None


class TdmsEquipmentCreate(TdmsEquipmentBase):
    pass


class TdmsEquipmentRead(TdmsEquipmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
