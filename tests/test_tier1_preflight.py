"""The Tier-1 pre-flight must be able to pass, block, and fail for the stated reasons."""
import json

from benchmarks import force_matrix as fm
from benchmarks import tier1_preflight as tp


def test_a_dead_campaign_stimulus_blocks_the_campaign():
    trace = {"design": "L1_hub1_t3_disjoint", "horizon": 3000, "cycles_run": 39,
             "peak": 5, "first_zero_cycle": 39, "alive_at_horizon": False,
             "theory_counts": [0] + [5] * 38}
    assert fm.persistence_verdict(trace) == "NOT_MEASURABLE_AS_DESIGNED"
    assert tp.decide([], fm.persistence_verdict(trace)) == "CAMPAIGN_NOT_MEASURABLE"


def test_an_arm_alive_at_the_horizon_passes():
    trace = {"horizon": 40, "peak": 4, "first_zero_cycle": None,
             "alive_at_horizon": True, "theory_counts": [4] * 40}
    assert fm.persistence_verdict(trace) == "ALIVE_AT_HORIZON"
    assert tp.decide([], "ALIVE_AT_HORIZON") == "PASSES"


def test_an_arm_that_never_forms_is_broken_not_merely_dead():
    trace = {"horizon": 40, "peak": 0, "first_zero_cycle": None,
             "alive_at_horizon": False, "theory_counts": [0] * 40}
    assert fm.persistence_verdict(trace) == "REFERENCE_ARM_BROKEN"
    assert tp.decide([], "REFERENCE_ARM_BROKEN") == "REFERENCE_ARM_BROKEN"


def test_a_witness_problem_fails_g1_whatever_persistence_says():
    assert tp.decide(["NO_DREAMS produced a dream"], "ALIVE_AT_HORIZON") == "G1_FAILS"


def test_the_reference_arm_is_read_from_the_trace_not_the_last_cycle():
    plateau_then_dead = [{"colony": "FULL", "theories": 0,
                          "series": {"theories": [4] * 36 + [3, 0, 0, 0]}}]
    assert fm.reference_arm_problems(plateau_then_dead) == []
    never = [{"colony": "FULL", "theories": 0, "series": {"theories": [0] * 40}}]
    assert "no theories in any cycle" in fm.reference_arm_problems(never)[0]


def test_a_negative_control_that_stops_suppressing_fails():
    bad = [{"colony": "NO_DREAMS", "series": {"dreams": [0, 0, 1, 0]}},
           {"colony": "NO_QUESTIONS", "series": {"questions": [0, 0, 0, 0]}}]
    problems = fm.negative_control_problems(bad)
    assert problems and "NO_DREAMS" in problems[0]
    good = [{"colony": "NO_DREAMS", "series": {"dreams": [0, 0, 0]}},
            {"colony": "NO_QUESTIONS", "series": {"questions": [0, 0, 0]}}]
    assert fm.negative_control_problems(good) == []


def test_the_page_and_the_verdict_match_the_artifact():
    record = json.loads(tp.ARTIFACT.read_text(encoding="utf-8"))
    assert record["verdict"] in tp.VERDICTS
    assert record["launch_blocked"] == (record["verdict"] != "PASSES")
    assert tp.PAGE.read_text(encoding="utf-8") == tp.render_page(record)
    assert record["negative_controls"]["passed"] is (
        not record["negative_controls"]["problems"])
    assert record["persistence"]["verdict"] == fm.persistence_verdict(
        record["campaign_stimulus"])
