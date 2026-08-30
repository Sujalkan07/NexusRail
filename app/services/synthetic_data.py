from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from typing import Any, Dict, List


SEVERITY_LEVELS = ["low", "medium", "high", "critical"]
TRAFFIC_DENSITY = ["low", "medium", "high"]
TMS_DEFECT_TYPES = [
    "track_crack",
    "ballast_settlement",
    "signalling_rail_joint",
    "track_wear",
    "sleepers_damage",
    "level_crossing_issue",
]
SMMS_FAILURE_TYPES = [
    "signal_fault",
    "track_circuit_failure",
    "point_machine_fault",
    "power_supply_issue",
    "communication_link_fault",
]
TDMS_EQUIPMENT_TYPES = [
    "overhead_equipment",
    "traction_transformer",
    "switchgear",
    "feeder_cable",
    "rectifier",
]
SERVICE_TYPES = ["passenger", "goods", "express", "commuter"]
STATUSES = ["on_time", "delayed", "cancelled", "rescheduled"]


def _seed(seed: int | None = None) -> random.Random:
    return random.Random(seed if seed is not None else 42)


def _iso_datetime(value: datetime) -> str:
    return value.isoformat()


def _choose_severity(rng: random.Random) -> str:
    return rng.choice(SEVERITY_LEVELS)


def _choose_traffic(rng: random.Random) -> str:
    return rng.choice(TRAFFIC_DENSITY)


def _build_section_map(rng: random.Random, section_count: int = 4) -> List[Dict[str, str]]:
    base_sections = [
        ("NR", "Delhi", "SEC-12", "R-71"),
        ("NR", "Delhi", "SEC-18", "R-88"),
        ("ER", "Kolkata", "SEC-27", "R-55"),
        ("CR", "Mumbai", "SEC-41", "R-13"),
        ("SR", "Chennai", "SEC-63", "R-30"),
    ]
    selected = base_sections[:section_count]
    sections = []
    for zone, division, section_code, route_code in selected:
        sections.append({
            "railway_zone": zone,
            "division": division,
            "section_code": section_code,
            "route_code": route_code,
            "track_id": f"TK-{section_code.split('-')[-1]}",
        })
    return sections


def _build_train_schedule_records(rng: random.Random, sections: List[Dict[str, str]], day_offset: int = 0) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for idx, section in enumerate(sections):
        traffic = _choose_traffic(rng)
        for j in range(3 + (idx % 2)):
            scheduled_date = date.today() + timedelta(days=day_offset + (j % 5))
            start_hour = 5 + ((idx + j) * 3) % 16
            arrival = datetime.combine(scheduled_date, datetime.min.time()) + timedelta(hours=start_hour, minutes=15)
            departure = arrival + timedelta(hours=1 + (j % 3))
            records.append({
                "source_system": "COA",
                "railway_zone": section["railway_zone"],
                "division": section["division"],
                "section_code": section["section_code"],
                "route_code": section["route_code"],
                "train_no": f"T{(idx + 1) * 100 + j}",
                "service_type": rng.choice(SERVICE_TYPES),
                "scheduled_date": scheduled_date,
                "origin_station": f"STN-{(idx + 1) * 10}",
                "destination_station": f"STN-{(idx + 2) * 10}",
                "direction": rng.choice(["up", "down"]),
                "arrival_time": _iso_datetime(arrival),
                "departure_time": _iso_datetime(departure),
                "is_goods": (j % 2 == 0),
                "status": rng.choice(STATUSES),
                "traffic_density": traffic,
                "conflicts_train_operations": bool((idx + j) % 2 == 0),
                "priority_score": 0.0,
                "priority_explanation": "",
            })
    return records


def _build_tms_defects(rng: random.Random, sections: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for idx, section in enumerate(sections):
        for j in range(2):
            severity = _choose_severity(rng)
            defect_type = rng.choice(TMS_DEFECT_TYPES)
            repair_duration = 1 + (idx + j) * 2 + (0 if severity in {"low", "medium"} else 3)
            conflict = bool((idx + j) % 2 == 0)
            record = {
                "source_system": "TMS",
                "railway_zone": section["railway_zone"],
                "division": section["division"],
                "section_code": section["section_code"],
                "route_code": section["route_code"],
                "track_id": section["track_id"],
                "km_post": round(100 + idx * 12 + j * 5, 3),
                "latitude": round(28.6 + idx * 0.4 + j * 0.1, 6),
                "longitude": round(77.2 + idx * 0.3 + j * 0.1, 6),
                "defect_type": defect_type,
                "defect_description": f"Synthetic defect: {defect_type} on {section['section_code']}",
                "severity": severity,
                "status": "open" if j % 2 == 0 else "monitoring",
                "is_critical": severity in {"high", "critical"},
                "priority_score": 0.0,
                "reported_at": _iso_datetime(datetime.utcnow() - timedelta(hours=8 + idx * 8 + j * 3)),
                "detected_at": _iso_datetime(datetime.utcnow() - timedelta(hours=12 + idx * 10 + j * 4)),
                "last_updated_at": _iso_datetime(datetime.utcnow() - timedelta(hours=2 + idx + j)),
                "estimated_repair_hours": repair_duration,
                "conflicts_train_operations": conflict,
                "traffic_density": _choose_traffic(rng),
                "priority_explanation": "",
            }
            records.append(record)
    return records


def _build_smms_failures(rng: random.Random, sections: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for idx, section in enumerate(sections):
        for j in range(2):
            severity = _choose_severity(rng)
            failure_type = rng.choice(SMMS_FAILURE_TYPES)
            overdue_hours = (idx + 1) * 6 + (j + 1) * 8 + (7 if severity in {"high", "critical"} else 0)
            requires_power_isolation = bool((idx + j) % 2 == 0)
            record = {
                "source_system": "SMMS",
                "railway_zone": section["railway_zone"],
                "division": section["division"],
                "section_code": section["section_code"],
                "route_code": section["route_code"],
                "signal_id": f"SIG-{(idx + 1) * 10 + j}",
                "equipment_id": f"SIG-EQ-{(idx + 1) * 10 + j}",
                "failure_type": failure_type,
                "failure_description": f"Synthetic {failure_type} on {section['section_code']}",
                "severity": severity,
                "status": "active" if j % 2 == 0 else "resolved",
                "overdue_hours": overdue_hours,
                "failure_started_at": _iso_datetime(datetime.utcnow() - timedelta(hours=overdue_hours)),
                "last_seen_at": _iso_datetime(datetime.utcnow() - timedelta(hours=max(1, overdue_hours // 4))),
                "requires_power_isolation": requires_power_isolation,
                "related_block_request_id": f"BLK-{idx + 1}-{j + 1}",
                "conflicts_train_operations": bool((idx + j) % 2 == 1),
                "traffic_density": _choose_traffic(rng),
                "estimated_repair_hours": 2 + (idx % 3) + (j % 2),
                "priority_score": 0.0,
                "priority_explanation": "",
            }
            records.append(record)
    return records


def _build_tdms_equipment(rng: random.Random, sections: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for idx, section in enumerate(sections):
        for j in range(2):
            equipment_type = rng.choice(TDMS_EQUIPMENT_TYPES)
            health_status = rng.choice(["healthy", "degraded", "critical", "failed"])
            criticality_score = round(1 + (idx + j) * 1.7 + (6 if health_status in {"critical", "failed"} else 0), 2)
            power_block_required = bool((idx + j) % 2 == 0 or health_status in {"critical", "failed"})
            isolation_start = datetime.utcnow() + timedelta(hours=2 + idx)
            isolation_end = isolation_start + timedelta(hours=4 + (j % 3))
            record = {
                "source_system": "TDMS",
                "railway_zone": section["railway_zone"],
                "division": section["division"],
                "section_code": section["section_code"],
                "route_code": section["route_code"],
                "equipment_id": f"OHE-{(idx + 1) * 10 + j}",
                "equipment_type": equipment_type,
                "substation_id": f"SUB-{(idx + 1) * 5 + j}",
                "health_status": health_status,
                "power_block_required": power_block_required,
                "isolation_window_start": _iso_datetime(isolation_start),
                "isolation_window_end": _iso_datetime(isolation_end),
                "last_maintenance_at": _iso_datetime(datetime.utcnow() - timedelta(days=15 + idx * 4)),
                "criticality_score": criticality_score,
                "equipment_notes": f"Synthetic {health_status} condition for {equipment_type}",
                "conflicts_train_operations": bool((idx + j) % 2 == 1),
                "traffic_density": _choose_traffic(rng),
                "priority_score": 0.0,
                "priority_explanation": "",
            }
            records.append(record)
    return records


def generate_simulated_scenario(seed: int | None = None, section_count: int = 4) -> Dict[str, Any]:
    rng = _seed(seed)
    sections = _build_section_map(rng, section_count=section_count)

    railway_context = {
        "zones": sorted({section["railway_zone"] for section in sections}),
        "divisions": sorted({section["division"] for section in sections}),
        "sections": sections,
    }

    tms_defects = _build_tms_defects(rng, sections)
    smms_failures = _build_smms_failures(rng, sections)
    tdms_equipment = _build_tdms_equipment(rng, sections)
    train_schedule = _build_train_schedule_records(rng, sections, day_offset=0)

    return {
        "railway_context": railway_context,
        "tms_defects": tms_defects,
        "smms_failures": smms_failures,
        "tdms_equipment": tdms_equipment,
        "train_schedule": train_schedule,
    }
