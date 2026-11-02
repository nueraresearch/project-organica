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
| tables of seven columns or more are wrapped in `landscape` | pandoc divides the measure evenly, so a nine-column table gives each column 41 pt while its header word "Reachability" is 58 pt and has nothing to hyphenate against. No portrait size that is still readable recovers that; a landscape page does, and the column fractions follow `\linewidth`. Each column also loses 1.5 pt, because the fractions sum to the measure and the table's own box then sat 0.13 pt over it. |
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
`tlmgr install caption lm microtype pdflscape`. The versions that actually built the PDFs
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
- **It does not look at the pages.** The log proves there are no overfull
  boxes, the extraction proves the words are on them, and
  `verify_pdf_info` proves the file carries its title and author — but
  nothing in this pipeline rasterises a page, so figure placement, caption
  collisions, page breaks and Paper 02's two landscape tables are
  **unverified visually** until a person opens the PDF. No text check
  substitutes for that, and none of the checks above should be read as if it
  had.

→ `benchmarks/svg_to_pdf.py`; `benchmarks/make_font_widths.py`;
`benchmarks/helvetica_widths.json`; `benchmarks/render_papers.py`;
`benchmarks/paper-template.tex`; `tests/test_svg_to_pdf.py`;
`docs/ZENODO-DEPOSIT.md`.
