"""The functional protocol must stay executable and pre-committed."""
from __future__ import annotations

import pathlib
import re

DOC = pathlib.Path("docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md")


def test_amendment_fixes_the_three_open_clauses():
    text = DOC.read_text(encoding="utf-8")
    assert "## 11. Amendment 1" in text
    assert "excluded from hyperparameter selection only" in text
    assert "refit on all 110" in text
    assert "exclude_self=True" in text
    assert "kept in the denominator with label zero" in text
    assert "0.50" in text and "self-majority" in text
    assert "not attributable" in text
    assert "G6 the disqualifier can fire" in text
    assert "### 11.5 Which baseline, which window" in text
    assert "not evaluable" in text
    assert "never pooled" in text


def test_seed_blocks_are_fresh_and_disjoint():
    """The protocol names each block by its bounds; both must be present."""
    text = DOC.read_text(encoding="utf-8")
    design = range(20270201, 20270206)
    confirmatory = range(20270206, 20270221)
    for block in (design, confirmatory):
        assert str(block[0]) in text and str(block[-1]) in text
    closed = set(range(20261201, 20261227)) | set(range(20270101, 20270121))
    assert closed.isdisjoint(set(design) | set(confirmatory))


def test_pass_direction_is_stated_once_and_consistently():
    """§4 and §9 must name the same bound; the endpoint is negative-is-better."""
    text = DOC.read_text(encoding="utf-8")
    assert "lower uncertainty bound" not in text
    sec9 = text.split("## 9. What a result would and would not mean", 1)[1].split("## 10.", 1)[0]
    assert "**upper** bound" in sec9
    assert "below zero" in sec9
    assert "did not move" in sec9
    assert "the wrong way" in sec9


def test_disqualifier_outcomes_are_all_named():
    """Every status the attribution can return must be fixed in the protocol."""
    text = DOC.read_text(encoding="utf-8")
    for status in ("not a transfer result", "not attributable", "not evaluable"):
        assert status in text
    assert "0.50" in text and "0.4999" in text and "0.90" in text


def test_no_cell_artifact_exists_yet():
    """The protocol says no cell has run; a result artifact appearing early is a defect."""
    assert not pathlib.Path("docs/functional_structure_study.json").exists()
    text = DOC.read_text(encoding="utf-8")
    assert "**Not built.**" in text
    assert not re.search(r"\{[a-z_]+\}", text)
