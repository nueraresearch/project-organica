"""The A1 pre-freeze machinery: U ordering, target selection and target-set checks."""
import inspect
import re
from pathlib import Path

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


def _n20_target_doc():
    import json
    act = json.loads(Path("docs/a1_target_freeze_act_n20.json").read_text(encoding="utf-8"))
    doc = a1_two_path.manifest()
    doc["targets"].update({
        "status": "FIXED BEFORE FREEZE",
        "protocol": a1_two_path.C8_TARGET_PROTOCOL,
        "n_per_seed": a1_two_path.C8_TARGET_N,
        "disjoint": False,
        "max_endpoint_degree": a1_two_path.C8_MAX_ENDPOINT_DEGREE,
        "selection_artifact": a1_two_path.C8_TARGET_SELECTION_PATH.relative_to(
            a1_two_path.ROOT).as_posix(),
        "by_seed": act["targets_by_seed"],
    })
    return doc


def test_target_set_problems_accepts_n20_degree_three_world_edges():
    doc = _n20_target_doc()
    assert a1_two_path.target_set_problems(doc) == []


def test_target_set_problems_rejects_n20_degree_and_duplicate_targets():
    doc = _n20_target_doc()
    doc["targets"]["max_endpoint_degree"] = 2
    problems = a1_two_path.target_set_problems(doc)
    assert any("endpoint-degree cap" in problem for problem in problems)

    doc = _n20_target_doc()
    first_seed = str(a1_two_path.SEEDS[0])
    edges = doc["targets"]["by_seed"][first_seed]
    edges[-1] = edges[0]
    problems = a1_two_path.target_set_problems(doc)
    assert any("repeats a target edge" in problem for problem in problems)


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
    assert doc["freeze_decision"]["provisional_freeze_draft"]["status"] == "DRAFT — PROVISIONAL FREEZE ONLY"
    assert doc["freeze_decision"]["owner_decision_memo_draft"]["status"] == "DRAFT — C1/C4 GATE ADOPTED ELSEWHERE"
    assert doc["freeze_decision"]["target_freeze_act_draft"]["status"] == "DRAFT — AWAITING OWNER SIGNATURE; NOT FROZEN"


def test_path_a_is_recorded_in_protocol_and_freeze_log():
    from pathlib import Path
    protocol = Path("docs/A1-TARGET-SELECTION-PROTOCOL.md").read_text(encoding="utf-8")
    review = Path("docs/A1-POWER-REVIEW.md").read_text(encoding="utf-8")
    assert "Path A selected (2026-11-14)" in protocol
    assert "Path A — recorded (2026-11-14)" in review
    assert "TARGET SETS STILL DRAFT" in review
    assert "Path B is not selected" in review


def test_owner_decision_memo_is_unsigned_and_records_remaining_decisions():
    import json
    from pathlib import Path

    doc = json.loads(Path("docs/a1_owner_decision_memo.json").read_text(encoding="utf-8"))
    assert doc["status"] == (
        "DRAFT — C1/C4 GATE ADOPTED ELSEWHERE; "
        "PATH A CONFIRMATION AND PROVISIONAL FREEZE NOT ADOPTED"
    )
    assert doc["signed"] is False
    assert doc["effective_date"] is None
    assert doc["path_a"]["selected"] == "A"
    assert doc["path_a"]["target_sets"] == "DRAFT — NOT FROZEN"
    assert doc["c1_c4"]["ordering"] == "POST-FREEZE VOID GATE"
    assert doc["c1_c4"]["not_ordering"] == "PRE-FREEZE ADMISSIBILITY GATE"
    assert doc["c1_c4"]["status"] == "ADOPTED — BINDING FOR A1; RECORDED SEPARATELY"
    assert doc["c1_c4_adopted_separately"]["record"] == "docs/A1-C1-C4-VOID-GATE.md"
    assert doc["denominator_floor"]["adopted_by"] == "A1-C1-C4-VOID-GATE-1"
    assert doc["current_state"]["grant"] == "NOT ISSUED"
    assert doc["current_state"]["run"] == "NOT STARTED"
    assert doc["current_state"]["c1_c4_ordering"] == "ADOPTED — A1-C1-C4-VOID-GATE-1"
    assert any(item["id"] == "c1_c4_ordering" for item in doc["decisions"])
    assert any(item["id"] == "path_a" for item in doc["decisions"])

    page = Path("docs/DECISION-A1-PATH-A-C1-C4.md").read_text(encoding="utf-8")
    assert "C1/C4 are post-freeze validity gates, not pre-freeze admissibility gates" in page
    assert "freeze → grant → run → measure C1/C4 → PASS or VOID" in page
    assert "**Signature and date:**" in page
    assert "A1 VOID — C1/C4" in page


def test_target_freeze_act_is_prepared_not_executed():
    import json
    from pathlib import Path

    act = json.loads(Path("docs/a1_target_freeze_act.json").read_text(encoding="utf-8"))
    artifact = json.loads(Path("docs/a1_target_selection.json").read_text(encoding="utf-8"))
    by_seed = {seed: row["selected"] for seed, row in artifact["per_seed"].items()}

    assert act["status"] == "DRAFT — AWAITING OWNER SIGNATURE; NOT FROZEN; NO GRANT, NO RUN"
    assert act["signed"] is False
    assert act["path"] == "A"
    assert act["targets_by_seed"] == by_seed
    assert act["target_count"] == 24
    assert act["unique_target_edges"] == 23
    assert act["checks"]["target_set_problems"] == []
    import hashlib
    artifact_bytes = Path("docs/a1_target_selection.json").read_bytes()
    assert act["selection_artifact_digest"] == hashlib.sha256(artifact_bytes).hexdigest()
    assert act["manifest_frozen_after_signature"] is True
    assert act["grant_after_signature"] == "NOT ISSUED"
    assert act["run_after_signature"] == "NOT STARTED"
    assert act["current_manifest_frozen"] is False

    manifest = json.loads(Path("docs/a1_two_path_manifest.json").read_text(encoding="utf-8"))
    assert manifest["frozen"] is False
    assert manifest["targets"]["status"].startswith("UNRESOLVED")
    assert manifest["seed_block"]["status"].startswith("PROVISIONAL")
    assert manifest["authorisation"]["granted"] is False

    from benchmarks import a1_two_path
    check = a1_two_path.manifest()
    check["targets"]["status"] = "FIXED BEFORE FREEZE"
    check["targets"]["by_seed"] = by_seed
    assert a1_two_path.target_set_problems(check) == []

    from benchmarks.presence_cap_experiment import seed_collisions
    allow = (a1_two_path.MANIFEST_PATH, a1_two_path.TARGET_SELECTION_PATH,
             a1_two_path.C8_TARGET_SELECTION_PATH, a1_two_path.C8_EXPANSION_PATH,
             a1_two_path.ADVERSARIAL_AUDIT_PATH, a1_two_path.POWER_REVIEW_PATH,
             a1_two_path.C5_TIMING_PATH, a1_two_path.TARGET_FREEZE_ACT_PATH,
             a1_two_path.N20_TARGET_FREEZE_ACT_PATH,
             a1_two_path.BASELINE_AVAILABILITY_PATH,
             a1_two_path.TARGET_VIABILITY_PATH,
             a1_two_path.DESIGN_VIABILITY_PATH,
             a1_two_path.N20_COMPETENT_PREREG_PATH,
             a1_two_path.K_DECOMPOSITION_PATH,
             a1_two_path.SUCCESSOR_PREFLIGHT_PATH,
             a1_two_path.SUCCESSOR_CANDIDATE_PATH,
             a1_two_path.LARGER_UNIVERSE_CANDIDATE_PATH,
             a1_two_path.LARGER_UNIVERSE_PREFLIGHT_PATH)
    assert seed_collisions(list(a1_two_path.SEEDS), allow=allow) == {}

    page = Path("docs/A1-TARGET-FREEZE-ACT.md").read_text(encoding="utf-8")
    assert "**Signature and date:**" in page
    assert "NO GRANT, NO RUN" in page
    assert "FIXED BEFORE FREEZE" in page


def test_n20_target_freeze_act_preserves_targets_and_prepares_c8():
    import hashlib
    import json
    from pathlib import Path

    act = json.loads(Path("docs/a1_target_freeze_act_n20.json").read_text(encoding="utf-8"))
    c20 = json.loads(Path("docs/a1_c8_target_selection.json").read_text(encoding="utf-8"))
    c4 = json.loads(Path("docs/a1_target_selection.json").read_text(encoding="utf-8"))
    by_seed = {seed: row["selected"] for seed, row in c20["per_seed"].items()}
    current = {seed: row["selected"] for seed, row in c4["per_seed"].items()}

    assert act["kind"] == "a1_target_freeze_act_n20"
    assert act["id"] == "A1-TARGET-FREEZE-N20-1"
    assert act["status"].startswith("DRAFT — C5 TARGET TIMING CLEARED BY EARLIER-U")
    assert act["signed"] is False
    assert act["path"] == "A"
    assert act["n_per_seed"] == 20
    assert act["disjoint"] is False
    assert act["max_endpoint_degree"] == 3
    assert act["threshold"] == 0.05
    assert act["threshold_changed"] is False
    assert act["targets_by_seed"] == by_seed
    assert act["target_count"] == 120
    assert act["unique_target_edges"] == 104
    assert act["current_target_count"] == 24
    assert act["current_unique_target_edges"] == 23
    assert act["current_targets_retained"] is True
    assert act["superset_of_current_targets"] is True
    for seed, selected in by_seed.items():
        assert len(selected) == 20
        assert len(set(selected)) == 20
        assert set(current[seed]) <= set(selected)
        assert act["per_seed"][seed]["retained_count"] == 4
        assert act["per_seed"][seed]["new_count"] == 16
        assert act["per_seed"][seed]["max_endpoint_degree"] == 3
        assert act["per_seed"][seed]["selection_digest"] == c20["per_seed"][seed]["selection_digest"]
        assert act["new_targets_by_seed"][seed] == [
            edge for edge in selected if edge not in current[seed]
        ]

    digest = hashlib.sha256(Path("docs/a1_c8_target_selection.json").read_bytes()).hexdigest()
    assert act["selection_artifact_digest"] == digest
    assert act["design"]["selection_artifact_digest"] == digest
    assert act["c8_resolution"]["status"] == "RESOLVED BY THIS ACT IF SIGNED"
    assert act["c8_resolution"]["rows_per_seed"] == 20
    assert act["c8_resolution"]["step"] == 0.05
    assert act["c8_resolution"]["threshold"] == 0.05
    assert act["c8_resolution"]["threshold_changed"] is False
    assert act["c8_resolution"]["adjudicable_after_signature"] is True
    assert act["c7_c1_c4_effect"]["C7_status"].startswith("UNCHANGED")
    assert act["c7_c1_c4_effect"]["C1_target_only_status"].startswith("STILL BELOW")
    assert act["blocking_preconditions"] == []
    blockers = {row["id"] for row in act["preconditions"] if row["blocking"]}
    assert blockers == set()
    assert act["c5_timing"]["status"].startswith("PASS")
    assert act["c5_timing"]["u_cycle"] == 4
    assert act["c5_timing"]["earliest_current_carrier_cycle"] == 5
    assert act["c5_timing"]["current_carriers_before_u"] == 0
    assert act["c5_timing"]["current_targets_preserved"] is True
    assert act["checks"]["target_set_problems"].startswith("PASS")
    assert act["current_manifest"]["frozen"] is False
    assert act["current_manifest"]["n_per_seed"] == 4
    assert act["manifest_frozen_after_signature"] is True
    assert act["grant_after_signature"] == "NOT ISSUED"
    assert act["run_after_signature"] == "NOT STARTED"

    page = Path("docs/A1-TARGET-FREEZE-ACT-N20.md").read_text(encoding="utf-8")
    assert "**Signature and date:**" in page
    assert "A1-C8-EXPANSION-1" in page
    assert "C5 TARGET TIMING CLEARED BY EARLIER-U" in page
    assert "C5: earlier `U` before carrier, K and Y" in page
    assert "1/20 = 0.05" in page
    assert "N=20 target validation" in page


def test_n20_target_freeze_act_applies_to_manifest_validator():
    assert a1_two_path.target_set_problems(_n20_target_doc()) == []


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
    from pathlib import Path

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
    power = curve["power_design_criterion"]
    assert power["status"] == (
        "RECORDED — C1 DESIGN CRITERION; NOT AN OBSERVED RETENTION "
        "AND NOT A SECOND ACCEPTANCE GATE"
    )
    assert power["target_all_six_power"] == 0.8
    assert power["reference_denominator"] == 63
    assert power["denominator_kind"].startswith("UPPER BOUND")
    assert power["observed_baseline_available_rows"] is None
    assert power["required_retention"] == required[1]["required_q_by_denominator"]["63"]
    assert power["required_retention_by_denominator"]["64"] == 0.984271
    assert power["required_retention_by_denominator"]["60"] == 0.983204
    assert power["not_a_second_acceptance_gate"] is True
    floor = curve["denominator_floor_rule"]
    assert floor["status"] == "ADOPTED — BINDING FOR A1"
    assert floor["floor"] == 60
    assert floor["minimum_denominator"] == 60
    assert floor["allowed_losses_at_60_64"] == 3
    assert floor["below_floor_disposition"] == "VOID — C1_DENOMINATOR_BELOW_FLOOR"
    assert floor["planned_range"] == [63, 64]
    assert any(row["disposition"] == "VOID — C1_DENOMINATOR_BELOW_FLOOR"
               for row in floor["table"])
    corr = curve["correlation_sensitivity"]
    assert corr["status"] == "SENSITIVITY — NOT AN OBSERVED CORRELATION OR RESULT"
    assert corr["reference_denominator"] == 63
    assert corr["rho_values"] == [0.0, 0.25, 0.5, 0.75, 0.95]
    assert len(corr["path_rows"]) == 10
    assert len(corr["seed_rows"]) == 10
    assert len(corr["joint_rows"]) == 6
    for row in corr["path_rows"] + corr["seed_rows"] + corr["joint_rows"]:
        for key in ("per_seed", "all_six_seeds"):
            assert 0.0 <= row[key] <= 1.0
    headline = corr["headline"]["at_63_q095"]
    assert headline["path_rho_0_5"]["per_seed"] > headline["independent"]["per_seed"]
    assert headline["seed_rho_0_5"]["all_six_seeds"] > headline["independent"]["all_six_seeds"]
    assert headline["joint_rho_0_5"]["all_six_seeds"] > headline["seed_rho_0_5"]["all_six_seeds"]
    page = Path("docs/A1-POWER-REVIEW.md").read_text(encoding="utf-8")
    assert "### Correlation sensitivity" in page
    assert "rho_paths" in page and "rho_seeds" in page
    assert "C1 power-design criterion" in page
    assert "80%" in page and "q=0.984017" in page


def test_path_a_and_c1_rule_are_recorded_without_a_run():
    import json
    from pathlib import Path

    doc = json.loads(Path("docs/a1_path_a_c1_rule.json").read_text(encoding="utf-8"))
    assert doc["status"] == "RECORDED — BINDING FOR A1; NO FREEZE, NO GRANT, NO RUN"
    assert doc["adopted_together"]["record"] == "docs/A1-C1-C4-VOID-GATE.md"
    assert doc["adopted_together"]["date"] == "2026-11-14"
    assert doc["adopted_together"]["status"] == "ADOPTED — BINDING FOR A1"
    assert "60-row denominator floor" in doc["adopted_together"]["scope"]
    assert doc["current_state"]["c1_c4_gate"].startswith("ADOPTED")
    assert doc["current_state"]["denominator_floor"].startswith("ADOPTED")
    assert doc["path_a"]["selected"] == "A"
    assert doc["path_a"]["target_sets"] == "DRAFT — NOT FROZEN"
    rule = doc["c1_acceptance_rule"]
    assert rule["threshold"] == 0.95
    assert rule["minimum_denominator"] == 60
    assert rule["allowed_losses_at_60_64"] == 3
    assert rule["below_floor_disposition"] == "VOID — C1_DENOMINATOR_BELOW_FLOOR"
    assert rule["zero_denominator_disposition"] == "VOID — C1_NO_DENOMINATOR"
    power = rule["power_design_criterion"]
    assert power["status"] == (
        "RECORDED — C1 DESIGN CRITERION; NOT AN OBSERVED RETENTION "
        "AND NOT A SECOND ACCEPTANCE GATE"
    )
    assert power["target_all_six_power"] == 0.8
    assert power["reference_denominator"] == 63
    assert power["denominator_kind"].startswith("UPPER BOUND")
    assert power["observed_baseline_available_rows"] is None
    assert doc["planned_range_kind"].startswith("UPPER BOUND")
    assert power["required_retention"] == 0.984017
    assert power["required_retention_by_denominator"]["64"] == 0.984271
    assert power["not_a_second_acceptance_gate"] is True
    table = {row["observed_min"]: row for row in rule["table"]}
    assert table["59" if "59" in table else "20-59"]["disposition"] == "VOID — C1_DENOMINATOR_BELOW_FLOOR"
    assert table["60"]["required_retained"] == 57
    assert table["64"]["required_retained"] == 61
    assert doc["current_state"]["grant"] == "NOT ISSUED"
    assert doc["current_state"]["run"] == "NOT STARTED"
    assert doc["current_state"]["observed_c1"] == "NONE"

    page = Path("docs/DECISION-A1-PATH-A-C1-RULE.md").read_text(encoding="utf-8")
    assert "| Minimum denominator | **60 rows** |" in page
    assert "VOID — C1_DENOMINATOR_BELOW_FLOOR" in page
    assert "A perfect **59/59** is still VOID" in page
    assert "80% all-six-seed power target" in page
    assert "**0.984017**" in page


def test_c1_denominator_feasibility_risk_is_recorded_as_an_upper_bound():
    import json
    from benchmarks import a1_power_review as review

    doc = json.loads(review.OUT_PATH.read_text(encoding="utf-8"))
    risk = doc["c1_denominator_feasibility"]
    assert risk["status"] == "RISK RECORDED — UNMEASURED; 63-64 IS AN UPPER BOUND"
    assert risk["planned_range"] == [63, 64]
    assert risk["denominator_kind"].startswith("UPPER BOUND")
    assert risk["observed_baseline_available_rows"] is None
    assert risk["floor"] == 60
    assert risk["below_floor_disposition"] == "VOID — C1_DENOMINATOR_BELOW_FLOOR"
    budget = risk["availability_budget"]
    assert budget["floor"] == 60
    expected_budget = {
        "20630101": (64, 4),
        "20630102": (63, 3),
        "20630103": (64, 4),
        "20630104": (64, 4),
        "20630105": (64, 4),
        "20630106": (63, 3),
    }
    for seed, (rows, unavailable) in expected_budget.items():
        row = budget["by_seed"][seed]
        assert row["candidate_rows"] == rows
        assert row["max_unavailable_rows"] == unavailable
        assert row["required_availability_fraction"] == round(60 / rows, 6)
    unrelated = risk["unrelated_observations"]
    assert unrelated["forbidden_use"] == "BASELINE-AVAILABILITY PROXY"
    c6 = next(finding for finding in doc["findings"]
              if finding["id"] == "c6_prevalence_observation")
    assert c6["not_baseline_availability_proxy"] is True
    page = review.PAGE_PATH.read_text(encoding="utf-8")
    assert "C1 denominator-feasibility risk note" in page
    assert "63–64" in page and "upper bound" in page
    assert "not baseline-availability proxies" in page


_PROXY_WORD = re.compile(r"\bprox(?:y|ies)\b", re.IGNORECASE)
_PROXY_SUBJECT = re.compile(r"\bC6\b|\bA0\b|\bprevalence\b", re.IGNORECASE)
_PROXY_DENIAL = re.compile(r"\b(?:not|no|never|without|forbidden)\b", re.IGNORECASE)
_UNRELEASED_MARKER = "## [0.15.0] — (unreleased)"


def _positive_proxy_claims(text):
    claims = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if (_PROXY_WORD.search(line) and _PROXY_SUBJECT.search(line)
                and not _PROXY_DENIAL.search(line)):
            claims.append((lineno, line.strip()))
    return claims


def scan_current_a1_proxy_claims(changelog_path=None, root=Path(".")):
    """Return positive C6/A0 proxy claims from current A1 documentation.

    Historical manual revision rows and historical changelog sections are not
    scanned. The current manual state and the unreleased 0.15.0 section are.
    """
    root = Path(root)
    manual_path = root / "docs/USER-MANUAL.md"
    manual = manual_path.read_text(encoding="utf-8")
    assert "**Revision log:**" in manual
    manual_current = manual.split("**Revision log:**", 1)[0]

    if changelog_path is None:
        changelog_path = root / "CHANGELOG.md"
    else:
        changelog_path = Path(changelog_path)
    changelog = changelog_path.read_text(encoding="utf-8")
    assert _UNRELEASED_MARKER in changelog
    unreleased = changelog.split(_UNRELEASED_MARKER, 1)[1]
    next_version = unreleased.find(chr(10) + "## [")
    assert next_version != -1
    unreleased = unreleased[:next_version]
    assert unreleased.strip()

    roadmap = root / "ROADMAP.md"
    documents = [(roadmap, roadmap.read_text(encoding="utf-8"))]
    documents += [(path, path.read_text(encoding="utf-8"))
                  for path in sorted((root / "docs").glob("A1-*.md"))]
    documents.append((manual_path, manual_current))
    documents.append((changelog_path, unreleased))

    offenders = []
    for path, text in documents:
        for lineno, line in _positive_proxy_claims(text):
            offenders.append(f"{path}:{lineno}: {line}")
    return offenders


def test_current_a1_docs_do_not_call_c6_or_a0_percentages_baseline_proxies():
    """Guard the current A1 record against reviving the old proxy wording."""
    # Prove the detector fires on the wording this guard exists to reject.
    assert _positive_proxy_claims(
        "C6 supplies a high K/Y_ind denominator; this is a proxy."
    )
    assert _positive_proxy_claims(
        "A0's hard-edge percentage is a baseline-availability proxy."
    )
    # And prove it does not flag the corrected negative wording.
    assert not _positive_proxy_claims(
        "C6 K/Y_ind rates are not baseline-availability proxies."
    )

    offenders = scan_current_a1_proxy_claims()
    assert not offenders, (
        "current A1 documentation presents C6/A0 percentages as "
        "baseline-availability proxies; use a negative, different-world "
        "characterization instead:\n" + "\n".join(offenders)
    )


def test_proxy_guard_fails_on_an_injected_positive_sentence(tmp_path):
    """The real scan, not only the helper, must reject a bad current changelog."""
    source = Path("CHANGELOG.md").read_text(encoding="utf-8")
    injected = source.replace(
        _UNRELEASED_MARKER,
        _UNRELEASED_MARKER
        + "\n\nC6 prevalence is a baseline-availability proxy for C1.\n",
        1,
    )
    assert injected != source
    temporary = tmp_path / "CHANGELOG.md"
    temporary.write_text(injected, encoding="utf-8")

    offenders = scan_current_a1_proxy_claims(changelog_path=temporary)
    assert any(str(temporary) in offender and "C6 prevalence" in offender
               for offender in offenders), offenders
