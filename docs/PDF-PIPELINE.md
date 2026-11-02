# PDF pipeline

**What it produces.** `papers/build/01_developmental_structure_formation.pdf`
and `papers/build/02_persistent_structural_provenance.pdf`, from the
manuscripts' Markdown sources and the repository's figure SVGs.

**Why there is a pipeline at all.** The repository's figures are SVG. SVG is
not acceptable to arXiv and is not what a reader opens. The obvious fix — draw
the figures again as PDF — is the wrong fix: it gives the claims two
renderers, and two renderers can disagree. So the SVG stays the single source
of truth and is *converted*.

## The three steps

### 1. SVG to vector PDF — `benchmarks/svg_to_pdf.py`

```
python benchmarks/svg_to_pdf.py --all
```

Writes `docs/figure_p0*.pdf` beside each SVG. The converter handles exactly
the vocabulary the figure generator emits — `rect`, `text`, `line`, `circle`,
`polyline`, with no groups and no transforms — and **raises on anything
else**, because a figure that silently loses an element in conversion is a
figure that lies.

Text metrics come from Adobe's AFM metrics for the Helvetica family, fetched
from the primary record and committed as `benchmarks/helvetica_widths.json`.
`benchmarks/make_font_widths.py` regenerates that file. The PDF embeds the
standard-14 Helvetica, whose advance widths those metrics describe; a text
run is therefore placed with the same width the SVG's own layout assumed, so
`text-anchor="middle"` and `text-anchor="end"` land where the SVG put them.

The pages are 96 dpi CSS pixels scaled to points (0.75 pt/px), so an 880×530
figure becomes a 660×397.5 pt page.

### 2. The check — `tests/test_svg_to_pdf.py`

```
python -m pytest tests/test_svg_to_pdf.py -q
```

46 tests. For every figure: every dictionary in every PDF object is closed;
the page has exactly one content stream; every text element in the SVG appears
as a text run in the PDF, and the count matches; the page size matches the
SVG's; and the file is a well-formed PDF with a cross-reference table.

**This check exists because the first converter was broken.** Its `/Resources`
dictionary was never closed, so `/Contents` was nested inside it and the
affected pages had **no content stream at all**. Seven of the eight figures
carry an opacity attribute, which took a different code path that closed the
dictionary correctly, so only one figure broke — and a lenient reader would
have shown a blank page rather than an error. The tests above are the check
that did not exist then.

The conversion was also verified against an **independent** PDF reader
(`pypdf`, which did not write the PDF): all eight figures' text extracts
exactly, and all eight page sizes match. `pypdf` is not a project dependency
and is not imported by the committed code; it was used to check the converter
during development, which is what caught the defect above.

### 3. Markdown to PDF — `benchmarks/render_papers.py`

```
python benchmarks/render_papers.py
```

pandoc converts the Markdown to LaTeX; MiKTeX's pdfLaTeX compiles it. The
template is `benchmarks/paper-template.tex`.

The build **does not modify the manuscript**. The committed Markdown keeps
pointing at the committed SVG; the rewrite to `.pdf` happens on a build copy
under `.scratch/paper-build/`. The title and the author line are lifted out
of the Markdown mechanically (the level-one heading is the title; the
`**Author:**` line is the author) so the LaTeX title block carries them
without the body repeating the author.

### What the template has to supply

The template replaces pandoc's own default template, so it inherits what that
template carried. Each of these was a build failure before it was a repair.

| What | Why the build needs it |
|---|---|
| `\usepackage{calc}` | Pandoc writes proportional column widths as `p{(\linewidth - 6\tabcolsep) * \real{0.2500}}`, and `\real` is a `calc` macro. |
| `\def\LTcaptype{}` | Pandoc wraps a table in `{\def\LTcaptype{none} % do not increment counter}`. longtable reads `\LTcaptype` as the **name of a counter** and steps it unless the value is empty, so `none` is read as a counter that does not exist. The empty value is exactly what pandoc means, so the generated file is rewritten to say it — on the build copy only. |
| `\DeclareUnicodeCharacter` for eleven characters | The manuscripts are written with typographic punctuation: em dash, en dash, minus sign, rightwards arrow, almost-equal, greater-or-equal, multiplication sign, plus-minus, section sign, Greek alpha, and `o` with grave. pdfLaTeX has no declaration for these by default. The mathematical ones are wrapped in `\ensuremath` so they are correct in text and in math mode alike. |
| `\usepackage{fancyvrb}` and `$highlighting-macros$` | Pandoc emits a code block that carries a class as `\begin{Shaded}\begin{Highlighting}[] ... \end{Highlighting}\end{Shaded}`. Both environments come from pandoc's default template. |
| `\hypersetup{pdftitle, pdfauthor, pdfsubject, pdfkeywords}` | hyperref fills none of these unless it is asked, so both PDFs opened with an **empty** title bar and imported into a reference manager as an untitled, unattributed document. `pdfusetitle` is not the repair here: this template's `\title` is a `\parbox`, and hyperref would copy the markup. The values arrive as pandoc metadata from `PDF_INFO` in the renderer — the paper's own title, not the project's "Paper 1/2" label — and `verify_pdf_info` reads all four back out of the built file, so "the PDF has a title" is a checked claim rather than an assumption about what hyperref did. Because the title would otherwise live in two places, `verify_title_matches` also asserts that `PDF_INFO`'s title is the manuscript's own level-one heading with the project's "Paper N:" label removed — the heading is the source of truth, so a retitle cannot ship under a stale title. |

## Build-copy rewrites

The build never edits a manuscript. Each repair below is applied to the copy
under `.scratch/paper-build/`, between pandoc and pdfLaTeX, by
`benchmarks/render_papers.py`. Every one of them was a box in the margin or a
word the deposited text could not spell before it was a rewrite.

| Rewrite | Defect it repairs |
|---|---|
| the level-one heading is removed from the body | pandoc typesets it as the title *and* as a numbered section heading; the second copy of the title ran 61 pt into the margin. |
| the author line is split at its em dashes | the author is a single unbreakable box in a `\title` block, so a name, an ORCID URL and an address ran 63 pt into the margin. |
| figure references point at the SVG's PDF | LaTeX cannot include an SVG. The committed Markdown keeps pointing at the committed SVG. |
| `\allowbreak` inside `\texttt` | inline code has no break opportunity, so ten paths were single unbreakable boxes, the widest 140 pt over. A span over 24 characters is broken between characters, as `\seqsplit` does, **whether or not it contains a slash**; shorter spans break only at a slash or an underscore escape. Length, not shape, decides: the earlier version of this rule skipped every slash-free span, and Paper 02's four-column table of 40-character test names then ran 209 pt into the margin with no break opportunity anywhere in the column. |
| `\LTcaptype` is emptied | longtable reads pandoc's `none` as the name of a counter and steps a counter that does not exist. |
| tables of seven columns or more are set a size or two down, in a narrower gutter | pandoc divides the measure evenly, so a nine-column table gives each column 41 pt while its header word "Reachability" is 58 pt. Rotating those tables onto landscape pages removed the overrun and cost three page-flow defects: `pdflscape` breaks the page at both ends, so the heading arrived alone on the page before and each three-row table sat at the top of an otherwise blank rotated sheet. Setting the table down and narrowing `\tabcolsep` from 6 pt to 4 pt returns 32 pt of text across nine columns, which is enough — `\footnotesize` for seven or eight columns, `\scriptsize` for nine or more, where the widest header word is 38 pt in a 43 pt column. |
| each figure is pinned where it is written, and keeps one caption | pandoc's `implicit_figures` turns an image's alt text into a float with its own `\caption`, so a figure page carried **two** captions — `Figure 2: Figure 2. …` — and, because the image was a float, the pair could separate: in the 25-page build Figure 2 landed alone on a page under a quarter-page of white while its own caption stayed on the page before. `pin_figures` rewrites each `\begin{figure}` as `[H]` (float.sty, installed) and drops the duplicated caption, leaving the manuscript's bold caption directly beneath its figure. |
| a heading is kept with the table beneath it | a longtable may break between the heading and its first row, and a `\filbreak` before the heading loses that contest: the heading fits, the table does not, and the heading stays behind — which is the defect the landscape pages were traded for. `\keepwithnext{110pt}` measures what is left on the page, the technique `needspace.sty` uses, written into the template because that package is not in this installation; when the heading and table cannot both fit it takes a forced break before the heading. |
| a code block is set with `samepage=true` | a verbatim block is a sequence of ordinary lines, so LaTeX will split it anywhere. Paper 02's reproduction block broke after eight lines and left two orphaned lines above the next heading; `samepage` moves the block whole instead. |
| code blocks are set at `footnotesize` | Paper 02's longest comment line is 103 characters and ran 61 pt over. Wrapping it would put a break into a block a reader may copy, so the block is set one size down instead. |

## The tools

pandoc and pdfLaTeX are looked up in the locations the script already knows — the Windows pandoc and MiKTeX install paths, then `PATH`:

| Tool | Location |
|---|---|
| pandoc 3.5 | `%LOCALAPPDATA%\Pandoc\pandoc.exe` |
| pdfTeX 1.40.29 (TeX Live 2026) | `%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe` |

MiKTeX's package auto-install is on (`initexmf --set-config-value=[MPM]auto-install=1`),
so a missing package is fetched on first use.

Those are the Windows paths the script was written against. The build recorded with this
deposit ran in a Linux container with pandoc 3.5 and TinyTeX on `PATH`, after
`tlmgr install caption lm microtype`. The versions that actually built the PDFs
are recorded in the reproduction bundle's `ENVIRONMENT.json`, so the pipeline states what
it ran on instead of assuming it.

Still absent on this machine: LibreOffice, Ghostscript, `pdftoppm`,
`pdftocairo`, Inkscape, and every Python imaging library the project does not
use. Nothing in the pipeline needs them.

## What this does not do

- It does not typeset the figures separately from the text; each figure is
  placed at its text width with its own caption, as in the Markdown.
- It does not check the rendered PDF's content against the manuscript's
  numbers. `tests/test_paper_numbers.py` does that, against the artifacts
  rather than against the PDF.
- It does not submit anything. The PDF is a deposit artifact.
- **It does not look at the pages by itself.** The log proves there are no
  overfull boxes, the extraction proves the words are on them, and
  `verify_pdf_info` proves the file carries its title and author — but
  nothing in this pipeline rasterises a page, so figure placement, caption
  collisions and page breaks are **not** covered by any check above. A
  rasteriser is not a build dependency and is not installed on this machine;
  to look at the pages, render them in a scratch environment
  (`python3 -m venv /tmp/pdfrender` then
  `/tmp/pdfrender/bin/pip install pymupdf`) and inspect the images. **Done
  2026-11-02 for all 40 pages:** Paper 01 renders clean — both multi-page
  tables break at row boundaries with the header repeated, and all five
  figures carry their captions and source lines. Paper 02 had **three layout
  defects** found in that review — a code block split across pages 7–8
  leaving two orphaned lines, a heading-only page 12, and two captionless,
  mostly blank landscape table pages (9 and 13) — all downstream of the
  landscape pass. They are fixed: those tables are set in portrait, the code
  block is unbreakable, and a heading now breaks the page rather than being
  left above its table (Journal §128). The rebuilt Paper 02 is 14 pages, 0
  errors, 0 overfull boxes. It still stays **unverified visually** until the
  owner looks at the new pages, because a machine check found the old defects
  only after they were looked at. No text check substitutes for looking, and none of the
  checks above should be read as if it had.

→ `benchmarks/svg_to_pdf.py`; `benchmarks/make_font_widths.py`;
`benchmarks/helvetica_widths.json`; `benchmarks/render_papers.py`;
`benchmarks/paper-template.tex`; `tests/test_svg_to_pdf.py`;
`docs/ZENODO-DEPOSIT.md`.

## How the figure PDFs are made

`benchmarks/figure_papers.py` writes **SVG** only, because the project is
standard-library-only and has no plotting dependency; the manuscripts embed the
**PDF** beside each SVG, and `render_papers.py` rewrites every `../docs/*.svg`
link to that PDF on the build copy. The two files therefore have to be kept in
step by hand, and nothing in the pipeline notices when they are not — the
deposited Figure 1 was rendered from a six-point version of a figure whose text
and caption describe eight ratios (journal §129).

Rendering is `svglib` + `reportlab` in a throwaway environment at the size the
committed files use (svglib already converts SVG px to PDF pt at 0.75, so the
scale is **1**, not 0.75 — scaling again renders the content at 56 % inside a
full-size page and leaves a blank band at the top):

```bash
python -m pip install svglib            # outside the project; the repo stays stdlib-only
python .scratch/svg2pdf.py              # writes docs/figure_p*.pdf from docs/figure_p*.svg
```

Check the result by extraction, not by eye alone: every page size should equal
the previous file's, and no text span should end past the page width
(`pymupdf`'s `get_text("dict")` gives the span bboxes). The generator's own guard
now uses real Helvetica advance widths, so a label that would overrun its canvas
is refused instead of clipped — which is what let three labels through before.
