"""Render the manuscripts to PDF.

The build is pandoc to LaTeX, then MiKTeX's pdfLaTeX.  Neither is on PATH by
default on this machine, so both are looked up in their install locations.

The figures are the repository's SVGs, converted to vector PDF by
``benchmarks/svg_to_pdf.py``; LaTeX cannot include an SVG, so the build points
the manuscript's figure references at the PDFs.  The manuscript source is not
modified: the rewrite happens on a build copy, so the committed Markdown keeps
pointing at the committed SVG.

    python benchmarks/render_papers.py            # both papers
    python benchmarks/render_papers.py --paper 01 # one of them

Output lands in ``papers/build/``.  The build directory is disposable; the
PDFs in it are deposit artifacts.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = Path(__file__).resolve().parent / "paper-template.tex"
BUILD = REPO / ".scratch" / "paper-build"
OUT = REPO / "papers" / "build"

#: Where pandoc and pdfLaTeX live on this machine, if they are not on PATH.
PANDOC_CANDIDATES = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "Pandoc" / "pandoc.exe",
    Path("pandoc"),
]
LATEX_CANDIDATES = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "MiKTeX" /
    "miktex" / "bin" / "x64" / "pdflatex.exe",
    Path("pdflatex"),
]

PAPERS = [
    "papers/01_developmental_structure_formation.md",
    "papers/02_persistent_structural_provenance.md",
]

IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>\.\./docs/[^)]+?)\.svg\)")
TITLE_RE = re.compile(r"^#\s+(?P<title>.+?)\s*$", re.M)
AUTHOR_RE = re.compile(r"^\*\*Author:\*\*\s*(?P<author>.+?)\s*$", re.M)


def find_tool(candidates: list[Path], name: str) -> str | None:
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
        found = shutil.which(str(candidate))
        if found:
            return found
    return None


def prepare(markdown: str) -> tuple[str, str, str]:
    """Return (build copy, title, author) with the figure references rewritten."""
    title_match = TITLE_RE.search(markdown)
    author_match = AUTHOR_RE.search(markdown)
    title = title_match.group("title") if title_match else ""
    author = author_match.group("author") if author_match else ""
    if not title:
        raise SystemExit("the manuscript has no level-one title")
    if not author:
        raise SystemExit("the manuscript has no **Author:** line")

    def replace(match: re.Match) -> str:
        name = Path(match.group("path")).name
        pdf = (REPO / "docs" / (name + ".pdf")).as_posix()
        return "![%s](%s){width=6.4in}" % (match.group("alt"), pdf)

    body = IMAGE_RE.sub(replace, markdown)
    # The author is in the title block, so the body line would repeat it.
    body = body.replace(author_match.group(0), "", 1)
    return body, title, author


def run(command: list[str], cwd: Path, what: str) -> None:
    result = subprocess.run(command, cwd=str(cwd), capture_output=True,
                            text=True, timeout=900)
    if result.returncode != 0:
        print(result.stdout[-4000:])
        print(result.stderr[-4000:])
        raise SystemExit("%s failed with exit code %d" % (what, result.returncode))


def fix_table_captype(tex_path: Path) -> int:
    """Rewrite pandoc's ``\\def\\LTcaptype{none}`` as an empty value.

    longtable reads ``\\LTcaptype`` as the name of a counter and steps it
    unless the value is empty, so pandoc's "none" is read as a counter that
    does not exist.  Pandoc means "do not increment a counter", which is
    longtable's empty case, so the generated file is corrected to say that.
    The committed manuscript is not touched; only the build copy.
    """
    raw = tex_path.read_bytes()
    out = raw.replace(b"\\def\\LTcaptype{none}", b"\\def\\LTcaptype{}")
    out = out.replace(b"\\renewcommand{\\LTcaptype}{none}",
                      b"\\renewcommand{\\LTcaptype}{}")
    if out != raw:
        tex_path.write_bytes(out)
    return raw.count(b"\\def\\LTcaptype{none}")


def render(rel: str, pandoc: str, pdflatex: str) -> Path:
    source = REPO / rel
    markdown = source.read_text(encoding="utf-8")
    body, title, author = prepare(markdown)

    BUILD.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    build_md = BUILD / (stem + ".md")
    build_tex = BUILD / (stem + ".tex")
    build_md.write_text(body, encoding="utf-8")

    run([pandoc, str(build_md), "--from", "markdown+pipe_tables",
         "--to", "latex", "--standalone", "--template", str(TEMPLATE),
         "--metadata", "title:%s" % title, "--metadata", "author:%s" % author,
         "--output", str(build_tex)], BUILD, "pandoc")

    fix_table_captype(build_tex)

    for _ in range(2):
        run([pdflatex, "-interaction=nonstopmode", "-halt-on-error",
             str(build_tex)], BUILD, "pdflatex")

    produced = BUILD / (stem + ".pdf")
    if not produced.exists():
        raise SystemExit("no PDF was produced for %s" % rel)
    target = OUT / (stem + ".pdf")
    shutil.copy2(produced, target)
    print("wrote %s (%d bytes)" % (target, target.stat().st_size))
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", default=None,
                        help="'01' or '02' for one paper")
    args = parser.parse_args(argv)

    pandoc = find_tool(PANDOC_CANDIDATES, "pandoc")
    pdflatex = find_tool(LATEX_CANDIDATES, "pdflatex")
    if not pandoc:
        print("pandoc not found; expected it under %%LOCALAPPDATA%%\\Pandoc"
              % ())
        return 1
    if not pdflatex:
        print("pdflatex not found; expected it under "
              "%%LOCALAPPDATA%%\\Programs\\MiKTeX\\miktex\\bin\\x64")
        return 1
    print("pandoc   : %s" % pandoc)
    print("pdflatex : %s" % pdflatex)

    papers = PAPERS
    if args.paper:
        papers = [p for p in PAPERS
                  if Path(p).name.startswith(args.paper)]
        if not papers:
            raise SystemExit("no paper matches %r" % args.paper)

    for rel in papers:
        render(rel, pandoc, pdflatex)
    return 0


if __name__ == "__main__":
    sys.exit(main())
