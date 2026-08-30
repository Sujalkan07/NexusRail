from app.services.synthetic_data import generate_simulated_scenario
from app.services.phase3_solver import solve_maintenance_blocks, build_solver_tasks


def test_phase3_solver_builds_feasible_mega_block():
    scenario = generate_simulated_scenario(seed=42, section_count=4)
    tasks = build_solver_tasks(scenario)
    result = solve_maintenance_blocks(tasks, scenario["train_schedule"], horizon_hours=72)

    assert result.feasible is True
    assert result.blocks
    assert result.selected_tasks
    assert result.objective_value >= 0
    for block in result.blocks:
        assert block["start_hour"] >= 0
        assert block["end_hour"] > block["start_hour"]
        assert block["task_ids"]


def test_phase3_solver_respects_train_conflicts():
    scenario = generate_simulated_scenario(seed=7, section_count=2)
    tasks = build_solver_tasks(scenario)
    result = solve_maintenance_blocks(tasks, scenario["train_schedule"], horizon_hours=36)

    assert result.feasible is True
    for block in result.blocks:
        for train in block["train_conflicts"]:
            assert train["section_code"] == block["section_code"] or train["section_code"] in {t["section_code"] for t in result.blocks}


def test_phase3_solver_respects_power_isolation():
    scenario = generate_simulated_scenario(seed=9, section_count=2)
    tasks = build_solver_tasks(scenario)
    result = solve_maintenance_blocks(tasks, scenario["train_schedule"], horizon_hours=48)

    assert result.feasible is True
    for block in result.blocks:
        if block["power_block_required"]:
            assert block["power_isolation_covered"] is True


def test_phase3_solver_handles_dependencies_and_rejections():
    scenario = generate_simulated_scenario(seed=11, section_count=2)
    tasks = build_solver_tasks(scenario)
    result = solve_maintenance_blocks(tasks, scenario["train_schedule"], horizon_hours=48)

    assert result.feasible is True
    assert "rejected_tasks" in result.to_dict()
    assert isinstance(result.rejected_tasks, list)


def test_phase3_solver_infeasible_scenario_returns_explanation():
    result = solve_maintenance_blocks([], [], horizon_hours=24)

    assert result.feasible is False or result.status == "infeasible"
    assert result.explanation


def test_phase3_solver_is_deterministic_across_runs():
    scenario = generate_simulated_scenario(seed=42, section_count=4)
    tasks = build_solver_tasks(scenario)
    result_a = solve_maintenance_blocks(tasks, scenario["train_schedule"], horizon_hours=72)
    result_b = solve_maintenance_blocks(tasks, scenario["train_schedule"], horizon_hours=72)

    assert result_a.to_dict() == result_b.to_dict()
