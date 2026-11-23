"""The programme label and the release line must not be confused with a version number."""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

from pathlib import Path

import organica

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "RELEASE-LINE.md"


def test_the_release_line_is_recorded_as_pre_1_and_targets_0_20() -> None:
    text = " ".join(DOC.read_text(encoding="utf-8").split())
    assert "pre-1.0" in text
    assert "0.20.0" in text
    assert "not a 2.x release" in text
    assert "programme label, not a version number" in text


def test_the_charter_links_it() -> None:
    charter = (ROOT / "docs" / "DECISION-V2-CHARTER.md").read_text(encoding="utf-8")
    assert "RELEASE-LINE.md" in charter
    assert "0.20.0" in charter


def test_the_manual_holds_the_three_namespaces_and_the_release_line() -> None:
    manual = (ROOT / "docs" / "USER-MANUAL.md").read_text(encoding="utf-8")
    assert "### 11.6 The three version namespaces" in manual
    assert "**0.15.0**, pre-1.0" in manual
    assert "planned as **0.20.0**" in manual


def test_the_shipped_version_is_the_one_the_release_line_records() -> None:
    # 0.16.0 is the K1S admission build. This is the stop-check for the next bump:
    # a version that moves without this line moving is a build nobody recorded.
    assert organica.__version__ == "0.16.0"
