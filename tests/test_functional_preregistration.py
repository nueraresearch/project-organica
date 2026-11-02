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


def test_seed_blocks_are_fresh_and_disjoint():
    text = DOC.read_text(encoding="utf-8")
    design = range(20270201, 20270206)
    confirmatory = range(20270206, 20270221)
    for seed in list(design) + list(confirmatory):
        assert str(seed) in text
    closed = set(range(20261201, 20261227)) | set(range(20270101, 20270121))
    assert closed.isdisjoint(set(design) | set(confirmatory))


def test_no_cell_artifact_exists_yet():
    """The protocol says no cell has run; a result artifact appearing early is a defect."""
    assert not pathlib.Path("docs/functional_structure_study.json").exists()
    text = DOC.read_text(encoding="utf-8")
    assert "**Not built.**" in text
    assert not re.search(r"\{[a-z_]+\}", text)
