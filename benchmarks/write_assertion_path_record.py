"""Record the verified admission replay in the capacity record, the manual and the changelog.

All numbers from `docs/gate13_assertion_path.json`; idempotent; asserts no placeholder survives.
"""
from __future__ import annotations

import json
from pathlib import Path

ART = json.loads(Path("docs/gate13_assertion_path.json").read_text())
S = ART["summary"]
A, F, M = S["all"], S["fail"], S["match"]
n_win_lo, n_win_hi = A["windows"]
rep = round((A["R"]["hits"] / A["R"]["distinct_min"] * 0 + A["R"]["hits"] / ((A["R"]["distinct_min"] + A["R"]["distinct_max"]) / 2))
            / (A["C"]["hits"] / ((A["C"]["distinct_min"] + A["C"]["distinct_max"]) / 2)), 1)
mult = round(A["R"]["hits"] / A["C"]["hits"], 1)
more = "more" if F["R"]["window_hits_total"] >= M["R"]["window_hits_total"] else "less"
cov_word = "fewer" if F["R"]["covered"] <= M["R"]["covered"] else "more"
n_cells = len(ART["cells"])

SECTION = f"""### 8.12 How the failing seeds spent the cap: a verified replay (2026-11-06)

Exploratory follow-up to §8.11. The block-2 artifact stores aggregates only, and the `top_k` density recorded there is
measured on the *final* pool — after the treatment has acted. `benchmarks/diagnose_assertion_path.py` therefore replays
the cap-20 cells for the five non-improving seeds and five improving seeds matched on recorded top-20 uplift, records
every per-cycle admission window, and accepts a replay only if its asserted set, covered count and SHA-1 digest equal
the stored cell's. **All {n_cells} replays matched** (`replay_mismatches` is empty), so the traces are the cells that
were scored. Artifact `docs/gate13_assertion_path.json`.

**The window is 20 rows and the arms spend it in opposite ways.** Over {n_win_lo}-{n_win_hi} cycles with admissions, the
count arm makes {A['C']['hits']} world-edge admissions spread across {A['C']['distinct_min']}-{A['C']['distinct_max']}
distinct edges; the ratio arm makes {A['R']['hits']} admissions concentrated into {A['R']['distinct_min']}-{A['R']['distinct_max']}
distinct edges. Per cycle the ratio window is about {mult}× as often a world edge, but it reaches roughly a third as many
distinct edges — the treatment trades exploration for repetition, about {rep}× per edge. That concentration is the
admission-side content of the ratio rule.

**The failing seeds did not spend the cap worse.** Non-improving against matched improving: ratio-window admissions
{F['R']['window_hits_total']} against {M['R']['window_hits_total']}, distinct window edges {F['R']['window_edges_distinct']}
against {M['R']['window_edges_distinct']}, asserted rows {F['R']['asserted']} against {M['R']['asserted']}. The failing
seeds' windows assert world edges slightly {more} often and end with {cov_word} distinct covered edges
({F['R']['covered']} against {M['R']['covered']}). On this trace there is no admission-side difference between the two
groups: whatever separates them is not how the cap is spent.

**And the window does not account for the coverage.** In all {A['R']['covered_gt_window']} of {n_cells // 2} ratio cells
the final covered count exceeds the number of distinct world edges its windows ever touched ({A['R']['covered']} covered
against {A['R']['distinct_min']}-{A['R']['distinct_max']} window-touched), with {A['R']['outside']} covered edges per
seed appearing in no window at all; for the count arm that happens in {A['C']['covered_gt_window']} of {n_cells // 2}
cells ({A['C']['covered']} covered, {A['C']['outside']} outside any window). `structure_edges` aggregates all six
structure types from the stored candidate snapshots and the prediction window touches only some of them, so a
window-level trace cannot attribute the ratio arm's coverage. That is a resolution boundary, not a mechanism: an
event-level claim would need a store-time observer at the structure level, which this harness does not have
(AGENTS rule 17(d)).

**What this changes.** §8.11 left the question at "the conversion from a denser top-20 to coverage is not determined by
the pool". This replay narrows it again: the conversion is not determined by the admission window either — the failing
and improving seeds admit at the same rate, the same window size, with the failing ones repeating world edges slightly
more and still ending with fewer distinct covered edges. The variation therefore sits downstream of admission, in how
repeated assertions of the same structures are consolidated into the other structure types, and that is what the next
instrument needs to observe. It is not a reason to change the cap, and it changes no verdict.
"""

MANUAL_PARA = f"""**The failing seeds did not spend their cap worse — a verified replay (exploratory).** Replaying the cap-20 cells
for the five non-improving seeds and five uplift-matched improving seeds, with every replay checked against the stored
digest ({n_cells}/{n_cells} matched): the ratio arm's window re-admits world edges at about {mult}× the count arm's rate but
concentrates them into {A['R']['distinct_min']}-{A['R']['distinct_max']} distinct edges against
{A['C']['distinct_min']}-{A['C']['distinct_max']}, so it trades reach for repetition rather than finding more.
Failing and improving seeds are indistinguishable on admissions ({F['R']['window_hits_total']} vs
{M['R']['window_hits_total']}), distinct window edges ({F['R']['window_edges_distinct']} vs
{M['R']['window_edges_distinct']}) and asserted rows; the failing seeds repeat world edges slightly {more} and end with
{cov_word} distinct covered edges ({F['R']['covered']} vs {M['R']['covered']}). Coverage also exceeds what any window
touched in {A['R']['covered_gt_window']} of {n_cells // 2} ratio cells, so the window does not account for it — the
remaining difference is downstream of admission. Diagnostic only; no criterion, no verdict moved.
`docs/gate13_assertion_path.json`; §8.12 capacity record.
"""

ROW = f"""| 2026-11-06 | **A verified replay finds no admission-side difference in the 20/5 split.** The cap-20 cells for the five non-improving seeds and five uplift-matched improving seeds were replayed with every per-cycle admission window recorded, and all {n_cells} replays reproduce the stored asserted set, covered count and digest. The ratio window admits world edges about {mult}× as often as the count window but into {A['R']['distinct_min']}-{A['R']['distinct_max']} distinct edges against {A['C']['distinct_min']}-{A['C']['distinct_max']} — repetition instead of reach. Failing and improving seeds do not differ on admissions ({F['R']['window_hits_total']} vs {M['R']['window_hits_total']}), distinct window edges ({F['R']['window_edges_distinct']} vs {M['R']['window_edges_distinct']}) or asserted rows, and the failing ones repeat slightly {more} while ending with {cov_word} covered edges ({F['R']['covered']} vs {M['R']['covered']}). Coverage exceeds window reach in {A['R']['covered_gt_window']} of {n_cells // 2} ratio cells, so the trace cannot attribute it; the difference is downstream of admission. Diagnostic, no verdict moved. `benchmarks/diagnose_assertion_path.py`, `docs/gate13_assertion_path.json`; §8.12 capacity record. |
"""

CHANGELOG = f"""### Analysed — a verified replay finds no admission-side difference in the 20/5 split (2026-11-06)

- The cap-20 cells for the five non-improving seeds and five uplift-matched improving seeds were replayed with every
  per-cycle admission window recorded; **all {n_cells} replays reproduce** the stored asserted set, covered count and
  digest, so the traces are the cells that were scored.
- The ratio window is about {mult}× as often a world edge per cycle as the count window, but it reaches
  {A['R']['distinct_min']}-{A['R']['distinct_max']} distinct edges against {A['C']['distinct_min']}-{A['C']['distinct_max']}: it
  trades exploration for repetition (about {rep}× per edge) instead of finding more.
- Failing and improving seeds do not differ on admissions ({F['R']['window_hits_total']} vs
  {M['R']['window_hits_total']}), distinct window edges ({F['R']['window_edges_distinct']} vs
  {M['R']['window_edges_distinct']}) or asserted rows ({F['R']['asserted']} vs {M['R']['asserted']}); the failing seeds
  repeat world edges slightly {more} and end with {cov_word} covered edges ({F['R']['covered']} vs {M['R']['covered']}).
  The cap is not where the 20/5 difference lives.
- Coverage exceeds window reach in {A['R']['covered_gt_window']} of {n_cells // 2} ratio cells
  ({A['R']['covered']} covered, {A['R']['outside']} outside any window) against {A['C']['covered_gt_window']} of
  {n_cells // 2} for the count arm ({A['C']['covered']}, {A['C']['outside']}), because `structure_edges` aggregates all six
  structure types and the window touches only some — a resolution boundary, recorded rather than bridged.
- Exploratory: no pre-registered criterion, no verdict re-scored. The remaining question moves downstream of admission,
  to how repeated assertions are consolidated. `benchmarks/diagnose_assertion_path.py`,
  `benchmarks/analyze_assertion_path.py`, `docs/gate13_assertion_path.json`.

"""

for block in (SECTION, MANUAL_PARA, ROW, CHANGELOG):
    assert "{" not in block and "}" not in block, "placeholder survived"

cap = Path("docs/GATE13-PAIRED-CAPACITY-TEST.md")
text = cap.read_text()
if "### 8.12 How the failing seeds spent the cap" not in text:
    cap.write_text(text.rstrip() + "\n\n" + SECTION)

man = Path("docs/USER-MANUAL.md")
text = man.read_text()
if "The failing seeds did not spend their cap worse" not in text:
    lines = text.split("\n")
    start = next(k for k, ln in enumerate(lines)
                 if "The 20/5 split after block 2 is not explained" in ln and not ln.startswith("|"))
    end = next((k for k in range(start + 1, len(lines)) if lines[k] == ""), len(lines))
    lines[end:end] = MANUAL_PARA.rstrip("\n").split("\n") + [""]
    text = "\n".join(lines)
if "verified replay finds no admission-side difference" not in text:
    text = text.rstrip() + "\n" + ROW
man.write_text(text)

chg = Path("CHANGELOG.md")
text = chg.read_text()
if "### Analysed — a verified replay finds no admission-side difference" not in text:
    chg.write_text(text.replace("## [0.12.0] — (unreleased)",
                                CHANGELOG + "## [0.12.0] — (unreleased)", 1))
print("written")
