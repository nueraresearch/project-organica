"""Tests that the world-edge distribution quoted in prose matches its artifacts.

Why this file exists
--------------------
On 2026-10-30 the owner reviewed the project's own reporting of the Gate 13
ranking failure and found one claim that was true but incomplete in a way that
mattered: the **rank of the first world edge** was reported — rank 31 in the
1-tag stimulus, rank 30 / 18 / 53 in the 2-tag seeds, rank 16 / 8 / 8 after the
LIMIT-4 separation — **without the distribution of the world's edges behind it**.
A first edge appearing early in a frequency ordering reads as though the
world's relations are nearly reachable by raising a budget. They are not.

The generalisable rule, recorded as manual finding 36:

    **A first edge at rank N is one edge arriving, not a set arriving.**

These tests are the mechanical half of that rule. They read the two artifacts,
compute the ranges, and assert that every range quoted in the documents is one
the artifacts support.

Discipline (mirrors AGENTS.md):

  * The check must be able to FAIL.  ``test_check_detects_a_drifted_range``
    feeds the checker a fabricated range and asserts that it is rejected.
  * Standard library only.
  * The one range that is *not* in the artifacts — "4-8 of 112", the figure
    quoted in correspondence before the correction — is allowed to appear
    ONLY where it is explicitly marked as superseded.
"""
from __future__ import annotations

import io
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

CARRIERS = [
    "docs/GATE13-RELATION-SEPARATION.md",
    "research-journal/phase_g_findings_20261021.md",
    "docs/USER-MANUAL.md",
    "docs/FACTS-SHEET.md",
    "CHANGELOG.md",
]

# The range quoted in correspondence before the correction.  It appears in the
# documents only inside the sentence that marks it as superseded.
SUPERSEDED = (4, 8)
SUPERSEDED_MARKERS = (
    "correspondence",
    "artifact says",
    "restated",
    "corrected",
    "superseded",
)

# "12 - 18 of 112", "12-18 of 112", "12–18 of 112"
RANGE_RE = re.compile(
    r"(\d{1,3})\s*[-–—−]\s*(\d{1,3})\s*(?:of|out of)\s*112"
)


def _norm(text: str) -> str:
    """Normalise dash variants and the spacing around them."""
    for dash in ("–", "—", "−"):
        text = text.replace(dash, "-")
    return re.sub(r"\s*-\s*", "-", text)


def paragraphs(text: str):
    """Yield (index, paragraph) with line breaks collapsed to spaces.

    Scanning whole paragraphs rather than lines is deliberate: a range can be
    split across a wrapped line, and a per-line scan would let it through.
    """
    norm = _norm(text)
    for i, para in enumerate(re.split(r"\n\s*\n", norm), 1):
        flat = re.sub(r"\s+", " ", para).strip()
        if flat:
            yield i, flat


@pytest.fixture(scope="module")
def allowed():
    """Every (low, high) range the artifacts support."""
    alloc = json.loads(
        io.open(REPO / "docs" / "gate13_allocation_rule.json", encoding="utf-8").read()
    )
    sweep = json.loads(
        io.open(REPO / "docs" / "gate13_capacity_sweep.json", encoding="utf-8").read()
    )

    pairs = set()

    by_k = {}
    for item in alloc:
        for k, row in item["global_top_k"].items():
            by_k.setdefault(k, []).append(row["covered"])
    for vals in by_k.values():
        pairs.add((min(vals), max(vals)))

    by_cap = {}
    for _seed, caps in sweep.items():
        for cap, row in caps.items():
            by_cap.setdefault(cap, []).append(row["covered_world_edges"])
    for vals in by_cap.values():
        pairs.add((min(vals), max(vals)))

    return pairs


def check_ranges(text: str, allowed) -> list:
    """Return the ranges quoted in `text` that no artifact supports."""
    problems = []
    for idx, para in paragraphs(text):
        for m in RANGE_RE.finditer(para):
            lo, hi = int(m.group(1)), int(m.group(2))
            if (lo, hi) in allowed:
                continue
            if (lo, hi) == SUPERSEDED and any(
                marker in para for marker in SUPERSEDED_MARKERS
            ):
                continue
            problems.append(
                f"paragraph {idx}: quotes the range {lo}-{hi} of 112, "
                "which no artifact supports"
            )
    return problems


class TestArtifactsAreReadable:
    def test_both_artifacts_parse(self):
        for name in ("gate13_allocation_rule", "gate13_capacity_sweep"):
            path = REPO / "docs" / (name + ".json")
            assert path.exists(), f"{name}.json is missing"
            data = json.loads(io.open(path, encoding="utf-8").read())
            assert data, f"{name}.json is empty"

    def test_the_distribution_is_what_the_correction_says(self, allowed):
        """The specific ranges the documents quote must be the artifact's."""
        expected = {
            "global_top_20": (0, 1),
            "global_top_40": (0, 2),
            "global_top_80": (8, 16),
            "global_top_160": (36, 55),
            "global_top_320": (106, 109),
            "cap_40": (1, 8),
            "cap_20": (0, 3),
        }
        alloc = json.loads(
            io.open(REPO / "docs" / "gate13_allocation_rule.json", encoding="utf-8").read()
        )
        sweep = json.loads(
            io.open(REPO / "docs" / "gate13_capacity_sweep.json", encoding="utf-8").read()
        )
        for label, expected_range in expected.items():
            if label.startswith("global_top_"):
                k = label.replace("global_top_", "")
                vals = [item["global_top_k"][k]["covered"] for item in alloc]
            else:
                cap = label.replace("cap_", "")
                vals = [
                    row["covered_world_edges"]
                    for caps in sweep.values()
                    for c, row in caps.items()
                    if c == cap
                ]
            assert (min(vals), max(vals)) == expected_range, (
                f"{label}: artifact says {min(vals)}-{max(vals)}, "
                f"the documents say {expected_range[0]}-{expected_range[1]}"
            )

    def test_the_expected_ranges_are_allowed(self, allowed):
        for pair in {(0, 1), (0, 2), (8, 16), (36, 55), (106, 109), (1, 8), (0, 3)}:
            assert pair in allowed, f"{pair} should be an artifact-supported range"


class TestDocumentsQuoteOnlyWhatTheArtifactsSupport:
    @pytest.mark.parametrize("rel", CARRIERS)
    def test_no_unsupported_range_is_quoted(self, rel, allowed):
        path = REPO / rel
        assert path.exists(), f"{rel} is missing"
        text = io.open(path, encoding="utf-8").read()
        problems = check_ranges(text, allowed)
        assert not problems, (
            f"{rel} quotes a range no artifact supports:\n" + "\n".join(problems)
        )

    @pytest.mark.parametrize("rel", CARRIERS)
    def test_the_distribution_is_present(self, rel):
        """A carrier must actually carry the distribution, not just the rank."""
        path = REPO / rel
        if not path.exists():
            pytest.skip(f"{rel} not present")
        text = _norm(io.open(path, encoding="utf-8").read())
        assert "106-109" in text, f"{rel} does not carry the top-320 range"
        assert "spread" in text, f"{rel} does not carry the spread statement"


class TestTheCheckCanFail:
    """A check that cannot disagree with its subject is not a check."""

    def test_check_detects_a_drifted_range(self, allowed):
        assert check_ranges("the top 20 recovers 0-1 of 112", allowed) == []
        problems = check_ranges("the top 20 recovers 12-18 of 112", allowed)
        assert problems, "the checker failed to notice an unsupported range"

    def test_check_detects_an_unsupported_upper_bound(self, allowed):
        problems = check_ranges("the top 40 recovers 0-99 of 112", allowed)
        assert problems

    def test_check_detects_a_range_split_across_a_wrapped_line(self, allowed):
        """A per-line scan would let this through; a paragraph scan must not."""
        wrapped = (
            "the figure *\"cap 40 recovers 4-8 of\n"
            "112\"* was carried in correspondence and is not what the artifact says"
        )
        assert check_ranges(wrapped, allowed) == []
        bare = "the figure *\"cap 40 recovers 4-8 of\n112\"* stands as the result"
        assert check_ranges(bare, allowed), (
            "a range split across a wrapped line escaped the check"
        )

    def test_the_superseded_range_is_allowed_only_when_marked(self, allowed):
        marked = 'the figure "cap 40 recovers 4-8 of 112" was carried in correspondence'
        assert check_ranges(marked, allowed) == []
        unmarked = "cap 40 recovers 4-8 of 112"
        assert check_ranges(unmarked, allowed), (
            "the checker allowed the superseded figure to stand as a claim"
        )
