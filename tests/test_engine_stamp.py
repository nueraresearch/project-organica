"""An artifact that does not name its build cannot be attributed to one."""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import hashlib
import json

import pytest

from benchmarks import engine_stamp as es


def test_the_stamp_records_the_version_the_pinned_commit_and_the_bytes():
    record = es.stamp({"kind": "probe", "cells": 3})
    assert record["engine_version"] == es.engine_version()
    assert record["engine_commit"] == es.pinned_commit()
    assert record["engine_sha256"] == es.engine_sha256()
    assert record["kind"] == "probe" and record["cells"] == 3, "the stamp must not drop fields"


def test_the_runner_is_the_module_that_wrote_the_record():
    """The commit names the engine; this names the harness, which the commit cannot say."""
    assert es.stamp({"cells": 1})["runner"] == __name__
    assert es.stamp([{"cells": 1}, {"cells": 2}])[1]["runner"] == __name__, (
        "a list artifact must not name this module as its own writer")


def test_the_byte_digest_is_computed_from_the_pin_and_moves_when_one_file_does(monkeypatch):
    """A digest with no sensitivity to its input would name nothing."""
    pin = json.loads((es.ROOT / "docs/engine_pin.json").read_text(encoding="utf-8"))
    canonical = json.dumps(pin["files"], sort_keys=True, separators=(",", ":"))
    assert es.engine_sha256() == hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    altered = dict(pin["files"])
    altered[sorted(altered)[0]] = "0" * 64
    monkeypatch.setattr(es.engine_pin, "load_pin", lambda: {"files": altered})
    assert es.engine_sha256() != hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_stamping_a_list_stamps_every_record_and_keeps_it_a_list():
    stamped = es.stamp([{"seed": 1}, {"seed": 2}])
    assert isinstance(stamped, list) and len(stamped) == 2
    assert all(es.missing(item) == [] for item in stamped)


def test_the_stamp_overwrites_a_stale_one():
    record = es.stamp({"engine_version": "0.0.0", "engine_commit": "0" * 40})
    assert record["engine_version"] == es.engine_version()
    assert record["engine_commit"] == es.pinned_commit()


def test_a_record_without_a_stamp_is_reported():
    assert es.missing({"engine_version": "1.2.3"}) == [
        "engine_commit", "engine_sha256", "runner"]
    assert es.missing({}) == ["engine_commit", "engine_sha256", "engine_version", "runner"]


def test_an_object_that_is_not_a_record_is_refused():
    """Silently writing an unstampable artifact is the failure this module prevents."""
    with pytest.raises(TypeError):
        es.stamp("a string is not an artifact")


def test_the_grandfathered_set_is_the_one_the_audit_recorded():
    waived = es.grandfathered()
    assert waived, "the grandfathered set is empty, so the exemption could not fire"
    for rel in sorted(waived):
        path = es.ROOT / rel
        assert path.exists(), rel + " is grandfathered but does not exist"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("engine_version"), rel + " is grandfathered without a version to grandfather"


def test_every_artifact_writer_stamps_and_every_result_names_its_build():
    """The live check: no unstamped writer, no half-stamped artifact, no invented commit."""
    assert es.unstamped_writers() == [], (
        "these modules write a JSON artifact without engine_stamp: %r" % es.unstamped_writers())
    assert es.half_stamped() == [], (
        "these artifacts name a version and no commit: %r" % es.half_stamped())
    assert es.bad_commits() == [], (
        "these artifacts carry an engine_commit that is not a sha: %r" % es.bad_commits())


def test_the_writer_check_can_fail(tmp_path, monkeypatch):
    """Proof the check fires: a writer that does not stamp is reported."""
    bad = tmp_path / "bad_harness.py"
    bad.write_text('import json\njson.dump({"cells": 1}, open("x.json", "w"))\n', encoding="utf-8")
    good = tmp_path / "good_harness.py"
    good.write_text("from benchmarks import engine_stamp\nengine_stamp.stamp({})\n", encoding="utf-8")
    monkeypatch.setattr(es, "BENCH", tmp_path)
    assert es.unstamped_writers() == ["bad_harness.py"]


def test_the_half_stamp_check_can_fail(tmp_path, monkeypatch):
    """Proof the check fires: a newly written artifact with a version and no commit is reported."""
    (tmp_path / "fresh.json").write_text(
        json.dumps({"engine_version": es.engine_version(), "cells": [1, 2]}), encoding="utf-8")
    monkeypatch.setattr(es, "DOCS", tmp_path)
    monkeypatch.setattr(es, "AUDIT", tmp_path / "no_such_audit.json")
    assert es.half_stamped() == [str(tmp_path / "fresh.json")]


def test_a_stamped_artifact_passes_the_half_stamp_check(tmp_path, monkeypatch):
    (tmp_path / "fresh.json").write_text(
        json.dumps(es.stamp({"cells": [1, 2]})), encoding="utf-8")
    monkeypatch.setattr(es, "DOCS", tmp_path)
    monkeypatch.setattr(es, "AUDIT", tmp_path / "no_such_audit.json")
    assert es.half_stamped() == []
    assert es.bad_commits() == []


def test_the_check_writes_nothing():
    before = sorted(p.name for p in es.DOCS.glob("*.json"))
    es.main(["--check"])
    assert sorted(p.name for p in es.DOCS.glob("*.json")) == before
