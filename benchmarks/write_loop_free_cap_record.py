"""Write block 8's records: §13 readings, capacity §8.19, manual paragraph and row, changelog section.

Idempotent: every section is keyed on a sentinel and replaced if present, so running the writer twice changes nothing.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ART = json.loads((REPO / "docs" / "gate13_loop_free_cap.json").read_text())
CAL = json.loads((REPO / "docs" / "gate13_loop_free_cap_calibration.json").read_text())
A = ART["allocation"]
G = ART["gates"]
C = ART["criteria"]
D = ART["descriptive"]
CAPS = ART["caps"]
V = ART["verdict"]
TODAY = "2026-11-06"


def f(x, n=4):
    return f"{x:.{n}f}"


g0 = " and ".join(f"{G['G0_by_cap'][str(c)]}/100" for c in CAPS)
g1 = " and ".join(f"{G['G1_by_cap'][str(c)]}/100" for c in CAPS)
m2 = C["M2"]
m2_text = ", ".join(f"cap {c}: {f(m2[str(c)]['mean'])} (interval {f(m2[str(c)]['ci95'][0])} to "
                    f"{f(m2[str(c)]['ci95'][1])})" for c in CAPS)

if V == "SCALING SUPPORTED":
    INTERP = ("The gain grows with the budget and is positive at both caps: the mechanism the arm claims -- spending "
              "admission slots on edges loops do not already assert -- is the one that produces the effect, because "
              "the effect grows when the pool of redundant edges does.")
elif V == "SCALE-DEPENDENT":
    INTERP = ("The gain exists at one budget and not the other, so this arm is a cap-specific intervention rather than a "
              "scaling one; the direction of the dependence is in the table above.")
elif V == "GAIN WITHOUT SCALING":
    INTERP = ("The arm helps at both budgets by a similar amount, so the benefit is a fixed improvement in how the "
              "budget is spent, not one that compounds as the budget grows.")
elif V == "NO GAIN AT THESE CAPS":
    INTERP = ("At caps 40 and 100 the arm does not beat R, so block 7's cap-20 gain does not extend to larger budgets; "
              "that is a statement about this arm at these caps, not about the cap-20 result, which stands on its own "
              "block.")
else:
    INTERP = ("The block is void on its gates, so its cell-level numbers are descriptive only and no verdict about "
              "scaling can be read from it.")

readings = f"""## 13. Readings ({TODAY}, one scoring pass)

{ART['cells']} cells, seeds {A['lo']}-{A['hi']}, R and Y at caps {', '.join(str(c) for c in CAPS)}, no cell missing and none
substituted. Every bar, gate and the allocation were read from `docs/gate13_loop_free_cap_calibration.json`; nothing was
adjusted after the run. Scored once by `benchmarks/score_loop_free_cap.py` into `docs/gate13_loop_free_cap.json`.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness, both caps | {g0} seeds with different asserted sets (bar {G['G0_bar']}) | {'yes' if G['G0_pass'] else 'no'} |
| G1 perturbation, both caps | {g1} seeds with an edge displaced (bar {G['G1_bar']}) | {'yes' if G['G1_pass'] else 'no'} |
| G2 axis live | R coverage {f(D['r_coverage'][str(CAPS[0])])} at cap {CAPS[0]} to {f(D['r_coverage'][str(CAPS[1])])} at cap {CAPS[1]}; lift {f(G['G2_r_lift_mean'])} (interval {f(G['G2_r_lift_ci'][0])} to {f(G['G2_r_lift_ci'][1])}) | {'yes' if G['G2_pass'] else 'no'} |

**Verdict: {V}.** {'All three gates pass. ' if G['all_pass'] else ''}**M1** {'passes' if C['M1']['pass'] else 'fails'}: mean
difference-in-differences {f(C['M1']['did_mean'])} (95% interval {f(C['M1']['did_ci'][0])} to {f(C['M1']['did_ci'][1])})
against the {f(C['M1']['bar'])} bar, median {f(C['M1']['did_median'])} and {C['M1']['positive_n']}/{C['M1']['n']} seeds
positive. **M2** {'passes' if C['M2_pass'] else 'fails'}: {m2_text}.

The two gains, which are what the DiD is built from: cap {CAPS[0]} mean Y − R {f(m2[str(CAPS[0])]['mean'])}, cap {CAPS[1]}
{f(m2[str(CAPS[1])]['mean'])}. Calibration had predicted {f(CAL['effect']['d40_mean'])} and {f(CAL['effect']['d100_mean'])}
respectively. Novel covered edges moved {D['novel_diff'][str(CAPS[0])]:+.2f} at cap {CAPS[0]} and
{D['novel_diff'][str(CAPS[1])]:+.2f} at cap {CAPS[1]}, loop-covered edges {D['loop_diff'][str(CAPS[0])]:+.3f} and
{D['loop_diff'][str(CAPS[1])]:+.3f}. Mean displacement {f(D['mean_disp'][str(CAPS[0])], 2)} and
{f(D['mean_disp'][str(CAPS[1])], 2)} cells.

{INTERP}

**Disclosed defect.** The launcher for this run omitted the arm selector, so arm C also executed alongside R and Y. C is outside this block's frozen design, which runs R and Y only; its cells are excluded from scoring, moved to `.scratch/loop_free_cap_unregistered_C.jsonl`, and reported as unregistered rather than judged. The scored grid is exactly the 400 registered cells and no C number enters any criterion.

This licenses a statement about the admission rule at these two budgets on this world family and readout; it is not a
statement about what loops are for, because the arm leaves the loops, their construction and their thresholds untouched.
"""


def replace_section(text: str, sentinel: str, body: str, next_heading: str = "\n## ") -> str:
    """Replace a section beginning at `sentinel` up to the next heading (or append if absent)."""
    i = text.find(sentinel)
    if i >= 0:
        j = text.find(next_heading, i + len(sentinel))
        return text[:i] + body + ("\n" + text[j:].lstrip("\n") if j >= 0 else "")
    return text.rstrip("\n") + "\n\n" + body


# ---- pre-registration: append §13 and flip the status line
pre = (REPO / "docs" / "GATE13-LOOP-FREE-CAP-SCALING-PREREGISTRATION.md").read_text()
pre = re.sub(r"\*\*Status: FROZEN, NOT RUN\.\*\*", f"**Status: RUN ({TODAY}). Verdict: {V}.**", pre)
pre = replace_section(pre, "## 13. Readings", readings)
(REPO / "docs" / "GATE13-LOOP-FREE-CAP-SCALING-PREREGISTRATION.md").write_text(pre)

# ---- capacity record: §8.19 after §8.18
cap = (REPO / "docs" / "GATE13-PAIRED-CAPACITY-TEST.md").read_text()
section = f"""## 8.19 Block 8 — cap scaling (2026-11-06)

Block 7 measured the loop-free admission arm's gain at cap 20. Block 8 asks whether that gain scales with the budget:
arms R and Y at caps **{CAPS[0]}** and **{CAPS[1]}**, {A['seeds']} fresh seeds ({A['lo']}-{A['hi']}), {ART['cells']} cells.
DiD(seed) = (Y − R at cap {CAPS[1]}) − (Y − R at cap {CAPS[0]}), paired within seed.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness, both caps | {g0} (bar {G['G0_bar']}) | {'yes' if G['G0_pass'] else 'no'} |
| G1 perturbation, both caps | {g1} (bar {G['G1_bar']}) | {'yes' if G['G1_pass'] else 'no'} |
| G2 axis live | R lift {f(G['G2_r_lift_mean'])} ({f(G['G2_r_lift_ci'][0])}, {f(G['G2_r_lift_ci'][1])}) | {'yes' if G['G2_pass'] else 'no'} |

Gain at cap {CAPS[0]}: {f(m2[str(CAPS[0])]['mean'])}; at cap {CAPS[1]}: {f(m2[str(CAPS[1])]['mean'])}. M1 (mean DiD ≥
{C['M1']['bar']}) {'passes' if C['M1']['pass'] else 'fails'} at {f(C['M1']['did_mean'])} ({f(C['M1']['did_ci'][0])},
{f(C['M1']['did_ci'][1])}); M2 (positive at both) {'passes' if C['M2_pass'] else 'fails'}.

**Verdict: {V}.** {INTERP}

The launcher also ran arm C, which this design excludes; those cells are unregistered, unjudged and kept in `.scratch/loop_free_cap_unregistered_C.jsonl`.

Artifacts: `docs/GATE13-LOOP-FREE-CAP-SCALING-PREREGISTRATION.md`, `docs/gate13_loop_free_cap.json`,
`docs/gate13_loop_free_cap_calibration.json`, `benchmarks/score_loop_free_cap.py`.
"""
cap = replace_section(cap, "## 8.19 Block 8", section)
(REPO / "docs" / "GATE13-PAIRED-CAPACITY-TEST.md").write_text(cap)

# ---- manual: paragraph after block 7's paragraph, row after block-7's row
man = (REPO / "docs" / "USER-MANUAL.md").read_text()
para = f"""**Block 8 asked whether that gain scales with the budget.** Same arm, arms R and Y, caps **{CAPS[0]}** and
**{CAPS[1]}**, {A['seeds']} fresh seeds ({A['lo']}-{A['hi']}), {ART['cells']} cells, with a gate that the cap axis is
live at all (R must improve from cap {CAPS[0]} to {CAPS[1]}). The scaling quantity is the per-seed
difference-in-differences: the gain at {CAPS[1]} minus the gain at {CAPS[0]}. **Verdict: {V}.** Gain {f(m2[str(CAPS[0])]['mean'])}
at cap {CAPS[0]} and {f(m2[str(CAPS[1])]['mean'])} at cap {CAPS[1]}; mean DiD {f(C['M1']['did_mean'])}
({f(C['M1']['did_ci'][0])}, {f(C['M1']['did_ci'][1])}) against the {f(C['M1']['bar'])} bar, M1 {'pass' if C['M1']['pass'] else 'fail'},
M2 {'pass' if C['M2_pass'] else 'fail'}. The launcher also ran arm C, which the design excludes; those cells are unregistered and unjudged. `benchmarks/score_loop_free_cap.py`, `docs/gate13_loop_free_cap.json`; §8.19
capacity record, §13 of the pre-registration."""
i = man.find("**Block 7 reran the same intervention arm")
assert i >= 0, "block-7 manual paragraph not found"
j = man.find("\n\n", i)
assert j >= 0
if "**Block 8 asked whether that gain scales" in man:
    k = man.find("**Block 8 asked whether that gain scales")
    m = man.find("\n\n", k)
    man = man[:k] + para + man[m:]
else:
    man = man[:j] + "\n\n" + para + man[j:]

row = (f"| {TODAY} | **Block 8 (cap scaling)** | Loop-free admission arm at caps {CAPS[0]} and {CAPS[1]} on "
       f"{A['seeds']} fresh seeds: {V.lower() if V != 'VOID / NOT COMPARABLE' else 'void'}, gain "
       f"{f(m2[str(CAPS[0])]['mean'])} at cap {CAPS[0]} and {f(m2[str(CAPS[1])]['mean'])} at cap {CAPS[1]}, DiD "
       f"{f(C['M1']['did_mean'])} against the {f(C['M1']['bar'])} bar. |")
row7 = "| 2026-11-06 | **Block 7 ("
i = man.find(row7)
assert i >= 0, "block-7 manual row not found"
if "| 2026-11-06 | **Block 8 (cap scaling)** |" in man:
    k = man.find("| 2026-11-06 | **Block 8 (cap scaling)** |")
    m = man.find("\n", k)
    man = man[:k] + row + man[m:]
else:
    e = man.find("\n", i)
    man = man[:e + 1] + row + "\n" + man[e + 1:]
(REPO / "docs" / "USER-MANUAL.md").write_text(man)

# ---- changelog before the unreleased heading
ch = (REPO / "CHANGELOG.md").read_text()
entry = f"""### Gate 13 block 8 run ({TODAY}) — does the gain scale with the cap?

- **Arms R and Y at caps {CAPS[0]} and {CAPS[1]}**, {A['seeds']} fresh seeds ({A['lo']}-{A['hi']}), {ART['cells']} cells.
  The runner gained a `--caps` option; the cap-20 self-test and a replayed cap-20 cell were checked to be identical to
  block 7 before the run.
- **Gates:** G0 liveness {g0} (bar {G['G0_bar']}), G1 perturbation {g1} (bar {G['G1_bar']}), G2 axis live
  {f(G['G2_r_lift_mean'])} ({f(G['G2_r_lift_ci'][0])}, {f(G['G2_r_lift_ci'][1])}): {'all pass' if G['all_pass'] else 'FAILED'}.
- **Verdict {V}.** M1 mean DiD {f(C['M1']['did_mean'])} ({f(C['M1']['did_ci'][0])}, {f(C['M1']['did_ci'][1])}) against
  {f(C['M1']['bar'])}; M2 positive at both caps: {m2_text}.
- **Disclosed launcher defect:** the run also executed arm C, which the design excludes. Those cells are unregistered and unjudged, kept apart, and the scored grid is exactly the 400 registered R/Y cells.
- `benchmarks/score_loop_free_cap.py`, `docs/gate13_loop_free_cap.json`, §8.19 capacity record.

"""
if "### Gate 13 block 8 run" in ch:
    # idempotent: the entry is generated deterministically from the artifact, so presence means no-op
    if entry not in ch:
        k = ch.find("### Gate 13 block 8 run")
        m = ch.find("\n## ", k)
        ch = ch[:k] + entry + (ch[m + 1:] if m >= 0 else "")
else:
    k = ch.find("\n## [0.11.0]")
    assert k >= 0, "changelog has no 0.11.0 heading to anchor the unreleased section"
    ch = ch[:k + 1] + entry + ch[k + 1:]
(REPO / "CHANGELOG.md").write_text(ch)

print("records written:", V)
print("gates:", {k: G[k] for k in ("G0_pass", "G1_pass", "G2_pass", "all_pass")})
print("criteria:", {"M1": C["M1"]["pass"], "M2": C["M2_pass"]})
