"""The A1 pre-freeze machinery: U ordering, target selection and target-set checks."""
import inspect

from benchmarks import a1_arms
from benchmarks import a1_target_selection as selection
from benchmarks import a1_two_path


def test_cycle_36_u_is_sampled_before_consolidation():
    source = inspect.getsource(a1_arms.run_cell)
    assert source.index("pending_u = sample_u(") < source.index("report = service.run_sleep_cycle()")


def test_u_row_reports_direct_reverse_and_strength():
    class Memory:
        def temporal_edges(self, min_count=1):
            assert min_count == 1
            return [("a", "b", 3), ("b", "a", 2)]

    row = a1_arms.sample_u(Memory(), {("a", "b")}, 36)[("a", "b")]
    assert row == {
        "direct_count": 3,
        "reverse_count": 2,
        "strength": 5,
        "measured_cycle": 36,
    }


def test_selection_is_deterministic_and_magnitude_blind():
    universe = {
        ("a", "b"), ("b", "a"), ("c", "d"), ("d", "c"),
        ("e", "f"), ("f", "e"), ("g", "h"), ("h", "g"),
    }
    candidates = selection.candidate_edges(7, universe)
    assert candidates == selection.candidate_edges(7, universe)
    temporal = {
        "a": {"b": 1}, "b": {"a": 1},
        "c": {"d": 1}, "d": {"c": 1},
        "e": {"f": 1}, "f": {"e": 1},
        "g": {"h": 1}, "h": {"g": 1},
    }
    members = selection.cycle_members(temporal, candidates)
    u = {edge: selection._u_row(temporal, edge, 36) for edge in candidates}
    first, _ = selection.select_edges(7, candidates, u, members)
    bigger = {edge: dict(value, strength=value["strength"] + 100) for edge, value in u.items()}
    second, _ = selection.select_edges(7, candidates, bigger, members)
    assert first == second
    assert len(first) == 4


def test_selection_refuses_to_reduce_below_n():
    universe = {("a", "b"), ("b", "a"), ("c", "d"), ("d", "c"), ("e", "f"), ("f", "e")}
    candidates = selection.candidate_edges(7, universe)
    temporal = {"a": {"b": 1}, "b": {"a": 1}, "c": {"d": 1}, "d": {"c": 1},
                "e": {"f": 1}, "f": {"e": 1}}
    members = selection.cycle_members(temporal, candidates)
    u = {edge: selection._u_row(temporal, edge, 36) for edge in candidates}
    selected, _ = selection.select_edges(7, candidates, u, members)
    assert selected == []


def test_target_set_problems_accepts_four_disjoint_world_edges():
    doc = a1_two_path.manifest()
    doc["targets"]["status"] = "FIXED BEFORE FREEZE"
    doc["targets"]["by_seed"] = {
        str(seed): a1_two_path._artifact_targets(seed) for seed in a1_two_path.SEEDS
    }
    assert a1_two_path.target_set_problems(doc) == []


def test_target_set_problems_rejects_short_and_overlapping_sets():
    doc = a1_two_path.manifest()
    doc["targets"]["status"] = "FIXED BEFORE FREEZE"
    doc["targets"]["by_seed"] = {
        str(seed): a1_two_path._artifact_targets(seed) for seed in a1_two_path.SEEDS
    }
    first_seed = str(a1_two_path.SEEDS[0])
    doc["targets"]["by_seed"][first_seed] = doc["targets"]["by_seed"][first_seed][:3]
    problems = a1_two_path.target_set_problems(doc)
    assert any("does not have 4 targets" in problem for problem in problems)

    doc["targets"]["by_seed"] = {
        str(seed): a1_two_path._artifact_targets(seed) for seed in a1_two_path.SEEDS
    }
    edges = doc["targets"]["by_seed"][first_seed]
    a, _ = edges[0].split(">", 1)
    _, b = edges[1].split(">", 1)
    doc["targets"]["by_seed"][first_seed][1] = "%s>%s" % (a, b)
    problems = a1_two_path.target_set_problems(doc)
    assert any("disjoint" in problem for problem in problems)


def test_selection_self_test():
    assert selection.self_test() == []


def test_selection_artifact_is_internally_consistent():
    import json
    doc = json.loads(selection.OUT_PATH.read_text(encoding="utf-8"))
    assert selection.problems(doc) == []
    assert sum(len(row["selected"]) for row in doc["per_seed"].values()) == 24


def test_adversarial_audit_artifact_is_current():
    import json
    from benchmarks import a1_adversarial_audit as audit
    doc = json.loads(audit.OUT_PATH.read_text(encoding="utf-8"))
    assert audit.problems(doc) == []
    assert audit.PAGE_PATH.read_text(encoding="utf-8") == audit.render(doc)


def test_power_review_artifact_is_current():
    import json
    from benchmarks import a1_power_review as review
    doc = json.loads(review.OUT_PATH.read_text(encoding="utf-8"))
    assert review.problems(doc) == []
    assert review.PAGE_PATH.read_text(encoding="utf-8") == review.render(doc)
    assert doc["path_selection"]["selected"] == "A"
    assert doc["path_selection"]["target_sets"] == "DRAFT — NOT FROZEN"
    assert doc["freeze_decision"]["path"] == "A"
    assert doc["freeze_decision"]["provisional_freeze_draft"]["status"] == "DRAFT — NOT DECIDED"
    assert doc["freeze_decision"]["owner_decision_memo_draft"]["status"] == "DRAFT — AWAITING OWNER SIGNATURE"


def test_path_a_is_recorded_in_protocol_and_freeze_log():
    from pathlib import Path
    protocol = Path("docs/A1-TARGET-SELECTION-PROTOCOL.md").read_text(encoding="utf-8")
    review = Path("docs/A1-POWER-REVIEW.md").read_text(encoding="utf-8")
    assert "Path A selected (2026-11-14)" in protocol
    assert "Path A — recorded (2026-11-14)" in review
    assert "TARGET SETS STILL DRAFT" in review
    assert "Path B is not selected" in review


def test_owner_decision_memo_is_unsigned_and_records_both_decisions():
    import json
    from pathlib import Path

    doc = json.loads(Path("docs/a1_owner_decision_memo.json").read_text(encoding="utf-8"))
    assert doc["status"] == "DRAFT — AWAITING OWNER SIGNATURE; NO FREEZE, NO GRANT, NO RUN"
    assert doc["signed"] is False
    assert doc["effective_date"] is None
    assert doc["path_a"]["selected"] == "A"
    assert doc["path_a"]["target_sets"] == "DRAFT — NOT FROZEN"
    assert doc["c1_c4"]["ordering"] == "POST-FREEZE VOID GATE"
    assert doc["c1_c4"]["not_ordering"] == "PRE-FREEZE ADMISSIBILITY GATE"
    assert doc["current_state"]["grant"] == "NOT ISSUED"
    assert doc["current_state"]["run"] == "NOT STARTED"
    assert any(item["id"] == "c1_c4_ordering" for item in doc["decisions"])
    assert any(item["id"] == "path_a" for item in doc["decisions"])

    page = Path("docs/DECISION-A1-PATH-A-C1-C4.md").read_text(encoding="utf-8")
    assert "C1/C4 are post-freeze validity gates, not pre-freeze admissibility gates" in page
    assert "freeze → grant → run → measure C1/C4 → PASS or VOID" in page
    assert "**Signature and date:**" in page
    assert "A1 VOID — C1/C4" in page


def test_provisional_freeze_gate_order_is_draft_only():
    import json
    from pathlib import Path

    doc = json.loads(Path("docs/a1_provisional_freeze_gate_order.json").read_text(encoding="utf-8"))
    assert doc["status"] == "DRAFT — NOT DECIDED; NO FREEZE, NO GRANT, NO RUN"
    freeze = doc["provisional_freeze"]
    assert freeze["status"] == "PROPOSED — NOT ADOPTED"
    assert freeze["evidentiary_status_only"] is True
    assert freeze["target_identity_final_after_freeze"] is True
    assert freeze["revocable_after_outcome"] is False
    assert freeze["licenses_retry"] is False
    assert freeze["reserves_seeds"] is False
    assert len(doc["gate_order"]) == 6
    assert "provisional freeze" in doc["gate_order"][1]
    assert any(row["reason_code"] == "C4_DELTA" for row in doc["void_conditions"])
    assert doc["report_shape"]["model"] is None

    page = Path("docs/A1-PROVISIONAL-FREEZE-GATE-ORDER.md").read_text(encoding="utf-8")
    assert "provisional in its evidentiary status, not in its target identity" in page
    assert "does not unfreeze the targets" in page
    assert "A1 VOID — C1/C4" in page
    assert "NOT ADJUDICATED — RUN VOID" in page


def test_power_review_curve_states_retention_assumptions():
    import json
    from benchmarks import a1_power_review as review

    doc = json.loads(review.OUT_PATH.read_text(encoding="utf-8"))
    curve = doc["c1_power_curve"]
    assert curve["status"] == "REFERENCE CURVE — NOT AN OBSERVED DENOMINATOR OR RESULT"
    assert curve["assumed_retention_rates"] == [0.95, 0.97, 0.98, 1.0]
    assert curve["denominators"] == [4, 20, 56, 59, 60, 63, 64]
    assert curve["minimum_denominator_for_one_loss"] == 20
    rows = {(row["denominator"], row["assumed_retention"]): row
            for row in curve["rows"]}
    assert len(rows) == 28
    for row in rows.values():
        assert abs(row["per_seed"] - row["per_arm"] ** 2) <= 1e-5
        assert abs(row["all_six_seeds"] - row["per_seed"] ** 6) <= 1e-5
    assert rows[(63, 0.95)]["all_six_seeds"] == 0.002807
    assert rows[(63, 0.98)]["all_six_seeds"] == 0.631767
    impact = {row["denominator"]: row for row in curve["denominator_impact"]}
    assert set(impact) == set(curve["denominators"])
    assert impact[59]["allowed_losses"] == 2
    assert impact[60]["allowed_losses"] == 3
    assert impact[60]["effective_floor"] == 0.95
    assert curve["cliff_60"]["from"] == 59
    assert curve["cliff_60"]["to"] == 60
    assert curve["cliff_60"]["all_six_ratio"] == 138.69
    required = curve["required_retention"]["rows"]
    assert [row["target_all_six"] for row in required] == [0.5, 0.8, 0.9, 0.95]
    assert required[1]["required_q_by_denominator"]["63"] == 0.984017
    floor = curve["denominator_floor_rule"]
    assert floor["status"] == "PROPOSED — NOT ADOPTED"
    assert floor["floor"] == 60
    assert floor["planned_range"] == [63, 64]
    assert any(row["disposition"] == "VOID — C1_DENOMINATOR_BELOW_FLOOR"
               for row in floor["table"])
