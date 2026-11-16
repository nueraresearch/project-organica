"""A2 — the identifier invariants, written before the primitive exists.

Each test is a property the primitive must have, not a description of its implementation. The
suite is expected to fail at import until `benchmarks/v2_primitive.py` exists.
"""
import pytest

from benchmarks.v2_primitive import Primitive, StaleVersion, UnknownComposite


def _abc():
    return ("alpha", "bravo", "charlie"), (
        ("alpha", "bravo"), ("alpha", "charlie"), ("bravo", "charlie")
    )


@pytest.fixture
def store(tmp_path):
    with Primitive(tmp_path / "primitive.db") as primitive:
        yield primitive


def test_i1_the_id_survives_versions_member_changes_and_a_flip(store):
    key, edges = _abc()
    cid = store.register(key, edges)
    assert store.resolve(cid)["version"] == 1

    store.add_member(cid, ("charlie", "delta"), 1)
    assert store.resolve(cid)["id"] == cid
    assert store.resolve(cid)["version"] == 2

    flipped = ("alpha", "charlie", "bravo")
    assert store.register(flipped) == cid


def test_i2_the_id_is_not_computed_from_the_members(store):
    key_a, edges_a = _abc()
    key_b = ("delta", "echo", "foxtrot")
    a = store.register(key_a, edges_a)
    b = store.register(key_b, (("delta", "echo"),))

    assert isinstance(a, int) and isinstance(b, int)
    assert b == a + 1
    store.remove_member(a, ("bravo", "charlie"), store.resolve(a)["version"])
    assert store.resolve(a)["id"] == a
    assert ("bravo", "charlie") not in store.members(a)


def test_i3_retirement_writes_a_tombstone_and_never_reuses_the_id(store):
    key, edges = _abc()
    cid = store.register(key, edges)
    store.retire(cid, 1)

    tombstone = store.resolve(cid)
    assert tombstone["retired"] is True
    assert tombstone["members"] == tuple(sorted(edges))
    assert store.register(key) == cid  # the key is not freed either
    assert store.register(("delta", "echo")) == cid + 1


def test_i4_retrieval_accepts_the_id_and_only_the_id(store):
    key, edges = _abc()
    cid = store.register(key, edges)

    for bad in ("1", key, True, None, 1.0):
        with pytest.raises(TypeError):
            store.resolve(bad)
        with pytest.raises(TypeError):
            store.members(bad)
    with pytest.raises(UnknownComposite):
        store.resolve(cid + 100)


def test_i5_an_id_names_the_object_and_a_version_names_a_state(store):
    key, edges = _abc()
    cid = store.register(key, edges)
    first = store.resolve(cid)["version"]
    store.add_member(cid, ("charlie", "delta"), first)
    current = store.resolve(cid)["version"]

    assert current == first + 1
    assert store.resolve(cid, version=current)["id"] == cid
    with pytest.raises(StaleVersion):
        store.resolve(cid, version=first)
