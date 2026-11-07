"""The operating-point pre-registration is frozen, executable, and checkable."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from benchmarks import operating_point_prereg as guard

ROOT = Path(__file__).resolve().parents[1]


def load():
    text = (ROOT / "docs" / "OPERATING-POINT-PREREGISTRATION.md").read_text(encoding="utf-8")
    registry = json.loads(
        (ROOT / "docs" / "research_question_registry.json").read_text(encoding="utf-8")
    )
    return text, registry


def load_artifact():
    path = ROOT / "docs" / "operating_point.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def unrun(text):
    """The committed protocol as it stood before any cell: no execution, no outcome."""
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
    tampered = base.replace("Q046 applied one uniform change", "Q046 applied  one uniform change", 1)
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
        "conditions": list(guard.CONDITIONS),
        "label": "NO_OPERATING_POINT",
    }
    assert any("records 0 executions" in item for item in problems(unrun(text), registry, artifact))


def test_a_missing_section_fails():
    text, registry = load()
    tampered = unrun(text).replace("## 6. The endpoint and the margin\n", "", 1)
    assert any("missing section" in item for item in problems(tampered, registry))


def test_a_missing_decision_row_fails():
    text, registry = load()
    kept = [line for line in unrun(text).splitlines() if not line.startswith("| `NO_DECAY_ONLY`")]
    assert any("no row for NO_DECAY_ONLY" in item for item in problems("\n".join(kept), registry))


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
        "seeds: 20302401, 20302402, 20302403",
        "seeds: 20302401, 20302402, 20302404",
        1,
    )
    assert any("seed block" in item for item in problems(tampered, registry))


def test_a_used_seed_fails():
    text, registry = load()
    assert any("overlaps" in item for item in problems(unrun(text), registry, seeds_used={20302402}))


def test_a_brace_placeholder_fails():
    text, registry = load()
    assert any("brace" in item for item in problems(unrun(text) + "\n{unfilled}\n", registry))
