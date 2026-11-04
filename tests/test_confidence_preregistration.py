"""Guard the confidence-amendment pre-registration.

A protocol is only worth more than a paragraph if it is fixed before the run and
if its numbers are internally consistent.  This test checks the second half of
that, and the things this project has learned to check:

- the document exists and is committed **before** any cell runs;
- it contains no surviving ``{placeholder}`` (AGENTS rule 20);
- it names all three arms and all six streams, so a later edit cannot quietly
  drop the control arm or the regression stream;
- its seed block arithmetic is right: the confirmatory seeds divided by the grid
  must equal the per-cell seed count, the reserve must start where the
  confirmatory block ends, and the grid size must equal the product of arms,
  streams and seeds;
- the thresholds are not self-serving: the pass bar for G5 on the lookback
  ablation must exceed a bare majority of the seeds, and the failure bar for the
  frozen arm must be low enough that the premise can fire;
- it says the frozen engine is untouched, because the amendment is authorized as
  a study and not as an edit.

Nothing here reads a result: no artifact exists yet, and this test must pass
before one does.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOC = REPO / "docs" / "CONFIDENCE-POSTERIOR-PREREGISTRATION.md"

ARMS = ("share", "jeffreys", "laplace")
STREAMS = ("baseline", "no_branch", "cold_start", "cold_start_unbranched",
           "real_git_history", "wide_lookback")


def text() -> str:
    return DOC.read_text(encoding="utf-8")


def numbers_near(pattern: str, source: str) -> list[int]:
    """The integers captured by ``pattern``, flattened.

    ``re.findall`` returns tuples when a pattern has more than one group, so a
    two-range pattern yields ``[(a, b), (c, d)]`` rather than four integers.
    """
    out: list[int] = []
    for match in re.findall(pattern, source):
        groups = match if isinstance(match, tuple) else (match,)
        out.extend(int(group) for group in groups)
    return out


def flattened(source: str) -> str:
    """Prose with line breaks and emphasis markers removed, for phrase checks."""
    return " ".join(source.replace("*", "").replace("`", "").split())


def test_the_protocol_is_committed():
    assert DOC.is_file(), "the pre-registration is missing"


def test_no_placeholder_survives():
    # A placeholder is silent: it looks like a sentence.  Rule 20's guard.
    found = re.findall(r"\{[a-z_][a-z0-9_]*\}", text())
    assert found == [], f"unfilled placeholders in the protocol: {found}"


def test_every_arm_and_stream_is_named():
    body = text()
    missing_arms = [a for a in ARMS if "`%s`" % a not in body]
    missing_streams = [s for s in STREAMS if "`%s`" % s not in body]
    assert missing_arms == [], f"arms missing from the protocol: {missing_arms}"
    assert missing_streams == [], f"streams missing: {missing_streams}"


def test_the_seed_block_arithmetic_holds():
    body = text()
    confirmatory = numbers_near(r"`(70\d{7})`[–-]`(70\d{7})`", body)
    # Two ranges are declared: confirmatory, then reserve.
    assert len(confirmatory) == 4, (
        "the protocol must declare exactly two seed ranges; found %r" % (confirmatory,))
    c_start, c_end, r_start, r_end = confirmatory
    confirmatory_count = c_end - c_start + 1
    reserve_count = r_end - r_start + 1
    assert confirmatory_count == 12, confirmatory_count
    assert reserve_count == confirmatory_count, (
        "the reserve block should be the same size as the confirmatory block")
    assert r_start == c_end + 1, "the reserve must start where the confirmatory block ends"
    assert c_start > 700000724, (
        "the amendment must not draw from the Stage B block or its four spares")

    grid = len(ARMS) * len(STREAMS) * confirmatory_count
    assert str(grid) in body, f"the protocol does not state its grid size ({grid})"


def test_the_bars_can_fail_and_cannot_be_won_trivially():
    body = flattened(text())
    # The pass bar on the lookback ablation is a super-majority of 12 seeds...
    assert "at least 9 of 12" in body, "P1's pass bar is missing or was relaxed"
    # ...and the frozen arm's failure bar is a strict minority, so the premise
    # check can fire rather than being unreachable by construction.
    assert "at most 1 of 12" in body, "P1's failure bar is missing or was relaxed"
    assert "6 or more of 12" in body, "the premise check P0 is missing or was relaxed"
    assert "not read" in body, "P0 must say that P1 is not read when it fires"


def test_the_frozen_engine_is_declared_untouched():
    body = text()
    assert "`organica/` is not modified" in body
    assert "test_v1_freeze.py" in body
