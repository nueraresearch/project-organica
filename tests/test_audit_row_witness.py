"""The audit-row witness gates share one fingerprint and one comparison."""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import hashlib
import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import audit_row_witness as witness_rows
from benchmarks import presence_cap_experiment as cap
from benchmarks import presence_construct_audit as construct
from benchmarks import presence_conversion_observer as observer


def test_fingerprint_is_the_audit_recipe_and_covers_the_whole_set():
    assert witness_rows.fingerprint({("a", "b")}) == hashlib.sha256(
        b"a>b").hexdigest()[:16]
    whole = {("a", "b"), ("b", "c")}
    subset = {("a", "b")}
    assert witness_rows.fingerprint(whole) != witness_rows.fingerprint(subset)
    assert witness_rows.fingerprint(whole) == witness_rows.fingerprint(
        [("b", "c"), ("a", "b")])


def test_the_pair_digest_has_one_implementation():
    for module in (construct, cap):
        source = inspect.getsource(module._digest)
        assert "asserted_fingerprint(pairs)" in source
        assert "hashlib" not in source and "hexdigest" not in source, module.__name__
    assert "def _digest" not in inspect.getsource(observer)


def test_compare_names_every_differing_field_and_passes_an_equal_row():
    reference = {"present_world_edges": 3, "asserted_world_edges": 2,
                 "asserted_fingerprint": "abc"}
    assert witness_rows.compare(reference, dict(reference))["reproduces"] is True
    witness = dict(reference, asserted_fingerprint="def")
    result = witness_rows.compare(reference, witness, labels=witness_rows.LABELS)
    assert result["reproduces"] is False
    assert result["differs"] == ["asserted fingerprint"]
    assert result["audit"]["asserted_fingerprint"] == "abc"
    assert result["seen"]["asserted_fingerprint"] == "def"


def test_compare_to_audit_uses_the_published_row_and_reports_a_missing_seed():
    row = witness_rows.audit_row(20261100)
    assert row is not None
    witness = {field: row[field] for field in witness_rows.WITNESS_FIELDS}
    result = witness_rows.compare_to_audit(witness, 20261100)
    assert result["reproduces"] is True, result
    missing = witness_rows.compare_to_audit(witness, 1)
    assert missing["audit"] is None
    assert missing["differs"] == ["the witness seed is not in the audit"]


def test_all_three_blocks_build_the_fingerprint_through_the_shared_rule():
    for module in (construct, cap, observer):
        source = inspect.getsource(module)
        asserted_lines = [line for line in source.splitlines()
                          if '"asserted_fingerprint":' in line]
        assert asserted_lines, module.__name__
        assert all("fingerprint(" in line for line in asserted_lines), (
            module.__name__, asserted_lines)
    assert "witness_rows.compare(" in inspect.getsource(construct)


def test_c9_k5_x8_share_the_helper_not_a_private_comparison():
    q1 = inspect.getsource(construct)
    assert "audit_row(cell[" in q1 and "witness_rows.compare(" in q1
    assert "compare_to_audit(" in inspect.getsource(cap)
    assert "compare_to_audit(" in inspect.getsource(observer)
    for module in (construct, cap, observer):
        source = inspect.getsource(module)
        # No block may reintroduce a private audit-row comparison by hand.
        assert "reference[\"asserted_fingerprint\"]" not in source
