"""G13-D adapter: the interventions must be real before any score is read."""
from __future__ import annotations

import pathlib

from benchmarks import g13d_diagnostic as g


def test_the_provenance_intervention_removes_sleep_sourced_sources():
    """The world-only lookback is the intervention; it has to bite."""
    import organica.memory as memory_module

    plain_path = g._scratch("probe_plain")
    world_path = g._scratch("probe_world")
    plain = memory_module.MemoryService(str(plain_path))
    filtered = g.WorldOnlyMemory(str(world_path))
    try:
        for mem in (plain, filtered):
            mem.store("willow", event_type="sleep", source="sleep:payload")
            mem.store("teal", event_type="observe", source="env")
        plain_pairs = {(u, v) for u, v, _ in plain.temporal_edges(min_count=1)}
        filtered_pairs = {(u, v) for u, v, _ in filtered.temporal_edges(min_count=1)}
        assert ("willow", "teal") in plain_pairs, "the frozen engine records it"
        assert ("willow", "teal") not in filtered_pairs, "the filter must remove it"
    finally:
        plain._conn.close()
        filtered._conn.close()


def test_the_capacity_intervention_is_the_authorized_value():
    assert g.CappedSleepService.MAX_PREDICTIONS == 1000
    assert g.SleepService.MAX_PREDICTIONS == 20
    assert g.G13DSleepService.MAX_PREDICTIONS == 1000


def test_the_plan_and_the_seed_set_are_the_authorized_ones():
    plan = pathlib.Path(g.PLAN_DOC).read_text(encoding="utf-8")
    assert "20261101" in plan and "20261105" in plan
    assert "256.0" in plan, "the fixed alpha must be in the plan"
    assert g.SEEDS == (20261101, 20261102, 20261103, 20261104, 20261105)
    assert g.ALPHA == 256.0


def test_no_confirmatory_seed_is_in_the_diagnostic():
    closed_confirmatory = set(range(20261207, 20261227))
    assert closed_confirmatory.isdisjoint(g.SEEDS)


def test_capacity_is_recorded_as_not_measured_everywhere():
    """A per-seed field must not assert a verdict the run never measured."""
    import json
    art = json.loads(pathlib.Path(g.DIAGNOSTIC_OUT).read_text(encoding="utf-8"))
    assert art["checks"]["cap_binding"] is None
    assert art["capacity_note"]
    for entry in art["per_seed"]:
        assert entry["checks"]["cap_binding"] is None
        assert entry["checks"]["capacity_note"]
        assert "max_candidates" not in entry, "the all-type counter must not read as a cap"
        assert entry["all_candidates_max_note"]


def test_aggregation_never_infers_capacity_from_the_all_type_counter():
    unmeasured = [{"checks": {"provenance_filter_bit": True, "cap_binding": None}}]
    assert g._aggregate_checks(unmeasured)["cap_binding"] is None
    mixed = [{"checks": {"provenance_filter_bit": True, "cap_binding": True}},
             {"checks": {"provenance_filter_bit": True, "cap_binding": None}}]
    assert g._aggregate_checks(mixed)["cap_binding"] is None
    measured = [{"checks": {"provenance_filter_bit": True, "cap_binding": False}},
                {"checks": {"provenance_filter_bit": True, "cap_binding": True}}]
    assert g._aggregate_checks(measured)["cap_binding"] is False
