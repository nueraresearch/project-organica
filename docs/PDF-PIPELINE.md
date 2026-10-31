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

## The tools

Neither tool is on PATH on this machine. The script finds both:

| Tool | Location |
|---|---|
| pandoc 3.13 | `%LOCALAPPDATA%\Pandoc\pandoc.exe` |
| MiKTeX-pdfTeX 4.23 (MiKTeX 25.12) | `%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe` |

MiKTeX's package auto-install is on (`initexmf --set-config-value=[MPM]auto-install=1`),
so a missing package is fetched on first use.

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

→ `benchmarks/svg_to_pdf.py`; `benchmarks/make_font_widths.py`;
`benchmarks/helvetica_widths.json`; `benchmarks/render_papers.py`;
`benchmarks/paper-template.tex`; `tests/test_svg_to_pdf.py`;
`docs/ZENODO-DEPOSIT.md`.
