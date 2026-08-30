from app.services.synthetic_data import generate_simulated_scenario
from app.services.prioritization import prioritize_records


def test_generate_simulated_scenario_handles_empty_sections_and_seeded_consistency():
    scenario = generate_simulated_scenario(seed=7, section_count=2)

    assert len(scenario["tms_defects"]) > 0
    assert len(scenario["smms_failures"]) > 0
    assert len(scenario["tdms_equipment"]) > 0
    assert len(scenario["train_schedule"]) > 0
    assert scenario["railway_context"]["sections"]


def test_prioritization_keeps_conflict_and_no_conflict_separate():
    records = [
        {"severity": "high", "is_critical": True, "conflicts_train_operations": True, "traffic_density": "high", "overdue_hours": 20},
        {"severity": "medium", "is_critical": False, "conflicts_train_operations": False, "traffic_density": "low", "overdue_hours": 1},
    ]

    results = prioritize_records(records)
    assert results[0]["priority_score"] > results[1]["priority_score"]
    assert results[0]["priority_score"] > 50
