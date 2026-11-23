"""The `DI` construct audit must agree with the records it claims to summarise.



Two failure modes are worth a test. The first is transcription: a number in the

document that drifted from the artifact. The second is scope creep: the audit

promises no reliability coefficient, so a coefficient appearing in it would mean

the construct question had been answered by the thing that was supposed to wait

for it.

"""



from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer



import json

from pathlib import Path



import pytest



from benchmarks.di_construct_audit import OUT, SOURCE, build



ROOT = Path(__file__).resolve().parent.parent

DOC = ROOT / "docs" / "DI-CONSTRUCT-AUDIT.md"

DESIGN = ROOT / "docs" / "STRUCTURE-BEHAVIOR-DESIGN.md"





@pytest.fixture(scope="module")

def audit() -> dict:

    return build()





@pytest.fixture(scope="module")

def text() -> str:

    return DOC.read_text(encoding="utf-8")





def test_the_stored_artifact_is_current(audit):

    """Regenerating must reproduce the committed artifact exactly."""

    assert json.loads(OUT.read_text(encoding="utf-8")) == audit





def test_it_reads_the_records_it_claims(audit):

    assert audit["source"]["records"] == 240

    assert audit["source"]["path"].replace("\\", "/") == "docs/phase_l_results.json"

    assert len(audit["q3_construct"]["runs_per_arm"]) == 8

    assert set(audit["q3_construct"]["runs_per_arm"].values()) == {30}





def test_the_window_is_pre_arrival_in_these_records(audit):

    """The protocol's window must return one constant value, not a noisy estimate."""

    window = audit["q4_window"]["protocol_window"]

    assert window["cycles"] == [110, 150]

    assert window["zeros_share_mean"] == 1.0

    assert window["constant_records"] == 240

    assert window["distinct_window_means"] == 1

    assert window["mean_of_window_means"] == 0.0





def test_the_matched_post_arrival_window_is_still_at_the_floor(audit):

    matched = audit["q4_window"]["matched_post_arrival_window"]

    assert matched["cycles"] == [150, 190]

    assert matched["records_all_zero"] == 234

    assert matched["distinct_window_means"] == 5

    assert matched["zero_share"] > 0.99

    assert matched["icc"] < 0.10





def test_the_index_is_quantised_by_the_pair_count(audit):

    q2 = audit["q2_trajectory_value"]

    assert q2["late_available_per_record"] == [18]

    assert q2["quantised_to_pair_count"] is True

    assert q2["smallest_di_gap"] == pytest.approx(1 / 18, abs=1e-6)

    assert q2["distinct_final_di"] == 15

    assert q2["per_cycle_not_cumulative"] is True

    # A per-cycle snapshot can fall back to zero; an accumulator could not.

    assert q2["single_cycle_decreases"] > 0

    assert q2["non_decreasing_records"] < 240





def test_the_asymptote_is_configuration_not_signal(audit):

    q3 = audit["q3_construct"]

    assert q3["arm_label_share_of_between"] > 0.95

    assert q3["zero_arms"] == ["1:1", "1:2", "1:3", "1:4"]

    assert q3["median_within_run_sd"] == 0.0





def test_the_document_answers_all_five_questions(text):

    for heading in (

        "## 2. Q1 — where and how `DI` is calculated",

        "## 3. Q2 — what each `di_trajectory` value is",

        "## 4. Q3 — which construct `DI` is",

        "## 5. Q4 — the meaningful window, and the design's window",

        "## 6. Q5 — can measurement error be separated from developmental change?",

    ):

        assert heading in text





def test_the_document_quotes_the_artifact(text, audit):

    """The numbers a reader sees must be the numbers the script wrote."""

    window = audit["q4_window"]["protocol_window"]

    matched = audit["q4_window"]["matched_post_arrival_window"]

    q3 = audit["q3_construct"]

    q2 = audit["q2_trajectory_value"]



    assert f"**{window['constant_records']}/240 constant at exactly 0.0**" in text

    assert f"**{matched['records_all_zero']}/240 records all-zero**" in text

    assert f"ICC **{q3['icc']:.3f}**".replace("ICC ", "") in text

    assert f"{q3['arm_label_share_of_between'] * 100:.1f} %" in text

    assert f"**{q2['smallest_di_gap']:.6f}**" in text

    assert f"{q2['single_cycle_decreases']:,}" in text

    for arm, mean in q3["arm_means"].items():

        if mean == 0.0:

            continue

        assert f"| `{arm}` | {mean:.3f} |" in text





def test_no_reliability_coefficient_is_reported(text, audit):

    """The audit's contract is to settle the construct, not to produce the number."""

    assert audit["what_this_is"].endswith("no reliability coefficient.")

    assert "no reliability coefficient computed" in text

    assert "No coefficient is reported here." in text





def test_the_design_record_carries_the_dated_note():

    design = DESIGN.read_text(encoding="utf-8")

    assert "docs/DI-CONSTRUCT-AUDIT.md" in design

    assert "the window is contested, and unresolved" in design

    assert "no seed\n> is allocated" in design or "no seed is allocated" in design
