"""Figures for the Organica manuscripts.

Every figure is drawn by hand as SVG from a committed artifact, so the
figures can be regenerated without re-running a campaign: the project is
stdlib-only and has no plotting dependency.

Every figure asserts the values it draws against the artifact before it
writes anything. A figure whose numbers cannot be found is an error, not an
empty plot -- a figure that silently draws nothing is worse than no figure,
and a figure drawn from a stale copy of a table is worse still. Where a
manuscript quotes a number, the assertion below pins the artifact to that
number, so the figure and the text cannot drift apart.

Usage:
    python benchmarks/figure_papers.py
Writes docs/figure_p*.svg
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"

INK = "#1a1a1a"
MUTED = "#5f5f5f"
FAINT = "#8a8a8a"
GRID = "#e6e6e6"
BLUE = "#1f4e79"
RED = "#c0504d"
AMBER = "#e8a33d"
GREEN = "#4f9d69"
PURPLE = "#8064a2"
GRAY = "#a8a8a8"
WHITE = "#ffffff"


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def need(cond, msg: str) -> None:
    if not cond:
        raise SystemExit(f"figure_papers: {msg}")


def load(rel: str):
    path = REPO / rel
    need(path.exists(), f"missing artifact {rel}")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


class Svg:
    def __init__(self, w: int, h: int, label: str = ""):
        self.w, self.h = w, h
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="Helvetica,Arial,sans-serif" '
            f'role="img" aria-label="{esc(label)}">',
            f'<title>{esc(label)}</title>',
            f'<rect width="{w}" height="{h}" fill="{WHITE}"/>',
        ]

    def text(self, x, y, s, size=12, fill=INK, anchor="start", weight="normal",
             style="", opacity=None):
        # SVG does not know how wide a string renders, so a note that overruns
        # the canvas is silently cut off by the renderer. Estimate the width and
        # refuse to draw it: a figure with a missing sentence looks finished.
        s = str(s)
        est = len(s) * size * 0.52
        if anchor == "start":
            need(x + est <= self.w + 2,
                 f"text overruns the canvas by ~{x + est - self.w:.0f}px at x={x:.0f}: {s[:44]}")
        elif anchor == "end":
            need(x - est >= -2,
                 f"text overruns the canvas by ~{-2 - (x - est):.0f}px at x={x:.0f}: {s[:44]}")
        else:
            need(x - est / 2 >= -2 and x + est / 2 <= self.w + 2,
                 f"text overruns the canvas at x={x:.0f}: {s[:44]}")
        o = f' opacity="{opacity}"' if opacity is not None else ""
        st = f' style="{style}"' if style else ""
        self.parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}"{o}{st}>{esc(s)}</text>')

    def line(self, x1, y1, x2, y2, stroke=INK, width=1, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}{o} stroke-linecap="round"/>')

    def rect(self, x, y, w, h, fill=INK, stroke=None, width=1, opacity=None):
        s = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" '
            f'fill="{fill}"{s}{o}/>')

    def circle(self, cx, cy, r, fill=INK, stroke=None, width=1, opacity=None):
        s = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"{s}{o}/>')

    def polyline(self, pts, stroke=INK, width=2, dash=None):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<polyline points="{d}" fill="none" stroke="{stroke}" '
            f'stroke-width="{width}"{da} stroke-linejoin="round"/>')

    def save(self, path: Path):
        # A mark drawn outside the canvas is silently dropped by the renderer,
        # which leaves a figure that looks finished and is missing a panel.
        # The check is here so that cannot happen quietly.
        for part in self.parts:
            for attr in ("x", "cx"):
                for m in re.finditer(rf'\b{attr}="(-?[\d.]+)"', part):
                    v = float(m.group(1))
                    need(-1 <= v <= self.w + 1,
                         f"{path.name}: {attr}={v} is outside the {self.w}px canvas")
            for attr in ("y", "cy"):
                for m in re.finditer(rf'\b{attr}="(-?[\d.]+)"', part):
                    v = float(m.group(1))
                    need(-1 <= v <= self.h + 1,
                         f"{path.name}: {attr}={v} is outside the {self.h}px canvas")
        self.parts.append("</svg>")
        data = "\n".join(self.parts)
        # An SVG with a malformed attribute does not fail loudly: the renderer
        # stops at the error and shows the part that parsed, which looks like a
        # figure with a missing panel. Parse it before writing.
        try:
            ET.fromstring(data)
        except ET.ParseError as exc:
            raise SystemExit(f"figure_papers: {path.name} is not well-formed XML: {exc}")
        path.write_text(data, encoding="utf-8")


def header(s: Svg, title: str, subtitle: str, source: str, width: int):
    # A subtitle that overruns the canvas is silently truncated by the renderer,
    # which looks like a finished sentence and is not one. The check is here so
    # that cannot happen quietly.
    need(len(subtitle) <= 132,
         f"subtitle is {len(subtitle)} chars and will not fit on one line: {subtitle[:48]}...")
    need(len(source) <= 150,
         f"source line is {len(source)} chars and will not fit on one line: {source[:48]}...")
    s.text(36, 38, title, size=16, weight="bold")
    s.text(36, 60, subtitle, size=11.5, fill=MUTED)
    s.text(36, s.h - 16, source, size=10, fill=FAINT)


def fmt(v, nd=4):
    return f"{v:.{nd}f}"


# ---------------------------------------------------------------------------
# Paper 1, Figure 1 -- the displacement curve
# ---------------------------------------------------------------------------

def fig_p01_displacement_curve():
    pl = load("docs/phase_l_results.json")
    arm = pl["summaries"]["V1"]
    curve = arm["curve"]
    need(len(curve) == 8, "expected 8 sweep points")
    need([c["label"] for c in curve] ==
         ["1:4", "1:3", "1:2", "1:1", "2:1", "3:1", "4:1", "6:1"], "sweep labels")
    need(arm["crossing_label"] == "3:1", "crossing label")
    need(arm["verdict"] == "INCONCLUSIVE", "verdict")

    # the numbers Paper 1 section 4.2 publishes, to three decimals
    published = {
        "1:4": (0.000, 0.743), "1:3": (0.000, 0.754), "1:2": (0.000, 0.748),
        "1:1": (0.000, 0.717), "2:1": (0.204, 0.606), "3:1": (0.706, 0.039),
        "4:1": (0.722, 0.000), "6:1": (0.715, 0.000),
    }
    for c in curve:
        di, pi = published[c["label"]]
        need(round(c["displacement_index_mean"], 3) == di,
             f"DI mismatch at {c['label']}: {c['displacement_index_mean']} vs {di}")
        need(round(c["preservation_index_mean"], 3) == pi,
             f"PI mismatch at {c['label']}: {c['preservation_index_mean']} vs {pi}")

    W, H = 840, 520
    s = Svg(W, H, "Phase L displacement and preservation indices against support ratio")
    header(s,
           "Phase L: the displacement curve is a step function",
           "Displacement index (DI) and preservation index (PI) against support ratio; "
           "30 seeds per point; bars are +/-1 sd across seeds.",
           "Source: docs/phase_l_results.json -> summaries.V1.curve  |  "
           "drawn by benchmarks/figure_papers.py",
           W)

    x0, x1 = 76, 800
    y_top, y_bot = 100, 392
    step = (x1 - x0) / len(curve)

    def y(v):
        return y_bot - v * (y_bot - y_top)

    for g in [i / 5 for i in range(6)]:
        s.line(x0, y(g), x1, y(g), stroke=GRID, width=1)
        s.text(x0 - 10, y(g) + 4, f"{g:.1f}", size=11, fill=MUTED, anchor="end")
    s.line(x0, y_bot, x1, y_bot, stroke=INK, width=1.2)

    for i, c in enumerate(curve):
        cx = x0 + (i + 0.5) * step
        for mean, sd, color, shape in (
                (c["displacement_index_mean"], c["displacement_index_stdev"], BLUE, "sq"),
                (c["preservation_index_mean"], c["preservation_index_stdev"], RED, "ci")):
            hi = min(1.0, mean + sd)
            lo = max(0.0, mean - sd)
            if hi > lo:
                s.line(cx, y(hi), cx, y(lo), stroke=color, width=1.4, opacity=0.85)
                s.line(cx - 4, y(hi), cx + 4, y(hi), stroke=color, width=1.4, opacity=0.85)
                s.line(cx - 4, y(lo), cx + 4, y(lo), stroke=color, width=1.4, opacity=0.85)
            if shape == "sq":
                s.rect(cx - 4.5, y(mean) - 4.5, 9, 9, fill=color)
            else:
                s.circle(cx, y(mean), 4.5, fill=color)

    # the crossing
    cxi = x0 + 5.5 * step
    s.line(cxi, y_top - 8, cxi, y_bot, stroke=INK, width=1.2, dash="4,4")
    s.text(cxi, y_top - 14, "crossing at 3:1", size=10.5, fill=INK, anchor="middle")

    for i, c in enumerate(curve):
        s.text(x0 + (i + 0.5) * step, y_bot + 20, c["label"], size=11.5, anchor="middle")
    s.text((x0 + x1) / 2, y_bot + 44,
           "support ratio (new events : memory events)", size=11.5, fill=MUTED, anchor="middle")

    # legend
    ly = 470
    s.rect(36, ly - 9, 13, 13, fill=BLUE)
    s.text(56, ly + 2, "DI -- displacement index (late structure retained)", size=11.5)
    s.circle(330, ly - 2, 5, fill=RED)
    s.text(342, ly + 2, "PI -- preservation index (early structure surviving)", size=11.5)

    out = DOCS / "figure_p01_displacement_curve.svg"
    s.save(out)
    return out


# ---------------------------------------------------------------------------
# Paper 1, Figure 2 -- which adjacent steps are real
# ---------------------------------------------------------------------------

def fig_p01_adjacent_differences():
    pl = load("docs/phase_l_results.json")
    arm = pl["summaries"]["V1"]
    diffs = arm["adjacent_differences"]
    need(len(diffs) == 7, "expected 7 adjacent steps")
    need(arm["decision_interval"]["level"] == "99.00%", "decision interval level")

    W, H = 840, 560
    s = Svg(W, H, "Paired differences between adjacent support ratios with 99% intervals")
    header(s,
           "Which steps are transitions, and which are plateau edges",
           "Paired difference between adjacent support ratios, 30 seeds paired by seed, "
           "with the preregistered 99% interval.",
           "Source: docs/phase_l_results.json -> summaries.V1.adjacent_differences  |  "
           "drawn by benchmarks/figure_papers.py",
           W)

    x0, x1 = 300, 792
    y_top, y_bot = 108, 404
    lo, hi = -0.7, 0.7

    def x(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)

    for g in [-0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6]:
        s.line(x(g), y_top, x(g), y_bot, stroke=GRID, width=1)
        s.text(x(g), y_bot + 18, f"{g:+.1f}", size=10.5, fill=MUTED, anchor="middle")
    s.line(x(0), y_top - 6, x(0), y_bot + 2, stroke=INK, width=1.3)
    s.text(x(0), y_bot + 36, "no change", size=10.5, fill=MUTED, anchor="middle")

    row_h = (y_bot - y_top) / len(diffs)
    for i, d in enumerate(diffs):
        yc = y_top + (i + 0.5) * row_h
        s.text(x0 - 16, yc + 4, f"{d['di']['from']} to {d['di']['to']}",
               size=11.5, anchor="end")
        for key, color, dy in (("di", BLUE, -10), ("pi", RED, 10)):
            m = d[key]
            lo_i, hi_i = m["interval"]
            excludes = (lo_i > 0) or (hi_i < 0)
            col = color if excludes else GRAY
            s.line(x(lo_i), yc + dy, x(hi_i), yc + dy, stroke=col, width=2.2,
                   opacity=None if excludes else 0.95)
            s.line(x(lo_i), yc + dy - 5, x(lo_i), yc + dy + 5, stroke=col, width=2.2)
            s.line(x(hi_i), yc + dy - 5, x(hi_i), yc + dy + 5, stroke=col, width=2.2)
            s.circle(x(m["mean_difference"]), yc + dy, 4.2, fill=col)

    s.text((x0 + x1) / 2, y_bot + 58,
           "paired difference between adjacent support ratios (99% bootstrap interval)",
           size=11.5, fill=MUTED, anchor="middle")

    ly = 494
    s.rect(36, ly - 9, 13, 13, fill=BLUE)
    s.text(56, ly + 2, "DI step", size=11.5)
    s.circle(126, ly - 2, 5, fill=RED)
    s.text(140, ly + 2, "PI step", size=11.5)
    s.circle(228, ly - 2, 4.2, fill=GRAY)
    s.text(242, ly + 2, "interval contains zero -- a plateau edge, not a transition",
           size=11.5, fill=MUTED)

    out = DOCS / "figure_p01_adjacent_differences.svg"
    s.save(out)
    return out


# ---------------------------------------------------------------------------
# Paper 1, Figure 3 -- the three Phase K families
# ---------------------------------------------------------------------------

K_NAMES = {
    "K1": "Incremental world modeling",
    "K2": "Belief revision",
    "K3": "Longitudinal knowledge integration",
}


def fig_p01_phase_k_families():
    pk = load("docs/phase_k_results.json")
    s_ = pk["summaries"]
    need(set(s_) == {"K1", "K2", "K3"}, "three Phase K families")

    published = {
        "K1": (0.5923, 0.9360, -0.3437, [-0.3773, -0.3123]),
        "K2": (0.4111, 0.9846, -0.5735, [-0.6162, -0.5309]),
        "K3": (0.0000, 0.8578, -0.8578, [-0.8598, -0.8571]),
    }
    for fam, s in s_.items():
        need(s["verdict"] == "REVERSED", f"{fam} verdict")
        need(s["decision_interval"]["level"] == "98.33%", f"{fam} interval level")
        p = published[fam]
        need(round(s["organica_primary_mean"], 4) == p[0], f"{fam} organica mean")
        need(round(s["best_simple_baseline_primary_mean"], 4) == p[1], f"{fam} baseline mean")
        d = s["paired_organica_minus_best_baseline"]
        need(round(d["mean"], 4) == p[2], f"{fam} paired mean")
        need(round(d["interval"][0], 4) == p[3][0] and round(d["interval"][1], 4) == p[3][1],
             f"{fam} paired interval")

    W, H = 840, 430
    s = Svg(W, H, "Phase K families: Organica minus the strongest simple baseline")
    header(s,
           "Every Phase K family is a clean loss",
           "Paired difference (Organica minus the best simple baseline), 10 seeds paired by seed, "
           "98.33% decision interval.",
           "Source: docs/phase_k_results.json -> summaries  |  "
           "drawn by benchmarks/figure_papers.py",
           W)

    x0, x1 = 306, 742
    y_top, y_bot = 112, 306
    lo, hi = -0.95, 0.05

    def x(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)

    for g in [-0.9, -0.6, -0.3, 0.0]:
        s.line(x(g), y_top, x(g), y_bot, stroke=GRID, width=1)
        s.text(x(g), y_bot + 18, f"{g:+.1f}", size=10.5, fill=MUTED, anchor="middle")
    s.line(x(0), y_top - 6, x(0), y_bot + 2, stroke=INK, width=1.3)

    row_h = (y_bot - y_top) / 3
    for i, fam in enumerate(["K1", "K2", "K3"]):
        d = s_[fam]["paired_organica_minus_best_baseline"]
        yc = y_top + (i + 0.5) * row_h
        s.text(36, yc - 14, f"{fam} -- {K_NAMES[fam]}", size=12, weight="bold")
        s.text(36, yc + 3,
               f"Organica {fmt(s_[fam]['organica_primary_mean'])}  |  "
               f"best baseline {fmt(s_[fam]['best_simple_baseline_primary_mean'])}",
               size=11, fill=MUTED)
        s.text(36, yc + 19, "REVERSED", size=11, fill=RED, weight="bold")
        lo_i, hi_i = d["interval"]
        s.line(x(lo_i), yc, x(hi_i), yc, stroke=RED, width=2.4)
        s.line(x(lo_i), yc - 5, x(lo_i), yc + 5, stroke=RED, width=2.4)
        s.line(x(hi_i), yc - 5, x(hi_i), yc + 5, stroke=RED, width=2.4)
        s.circle(x(d["mean"]), yc, 5, fill=RED)

    s.text((x0 + x1) / 2, y_bot + 42,
           "Organica minus best simple baseline (paired difference, 98.33% interval)",
           size=11.5, fill=MUTED, anchor="middle")
    s.text(36, H - 56,
           "All three intervals lie wholly below zero: each family is an excluded family, "
           "not an ambiguous one.", size=11.5, fill=INK)
    s.text(36, H - 38,
           "Positive would favor Organica. The interval is Bonferroni-adjusted across the "
           "three candidate families.", size=11.5, fill=MUTED)

    out = DOCS / "figure_p01_phase_k_families.svg"
    s.save(out)
    return out


# ---------------------------------------------------------------------------
# Paper 1, Figure 4 -- the acquisition benchmark and the readout that lost
# ---------------------------------------------------------------------------

def fig_p01_acquisition():
    gate = load("docs/acquisition_compositional_gate.json")
    pilot = load("docs/acquisition_single_seed_pilot.json")

    need(gate["n_worlds"] == 30, "n worlds")
    need(round(gate["mean_gap"], 4) == 0.1035, "headroom")
    need(gate["gate_nats"] == 0.05, "gate")

    W, H = 1040, 570
    s = Svg(W, H, "The rebuilt acquisition benchmark is discriminative, and the readout lost")
    header(s,
           "The benchmark was discriminative; the readout lost",
           "Left: benchmark headroom in nats against the 0.05-nat gate. Right: the Pilot 0 "
           "readout by learner.",
           "Source: docs/acquisition_compositional_gate.json, docs/acquisition_single_seed_pilot.json  |  "
           "drawn by benchmarks/figure_papers.py",
           W)

    # ---------------- panel A ----------------
    ax0, ax1 = 92, 470
    ay_top, ay_bot = 132, 388
    gmax = 0.22

    def ax(v):
        return ax0 + v / gmax * (ax1 - ax0)

    s.text(36, 108, "A. Benchmark headroom (nats)", size=13, weight="bold")
    for g in [0.0, 0.05, 0.10, 0.15, 0.20]:
        s.line(ax(g), ay_top, ax(g), ay_bot, stroke=GRID, width=1)
        s.text(ax(g), ay_bot + 18, f"{g:.2f}", size=10.5, fill=MUTED, anchor="middle")
    s.line(ax(gate["gate_nats"]), ay_top - 6, ax(gate["gate_nats"]), ay_bot + 2,
           stroke=INK, width=1.3, dash="4,4")
    s.text(ax(gate["gate_nats"]) + 6, ay_top + 4, "gate 0.05 nats", size=10.5, fill=INK)

    bars = [
        ("All 30 worlds", gate["mean_gap"], gate["gap_lower_99"], gate["gap_upper_99"]),
        ("Withheld cell", gate["gap_on_held_cell"]["mean"],
         gate["gap_on_held_cell"]["lower_99"], gate["gap_on_held_cell"]["upper_99"]),
        ("Other cells", gate["gap_on_other_cells"]["mean"],
         gate["gap_on_other_cells"]["lower_99"], gate["gap_on_other_cells"]["upper_99"]),
    ]
    bh = 34
    for i, (name, mean, l, h) in enumerate(bars):
        yc = ay_top + 44 + i * 78
        s.text(ax0, yc - bh / 2 - 10, name, size=11.5, fill=INK)
        s.rect(ax(0), yc - bh / 2, ax(mean) - ax(0), bh, fill=BLUE, opacity=0.9)
        s.line(ax(l), yc, ax(h), yc, stroke=INK, width=2.2)
        s.line(ax(l), yc - 6, ax(l), yc + 6, stroke=INK, width=2.2)
        s.line(ax(h), yc - 6, ax(h), yc + 6, stroke=INK, width=2.2)
        s.text(ax(max(h, mean)) + 12, yc + 4, f"{mean:.4f}", size=11.5, weight="bold")
    s.text((ax0 + ax1) / 2, ay_bot + 40,
           "Bayes ceiling minus best simple baseline (99% interval)",
           size=11, fill=MUTED, anchor="middle")

    # ---------------- panel B ----------------
    bx0, bx1 = 560, 996
    by_top, by_bot = 132, 388
    blo, bhi = 0.25, 0.50

    def by(v):
        return by_bot - (v - blo) / (bhi - blo) * (by_bot - by_top)

    s.text(536, 108, "B. Pilot 0 readout (log-loss)", size=13, weight="bold")
    for g in [0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
        s.line(bx0, by(g), bx1, by(g), stroke=GRID, width=1)
        s.text(bx0 - 10, by(g) + 4, f"{g:.2f}", size=10.5, fill=MUTED, anchor="end")

    c1 = pilot["cells"]["cell_1_organica_P_none_E_pres"]["scores"]
    c7 = pilot["cells"]["cell_7_replay_E_pres"]["scores"]
    c9 = pilot["cells"]["cell_9_statistical_E_pres"]["scores"]
    base = pilot["references"]["base_rate"]
    bayes = pilot["references"]["bayes_ceiling"]

    def ll(block, key):
        return block[key]["house_shape"]["log_loss"]

    learners = [
        ("Organica", ll(c1, "retention"), ll(c1, "transfer_diagnostic"), ll(c1, "revision"), RED),
        ("Replay", ll(c7, "retention"), ll(c7, "transfer"), ll(c7, "revision"), GRAY),
        ("Statistical", ll(c9, "retention"), ll(c9, "transfer"), ll(c9, "revision"), GRAY),
        ("Base rate", ll(base, "retention"), ll(base, "transfer"), ll(base, "revision"), AMBER),
        ("Bayes ceiling", ll(bayes, "retention"), ll(bayes, "transfer"), ll(bayes, "revision"), BLUE),
    ]
    need(round(learners[0][1], 6) == 0.453018, "organica retention")
    need(round(learners[4][1], 6) == 0.276259, "bayes retention")

    floor = pilot["cells"]["cell_8_replay_E_rem"]["scores"]["retention"]["house_shape"]["log_loss"]
    need(round(floor, 6) == 0.403045, "floor")

    group_w = (bx1 - bx0) / len(learners)
    bar_w = 22
    for gi, (name, r, t, v, color) in enumerate(learners):
        gx = bx0 + gi * group_w + group_w / 2
        for bi, (v, sub) in enumerate(((r, "ret"), (t, "xfer"), (v, "rev"))):
            bx = gx + (bi - 1) * (bar_w + 3) - bar_w / 2
            top = by(v)
            s.rect(bx, top, bar_w, by_bot - top, fill=color,
                   opacity=0.95 if name == "Organica" else 0.65)
        s.text(gx, by_bot + 18, name, size=10.5, anchor="middle",
               fill=INK if name == "Organica" else MUTED,
               weight="bold" if name == "Organica" else "normal")
    s.line(bx0, by(floor), bx1, by(floor), stroke=INK, width=1.3, dash="5,4")
    s.text(bx1, by(floor) - 7, "floor after episodes deleted (0.403045)",
           size=10.5, fill=INK, anchor="end")

    s.text((bx0 + bx1) / 2, by_bot + 40,
           "three readout conditions (retention / transfer / revision)",
           size=11, fill=MUTED, anchor="middle")
    s.text(36, 446,
           "Organica's readout is worse than the baselines' score after their episodes were "
           "deleted.", size=11.5, fill=INK)
    s.text(36, 464,
           "The transfer column is a diagnostic for Organica, not a measurement of transfer: "
           "the acquisition gate failed.", size=11, fill=MUTED)

    out = DOCS / "figure_p01_acquisition.svg"
    s.save(out)
    return out


# ---------------------------------------------------------------------------
# Paper 1, Figure 5 -- the capacity dose-response
# ---------------------------------------------------------------------------

def fig_p01_capacity_sweep():
    sweep = load("docs/gate13_capacity_sweep.json")
    caps = ["20", "40", "80", "None"]
    labels = ["cap 20", "cap 40", "cap 80", "uncapped"]
    seeds = sorted(sweep.keys())
    need(len(seeds) == 5, "five seeds")
    for seed in seeds:
        need(set(sweep[seed].keys()) == set(caps), f"caps for {seed}")

    cov = {c: [] for c in caps}
    for seed in seeds:
        for c in caps:
            row = sweep[seed][c]
            need(row["world_edges"] == 112, "world edges")
            cov[c].append(row["asserted_coverage"])
        # the gate must fail on the frozen cap and pass once the budget is raised
        need(sweep[seed]["20"]["passed_gate_13"] is False,
             f"gate must fail at the frozen cap for {seed}")
        need(sweep[seed]["None"]["passed_gate_13"] is True,
             f"gate must pass once the cap is removed for {seed}")

    lo20, hi20 = min(cov["20"]), max(cov["20"])
    loNone, hiNone = min(cov["None"]), max(cov["None"])
    need(round(lo20, 4) == 0.0 and round(hi20, 4) == 0.0268, "cap-20 range")
    need(round(loNone, 4) == 0.9911 and round(hiNone, 4) == 1.0, "uncapped range")

    W, H = 880, 530
    s = Svg(W, H, "Asserted structure coverage against the candidate budget")
    header(s,
           "Coverage is a steep dose-response in the selection budget",
           "Fraction of the world's 112 relations the organism asserted, against the candidate "
           "budget; five diagnostic seeds per point.",
           "Source: docs/gate13_capacity_sweep.json  |  drawn by benchmarks/figure_papers.py",
           W)

    x0, x1 = 96, 790
    y_top, y_bot = 116, 376

    def y(v):
        return y_bot - v * (y_bot - y_top)

    for g in [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]:
        stroke = INK if g == 0.5 else GRID
        width = 1.3 if g == 0.5 else 1
        dash = "5,4" if g == 0.5 else None
        s.line(x0, y(g), x1, y(g), stroke=stroke, width=width, dash=dash)
        s.text(x0 - 10, y(g) + 4, f"{g:.1f}", size=11,
               fill=INK if g == 0.5 else MUTED, anchor="end")
    s.text(x1 + 6, y(0.5) + 4, "gate 0.50", size=10.5, fill=INK)

    step = (x1 - x0) / len(caps)
    for i, c in enumerate(caps):
        cx = x0 + (i + 0.5) * step
        pts = []
        for j, v in enumerate(cov[c]):
            px = cx + (j - (len(cov[c]) - 1) / 2) * 16
            s.circle(px, y(v), 4.5, fill=BLUE, opacity=0.75)
            pts.append((px, y(v)))
        s.polyline(pts, stroke=BLUE, width=1.6, dash="3,3")
        mean = sum(cov[c]) / len(cov[c])
        s.circle(cx, y(mean), 5.5, fill=BLUE)
        s.text(cx, y(mean) - 14, f"{mean:.3f}", size=10.5, fill=BLUE, anchor="middle")
        s.text(cx, y_bot + 20, labels[i], size=11.5, anchor="middle")

    s.text((x0 + x1) / 2, y_bot + 44,
           "candidate budget (MAX_PREDICTIONS cap)", size=11.5, fill=MUTED, anchor="middle")
    s.text(36, 450,
           "At the frozen cap of 20 the organism asserts almost nothing; raising the budget "
           "restores coverage.", size=11.5)
    s.text(36, 468,
           "The budget is the proximate bound: precision never exceeds 0.3443 at any budget "
           "under either allocation rule.", size=11.5, fill=MUTED)

    out = DOCS / "figure_p01_capacity_sweep.svg"
    s.save(out)
    return out


# ---------------------------------------------------------------------------
# Paper 2, Figure 1 -- the three arms, and whether the check could have failed
# ---------------------------------------------------------------------------

def fig_p02_reconstruction_arms():
    arms = [
        ("default", "docs/audit_trace_probe.json", "default arm"),
        ("stress", "docs/audit_trace_probe_stress.json", "stress arm"),
        ("tie", "docs/audit_trace_probe_tie.json", "forced-tie arm"),
    ]
    data = []
    for key, rel, name in arms:
        d = load(rel)
        s_ = d["summary"]
        a3 = d["A3_ancestry_honesty"]
        a7 = d["A7_event_level_attribution"]
        need(d["A1_evidence_replay_aggregate"]["cycles_failing"] == 0, f"{key} A1")
        need(d["A2_selection_reconstruction"]["cycles_failing"] == 0, f"{key} A2")
        need(a3["structures_resolved"] == a3["structures_checked"], f"{key} A3")
        need(a7["edge_mismatches"] == [], f"{key} A7")
        data.append({
            "name": name,
            "cycles": d["protocol"]["cycles"],
            "beliefs": d["A1_evidence_replay_aggregate"]["beliefs_checked"],
            "structures": a3["structures_checked"],
            "died": s_["total_died"],
            "lost": s_["total_lost"],
            "max_died": s_["max_died"],
            "max_lost": s_["max_lost"],
            "ties": a7["timestamp_ties"]["stores_with_tied_window"],
        })

    need(data[0]["beliefs"] == 1412 and data[0]["structures"] == 8061, "default arm counts")
    need(data[0]["lost"] == 0, "default arm lost must be zero (the cap never bound)")
    need(data[1]["lost"] == 403, "stress arm lost count")
    need(data[2]["ties"] == 479, "tie arm ties")

    W, H = 1080, 560
    s = Svg(W, H, "The three audit-trace arms and the non-vacuity of the selection check")
    header(s,
           "The selection check could only fail where the contest was decided",
           "Candidates dropped and candidates that lost on rank, per arm, with what each arm "
           "checked.",
           "Source: docs/audit_trace_probe.json, docs/audit_trace_probe_stress.json, "
           "docs/audit_trace_probe_tie.json  |  drawn by benchmarks/figure_papers.py",
           W)

    # ---------------- panel A: candidates that lost on rank ----------------
    ax0, ax1 = 118, 556
    ay_top, ay_bot = 152, 386
    lmax = 450

    def ay(v):
        return ay_bot - v / lmax * (ay_bot - ay_top)

    s.text(ax0 - 22, 122, "A. Candidates that lost on rank", size=13, weight="bold")
    for g in [0, 100, 200, 300, 400]:
        s.line(ax0, ay(g), ax1, ay(g), stroke=GRID, width=1)
        s.text(ax0 - 10, ay(g) + 4, f"{g}", size=10.5, fill=MUTED, anchor="end")
    s.line(ax0, ay_bot, ax1, ay_bot, stroke=INK, width=1.2)

    gstep = (ax1 - ax0) / 3
    for i, a in enumerate(data):
        cx = ax0 + (i + 0.5) * gstep
        bw = 74
        top = ay(a["lost"])
        if a["lost"] > 0:
            s.rect(cx - bw / 2, top, bw, ay_bot - top, fill=RED, opacity=0.9)
        else:
            s.rect(cx - bw / 2, ay_bot - 2, bw, 2, fill=RED, opacity=0.9)
        s.text(cx, top - 10, f"{a['lost']}", size=13, weight="bold", anchor="middle",
               fill=RED if a["lost"] else MUTED)
        s.text(cx, top - 26, f"max {a['max_lost']} in one cycle", size=10,
               anchor="middle", fill=FAINT)
        s.text(cx, ay_bot + 22, a["name"], size=12, anchor="middle", weight="bold")
        s.text(cx, ay_bot + 40, f"{a['cycles']} cycles  |  {a['beliefs']:,} beliefs",
               size=10, anchor="middle", fill=MUTED)
        s.text(cx, ay_bot + 54, f"{a['structures']:,} structures checked",
               size=10, anchor="middle", fill=MUTED)

    s.text(36, ay_bot + 88,
           "In the default and forced-tie arms no candidate ever lost on rank, so the "
           "selection test could not have failed there.", size=11.5)
    s.text(36, ay_bot + 106,
           "The stress arm carries the non-vacuity argument: the cap bound, and 403 "
           "candidates lost on it.", size=11.5, fill=MUTED)

    # ---------------- panel B: candidates dropped ----------------
    bx0, bx1 = 676, 1042
    by_top, by_bot = 152, 386
    dmax = 6

    def dy(v):
        return by_bot - v / dmax * (by_bot - by_top)

    s.text(bx0 - 22, 122, "B. Candidates dropped (died)", size=13, weight="bold")
    for g in [0, 2, 4, 6]:
        s.line(bx0, dy(g), bx1, dy(g), stroke=GRID, width=1)
        s.text(bx0 - 10, dy(g) + 4, f"{g}", size=10.5, fill=MUTED, anchor="end")
    s.line(bx0, by_bot, bx1, by_bot, stroke=INK, width=1.2)

    gstep2 = (bx1 - bx0) / 3
    for i, a in enumerate(data):
        cx = bx0 + (i + 0.5) * gstep2
        bw = 62
        top = dy(a["died"])
        s.rect(cx - bw / 2, top, bw, by_bot - top, fill=GRAY, opacity=0.9)
        s.text(cx, top - 10, f"{a['died']}", size=13, weight="bold", anchor="middle")
        s.text(cx, top - 26, f"max {a['max_died']} in one cycle", size=10,
               anchor="middle", fill=FAINT)
        s.text(cx, by_bot + 22, a["name"], size=11.5, anchor="middle", fill=MUTED)

    s.text(36, ay_bot + 124,
           "The forced-tie arm additionally made 479 stores carry a tied timestamp window, "
           "and the observer still reproduced the engine's choice.", size=11.5, fill=MUTED)

    out = DOCS / "figure_p02_reconstruction_arms.svg"
    s.save(out)
    return out


def fig_p02_self_sourcing():
    d = load("docs/audit_trace_probe.json")
    a7 = d["A7_event_level_attribution"]
    distinct = a7["distinct_evidence"]
    refs = a7["support_references"]
    alltr = a7["all_transitions_recorded"]

    pops = [
        ("distinct supporting transitions\nbehind reported beliefs",
         distinct["self_sourced"], distinct["total_transitions"],
         "the pre-committed disqualifier's figure"),
        ("support references across\nreporting cycles",
         refs["self_sourced"], refs["total"],
         "a weighted view of reported support"),
        ("all distinct transitions\nthe observer recorded",
         alltr["self_sourced"], alltr["total_transitions"],
         "context, not the disqualifier's figure"),
    ]
    need((distinct["self_sourced"], distinct["total_transitions"]) == (802, 4481), "distinct pop")
    need((refs["self_sourced"], refs["total"]) == (53980, 307857), "reference pop")
    need((alltr["self_sourced"], alltr["total_transitions"]) == (5436, 12583), "all pop")

    W, H = 840, 495
    s = Svg(W, H, "Self-sourced share against three separately named populations")
    header(s,
           "The same ratio, against three differently named populations",
           "Share of self-sourced transitions, reported separately for each population the "
           "observer measured.",
           "Source: docs/audit_trace_probe.json -> A7_event_level_attribution  |  "
           "drawn by benchmarks/figure_papers.py",
           W)

    x0, x1 = 96, 800
    y_top, y_bot = 128, 344

    def y(v):
        return y_bot - v * (y_bot - y_top)

    for g in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
        s.line(x0, y(g), x1, y(g), stroke=GRID, width=1)
        s.text(x0 - 10, y(g) + 4, f"{g:.0%}", size=11, fill=MUTED, anchor="end")

    step = (x1 - x0) / len(pops)
    for i, (name, n, total, note) in enumerate(pops):
        cx = x0 + (i + 0.5) * step
        share = n / total
        bw = 96
        s.rect(cx - bw / 2, y(share), bw, y_bot - y(share), fill=BLUE, opacity=0.9)
        s.text(cx, y(share) - 12, f"{share:.1%}", size=15, weight="bold", anchor="middle")
        s.text(cx, y_bot + 22, f"{n:,} of {total:,}", size=11, anchor="middle", fill=INK)
        for j, line in enumerate(name.split("\n")):
            s.text(cx, y_bot + 40 + j * 15, line, size=10.5, anchor="middle", fill=MUTED)
        s.text(cx, y_bot + 72, note, size=10, anchor="middle", fill=FAINT, style="font-style:italic")

    s.text(36, 442,
           "A count must be named as what it counts: the same phenomenon, measured over "
           "three populations.", size=11.5)

    out = DOCS / "figure_p02_self_sourcing.svg"
    s.save(out)
    return out


# ---------------------------------------------------------------------------
# Paper 2, Figure 3 -- the boundary of the instrument
# ---------------------------------------------------------------------------

def fig_p02_cognition_window():
    default = load("docs/audit_trace_probe.json")
    tie = load("docs/audit_trace_probe_tie.json")

    sweep_def = default["A3_ancestry_honesty"]["diagnostics"]["window_sweep"]
    sweep_tie = tie["A3_ancestry_honesty"]["diagnostics"]["window_sweep"]
    need(len(sweep_def) == 8, "window sweep entries")

    win = default["A7_event_level_attribution"]["cognition_window"]
    need(win["window_sleep_events"] == 4000, "window size")
    need(win["window_span_cycles"] == 1.7, "window span")
    cycles = default["protocol"]["cycles"]

    W, H = 1080, 520
    s = Svg(W, H, "Lineage reachability against the window, and the window against the run")
    header(s,
           "The boundary of the instrument is measurable, and it is narrow",
           "Left: share of structures whose ancestry resolved, against the window the observer "
           "may read.",
           "Source: docs/audit_trace_probe.json, docs/audit_trace_probe_tie.json  |  "
           "drawn by benchmarks/figure_papers.py",
           W)

    # ---------------- panel A ----------------
    ax0, ax1 = 92, 470
    ay_top, ay_bot = 136, 368

    def ay(v):
        return ay_bot - v * (ay_bot - ay_top)

    s.text(36, 112, "A. Lineage reachability vs window size", size=13, weight="bold")
    for g in [0.0, 0.5, 1.0]:
        s.line(ax0, ay(g), ax1, ay(g), stroke=GRID, width=1)
        s.text(ax0 - 10, ay(g) + 4, f"{g:.1f}", size=10.5, fill=MUTED, anchor="end")

    labels = [str(w["window_candidates"]) for w in sweep_def]
    step = (ax1 - ax0) / len(labels)
    for i, (lbl, wd, wt) in enumerate(zip(labels, sweep_def, sweep_tie)):
        cx = ax0 + (i + 0.5) * step
        # the two arms coincide exactly where the window is large enough, so they
        # are offset horizontally rather than drawn on top of one another
        s.circle(cx - 5, ay(wd["lineage_reachability"]), 4.2, fill=BLUE, opacity=0.9)
        s.circle(cx + 5, ay(wt["lineage_reachability"]), 4.2, fill=AMBER, opacity=0.9)
        s.text(cx, ay_bot + 18, lbl, size=9.5, anchor="middle", fill=MUTED)
    s.text((ax0 + ax1) / 2, ay_bot + 38, "window candidates the observer may read",
           size=11, fill=MUTED, anchor="middle")
    s.circle(300, 124, 4.2, fill=BLUE, opacity=0.8)
    s.text(310, 128, "default arm", size=10.5)
    s.circle(390, 124, 4.2, fill=AMBER, opacity=0.8)
    s.text(400, 128, "forced-tie arm", size=10.5)
    s.text(36, 424,
           "Reachability is a function of the window, not of the substrate: the substrate "
           "holds every relation.", size=11.5)

    # ---------------- panel B ----------------
    bx0, bx1 = 566, 1042
    by = 226
    s.text(bx0 - 22, 122, "B. The window against the run (default arm)", size=13, weight="bold")
    span = cycles
    keep = win["window_span_cycles"]
    s.rect(bx0, by - 26, bx1 - bx0, 52, fill=GRID, opacity=0.7)
    wx = bx1 - (keep / span) * (bx1 - bx0)
    # the window is a small share of the run; give it a floor so it is visible
    # as a mark rather than being lost to rounding, without exaggerating it
    s.rect(min(wx, bx1 - 6), by - 26, max(6, bx1 - wx), 52, fill=RED, opacity=0.9)
    s.text(bx0, by - 38, "cycle 0", size=10.5, fill=MUTED)
    s.text(bx1, by - 38, f"cycle {span}", size=10.5, fill=MUTED, anchor="end")
    s.text(wx - 8, by + 48, "the cognition window", size=10.5, fill=RED, anchor="end")
    s.text(wx - 8, by + 64, f"last {keep} cycles", size=10.5, fill=RED, anchor="end")
    s.text(bx0, by + 88,
           "everything before it is unrecoverable, because the organism does not retain it "
           "either", size=10.5, fill=MUTED)
    s.text(bx0, by + 104,
           f"{win['window_sleep_events']:,} sleep events of "
           f"{win['sleep_events_total']:,} stored "
           f"({win['sleep_events_per_cycle']:,} per cycle)", size=10.5, fill=MUTED)

    out = DOCS / "figure_p02_cognition_window.svg"
    s.save(out)
    return out


FIGURES = [
    fig_p01_displacement_curve,
    fig_p01_adjacent_differences,
    fig_p01_phase_k_families,
    fig_p01_acquisition,
    fig_p01_capacity_sweep,
    fig_p02_reconstruction_arms,
    fig_p02_self_sourcing,
    fig_p02_cognition_window,
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", default="", help="substring filter on figure names")
    args = ap.parse_args()
    for fn in FIGURES:
        if args.only and args.only not in fn.__name__:
            continue
        path = fn()
        print(f"wrote {path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
