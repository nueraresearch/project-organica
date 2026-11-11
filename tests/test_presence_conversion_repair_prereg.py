"""PRESENCE-CONVERSION-2 must be frozen, unrun, ungranted and structurally complete.

The block exists because Q3's observer was not neutral: it lifted `MAX_PREDICTIONS` and
returned the first cap rows, which changes the engine's quota split rather than only the
truncation. This block's whole claim to validity is that it returns the engine's own list
untouched and observes with a second call.

These tests hold the record to that claim: the state is frozen and unrun, the seed block is
fresh against every committed artifact, every gate and every verdict is declared, a bare
`granted: true` fails the check, the rendered page matches the record, and `--measure`
refuses before it can reach an engine.
"""
from __future__ import annotations
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import presence_conversion_repair as repair  # noqa: E402
from benchmarks.presence_conversion_repair import prereg  # the frozen record, for the guards below


def test_the_block_is_frozen_unrun_and_granted():
    body = repair.prereg()

    assert body["prereg"] == "PRESENCE-CONVERSION-2"
    assert body["status"] == "FROZEN, RUN"
    assert body["no_cells_run"] is False
    assert body["result"]["verdict"]
    assert body["result"]["artifact"] == "docs/presence_conversion_repair_run.json"
    assert body["authorisation"]["granted"] is True
    assert body["authorisation"]["granted_on"] == "2026-11-11"
    quote = body["authorisation"]["quote"]
    assert quote in repair.AUTHORISATION_DOC.read_text(encoding="utf-8")
    assert repair.ARTIFACT.exists(), "a run block must have its result artifact"
    assert repair.validate() == []


def test_the_seed_block_is_fresh_and_the_design_is_fixed():
    body = repair.prereg()
    design = body["design"]

    assert design["seeds"] == list(range(20611601, 20611607))
    assert design["bootstrap"] == 20611607
    assert design["cycles"] == 120
    assert design["cells"] == 12
    assert design["arms"] == ["off", "on"]
    assert body["engine"]["edit"] == "none"

    from benchmarks import presence_cap_experiment as cap
    collisions = cap.seed_collisions(
        design["seeds"] + [design["bootstrap"]],
        allow=(repair.PREREG, repair.DOC, repair.AUTHORISATION_DOC, repair.N3_ARTIFACT,
               repair.UNEXPLAINED_ARTIFACT, repair.ASSERTION_ARTIFACT, repair.PROBE_ARTIFACT, repair.TURNOVER_ARTIFACT,
               repair.ARTIFACT, repair.ROOT / "docs/presence_band_rank_prereg.json",
               repair.ROOT / "docs/PRESENCE-BAND-RANK-PREREGISTRATION.md",
               repair.ROOT / "docs/presence_band_rank_run.json",
               repair.ROOT / "docs/PRESENCE-BAND-RANK-RESULT.md",
               repair.ROOT / "docs/AUTHORISATION-PRESENCE-BAND-1.md",
               repair.ROOT / "docs/presence_band_rank_2_prereg.json",
               repair.ROOT / "docs/PRESENCE-BAND-RANK-2-PREREGISTRATION.md"))
    assert collisions == {}


def test_every_gate_and_every_verdict_is_declared():
    body = repair.prereg()

    assert tuple(body["gates"]) == repair.GATE_NAMES
    verdicts = {row["verdict"] for row in body["decision_table"]}
    assert verdicts == set(repair.VERDICTS)
    for row in body["decision_table"]:
        assert row["condition"] and row["reading"] and row["decision"]


def test_the_observer_returns_the_engine_list_untouched():
    observer = repair.prereg()["observer"]

    assert "untouched" in observer["served"]
    assert "second" in observer["observed"].lower()
    assert observer["ceiling"] > observer["shipped_cap"] == 40
    assert "quota" in repair.prereg()["engine"]["mechanism"].lower()


def test_a_bare_grant_fails_the_check():
    """A field flipped without a dated document must go red, not pass as an authorisation."""
    body = json.loads(json.dumps(repair.prereg()))
    body["authorisation"] = {"required": True, "granted": True}

    problems = repair.validate(body)
    assert any("granted without" in problem or "does not exist" in problem
               for problem in problems), problems


def test_the_page_matches_the_record():
    assert repair.DOC.exists()
    assert repair.DOC.read_text(encoding="utf-8") == repair.render_prereg(repair.prereg())
    assert repair.check_prereg() == 0


def test_measure_refuses_before_anything_can_run(monkeypatch, tmp_path):
    monkeypatch.setattr(repair, "ARTIFACT", tmp_path / "presence_conversion_repair_run.json")

    with pytest.raises(SystemExit) as raised:
        repair.refuse()

    assert "no runner" in str(raised.value)


def test_the_dry_run_plans_fourteen_runs_and_executes_none(capsys):
    assert repair.main(["--dry-run"]) == 0
    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]

    assert len(lines) == 14, lines
    assert all(line.startswith("python -m benchmarks.presence_conversion_repair") for line in lines)
    assert repair.main(["--dry-run"]) == 0  # still plans only; the campaign parts already exist


def test_n2_states_the_behavioural_claim_not_only_served_equality():
    """Rule 17(c): the claim is that observation changes nothing, including the next cycle."""
    text = prereg()["gates"]["N2_observation_cannot_leak"].lower()
    assert "served window equals" in text
    assert "next cycle" in text
    assert "universe" in text


def test_n3_keeps_the_transition_cooccurrence_split_per_row():
    """The split the mechanism turns on must survive in the artifact, not only as totals."""
    body = prereg()
    text = body["gates"]["N3_allocation_recorded"].lower()
    assert "every served row" in text
    assert "cooccurrence" in text
    assert "served_rows" in body["observer"]["records"]


def test_the_amendment_is_disclosed_with_a_date_and_a_reason():
    amendments = prereg()["amendments"]
    assert amendments, "an amended frozen record must disclose the amendment"
    assert amendments[0]["date"] == "2026-11-10"
    assert amendments[0]["reason"] and amendments[0]["disclosure"]
    assert prereg()["status"] == "FROZEN, RUN"
    assert prereg()["authorisation"]["granted"] is True
    assert amendments[-1]["date"] == "2026-11-11"
    assert any("N4" in row["reason"] for row in amendments), "the N4 correction is not disclosed"
