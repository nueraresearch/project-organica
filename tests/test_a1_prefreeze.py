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


def _n4_target_doc():
    """The N=4 protocol's own document. The live manifest now freezes the N=20 competent block, so the
    N=4 rules have to be exercised on a document that declares the N=4 size, not on whatever is frozen."""
    doc = a1_two_path.manifest()
    for key in ("n_min", "max_endpoint_degree", "selection_artifact_digest", "freeze_act",
                "freeze_act_id", "estimand", "current_targets_retained"):
        doc["targets"].pop(key, None)
    doc["targets"].update({
        "status": "FIXED BEFORE FREEZE",
        "protocol": a1_two_path.TARGET_PROTOCOL,
        "n_per_seed": a1_two_path.TARGET_N,
        "disjoint": True,
        "selection_artifact": "docs/a1_target_selection.json",
        "by_seed": {str(seed): a1_two_path._artifact_targets(seed)
                    for seed in a1_two_path.SEEDS},
    })
    return doc


def test_target_set_problems_accepts_four_disjoint_world_edges():
    assert a1_two_path.target_set_problems(_n4_target_doc()) == []


def test_target_set_problems_rejects_short_and_overlapping_sets():
    doc = _n4_target_doc()
    first_seed = str(a1_two_path.SEEDS[0])
    short = dict(doc["targets"]["by_seed"])
    short[first_seed] = short[first_seed][:3]
    doc["targets"]["by_seed"] = short
    problems = a1_two_path.target_set_problems(doc)
    assert any("does not have 4 targets" in problem for problem in problems), problems

    doc = _n4_target_doc()
    edges = list(doc["targets"]["by_seed"][first_seed])
    a, _ = edges[0].split(">", 1)
    _, b = edges[1].split(">", 1)
    edges[1] = "%s>%s" % (a, b)
    doc["targets"]["by_seed"][first_seed] = edges
    problems = a1_two_path.target_set_problems(doc)
    assert any("disjoint" in problem for problem in problems), problems


def _n20_target_doc():
    import json
    act = json.loads(Path("docs/a1_target_freeze_act_n20.json").read_text(encoding="utf-8"))
    doc = a1_two_path.manifest()
    doc["targets"].update({
        "status": "FIXED BEFORE FREEZE",
        "protocol": a1_two_path.C8_TARGET_PROTOCOL,
        "n_per_seed": a1_two_path.C8_TARGET_N,
        "n_min": act["n_min"],
        "disjoint": False,
        "max_endpoint_degree": a1_two_path.C8_MAX_ENDPOINT_DEGREE,
        "selection_artifact": act["selection_artifact"],
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
    import hashlib
    import json
    from pathlib import Path

    act = json.loads(Path("docs/a1_target_freeze_act.json").read_text(encoding="utf-8"))
    artifact = json.loads(Path("docs/a1_target_selection.json").read_text(encoding="utf-8"))
    by_seed = {seed: row["selected"] for seed, row in artifact["per_seed"].items()}

    # Re-issued for the adopted block: the act now describes the live selection,
    # and the superseded edition's tables are history, not restated data.
    assert act["status"].startswith("DRAFT")
    assert act["reissue"]["signed"] is False
    assert act["reissue"]["previous_edition_seed_block"] == [
        20630101, 20630102, 20630103, 20630104, 20630105, 20630106]
    assert act["reissue"]["current_seed_block"] == [
        20740101, 20740102, 20740103, 20740104, 20740105, 20740106]
    assert "supersession" not in act
    assert act["signed"] is False
    assert act["path"] == "A"
    assert act["targets_by_seed"] == by_seed
    assert set(act["targets_by_seed"]) == {
        str(seed) for seed in act["reissue"]["current_seed_block"]}
    assert act["target_count"] == sum(len(edges) for edges in by_seed.values())
    assert act["unique_target_edges"] == len(
        {edge for edges in by_seed.values() for edge in edges})
    for seed, row in artifact["per_seed"].items():
        assert act["per_seed"][seed]["selection_digest"] == row["selection_digest"]
        assert act["per_seed"][seed]["universe_digest"] == row["universe_digest"]
    assert act["checks"]["target_set_problems"] == []
    artifact_bytes = Path("docs/a1_target_selection.json").read_bytes()
    assert act["selection_artifact_digest"] == hashlib.sha256(
        artifact_bytes).hexdigest()
    assert act["manifest_frozen_after_signature"] is True
    assert act["grant_after_signature"] == "NOT ISSUED"
    assert act["run_after_signature"] == "NOT STARTED"
    assert act["manifest_frozen_after_signature"] is True
    assert act["blocking_preconditions"] == [
        "C2_C8_competence_rule", "C4_exposure_acceptance",
    ]

    viability = json.loads(Path("docs/a1_design_viability.json").read_text(encoding="utf-8"))
    recorded = {str(row["seed"]): row["max_attainable"]
                for row in viability["c1_ceiling"]["candidate_stream"]["per_seed"]}
    assert act["design_viability"]["recorded_c1_ceiling_by_seed"].keys() == recorded.keys()
    for seed, ceiling in recorded.items():
        assert act["design_viability"]["recorded_c1_ceiling_by_seed"][seed][
            "max_attainable"] == ceiling
    assert act["design_viability"]["floor"] == viability["c1_ceiling"]["floor"]
    assert act["design_viability"]["recorded_disposition"] == viability["disposition"]
    measured = act["design_viability"]["measured_for_adopted_block"]
    avail = json.loads(Path("docs/a1_baseline_availability_adopted.json").read_text(
        encoding="utf-8"))
    assert measured["id"] == avail["id"]
    for row in avail["per_seed"]:
        recorded = measured["per_seed"][str(row["seed"])]
        assert recorded["A_available"] == row["protocol"]["A_available"]
        assert recorded["max_attainable"] == row["protocol"]["c1_min_denominator"]
        assert recorded["reaches_floor"] is False
    assert act["design_viability"]["cleared"] is False
    assert act["design_viability"]["blocker_state"].startswith("RECONCILED")
    reconciliation = act["design_viability"]["denominator_reconciliation"]
    assert reconciliation["defined_by"].endswith("A1-TARGET-SELECTION-PROTOCOL.md")
    assert "non-target edges" in reconciliation["definition_quote"]
    measured = reconciliation["measured_under_the_protocol_definition"]
    assert measured["min"] == min(measured["denominator_by_seed"])
    assert measured["floor_reachable"] is True
    assert measured["floor_reachable"] != measured[
        "candidate_stream_for_comparison"]["floor_reachable"]
    assert reconciliation["what_this_does_not_establish"].startswith(
        "that C1 passes")
    assert act["design_viability"]["is_a_signature_blocker"] is True
    assert "C1 DENOMINATOR RECONCILED TO THE PROTOCOL" in act["status"]

    c5 = json.loads(Path("docs/a1_c5_target_timing.json").read_text(encoding="utf-8"))
    assert act["c5_timing"]["status"].startswith("PASS")
    assert act["c5_timing"]["u_cycle"] == c5["u_cycle"]
    assert act["c5_timing"]["earliest_observed_carrier_cycle"] == c5[
        "earliest_observed_carrier_cycle"]
    assert act["c5_timing"]["earliest_current_carrier_cycle"] == c5[
        "earliest_current_carrier_cycle"]
    assert act["c5_timing"]["current_carriers_before_u"] == 0

    manifest = json.loads(Path("docs/a1_two_path_manifest.json").read_text(encoding="utf-8"))
    # The N=20 act is signed and the manifest frozen on its block; the N=4 act itself remains a draft.
    assert manifest["frozen"] is True
    assert manifest["status"].startswith("GRANTED, RUN")
    assert manifest["targets"]["n_per_seed"] == 20
    assert act["status"].startswith("DRAFT")
    assert manifest["targets"]["status"].startswith("FIXED BEFORE FREEZE")
    assert manifest["seed_block"]["status"].startswith("PROVISIONAL")
    assert manifest["authorisation"]["granted"] is True
    assert manifest["authorisation"]["document"] == "docs/A1-GRANT.md"

    from benchmarks import a1_two_path
    check = _n4_target_doc()
    assert check["targets"]["by_seed"] == by_seed
    assert a1_two_path.target_set_problems(check) == []

    page = Path("docs/A1-TARGET-FREEZE-ACT.md").read_text(encoding="utf-8")
    assert "**Signature and date:**" in page
    assert "NO GRANT, NO RUN" in page
    assert "FIXED BEFORE FREEZE" in page
    assert "Re-issued 2026-11-15" in page
    assert "the floor is reachable" in page
    assert "used the planning quantity as though it were the scored one" in page
    assert "45 / 34 / 47 / 48 / 38 / 41" in page
    assert "Do not freeze or run the current A1 design" in page
    assert "79 / 64 / 79 / 74 / 72 / 74" in page
    assert "`20630101`" not in page

def test_n20_target_freeze_act_freezes_the_competent_block():
    """The act is signed on the block DECISION-A1-COMPETENT-ESTIMAND adopted, with its consequences stated."""
    import hashlib
    import json
    from pathlib import Path

    from benchmarks import a1_c5_competent_audit, a1_scorer_pin, a1_two_path

    act = json.loads(Path("docs/a1_target_freeze_act_n20.json").read_text(encoding="utf-8"))
    comp = json.loads(Path("docs/a1_c8_target_selection_competent.json").read_text(encoding="utf-8"))
    cur = json.loads(Path("docs/a1_target_selection.json").read_text(encoding="utf-8"))
    blocks = {seed: row["selected"] for seed, row in comp["per_seed"].items()}
    current = {seed: row["selected"] for seed, row in cur["per_seed"].items()}

    assert act["kind"] == "a1_target_freeze_act_n20"
    assert act["id"] == "A1-TARGET-FREEZE-N20-1"
    assert act["status"].startswith("SIGNED BY OWNER 2026-11-15")
    assert act["signed"] is True
    assert act["effective_date"] == "2026-11-15"
    assert act["selection_artifact"] == "docs/a1_c8_target_selection_competent.json"
    assert act["selection_artifact_digest"] == hashlib.sha256(
        Path("docs/a1_c8_target_selection_competent.json").read_bytes()).hexdigest()
    assert act["targets_by_seed"] == blocks
    assert act["block_sizes"] == [len(blocks[seed]) for seed in sorted(blocks)]
    assert act["n_min"] == 17
    assert act["n_per_seed"] == 20
    assert act["target_count"] == sum(len(v) for v in blocks.values()) == 115
    assert act["unique_target_edges"] == len({e for v in blocks.values() for e in v}) == 90
    assert act["threshold"] == 0.05 and act["threshold_changed"] is False
    assert act["estimand"].startswith("the pre-37 cycle-membership directed-edge effect, conditional")

    # The block is not a superset of the previous one, and the act does not claim it is.
    retained = {seed: [e for e in current[seed] if e in set(blocks[seed])] for seed in blocks}
    assert act["current_targets_retained_by_seed"] == retained
    assert sum(len(v) for v in retained.values()) == 7
    assert act["current_targets_retained"] is False
    assert act["superset_of_current_targets"] is False
    assert act["new_targets_by_seed"] == {
        seed: [e for e in blocks[seed] if e not in set(current[seed])] for seed in blocks}

    # C8's denominator follows each block's size; the two short seeds may spend no assertion.
    assert act["c8_resolution"]["assertions_allowed_per_seed"] == "1, 0, 1, 1, 0, 1"

    # C5 is cleared on THIS block, not inherited from the representative one.
    audit = json.loads(Path("docs/a1_c5_target_timing_competent.json").read_text(encoding="utf-8"))
    assert audit["status"].startswith("PASS")
    assert audit["totals"] == {"rows": 115, "late": 0, "observed_carriers": 115, "missing_carriers": 0}
    assert a1_c5_competent_audit.problems() == []

    # The verdict code is pinned, and the pin covers both modules.
    assert a1_scorer_pin.verify() == []
    assert set(a1_scorer_pin.build()["modules"]) == {"benchmarks/a1_arms.py", "benchmarks/a1_result.py"}

    # Nothing blocks, no grant exists, no cell ran.
    assert [row["id"] for row in act["preconditions"] if row["blocking"]] == []
    assert act["grant_after_signature"].startswith("ISSUED 2026-11-15")
    assert "A1-GRANT" in act["grant_after_signature"]
    assert act["run_after_signature"].startswith("RAN 2026-11-15")
    assert "A1-RUN" in act["run_after_signature"]
    assert act["held_on"]["reason"] == "CLEARED_BY_DECISION-A1-COMPETENT-ESTIMAND"

    # The block validates between the floor and the nominal size.
    assert a1_two_path.target_set_problems(_n20_target_doc()) == []


def test_registered_target_map_reads_the_block_the_manifest_names():
    """The scorer's expected targets must follow the frozen manifest, not a module-level default."""
    import json

    from benchmarks import a1_arms

    act = json.loads(Path("docs/a1_target_freeze_act_n20.json").read_text(encoding="utf-8"))
    mapped = a1_arms.registered_target_map()
    assert mapped == act["targets_by_seed"]

    # The defect this replaced: the representative artifact shares only 37 rows with the frozen block, so a
    # map built from it would disagree on every seed.
    representative = json.loads(Path("docs/a1_c8_target_selection.json").read_text(encoding="utf-8"))
    for seed, edges in representative["per_seed"].items():
        assert edges["selected"] != mapped[seed], seed


def test_the_execution_gate_opens_under_the_grant_and_still_refuses_without_it():
    """A gate that cannot refuse is decoration; a gate that refuses a granted, frozen manifest is broken."""
    from benchmarks import a1_two_path
    from benchmarks.authorisation_guard import preparation_only

    # The block has run once, so the live manifest must now refuse a second run.
    live = a1_two_path.preflight()
    assert "the manifest already names a result" in live, live

    # The gate itself still opens on a granted, frozen, unrun manifest: that is what it was opened on.
    pre_run = a1_two_path.manifest()
    pre_run["status"] = "GRANTED, NOT RUN"
    pre_run["result"] = {"path": None, "exists": False}
    assert a1_two_path.preflight(pre_run) == []

    ungranted = a1_two_path.manifest()
    ungranted["authorisation"] = {"granted": False, "granted_on": None,
                                  "document": None, "quote": None}
    refusals = a1_two_path.preflight(ungranted)
    assert "the dated grant is not recorded" in refusals

    unprepared = a1_two_path.manifest()
    unprepared["authorisation"]["quote"] = "Write the dated grant document, without running anything."
    assert any("preparation-only" in reason for reason in a1_two_path.preflight(unprepared))
    assert preparation_only(unprepared["authorisation"]["quote"]) is True

    unfrozen = a1_two_path.manifest()
    unfrozen["frozen"] = False
    unfrozen["result"] = {"path": None, "exists": False}
    unfrozen["status"] = "GRANTED, NOT RUN"
    assert "the manifest is not frozen" in a1_two_path.preflight(unfrozen)


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
