"""A3 — the mutation invariants, written before the primitive exists.

M1, M2 and M5 carry a bystander composite as the control: the test serialises its resolved
state and compares it byte for byte after the other composite is mutated.
"""
import json

import pytest

from benchmarks.v2_primitive import (
    FROZEN_TABLES,
    FrozenGraphError,
    Primitive,
    RetiredComposite,
    StaleVersion,
)


def _abc():
    return ("alpha", "bravo", "charlie"), (
        ("alpha", "bravo"), ("alpha", "charlie"), ("bravo", "charlie")
    )


@pytest.fixture
def store(tmp_path):
    with Primitive(tmp_path / "primitive.db") as primitive:
        yield primitive


def _frozen(store, cid):
    return json.dumps(store.resolve(cid), sort_keys=True, ensure_ascii=False)


def test_m1_a_mutation_leaves_a_bystander_byte_identical(store):
    key, edges = _abc()
    target = store.register(key, edges)
    bystander = store.register(("delta", "echo", "foxtrot"), (("delta", "echo"),))
    before = _frozen(store, bystander)

    store.add_member(target, ("charlie", "golf"), 1)
    assert _frozen(store, bystander) == before

    store.remove_member(target, ("charlie", "golf"), store.resolve(target)["version"])
    assert _frozen(store, bystander) == before


def test_m2_shared_atoms_are_immutable_and_their_binding_does_not_move(store):
    shared = ("alpha", "bravo")
    target = store.register(("alpha", "bravo", "charlie"), (shared, ("bravo", "charlie")))
    bystander = store.register(("alpha", "bravo", "delta"), (shared,))
    atom_before = store.atom(shared)
    before = _frozen(store, bystander)

    store.add_member(target, ("charlie", "echo"), 1)
    store.remove_member(target, shared, store.resolve(target)["version"])

    assert store.atom(shared) == atom_before
    assert store.resolve(bystander)["members"] == (shared,)
    assert _frozen(store, bystander) == before


def test_m3_a_mutation_is_atomic_versioned_and_rejects_a_stale_version(store):
    key, edges = _abc()
    cid = store.register(key, edges)
    first = store.resolve(cid)["version"]

    store.add_member(cid, ("charlie", "delta"), first)
    current = store.resolve(cid)["version"]
    assert current == first + 1

    with pytest.raises(StaleVersion):
        store.add_member(cid, ("delta", "echo"), first)
    assert store.resolve(cid)["version"] == current

    with pytest.raises(KeyError):
        store.remove_member(cid, ("zulu", "yankee"), current)
    assert store.resolve(cid)["version"] == current


def test_m4_retirement_preserves_the_id_and_the_members(store):
    key, edges = _abc()
    cid = store.register(key, edges)
    store.retire(cid, 1)

    assert store.resolve(cid)["retired"] is True
    assert store.resolve(cid)["members"] == tuple(sorted(edges))
    with pytest.raises(RetiredComposite):
        store.add_member(cid, ("charlie", "delta"), 2)


def test_m5_the_frozen_graph_is_read_only_to_the_primitive(store):
    assert store.table_names() == {
        "atoms", "composite_ids", "composites", "members", "tombstones"
    }
    store.assert_frozen_graph_untouched(FROZEN_TABLES)
    with pytest.raises(FrozenGraphError):
        store.assert_frozen_graph_untouched({"atoms"})

    source = (("alpha", "bravo"), ("bravo", "charlie"))
    snapshot = tuple(source)
    cid = store.register(("alpha", "bravo", "charlie"), source)
    store.add_member(cid, ("charlie", "delta"), 1)
    assert source == snapshot
