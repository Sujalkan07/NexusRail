from fastapi import FastAPI

from app.api.routes import (
    smms_failures,
    tdms_equipment,
    tms_defects,
    train_schedule,
)
from app.core.database import engine
from app.models.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NexusRail API", version="0.1.0")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "NexusRail"}


app.include_router(tms_defects.router, prefix="/api/v1")
app.include_router(smms_failures.router, prefix="/api/v1")
app.include_router(tdms_equipment.router, prefix="/api/v1")
app.include_router(train_schedule.router, prefix="/api/v1")
