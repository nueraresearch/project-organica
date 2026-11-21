"""The layer census must cover every test module and keep the authorized count at zero.

Tagging is a claim about what a module does; these tests hold the claim to the source where the
source is unambiguous, report the split, and prove the census can fail.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import test_layers as tl  # noqa: E402


def test_every_test_module_declares_one_valid_layer():
    problems = tl.problems()
    assert problems == [], problems


def test_the_split_covers_the_suite_and_authorises_nothing():
    counts = tl.split()
    assert counts["modules"] == len(tl.modules())
    assert counts[tl.AUTHORIZED] == 0
    assert sum(counts[layer] for layer in tl.LAYERS) == counts["modules"]
    assert counts["synthetic"] >= 1, "some module must execute a synthetic cell"


def _module(tmp_path, source):
    path = tmp_path / "test_fake.py"
    path.write_text(source, encoding="utf-8")
    return path


def _problems(tmp_path, monkeypatch):
    monkeypatch.setattr(tl, "ROOT", tmp_path)
    monkeypatch.setattr(tl, "TESTS", tmp_path)
    return tl.problems()


def test_an_untagged_module_is_reported(tmp_path, monkeypatch):
    _module(tmp_path, "def test_x():\n    assert True\n")
    assert _problems(tmp_path, monkeypatch) == ["test_fake.py: no LAYER declared"]


def test_an_authorized_tag_is_reported(tmp_path, monkeypatch):
    _module(tmp_path, 'LAYER = "authorized"\n')
    assert _problems(tmp_path, monkeypatch) == [
        "test_fake.py: tagged authorized; no test module may run a granted cell"]


def test_a_static_tag_on_an_engine_module_is_reported(tmp_path, monkeypatch):
    _module(tmp_path, 'LAYER = "static"\n\nSleepService(memory)\n')
    assert _problems(tmp_path, monkeypatch) == [
        "test_fake.py: tagged static but executes the engine (SleepService)"]


def test_a_dry_run_tag_on_an_unrefused_cell_is_reported(tmp_path, monkeypatch):
    _module(tmp_path, 'LAYER = "dry-run"\nmain(["--measure"])\n')
    assert _problems(tmp_path, monkeypatch) == [
        "test_fake.py: tagged dry-run but names a cell-running entry point with no refusal marker"]


def test_a_refused_cell_is_not_reported(tmp_path, monkeypatch):
    _module(tmp_path, 'LAYER = "dry-run"\nmain(["--measure"])\n# REFUSED\n')
    assert _problems(tmp_path, monkeypatch) == []
