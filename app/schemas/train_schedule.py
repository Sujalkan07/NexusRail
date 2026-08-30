from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TrainScheduleBase(BaseModel):
    source_system: str = "COA"
    railway_zone: Optional[str] = None
    division: Optional[str] = None
    section_code: Optional[str] = None
    route_code: Optional[str] = None
    train_no: Optional[str] = None
    service_type: Optional[str] = None
    scheduled_date: Optional[date] = None
    origin_station: Optional[str] = None
    destination_station: Optional[str] = None
    direction: Optional[str] = None
    arrival_time: Optional[datetime] = None
    departure_time: Optional[datetime] = None
    is_goods: bool = False
    status: Optional[str] = None


class TrainScheduleCreate(TrainScheduleBase):
    pass


class TrainScheduleRead(TrainScheduleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    last_updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
