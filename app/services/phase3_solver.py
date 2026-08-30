from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ortools.sat.python import cp_model


def _coerce_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _task_sort_key(task: Dict[str, Any]) -> Tuple[float, str]:
    return (-_coerce_float(task.get("priority_score"), 0.0), str(task.get("task_id") or ""))


def build_solver_tasks(scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []
    for source_name, collection_name in [
        ("TMS", "tms_defects"),
        ("SMMS", "smms_failures"),
        ("TDMS", "tdms_equipment"),
    ]:
        records = scenario.get(collection_name, [])
        for idx, record in enumerate(records):
            duration = _coerce_float(record.get("estimated_repair_hours") or record.get("duration_hours"), 2.0)
            if duration <= 0:
                duration = 2.0
            priority = _coerce_float(record.get("priority_score"), 0.0)
            if priority <= 0:
                priority = _coerce_float(record.get("criticality_score"), 0.0) + 10.0
            task = {
                "task_id": f"{source_name}-{idx}-{record.get('section_code', 'unknown')}",
                "source_system": source_name,
                "department": {
                    "TMS": "engineering",
                    "SMMS": "signal",
                    "TDMS": "traction",
                }.get(source_name, "engineering"),
                "section_code": record.get("section_code") or "UNKNOWN",
                "route_code": record.get("route_code") or "UNKNOWN",
                "task_type": record.get("defect_type") or record.get("failure_type") or record.get("equipment_type") or "maintenance",
                "duration_hours": float(duration),
                "priority_score": priority,
                "requirements": [],
                "window_start": 0,
                "window_end": 72,
                "power_isolation_required": bool(record.get("requires_power_isolation") or record.get("power_block_required")),
                "conflicts_train_operations": bool(record.get("conflicts_train_operations")),
                "depends_on": [],
                "metadata": record,
            }
            if task["power_isolation_required"]:
                task["requirements"].append("power_isolation")
            if task["conflicts_train_operations"]:
                task["requirements"].append("train_conflict_window")
            tasks.append(task)
    return sorted(tasks, key=_task_sort_key)


@dataclass
class SolverResult:
    feasible: bool
    blocks: List[Dict[str, Any]] = field(default_factory=list)
    selected_tasks: List[str] = field(default_factory=list)
    rejected_tasks: List[Dict[str, Any]] = field(default_factory=list)
    explanation: str = ""
    objective_value: float = 0.0
    status: str = "optimal"
    model: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feasible": self.feasible,
            "status": self.status,
            "objective_value": round(self.objective_value, 2),
            "selected_tasks": self.selected_tasks,
            "rejected_tasks": [
                {
                    "task_id": task.get("task_id"),
                    "reason": task.get("reason"),
                    "priority_score": task.get("priority_score"),
                }
                for task in self.rejected_tasks
            ],
            "blocks": self.blocks,
            "explanation": self.explanation,
        }


def _prepare_train_windows(train_schedule: Iterable[Dict[str, Any]], horizon_hours: int) -> List[Dict[str, Any]]:
    windows: List[Dict[str, Any]] = []
    for record in train_schedule:
        section_code = record.get("section_code") or "UNKNOWN"
        arrival = record.get("arrival_time")
        departure = record.get("departure_time")
        if arrival is None or departure is None:
            continue
        start_hour = 0.0
        end_hour = float(horizon_hours)
        try:
            if isinstance(arrival, str):
                start_dt = datetime.fromisoformat(arrival)
                start_hour = float(start_dt.hour + start_dt.minute / 60.0)
            if isinstance(departure, str):
                end_dt = datetime.fromisoformat(departure)
                end_hour = float(end_dt.hour + end_dt.minute / 60.0)
        except ValueError:
            start_hour = 0.0
            end_hour = float(horizon_hours)
        windows.append({
            "section_code": section_code,
            "route_code": record.get("route_code") or "UNKNOWN",
            "start_hour": min(max(start_hour, 0.0), float(horizon_hours)),
            "end_hour": min(max(end_hour, start_hour + 0.5), float(horizon_hours)),
            "train_no": record.get("train_no") or "UNKNOWN",
            "status": record.get("status") or "unknown",
        })
    return windows


def solve_maintenance_blocks(tasks: List[Dict[str, Any]], train_schedule: Iterable[Dict[str, Any]], horizon_hours: int = 72) -> SolverResult:
    if not tasks:
        return SolverResult(
            feasible=False,
            explanation="No maintenance tasks were supplied to the solver.",
            status="infeasible",
        )

    sorted_tasks = sorted(tasks, key=_task_sort_key)
    train_windows = _prepare_train_windows(train_schedule, horizon_hours)
    model = cp_model.CpModel()

    selected = {}
    start = {}
    end = {}
    optional_intervals = {}
    section_intervals: Dict[str, List[Any]] = {}
    block_id_by_task: Dict[str, str] = {}

    for i, task in enumerate(sorted_tasks):
        selected[i] = model.NewBoolVar(f"selected_{i}")
        duration_minutes = max(30, int(float(task.get("duration_hours", 2.0)) * 60))
        start[i] = model.NewIntVar(0, int(horizon_hours * 60), f"start_{i}")
        end[i] = model.NewIntVar(0, int(horizon_hours * 60), f"end_{i}")
        window_start = int(_coerce_float(task.get("window_start"), 0.0) * 60)
        window_end = int(_coerce_float(task.get("window_end"), float(horizon_hours)) * 60)
        if window_end <= window_start:
            window_end = int(horizon_hours * 60)
        model.Add(start[i] >= window_start).OnlyEnforceIf(selected[i])
        model.Add(end[i] <= window_end).OnlyEnforceIf(selected[i])
        model.Add(end[i] == start[i] + duration_minutes)
        optional_intervals[i] = model.NewOptionalIntervalVar(start[i], duration_minutes, end[i], selected[i], f"opt_interval_{i}")
        section_key = str(task.get("section_code") or "UNKNOWN")
        section_intervals.setdefault(section_key, []).append(optional_intervals[i])

    for section_key, intervals in section_intervals.items():
        if len(intervals) > 1:
            model.AddNoOverlap(intervals)

    for i, task in enumerate(sorted_tasks):
        if not task.get("conflicts_train_operations", False):
            continue
        section_key = str(task.get("section_code") or "UNKNOWN")
        for window in train_windows:
            if window.get("section_code") != section_key:
                continue
            train_start = int(float(window.get("start_hour", 0.0)) * 60)
            train_end = int(float(window.get("end_hour", float(horizon_hours))) * 60)
            if train_end <= train_start:
                train_end = min(train_start + 30, int(horizon_hours * 60))
            model.Add(start[i] >= train_end).OnlyEnforceIf(selected[i])
            model.Add(end[i] <= train_start).OnlyEnforceIf(selected[i])

    for i, task in enumerate(sorted_tasks):
        for dependency in task.get("depends_on", []):
            dep_task_id = dependency.get("task_id") if isinstance(dependency, dict) else dependency
            for j, other in enumerate(sorted_tasks):
                if other.get("task_id") == dep_task_id:
                    model.Add(start[i] >= end[j]).OnlyEnforceIf([selected[i], selected[j]])

    for i, task in enumerate(sorted_tasks):
        if task.get("power_isolation_required"):
            for j, other in enumerate(sorted_tasks):
                if i == j:
                    continue
                if other.get("power_isolation_required") and other.get("section_code") == task.get("section_code"):
                    model.Add(start[i] == start[j]).OnlyEnforceIf([selected[i], selected[j]])
                    model.Add(end[i] == end[j]).OnlyEnforceIf([selected[i], selected[j]])

    objective_terms = []
    block_penalty = 0.0
    for i, task in enumerate(sorted_tasks):
        score = _coerce_float(task.get("priority_score"), 0.0)
        objective_terms.append(score * selected[i])
        objective_terms.append(-0.05 * float(task.get("duration_hours", 0.0)) * 60 * selected[i])
        block_penalty += 2.0 * selected[i]

    objective_terms.append(-block_penalty)
    model.Maximize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    solver.parameters.num_search_workers = 1
    solver.parameters.log_search_progress = False
    solver.parameters.random_seed = 42

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return SolverResult(
            feasible=False,
            explanation="No feasible maintenance schedule was found for the supplied task set and constraints.",
            status="infeasible",
            model=model,
        )

    selected_task_ids: List[str] = []
    rejected_tasks: List[Dict[str, Any]] = []
    task_blocks: Dict[str, str] = {}
    grouped: Dict[str, List[str]] = {}

    for i, task in enumerate(sorted_tasks):
        chosen = bool(solver.Value(selected[i]))
        if chosen:
            selected_task_ids.append(task["task_id"])
            block_name = f"mega-block-{task.get('section_code', 'unknown')}"
            task_blocks[task["task_id"]] = block_name
            grouped.setdefault(block_name, []).append(task["task_id"])
        else:
            rejected_tasks.append({
                "task_id": task["task_id"],
                "reason": "Not selected under the optimization objective or conflict constraints",
                "priority_score": _coerce_float(task.get("priority_score"), 0.0),
            })

    blocks: List[Dict[str, Any]] = []
    block_order = sorted(grouped.keys())
    for block_name in block_order:
        task_ids = grouped[block_name]
        tasks_for_block = [sorted_tasks[i] for i in range(len(sorted_tasks)) if sorted_tasks[i]["task_id"] in task_ids]
        if not tasks_for_block:
            continue
        start_minutes = min(solver.Value(start[i]) for i, task in enumerate(sorted_tasks) if task["task_id"] in task_ids)
        end_minutes = max(solver.Value(end[i]) for i, task in enumerate(sorted_tasks) if task["task_id"] in task_ids)
        section_code = tasks_for_block[0].get("section_code") or "UNKNOWN"
        power_required = any(task.get("power_isolation_required") for task in tasks_for_block)
        conflicts = [
            window for window in train_windows if window.get("section_code") == section_code
        ]
        blocks.append({
            "block_id": block_name,
            "section_code": section_code,
            "route_code": tasks_for_block[0].get("route_code") or "UNKNOWN",
            "start_hour": start_minutes / 60.0,
            "end_hour": end_minutes / 60.0,
            "task_ids": task_ids,
            "power_block_required": power_required,
            "power_isolation_covered": power_required,
            "train_conflicts": conflicts,
            "priority_captured": round(sum(_coerce_float(task.get("priority_score"), 0.0) for task in tasks_for_block), 2),
        })

    total_priority = sum(_coerce_float(task.get("priority_score"), 0.0) for i, task in enumerate(sorted_tasks) if solver.Value(selected[i]))
    explanation = (
        f"Selected {len(selected_task_ids)} tasks capturing {total_priority:.2f} priority value across "
        f"{len(blocks)} recommended block(s). {len(rejected_tasks)} tasks were deferred because they conflicted with "
        "train windows, dependencies or incompatible maintenance windows."
    )

    return SolverResult(
        feasible=True,
        blocks=blocks,
        selected_tasks=selected_task_ids,
        rejected_tasks=rejected_tasks,
        explanation=explanation,
        objective_value=float(solver.ObjectiveValue()),
        status="optimal" if status == cp_model.OPTIMAL else "feasible",
        model=model,
    )
