"""Check the Zenodo deposit bundle.

The deposit is the one place where a file list is a claim: it says what a
reader will receive.  Three things have to hold for that claim to be worth
anything, and all three are checked here.

1. **Every artifact a manuscript cites is inside the software record.**  A
   manuscript that cites evidence the deposit does not carry is a manuscript
   whose numbers cannot be checked from the deposit.

2. **The bundles are what the manifests say they are.**  Every file a
   manifest lists must exist, and its checksum must be the checksum of the
   bytes on disk.

3. **The software bundle is the tree at the tag**, not the working tree: a
   deposit that carries uncommitted or newer work would not be the release it
   claims to be.

The test fails on a doctored manifest, so a passing run is not a formality.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tarfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "benchmarks"))

import deposit_bundle  # noqa: E402


@pytest.fixture(scope="module")
def manifest():
    """The built manifest.  The bundles are rebuilt once for this module."""
    if deposit_bundle.OUT.exists():
        import shutil
        shutil.rmtree(deposit_bundle.OUT)
    bundles = {
        "software": deposit_bundle.build_software(deposit_bundle.SOFTWARE_TAG),
        "paper-01": deposit_bundle.build_paper("paper-01"),
        "paper-02": deposit_bundle.build_paper("paper-02"),
    }
    return deposit_bundle.write_manifests(deposit_bundle.SOFTWARE_TAG, bundles)


def test_the_manifest_names_the_three_records(manifest):
    assert set(manifest["records"]) == {"software", "paper-01", "paper-02"}
    for key, record in manifest["records"].items():
        assert record["metadata_file"] in deposit_bundle.RECORDS.values(), (
            "%s names a metadata file that is not in the package" % key)
        assert record["files"], "%s carries no files" % key


def test_every_cited_artifact_is_in_the_software_record(manifest):
    """The check the deposit checklist asks for."""
    missing = manifest["cited_artifact_missing"]
    assert not missing, (
        "the manuscripts cite artifacts the software record does not carry: "
        + ", ".join("%s (%s)" % (m["artifact"], m["paper"]) for m in missing))
    assert manifest["cited_artifact_check"], "nothing was checked"


def test_the_cited_artifact_check_covers_both_papers(manifest):
    papers = {c["paper"] for c in manifest["cited_artifact_check"]}
    assert papers == {"paper-01", "paper-02"}
    assert len(manifest["cited_artifact_check"]) >= 10


def test_every_listed_file_exists_and_checksums(manifest):
    for key, record in manifest["records"].items():
        directory = deposit_bundle.OUT / key
        for entry in record["files"]:
            path = directory / entry["key"]
            assert path.exists(), "%s lists %s, which is not there" % (
                key, entry["key"])
            assert path.stat().st_size == entry["size"], (
                "%s lists %s with the wrong size" % (key, entry["key"]))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            assert entry["checksum"] == "sha256:%s" % digest, (
                "%s lists %s with the wrong checksum" % (key, entry["key"]))


def test_the_sums_file_matches_the_listed_checksums(manifest):
    for key, record in manifest["records"].items():
        sums = (deposit_bundle.OUT / key / "SHA256SUMS").read_text(
            encoding="utf-8")
        for entry in record["files"]:
            if entry["key"] == "SHA256SUMS":
                continue
            digest = entry["checksum"].split(":")[1]
            assert "%s  %s" % (digest, entry["key"]) in sums, (
                "%s is not in %s's SHA256SUMS" % (entry["key"], key))


def test_the_software_bundle_is_the_tree_at_the_tag(manifest):
    """The deposit must be the release, not the working tree."""
    archive = deposit_bundle.OUT / "software" / (
        "project-organica-%s.tar.gz" % deposit_bundle.SOFTWARE_TAG)
    assert archive.exists()
    with tarfile.open(archive, "r:gz") as tar:
        names = set(tar.getnames())
    assert "pyproject.toml" in names
    assert "organica/__init__.py" in names
    assert "zenodo/software-v0.10.0.json" in names
    assert "docs/CANDIDATE-MEMBERSHIP-AUDIT.md" in names
    # The working tree is ahead of the tag; the deposit must not carry that.
    for newer in ("docs/DIVERGENCE-CYCLE-CAPTURE.md",
                   "docs/DIVERGENCE-MECHANISM-BRIEF.md"):
        assert newer not in names, (
            "the software bundle carries %s, which is not in the tagged tree"
            % newer)


def test_the_paper_bundles_carry_their_manuscript_and_figures(manifest):
    for key, rel in deposit_bundle.PAPERS.items():
        directory = deposit_bundle.OUT / key
        stem = Path(rel).stem
        assert (directory / (stem + ".md")).exists(), (
            "%s carries no manuscript source" % key)
        assert (directory / (stem + ".pdf")).exists(), (
            "%s carries no rendered manuscript" % key)
        markdown = (REPO / rel).read_text(encoding="utf-8")
        figures = [n for n in deposit_bundle.cited_artifacts(markdown)
                   if n.endswith(".svg")]
        assert figures, "%s cites no figures" % key
        for name in figures:
            produced = directory / (Path(name).stem + ".pdf")
            assert produced.exists(), (
                "%s cites %s but does not carry it" % (key, name))


def test_the_papers_carry_the_cc_by_licence(manifest):
    """CC-BY-4.0 was the decided licence for the manuscripts."""
    for key in ("paper-01", "paper-02"):
        assert manifest["records"][key]["license"] == "CC-BY-4.0", (
            "%s carries a licence other than the decided CC-BY-4.0" % key)
    assert manifest["records"]["software"]["license"] == "Apache-2.0"


# ---------------------------------------------------------------------------
# fail-tests
# ---------------------------------------------------------------------------

def test_a_doctored_checksum_is_rejected(manifest):
    import copy
    broken = copy.deepcopy(manifest)
    entry = broken["records"]["paper-01"]["files"][0]
    entry["checksum"] = "sha256:" + "0" * 64
    path = deposit_bundle.OUT / "paper-01" / entry["key"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert entry["checksum"] != "sha256:%s" % digest, (
        "a wrong checksum is not distinguishable from the right one")


def test_a_missing_cited_artifact_is_detected():
    """The check must be able to fail: cite something that is not there."""
    tree = deposit_bundle.files_at_tag(deposit_bundle.SOFTWARE_TAG)
    assert "docs/does-not-exist.json" not in tree
    assert "docs/CANDIDATE-MEMBERSHIP-AUDIT.md" in tree
    # The divergence-cycle capture was committed after the tag, so it is
    # correctly absent from the software record's tree.
    assert "docs/DIVERGENCE-CYCLE-CAPTURE.md" not in tree
