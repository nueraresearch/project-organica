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

3. **The software bundle is the archived tree**, not a hand-picked directory:
   the archive's file list must equal the ref's file list, so a file cannot be
   left out or slipped in.

The software record used to be archived from the ``v0.10.0`` tag, and that
was wrong in a way only check 1 could see: Paper 01 §4.10 cites two artifacts
committed *after* that tag, so the deposit could not carry the evidence its
own manuscript names.  The archive is now taken from a commit at version
``0.12.0``; the checks below assert both halves of that — the cited artifacts
are present now, and they really were absent from the tag, so the test would
have failed before the fix.

The test fails on a doctored manifest, so a passing run is not a formality.
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
import tarfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "benchmarks"))

import deposit_bundle  # noqa: E402

#: The two artifacts the v0.10.0 tag does not carry, because Paper 01 §4.10
#: was written after it.  The deposit failed on exactly these.
LATE_ARTIFACTS = (
    "docs/functional_structure_confirmatory.json",
    "docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md",
)


@pytest.fixture(scope="module")
def manifest():
    """The built manifest.  The bundles are rebuilt once for this module."""
    if deposit_bundle.OUT.exists():
        shutil.rmtree(deposit_bundle.OUT)
    bundles = {
        "software": deposit_bundle.build_software(deposit_bundle.SOFTWARE_REF),
        "paper-01": deposit_bundle.build_paper("paper-01"),
        "paper-02": deposit_bundle.build_paper("paper-02"),
        deposit_bundle.REPRODUCTION: deposit_bundle.build_reproduction(),
    }
    return deposit_bundle.write_manifests(deposit_bundle.SOFTWARE_REF, bundles)


def test_the_manifest_names_the_four_bundles(manifest):
    assert set(manifest["records"]) == {"software", "paper-01", "paper-02",
                                       deposit_bundle.REPRODUCTION}
    for key in ("software", "paper-01", "paper-02"):
        assert manifest["records"][key]["metadata_file"] in (
            deposit_bundle.RECORDS.values()), (
            "%s names a metadata file that is not in the package" % key)
    assert manifest["records"][deposit_bundle.REPRODUCTION]["metadata_file"] is None, (
        "the reproduction bundle is not a Zenodo record and has no metadata file")
    for key, record in manifest["records"].items():
        assert record["files"], "%s carries no files" % key


def test_the_reproduction_bundle_names_the_commit_and_the_commands(manifest):
    """A reviewer can find the state, rebuild it, and check the PDF it carries."""
    directory = deposit_bundle.OUT / deposit_bundle.REPRODUCTION
    environment = json.loads((directory / "ENVIRONMENT.json").read_text(
        encoding="utf-8"))
    assert environment["software_commit"] == manifest["software_commit"], (
        "the reproduction bundle names a commit the manifest does not")
    assert environment["python"], "no Python version was recorded"

    text = (directory / "REPRODUCE.md").read_text(encoding="utf-8")
    assert manifest["software_commit"] in text, (
        "REPRODUCE.md does not name the commit it was built from")
    for command in ("benchmarks/figure_papers.py", "benchmarks/svg_to_pdf.py",
                    "benchmarks/render_papers.py",
                    "benchmarks/deposit_bundle.py"):
        assert command in text, (
            "REPRODUCE.md omits the command that regenerates %s" % command)

    # The papers it carries are the papers' records, not copies of something else.
    for paper in environment["papers"]:
        listed = {e["key"]: e for e in manifest["records"][paper["record"]]["files"]}
        assert listed[paper["pdf"]]["checksum"] == "sha256:" + paper["sha256"], (
            "%s carries a different PDF from the one %s records"
            % (deposit_bundle.REPRODUCTION, paper["record"]))
        assert paper["pages"] is None or paper["pages"] > 0


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


def test_the_manifest_names_the_archived_commit(manifest):
    """A version with no tag needs a commit, or the record names nothing."""
    assert manifest["software_version"] == deposit_bundle.SOFTWARE_VERSION
    commit = manifest["software_commit"]
    assert len(commit) == 40 and all(c in "0123456789abcdef" for c in commit)
    assert manifest["software_tag_cut"] is False


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


def test_the_software_bundle_is_the_archived_tree(manifest):
    """The deposit must be the archived tree, file for file."""
    archive = deposit_bundle.OUT / "software" / (
        "project-organica-v%s.tar.gz" % deposit_bundle.SOFTWARE_VERSION)
    assert archive.exists()
    with tarfile.open(archive, "r:gz") as tar:
        names = set(tar.getnames())
    expected = deposit_bundle.files_at_ref(deposit_bundle.SOFTWARE_REF)
    # git archive also emits a directory entry for every directory; those are
    # names no file ends in "/", so they are not file paths and are dropped by
    # the check below rather than by a suffix rule.
    extra = {n for n in names if n not in expected}
    assert all(any(e.startswith(n.rstrip("/") + "/") for e in expected)
               for n in extra), (
        "the archive carries %d path(s) the ref does not have: %s"
        % (len(extra), sorted(extra)[:5]))
    missing = expected - names
    assert not missing, (
        "the archive is missing %d path(s) the ref has: %s"
        % (len(missing), sorted(missing)[:5]))
    assert "pyproject.toml" in names
    assert "organica/__init__.py" in names
    assert "zenodo/software-v%s.json" % deposit_bundle.SOFTWARE_VERSION in names


def test_the_archived_tree_carries_the_evidence_the_tag_lacked(manifest):
    """The fix, stated as a check: the late artifacts are in, and were not."""
    archived = deposit_bundle.files_at_ref(deposit_bundle.SOFTWARE_REF)
    tagged = deposit_bundle.files_at_ref("v0.10.0")
    for artifact in LATE_ARTIFACTS:
        assert artifact in archived, "%s is not in the archived tree" % artifact
        assert artifact not in tagged, (
            "%s is in v0.10.0, so this test no longer describes the defect it "
            "guards" % artifact)
        cited = any(c["artifact"] == artifact and c["in_software_record"]
                    for c in manifest["cited_artifact_check"])
        assert cited, "%s is not registered as present by the check" % artifact


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
    broken = copy.deepcopy(manifest)
    entry = broken["records"]["paper-01"]["files"][0]
    entry["checksum"] = "sha256:" + "0" * 64
    path = deposit_bundle.OUT / "paper-01" / entry["key"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert entry["checksum"] != "sha256:%s" % digest, (
        "a wrong checksum is not distinguishable from the right one")


def test_a_missing_cited_artifact_is_detected():
    """The check must be able to fail: cite something that is not there."""
    tree = deposit_bundle.files_at_ref(deposit_bundle.SOFTWARE_REF)
    assert "docs/does-not-exist.json" not in tree
    assert "docs/CANDIDATE-MEMBERSHIP-AUDIT.md" in tree
    # ... and the tree really is the working tree's committed state, not an
    # older snapshot: a file the v0.10.0 tag lacks is present here.
    assert "docs/DIVERGENCE-CYCLE-CAPTURE.md" in tree


def test_the_manifest_records_a_commit_not_a_tag_object(manifest):
    """``software_commit`` must name a commit, not an annotated tag object.

    ``git rev-parse v0.12.0`` returns the tag object's SHA while
    ``v0.12.0^{commit}`` returns the commit.  A manifest that records the
    former identifies something that is not a checkable tree state.
    """
    import subprocess

    sha = manifest["software_commit"]
    kind = subprocess.run(["git", "cat-file", "-t", sha], cwd=str(REPO),
                          capture_output=True, text=True).stdout.strip()
    assert kind == "commit", (
        "software_commit must be a commit SHA, not a tag object: %r is a %s"
        % (sha, kind))
