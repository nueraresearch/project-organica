"""The functional protocol must stay executable and pre-committed."""
from __future__ import annotations

import json
import pathlib
import re

import pytest

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
    assert not re.search(r"\{[a-z_]+\}", text)


def test_run_order_is_explicit_and_not_circular():
    """§10 must sequence the blocks rather than require the design block to have passed itself."""
    text = DOC.read_text(encoding="utf-8")
    # The superseded rule forbade the design run that the design block is.
    assert ("no cell of any block may run until the harness and its gates are committed "
            "and the design block has passed") not in text
    sec10 = text.split("## 10.", 1)[1].split("## 11.", 1)[0]
    marks = ("**Build and commit.**", "**Design block only", "**Confirmatory block, only if")
    order = [sec10.index(m) for m in marks]
    assert order == sorted(order), order
    assert "20270201" in sec10 and "20270205" in sec10
    assert "20270206" in sec10 and "20270220" in sec10
    # The lock is explicit: the design block does not form the endpoint.
    assert "not formed on design seeds" in sec10
    assert "**The endpoint stays locked until step 3.**" in sec10



def test_design_boundary_and_limb_status_are_stated():
    """§10 must say what the design run computed, and what the limb's status means."""
    text = DOC.read_text(encoding="utf-8")
    # Flatten the line wrapping: these are claims, not typographic positions.
    sec10 = " ".join(text.split("## 10.", 1)[1].split("## 11.", 1)[0].split())
    assert "endpoint-derived diagnostic" in sec10
    assert "not attributable under the current provenance measure" in sec10
    assert "It does **not** say Organica failed to transfer" in sec10
    assert "endpoint_boundary" in sec10
    assert "What was actually computed and inspected" in sec10
    assert "**Computed.**" in sec10 and "**Withheld.**" in sec10
    assert "**Inspected.**" in sec10 and "**Concluded.**" in sec10
    # The two statements that contradicted the measurement must not return.
    assert "before any score is read" not in sec10
    assert "cannot make or withhold a claim on a design seed" not in sec10
    assert "instrument reading" in sec10
    # The recommendation is labelled as the owner's decision, never as an authorisation.
    assert "for the owner" in sec10
    assert "Nothing in this section authorises it" in sec10


def test_confirmatory_record_matches_the_artifact():
    """§10.4's figures are read off the artifact; a drift between them is a defect."""
    art_path = pathlib.Path("docs/functional_structure_confirmatory.json")
    if not art_path.exists():
        pytest.skip("confirmatory artifact not present in this checkout")
    art = json.loads(art_path.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")
    sec = " ".join(doc.split("### 10.4", 1)[1].split("## 11.", 1)[0].split())
    for window in ("primary", "co_primary"):
        block = art[window]
        for value in (block["pooled_delta"], block["interval"]["low"], block["interval"]["high"]):
            assert f"{value:.6f}" in sec, (window, value)
    assert f"{art['n']}" in sec
    assert art["status"] == art["primary"]["outcome"]
    assert art["primary"]["passed"] is False or art["primary"]["outcome"] == "improvement"
