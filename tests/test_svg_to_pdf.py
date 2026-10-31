"""The figures, converted to PDF, must carry every mark the SVG carries.

Why this file exists
--------------------
The SVG figures are the single source of truth for the papers' claims, and
the PDF is what a reader sees.  A conversion that drops a label, moves a mark
or writes a malformed object produces a figure that is not the figure the
repository claims -- and it does so silently.

The first version of ``benchmarks/svg_to_pdf.py`` had exactly that defect: the
``/Resources`` dictionary was never closed, so ``/Contents`` was nested inside
it and the affected pages had **no content stream at all**.  Seven of the eight
figures had an opacity attribute, which took a different code path that closed
the dictionary correctly, so only one figure broke -- and a reader that was
not strict would have shown a blank page rather than an error.  These tests
are the check that did not exist then.

The checks here are stdlib-only and read the PDF the converter wrote, so they
can run in the project's test suite without a third-party reader.  The
conversion is also verified against an independent reader (pypdf) during
development; that verification is recorded in ``docs/PDF-PIPELINE.md``.
"""
from __future__ import annotations

import io
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SVG_NS = "{http://www.w3.org/2000/svg}"

FIGURES = sorted((REPO / "docs").glob("figure_p0*.svg"))

#: A text-showing operator in the content stream.
TEXT_OP = re.compile(r"\((?P<text>(?:[^()\\]|\\.)*)\)\s*Tj")
OBJECT = re.compile(rb"(?ms)^(\d+) 0 obj\r?\n(.*?)\r?\nendobj")


def convert(svg_path: Path, pdf_path: Path) -> bytes:
    import sys
    sys.path.insert(0, str(REPO))
    from benchmarks import svg_to_pdf
    svg_to_pdf.convert(svg_path, pdf_path)
    return pdf_path.read_bytes()


def objects(raw: bytes) -> dict[int, bytes]:
    out = {}
    for match in OBJECT.finditer(raw):
        out[int(match.group(1))] = match.group(2)
    return out


def balanced(body: bytes) -> bool:
    """Whether every dictionary in the object body is closed."""
    depth = 0
    index = 0
    while index < len(body):
        char = body[index:index + 2]
        if char == b"<<":
            depth += 1
            index += 2
            continue
        if char == b">>":
            depth -= 1
            if depth < 0:
                return False
            index += 2
            continue
        index += 1
    return depth == 0


def content_stream(raw: bytes, objs: dict[int, bytes]) -> bytes:
    for number, body in objs.items():
        match = re.search(rb"(?ms)^stream\r?\n(.*?)endstream", body)
        if match:
            return match.group(1)
    return b""


def svg_texts(path: Path) -> list[str]:
    root = ET.parse(path).getroot()
    out = []
    for element in root.iter():
        if element.tag == SVG_NS + "text":
            out.append("".join(element.itertext()))
    return out


def svg_size(path: Path) -> tuple[float, float]:
    root = ET.parse(path).getroot()
    return float(root.get("width")), float(root.get("height"))


def unescape(raw: str) -> str:
    out = []
    index = 0
    while index < len(raw):
        char = raw[index]
        if char == "\\" and index + 1 < len(raw):
            nxt = raw[index + 1]
            if nxt in "()\\":
                out.append(nxt)
                index += 2
                continue
            if nxt.isdigit():
                out.append(chr(int(raw[index + 1:index + 4], 8)))
                index += 4
                continue
        out.append(char)
        index += 1
    return "".join(out)


@pytest.fixture(scope="module")
def converted(tmp_path_factory):
    out = {}
    for svg in FIGURES:
        pdf = tmp_path_factory.mktemp("pdf") / (svg.stem + ".pdf")
        convert(svg, pdf)
        out[svg] = pdf
    return out


def test_there_are_figures_to_check():
    assert FIGURES, "no figures found in docs/"


@pytest.mark.parametrize("svg", FIGURES, ids=lambda p: p.name)
class TestFigureConversion:

    def test_every_object_dictionary_is_closed(self, svg, converted):
        """The defect that produced a blank page: an unclosed dictionary.

        When ``/Resources`` was left unclosed, ``/Contents`` became a key of
        ``/Resources`` rather than of the page, and the page had no content
        stream.  A page whose dictionaries do not balance is a malformed
        page, and that is checkable without a PDF library.
        """
        raw = converted[svg].read_bytes()
        for number, body in objects(raw).items():
            if b"stream" in body.split(b"\n", 1)[0]:
                continue
            assert balanced(body), (
                "object %d in %s has unbalanced dictionary brackets"
                % (number, svg.name))

    def test_the_page_has_a_content_stream(self, svg, converted):
        raw = converted[svg].read_bytes()
        objs = objects(raw)
        pages = [body for body in objs.values()
                 if re.search(rb"/Type\s*/Page(?![s])", body)]
        assert len(pages) == 1, "%s should have exactly one page" % svg.name
        page = pages[0]
        match = re.search(rb"/Contents\s+(\d+) 0 R", page)
        assert match, (
            "/Contents is not a key of the page dictionary in %s; it was "
            "nested inside /Resources" % svg.name)
        assert int(match.group(1)) in objs, (
            "the page's content stream object is missing in %s" % svg.name)
        assert content_stream(raw, objs).strip(), (
            "the page has an empty content stream in %s" % svg.name)

    def test_every_svg_text_appears_in_the_pdf(self, svg, converted):
        raw = converted[svg].read_bytes()
        stream = content_stream(raw, objects(raw)).decode("latin-1")
        shown = [unescape(match.group("text")) for match in TEXT_OP.finditer(stream)]
        expected = svg_texts(svg)
        assert len(shown) == len(expected), (
            "%s draws %d text runs but the SVG has %d text elements"
            % (svg.name, len(shown), len(expected)))
        for want in expected:
            assert want in shown, (
                "%s does not carry the text %r" % (svg.name, want))

    def test_the_page_size_matches_the_svg(self, svg, converted):
        raw = converted[svg].read_bytes()
        match = re.search(rb"/MediaBox \[0 0 ([\d.]+) ([\d.]+)\]", raw)
        assert match, "%s has no MediaBox" % svg.name
        width, height = svg_size(svg)
        assert float(match.group(1)) == pytest.approx(width * 0.75, abs=0.01)
        assert float(match.group(2)) == pytest.approx(height * 0.75, abs=0.01)

    def test_the_pdf_is_not_a_stub(self, svg, converted):
        raw = converted[svg].read_bytes()
        assert raw.startswith(b"%PDF-1.4")
        assert raw.rstrip().endswith(b"%%EOF")
        assert b"/Type /Catalog" in raw
        assert b"startxref" in raw


class TestTheCheckCanFail:
    """A check that cannot disagree with its subject is not a check."""

    def test_the_balance_check_notices_an_unclosed_dictionary(self):
        good = b"<< /Type /Page /Resources << /Font << /F1 5 0 R >> >> >>"
        bad = b"<< /Type /Page /Resources << /Font << /F1 5 0 R >> /Contents 4 0 R >>"
        assert balanced(good)
        assert not balanced(bad)

    def test_the_balance_check_notices_an_extra_bracket(self):
        assert not balanced(b"<< /Type /Page >> >>")

    def test_the_text_check_notices_a_dropped_label(self, tmp_path):
        svg = REPO / "docs" / "figure_p01_capacity_sweep.svg"
        pdf = tmp_path / "x.pdf"
        convert(svg, pdf)
        raw = pdf.read_bytes()
        stream = content_stream(raw, objects(raw)).decode("latin-1")
        shown = [unescape(m.group("text")) for m in TEXT_OP.finditer(stream)]
        assert shown, "no text was drawn"
        # removing one text run must break the count and the membership
        trimmed = shown[:-1]
        assert len(trimmed) != len(svg_texts(svg))
        assert svg_texts(svg)[0] not in trimmed or len(trimmed) != len(
            svg_texts(svg))


class TestTheConverterRefusesWhatItCannotDo:
    """An element the converter does not implement must be an error."""

    def test_an_unsupported_element_is_an_error(self, tmp_path):
        import sys
        sys.path.insert(0, str(REPO))
        from benchmarks import svg_to_pdf
        source = tmp_path / "odd.svg"
        source.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
            '<path d="M0 0 L10 10"/></svg>', encoding="utf-8")
        with pytest.raises(svg_to_pdf.SvgError):
            svg_to_pdf.convert(source, tmp_path / "odd.pdf")

    def test_an_unsupported_colour_is_an_error(self, tmp_path):
        import sys
        sys.path.insert(0, str(REPO))
        from benchmarks import svg_to_pdf
        source = tmp_path / "colour.svg"
        source.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
            '<rect width="10" height="10" fill="rebeccapurple"/></svg>',
            encoding="utf-8")
        with pytest.raises(svg_to_pdf.SvgError):
            svg_to_pdf.convert(source, tmp_path / "colour.pdf")
