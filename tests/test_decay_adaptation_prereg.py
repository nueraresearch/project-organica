"""The decay-adaptation pre-registration is frozen, executable, and checkable."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from benchmarks import decay_adaptation_prereg as guard

ROOT = Path(__file__).resolve().parents[1]


def load():
    text = (ROOT / "docs" / "DECAY-ADAPTATION-PREREGISTRATION.md").read_text(encoding="utf-8")
    registry = json.loads(
        (ROOT / "docs" / "research_question_registry.json").read_text(encoding="utf-8")
    )
    return text, registry


def load_artifact():
    path = ROOT / "docs" / "decay_adaptation.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def unrun(text):
    frozen, sep, _ = text.partition("\n## 12. Outcome")
    assert sep
    frozen = frozen.replace("executions: 1", "executions: 0", 1)
    return frozen + "\n## 12. Outcome\n\n**Not yet written.** No cell has run.\n"


def problems(text, registry, artifact=None, seeds_used=()):
    return guard.validate(text, registry, artifact, seeds_used=seeds_used)


def test_clean_protocol_passes():
    text, registry = load()
    artifact = load_artifact()
    if artifact is not None:
        assert problems(text, registry, artifact) == []
    else:
        assert problems(text, registry) == []


def test_unrun_protocol_passes_with_the_question_open():
    text, registry = load()
    reopened = copy.deepcopy(registry)
    entry = next(q for q in reopened["questions"] if q.get("id") == guard.QUESTION)
    entry["status"] = "open"
    assert problems(unrun(text), reopened) == []


def test_an_edit_to_the_frozen_sections_moves_the_digest():
    text, registry = load()
    base = unrun(text)
    tampered = base.replace("Q048 found a threshold", "Q048 found  a threshold", 1)
    assert tampered != base
    assert any("digest" in item for item in problems(tampered, registry))


def test_execution_record_without_an_artifact_fails():
    text, registry = load()
    base = unrun(text)
    tampered = base.replace("executions: 0", "executions: 1", 1)
    assert tampered != base
    assert any("but no artifact exists" in item for item in problems(tampered, registry))


def test_artifact_without_an_execution_record_fails():
    text, registry = load()
    artifact = {
        "protocol_digest": guard.FROZEN_DIGEST,
        "seeds": list(guard.SEEDS),
        "arms": list(guard.ARMS),
        "families": list(guard.FAMILIES),
        "cells": [{}] * 40,
        "label": "NO_COST_DETECTED",
    }
    assert any("records 0 executions" in item for item in problems(unrun(text), registry, artifact))


def test_a_missing_section_fails():
    text, registry = load()
    tampered = unrun(text).replace("## 6. The endpoint, the delta and the margin\n", "", 1)
    assert any("missing section" in item for item in problems(tampered, registry))


def test_a_missing_decision_row_fails():
    text, registry = load()
    kept = [line for line in unrun(text).splitlines() if not line.startswith("| `BOTH_COST`")]
    assert any("no row for BOTH_COST" in item for item in problems("\n".join(kept), registry))


def test_an_unregistered_question_fails():
    text, registry = load()
    broken = copy.deepcopy(registry)
    broken["questions"] = [q for q in broken["questions"] if q.get("id") != guard.QUESTION]
    assert any("not in the registry" in item for item in problems(unrun(text), broken))


def test_a_question_without_the_preregistration_fails():
    text, registry = load()
    broken = copy.deepcopy(registry)
    entry = next(q for q in broken["questions"] if q.get("id") == guard.QUESTION)
    entry["preregistrations"] = []
    assert any("does not carry this pre-registration" in item for item in problems(unrun(text), broken))


def test_a_different_seed_block_fails():
    text, registry = load()
    tampered = unrun(text).replace(
        "seeds: 20302601, 20302602, 20302603, 20302604, 20302605",
        "seeds: 20302601, 20302602, 20302603, 20302604, 20302606",
        1,
    )
    assert any("seed block" in item for item in problems(tampered, registry))


def test_a_different_arm_block_fails():
    text, registry = load()
    tampered = unrun(text).replace(
        "arms: shipped, factor099, factor09925, no_decay",
        "arms: shipped, no_decay",
        1,
    )
    assert any("arms in the protocol" in item for item in problems(tampered, registry))


def test_a_used_seed_fails():
    text, registry = load()
    assert any("overlaps" in item for item in problems(unrun(text), registry, seeds_used={20302603}))


def test_a_brace_placeholder_fails():
    text, registry = load()
    assert any("brace" in item for item in problems(unrun(text) + "\n{unfilled}\n", registry))
