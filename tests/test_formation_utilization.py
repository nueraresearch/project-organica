"""The formation-utilization harness's own checks.

Every audit in the protocol ships with a test that FIRES: the test mutates the
condition the audit exists to detect and asserts the audit rejects it.  A gate
that cannot fail is decoration (AGENTS rule 25c), and an audit whose failure
branch has never executed is a gate nobody has tested.

The substrate test is the one AGENTS rule 5 requires for a new instrument: with
the oracle filter off, an arm must leave the store byte-identical to a run
without the recording subclass.  Two runs are compared table by table, and the
surviving candidate dump is compared too, because the readout is downstream of
the store.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import formation_utilization as fu  # noqa: E402
from benchmarks.acquisition_harness import _CapOverrideSleepService  # noqa: E402
from organica.memory import MemoryService  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# The engine stamps its own `_sleep_meta` rows with wall-clock time, so two
# runs of the SAME code differ there.  Normalising that field is what makes the
# comparison meaningful; the test below also compares the stock class against
# itself, so the normaliser cannot be hiding a subclass-specific difference.
_WALL_CLOCK = re.compile(r'"(ran_at|created_at|timestamp|time)":\s*[0-9][0-9eE+.\-]*')


def _normalise(content: str) -> str:
    return _WALL_CLOCK.sub(lambda m: f'"{m.group(1)}":0', content)


def _fingerprint(mem: MemoryService) -> str:
    parts = [
        [(source, event_type, _normalise(content), tags)
         for source, event_type, content, tags in mem._conn.execute(
             "SELECT source, event_type, content, tags FROM events ORDER BY rowid"
         ).fetchall()],
        mem._conn.execute(
            "SELECT tag_from, tag_to, count FROM precedes ORDER BY tag_from, tag_to"
        ).fetchall(),
        mem._conn.execute(
            "SELECT tag_a, tag_b, count FROM cooccurrences ORDER BY tag_a, tag_b"
        ).fetchall(),
        mem._conn.execute(
            "SELECT tag, count FROM tag_counts ORDER BY tag"
        ).fetchall(),
    ]
    return hashlib.sha256(repr(parts).encode("utf-8")).hexdigest()


def _candidate_dump(svc) -> list[tuple]:
    out = []
    for c in svc._load_prior_candidates():
        out.append((c.get("id"), c.get("type"), c.get("source"), c.get("target"),
                    c.get("strength"),
                    json.dumps(c.get("evidence"), sort_keys=True)))
    return out


def _short_run(service_cls, cap: int, admission=None, fixed=None):
    prep = fu.prepare_world(fu.TASK_T2, fu.TIMING_SEED)
    db = fu._fresh_db(f"test_fu_{time.time_ns()}.db")
    mem = MemoryService(str(db))
    try:
        if service_cls is fu._AdmissionSleepService:
            svc = service_cls(mem, cap, admission, fixed)
        else:
            svc = service_cls(mem, cap)
        for cyc in range(6):
            for ev in prep["events"][cyc * prep["epc"]:(cyc + 1) * prep["epc"]]:
                mem.store(ev, event_type="observe", source="env")
            svc.run_sleep_cycle()
        reads = getattr(svc, "temporal_reads", [])
        return _fingerprint(mem), _candidate_dump(svc), reads
    finally:
        mem._conn.close()
        try:
            db.unlink(missing_ok=True)
        except PermissionError:
            pass


def _arm(layer1_coverage: float, layer1_precision: float,
         transfer: float, readout_precision: float = 0.5) -> dict:
    return {
        "layer1_coverage": layer1_coverage,
        "layer1_precision_world": layer1_precision,
        "readout_precision": readout_precision,
        "scores": {"transfer": {"house_shape": {"log_loss": transfer}}},
    }


# ---------------------------------------------------------------------------
# A1 — arm differential
# ---------------------------------------------------------------------------

def test_a1_passes_when_the_arms_differ():
    a = fu.audit_arm_differential({"A": 0.0, "B": 0.985, "C": 0.982})
    assert a["passed"], a["reason"]


def test_a1_fires_when_the_arms_are_indistinguishable():
    a = fu.audit_arm_differential({"A": 0.0, "B": 0.0, "C": 0.0})
    assert a["passed"] is False
    assert "B_at_or_above_gate" in a["reason"]


# ---------------------------------------------------------------------------
# A2 — oracle exactness
# ---------------------------------------------------------------------------

def test_a2_passes_on_exact_admission():
    support = {("a", "b"), ("b", "c")}
    eligible = [[("a", "b"), ("a", "x"), ("b", "c")]]
    admitted = [[("a", "b"), ("b", "c")]]
    a = fu.audit_oracle_exactness(eligible, admitted, support, cap=1000)
    assert a["passed"], a["reason"]


def test_a2_fires_on_an_injected_false_edge():
    support = {("a", "b"), ("b", "c")}
    eligible = [[("a", "b"), ("a", "x")]]
    admitted = [[("a", "b"), ("a", "x")]]
    a = fu.audit_oracle_exactness(eligible, admitted, support, cap=1000)
    assert a["passed"] is False
    assert "non-permitted pair" in a["reason"]


def test_a2_fires_when_a_permitted_edge_is_dropped():
    support = {("a", "b"), ("b", "c")}
    eligible = [[("a", "b"), ("b", "c")]]
    admitted = [[("a", "b")]]
    a = fu.audit_oracle_exactness(eligible, admitted, support, cap=1000)
    assert a["passed"] is False
    assert "expected 2" in a["reason"]


def test_a2_fires_when_the_cap_binds_after_filtering():
    support = {("a", "b"), ("b", "c"), ("c", "d")}
    eligible = [[("a", "b"), ("b", "c"), ("c", "d")]]
    admitted = [[("a", "b"), ("b", "c"), ("c", "d")]]
    a = fu.audit_oracle_exactness(eligible, admitted, support, cap=2)
    assert a["passed"] is False
    assert "cap bound" in a["reason"]


def test_a2_fires_when_evidence_differs():
    support = {("a", "b")}
    eligible = [[("a", "b")]]
    admitted = [[("a", "b")]]
    a = fu.audit_oracle_exactness(
        eligible, admitted, support, cap=1000,
        pre_cap_evidence=[{("a", "b"): {"temporal_count": 7}}],
        admitted_evidence=[{("a", "b"): {"temporal_count": 6}}])
    assert a["passed"] is False
    assert "different evidence" in a["reason"]


# ---------------------------------------------------------------------------
# A8 — temporal input invariance (Amendment 1)
# ---------------------------------------------------------------------------

def _follower(graphs, eligible, evidence):
    return {"graphs": graphs, "eligible": eligible, "evidence": evidence}


def test_a8_passes_when_the_admission_arms_read_the_same_basis():
    g = {"a": {"b": 3}, "b": {"c": 2}}
    e = [[("a", "b"), ("b", "c")]]
    ev = [{("a", "b"): {"temporal_count": 3},
           ("b", "c"): {"temporal_count": 2}}]
    a = fu.audit_temporal_input(
        [g], e, ev,
        {"C": _follower([g], e, ev), "S": _follower([g], e, ev)},
        engine_own_table_symdiff=7)
    assert a["passed"], a["reason"]
    assert a["evidence"]["engine_own_table_symmetric_difference"] == 7


def test_a8_fires_when_a_cycle_reads_a_different_graph():
    g = {"a": {"b": 3}}
    other = {"a": {"b": 4}}
    e = [[("a", "b")]]
    ev = [{("a", "b"): {"temporal_count": 3}}]
    a = fu.audit_temporal_input([g], e, ev, {"C": _follower([other], e, ev)})
    assert a["passed"] is False
    assert a["evidence"]["first_failures"][0]["kind"] == "temporal_graph"


def test_a8_fires_when_the_eligible_stream_differs():
    g = {"a": {"b": 3}}
    e = [[("a", "b")]]
    other_e = [[("a", "b"), ("a", "x")]]
    ev = [{("a", "b"): {"temporal_count": 3}}]
    a = fu.audit_temporal_input([g], e, ev, {"C": _follower([g], other_e, ev)})
    assert a["passed"] is False
    assert "eligible_stream" in a["reason"]


def test_a8_fires_on_a_cycle_count_mismatch():
    g = {"a": {"b": 3}}
    e = [[("a", "b")]]
    ev = [{("a", "b"): {"temporal_count": 3}}]
    a = fu.audit_temporal_input(
        [g, g], e + e, ev + ev, {"C": _follower([g], e, ev)})
    assert a["passed"] is False
    assert "cycle_count" in a["reason"]


def test_a8_fires_when_the_evidence_differs():
    g = {"a": {"b": 3}}
    e = [[("a", "b")]]
    b_ev = [{("a", "b"): {"temporal_count": 3}}]
    c_ev = [{("a", "b"): {"temporal_count": 4}}]
    a = fu.audit_temporal_input([g], e, b_ev, {"C": _follower([g], e, c_ev)})
    assert a["passed"] is False
    assert "evidence" in a["reason"]


# ---------------------------------------------------------------------------
# Amendment 1 — the fixed temporal basis
# ---------------------------------------------------------------------------

def test_fixed_temporal_graph_is_read_verbatim_and_then_exhausts():
    db = fu._fresh_db(f"test_fu_fixed_{time.time_ns()}.db")
    mem = MemoryService(str(db))
    try:
        mem.store("alpha beta", event_type="observe", source="env")
        mem.store("beta gamma", event_type="observe", source="env")
        svc = fu._AdmissionSleepService(mem, fu.CAP_B,
                                        fixed_temporal=[{"x": {"y": 9}}])
        assert svc._load_temporal() == {"x": {"y": 9}}
        assert svc.temporal_reads == [{"x": {"y": 9}}]
        with pytest.raises(AssertionError):
            svc._load_temporal()
    finally:
        mem._conn.close()
        try:
            db.unlink(missing_ok=True)
        except PermissionError:
            pass


def test_fixed_basis_reproduces_the_captured_arm_and_changes_when_it_differs():
    b_fp, b_dump, b_graphs = _short_run(fu._AdmissionSleepService, fu.CAP_B)
    assert b_graphs, "the unfiltered arm did not record a temporal basis"
    c_fp, c_dump, c_graphs = _short_run(fu._AdmissionSleepService, fu.CAP_B,
                                        fixed=b_graphs)
    assert c_graphs == b_graphs
    assert (c_fp, c_dump) == (b_fp, b_dump)
    empty = [{} for _ in b_graphs]
    d_fp, _, _ = _short_run(fu._AdmissionSleepService, fu.CAP_B, fixed=empty)
    assert d_fp != b_fp


def test_amendment_table_matches_the_pre_amendment_artifact():
    art = json.loads(
        (REPO / "docs/formation_utilization_timing_pre_amendment.json")
        .read_text(encoding="utf-8"))
    text = (REPO / "docs/FORMATION-UTILIZATION-PREREGISTRATION.md").read_text(
        encoding="utf-8")
    section = text.split("## 12.", 1)[1]
    rows = {}
    for line in section.splitlines():
        if line.startswith("| T2 |") or line.startswith("| T1 |"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows[cells[0]] = cells
    assert set(rows) == {"T2", "T1"}, "the amendment's D1 table is missing"
    for task in ("T2", "T1"):
        d = art["tasks"][task]["diagnostics"]["D1"]["evidence"]
        cycles = art["tasks"][task]["audits"]["A2"]["evidence"]["cycles"]
        cells = rows[task]
        assert cells[1] == f"{d['temporal_edges_b']} vs {d['temporal_edges_c']}"
        assert cells[2] == str(d["temporal_symmetric_difference"])
        assert cells[3] == (f"{d['cycles_with_a_differing_permitted_stream']} of "
                            f"{cycles} (first at cycle {d['first_differing_cycle']})")
        assert cells[4] == (f"{d['missing_permitted_candidates']} / "
                            f"{d['extra_permitted_candidates']}")


# ---------------------------------------------------------------------------
# A3 — precision premise
# ---------------------------------------------------------------------------

def test_a3_passes_inside_the_band_with_exact_admission():
    a = fu.audit_precision_premise(0.3443, 1.0)
    assert a["passed"], a["reason"]


def test_a3_fires_when_B_precision_leaves_the_band():
    a = fu.audit_precision_premise(0.60, 1.0)
    assert a["passed"] is False
    assert "left the measured band" in a["reason"]


def test_a3_fires_when_C_admission_is_not_exact():
    a = fu.audit_precision_premise(0.30, 0.92)
    assert a["passed"] is False
    assert "not 1.0" in a["reason"]


def test_a3_fires_on_an_empty_denominator():
    a = fu.audit_precision_premise(None, None)
    assert a["passed"] is False
    assert "not measurable" in a["reason"]


def test_a3_is_not_applicable_where_the_band_has_no_provenance():
    a = fu.audit_precision_premise(0.54, 1.0, band_applies=False)
    assert a["passed"] is None
    assert a["applicable"] is False
    assert "no committed band" in a["reason"]


# ---------------------------------------------------------------------------
# A4 — denominators
# ---------------------------------------------------------------------------

def test_a4_fires_on_an_empty_limb():
    a = fu.audit_denominators({
        "retention": {"events": 10, "cells": 100},
        "transfer": {"events": 10, "cells": 100},
        "revision": {"events": 0, "cells": 0},
    })
    assert a["passed"] is False
    assert "revision" in a["reason"]


def test_a4_passes_with_every_limb_populated():
    a = fu.audit_denominators({
        "retention": {"events": 10, "cells": 100},
        "transfer": {"events": 10, "cells": 100},
        "revision": {"events": 10, "cells": 100},
    })
    assert a["passed"]


# ---------------------------------------------------------------------------
# A5 — the readout recovers a known answer, and can be wrong
# ---------------------------------------------------------------------------

def test_a5_passes_on_the_committed_readout():
    a = fu.audit_readout_construct()
    assert a["passed"], a["reason"]


def test_a5_fires_when_the_readout_ignores_its_evidence():
    def ignores_evidence(rows, base, alpha):
        return lambda u, v: base.get(v, 0.0)

    a = fu.audit_readout_construct(ignores_evidence)
    assert a["passed"] is False
    assert "beats_base_rate" in a["reason"]


def test_a5_fires_when_the_readout_is_transposed():
    def transposed(rows, base, alpha):
        flipped = {s: {t: 0.0 for t in base} for s in base}
        for s, targets in rows.items():
            for t, w in targets.items():
                flipped.setdefault(t, {})[s] = w
        return fu.make_organica_backoff(flipped, base, alpha)

    a = fu.audit_readout_construct(transposed)
    assert a["passed"] is False


# ---------------------------------------------------------------------------
# A6 — no leakage
# ---------------------------------------------------------------------------

def test_a6_passes_when_the_shuffle_collapses():
    meta = {"size": 128, "support_size": 128, "retained_permitted": 0,
            "retained_share": 0.0, "filled_from_permitted": 0}
    a = fu.audit_no_leakage(_arm(0.0, 0.0, 4.0), _arm(1.0, 0.98, 2.0), meta)
    assert a["passed"], a["reason"]


def test_a6_fires_when_the_shuffled_arm_keeps_its_coverage():
    meta = {"size": 128, "support_size": 128, "retained_permitted": 0,
            "retained_share": 0.0, "filled_from_permitted": 0}
    a = fu.audit_no_leakage(_arm(0.94, 0.90, 2.0), _arm(1.0, 0.98, 2.0), meta)
    assert a["passed"] is False
    assert "not doing the work" in a["reason"]


def test_a6_is_not_applicable_where_no_wrong_filter_exists():
    meta = {"size": 272, "support_size": 272, "retained_permitted": 144,
            "retained_share": 0.5294, "filled_from_permitted": 144}
    a = fu.audit_no_leakage(_arm(0.2, 0.4, 3.0), _arm(1.0, 1.0, 2.0), meta)
    assert a["passed"] is None
    assert a["applicable"] is False


# ---------------------------------------------------------------------------
# A7 — attribution share
# ---------------------------------------------------------------------------

def test_a7_passes_when_layer_one_carries_the_majority():
    a = fu.audit_attribution({
        "prediction_candidate": {"unique_count": 20, "edge_weight": 900.0},
        "concept_candidate": {"unique_count": 4, "edge_weight": 100.0},
    })
    assert a["passed"], a["reason"]


def test_a7_fires_when_the_uncontrolled_layers_dominate():
    a = fu.audit_attribution({
        "prediction_candidate": {"unique_count": 20, "edge_weight": 100.0},
        "concept_candidate": {"unique_count": 4, "edge_weight": 900.0},
    })
    assert a["passed"] is False
    assert "Layer 1 carries" in a["reason"]


def test_a7_fires_on_an_empty_readout():
    a = fu.audit_attribution({"prediction_candidate": {"unique_count": 0,
                                                      "edge_weight": 0.0}})
    assert a["passed"] is False


# ---------------------------------------------------------------------------
# The oracle set and the shuffle
# ---------------------------------------------------------------------------

def test_support_is_regime_invariant_and_contains_the_training_edges():
    expected = {"T2": (128, 112), "T1": (272, 167)}
    for task in fu.TASKS:
        prep = fu.prepare_world(task, fu.TIMING_SEED)
        s0 = fu.build_support(task, prep["world"], 0)
        s1 = fu.build_support(task, prep["world"], 1)
        size, edges = expected[task]
        assert s0 == s1
        assert len(s0) == size
        assert len(prep["world_edges"]) == edges
        assert not (prep["world_edges"] - s0)


def test_the_shuffled_filter_has_matching_shape_and_no_true_pairs_on_T2():
    prep = fu.prepare_world(fu.TASK_T2, fu.TIMING_SEED)
    support = fu.build_support(fu.TASK_T2, prep["world"], 0)
    shuffled, meta = fu.shuffled_support(support, fu.TIMING_SEED)
    assert meta["retained_permitted"] == 0
    assert len(shuffled) == len(support)
    by_source: dict[str, int] = {}
    for u, _ in support:
        by_source[u] = by_source.get(u, 0) + 1
    for u, v in shuffled:
        assert (u, v) not in support
    shuffled_by_source: dict[str, int] = {}
    for u, _ in shuffled:
        shuffled_by_source[u] = shuffled_by_source.get(u, 0) + 1
    assert shuffled_by_source == by_source


def test_the_shuffled_filter_reports_its_retained_share_on_T1():
    prep = fu.prepare_world(fu.TASK_T1, fu.TIMING_SEED)
    support = fu.build_support(fu.TASK_T1, prep["world"], 0)
    _, meta = fu.shuffled_support(support, fu.TIMING_SEED)
    assert meta["retained_permitted"] > 0
    assert meta["retained_share"] == round(
        meta["retained_permitted"] / meta["support_size"], 4)


# ---------------------------------------------------------------------------
# Decision rule
# ---------------------------------------------------------------------------

def test_a_verdict_cannot_be_computed_from_one_seed():
    with pytest.raises(ValueError):
        fu.paired_bootstrap([0.3])


def test_analyse_reports_single_seed_cells_as_not_measurable():
    record = {
        "task": "T2", "seed": 20261101,
        "arms": {arm: {"scores": {limb: {"house_shape": {"log_loss": 1.0}}
                                  for limb in fu.LIMBS}} for arm in "ABC"},
        "bar": {limb: {"member": "replay"} for limb in fu.LIMBS},
        "comparators": {"replay": {limb: {"house_shape": {"log_loss": 2.0}}
                                   for limb in fu.LIMBS}},
    }
    analysis = fu.analyse([record])
    cell = analysis["tasks"]["T2"]["cells"]["C"]["transfer"]
    assert cell["verdict"] == "not measurable"


def _fake_result(task: str, seed: int, audit_passed: bool = True) -> dict:
    arms = {
        label: {"scores": {limb: {"house_shape": {"log_loss": 1.0}}
                           for limb in fu.LIMBS}}
        for label in "ABC"
    }
    return {
        "task": task, "seed": seed, "arms": arms,
        "bar": {limb: {"member": "replay"} for limb in fu.LIMBS},
        "comparators": {"replay": {limb: {"house_shape": {"log_loss": 2.0}}
                                    for limb in fu.LIMBS}},
        "audits": {key: {"audit": key, "name": key, "passed": audit_passed,
                          "applicable": True, "checks": {}, "evidence": {},
                          "reason": "synthetic"}
                   for key in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8")},
        "campaign_ready": audit_passed,
        "campaign_ready_reason": "synthetic",
    }


def test_campaign_with_one_seed_does_not_invent_a_verdict(monkeypatch):
    monkeypatch.setattr(fu, "_run_unit",
                        lambda unit: _fake_result(unit[0], unit[1], True))
    artifact = fu.campaign_pass(seed_count=1, workers=1)
    assert artifact["status"] == "complete"
    cell = artifact["analysis"]["tasks"]["T2"]["cells"]["C"]["transfer"]
    assert cell["verdict"] == "not measurable"
    assert artifact["analysis"]["tasks"]["T2"]["mapping"]["label"] == "not measurable"


def test_campaign_stops_when_an_audit_fails(monkeypatch):
    monkeypatch.setattr(fu, "_run_unit",
                        lambda unit: _fake_result(unit[0], unit[1], False))
    artifact = fu.campaign_pass(seed_count=1, workers=1)
    assert artifact["status"] == "not measurable"
    assert artifact["audits"]["failing"]
    md = fu.render_campaign_markdown(artifact)
    assert "not measurable" in md
    assert "Verdict" not in md


def test_verdict_orientation_and_mapping():
    assert fu.verdict_of(0.01, 0.4) == "win"
    assert fu.verdict_of(-0.4, -0.01) == "loss"
    assert fu.verdict_of(-0.2, 0.2) == "tie"
    assert fu.map_outcome("win", "win")["target"] == "use / abstraction"
    assert fu.map_outcome("loss", "win")["target"] == "candidate selection / precision"
    assert fu.map_outcome("win", "loss")["label"].startswith("invalid")
    assert fu.map_outcome("loss", "loss")["target"].startswith("the use path")


# ---------------------------------------------------------------------------
# Generated markdown must contain numbers, not templates (AGENTS rule 20)
# ---------------------------------------------------------------------------

def _stop_artifact(reason: str) -> dict:
    return {
        "status": "not measurable",
        "generated_utc": "2026-10-30T00:00:00+00:00",
        "audits": {
            "failing": [{"audit": "A1", "task": "T2", "seed": 20261101}],
            "reason": reason,
        },
    }


def test_campaign_markdown_refuses_a_surviving_placeholder():
    with pytest.raises(AssertionError):
        fu.render_campaign_markdown(
            _stop_artifact("coverage {ties} was never computed"))


def test_campaign_markdown_renders_a_clean_stop():
    md = fu.render_campaign_markdown(
        _stop_artifact("coverage 0.0000 below the gate"))
    assert "not measurable" in md
    assert "A1" in md


# ---------------------------------------------------------------------------
# Substrate equivalence: the recording subclass must change nothing
# ---------------------------------------------------------------------------

def test_recording_subclass_is_behavior_neutral():
    stock_fp, stock_dump, _ = _short_run(_CapOverrideSleepService, fu.CAP_B)
    rec_fp, rec_dump, _ = _short_run(fu._AdmissionSleepService, fu.CAP_B)
    assert rec_fp == stock_fp
    assert rec_dump == stock_dump


def test_recording_equals_running_the_stock_class_twice():
    fp1, dump1, _ = _short_run(_CapOverrideSleepService, fu.CAP_B)
    fp2, dump2, _ = _short_run(_CapOverrideSleepService, fu.CAP_B)
    fp3, dump3, _ = _short_run(fu._AdmissionSleepService, fu.CAP_B)
    assert fp1 == fp2 == fp3
    assert dump1 == dump2 == dump3


def test_filter_off_is_identical_to_the_stock_cap_class():
    stock_fp, _, _ = _short_run(_CapOverrideSleepService, fu.CAP_A)
    rec_fp, _, _ = _short_run(fu._AdmissionSleepService, fu.CAP_A, None)
    assert rec_fp == stock_fp
