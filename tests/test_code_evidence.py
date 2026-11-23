"""The engine still does what the analysis says it does.

Every claim in docs/code_evidence.json names a regex that must match a source file. If a future change breaks
one, this fails before any document can keep quoting the claim.
"""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = json.loads((ROOT / "docs" / "code_evidence.json").read_text(encoding="utf-8"))
DOC = ROOT / "docs" / "CODE-AS-EVIDENCE.md"


def test_every_anchor_still_matches_the_engine() -> None:
    misses = []
    for claim in EVIDENCE["claims"]:
        for anchor in claim["anchors"]:
            source = (ROOT / anchor["path"]).read_text(encoding="utf-8")
            if not re.search(anchor["regex"], source):
                misses.append((claim["id"], anchor["path"], anchor["regex"]))
    assert not misses, misses


def test_the_absence_check_still_finds_no_membership_mutation() -> None:
    claim = next(c for c in EVIDENCE["claims"] if c["id"] == "no-membership-mutation-exists")
    pattern = claim["absence_check"]["pattern"]
    hits = [Path(p).name for p in glob.glob(str(ROOT / "organica" / "*.py"))
            if re.search(pattern, Path(p).read_text(encoding="utf-8"))]
    assert hits == [], hits


def test_the_analysis_restates_every_claim_and_correction() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "In one paragraph." in text
    for claim in EVIDENCE["claims"]:
        assert claim["id"] in text, claim["id"]
    for correction in EVIDENCE["corrections"]:
        assert correction["id"] in text, correction["id"]
    assert "{" not in text


def test_the_open_questions_are_named_and_not_answered_by_fiat() -> None:
    text = DOC.read_text(encoding="utf-8")
    for marker in ("O1", "O2", "O3", "O4"):
        assert marker in text
    assert len(EVIDENCE["open"]) == 4
