"""Assemble the Zenodo deposit bundles and check the file list against the
manuscripts.

The deposit is **not** made here and nothing is uploaded.  This builds the
three bundles, writes their manifests and checksums, and answers the one
question the deposit checklist leaves open: *does the software record carry
every artifact the manuscripts cite?*

Three records:

  software     the source tree at the ``v0.10.0`` tag, plus the manifests
  paper-01     Paper 01 as PDF and Markdown, plus its figures as vector PDF
  paper-02     Paper 02 as PDF and Markdown, plus its figures as vector PDF

The file list is written to ``docs/ZENODO-DEPOSIT.md``'s sibling
``.scratch/deposit/MANIFEST.json`` rather than into the metadata JSON, because
Zenodo's published record schema sets ``additionalProperties: false`` and has
no ``files`` field: the files are uploaded through the form, and the list
travels with the record as a document.

    python benchmarks/deposit_bundle.py            # build all three
    python benchmarks/deposit_bundle.py --check    # check only, build nothing

Everything lands under ``.scratch/deposit/``, which is disposable and
gitignored.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / ".scratch" / "deposit"

#: The tag the software record carries.
SOFTWARE_TAG = "v0.10.0"

#: The three records, and the metadata file each one's manifest describes.
RECORDS = {
    "software": "zenodo/software-v0.10.0.json",
    "paper-01": "zenodo/paper-01-preprint.json",
    "paper-02": "zenodo/paper-02-preprint.json",
}

#: Manuscript source -> the bundle it belongs to.
PAPERS = {
    "paper-01": "papers/01_developmental_structure_formation.md",
    "paper-02": "papers/02_persistent_structural_provenance.md",
}

#: A reference to an artifact in ``docs/``, in either of the forms the
#: manuscripts use (``docs/x.json`` and ``../docs/x.json``).
CITE_RE = re.compile(r"(?:\.\./)?docs/([A-Za-z0-9_.-]+\.(?:md|json|svg))")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(args: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=str(cwd or REPO), capture_output=True,
                          text=True)
    if proc.returncode != 0:
        raise RuntimeError("%s failed:\n%s" % (" ".join(args), proc.stderr))
    return proc.stdout


def cited_artifacts(markdown: str) -> list[str]:
    """The ``docs/`` artifacts a manuscript names, in order, deduplicated."""
    out: list[str] = []
    for name in CITE_RE.findall(markdown):
        if name not in out:
            out.append(name)
    return out


def files_at_tag(tag: str) -> set[str]:
    """Every path in the tree at ``tag``."""
    out = run(["git", "ls-tree", "-r", "--name-only", tag])
    return {line.strip() for line in out.splitlines() if line.strip()}


def build_software(tag: str) -> list[Path]:
    """The source tree at the tag, as one archive."""
    bundle = OUT / "software"
    bundle.mkdir(parents=True, exist_ok=True)
    archive = bundle / ("project-organica-%s.tar.gz" % tag)
    if archive.exists():
        archive.unlink()
    # `git archive` writes the archive itself; -o names the output file.
    run(["git", "archive", "--format=tar.gz", "-o", str(archive), tag])
    return [archive]


def build_paper(key: str) -> list[Path]:
    """A manuscript as PDF and Markdown, with its figures as vector PDF."""
    source = REPO / PAPERS[key]
    bundle = OUT / key
    bundle.mkdir(parents=True, exist_ok=True)

    stem = source.stem
    written: list[Path] = []

    pdf = REPO / "papers" / "build" / (stem + ".pdf")
    if not pdf.exists():
        raise RuntimeError(
            "%s is missing. Build it first: python benchmarks/render_papers.py"
            % pdf)
    shutil.copy2(pdf, bundle / pdf.name)
    written.append(bundle / pdf.name)

    shutil.copy2(source, bundle / source.name)
    written.append(bundle / source.name)

    markdown = source.read_text(encoding="utf-8")
    figures = [name for name in cited_artifacts(markdown)
               if name.endswith(".svg")]
    if figures:
        svgs = [str(REPO / "docs" / name) for name in figures]
        run([sys.executable, "-X", "utf8", str(REPO / "benchmarks" /
                                                "svg_to_pdf.py"),
             "--outdir", str(bundle)] + svgs)
        for name in figures:
            produced = bundle / (Path(name).stem + ".pdf")
            if not produced.exists():
                raise RuntimeError("the figure %s was not converted" % name)
            written.append(produced)
    return written


def write_manifests(tag: str, bundles: dict[str, list[Path]]) -> dict:
    """Per-record manifests and checksums, and the top-level manifest."""
    tree = files_at_tag(tag)
    manifest: dict = {
        "kind": "zenodo_deposit_manifest",
        "software_tag": tag,
        "records": {},
    }

    for key, files in bundles.items():
        record_dir = OUT / key
        entries = []
        for path in sorted(files, key=lambda p: p.name):
            entries.append({
                "key": path.name,
                "size": path.stat().st_size,
                "checksum": "sha256:%s" % sha256(path),
            })
        sums = "".join("%s  %s\n" % (e["checksum"].split(":")[1], e["key"])
                       for e in entries)
        (record_dir / "SHA256SUMS").write_text(sums, encoding="utf-8",
                                               newline="\n")

        metadata_path = REPO / RECORDS[key]
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        record = {
            "metadata_file": RECORDS[key],
            "title": metadata.get("title"),
            "license": metadata.get("license"),
            "upload_type": metadata.get("upload_type"),
            "publication_type": metadata.get("publication_type"),
            "files": entries + [{
                "key": "SHA256SUMS",
                "size": (record_dir / "SHA256SUMS").stat().st_size,
                "checksum": "sha256:%s" % sha256(record_dir / "SHA256SUMS"),
            }],
        }
        (record_dir / "DEPOSIT-MANIFEST.json").write_text(
            json.dumps(record, indent=1, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n")
        manifest["records"][key] = record

    # The check the deposit checklist asks for: every artifact a manuscript
    # cites must be inside the software record's tree.
    checks = []
    for key, rel in PAPERS.items():
        markdown = (REPO / rel).read_text(encoding="utf-8")
        for name in cited_artifacts(markdown):
            in_tree = ("docs/" + name) in tree
            checks.append({
                "paper": key,
                "artifact": "docs/" + name,
                "in_software_record": in_tree,
            })
    manifest["cited_artifact_check"] = checks
    missing = [c for c in checks if not c["in_software_record"]]
    manifest["cited_artifact_missing"] = missing

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=1, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    return manifest


def check_only() -> dict:
    tree = files_at_tag(SOFTWARE_TAG)
    checks = []
    for key, rel in PAPERS.items():
        markdown = (REPO / rel).read_text(encoding="utf-8")
        for name in cited_artifacts(markdown):
            checks.append({"paper": key, "artifact": "docs/" + name,
                           "in_software_record": ("docs/" + name) in tree})
    return {"cited_artifact_check": checks,
            "cited_artifact_missing": [c for c in checks
                                       if not c["in_software_record"]]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="only check the cited artifacts; build nothing")
    args = parser.parse_args(argv)

    if args.check:
        report = check_only()
        missing = report["cited_artifact_missing"]
        print("cited artifacts: %d, missing from the %s tree: %d"
              % (len(report["cited_artifact_check"]), SOFTWARE_TAG, len(missing)))
        for item in missing:
            print("  MISSING  %s (cited by %s)"
                  % (item["artifact"], item["paper"]))
        return 1 if missing else 0

    if OUT.exists():
        shutil.rmtree(OUT)
    bundles = {
        "software": build_software(SOFTWARE_TAG),
        "paper-01": build_paper("paper-01"),
        "paper-02": build_paper("paper-02"),
    }
    manifest = write_manifests(SOFTWARE_TAG, bundles)
    for key, record in manifest["records"].items():
        print("%-10s %d file(s)" % (key, len(record["files"])))
        for entry in record["files"]:
            print("    %-52s %9d" % (entry["key"], entry["size"]))
    missing = manifest["cited_artifact_missing"]
    print("cited artifacts missing from the %s tree: %d"
          % (SOFTWARE_TAG, len(missing)))
    for item in missing:
        print("    MISSING  %s (cited by %s)" % (item["artifact"], item["paper"]))
    print("manifest: %s" % (OUT / "MANIFEST.json"))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
