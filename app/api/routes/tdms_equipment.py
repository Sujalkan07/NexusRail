from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.tdms_equipment import TdmsEquipment
from app.schemas.tdms_equipment import TdmsEquipmentCreate, TdmsEquipmentRead

router = APIRouter(prefix="/tdms-equipment", tags=["tdms-equipment"])


@router.get("", response_model=List[TdmsEquipmentRead])
def list_tdms_equipment(db: Session = Depends(get_db)):
    return db.query(TdmsEquipment).all()


@router.get("/{equipment_id}", response_model=TdmsEquipmentRead)
def get_tdms_equipment(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.query(TdmsEquipment).filter(TdmsEquipment.id == equipment_id).first()
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TDMS equipment not found")
    return equipment


@router.post("", response_model=TdmsEquipmentRead, status_code=status.HTTP_201_CREATED)
def create_tdms_equipment(payload: TdmsEquipmentCreate, db: Session = Depends(get_db)):
    equipment = TdmsEquipment(**payload.model_dump())
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment
