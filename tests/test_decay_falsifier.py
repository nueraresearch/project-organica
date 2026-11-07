"""The decay falsifier must publish what the series says, and be able to fail."""

import json

from benchmarks import decay_falsifier as df


def _record():
    return json.loads(df.ARTIFACT.read_text(encoding="utf-8"))


def _series():
    raw = json.loads(df.RAW.read_text(encoding="utf-8"))
    row = next(r for r in raw["rows"] if r["colony"] == "FULL")
    return row["series"]


def test_the_recorded_counts_match_the_raw_series():
    record = _record()
    series = _series()
    assert record["theories"] == df.series_facts(series["theories"])
    assert record["beliefs"] == df.series_facts(series["beliefs"])


def test_the_recorded_verdict_follows_from_the_series():
    record = _record()
    series = _series()
    expected = df.verdict_for(series["theories"], series["beliefs"], int(record["cycles"]))
    assert record["verdict"] == expected["verdict"]
    assert record["falsifier_fired"] == expected["falsifier_fired"]


def test_the_result_describes_the_pinned_engine():
    record = _record()
    assert record["engine_pin_current"] is True
    assert record["engine_version"] == json.loads(
        (df.ROOT / "docs" / "engine_pin.json").read_text(encoding="utf-8")
    )["version"]


def test_verdict_falsified_when_theories_stay_live():
    result = df.verdict_for([2, 1, 3, 2], [1, 1, 1, 1], 4)
    assert result["verdict"] == "FALSIFIED"
    assert result["falsifier_fired"] is True


def test_verdict_reproduces_when_theories_die():
    result = df.verdict_for([3, 2, 0, 0], [4, 2, 0, 0], 4)
    assert result["verdict"] == "REPRODUCES"
    assert result["falsifier_fired"] is False


def test_verdict_intermittent_when_theories_return():
    result = df.verdict_for([3, 0, 0, 2], [4, 1, 0, 1], 4)
    assert result["verdict"] == "INTERMITTENT"
    assert result["falsifier_fired"] is False


def test_series_facts_count_cycles_not_items():
    facts = df.series_facts([0, 0, 2, 3, 0])
    assert facts == {"cycles": 5, "cycles_with_any": 2, "last_nonzero_cycle": 4, "at_end": 0}


def test_the_document_matches_a_fresh_render():
    record = _record()
    assert df.DOC.exists()
    assert df.DOC.read_text(encoding="utf-8") == df.render(record)


def test_a_verdict_that_does_not_follow_is_caught():
    record = _record()
    wrong = "FALSIFIED" if record["verdict"] != "FALSIFIED" else "REPRODUCES"
    found = df.problems(dict(record, verdict=wrong))
    assert any("verdict does not follow" in message for message in found), found


def test_a_stale_document_is_caught():
    record = _record()
    found = df.problems(dict(record, seed=-1))
    assert any("stale" in message for message in found), found


def test_the_artifact_itself_passes_its_own_check():
    assert df.problems(_record()) == []


def test_check_writes_nothing():
    artifact_before = df.ARTIFACT.read_bytes()
    doc_before = df.DOC.read_bytes()
    assert df.main(["--check"]) == 0
    assert df.ARTIFACT.read_bytes() == artifact_before
    assert df.DOC.read_bytes() == doc_before
