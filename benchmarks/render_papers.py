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
    #
    # A sentinel, not "\\\\": pandoc parses metadata values as markdown and
    # escapes a backslash pair, so the title page printed the literal "\\\\"
    # between the name, the ORCID and the address instead of breaking the line
    # (journal §131).  `fix_author_breaks` turns the sentinel into the break on
    # the build copy, where nothing can escape it again.
    author = author.replace(" \u2014 ", " %s " % AUTHOR_BREAK)
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


HIGHLIGHTING_RE = re.compile(r"\\begin\{Highlighting\}\[(?P<opts>[^\]]*)\]")


def keep_code_blocks_whole(tex_path: Path) -> int:
    """Stop a code block from being split across a page break.

    Paper 02's reproduction block broke after its eighth line and left two
    orphaned lines alone above the next heading.  A verbatim block is a
    sequence of ordinary lines, so LaTeX is free to break it anywhere; a
    reader copying the commands off the page gets a block that continues on a
    page they may not have.  fancyvrb's ``samepage`` option keeps the block in
    one piece, moving it whole to the next page rather than dividing it.

    Applied to every highlighted block rather than to the one that broke: the
    defect is a property of the environment, and the manuscript that broke is
    only the one whose block was long enough to show it.

    Returns the number of blocks examined.
    """
    text = tex_path.read_text(encoding="utf-8")

    def replace(match: re.Match) -> str:
        opts = match.group("opts").strip()
        opts = (opts + "," if opts else "") + "samepage=true"
        return "\\begin{Highlighting}[%s]" % opts

    out = HIGHLIGHTING_RE.sub(replace, text)
    if out != text:
        tex_path.write_text(out, encoding="utf-8")
    return len(HIGHLIGHTING_RE.findall(text))


#: The heading a wide table belongs to, so the two stay on one page.  Pandoc
#: emits ``#``, ``##`` and ``###`` as section, subsection and subsubsection, so
#: all three are matched: Paper 02's numbered sections are ``###``.
HEADING_BEFORE_TABLE_RE = re.compile(
    r"(?P<head>\\(?:sub)*section\{[^}]*\}(?:\s*\\label\{[^}]*\})?)"
    r"(?P<gap>\s*)\\begin\{samepage\}")

#: Enough vertical space for a heading plus a header row and the three data
#: rows these audit tables carry, with room over.
WIDE_TABLE_RESERVE = "110pt"


def _wide_table_size(columns: int) -> str:
    r"""One size down for seven or eight columns, two for nine or more.

    Measured, not guessed: at ``\footnotesize`` the nine-column ancestry table
    still put "Reachability" 4.31 pt into the margin, because a p-column cannot
    hyphenate a word into a width that has no room for any of its pieces.  At
    ``\scriptsize`` the same word is 38 pt in a 43 pt column.  Seven- and
    eight-column tables fit at ``\footnotesize`` and are left larger.
    """
    return "\\scriptsize" if columns >= 9 else "\\footnotesize"


def fit_wide_tables(tex_path: Path, min_columns: int = 7) -> list[int]:
    r"""Set the wide tables small enough to stay in the portrait measure.

    Pandoc divides the measure evenly between columns, so the nine-column
    ancestry table gives each column 41 pt at 11 pt while its header word
    "Reachability" is 58 pt.  The first fix rotated those tables onto landscape
    pages, which removed the overflow and introduced three standing defects
    instead: ``pdflscape`` breaks the page at both ends of the environment, so
    the heading arrived alone on the page before, and each three-row table sat
    at the top of an otherwise blank rotated sheet whose page number was
    rotated with it.

    The shortfall is about a third of the measure.  Setting the table a size or
    two down and narrowing the gutter from 6 pt to 4 pt recovers it inside the
    measure: nine columns gain 32 pt of text, and at ``\scriptsize`` the widest
    header word is 38 pt in a 43 pt column.  Nothing in the table is dropped,
    no column is merged, and the table stays in the flow beneath its heading.

    The heading is kept with its table by reserving the space it needs, not by
    asking politely.  A ``\filbreak`` before the block was not enough: the
    heading fitted at the foot of the page, the table did not, and the break
    between them won, leaving the heading alone --- which is the defect this
    pass exists to remove.  ``\keepwithnext`` measures what is left on the page
    and breaks before the heading when the block cannot fit, so the heading and
    its table always travel together.

    The threshold stays at seven columns, for the reason it was set: Paper 01's
    six-column tables set perfectly well at full size.

    Returns the column counts of the tables treated.
    """
    text = tex_path.read_text(encoding="utf-8")
    fitted: list[int] = []

    def replace(match: re.Match) -> str:
        columns = match.group("spec").count("p{")
        if columns < min_columns:
            return match.group(0)
        table = ("\\begin{longtable}[]{@{}%s@{}}%s\\end{longtable}"
                 % (match.group("spec"), match.group("body")))
        fitted.append(columns)
        return ("\\begin{samepage}\n\\begingroup%s\n"
                "\\setlength{\\tabcolsep}{4pt}\n%s\n"
                "\\endgroup\n\\end{samepage}"
                % (_wide_table_size(columns), table))

    out = LONGTABLE_RE.sub(replace, text)
    out = HEADING_BEFORE_TABLE_RE.sub(
        lambda m: "\\keepwithnext{%s}\n\\begin{samepage}\n%s%s" % (
            WIDE_TABLE_RESERVE, m.group("head"), m.group("gap")), out)
    if out != text:
        tex_path.write_text(out, encoding="utf-8")
    return fitted


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


PAPER_LABEL_RE = re.compile(r"^Paper\s+\d+\s*[:.\u2014-]\s*")


def manuscript_title(heading: str) -> str:
    """The manuscript's own title, with the project's "Paper N:" label off."""
    return PAPER_LABEL_RE.sub("", heading).strip()


def verify_title_matches(stem: str, heading: str) -> None:
    """Assert PDF_INFO declares the title the manuscript currently has.

    The title lives in two places -- the level-one heading and ``PDF_INFO`` --
    so a retitle can leave the PDF claiming a title the paper no longer has,
    and neither half looks wrong on its own.  The heading is the source of
    truth; the label ("Paper 1:") is the project's, not the paper's, and does
    not belong in the document properties.
    """
    declared = PDF_INFO[stem]["title"]
    expected = manuscript_title(heading)
    if declared != expected:
        raise SystemExit(
            "%s: PDF_INFO title %r does not match the manuscript heading %r; "
            "update PDF_INFO, or the heading if the retitle is wrong"
            % (stem, declared, expected))


AUTHOR_BREAK = "@AUTHORBREAK@"


def fix_author_breaks(tex_path: Path) -> int:
    """Turn the author-line sentinel into a real LaTeX line break.

    The separator cannot be handed to pandoc as a backslash pair: metadata
    values are parsed as markdown, and a pair survives into the ``.tex`` escaped,
    so the title page printed the two characters instead of breaking.  The
    sentinel passes through untouched and is replaced here, on the build copy.
    """
    text = tex_path.read_text(encoding="utf-8")
    count = text.count(AUTHOR_BREAK)
    if count:
        tex_path.write_text(text.replace(AUTHOR_BREAK, "\\\\"), encoding="utf-8")
    if AUTHOR_BREAK in tex_path.read_text(encoding="utf-8"):
        raise SystemExit("an author-line sentinel survived the rewrite")
    return count


def pin_figures(tex_path: Path) -> int:
    """Pin each figure where it is written, and drop the duplicate caption.

    Each manuscript already carries its own caption as the bold paragraph
    beneath the image, and pandoc's ``implicit_figures`` turns the image's alt
    text into a second ``\\caption``.  Two captions appear, and because the
    image is a float the pair can separate: in the 25-page build Figure 2 was
    carried onto a page of its own while its own caption stayed behind on the
    previous page, and the float page centred it under a quarter-page of white.

    float's ``[H]`` pins the image exactly where it is written, next to the
    caption the manuscript supplies, and the duplicated caption is removed.
    """
    text = tex_path.read_text(encoding="utf-8")
    removed = 0
    out: list[str] = []
    i = 0
    while True:
        start = text.find("\\begin{figure}", i)
        if start < 0:
            out.append(text[i:])
            break
        out.append(text[i:start])
        out.append("\\begin{figure}[H]")
        end = text.find("\\end{figure}", start)
        if end < 0:
            raise SystemExit("unterminated figure environment in %s" % tex_path.name)
        block = text[start + len("\\begin{figure}"):end]
        cap = block.find("\\caption{")
        if cap >= 0:
            depth, e = 0, cap + len("\\caption")
            while e < len(block):
                ch = block[e]
                if ch == "\\":
                    e += 2
                    continue
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        break
                e += 1
            block = block[:cap] + block[e + 1:]
            removed += 1
        out.append(block.rstrip("\n") + "\n")
        i = end
    tex_path.write_text("".join(out), encoding="utf-8")
    return removed


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

    verify_title_matches(stem, title)
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

    fix_author_breaks(build_tex)
    make_code_spans_breakable(build_tex)
    fix_table_captype(build_tex)
    keep_code_blocks_whole(build_tex)
    fit_wide_tables(build_tex)
    pin_figures(build_tex)

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
