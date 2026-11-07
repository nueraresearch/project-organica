"""The persistence repair pre-registration is frozen, unrun, and checkable.

These tests tamper with one thing at a time and require the corresponding failure; a guard that
only ever sees a clean protocol has not been shown to fire.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from benchmarks import persistence_repair_prereg as guard

ROOT = Path(__file__).resolve().parents[1]


def load():
    text = (ROOT / "docs" / "PERSISTENCE-REPAIR-PREREGISTRATION.md").read_text(encoding="utf-8")
    registry = json.loads(
        (ROOT / "docs" / "research_question_registry.json").read_text(encoding="utf-8")
    )
    return text, registry


def problems(text, registry, artifact=None, seeds_used=()):
    return guard.validate(text, registry, artifact, seeds_used=seeds_used)


def test_clean_protocol_passes():
    text, registry = load()
    assert problems(text, registry) == []


def test_any_edit_to_the_frozen_sections_moves_the_digest():
    text, registry = load()
    tampered = text.replace(
        "Q044 split every missed re-emission",
        "Q044 split  every missed re-emission",
        1,
    )
    assert tampered != text
    assert any("digest" in item for item in problems(tampered, registry))


def test_execution_record_without_an_artifact_fails():
    text, registry = load()
    tampered = text.replace("executions: 0", "executions: 1", 1)
    assert any("but no artifact exists" in item for item in problems(tampered, registry))


def test_artifact_without_an_execution_record_fails():
    text, registry = load()
    artifact = {
        "protocol_digest": guard.FROZEN_DIGEST,
        "seeds": list(guard.SEEDS),
        "label": "NEITHER",
    }
    found = problems(text, registry, artifact)
    assert any("records 0 executions" in item for item in found)


def test_a_missing_section_fails():
    text, registry = load()
    tampered = text.replace("## 6. The endpoint and the margin\n", "", 1)
    assert any("missing section" in item for item in problems(tampered, registry))


def test_a_missing_decision_row_fails():
    text, registry = load()
    lines = text.splitlines()
    kept = [line for line in lines if not line.startswith("| `NEITHER`")]
    assert len(kept) < len(lines)
    assert any("no row for NEITHER" in item for item in problems("\n".join(kept), registry))


def test_an_unregistered_question_fails():
    text, registry = load()
    broken = copy.deepcopy(registry)
    broken["questions"] = [q for q in broken["questions"] if q.get("id") != guard.QUESTION]
    assert any("not in the registry" in item for item in problems(text, broken))


def test_a_question_without_the_preregistration_fails():
    text, registry = load()
    broken = copy.deepcopy(registry)
    entry = next(q for q in broken["questions"] if q.get("id") == guard.QUESTION)
    entry["preregistrations"] = []
    assert any("does not carry this pre-registration" in item for item in problems(text, broken))


def test_a_different_seed_block_fails():
    text, registry = load()
    tampered = text.replace(
        "seeds: 20302101, 20302102, 20302103",
        "seeds: 20302101, 20302102, 20302104",
        1,
    )
    assert any("seed block" in item for item in problems(tampered, registry))


def test_a_used_seed_fails():
    text, registry = load()
    assert any("overlaps" in item for item in problems(text, registry, seeds_used={20302102}))


def test_a_brace_placeholder_fails():
    text, registry = load()
    assert any("brace" in item for item in problems(text + "\n{unfilled}\n", registry))
