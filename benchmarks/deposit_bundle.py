"""Assemble the Zenodo deposit bundles and check the file list against the
manuscripts.

The deposit is **not** made here and nothing is uploaded.  This builds the
three bundles, writes their manifests and checksums, and answers the one
question the deposit checklist leaves open: *does the software record carry
every artifact the manuscripts cite?*

Four bundles:

  software       the source tree at the archived commit
  paper-01       Paper 01 as PDF and Markdown, plus its figures as vector PDF
  paper-02       Paper 02 as PDF and Markdown, plus its figures as vector PDF
  reproduction   both rendered papers, the archived commit, the build
                 environment, and the commands that rebuild them

The reproduction bundle is the reviewer's entry point rather than a fourth
Zenodo record: it answers "which state was this built from, on what, and how
do I rebuild it?" without asking anyone to trust a version string.

The software record is archived from the **``v0.12.0`` tag**.  It used to be
built from the ``v0.10.0`` tag, and that stopped being correct when Paper 01
gained §4.10: the capacity-1,000 result cites
``docs/functional_structure_confirmatory.json`` and
``docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md``, both committed after that
tag, so a v0.10.0 tree cannot carry the evidence its own manuscript cites.
The ``v0.12.0`` tag is cut at the release-identity commit, so ``SOFTWARE_REF``
defaults to it and the manifest records the resolved commit SHA as well.
Nothing here publishes anything.

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
import datetime
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from benchmarks import engine_stamp

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / ".scratch" / "deposit"

#: The version the software record carries, and the ref it is archived from.
#: ``v0.12.0`` is the deposit version and the latest cut tag, so the archive
#: is taken from it and the resolved commit SHA is recorded in the manifest.
SOFTWARE_VERSION = "0.12.0"
SOFTWARE_REF = os.environ.get("ORGANICA_SOFTWARE_REF", "v0.12.0")

#: The three records, and the metadata file each one's manifest describes.
RECORDS = {
    "software": "zenodo/software-v%s.json" % SOFTWARE_VERSION,
    "paper-01": "zenodo/paper-01-preprint.json",
    "paper-02": "zenodo/paper-02-preprint.json",
}

#: Manuscript source -> the bundle it belongs to.
PAPERS = {
    "paper-01": "papers/01_developmental_structure_formation.md",
    "paper-02": "papers/02_persistent_structural_provenance.md",
}

#: The reproduction bundle is assembled here but is not a Zenodo record: it has
#: no metadata file, because it is not a deposit.  It is the material a reader
#: needs in order to check one.
REPRODUCTION = "reproduction"

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


def resolved_commit(ref: str) -> str:
    """The commit a ref names, peeled from any annotated tag object.

    ``git rev-parse v0.12.0`` returns the tag object's SHA, not the commit
    it points at, and a tag object is not a commit: a manifest that records
    one names something that cannot be checked out by that id.
    """
    return run(["git", "rev-parse", "--verify", ref + "^{commit}"]).strip()


def files_at_ref(ref: str) -> set[str]:
    """Every path in the tree at ``ref``."""
    out = run(["git", "ls-tree", "-r", "--name-only", ref])
    return {line.strip() for line in out.splitlines() if line.strip()}


def build_software(ref: str) -> list[Path]:
    """The source tree at the ref, as one archive."""
    bundle = OUT / "software"
    bundle.mkdir(parents=True, exist_ok=True)
    archive = bundle / ("project-organica-v%s.tar.gz" % SOFTWARE_VERSION)
    if archive.exists():
        archive.unlink()
    # `git archive` writes the archive itself; -o names the output file.
    run(["git", "archive", "--format=tar.gz", "-o", str(archive), ref])
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


def _tool_version(command: str) -> str | None:
    """The first line of ``<command> --version``, or None if it is absent.

    A missing tool is recorded as missing, not guessed at: this bundle says what
    the build ran on, and "unknown" is the honest value when it was not there.
    """
    path = shutil.which(command)
    if not path:
        return None
    try:
        proc = subprocess.run([path, "--version"], capture_output=True,
                              text=True, errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return lines[0] if lines else None


def _page_count(stem: str) -> int | None:
    """Pages of the PDF, read back from the LaTeX log that produced it.

    The project has no PDF library and this is not a reason to add one; the
    build log records the page count, and the checksum below is what a reader
    actually verifies.
    """
    log = REPO / ".scratch" / "paper-build" / (stem + ".log")
    if not log.exists():
        return None
    text = log.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Output written on \S+?\.pdf \((\d+) pages?", text)
    return int(match.group(1)) if match else None


def reproduce_markdown(environment: dict) -> str:
    """The REPRODUCE.md text, with every value substituted from the build."""
    commit = environment["software_commit"]
    version = environment["software_version"]
    lines = [
        "# Reproducing Papers 01 and 02",
        "",
        "Written by `python benchmarks/deposit_bundle.py` on %s.  Every value"
        % environment["generated"],
        "below is substituted from the build; none of it is typed by hand.",
        "",
        "This bundle is the reviewer's way in.  It names the exact state the two",
        "manuscripts were built from, the environment they were built in, the",
        "commands that rebuild them, and the PDFs themselves, so a claim can be",
        "checked without running a campaign.",
        "",
        "## The archived state",
        "",
        "| field | value |",
        "|---|---|",
        "| version | %s |" % version,
        "| commit | `%s` |" % commit,
        "| archive | `project-organica-v%s.tar.gz` |" % version,
        "",
        "The archive is the software record.  A version string does not check out",
        "and a commit does, so this bundle names the commit:",
        "",
        "```",
        "git clone https://github.com/nueraresearch/project-organica.git",
        "cd project-organica",
        "git checkout %s" % commit,
        "```",
        "",
        "## Build environment",
        "",
        "These are the versions on the machine that built this bundle, not a",
        "requirement: any pdfLaTeX with the packages below should do.",
        "",
        "| tool | version |",
        "|---|---|",
        "| Python | %s |" % environment["python"],
        "| platform | %s |" % environment["platform"],
        "| pandoc | %s |" % (environment["pandoc"] or "not present"),
        "| pdfLaTeX | %s |" % (environment["pdflatex"] or "not present"),
        "",
        "The project itself is standard library only: Python and the two",
        "typesetting tools are the whole requirement.  `pytest` is needed for the",
        "test suite and nothing else.  The LaTeX packages the template loads are",
        "`booktabs`, `longtable`, `array`, `calc`, `fancyvrb`, `pdflscape`,",
        "`caption`, `lm`, `microtype` and \u2014 for the Unicode map — `glyphtounicode`.",
        "",
        "## Commands, in order",
        "",
        "```bash",
        "python benchmarks/figure_papers.py       # papers' figures, from the",
        "                                         # committed artifacts",
        "python benchmarks/svg_to_pdf.py --all    # SVG -> vector PDF",
        "python benchmarks/render_papers.py       # both manuscripts to PDF",
        "python benchmarks/deposit_bundle.py      # these bundles and checksums",
        "python -m pytest tests -q                # the checks",
        "```",
        "",
        "Figures are drawn from committed artifacts, not from a new run: the",
        "engine is frozen and re-running a campaign would produce different",
        "seeds, not the same paper.  `tests/test_paper_numbers.py` and",
        "`tests/test_readout_tables.py` re-derive every number the manuscripts",
        "quote from the artifacts, and fail on drift.",
        "",
        "## Expected results",
        "",
        "| paper | pages | bytes | sha256 |",
        "|---|---|---|---|",
    ]
    for paper in environment["papers"]:
        lines.append("| %s | %s | %s | `%s` |" % (
            paper["record"],
            paper["pages"] if paper["pages"] is not None else "see PDF",
            paper["bytes"],
            paper["sha256"]))
    lines.extend([
        "",
        "A rebuilt PDF that differs in bytes from the checksums above is not",
        "necessarily wrong: pdfLaTeX embeds a build timestamp, so byte equality",
        "holds only within the same day and the same tool chain.  The checks that",
        "travel with the source are the ones that matter: the page count, the zero",
        "errors and overfull boxes in the log, and the extracted text matching the",
        "manuscript.",
        "",
        "## What this bundle does not reproduce",
        "",
        "The experiments.  Every number in both manuscripts comes from a record",
        "that was committed when it was measured, and the engine that produced it",
        "is frozen at `v0.9.0`; re-running a campaign would test the engine again,",
        "not rebuild these papers.  The reproducibility offered here is that of",
        "the *reading and checking* path: the numbers trace to artifacts, the",
        "artifacts are in the software record, and the PDFs are built from the",
        "manuscripts by the commands above.",
        "",
        "Nor does it upload itself.  A Zenodo deposit mints a public DOI and is",
        "the owner's action; see `docs/ZENODO-DEPOSIT.md`.",
        "",
    ])
    return "\n".join(lines)


def build_reproduction() -> list[Path]:
    """Both rendered papers, with the commit, environment and commands."""
    bundle = OUT / REPRODUCTION
    bundle.mkdir(parents=True, exist_ok=True)

    papers = []
    for key, rel in PAPERS.items():
        stem = Path(rel).stem
        pdf = REPO / "papers" / "build" / (stem + ".pdf")
        if not pdf.exists():
            raise RuntimeError(
                "%s is missing. Build it first: python benchmarks/render_papers.py"
                % pdf)
        shutil.copy2(pdf, bundle / pdf.name)
        papers.append({
            "record": key,
            "manuscript": rel,
            "pdf": pdf.name,
            "pages": _page_count(stem),
            "bytes": (bundle / pdf.name).stat().st_size,
            "sha256": sha256(bundle / pdf.name),
        })

    environment = {
        "kind": "reproduction_environment",
        "generated": datetime.date.today().isoformat(),
        "software_version": SOFTWARE_VERSION,
        "software_commit": resolved_commit(SOFTWARE_REF),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "pandoc": _tool_version("pandoc"),
        "pdflatex": _tool_version("pdflatex"),
        "papers": papers,
    }
    (bundle / "ENVIRONMENT.json").write_text(
        json.dumps(engine_stamp.stamp(environment), indent=1) + "\n", encoding="utf-8",
        newline="\n")
    (bundle / "REPRODUCE.md").write_text(
        reproduce_markdown(environment), encoding="utf-8", newline="\n")

    written = [bundle / "REPRODUCE.md", bundle / "ENVIRONMENT.json"]
    written.extend(bundle / paper["pdf"] for paper in papers)
    return written


def write_manifests(ref: str, bundles: dict[str, list[Path]]) -> dict:
    """Per-record manifests and checksums, and the top-level manifest."""
    tree = files_at_ref(ref)
    manifest: dict = {
        "kind": "zenodo_deposit_manifest",
        "software_version": SOFTWARE_VERSION,
        "software_ref": ref,
        "software_commit": resolved_commit(ref),
        "software_tag_cut": False,
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

        if key == REPRODUCTION:
            # No metadata file: this bundle is not deposited as a record of its
            # own, it travels with the manuscripts as their checking material.
            record = {
                "metadata_file": None,
                "title": "Reproduction bundle: commit, environment, commands "
                         "and rendered manuscripts",
                "license": None,
                "upload_type": None,
                "publication_type": None,
                "files": entries + [{
                    "key": "SHA256SUMS",
                    "size": (record_dir / "SHA256SUMS").stat().st_size,
                    "checksum": "sha256:%s" % sha256(record_dir / "SHA256SUMS"),
                }],
            }
            manifest["records"][key] = record
            continue

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
            json.dumps(engine_stamp.stamp(record), indent=1, sort_keys=True) + "\n",
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
        json.dumps(engine_stamp.stamp(manifest), indent=1, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    return manifest


def check_only() -> dict:
    tree = files_at_ref(SOFTWARE_REF)
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
              % (len(report["cited_artifact_check"]), SOFTWARE_REF, len(missing)))
        for item in missing:
            print("  MISSING  %s (cited by %s)"
                  % (item["artifact"], item["paper"]))
        return 1 if missing else 0

    if OUT.exists():
        shutil.rmtree(OUT)
    bundles = {
        "software": build_software(SOFTWARE_REF),
        "paper-01": build_paper("paper-01"),
        "paper-02": build_paper("paper-02"),
        REPRODUCTION: build_reproduction(),
    }
    manifest = write_manifests(SOFTWARE_REF, bundles)
    print("software record: v%s from %s (%s)"
          % (SOFTWARE_VERSION, SOFTWARE_REF, manifest["software_commit"]))
    for key, record in manifest["records"].items():
        print("%-10s %d file(s)" % (key, len(record["files"])))
        for entry in record["files"]:
            print("    %-52s %9d" % (entry["key"], entry["size"]))
    missing = manifest["cited_artifact_missing"]
    print("cited artifacts missing from the v%s tree: %d"
          % (SOFTWARE_VERSION, len(missing)))
    for item in missing:
        print("    MISSING  %s (cited by %s)" % (item["artifact"], item["paper"]))
    print("manifest: %s" % (OUT / "MANIFEST.json"))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
