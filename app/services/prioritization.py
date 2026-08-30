from __future__ import annotations

from typing import Any, Dict, Iterable, List


SEVERITY_WEIGHTS = {
    "low": 0.25,
    "medium": 0.45,
    "high": 0.7,
    "critical": 0.95,
}

HEALTH_WEIGHTS = {
    "healthy": 0.15,
    "degraded": 0.45,
    "critical": 0.8,
    "failed": 0.98,
}

TRAFFIC_WEIGHTS = {
    "low": 0.2,
    "medium": 0.5,
    "high": 0.85,
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _factor_score(record: Dict[str, Any], factor_name: str, default: float = 0.0) -> float:
    return _safe_float(record.get(factor_name), default)


def prioritize_records(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for record in records:
        severity = str(record.get("severity") or record.get("health_status") or "low").lower()
        severity_factor = SEVERITY_WEIGHTS.get(severity, 0.25)
        if "health_status" in record:
            severity_factor = HEALTH_WEIGHTS.get(severity, 0.45)

        criticality = _factor_score(record, "criticality_score", 0.0)
        criticality_factor = min(max(criticality / 10.0, 0.0), 1.0)
        if record.get("is_critical"):
            criticality_factor = max(criticality_factor, 0.8)

        overdue_hours = _factor_score(record, "overdue_hours", 0.0)
        overdue_factor = min(overdue_hours / 72.0, 1.0)

        repair_hours = _factor_score(record, "estimated_repair_hours", 0.0)
        repair_factor = min(repair_hours / 12.0, 1.0)

        conflict_flag = bool(record.get("conflicts_train_operations"))
        conflict_factor = 1.0 if conflict_flag else 0.0

        traffic_density = str(record.get("traffic_density") or "low").lower()
        traffic_factor = TRAFFIC_WEIGHTS.get(traffic_density, 0.2)

        power_isolation = bool(record.get("requires_power_isolation") or record.get("power_block_required"))
        isolation_factor = 1.0 if power_isolation else 0.2

        score = (
            0.30 * severity_factor
            + 0.20 * criticality_factor
            + 0.15 * overdue_factor
            + 0.15 * conflict_factor
            + 0.10 * traffic_factor
            + 0.10 * repair_factor
            + 0.10 * isolation_factor
        ) * 100.0
        score = max(0.0, min(score, 100.0))

        factors = [
            ("severity", round(severity_factor, 3)),
            ("criticality", round(criticality_factor, 3)),
            ("overdue_hours", round(overdue_factor, 3)),
            ("train_conflict", round(conflict_factor, 3)),
            ("traffic_density", round(traffic_factor, 3)),
            ("repair_duration", round(repair_factor, 3)),
            ("power_isolation", round(isolation_factor, 3)),
        ]

        explanation_parts = [
            f"Severity factor: {severity_factor:.2f}",
            f"Criticality factor: {criticality_factor:.2f}",
            f"Overdue factor: {overdue_factor:.2f}",
            f"Train conflict factor: {conflict_factor:.2f}",
            f"Traffic factor: {traffic_factor:.2f}",
            f"Repair duration factor: {repair_factor:.2f}",
            f"Power isolation factor: {isolation_factor:.2f}",
        ]

        explanation = "; ".join(explanation_parts)
        record_result = dict(record)
        record_result["priority_score"] = round(score, 2)
        record_result["priority_factors"] = factors
        record_result["priority_explanation"] = explanation
        results.append(record_result)

    results.sort(key=lambda x: x["priority_score"], reverse=True)
    return results
