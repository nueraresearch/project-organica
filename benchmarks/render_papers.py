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

#: The deposited PDFs' own document properties.  Without these the file opens
#: with an empty title bar and imports into a reference manager as an untitled,
#: unattributed document, because hyperref only fills them from ``\title`` and
#: ``\author`` when asked -- and this template's title is a ``\parbox``, so
#: ``pdfusetitle`` would copy the markup instead of the words.  The titles are
#: the papers' own titles, not the project's "Paper 1/2" labels.
PDF_INFO = {
    "01_developmental_structure_formation": {
        "title": "Developmental Structure Formation in Organica 1",
        "subject": "Organica 1: whether developmental structure forms, what "
                   "it confers on external tasks, and where its claims stop",
        "keywords": "developmental machine intelligence; structure formation; "
                    "curriculum dependence; preregistration; negative results",
    },
    "02_persistent_structural_provenance": {
        "title": "Reconstructing Evidence and Selection from Organica's "
                 "Surviving State",
        "subject": "Organica 1: what a reconstruction from surviving state "
                   "can recover, and the boundaries of that claim",
        "keywords": "developmental machine intelligence; audit trace; "
                    "provenance; reconstruction; preregistration",
    },
}

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


def prepare(markdown: str) -> tuple[str, str, str, str]:
    """Return (build copy, title, author, plain author) for the manuscript.

    The plain author is the name alone, for the PDF's document properties;
    the typeset one also carries the ORCID and the address.
    """
    title_match = TITLE_RE.search(markdown)
    author_match = AUTHOR_RE.search(markdown)
    title = title_match.group("title") if title_match else ""
    author = author_match.group("author") if author_match else ""
    plain_author = author.split(" \u2014 ")[0].strip()
    # The author line is a single hbox in a LaTeX title block, so a name, an
    # ORCID URL and an address on one line run 63 pt into the margin.  Split
    # it at the em dashes the manuscript already uses as separators.
    author = author.replace(" \u2014 ", " \\\\ ")
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
    # The title is in the LaTeX title block; leaving the level-one heading in the
    # body typesets the title twice, the second time as a section heading that
    # runs into the margin.
    body = TITLE_RE.sub("", body, count=1).lstrip("\n")
    return body, title, author, plain_author


def run(command: list[str], cwd: Path, what: str) -> None:
    # pdfLaTeX writes its log in the locale's encoding, not UTF-8, so a
    # strict decode fails on a build that otherwise succeeded.
    result = subprocess.run(command, cwd=str(cwd), capture_output=True,
                            text=True, errors="replace", timeout=900)
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


CODE_SPAN_RE = re.compile(r"\\texttt\{([^{}]*)\}")


def make_code_spans_breakable(tex_path: Path) -> int:
    """Let a long texttt path wrap at its slashes instead of overflowing.

    Pandoc writes inline code as texttt{...}, and TeX has no break opportunity
    inside one: a repository path is a single unbreakable box.  The first build
    put ten of them into the margin, the widest by 140 pt.  Inserting
    allowbreak after each slash gives the line a place to end without
    hyphenating a path or changing a glyph.

    Length, not shape, decides the treatment.  A span over 24 characters is
    broken between characters, as \seqsplit does, whether or not it looks like
    a path: Paper 02's acceptance-criterion table is four columns of test names,
    each a single 40-plus-character token with no slash in it, and the earlier
    version of this function returned those untouched unless they contained a
    slash.  The table then ran 209 pt into the margin with no break opportunity
    anywhere in the column.  Shorter spans are broken only at a slash or an
    underscore escape, so ordinary words in code are not sprinkled with break
    points they do not need.

    The committed manuscript is untouched; this rewrites the build copy only.
    Returns the number of spans examined.
    """
    raw = tex_path.read_text(encoding="utf-8")

    def replace(match: re.Match) -> str:
        inner = match.group(1)
        if len(inner) > 24:
            # A long path, hash or identifier: allow a break between any two
            # characters, as \seqsplit does.
            units, i = [], 0
            while i < len(inner):
                # Keep an escape ("\\_") in one piece: splitting between the
                # backslash and the underscore turns the escape into a line break
                # and an unescaped underscore, which is a LaTeX error.
                width = 2 if inner[i] == "\\" and i + 1 < len(inner) else 1
                units.append(inner[i:i + width])
                i += width
            return "\\texttt{%s}" % "\\allowbreak{}".join(units)
        inner = inner.replace("/", "/\\allowbreak{}")
        inner = inner.replace("\\_", "\\_\\allowbreak{}")
        return "\\texttt{%s}" % inner

    out = CODE_SPAN_RE.sub(replace, raw)
    if out != raw:
        tex_path.write_text(out, encoding="utf-8")
    return len(CODE_SPAN_RE.findall(raw))


LONGTABLE_RE = re.compile(
    r"\\begin\{longtable\}\[\]\{@\{\}(?P<spec>.*?)@\{\}\}(?P<body>.*?)"
    r"\\end\{longtable\}", re.S)


def landscape_wide_tables(tex_path: Path, min_columns: int = 7) -> list[int]:
    """Typeset the wide tables on landscape pages.

    Pandoc divides the measure evenly between the columns, so a nine-column
    table gets 41 pt per column while its header says "Reachability" --- 58 pt
    of word with no break in it and nothing to hyphenate against.  The table
    ran 17 pt into the margin, and shrinking the font cannot recover a 40%
    shortfall without making the table unreadable.  A landscape page gives the
    same fractions of a much wider measure, which is what these audit tables
    need; the alternative was dropping a column and losing a measured quantity.

    The threshold is seven columns, not the six at which the measure starts to
    pinch: Paper 01 has two six-column tables that set perfectly well in
    portrait, and rotating them cost three pages for no gain.  At seven columns
    a portrait column is at most a seventh of the measure (67 pt), which cannot
    hold an ordinary fifteen-character word, and that is the point at which a
    portrait setting stops being a choice.

    The column fractions are recomputed by pandoc from ``\\linewidth``, so
    wrapping the table is enough: longtable measures the landscape measure at
    the point it starts.  Each column also loses 1.5 pt, because the widths sum
    to the measure exactly and the table's own box then sits 0.13 pt over it.

    Returns the column counts of the tables wrapped.
    """
    text = tex_path.read_text(encoding="utf-8")
    wrapped: list[int] = []

    def replace(match: re.Match) -> str:
        spec = match.group("spec")
        columns = spec.count("p{")
        if columns < min_columns:
            return match.group(0)
        spec = re.sub(r"\\linewidth - (\d+)\\tabcolsep",
                      r"\\linewidth - \1\\tabcolsep - 1.5pt", spec)
        table = ("\\begin{longtable}[]{@{}%s@{}}%s\\end{longtable}"
                 % (spec, match.group("body")))
        wrapped.append(columns)
        return "\\begin{landscape}\n%s\n\\end{landscape}" % table

    out = LONGTABLE_RE.sub(replace, text)
    if out != text:
        tex_path.write_text(out, encoding="utf-8")
    return wrapped


def read_pdf_info(pdf: Path, field: str) -> str | None:
    """Return one Info-dictionary string from the PDF's bytes, or None.

    pdfTeX writes the Info dictionary uncompressed as literal strings, with
    every byte above ASCII -- and every space -- as an octal escape.  A
    metadata string of ASCII text therefore arrives UTF-16BE behind a byte
    order mark, and a reader is a dozen lines rather than a dependency.
    """
    raw = pdf.read_bytes()
    marker = ("/%s(" % field).encode("ascii")
    start = raw.find(marker)
    if start < 0:
        return None
    out = bytearray()
    i = start + len(marker)
    while i < len(raw):
        char = raw[i:i + 1]
        if char == b")":
            break
        if char == b"\\":
            octal = raw[i + 1:i + 4]
            if re.fullmatch(rb"[0-7]{3}", octal):
                out.append(int(octal, 8))
                i += 4
                continue
            out.extend(raw[i + 1:i + 2])
            i += 2
            continue
        out.extend(char)
        i += 1
    if out.startswith(b"\xfe\xff"):
        return out[2:].decode("utf-16-be")
    return out.decode("latin-1")


def verify_pdf_info(pdf: Path, expected: dict[str, str]) -> None:
    """Assert the document properties are in the PDF, not only in the source.

    The check exists because "the PDF has a title" is otherwise an assumption
    about what hyperref did with a variable it was merely offered.
    """
    wrong = []
    for field, value in expected.items():
        actual = read_pdf_info(pdf, field)
        if actual != value:
            wrong.append("%s was %r" % (field, actual))
    if wrong:
        raise SystemExit("%s: document properties %s"
                         % (pdf.name, "; ".join(wrong)))


def render(rel: str, pandoc: str, pdflatex: str) -> Path:
    source = REPO / rel
    markdown = source.read_text(encoding="utf-8")
    body, title, author, plain_author = prepare(markdown)

    BUILD.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    build_md = BUILD / (stem + ".md")
    build_tex = BUILD / (stem + ".tex")
    build_md.write_text(body, encoding="utf-8")

    info = PDF_INFO[stem]
    metadata = [
        ("title", title),
        ("author", author),
        ("pdf-title", info["title"]),
        ("pdf-author", plain_author),
        ("pdf-subject", info["subject"]),
        ("pdf-keywords", info["keywords"]),
    ]
    command = [pandoc, str(build_md), "--from", "markdown+pipe_tables",
               "--to", "latex", "--standalone", "--template", str(TEMPLATE)]
    for key, value in metadata:
        command += ["--metadata", "%s:%s" % (key, value)]
    run(command + ["--output", str(build_tex)], BUILD, "pandoc")

    make_code_spans_breakable(build_tex)
    fix_table_captype(build_tex)
    landscape_wide_tables(build_tex)

    for _ in range(2):
        run([pdflatex, "-interaction=nonstopmode", "-halt-on-error",
             str(build_tex)], BUILD, "pdflatex")

    produced = BUILD / (stem + ".pdf")
    if not produced.exists():
        raise SystemExit("no PDF was produced for %s" % rel)
    target = OUT / (stem + ".pdf")
    shutil.copy2(produced, target)
    verify_pdf_info(target, {"Title": info["title"],
                             "Author": plain_author,
                             "Subject": info["subject"],
                             "Keywords": info["keywords"]})
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
