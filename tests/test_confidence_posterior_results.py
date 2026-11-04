"""Guard the confidence-amendment results document against its artifact.

The document is generated from ``docs/confidence_posterior.json``, and this test
is what makes that a fact rather than a habit: every number it quotes is
re-derived here from the artifact, and the reading it states must be the reading
the artifact's own analysis computed.

It also pins the one thing that must not be softened by a later edit: the
reading is **R3 — void**, because control C2 fired.  A document that reported
the amendment as supported would be reading a control failure as a result, which
is the defect this project's rule 13 exists to prevent.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOC = REPO / "docs" / "CONFIDENCE-POSTERIOR-RESULTS.md"
ARTIFACT = REPO / "docs" / "confidence_posterior.json"
PINNED = REPO / "docs" / "confidence_posterior_pinned.json"


def artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def body() -> str:
    return DOC.read_text(encoding="utf-8")


def pinned() -> dict:
    return json.loads(PINNED.read_text(encoding="utf-8"))


def test_the_results_document_is_committed():
    assert DOC.is_file(), "the results document is missing"
    assert ARTIFACT.is_file(), "the artifact it reports is missing"
    assert PINNED.is_file(), "the pinned re-check it reports is missing"


def test_it_states_the_reading_the_artifact_computed():
    reading = artifact()["analysis"]["reading"]
    assert reading == "R3", (
        "the artifact's reading changed; the document must be regenerated, "
        "not hand-edited")
    assert "R3" in body()
    assert "void" in body().lower()


def test_it_does_not_read_the_control_failure_as_a_result():
    text = body()
    assert "C2" in text, "the failing control must be named"
    # No part of the document may present the amendment as supported.
    for forbidden in ("R1 —", "R1 -", "supports the amendment",
                      "confirms the amendment", "the formula was the constraint"):
        assert forbidden not in text, forbidden


def test_every_quoted_g5_count_is_the_artifact_s():
    text = body()
    counts = artifact()["analysis"]["g5_present_counts"]
    for arm in ("share", "jeffreys"):
        for stream in ("baseline", "wide_lookback", "real_git_history",
                       "cold_start_unbranched"):
            value = counts[arm][stream]
            row = re.search(r"\| `%s` \| `%s` \| [^|]+ \| [^|]+ \| (\d+)/12"
                            % (stream, arm), text)
            assert row, f"no row for {stream}/{arm}"
            assert int(row.group(1)) == value, (stream, arm, row.group(1), value)


def test_the_premise_finding_is_stated_with_its_number():
    counts = artifact()["analysis"]["g5_present_counts"]
    frozen = counts["share"]["real_git_history"]
    assert frozen >= 1, "the premise finding would not fire"
    text = body()
    assert f"{frozen}/12" in text, "the non-reproduced premise must carry its count"


def test_the_unpinned_stream_is_disclosed_with_the_pinned_number():
    """The withdrawn premise must be reported, with the check that withdrew it."""
    record = pinned()
    text = body()
    assert str(record["corpus_events"]) in text, (
        "the document must state the corpus the re-check ran on")
    assert record["corpus_sha256"][:12] in text, "the corpus hash must be quoted"
    stored = artifact()["analysis"]["g5_present_counts"]["share"]["real_git_history"]
    now = record["arms"]["share"]["g5"]
    assert now != stored, (
        "the re-check reproduces the stored figure; there is nothing to withdraw")
    assert f"{now}/12" in text, "the pinned G5 count must be quoted"
    lowered = text.lower()
    assert "withdrawn" in lowered, "the premise must be withdrawn, not restated"
    assert "not pinned" in lowered or "never pinned" in lowered, (
        "the document must name the defect that caused it")
    assert "supports the amendment" not in lowered


def test_the_mechanism_diagnostic_matches_the_cells():
    cells = artifact()["cells"]
    # Two streams are bit-identical across arms, which is what the document says.
    for stream in ("wide_lookback", "cold_start_unbranched"):
        medians = {}
        for arm in ("share", "jeffreys", "laplace"):
            values = [c["confidence_median_final"] for c in cells
                      if c["stream"] == stream and c["arm"] == arm]
            medians[arm] = set(values)
        assert len(set.union(*medians.values())) <= 1, (
            f"{stream} should be identical across arms; the document says so")
    # ``real_git_history`` moves slightly, so the claim there is about G5 only.
    counts = artifact()["analysis"]["g5_present_counts"]
    assert len({counts[a]["real_git_history"]
                for a in ("share", "jeffreys", "laplace")}) == 1
    # ...and baseline must differ, or the override would not be live at all.
    base = {}
    for arm in ("share", "jeffreys", "laplace"):
        base[arm] = {c["confidence_median_final"] for c in cells
                     if c["stream"] == "baseline" and c["arm"] == arm}
    assert base["share"] != base["jeffreys"], "the override is not live on baseline"


def test_no_placeholder_survives():
    found = re.findall(r"\{[a-z_][a-z0-9_]*\}", body())
    assert found == [], f"unfilled placeholders: {found}"
