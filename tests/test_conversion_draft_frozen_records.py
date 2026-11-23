"""Every frozen conversion record's gates and control seeds must reach the draft.

The program draft is hand-maintained while each question also has its own frozen
record.  A record can therefore gain a gate or a control cell and leave the
draft describing an older protocol -- Q1's C9 and Q2's witness seed both had to
be carried over by hand.  Nothing checked that the draft still named them, so
the drift could return silently.

This check discovers the records by their own ``program.draft`` pointer, so a
new frozen record joins automatically.  For each one it requires every gate
name in ``gates`` and every control/witness-cell seed to appear in the draft.
Bootstrap seeds are excluded: they are reserved for resampling, not controls.

``test_the_check_can_fail`` feeds a synthetic record whose gate and seed are
absent and requires both to be reported.
"""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

DRAFT = REPO / "docs" / "PRESENCE-ASSERTION-CONVERSION-PREREGISTRATION.md"


def frozen_records() -> list[tuple[Path, dict]]:
    """The frozen records that name this draft as their program document."""
    wanted = DRAFT.relative_to(REPO).as_posix()
    found: list[tuple[Path, dict]] = []
    for path in sorted((REPO / "docs").glob("*prereg.json")):
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(body, dict):
            continue
        if (body.get("program") or {}).get("draft") != wanted:
            continue
        if not str(body.get("status", "")).startswith("FROZEN"):
            continue
        found.append((path, body))
    return found


def _seed_ints(value) -> set[int]:
    """Integers held under a seed-naming key, anywhere inside a control value."""
    found: set[int] = set()
    if isinstance(value, bool):
        return found
    if isinstance(value, int):
        return {value}
    if isinstance(value, dict):
        for key, item in value.items():
            if "seed" in key.lower():
                found |= _seed_ints(item)
            elif isinstance(item, (dict, list)):
                found |= _seed_ints(item)
    elif isinstance(value, list):
        for item in value:
            found |= _seed_ints(item)
    return found


def control_seeds(body: dict) -> set[int]:
    """The seeds of ``control_cell``/``witness_cell`` entries, not bootstrap seeds."""
    found: set[int] = set()
    for key, value in (body.get("design") or {}).items():
        if "control" in key.lower() or "witness" in key.lower():
            found |= _seed_ints(value)
    for key, value in body.items():
        if "control" in key.lower() or "witness" in key.lower():
            found |= _seed_ints(value)
    return found


def problems(text: str | None = None,
             records: list[tuple[Path | str, dict]] | None = None) -> list[str]:
    """Every gate or control seed a frozen record names but the draft does not."""
    text = DRAFT.read_text(encoding="utf-8") if text is None else text
    records = frozen_records() if records is None else records
    missing: list[str] = []
    for path, body in records:
        identity = body.get("prereg") or Path(path).name
        for gate in (body.get("gates") or {}):
            if gate not in text:
                missing.append("%s: gate %s is not in the draft" % (identity, gate))
        for seed in sorted(control_seeds(body)):
            if str(seed) not in text:
                missing.append("%s: control seed %d is not in the draft" % (identity, seed))
    return missing


def test_every_frozen_record_is_discovered():
    records = frozen_records()
    identities = {body.get("prereg") for _path, body in records}
    assert identities == {"PRESENCE-CONSTRUCT-1", "PRESENCE-CAP-1",
                          "PRESENCE-CONVERSION-1", "PRESENCE-CONVERSION-2"}
    for path, body in records:
        assert body.get("gates"), path
        assert control_seeds(body), path


def test_every_gate_and_control_seed_is_in_the_draft():
    assert problems() == []


def test_control_seed_extraction_excludes_the_bootstrap():
    cap = next(body for _path, body in frozen_records()
               if body.get("prereg") == "PRESENCE-CAP-1")
    seeds = control_seeds(cap)
    assert 20261100 in seeds
    assert 20611407 not in seeds, "the reserved bootstrap is not a control"


def test_the_check_can_fail():
    body = {
        "prereg": "PRESENCE-FAKE-1",
        "gates": {"Z9_never_written": "a gate the draft omits"},
        "design": {"control_cell": {"seed": 99999999}},
    }
    findings = problems("the draft mentions neither item\n", [("fake.json", body)])
    assert any("Z9_never_written" in finding for finding in findings), findings
    assert any("99999999" in finding for finding in findings), findings

# --- the three records must agree that no block waits for or depends on another.
QUESTIONS = {
    "PRESENCE-CONSTRUCT-1": "Q1",
    "PRESENCE-CAP-1": "Q2",
    "PRESENCE-CONVERSION-1": "Q3",
    "PRESENCE-CONVERSION-2": "Q4",
}


def ordering_problems(records=None) -> list[str]:
    """No block may wait for another, and each names the blocks that preceded it."""

    records = frozen_records() if records is None else records
    found: list[str] = []
    by_id = {body.get("prereg"): body for _path, body in records}
    if set(by_id) != set(QUESTIONS):
        found.append("the program does not have exactly the four frozen blocks")
    for identity, label in QUESTIONS.items():
        body = by_id.get(identity)
        if body is None:
            found.append("%s is not frozen" % label)
            continue
        text = (body.get("program") or {}).get("relationship") or ""
        if "frozen on its own" not in text:
            found.append("%s does not state it was frozen on its own" % label)
        if "not re-scored" not in text:
            found.append("%s does not say a later definition change is not re-scored" % label)
        if not any(marker in text.lower() for marker in
                   ("does not wait", "without waiting", "does not depend")):
            found.append("%s does not disclaim waiting or dependence" % label)
        # A block cannot name a block that froze after it: the earlier record is
        # immutable, so the naming runs forward from the blocks that preceded it.
        for other_identity in list(QUESTIONS)[:list(QUESTIONS).index(identity)]:
            other_label = QUESTIONS[other_identity]
            if other_label not in text:
                found.append("%s does not name %s" % (label, other_label))
    return found


def test_every_record_agrees_on_ordering_independence():
    assert ordering_problems() == []


def test_the_ordering_check_can_fail():
    records = [(path, copy.deepcopy(body)) for path, body in frozen_records()]
    cap = next(body for _path, body in records
               if body.get("prereg") == "PRESENCE-CAP-1")
    cap["program"]["relationship"] = (
        "This is the Q2 half, frozen on its own; it does not wait for other blocks and is "
        "not re-scored.")
    findings = ordering_problems(records)
    assert any("Q2 does not name Q1" in finding for finding in findings), findings

READING_HEADING = "## 6. Reading rule: a frozen protocol is not a result"


def reading_rule_problems(text: str) -> list[str]:
    start = text.find(READING_HEADING)
    if start < 0:
        return ["the draft has no reading-rule heading"]
    rule = text[start:]
    end = rule.find("\n## ", 1)
    rule = rule if end < 0 else rule[:end]
    found = []
    for phrase in ("a frozen protocol is not a result", "no synthesis may cite",
                   "result artifact", "FROZEN, NOT RUN"):
        if phrase.lower() not in rule.lower():
            found.append("the reading rule does not say %r" % phrase)
    if "Q1" not in rule or "passed" not in rule:
        found.append("the reading rule does not name Q1 and the passed claim")
    return found


def test_the_draft_forbids_citing_an_unrun_block_as_passed():
    rule = DRAFT.read_text(encoding="utf-8")
    assert reading_rule_problems(rule) == []
    for _path, body in frozen_records():
        if body.get("no_cells_run"):
            # The rule cuts both ways: a frozen record that has run must carry its result,
            # and one that has not must not carry a result it never produced.
            assert body["status"] == "FROZEN, NOT RUN", body.get("prereg")
            assert "result" not in body, body.get("prereg")
            continue
        assert body["status"] == "FROZEN, RUN"
        assert body["no_cells_run"] is False
        assert (REPO / body["result"]["artifact"]).exists(), body["result"]["artifact"]
        auth = body["authorisation"]
        assert auth["granted"] is True
        assert auth["granted_on"] in (REPO / auth["document"]).read_text(encoding="utf-8")
        assert (REPO / auth["document"]).exists(), auth["document"]


def test_the_reading_rule_check_can_fail():
    assert reading_rule_problems("## 6. Reading rule\n\nno synthesis may cite Q1 as passed\n")
