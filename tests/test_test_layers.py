"""The layer census must cover every test module and keep the authorized count at zero.

Tagging is a claim about what a module does; these tests hold the claim to the source, report the
split so the shape of the suite is visible, and prove the census can fail (untagged, unknown layer,
an ``authorized`` tag, and a ``static`` tag on a module that executes the engine).
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import test_layers as tl  # noqa: E402


def test_every_test_module_declares_one_valid_layer():
    assert tl.problems() == [], tl.problems()


def test_the_split_covers_the_suite_and_authorises_nothing():
    counts = tl.split()
    assert counts["modules"] == len(tl.modules())
    assert counts[tl.AUTHORIZED] == 0
    assert sum(counts[layer] for layer in tl.LAYERS) == counts["modules"]
    assert counts["synthetic"] >= 1, "some module must execute a synthetic cell"


def test_the_layers_are_the_four_named_ones():
    assert tl.LAYERS == ("static", "dry-run", "synthetic", "authorized")


def _module(tmp_path, source):
    path = tmp_path / "test_fake.py"
    path.write_text(source, encoding="utf-8")
    return path


def test_an_untagged_module_is_reported(tmp_path):
    path = _module(tmp_path, "def test_x():\n    assert True\n")
    assert tl.declared(path) == []


def test_an_authorized_tag_is_reported(tmp_path):
    path = _module(tmp_path, 'LAYER = "authorized"\n')
    assert tl.declared(path) == ["authorized"]


def test_a_static_tag_on_an_engine_module_is_a_mismatch(tmp_path):
    path = _module(tmp_path, 'LAYER = "static"\n\nSleepService(memory)\n')
    assert tl.evidence(path)["engine"] == ["SleepService"]
    assert tl.classify(path) == "synthetic"


def test_a_cell_entry_point_without_a_refusal_marker_is_authorized(tmp_path):
    path = _module(tmp_path, 'LAYER = "dry-run"\nmain(["--measure"])\n')
    assert tl.classify(path) == "authorized"
    with_refusal = _module(tmp_path, 'LAYER = "dry-run"\nmain(["--measure"])\n# REFUSED\n')
    assert tl.classify(with_refusal) == "dry-run"
