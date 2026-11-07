"""The engine pin must describe the engine that exists."""

import copy

from benchmarks import engine_pin as ep


def test_the_pin_matches_the_engine():
    assert ep.compare(ep.load_pin()) == []


def test_the_pin_is_reproducible_from_the_tree():
    pin = ep.load_pin()
    fresh = ep.compute()
    assert fresh["version"] == pin["version"]
    assert fresh["files"] == pin["files"], "the pin does not match a fresh hash of organica/"


def test_every_engine_module_is_pinned():
    pin = ep.load_pin()
    assert set(pin["files"]) == set(ep.engine_files())
    assert pin["files"], "the pin is empty, so it could not fail"


def test_a_changed_file_without_a_version_bump_is_reported():
    pin = copy.deepcopy(ep.load_pin())
    name = sorted(pin["files"])[0]
    now = dict(pin["files"])
    now[name] = "0" * 64
    found = ep.compare(pin, now=now, version=pin["version"])
    assert any("without a version bump" in message and name in message for message in found), found


def test_a_changed_file_with_a_version_bump_is_reported():
    pin = copy.deepcopy(ep.load_pin())
    name = sorted(pin["files"])[0]
    now = dict(pin["files"])
    now[name] = "0" * 64
    found = ep.compare(pin, now=now, version="99.0.0")
    assert any("99.0.0" in message and "re-run" in message for message in found), found
    assert not any("without a version bump" in message for message in found), found


def test_an_added_file_is_reported():
    pin = copy.deepcopy(ep.load_pin())
    now = dict(pin["files"])
    now["organica/new_module.py"] = "0" * 64
    found = ep.compare(pin, now=now, version=pin["version"])
    assert any("added" in message and "new_module" in message for message in found), found


def test_a_removed_file_is_reported():
    pin = copy.deepcopy(ep.load_pin())
    now = dict(pin["files"])
    now.pop(sorted(now)[0])
    found = ep.compare(pin, now=now, version=pin["version"])
    assert any("removed" in message for message in found), found


def test_a_version_bump_alone_is_reported():
    pin = copy.deepcopy(ep.load_pin())
    found = ep.compare(pin, now=dict(pin["files"]), version="99.0.0")
    assert any("re-pin or revert" in message for message in found), found


def test_check_writes_nothing():
    before = ep.PIN.read_bytes()
    assert ep.main(["--check"]) == 0
    assert ep.PIN.read_bytes() == before
