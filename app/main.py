from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    dashboard,
    smms_failures,
    tdms_equipment,
    tms_defects,
    train_schedule,
    planning,
)
from app.core.database import engine
from app.models.base import Base
import app.models.planning  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NexusRail API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|0\.0\.0\.0):(5173|5174|5175|\d+)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "NexusRail"}


app.include_router(tms_defects.router, prefix="/api/v1")
app.include_router(smms_failures.router, prefix="/api/v1")
app.include_router(tdms_equipment.router, prefix="/api/v1")
app.include_router(train_schedule.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(planning.router, prefix="/api/v1")
