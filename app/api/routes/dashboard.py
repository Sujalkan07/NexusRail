from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.dashboard import build_dashboard_snapshot

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)) -> Dict[str, object]:
    return build_dashboard_snapshot(db)


@router.get("/recommendations")
def get_dashboard_recommendations(db: Session = Depends(get_db)) -> Dict[str, object]:
    snapshot = build_dashboard_snapshot(db)
    return snapshot["recommendations"]
