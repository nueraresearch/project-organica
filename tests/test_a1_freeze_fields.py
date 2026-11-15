"""Both freeze acts must carry the same selection-record fields, and none of them may be filled.

`DECISION-A1-C8-SELECTION` S2 requires the pool, the selected block and the constructor's identity
to be recorded in the freeze act before any cell runs. This test holds the two acts to a shared
field list, so one act cannot quietly lose a field the other keeps, and holds the acts to their
own words while they are unsigned.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from benchmarks import a1_freeze_fields

ROOT = Path(__file__).resolve().parents[1]
ACTS = [ROOT / "docs" / "A1-TARGET-FREEZE-ACT.md",
        ROOT / "docs" / "A1-TARGET-FREEZE-ACT-N20.md"]
START, END = "<!-- s2-fields:start -->", "<!-- s2-fields:end -->"

FIELDS = [
    "Act ID",
    "Competent pool per seed",
    "Competent pool digest",
    "Selected block per seed",
    "Selected block digest",
    "Row count per seed",
    "Constructor identity",
    "Constructor output digest",
    "Competence predicate",
    "Unfiltered selection",
]

STATES = {"`NOT RECORDED`", "`FIXED BY RECORD`"}


def section(text: str) -> str:
    if text.count(START) != 1 or text.count(END) != 1:
        raise AssertionError("the act does not carry exactly one s2-fields block")
    left, right = text.index(START) + len(START), text.index(END)
    if right < left:
        raise AssertionError("the s2-fields markers are out of order")
    return text[left:right]


def rows(text: str) -> list[tuple[str, str]]:
    """Field name and state for each row, skipping the header and the separator."""
    found = []
    for line in section(text).splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 3 or cells[0] in ("Field", "") or set(cells[0]) <= set("-"):
            continue
        found.append((cells[0].strip("`"), cells[2]))
    return found


def test_both_acts_carry_the_fields() -> None:
    for act in ACTS:
        names = [name for name, _ in rows(act.read_text(encoding="utf-8"))]
        assert names == FIELDS, act.name


def test_the_two_acts_cannot_drift_apart() -> None:
    first, second = (rows(act.read_text(encoding="utf-8")) for act in ACTS)
    assert [name for name, _ in first] == [name for name, _ in second]


def test_the_n20_act_is_generated_from_the_artifact() -> None:
    """The act's record is a render, so it cannot disagree with the artifact it describes."""
    assert a1_freeze_fields.problems() == []
    text = ACTS[1].read_text(encoding="utf-8")
    assert a1_freeze_fields.committed(text) == a1_freeze_fields.render()
    recorded = [name for name, _, state in a1_freeze_fields.fields() if state != "`NOT RECORDED`"]
    assert len(recorded) == 10, recorded


def test_every_row_is_now_recorded() -> None:
    """S2 is record-complete: nothing is left for the owner to fill by hand before signing."""
    blocked = {name: value for name, value, state in a1_freeze_fields.fields()
               if state == "`NOT RECORDED`"}
    assert blocked == {}
    values = {name: value for name, value, _ in a1_freeze_fields.fields()}
    assert "A1-C8-SELECTION-DISCLOSURE.md" in values["Unfiltered selection"]
    assert a1_freeze_fields._file_digest(a1_freeze_fields.DISCLOSURE) in values["Unfiltered selection"]


def test_the_pool_digest_describes_the_pool_not_the_block() -> None:
    """The first version digested the block under the pool's name; equal digests would hide that."""
    values = {name: value for name, value, _ in a1_freeze_fields.fields()}
    assert values["Competent pool digest"] != values["Selected block digest"]
    pools = a1_freeze_fields.pool(a1_freeze_fields.json.loads(
        a1_freeze_fields.ARTIFACT.read_text(encoding="utf-8")))
    assert [len(pools[seed]) for seed in sorted(pools)] == [38, 27, 37, 40, 32, 31]


def test_the_n4_act_records_nothing() -> None:
    """The N=4 block is not produced by the competence constructor, so nothing is derived for it."""
    states = [state for _, state in rows(ACTS[0].read_text(encoding="utf-8"))]
    assert states.count("`NOT RECORDED`") == len(states) - 1
    assert "**not** generated here" in ACTS[0].read_text(encoding="utf-8")


def test_a_stale_field_fails() -> None:
    text = ACTS[1].read_text(encoding="utf-8")
    doctored = text.replace("`3881af97", "`0000af97", 1)
    assert doctored != text
    assert a1_freeze_fields.problems(doctored), "a doctored digest passed the check"


def test_the_acts_still_withhold_the_signature() -> None:
    for act in ACTS:
        text = act.read_text(encoding="utf-8")
        assert "AWAITING THE OWNER'S SIGNATURE" in text, act.name
        assert "not signable while any row above reads `NOT RECORDED`" in text, act.name


def test_the_field_list_is_checked_not_remembered() -> None:
    """A field dropped from an act must fail, so the parser is proved on a doctored copy."""
    text = ACTS[0].read_text(encoding="utf-8")
    doctored = text.replace("| Constructor identity |", "| Something else |", 1)
    names = [name for name, _ in rows(doctored)]
    assert names != FIELDS
    assert "Constructor identity" not in names


def test_the_acts_cite_the_clause_that_requires_them() -> None:
    for act in ACTS:
        text = act.read_text(encoding="utf-8")
        assert "DECISION-A1-C8-SELECTION.md" in text, act.name
        assert "S2" in text, act.name
