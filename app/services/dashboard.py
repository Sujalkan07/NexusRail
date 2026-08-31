from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from sqlalchemy.orm import Session

from app.models.smms_failure import SmmsFailure
from app.models.tdms_equipment import TdmsEquipment
from app.models.tms_defect import TmsDefect
from app.models.train_schedule import TrainSchedule
from app.services.phase3_solver import build_solver_tasks, solve_maintenance_blocks
from app.services.synthetic_data import generate_simulated_scenario


def _serialize_record(record: Any) -> Dict[str, Any]:
    if record is None:
        return {}
    data = {}
    for key in record.__table__.columns.keys():
        value = getattr(record, key)
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        else:
            data[key] = value
    return data


def _flatten_records(records: Iterable[Any]) -> List[Dict[str, Any]]:
    return [_serialize_record(record) for record in records]


def _task_count_by_section(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {}
    for record in records:
        section = str(record.get("section_code") or "UNKNOWN")
        counts[section] = counts.get(section, 0) + 1
    return [{"section_code": section, "count": count} for section, count in sorted(counts.items())]


def _available_records(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    return {
        "tms_defects": _flatten_records(db.query(TmsDefect).all()),
        "smms_failures": _flatten_records(db.query(SmmsFailure).all()),
        "tdms_equipment": _flatten_records(db.query(TdmsEquipment).all()),
        "train_schedule": _flatten_records(db.query(TrainSchedule).all()),
    }


def build_dashboard_snapshot(db: Session) -> Dict[str, Any]:
    records = _available_records(db)
    if not any(records.values()):
        scenario = generate_simulated_scenario(seed=42, section_count=4)
        records = {
            "tms_defects": scenario["tms_defects"],
            "smms_failures": scenario["smms_failures"],
            "tdms_equipment": scenario["tdms_equipment"],
            "train_schedule": scenario["train_schedule"],
        }

    task_records = []
    for collection in (records["tms_defects"], records["smms_failures"], records["tdms_equipment"]):
        task_records.extend(collection)

    scenario = {
        "railway_context": {
            "sections": sorted(
                {
                    (item.get("section_code") or "UNKNOWN", item.get("route_code") or "UNKNOWN")
                    for item in task_records + records["train_schedule"]
                    if item.get("section_code")
                },
                key=lambda item: item[0],
            ),
        },
        "tms_defects": records["tms_defects"],
        "smms_failures": records["smms_failures"],
        "tdms_equipment": records["tdms_equipment"],
        "train_schedule": records["train_schedule"],
    }

    tasks = build_solver_tasks(scenario)
    solver_result = solve_maintenance_blocks(tasks, scenario["train_schedule"], horizon_hours=72)

    total_priority = sum(float(task.get("priority_score", 0.0)) for task in tasks)
    total_tasks = len(tasks)
    blocking_sections = _task_count_by_section(records["train_schedule"])
    active_conflicts = sum(
        1
        for train in records["train_schedule"]
        if str(train.get("status") or "").lower() in {"delayed", "rescheduled", "cancelled"}
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system_status": {
            "database": "available",
            "backend": "online",
            "solver": "available" if solver_result.feasible else "degraded",
            "approval": "permission-aware",
        },
        "overview": {
            "total_tasks": total_tasks,
            "tasks_selected": len(solver_result.selected_tasks),
            "tasks_rejected": len(solver_result.rejected_tasks),
            "priority_total": round(total_priority, 2),
            "priority_captured": round(sum(float(block.get("priority_captured", 0.0)) for block in solver_result.blocks), 2),
            "active_train_conflicts": active_conflicts,
            "sections_monitoring": len({item.get("section_code") for item in task_records if item.get("section_code")}),
        },
        "records": records,
        "recommendations": {
            "feasible": solver_result.feasible,
            "status": solver_result.status,
            "objective_value": solver_result.objective_value,
            "selected_tasks": solver_result.selected_tasks,
            "rejected_tasks": solver_result.rejected_tasks,
            "blocks": solver_result.blocks,
            "explanation": solver_result.explanation,
            "train_conflicts": [
                {
                    "section_code": train.get("section_code"),
                    "train_no": train.get("train_no"),
                    "route_code": train.get("route_code"),
                    "status": train.get("status"),
                    "arrival_time": train.get("arrival_time"),
                    "departure_time": train.get("departure_time"),
                }
                for train in records["train_schedule"]
            ],
        },
        "timeline": {
            "sections": blocking_sections,
            "available": True,
        },
        "approval": {
            "required": True,
            "auth_required": True,
            "status": "pending_review",
            "message": "Human review is required before any block is approved; backend persistence is not yet configured.",
        },
    }
