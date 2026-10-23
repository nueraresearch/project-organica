"""
The before/after figure for the Ablation Matrix V2.

Four panels, drawn from the committed campaign artifact so the figure can
be regenerated without re-running the campaign:

  A  Theory population over time -- ALPHABETICAL (before) vs SALIENCE (after)
  B  Contradiction density over time -- the same two arms
  C  The salience distribution the two policies choose between
  D  Every metric, every colony -- which measurements carry signal

Output is SVG written by hand: the project is stdlib-only and has no
plotting dependency.

Usage:
    python benchmarks/figure_campaign.py
Writes docs/figure_campaign.svg
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

COLORS = {
    "FULL": "#1f4e79",
    "SALIENCE": "#c0504d",
    "NO_CONTRADICTIONS": "#7f7f7f",
    "NO_QUESTIONS": "#e8a33d",
    "NO_DREAMS": "#4f9d69",
    "ANTI_EIG": "#8064a2",
}
BG = "#ffffff"
FG = "#1a1a1a"
GRID = "#e3e3e3"


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Svg:
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="Helvetica,Arial,sans-serif">',
            f'<rect width="{w}" height="{h}" fill="{BG}"/>',
        ]

    def text(self, x, y, s, size=12, fill=FG, anchor="start", weight="normal",
             style=""):
        self.parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" {style}>{esc(s)}</text>')

    def line(self, x1, y1, x2, y2, stroke=GRID, width=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}/>')

    def polyline(self, points, stroke, width=1.6, opacity=1.0):
        if not points:
            return
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        self.parts.append(
            f'<polyline points="{d}" fill="none" stroke="{stroke}" '
            f'stroke-width="{width}" stroke-opacity="{opacity}" '
            f'stroke-linejoin="round"/>')

    def rect(self, x, y, w, h, fill, stroke="none", width=1, opacity=1.0):
        self.parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
            f'fill-opacity="{opacity}"/>')

    def circle(self, x, y, r, fill):
        self.parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}"/>')

    def save(self, path: Path):
        self.parts.append("</svg>")
        path.write_text("\n".join(self.parts), encoding="utf-8")
        print(f"wrote {path}")


def panel(svg: Svg, x, y, w, h, title):
    svg.rect(x, y, w, h, "#fbfbfb", stroke="#d0d0d0", width=1)
    svg.text(x + 14, y + 24, title, size=13, weight="bold")
    return (x + 58, y + 42, w - 78, h - 84)      # plot area


def axes(svg: Svg, px, py, pw, ph, ymin, ymax, xmax, ylabel, xlabel,
         yticks=5):
    svg.line(px, py + ph, px + pw, py + ph, stroke="#888", width=1.2)
    svg.line(px, py, px, py + ph, stroke="#888", width=1.2)
    for i in range(yticks + 1):
        v = ymin + (ymax - ymin) * i / yticks
        yy = py + ph - (v - ymin) / (ymax - ymin or 1) * ph
        svg.line(px, yy, px + pw, yy, stroke=GRID, width=1)
        svg.text(px - 8, yy + 4, f"{v:g}", size=10, fill="#555", anchor="end")
    for i in range(6):
        v = xmax * i / 5
        xx = px + pw * i / 5
        svg.text(xx, py + ph + 16, f"{int(v)}", size=10, fill="#555", anchor="middle")
    svg.text(px - 44, py + ph / 2, ylabel, size=10, fill="#444", anchor="middle",
             style='transform="rotate(-90)"')
    svg.text(px + pw / 2, py + ph + 34, xlabel, size=10, fill="#444", anchor="middle")


def series_points(values, px, py, pw, ph, ymin, ymax, xmax):
    pts = []
    n = len(values)
    for i, v in enumerate(values):
        if v is None:
            continue
        x = px + pw * (i / max(1, n - 1)) * (xmax / max(1, xmax))
        y = py + ph - (v - ymin) / (ymax - ymin or 1) * ph
        pts.append((x, y))
    return pts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", default=str(REPO / "docs" / "force_matrix.json"))
    ap.add_argument("--out", default=str(REPO / "docs" / "figure_campaign.svg"))
    args = ap.parse_args()

    path = Path(args.matrix)
    if not path.exists():
        print("campaign artifact not present:", path)
        sys.exit(1)
    doc = json.loads(path.read_text(encoding="utf-8"))
    rows = {r["colony"]: r for r in doc["rows"]}
    cycles = doc.get("cycles") or 0

    svg = Svg(1240, 900)
    svg.text(30, 34, "Organica Ablation Matrix V2 — before/after", size=19, weight="bold")
    svg.text(30, 55,
             "alphabetical (before) vs salience (after) retention, on the branch stimulus that closed the launch gates",
             size=12, fill="#555")
    svg.text(30, 72,
             f"{cycles} cycles per colony · one fixed seed per colony · substrate: tag counter scoped to world events",
             size=11, fill="#777")

    # ---- Panel A: theory population over time -------------------------------
    px, py, pw, ph = panel(svg, 30, 92, 580, 360,
                           "A · Theory population over time")
    arms = [c for c in ("FULL", "SALIENCE") if c in rows]
    theo = {c: rows[c]["series"]["theories"] for c in arms}
    ymax = max(max(v) for v in theo.values()) if theo else 8
    ymax = max(ymax, 1)
    axes(svg, px, py, pw, ph, 0, ymax, cycles, "theories", "cycle")
    for c in arms:
        svg.polyline(series_points(theo[c], px, py, pw, ph, 0, ymax, cycles),
                     COLORS[c], width=1.8)
    for i, c in enumerate(arms):
        lx = px + 14 + i * 190
        svg.rect(lx, py + 10, 18, 4, COLORS[c])
        svg.text(lx + 24, py + 16, c, size=11, fill=COLORS[c], weight="bold")

    # ---- Panel B: contradiction density over time ---------------------------
    px, py, pw, ph = panel(svg, 630, 92, 580, 360,
                           "B · Contradiction density over time")
    cd = {c: rows[c]["series"]["contradiction_density"] for c in arms}
    vals = [v for series in cd.values() for v in series if v is not None]
    lo, hi = (min(vals), max(vals)) if vals else (0, 1)
    pad = (hi - lo) * 0.1 or 1
    axes(svg, px, py, pw, ph, lo - pad, hi + pad, cycles,
         "raw contradiction / belief", "cycle")
    for c in arms:
        svg.polyline(series_points(cd[c], px, py, pw, ph, lo - pad, hi + pad, cycles),
                     COLORS[c], width=1.8)
    for i, c in enumerate(arms):
        lx = px + 14 + i * 190
        svg.rect(lx, py + 10, 18, 4, COLORS[c])
        svg.text(lx + 24, py + 16, c, size=11, fill=COLORS[c], weight="bold")

    # ---- Panel C: the salience distribution the policies choose between ----
    px, py, pw, ph = panel(svg, 30, 468, 580, 380,
                           "C · Salience distribution — what the two policies choose between")
    allsc = []
    for c in arms:
        series = rows[c]["series"].get("salience_flat") or []
        allsc.extend(series)
    if not allsc:
        allsc = [0.0, 1.0]
    lo, hi = min(allsc), max(allsc)
    if hi <= lo:
        hi = lo + 1
    bins = 26
    width = pw / bins
    for c in arms:
        series = rows[c]["series"].get("salience_flat") or []
        counts = [0] * bins
        for v in series:
            k = min(bins - 1, int((v - lo) / (hi - lo) * bins))
            counts[k] += 1
        top = max(counts) or 1
        for k, cnt in enumerate(counts):
            h = ph * cnt / top
            svg.rect(px + k * width + 1, py + ph - h, width - 2, h,
                     COLORS[c], opacity=0.35)
        svg.polyline([(px + k * width + width / 2, py + ph - ph * cnt / top)
                      for k, cnt in enumerate(counts)], COLORS[c], width=1.8)
    axes(svg, px, py, pw, ph, 0, 1, 1, "salience score (scaled)", "belief")
    svg.text(px - 44, py + ph / 2, "density", size=10, fill="#444", anchor="middle",
             style='transform="rotate(-90)"')
    for i, c in enumerate(arms):
        lx = px + 14 + i * 190
        svg.rect(lx, py + 10, 18, 4, COLORS[c])
        svg.text(lx + 24, py + 16, c, size=11, fill=COLORS[c], weight="bold")

    # ---- Panel D: every metric, every colony -------------------------------
    px, py, pw, ph = panel(svg, 630, 468, 580, 380,
                           "D · Every metric, every colony")
    metric_defs = [
        ("M1", "theory duty", lambda m: m["M1_theory_duty_cycle"]["whole_run"]),
        ("M2", "question duty", lambda m: m["M2_question_duty_cycle"]["whole_run"]),
        ("M3", "contradiction density", lambda m: m["M3_contradiction_density"]["mean"]),
        ("M4", "contradiction survival", lambda m: m["M4_contradiction_survival"]["rate"]),
        ("M5", "development velocity", lambda m: m["M5_development_velocity"]["new_per_100_cycles"]),
        ("M7", "belief lifetime", lambda m: m["M7_mean_hypothesis_lifetime"]["mean"]),
    ]
    colonies = [c for c in COLORS if c in rows]
    ncols = len(colonies)
    slot = pw / max(1, len(metric_defs))
    barw = slot / (ncols + 1)
    for mi, (code, label, get) in enumerate(metric_defs):
        vals = []
        for c in colonies:
            v = get(rows[c]["metrics"])
            vals.append(v if isinstance(v, (int, float)) else 0)
        lo, hi = min(vals + [0]), max(vals)
        span = (hi - lo) or 1
        base = px + mi * slot
        svg.text(base + slot / 2, py + 14, f"{code} {label}", size=10,
                 fill="#444", anchor="middle")
        for ci, c in enumerate(colonies):
            v = vals[ci]
            h = max(1.0, (v - lo) / span * (ph - 46))
            bx = base + 6 + ci * barw
            svg.rect(bx, py + ph - h, barw - 2, h, COLORS[c], opacity=0.85)
            svg.text(bx + (barw - 2) / 2, py + ph - h - 4, f"{v:.3g}", size=8,
                     fill=COLORS[c], anchor="middle")
    svg.text(px - 44, py + ph / 2, "value (scaled per metric)", size=10,
             fill="#444", anchor="middle", style='transform="rotate(-90)"')
    for i, c in enumerate(colonies):
        lx = px + 6 + i * 118
        svg.rect(lx, py + ph + 6, 14, 4, COLORS[c])
        svg.text(lx + 19, py + ph + 12, c, size=9, fill=COLORS[c])

    svg.text(30, 880,
             "Source: docs/force_matrix.json · generated by benchmarks/figure_campaign.py · "
             "metric definitions frozen in docs/FORCE-MATRIX-PREREGISTRATION.md §2",
             size=10, fill="#888")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    svg.save(out)


if __name__ == "__main__":
    main()
