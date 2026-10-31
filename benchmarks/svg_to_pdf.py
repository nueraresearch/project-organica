"""Convert the repository's SVG figures to vector PDF.

The figures are the single source of truth for the papers' claims, so this
converts the committed SVG rather than drawing the figures a second time: a
figure drawn twice can disagree with itself.

The SVG vocabulary the figure generator emits is small and closed -- ``rect``,
``text``, ``line``, ``circle`` and ``polyline``, with no groups and no
transforms -- and this converter handles exactly that.  Anything outside it is
an error rather than a silent omission: a figure that loses an element in
conversion is a figure that lies.

Text metrics come from Adobe's AFM metrics for the Helvetica family, read from
the primary record and committed as ``benchmarks/helvetica_widths.json``
(``benchmarks/make_font_widths.py`` regenerates it).  The PDF embeds the
standard-14 Helvetica, whose advance widths those metrics describe.

    python benchmarks/svg_to_pdf.py docs/figure_p01_capacity_sweep.svg
    python benchmarks/svg_to_pdf.py --all
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WIDTHS_PATH = Path(__file__).resolve().parent / "helvetica_widths.json"

#: CSS pixels to PostScript points (72 pt per inch, 96 px per inch).
PX_TO_PT = 0.75

SVG_NS = "{http://www.w3.org/2000/svg}"

NAMED_COLORS = {
    "black": (0.0, 0.0, 0.0),
    "white": (1.0, 1.0, 1.0),
    "red": (1.0, 0.0, 0.0),
    "green": (0.0, 0.5, 0.0),
    "blue": (0.0, 0.0, 1.0),
    "gray": (0.5, 0.5, 0.5),
    "grey": (0.5, 0.5, 0.5),
    "silver": (0.75, 0.75, 0.75),
    "navy": (0.0, 0.0, 0.5),
}


class SvgError(ValueError):
    """The SVG uses something this converter does not implement."""


def load_widths() -> dict:
    if not WIDTHS_PATH.exists():
        raise SvgError("missing %s; run benchmarks/make_font_widths.py"
                        % WIDTHS_PATH.name)
    payload = json.loads(WIDTHS_PATH.read_text(encoding="utf-8"))
    return payload["_fonts"]


def parse_color(value: str | None):
    """Return (r, g, b) in 0..1, or None for 'none'."""
    if value is None:
        return None
    value = value.strip().lower()
    if value in ("none", "transparent", ""):
        return None
    if value.startswith("#"):
        digits = value[1:]
        if len(digits) == 3:
            digits = "".join(c * 2 for c in digits)
        if len(digits) != 6:
            raise SvgError("unsupported colour %r" % value)
        return tuple(int(digits[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    if value in NAMED_COLORS:
        return NAMED_COLORS[value]
    raise SvgError("unsupported colour %r" % value)


def num(element, attribute: str, default: float = 0.0) -> float:
    raw = element.get(attribute)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        raise SvgError("%s has a non-numeric %s=%r"
                       % (element.tag, attribute, raw))


def text_width(text: str, font: str, size: float) -> float:
    """The advance width of ``text`` in points."""
    table = load_widths()
    widths = table.get(font)
    if widths is None:
        raise SvgError("no width table for font %r" % font)
    total = 0
    for ch in text:
        code = ord(ch)
        if code > 255:
            raise SvgError("character %r is outside the WinAnsi range the "
                           "standard-14 fonts use" % ch)
        key = str(code)
        if key not in widths:
            raise SvgError("no advance width for character %r (code %d)"
                           % (ch, code))
        total += widths[key]
    return total * size / 1000.0


def escape_pdf_string(text: str) -> bytes:
    out = bytearray()
    for ch in text:
        code = ord(ch)
        if code > 255:
            raise SvgError("character %r is outside the WinAnsi range" % ch)
        if ch in "()\\":
            out.extend(b"\\" + ch.encode("latin-1"))
        elif code < 32:
            out.extend(b"\\%03o" % code)
        else:
            out.extend(ch.encode("latin-1"))
    return bytes(out)


def number(value: float) -> str:
    """A short, exact-enough decimal."""
    text = "%.4f" % value
    text = text.rstrip("0").rstrip(".")
    return text if text not in ("", "-0") else "0"


class Converter:
    def __init__(self, root: ET.Element):
        self.width = num(root, "width", 0.0)
        self.height = num(root, "height", 0.0)
        if not self.width or not self.height:
            raise SvgError("the SVG has no width/height")
        view_box = root.get("viewBox")
        if view_box:
            parts = [float(v) for v in re.split(r"[\s,]+", view_box.strip())]
            if len(parts) == 4 and parts[2] and parts[3]:
                # the viewBox is the user-unit box; width/height give the size
                self.vb_x, self.vb_y = parts[0], parts[1]
                self.scale = self.width / parts[2]
        else:
            self.vb_x = self.vb_y = 0.0
            self.scale = 1.0
        self.opacities: dict[str, int] = {}
        self.body: list[str] = []

    # -- coordinate helpers -------------------------------------------------

    def px(self, value: float) -> float:
        return (value - self.vb_x) * self.scale

    def py(self, value: float) -> float:
        return self.height - (value - self.vb_y) * self.scale

    def gs_for(self, opacity: float | None) -> str | None:
        if opacity is None or opacity >= 1.0:
            return None
        key = "%.3f" % opacity
        if key not in self.opacities:
            self.opacities[key] = len(self.opacities) + 1
        return "GS%d" % self.opacities[key]

    # -- element handlers ---------------------------------------------------

    #: Elements that carry metadata rather than marks.  They are read by
    #: assistive technology and by the figure's own caption, and they draw
    #: nothing.
    METADATA_TAGS = ("title", "desc", "metadata")

    def draw(self, element: ET.Element) -> None:
        tag = element.tag.replace(SVG_NS, "")
        if tag in self.METADATA_TAGS:
            return
        handler = getattr(self, "_draw_" + tag, None)
        if handler is None:
            raise SvgError("unsupported SVG element <%s>" % tag)
        handler(element)

    def _draw_g(self, element: ET.Element) -> None:
        """A group: its children, in order, with no transform."""
        if element.get("transform"):
            raise SvgError("a group with a transform is not supported")
        self.body.append("q")
        for child in element:
            self.draw(child)
        self.body.append("Q")

    def _opacity(self, element: ET.Element) -> str | None:
        raw = element.get("opacity")
        opacity = float(raw) if raw is not None else None
        return self.gs_for(opacity)

    def _stroke_setup(self, element: ET.Element) -> None:
        colour = parse_color(element.get("stroke"))
        if colour is None:
            return
        self.body.append("%s %s %s RG" % (number(colour[0]), number(colour[1]),
                                          number(colour[2])))
        width = num(element, "stroke-width", 1.0) * self.scale
        self.body.append("%s w" % number(width))
        cap = element.get("stroke-linecap")
        if cap == "round":
            self.body.append("1 J")
        elif cap == "square":
            self.body.append("2 J")
        elif cap:
            raise SvgError("unsupported stroke-linecap %r" % cap)
        join = element.get("stroke-linejoin")
        if join == "round":
            self.body.append("1 j")
        elif join == "bevel":
            raise SvgError("unsupported stroke-linejoin %r" % join)
        dashes = element.get("stroke-dasharray")
        if dashes:
            values = [float(v) for v in re.split(r"[\s,]+", dashes.strip()) if v]
            if not values:
                raise SvgError("empty stroke-dasharray")
            scaled = [number(v * self.scale) for v in values]
            self.body.append("[%s] 0 d" % " ".join(scaled))

    def _draw_rect(self, element: ET.Element) -> None:
        x = num(element, "x")
        y = num(element, "y")
        w = num(element, "width")
        h = num(element, "height")
        fill = parse_color(element.get("fill"))
        if fill is None:
            return
        gs = self._opacity(element)
        if gs:
            self.body.append("/%s gs" % gs)
        self.body.append("%s %s %s rg" % (number(fill[0]), number(fill[1]),
                                           number(fill[2])))
        self.body.append("%s %s %s %s re f"
                         % (number(self.px(x)), number(self.py(y + h)),
                            number(w * self.scale), number(h * self.scale)))

    def _draw_line(self, element: ET.Element) -> None:
        gs = self._opacity(element)
        if gs:
            self.body.append("/%s gs" % gs)
        self._stroke_setup(element)
        self.body.append("%s %s m %s %s l S"
                         % (number(self.px(num(element, "x1"))),
                            number(self.py(num(element, "y1"))),
                            number(self.px(num(element, "x2"))),
                            number(self.py(num(element, "y2")))))

    def _draw_circle(self, element: ET.Element) -> None:
        cx = num(element, "cx")
        cy = num(element, "cy")
        r = num(element, "r")
        if r <= 0:
            return
        gs = self._opacity(element)
        if gs:
            self.body.append("/%s gs" % gs)
        fill = parse_color(element.get("fill"))
        stroke = parse_color(element.get("stroke"))
        k = 0.5522847498307936 * r
        x0, y0 = self.px(cx), self.py(cy)
        rx, ry = r * self.scale, r * self.scale
        kx, ky = k * self.scale, k * self.scale
        path = [
            "%s %s m" % (number(x0 + rx), number(y0)),
            "%s %s %s %s %s %s c" % (number(x0 + rx), number(y0 + ky),
                                     number(x0 + kx), number(y0 + ry),
                                     number(x0), number(y0 + ry)),
            "%s %s %s %s %s %s c" % (number(x0 - kx), number(y0 + ry),
                                     number(x0 - rx), number(y0 + ky),
                                     number(x0 - rx), number(y0)),
            "%s %s %s %s %s %s c" % (number(x0 - rx), number(y0 - ky),
                                     number(x0 - kx), number(y0 - ry),
                                     number(x0), number(y0 - ry)),
            "%s %s %s %s %s %s c" % (number(x0 + kx), number(y0 - ry),
                                     number(x0 + rx), number(y0 - ky),
                                     number(x0 + rx), number(y0)),
        ]
        self.body.extend(path)
        if fill is not None and stroke is None:
            self.body.append("%s %s %s rg f" % (number(fill[0]),
                                               number(fill[1]), number(fill[2])))
        elif stroke is not None:
            self._stroke_setup(element)
            self.body.append("S")
        else:
            self.body.append("n")

    def _draw_polyline(self, element: ET.Element) -> None:
        raw = element.get("points")
        if not raw:
            raise SvgError("a polyline has no points")
        pairs = [p for p in re.split(r"[\s,]+", raw.strip()) if p]
        if len(pairs) % 2:
            raise SvgError("a polyline has an odd number of coordinates")
        coords = [(float(pairs[i]), float(pairs[i + 1]))
                  for i in range(0, len(pairs), 2)]
        if len(coords) < 2:
            return
        gs = self._opacity(element)
        if gs:
            self.body.append("/%s gs" % gs)
        fill = parse_color(element.get("fill"))
        stroke = parse_color(element.get("stroke"))
        self.body.append("%s %s m" % (number(self.px(coords[0][0])),
                                      number(self.py(coords[0][1]))))
        for x, y in coords[1:]:
            self.body.append("%s %s l" % (number(self.px(x)),
                                          number(self.py(y))))
        if fill is not None and stroke is None:
            self.body.append("%s %s %s rg f" % (number(fill[0]),
                                               number(fill[1]), number(fill[2])))
        elif stroke is not None:
            self._stroke_setup(element)
            self.body.append("S")
        else:
            self.body.append("n")

    def _draw_text(self, element: ET.Element) -> None:
        text = "".join(element.itertext())
        if not text:
            return
        size = num(element, "font-size", 12.0) * self.scale
        bold = (element.get("font-weight") or "").strip().lower() in (
            "bold", "bolder", "600", "700", "800", "900")
        font = "Helvetica-Bold" if bold else "Helvetica"
        fill = parse_color(element.get("fill"))
        if fill is None:
            fill = (0.0, 0.0, 0.0)
        width = text_width(text, font, size)
        x = self.px(num(element, "x"))
        anchor = element.get("text-anchor") or "start"
        if anchor == "middle":
            x -= width / 2.0
        elif anchor == "end":
            x -= width
        elif anchor != "start":
            raise SvgError("unsupported text-anchor %r" % anchor)
        y = self.py(num(element, "y"))
        gs = self._opacity(element)
        if gs:
            self.body.append("/%s gs" % gs)
        self.body.append("%s %s %s rg" % (number(fill[0]), number(fill[1]),
                                           number(fill[2])))
        self.body.append("BT /%s %s Tf %s %s Td (%s) Tj ET"
                         % ("F2" if bold else "F1", number(size),
                            number(x), number(y),
                            escape_pdf_string(text).decode("latin-1")))

    # -- output -------------------------------------------------------------

    def stream(self) -> bytes:
        return ("\n".join(self.body) + "\n").encode("latin-1")

    def pdf(self, title: str) -> bytes:
        page_w = self.width * PX_TO_PT
        page_h = self.height * PX_TO_PT
        content = self.stream()
        objects: list[bytes] = []

        def add(body: bytes) -> int:
            objects.append(body)
            return len(objects)

        catalog = add(b"")
        pages = add(b"")
        page = add(b"")
        contents = add(("<< /Length %d >>\nstream\n" % len(content)).encode("latin-1")
                       + content + b"endstream")
        font_regular = add(b"<< /Type /Font /Subtype /Type1 "
                           b"/BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
        font_bold = add(b"<< /Type /Font /Subtype /Type1 "
                        b"/BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        gs_ids: dict[str, int] = {}
        for key, index in sorted(self.opacities.items(), key=lambda kv: kv[1]):
            gs_ids[key] = add(("<< /Type /ExtGState /ca %s /CA %s >>"
                               % (key, key)).encode("latin-1"))
        info = add(("<< /Title (%s) /Producer (benchmarks/svg_to_pdf.py) >>"
                    % title.replace("(", "").replace(")", "")
                    ).encode("latin-1"))

        objects[catalog - 1] = ("<< /Type /Catalog /Pages %d 0 R >>"
                                % pages).encode("latin-1")
        objects[pages - 1] = ("<< /Type /Pages /Kids [%d 0 R] /Count 1 >>"
                              % page).encode("latin-1")
        # The Resources dictionary needs BOTH closing brackets: one for the
        # font dictionary and one for Resources itself.  Leaving the outer
        # one out nests /Contents inside /Resources, which a strict reader
        # treats as a page with no content.
        resources = ("<< /Font << /F1 %d 0 R /F2 %d 0 R >> >>"
                     % (font_regular, font_bold))
        if gs_ids:
            entries = " ".join("/GS%d %d 0 R" % (index, gs_ids[key])
                                for key, index in sorted(
                                    gs_ids.items(), key=lambda kv: kv[1]))
            resources = ("<< /Font << /F1 %d 0 R /F2 %d 0 R >> /ExtGState << "
                         "%s >> >>" % (font_regular, font_bold, entries))
        objects[page - 1] = (("<< /Type /Page /Parent %d 0 R /MediaBox "
                              "[0 0 %s %s] /Resources %s /Contents %d 0 R >>"
                              % (pages, number(page_w), number(page_h),
                                 resources, contents)).encode("latin-1"))

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for index, body in enumerate(objects, start=1):
            offsets.append(len(out))
            out += ("%d 0 obj\n" % index).encode("latin-1") + body + b"\nendobj\n"
        xref_at = len(out)
        out += ("xref\n0 %d\n" % (len(objects) + 1)).encode("latin-1")
        out += b"0000000000 65535 f \n"
        for offset in offsets[1:]:
            out += ("%010d 00000 n \n" % offset).encode("latin-1")
        out += ("trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n"
                "%d\n%%%%EOF\n" % (len(objects) + 1, catalog, info, xref_at)
                ).encode("latin-1")
        return bytes(out)


def convert(svg_path: Path, pdf_path: Path) -> int:
    root = ET.parse(svg_path).getroot()
    converter = Converter(root)
    for child in root:
        converter.draw(child)
    title = root.get("aria-label") or svg_path.stem
    pdf_path.write_bytes(converter.pdf(title))
    return len(converter.body)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", nargs="*", help="SVG files to convert")
    parser.add_argument("--all", action="store_true",
                        help="convert every figure in docs/")
    parser.add_argument("--outdir", default=None,
                        help="output directory (default: beside the SVG)")
    args = parser.parse_args(argv)

    if args.all:
        targets = sorted((REPO / "docs").glob("figure_p0*.svg"))
    else:
        targets = [Path(p) for p in args.svg]
    if not targets:
        parser.error("give at least one SVG or --all")

    for target in targets:
        outdir = Path(args.outdir) if args.outdir else target.parent
        outdir.mkdir(parents=True, exist_ok=True)
        out = outdir / (target.stem + ".pdf")
        try:
            count = convert(target, out)
        except SvgError as error:
            print("FAILED %s: %s" % (target.name, error))
            return 1
        print("wrote %s (%d operators)" % (out, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
