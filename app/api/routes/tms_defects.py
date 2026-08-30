from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.tms_defect import TmsDefect
from app.schemas.tms_defect import TmsDefectCreate, TmsDefectRead

router = APIRouter(prefix="/tms-defects", tags=["tms-defects"])


@router.get("", response_model=List[TmsDefectRead])
def list_tms_defects(db: Session = Depends(get_db)):
    return db.query(TmsDefect).all()


@router.get("/{defect_id}", response_model=TmsDefectRead)
def get_tms_defect(defect_id: int, db: Session = Depends(get_db)):
    defect = db.query(TmsDefect).filter(TmsDefect.id == defect_id).first()
    if defect is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TMS defect not found")
    return defect


@router.post("", response_model=TmsDefectRead, status_code=status.HTTP_201_CREATED)
def create_tms_defect(payload: TmsDefectCreate, db: Session = Depends(get_db)):
    defect = TmsDefect(**payload.model_dump())
    db.add(defect)
    db.commit()
    db.refresh(defect)
    return defect
