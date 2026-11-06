"""Candidate supersession (docs/DECISION-CANDIDATE-SUPERSESSION.md).

The stored sleep rows are a history: a surviving candidate is re-written every cycle, so
an old copy at the formation confidence sits beside the copy that has decayed. These tests
pin the three properties the decision claims:

  D1  one live copy per identity, the newest generation;
  D2  a pruned candidate is recorded dead and stops being loaded;
  and (rule 25c) the pre-fix rule is shown to return the stale copy on the same rows, so
  the checks can fail rather than passing by construction.
"""

from __future__ import annotations

import json

import pytest

from organica.memory import MemoryService
from organica.candidates import SleepReport
from organica.sleep import SchemaCandidate, SleepService


@pytest.fixture
def engine(tmp_path):
    mem = MemoryService(str(tmp_path / "supersession.db"))
    svc = SleepService(mem)
    try:
        yield mem, svc
    finally:
        mem.close()


def _form_schema(mem, svc):
    for _ in range(10):
        with mem.batch():
            mem.store("amber birch cedar", event_type="observe", source="env:A")
            mem.store("delta ember flora", event_type="observe", source="env:A")
    report = svc.run_sleep_cycle()
    schemas = [s for s in report.schemas if s.source_role == "antecedent"]
    assert schemas, "the directional world must form a schema"
    return schemas[0]


def _decay(svc, priors: list[dict]) -> tuple[int, int, int]:
    svc._prior_cache = None
    return svc._natural_selection(
        prior=priors, concepts=[], phrases=[], loops=[], predictions=[], schemas=[])


def _live(svc, cand_id: str) -> dict | None:
    svc._prior_cache = None
    for candidate in svc._load_prior_candidates():
        if candidate.get("id") == cand_id:
            return candidate
    return None


def _stored(svc, cand_id: str) -> list[dict]:
    out = []
    for event in svc.memory.recent(n=4000, event_type="sleep"):
        if not event.source.startswith("sleep:") or event.source == "sleep:meta":
            continue
        try:
            row = json.loads(event.content)
        except (json.JSONDecodeError, ValueError):
            continue
        if row.get("id") == cand_id:
            out.append(row)
    return out


def _prior_dict(schema) -> dict:
    return {
        "type": "schema_candidate",
        "id": schema.id,
        "generation": schema.generation,
        "source_role": schema.source_role,
        "target_role": schema.target_role,
        "confidence": schema.confidence,
        "source_exemplars": list(schema.source_exemplars),
        "target_exemplars": list(schema.target_exemplars),
        "evidence": dict(schema.evidence),
    }


def test_the_newest_copy_supersedes_its_predecessors(engine):
    """D1: after one decay cycle the loader returns the decayed copy, not the original."""
    mem, svc = engine
    schema = _form_schema(mem, svc)
    prior = _prior_dict(schema)
    formation = prior["confidence"]

    _decay(svc, [prior])
    live = _live(svc, schema.id)

    assert live is not None, "the decayed copy must still be live"
    assert live["confidence"] == pytest.approx(round(formation * 0.8, 4))
    assert len(_stored(svc, schema.id)) >= 2, "the history must still be on disk"


def test_a_loaded_view_never_repeats_an_identity(engine):
    """D1: five decay cycles produce five rows and one live copy."""
    mem, svc = engine
    schema = _form_schema(mem, svc)
    prior = _prior_dict(schema)
    for _ in range(5):
        _decay(svc, [prior])
        prior = _live(svc, schema.id)
        assert prior is not None

    loaded = svc._load_prior_candidates()
    ids = [c.get("id") for c in loaded]
    assert len(ids) == len(set(ids)), "the loader returned two copies of one identity"
    assert sum(1 for i in ids if i == schema.id) == 1


def test_a_pruned_candidate_is_recorded_dead_and_stops_being_loaded(engine):
    """D2: retirement supersedes the last live copy, so it cannot be reloaded and re-decayed."""
    mem, svc = engine
    prior = {
        "type": "schema_candidate",
        "id": "schema:alpha->beta",
        "generation": 4,
        "confidence": 0.16,          # 0.16 * 0.8 = 0.128 < DEATH_THRESHOLD = 0.15
        "source_exemplars": ["alpha"],
        "target_exemplars": ["beta"],
        "evidence": {},
    }
    _, _, pruned = _decay(svc, [prior])
    assert pruned == 1

    assert _live(svc, prior["id"]) is None
    tombstones = [r for r in _stored(svc, prior["id"]) if r.get("retired")]
    assert len(tombstones) == 1, "a prune must write a death record"
    assert tombstones[0]["evidence"]["retired_from"] == pytest.approx(0.16)

    # The live prior is now empty for this id, so it is not decayed again forever.
    _, _, pruned_again = _decay(svc, [])
    assert pruned_again == 0, "a retired candidate must not be decayed again"


def test_re_extraction_supersedes_a_tombstone(engine):
    """D2: retirement is not permanent suppression — a newer live copy wins."""
    mem, svc = engine
    cand_id = "schema:amber->delta"
    svc._store_single_candidate({"type": "schema_candidate", "id": cand_id,
                                 "confidence": 0.12, "retired": True, "evidence": {}})
    svc._store_single_candidate({"type": "schema_candidate", "id": cand_id,
                                 "confidence": 0.7, "generation": 9, "evidence": {}})
    live = _live(svc, cand_id)
    assert live is not None and live["confidence"] == pytest.approx(0.7)


def test_the_old_rule_would_have_kept_the_stale_copy(engine):
    """Rule 25c: the pre-fix selector is reconstructed on the same rows and must fail.

    Five decay cycles take the live confidence below STABLE_THRESHOLD, so priming must
    stop. The maximum over all stored copies is still the formation confidence, which is
    what the old reader returned — if this assertion ever fails, the defect the decision
    fixes was not reproduced by this test.
    """
    mem, svc = engine
    schema = _form_schema(mem, svc)
    prior = _prior_dict(schema)
    formation = prior["confidence"]
    for _ in range(5):
        _decay(svc, [prior])
        prior = _live(svc, schema.id)
        assert prior is not None

    live = _live(svc, schema.id)
    history_max = max(
        r["confidence"] for r in _stored(svc, schema.id) if not r.get("retired"))

    assert live["confidence"] < svc.STABLE_THRESHOLD <= history_max
    assert history_max == pytest.approx(formation)


def test_a_carried_structure_does_not_count_as_current_evidence(engine):
    """Freeze amendment (docs/V1-FREEZE.md §6): carried is a view, not this cycle's evidence."""
    mem, svc = engine
    schema = _form_schema(mem, svc)
    prior = _prior_dict(schema)
    carried = SchemaCandidate(
        id=schema.id,
        source_exemplars=list(schema.source_exemplars),
        target_exemplars=list(schema.target_exemplars),
        confidence=schema.confidence,
        evidence=dict(schema.evidence),
        carried_forward=True,
    )
    strengthened, decayed, pruned = svc._natural_selection(
        prior=[prior], concepts=[], phrases=[], loops=[], predictions=[], schemas=[carried])
    assert (strengthened, decayed, pruned) == (0, 1, 0)
    live = _live(svc, schema.id)
    assert live["confidence"] == pytest.approx(round(prior["confidence"] * 0.8, 4))


def test_a_carried_structure_is_not_re_stored(engine):
    """Re-writing a carried copy would reinstate the pre-decay value as the newest row."""
    mem, svc = engine
    carried = SchemaCandidate(
        id="schema:carried->only", source_exemplars=["carried"],
        target_exemplars=["only"], confidence=0.7, carried_forward=True)
    svc._store_candidates(SleepReport(cycle=1, ran_at=0.0, schemas=[carried]))
    assert _stored(svc, "schema:carried->only") == []


def test_the_carried_marker_never_reaches_the_store(engine):
    mem, svc = engine
    svc._store_single_candidate({"type": "schema_candidate", "id": "schema:marker->test",
                                 "confidence": 0.7, "carried_forward": True})
    rows = _stored(svc, "schema:marker->test")
    assert rows and "carried_forward" not in rows[0]
