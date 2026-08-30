from app.services.synthetic_data import generate_simulated_scenario


def test_generate_simulated_scenario_builds_all_table_types():
    scenario = generate_simulated_scenario(seed=42)

    assert set(scenario.keys()) >= {"railway_context", "tms_defects", "smms_failures", "tdms_equipment", "train_schedule"}
    assert len(scenario["tms_defects"]) > 0
    assert len(scenario["smms_failures"]) > 0
    assert len(scenario["tdms_equipment"]) > 0
    assert len(scenario["train_schedule"]) > 0

    for record in scenario["tms_defects"]:
        assert record["section_code"]
        assert record["route_code"]
        assert record["priority_score"] >= 0
        assert "priority_explanation" in record

    for record in scenario["smms_failures"]:
        assert record["section_code"]
        assert record["route_code"]
        assert record["priority_score"] >= 0
        assert "priority_explanation" in record

    for record in scenario["tdms_equipment"]:
        assert record["section_code"]
        assert record["route_code"]
        assert record["priority_score"] >= 0
        assert "priority_explanation" in record


def test_simulated_records_share_common_correlation_keys():
    scenario = generate_simulated_scenario(seed=42)
    shared = {"railway_zone", "division", "section_code", "route_code"}

    route_map = {item["section_code"]: item["route_code"] for item in scenario["tms_defects"]}
    assert route_map

    for record in scenario["smms_failures"]:
        assert record["section_code"] in route_map or record["route_code"]

    for record in scenario["tdms_equipment"]:
        assert record["section_code"] in route_map or record["route_code"]

    for record in scenario["train_schedule"]:
        assert record["section_code"]
        assert record["route_code"]
        assert record["scheduled_date"]
        assert record["arrival_time"]
        assert record["departure_time"]

    assert scenario["railway_context"]["zones"]
    assert scenario["railway_context"]["divisions"]
    assert "sections" in scenario["railway_context"]
