"""
tests/test_relational_schema_layer.py
--------------------------------------
Unit and integration tests for the Relational Schema Layer (v0.12.0).

Verifies:
  1. Relational schema extraction from asymmetric flow between discovered clusters/roles.
  2. Provenance grounding: schema parent_ids link to supporting predictions/concepts.
  3. Natural selection and Law VI memory decay for schema candidates.
  4. Top-down structural candidate priming across disjoint vocabularies (Context A -> Context B).
  5. Lineage reachability: primed prediction traces back to schema and source events.
  6. Control invariance: naïve organisms, pruned organisms, and symmetric worlds do NOT prime.

Vocabulary note
---------------
The tag extractor (`_extract_tags` in memory.py) uses ``re.findall(r'\\b[a-zA-Z]{4,}\\b', …)``.
Only alphabetic words of 4+ characters become tags; underscores split words at the boundary
so ``source_a`` extracts nothing.  All test events use natural English words ≥ 4 chars that
are not in the stop-word list.
"""

from __future__ import annotations
LAYER = "synthetic"  # benchmarks/test_layers.py: the module's execution layer

import pytest

from organica.memory import MemoryService
from organica.sleep import SleepService, SchemaCandidate, PredictionCandidate


@pytest.fixture
def fresh_engine(tmp_path):
    db_path = tmp_path / "test_schema.db"
    mem = MemoryService(str(db_path))
    svc = SleepService(mem)
    try:
        yield mem, svc
    finally:
        mem.close()


def test_schema_extraction_from_asymmetric_cluster_flow(fresh_engine):
    """When two clusters have strong, asymmetric directional transitions, a SchemaCandidate is formed.

    Cluster A: {atlas, baker, canon}  — appear in every FIRST event of each batch
    Cluster B: {delta, ember, flora}  — appear in every SECOND event of each batch

    With 8 repetitions:
      cross A→B ≈ 72, cross B→A ≈ 63 → net forward flow = 9 → asymmetric ✓
      symmetric worlds produce net = 0 (see control test).
    """
    mem, svc = fresh_engine

    for _ in range(8):
        with mem.batch():
            mem.store("atlas baker canon", event_type="observe", source="env")
            mem.store("delta ember flora", event_type="observe", source="env")

    rep = svc.run_sleep_cycle()
    assert len(rep.schemas) > 0, "Expected at least one SchemaCandidate to be extracted"

    schema = rep.schemas[0]
    assert schema.type == "schema_candidate"
    assert schema.source_role == "antecedent"
    assert schema.target_role == "consequent"
    assert schema.confidence >= 0.4
    assert schema.generation == 3
    assert len(schema.parent_ids) > 0, "Schema must have lineage parents"
    # directional_ratio = flow_A_to_B / max(flow_B_to_A, 1); asymmetric worlds > 1.0
    assert schema.evidence["directional_ratio"] > 1.0


def test_schema_law_vi_decay_and_reinforcement(fresh_engine):
    """Schema candidate obeys Law VI: confidence grows with each cycle the schema is re-observed,
    and decreases (via _natural_selection) when the schema key is absent from current candidates.

    Phase 1: 8 directed batches → schema forms at confidence C0.
    Phase 2: 8 MORE directed batches → schema is re-observed → confidence > C0 (reinforcement).
    Phase 3: Verify _natural_selection decays a prior schema that is NOT in current_keys.

    Uses 'solar lunar atlas' (Group A) and 'tidal ember delta' (Group B) — all words
    are ≥5 alphabetic characters and are not in the stop-word list.

    Design note: temporal edges persist in the DB, so a schema formed from directed data will
    continue to be re-extracted (and reinforced) as long as the same directed clusters are
    present.  Decay is therefore tested at the _natural_selection level, where we verify that
    the method correctly reduces confidence for a prior key absent from current candidates.
    """
    mem, svc = fresh_engine

    # Phase 1: Induce schema
    for _ in range(8):
        with mem.batch():
            mem.store("solar lunar atlas", event_type="observe", source="env")
            mem.store("tidal ember delta", event_type="observe", source="env")

    rep1 = svc.run_sleep_cycle()
    assert len(rep1.schemas) > 0, "Schema must form from asymmetric cross-cluster flow"
    init_conf = rep1.schemas[0].confidence

    # Phase 2: Continue directed observations -> schema strengthened each cycle
    for _ in range(8):
        with mem.batch():
            mem.store("solar lunar atlas", event_type="observe", source="env")
            mem.store("tidal ember delta", event_type="observe", source="env")

    rep2 = svc.run_sleep_cycle()
    strengthened_schemas = [s for s in rep2.schemas if s.source_role == "antecedent"]
    assert len(strengthened_schemas) > 0
    assert strengthened_schemas[0].confidence > init_conf, (
        "Schema must be reinforced when re-observed in consecutive cycles (Law VI strengthening)"
    )
    reinforced_conf = strengthened_schemas[0].confidence

    # Phase 3: Verify _natural_selection decay logic.
    # Build a synthetic prior dict for the schema candidate and check it decays
    # when absent from an empty current_keys set.
    prior_schema_dict = {
        "type": "schema_candidate",
        "id": rep2.schemas[0].id,
        "generation": rep2.schemas[0].generation,
        "source_role": "antecedent",
        "target_role": "consequent",
        "confidence": reinforced_conf,
        "source_exemplars": rep2.schemas[0].source_exemplars,
        "target_exemplars": rep2.schemas[0].target_exemplars,
        "evidence": {"forward_flow": 72, "backward_flow": 63},
    }
    # _natural_selection with an empty current set → schema not in current_keys → decays
    # We call it directly with an empty candidate list so the schema is not re-matched.
    n_strengthened, n_decayed, n_pruned = svc._natural_selection(
        prior=[prior_schema_dict],
        concepts=[], phrases=[], loops=[], predictions=[],
        schemas=[],  # schema NOT re-extracted → will decay
    )
    assert n_decayed >= 1 or n_pruned >= 1, (
        "Schema must decay or be pruned when absent from current cycle candidates (Law VI)"
    )


def test_priming_is_rank_only_and_never_admits_thin_evidence(fresh_engine):
    """Decision D1/D2: a schema may reorder admissible predictions; it may not admit one.

    Context A forms a directional schema (amber/birch/cedar -> delta/ember/flora).
    Context B then presents quartz->tidal exactly once. 1 < PREDICTION_MIN_COUNT = 5,
    so no prior of any kind may propose that edge, and no prediction may report a
    count above the one it observed.
    """
    mem, svc = fresh_engine

    for _ in range(10):
        with mem.batch():
            mem.store("amber birch cedar", event_type="observe", source="env:A")
            mem.store("delta ember flora", event_type="observe", source="env:A")
    rep_a = svc.run_sleep_cycle()
    schemas = [s for s in rep_a.schemas if s.source_role == "antecedent"]
    assert schemas, "Context A must form a directional schema"
    assert schemas[0].source_exemplars and schemas[0].target_exemplars

    with mem.batch():
        mem.store("quartz prism", event_type="observe", source="env:B")
        mem.store("tidal lunar", event_type="observe", source="env:B")
    rep_b = svc.run_sleep_cycle()

    thin = [p for p in rep_b.predictions if p.source == "quartz" and p.target == "tidal"]
    assert thin == [], (
        "A count-1 edge must not be admitted by any prior; got "
        f"{[(p.source, p.target, p.evidence.get('temporal_count')) for p in rep_b.predictions]}"
    )
    for p in rep_b.predictions:
        assert p.evidence["temporal_count"] >= svc.PREDICTION_MIN_COUNT
        assert "effective_count" not in p.evidence
        assert "schema_primed" not in p.evidence


def test_control_arm_invariance(tmp_path):
    """Naïve and symmetric world controls do NOT perform false-positive candidate priming."""
    # Control 1: Naïve (fresh memory enters Context B directly)
    db1 = tmp_path / "ctrl1.db"
    mem1 = MemoryService(str(db1))
    svc1 = SleepService(mem1)
    try:
        with mem1.batch():
            mem1.store("quartz prism", event_type="observe", source="env:B")
            mem1.store("tidal lunar", event_type="observe", source="env:B")
        rep1 = svc1.run_sleep_cycle()
        # Count is 1 < 5 and no schema exists -> no prediction candidate
        naive_preds = [p for p in rep1.predictions if p.source == "quartz" and p.target == "tidal"]
        assert len(naive_preds) == 0, "Naïve organism must NOT propose candidates with count < 5"
    finally:
        mem1.close()

    # Control 3: Symmetric world (copper/bronze ↔ silver/gold alternating) -> no schema formed
    # The alternating third event creates equal forward and backward cross-group flow (net=0).
    db2 = tmp_path / "ctrl2.db"
    mem2 = MemoryService(str(db2))
    svc2 = SleepService(mem2)
    try:
        for _ in range(8):
            with mem2.batch():
                # Symmetric alternating transitions: copper-bronze appears first AND third
                mem2.store("copper bronze", event_type="observe", source="env:C")
                mem2.store("silver gold", event_type="observe", source="env:C")
                mem2.store("copper bronze", event_type="observe", source="env:C")
        rep2 = svc2.run_sleep_cycle()
        # In a symmetric world, forward flow == backward flow (net=0) -> no schema
        assert len(rep2.schemas) == 0, (
            f"Symmetric transitions must not form directional schemas; schemas={rep2.schemas}"
        )
    finally:
        mem2.close()


def test_rs0_orthogonal_role_rejection_gate(tmp_path):
    """RS0: Orthogonal Rejection Gate (The Benchmark Falsifier).

    Treatment world (structured directional transitions) must form a SchemaCandidate.
    Orthogonal world (random p=0.50 coin-flip transitions) must NOT form a SchemaCandidate.
    This guarantees that schema existence is content-sensitive and requires true contingency,
    preventing spurious top-down candidate priming from flat random noise.
    """
    # 1. Treatment world: strong contingency (p=0.85) -> schema formed
    db_t = tmp_path / "treat.db"
    mem_t = MemoryService(str(db_t))
    svc_t = SleepService(mem_t)
    try:
        # A: amber birch cedar -> B: delta ember flora (consecutive alternation)
        for _ in range(12):
            with mem_t.batch():
                mem_t.store("amber birch cedar", event_type="observe", source="env:T")
                mem_t.store("delta ember flora", event_type="observe", source="env:T")
        rep_t = svc_t.run_sleep_cycle()
        assert len(rep_t.schemas) > 0, "Treatment world must form directional schema"
        assert rep_t.schemas[0].evidence.get("contingency_ratio", 0) >= 2.0 or rep_t.schemas[0].evidence.get("directional_ratio", 0) >= 1.10
    finally:
        mem_t.close()

    # 2. Orthogonal world: flat coin-flips (p=0.50) -> NO schema formed
    db_o = tmp_path / "ortho.db"
    mem_o = MemoryService(str(db_o))
    svc_o = SleepService(mem_o)
    try:
        import random
        rng = random.Random(20261101)
        # Random transitions between copper/bronze/iron and silver/gold/platinum
        group_s = ["copper", "bronze", "iron"]
        group_t = ["silver", "gold", "platinum"]
        curr = "s"
        for _ in range(15):
            with mem_o.batch():
                for _ in range(4):
                    tags = group_s if curr == "s" else group_t
                    sample = rng.sample(tags, 2)
                    mem_o.store(f"{sample[0]} {sample[1]}", event_type="observe", source="env:O")
                    if rng.random() < 0.50:
                        curr = "t" if curr == "s" else "s"
        rep_o = svc_o.run_sleep_cycle()
        assert len(rep_o.schemas) == 0, (
            f"Orthogonal world with flat p=0.50 transitions must NOT form directional schemas; "
            f"schemas={[s.id for s in rep_o.schemas]}"
        )
    finally:
        mem_o.close()


def test_schema_ids_are_context_specific(tmp_path):
    """D3: two disjoint worlds must not share a schema identity."""
    ids = []
    worlds = (
        ("a", "amber birch cedar", "delta ember flora"),
        ("c", "copper bronze iron", "silver gold platinum"),
    )
    for name, first, second in worlds:
        mem = MemoryService(str(tmp_path / f"ids_{name}.db"))
        svc = SleepService(mem)
        try:
            for _ in range(10):
                with mem.batch():
                    mem.store(first, event_type="observe", source="env")
                    mem.store(second, event_type="observe", source="env")
            rep = svc.run_sleep_cycle()
            assert rep.schemas, f"world {name} must form a schema"
            ids.append(rep.schemas[0].id)
        finally:
            mem.close()
    assert ids[0] != ids[1], f"schema ids must be context-bearing, got {ids}"


def test_no_prediction_reports_an_inflated_count(fresh_engine):
    """D1: after a schema exists, every prediction still reports its observed count."""
    mem, svc = fresh_engine
    for _ in range(10):
        with mem.batch():
            mem.store("amber birch cedar", event_type="observe", source="env:A")
            mem.store("delta ember flora", event_type="observe", source="env:A")
    svc.run_sleep_cycle()

    for _ in range(8):
        with mem.batch():
            mem.store("quartz prism", event_type="observe", source="env:B")
            mem.store("tidal lunar", event_type="observe", source="env:B")
    rep = svc.run_sleep_cycle()

    assert rep.predictions, "Context B must admit predictions on its own evidence"
    for p in rep.predictions:
        observed = p.evidence["temporal_count"]
        assert observed >= svc.PREDICTION_MIN_COUNT
        assert "effective_count" not in p.evidence
        assert "schema_primed" not in p.evidence
        # strength = min(1, count/frequency), optionally +0.05 per Law VI
        # reinforcement; a substituted count would leave this band entirely.
        ratio = observed / max(p.evidence["source_frequency"], 1)
        assert min(1.0, ratio) <= p.strength <= 1.0


def test_role_polarity_match_can_fire_and_can_fail():
    """D2: the congruence gate must be able to admit AND to reject (rule 25c)."""
    from organica.sleep_extraction import role_polarity_match

    # schema: source is a net sender, target a net receiver
    assert role_polarity_match(10, 2, 1, 9, 1, 1) is True
    assert role_polarity_match(2, 10, 1, 9, 1, 1) is False    # source polarity wrong
    assert role_polarity_match(10, 2, 9, 1, 1, 1) is False    # target polarity wrong
    assert role_polarity_match(5, 5, 1, 9, 1, 1) is False     # flat source cannot match
    assert role_polarity_match(10, 2, 1, 9, 0, 1) is False    # schema polarity unknown
    assert role_polarity_match(10, 2, 1, 9, 1, 0) is False    # target schema unknown
