from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.smms_failure import SmmsFailure
from app.schemas.smms_failure import SmmsFailureCreate, SmmsFailureRead

router = APIRouter(prefix="/smms-failures", tags=["smms-failures"])


@router.get("", response_model=List[SmmsFailureRead])
def list_smms_failures(db: Session = Depends(get_db)):
    return db.query(SmmsFailure).all()


@router.get("/{failure_id}", response_model=SmmsFailureRead)
def get_smms_failure(failure_id: int, db: Session = Depends(get_db)):
    failure = db.query(SmmsFailure).filter(SmmsFailure.id == failure_id).first()
    if failure is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SMMS failure not found")
    return failure


@router.post("", response_model=SmmsFailureRead, status_code=status.HTTP_201_CREATED)
def create_smms_failure(payload: SmmsFailureCreate, db: Session = Depends(get_db)):
    failure = SmmsFailure(**payload.model_dump())
    db.add(failure)
    db.commit()
    db.refresh(failure)
    return failure
