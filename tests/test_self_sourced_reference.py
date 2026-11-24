"""The self-sourcing reference must be the one its three artifacts support.

The reference rate that `docs/AUDIT-TRACE-SPEC.md` section 11 fixes was 17.9 %
for a month, measured by an observer that read sleep rows the engine never reads.
On 2026-11-23 it was re-derived to 0.0 % from the audit-trace probe's three
0.16.0 arms — data the reusable-knowledge rule does not judge (AGENTS rule 19).

These tests make the re-derivation mechanical (rules 27 and 29): the committed
artifact, the constant the harness reads, and the structural reason in the frozen
engine source must agree, and the checker must be able to reject a doctored arm.
"""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import copy
import json
from pathlib import Path

from benchmarks import reusable_knowledge as rk
from benchmarks import self_sourced_reference as reference

REPO = Path(__file__).resolve().parent.parent


def test_the_committed_reference_matches_the_three_audit_arms():
    ok, problems = reference.check()
    assert ok, problems
    assert json.loads(reference.OUT.read_text())["reference"] == 0.0


def test_the_constant_the_harness_reads_is_the_artifact_value():
    art = json.loads(reference.OUT.read_text())
    assert rk.SELF_SOURCED_REFERENCE == art["reference"]
    assert "docs/self_sourced_reference.json" in rk.REFERENCE_PROVENANCE
    assert art["derived_from"].startswith("data the rule does not judge")
    # the value is a zero, not an estimate: every arm must read self = 0
    for arm, block in art["arms"].items():
        assert block["populations"][reference.POPULATION]["self_sourced"] == 0, arm


def test_the_reference_is_asserted_against_the_frozen_engine_source():
    reason = reference.build()["structural_reason"]
    source = (REPO / "organica" / "memory.py").read_text(encoding="utf-8")
    assert reason["sql"] in source
    assert "WHERE event_type != 'sleep'" in reason["sql"]


def test_the_check_can_fail():
    expected = reference.build()
    doctored = copy.deepcopy(expected)
    doctored["arms"]["default"]["populations"][reference.POPULATION]["self_sourced"] = 1
    problems = reference.diff(expected, doctored)
    assert any("self_sourced" in problem for problem in problems), problems
