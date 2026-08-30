from app.services.prioritization import prioritize_records


def test_prioritization_generates_explainable_scores():
    records = [
        {
            "source_system": "TMS",
            "severity": "critical",
            "is_critical": True,
            "estimated_repair_hours": 8,
            "overdue_hours": 72,
            "conflicts_train_operations": True,
            "traffic_density": "high",
            "section_code": "SEC-12",
            "route_code": "R-71",
        },
        {
            "source_system": "SMMS",
            "severity": "low",
            "is_critical": False,
            "estimated_repair_hours": 1,
            "overdue_hours": 2,
            "conflicts_train_operations": False,
            "traffic_density": "low",
            "section_code": "SEC-18",
            "route_code": "R-88",
        },
    ]

    results = prioritize_records(records)

    assert len(results) == 2
    assert results[0]["priority_score"] >= results[1]["priority_score"]
    assert "priority_explanation" in results[0]
    assert "priority_factors" in results[0]
    assert len(results[0]["priority_factors"]) > 0
    assert results[0]["priority_score"] <= 100
    assert results[0]["priority_score"] >= 0


def test_prioritization_handles_missing_values():
    records = [{
        "source_system": "TDMS",
        "health_status": "degraded",
        "criticality_score": 6.5,
        "power_block_required": True,
        "conflicts_train_operations": False,
        "traffic_density": "medium",
    }]

    results = prioritize_records(records)
    assert len(results) == 1
    assert results[0]["priority_score"] >= 0
    assert results[0]["priority_explanation"]
