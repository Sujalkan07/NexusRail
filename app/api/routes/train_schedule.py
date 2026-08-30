from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.train_schedule import TrainSchedule
from app.schemas.train_schedule import TrainScheduleCreate, TrainScheduleRead

router = APIRouter(prefix="/train-schedule", tags=["train-schedule"])


@router.get("", response_model=List[TrainScheduleRead])
def list_train_schedule(db: Session = Depends(get_db)):
    return db.query(TrainSchedule).all()


@router.get("/{schedule_id}", response_model=TrainScheduleRead)
def get_train_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(TrainSchedule).filter(TrainSchedule.id == schedule_id).first()
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train schedule record not found")
    return schedule


@router.post("", response_model=TrainScheduleRead, status_code=status.HTTP_201_CREATED)
def create_train_schedule(payload: TrainScheduleCreate, db: Session = Depends(get_db)):
    schedule = TrainSchedule(**payload.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule
