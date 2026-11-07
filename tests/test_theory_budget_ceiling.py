"""The budget ceiling must come from the cells, and the analysis must be able to fail."""

from benchmarks import theory_budget_ceiling as tbc
from organica.sleep import SleepService


def _row(budget, seed, peak, final, theories=8, stable=35, degree=12):
    cap_t, cap_h = tbc.BUDGETS[budget]
    return {
        "budget": budget,
        "seed": seed,
        "degree": degree,
        "realised_degree": degree,
        "world_edges": 60,
        "theories_final": theories,
        "theories_max": theories,
        "hypotheses_final": 4,
        "hypotheses_max": 4,
        "cap_theories": cap_t,
        "cap_hypotheses": cap_h,
        "cap_bound_theories": theories >= cap_t,
        "cap_bound_hypotheses": False,
        "stable_final": stable if final else 0,
        "stable_peak": stable,
        "coverage_peak": peak,
        "precision": 1.0 if peak else None,
        "coverage": final,
        "false_assertions": 0,
    }


def _rows(shipped, lifted, doubled=None, theories=(8, 16, 20), final=None):
    doubled = shipped if doubled is None else doubled
    final = shipped if final is None else final
    out = []
    for seed in range(3):
        out.append(_row("shipped", seed, shipped, final, theories[0]))
        out.append(_row("doubled", seed, doubled, final, theories[1]))
        out.append(_row("lifted", seed, lifted, final, theories[2]))
    return out


def test_the_lifted_arm_really_overrides_the_engine_caps():
    arm = tbc.arm_for("lifted")
    assert issubclass(arm, SleepService)
    assert arm.MAX_THEORIES == 64
    assert arm.MAX_HYPOTHESES == 128
    assert tbc.arm_for("shipped").MAX_THEORIES == SleepService.MAX_THEORIES


def test_the_ceiling_is_the_peak_at_the_shipped_budget():
    record = tbc.analyse(_rows(0.40, 0.72))
    assert record["peak_ceiling_at_shipped_budget"] == 0.40
    assert record["peak_ceiling_if_budget_lifted"] == 0.72
    assert record["verdict"] == "BUDGET_BOUND"
    assert record["next_bar"] == 0.40
    assert record["budget_gap"] == 0.32


def test_a_peak_with_a_dead_final_cycle_is_decay_dominated_not_axis_dead():
    record = tbc.analyse(_rows(0.5833, 0.5833, final=0.0, theories=(7, 12, 12)))
    assert record["verdict"] == "DECAY_DOMINATED"
    assert record["peak_ceiling_at_shipped_budget"] == 0.5833
    assert record["final_cycle_coverage_at_shipped_budget"] == 0.0
    assert record["next_bar"] == 0.5833
    assert "peak" in record["next_bar_endpoint"]


def test_a_budget_that_does_not_move_peak_coverage_is_world_bound():
    record = tbc.analyse(_rows(0.55, 0.56))
    assert record["verdict"] == "WORLD_BOUND"
    assert record["next_bar"] == 0.55


def test_an_identical_arm_with_no_cap_binding_is_an_axis_defect():
    record = tbc.analyse(_rows(0.50, 0.50, theories=(4, 6, 7)))
    assert record["verdict"] == "AXIS_DEAD"


def test_a_zero_with_no_stable_edge_anywhere_names_the_filter_not_the_budget():
    rows = _rows(0.0, 0.0, final=0.0, theories=(7, 12, 12), )
    for row in rows:
        row["stable_final"] = 0
        row["stable_peak"] = 0
    record = tbc.analyse(rows)
    assert record["max_stable_edge_any_cell"] == 0
    assert record["verdict"] == "NO_STABLE_EDGES"
    assert "strength filter" in tbc.render(record)


def test_a_wrong_degree_is_a_gate_failure():
    rows = _rows(0.40, 0.72)
    rows[-1] = dict(rows[-1], realised_degree=6)
    record = tbc.analyse(rows)
    assert any("realised degree" in failure for failure in record["failures"])


def test_a_bar_above_the_measured_ceiling_is_rejected():
    record = tbc.analyse(_rows(0.40, 0.72))
    found = tbc.problems(dict(record, next_bar=0.55))
    assert any("exceeds the measured peak ceiling" in message for message in found), found


def test_a_decay_verdict_with_a_live_final_cycle_is_rejected():
    record = tbc.analyse(_rows(0.40, 0.72))
    found = tbc.problems(dict(record, verdict="DECAY_DOMINATED"))
    assert any("final cycle is not zero" in message for message in found), found


def test_an_unmeasurable_cell_is_named_not_scored_as_zero():
    rows = _rows(0.40, 0.72)
    rows[0] = dict(rows[0], coverage=None)
    record = tbc.analyse(rows)
    assert any("not measurable" in failure for failure in record["failures"])


def test_the_rendered_page_states_both_endpoints():
    record = tbc.analyse(_rows(0.5833, 0.5833, final=0.0, theories=(7, 12, 12)))
    page = tbc.render(record)
    assert "0.5833" in page and "median peak coverage" in page
    assert "{" not in page and "}" not in page
