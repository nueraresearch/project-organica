"""The 3,000-cycle operability result must be reported as liveness, with its unit and
its missing bound stated, and its table must be checked against the record.

The figures are the owner's, transcribed from a run whose artifact is not in this
worktree, so the check pins the arithmetic and the provenance rather than pretending a
series was read. When `docs/decay_operability.json` is committed, the skip-guarded
checks start asserting against it instead of skipping.
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RECORD = ROOT / "docs" / "decay_operability_record.json"
ARTIFACT = ROOT / "docs" / "decay_operability.json"
PROPOSAL = ROOT / "docs" / "DECAY-OPERABILITY-PROPOSAL.md"
RERUN = ROOT / "docs" / "RERUN-0.12.0.md"


def _rec():
    return json.loads(RECORD.read_text(encoding="utf-8"))


def _flat():
    return " ".join(PROPOSAL.read_text(encoding="utf-8").split())


def test_the_two_horizons_are_derived_from_the_reported_masses():
    rec = _rec()
    old, new = rec["two_horizons"]
    assert old["mass_start"] == new["mass_start"] == 1819
    assert old["mass_final"] == 6981 and old["cycles"] == 80
    assert new["mass_final"] == 197753 and new["cycles"] == 3000
    assert old["ratio"] == round(old["mass_final"] / old["mass_start"], 3)
    assert new["ratio"] == round(new["mass_final"] / new["mass_start"], 3)
    assert rec["derived"]["edge_mass_ratio_end_over_first"] == new["ratio"]
    assert rec["derived"]["edge_mass_per_cycle"] == round(
        (new["mass_final"] - new["mass_start"]) / (new["cycles"] - 1), 3)


def test_the_mass_is_named_as_weight_and_not_as_edges():
    mass = _rec()["edge_mass"]
    assert "SUM(precedes.count)" in mass["quantity"]
    assert mass["not"].startswith("not a row count")
    flat = _flat()
    assert "SUM(precedes.count)" in flat
    assert "not 197,753 distinct edges" in flat
    assert "accumulated weight, not a row count" in flat


def test_growth_is_reported_and_explicitly_not_judged():
    assert _rec()["growth_criterion"].startswith("unset")
    assert "reported and not judged" in _rec()["growth_criterion"]
    flat = _flat()
    assert "No bar existed" in flat
    assert "taken from the run it judges" in flat
    assert "One seed, one stimulus, one horizon" in flat


def test_a_mean_rate_is_not_offered_as_the_trajectory():
    assert "a mean rate is not a trajectory" in _rec()["derived"]["note"]
    assert "not a trajectory" in _flat()
    assert "decile snapshots" in _flat()


def test_the_record_certifies_liveness_and_refuses_soundness():
    rec = _rec()
    assert rec["certifies"] == "liveness at 3,000 cycles for the decay-off arm"
    refused = " ".join(rec["does_not_certify"])
    assert "resource soundness" in refused
    assert "decay verdict" in refused
    assert "0.9.0 versus 0.12.0" in refused
    flat = _flat()
    assert "does not certify resource soundness" in flat
    assert "does not show decay is useless" in flat


def test_the_figures_are_labeled_as_transcribed_and_the_artifact_is_named():
    prov = _rec()["provenance"]
    assert prov["figures"] == "owner-reported, transcribed"
    assert prov["artifact"] == "docs/decay_operability.json"
    assert "absent" in prov["artifact_here"]
    flat = _flat()
    assert "owner's, transcribed" in flat
    assert "not in this worktree" in flat
    assert "rule 27" in flat


def test_the_document_and_record_agree_on_every_figure():
    rec = _rec()
    flat = _flat()
    old, new = rec["two_horizons"]
    assert f"1,819 -> {old['mass_final']:,}" in flat
    assert f"1,819 -> {new['mass_final']:,}" in flat
    assert f"×{old['ratio']}" in flat and f"×{new['ratio']}" in flat
    assert f"{rec['derived']['edge_mass_per_cycle']} mass per cycle" in flat
    assert "live through cycle 2,999" in flat


def test_the_eighty_cycle_row_still_matches_the_rerun_record():
    rerun = " ".join(RERUN.read_text(encoding="utf-8").split())
    old = _rec()["two_horizons"][0]
    assert f"{old['mass_start']:,} -> {old['mass_final']:,}" in rerun
    assert str(old["cycles"]) in rerun


def test_the_result_is_recorded_beside_the_counterfactual_in_the_same_section():
    text = PROPOSAL.read_text(encoding="utf-8")
    assert "## 4. The 3,000-cycle operational measurement" in text
    section = text.split("## 4. The 3,000-cycle operational measurement", 1)[1]
    section = section.split("## 5.", 1)[0]
    assert "RERUN-0.12.0.md" in section
    assert "80 cycles" in section and "3,000 cycles" in section


def test_no_growth_bound_is_invented_anywhere():
    rec = _rec()
    joined = " ".join(rec["caveats"])
    assert "no bar existed" in joined
    assert not re.search(r"(max|ceiling|bound)\s*(of|=)\s*\d", json.dumps(rec), re.I)


def test_the_record_consumes_no_seeds():
    raw = RECORD.read_text(encoding="utf-8")
    assert not re.search(r"\b20\d{6}\b", raw)
    assert not any("seed" in key for key in _rec())


def test_the_document_has_no_placeholders():
    assert not re.search(r"\{[a-z_]+\}", PROPOSAL.read_text(encoding="utf-8"))


@pytest.mark.skipif(ARTIFACT.exists(), reason="the run artifact is here; it is the authority")
def test_a_transcription_says_it_is_one():
    assert not ARTIFACT.exists()
    assert _rec()["provenance"]["authority"].startswith("the artifact once committed")


@pytest.mark.skipif(not ARTIFACT.exists(), reason="the run artifact has not been committed")
def test_the_record_matches_the_artifact_when_it_lands():
    body = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    rec = _rec()
    assert body["cycles"] == rec["run"]["cycles"] == 3000
    assert body["comparison"]["decay_off_live"] is rec["arms"]["decay_off"]["liveness"]
    mass = body["arms"]["decay_off"]["summary"]["edge_mass_final"]
    assert mass == rec["edge_mass"]["final"]
    assert body["arms"]["decay_off"]["series"]["edge_mass"][0] == rec["edge_mass"]["start"]
    assert body["comparison"]["growth_criterion"] == rec["growth_criterion"]


def test_the_row_count_and_database_factor_make_the_mass_readable():
    mass = _rec()["edge_mass"]
    assert mass["rows_final"] == 27
    assert mass["mean_count_per_row"] == round(mass["final"] / mass["rows_final"], 1)
    assert _rec()["db"]["bytes_ratio_end_over_first"] == 1.55
    joined = " ".join(_rec()["does_not_certify"])
    assert "latency or CPU" in joined
    flat = _flat()
    assert "27 temporal-edge rows" in flat
    assert f"{mass['mean_count_per_row']:,} accumulated counts per pair" in flat
    assert "not 200,000 new edges" in flat
    assert "Storage did not track mass" in flat
    assert "Four cautions" in flat


def test_the_row_count_is_labeled_as_reported_not_checked_across_horizons():
    source = _rec()["edge_mass"]["row_count_source"]
    assert "owner-reported" in source
    assert "not something this record checked" in source
    assert "not something this table checked" in _flat()


def test_decay_necessity_is_unresolved_rather_than_refuted():
    necessity = _rec()["necessity"]
    assert necessity["status"] == "unresolved"
    assert "not run" in necessity["why"]
    assert "two points of the parameter range" in necessity["not"]
    flat = _flat()
    assert "Necessity is **unresolved**, not refuted" in flat
    assert "not about the parameter's role" in flat
    assert "decay is useless" in flat and "has not run" in flat
