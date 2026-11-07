"""The tuning cycle's seeds must be fresh and its phases must stay apart.

The exploratory phase may read the 448-cell calibration; the confirmatory phase
may not. These checks are mechanical: no recorded seed appears in any other file,
and the design record states the separation instead of implying it.
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "decay_tuning_cycle.json"
DOC = ROOT / "docs" / "DECAY-TUNING-CYCLE.md"
SELF = {str(ARTIFACT.relative_to(ROOT)), str(DOC.relative_to(ROOT)),
        "tests/test_decay_tuning_cycle.py"}
# A derived inventory: Stage B's audit lists every consumed block, so it necessarily
# restates these seeds. That is registration, not reuse -- and it is asserted below.
INVENTORY = "docs/stage_b_protocol.json"


def _recorded():
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    return art, art["development_seeds"], art["confirmatory_seeds"]


def _seeds_elsewhere():
    """Every 8-digit seed-looking number in the repository, outside this record."""
    found = {}
    for folder in ("docs", "tests", "benchmarks", "research-journal", "papers"):
        base = ROOT / folder
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.suffix not in {".md", ".json", ".py", ".txt", ".cff"}:
                continue
            rel = str(path.relative_to(ROOT))
            if rel in SELF or rel == INVENTORY:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for number in re.findall(r"\b20\d{6}\b", text):
                found.setdefault(int(number), set()).add(rel)
    return found


def test_the_blocks_are_contiguous_disjoint_and_the_right_size():
    art, dev, conf = _recorded()
    assert len(dev) == 8 and len(conf) == 20
    assert dev == list(range(dev[0], dev[0] + 8))
    assert conf == list(range(conf[0], conf[0] + 20))
    assert dev[-1] < conf[0], "development and confirmatory blocks must not overlap"
    assert art["degree_ladder"] == [2, 4, 6, 12]


def test_no_recorded_seed_appears_anywhere_else_in_the_repository():
    _, dev, conf = _recorded()
    elsewhere = _seeds_elsewhere()
    clash = {seed: sorted(elsewhere[seed]) for seed in dev + conf if seed in elsewhere}
    assert clash == {}, "seeds already used elsewhere in the repository: %s" % clash


def test_the_scan_can_find_a_seed_that_is_used():
    """The scan must not be vacuous: the matrix seed is in the repository."""
    assert 20261023 in _seeds_elsewhere()


def test_the_stage_b_inventory_registers_the_block_as_consumed():
    """A declared block must be registered, so no later study can reallocate it."""
    _, dev, conf = _recorded()
    inventory = json.loads((ROOT / INVENTORY).read_text(encoding="utf-8"))
    seeds = inventory["seeds"]
    registered = seeds["consumed_blocks"]["docs/decay_tuning_cycle.json"]
    assert registered == dev + conf
    low, high = seeds["candidate_block"]
    assert set(seeds["overlap_with_consumed"]).isdisjoint(set(dev + conf))
    assert high < dev[0] or low > conf[-1], "the blocks must not overlap"


def test_the_record_keeps_the_phases_apart():
    text = DOC.read_text(encoding="utf-8")
    assert "docs/decay_tuning_cycle.json" in text
    assert "never confirmation" in text
    assert "exploratory" in text.lower()
    assert "degree-aware" in text
    assert "does not establish that\nevery real value fails" in text


def test_the_record_does_not_reuse_the_old_campaign_as_confirmation():
    assert "no old cell becomes confirmatory" in DOC.read_text(encoding="utf-8")


def test_a_record_that_drops_the_separation_fails_the_check():
    """The doc check must be able to fail."""
    text = DOC.read_text(encoding="utf-8")
    with pytest.raises(AssertionError):
        assert "never confirmation" in text.replace("never confirmation", "evidence")
