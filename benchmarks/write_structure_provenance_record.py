"""Record the store-time structure-type attribution in the capacity record, the manual and the changelog."""
from __future__ import annotations

import json
from pathlib import Path

ART = json.loads(Path("docs/gate13_structure_provenance.json").read_text())
assert not ART["verification_failures"], "attribution unverified"
C, S = ART["cells"], ART["summary"]
F, M = S["fail"], S["match"]
n = len(C)

seeds = sorted({k.split("_")[0] for k in C})
loop_pairs = [(C[f"{s}_C"]["covered_by_type"].get("loop_candidate", 0),
               C[f"{s}_R"]["covered_by_type"].get("loop_candidate", 0)) for s in seeds]
loop_diff = max(abs(a - b) for a, b in loop_pairs)
assert loop_diff == 0, f"loop coverage differs across arms by {loop_diff}; the invariance claim would be false"

loop_all = [C[k]["covered_by_type"].get("loop_candidate", 0) for k in C]
pred_all = [C[k]["covered_by_type"].get("prediction_candidate", 0) for k in C]
other_max = max(sum(v for t, v in C[k]["covered_by_type"].items()
                    if t not in ("loop_candidate", "prediction_candidate")) for k in C)


def cell(seed, arm, key, default=0):
    return C[f"{seed}_{arm}"]["covered_by_type"].get(key, default)


def multi(seed, arm):
    return C[f"{seed}_{arm}"]["covered_multi_type"]


def cov(seed, arm):
    return C[f"{seed}_{arm}"]["covered"]

SECTION = f"""### 8.13 What carries the coverage: loop candidates, and prediction candidates that add or duplicate (2026-11-06)

Exploratory follow-up to §8.12. `benchmarks/diagnose_structure_provenance.py` wraps `MemoryService.store` and captures
every `event_type="sleep"` payload as it is written — the same candidate rows `structure_edges` aggregates — then
reconstructs the live set the way `_load_prior_candidates` does (newest generation per key, death records dropped), and
attributes each covered world edge to the structure type(s) asserting it. Fidelity is enforced three ways, and a cell is
not read unless all three hold: the replay reproduces the stored asserted set, covered count and digest; the
reconstructed edge set equals `structure_edges` on the database's own candidate list; and every per-edge weight agrees.
**All {n} cells pass all three** (`verification_failures` is empty). Artifact `docs/gate13_structure_provenance.json`.

**Two of the eight branches carry the coverage.** `loop_candidate` accounts for {min(loop_all)}-{max(loop_all)} covered
world edges per seed and `prediction_candidate` for {min(pred_all)}-{max(pred_all)}; every other branch contributes at
most {other_max} edge in any cell. (`structure_edges` documents "six structure types"; the code has eight branches —
`concept_candidate` and `phrase_candidate` share one. This is a wording defect in the docstring, recorded here and not
changed in the frozen readout.)

**The loop component is arm-invariant.** Loop attribution is identical in both arms on all {len(seeds)} seeds — maximum
difference {loop_diff} edges. Loops are built from the stream and are not what the cap ranks, so this is the internal
consistency check one wants: the two arms differ only in which predictions are admitted.

**The treatment is entirely temporal, and the split is redundancy.** The ratio arm raises prediction attribution in both
groups — {F['C']['prediction_candidate']} to {F['R']['prediction_candidate']} in the failing seeds,
{M['C']['prediction_candidate']} to {M['R']['prediction_candidate']} in the matched improving ones. What differs is
whether those edges are already in the loop structure: covered edges asserted by both a loop and a prediction rise
{F['C']['multi_type']} to {F['R']['multi_type']} in the failing group and **fall** {M['C']['multi_type']} to
{M['R']['multi_type']} in the improving group, giving {F['C']['covered_total']} to {F['R']['covered_total']} against
{M['C']['covered_total']} to {M['R']['covered_total']}. The three clearest cases: 20270901 goes from
{cell('20270901','C','prediction_candidate')} prediction edges with {multi('20270901','C')} overlap to
{cell('20270901','R','prediction_candidate')} with {multi('20270901','R')}, and coverage is unchanged at
{cov('20270901','C')}; 20270921 goes from {cell('20270921','C','prediction_candidate')} to
{cell('20270921','R','prediction_candidate')} with overlap {multi('20270921','C')} to {multi('20270921','R')}, and loses
{cov('20270921','C')} to {cov('20270921','R')}; 20270906 goes from
{cell('20270906','C','prediction_candidate')} to {cell('20270906','R','prediction_candidate')} while overlap drops
{multi('20270906','C')} to {multi('20270906','R')}, and gains {cov('20270906','C')} to {cov('20270906','R')}.

**This closes §8.12's boundary.** The coverage that appeared outside any admission window is loop coverage, and loops are
not the object the cap ranks. The cap ranks prediction candidates; the readout counts both. So the honest statement of
the mechanism is: the ratio rule does not touch the loop structure at all, it changes which temporal edges are asserted,
and that change is worth something only where those edges are not already present in the loops.

**Limits.** This is the composition of the final asserted set at the readout's own resolution, not a time order: an edge
asserted by both a loop and a prediction is double-attributed in the final structure, and this measurement cannot say
which came first. The groups are the same 5-versus-5 split as §8.11-§8.12, defined by the outcome, with no pre-registered
criterion; nothing here re-scores a verdict.
"""

MANUAL_PARA = f"""**What carries the ratio arm's coverage: temporal edges, and whether loops already have them (exploratory).** A
store-time observer captured every sleep payload and attributed the covered world edges to structure type, verified in all
{n} cells against the stored digest, the reconstructed edge set and the per-edge weights. Loops carry
{min(loop_all)}-{max(loop_all)} of the {min(C[k]['covered'] for k in C)}-{max(C[k]['covered'] for k in C)} covered edges and
are identical in both arms on all {len(seeds)} seeds; the entire treatment effect is `prediction_candidate` edges
({F['C']['prediction_candidate']} to {F['R']['prediction_candidate']} in failing seeds, {M['C']['prediction_candidate']} to
{M['R']['prediction_candidate']} in improving ones). The split is whether those edges are already in the loop structure:
overlap rises {F['C']['multi_type']} to {F['R']['multi_type']} where the seeds fail and falls {M['C']['multi_type']} to
{M['R']['multi_type']} where they improve. So admission is a conditional bottleneck — worth something only when the
temporal edges it selects are not already implied by loops. Final-set composition, not time order; no verdict moved.
`docs/gate13_structure_provenance.json`; §8.13 capacity record.
"""

ROW = f"""| 2026-11-06 | **Store-time attribution: loops carry the coverage and are arm-invariant; the ratio effect is temporal and fails where the loops already cover it.** Every sleep payload captured as written and each covered edge attributed to its asserting type(s), verified in all {n} cells against stored digest, reconstructed edge set and per-edge weights. `loop_candidate` carries {min(loop_all)}-{max(loop_all)} covered edges and is identical across arms on all {len(seeds)} seeds (max difference {loop_diff}); `prediction_candidate` carries {min(pred_all)}-{max(pred_all)} and is the whole treatment effect, rising {F['C']['prediction_candidate']} to {F['R']['prediction_candidate']} in failing seeds and {M['C']['prediction_candidate']} to {M['R']['prediction_candidate']} in improving ones. Loop+prediction overlap rises {F['C']['multi_type']} to {F['R']['multi_type']} where seeds fail and falls {M['C']['multi_type']} to {M['R']['multi_type']} where they improve — the 20/5 split is redundancy, not reach. Resolves §8.12's window boundary; no verdict moved. `benchmarks/diagnose_structure_provenance.py`, `docs/gate13_structure_provenance.json`; §8.13 capacity record. |
"""

CHANGELOG = f"""### Analysed — loops carry the coverage, the ratio effect is temporal, and the 20/5 split is redundancy (2026-11-06)

- A store-time observer captured every `event_type="sleep"` payload as written and attributed each covered world edge to
  the structure type(s) asserting it; **all {n} cells verify** against the stored digest, against `structure_edges` on the
  database's own candidate list, and against every per-edge weight.
- `loop_candidate` carries {min(loop_all)}-{max(loop_all)} of the covered edges and is **identical across arms on all
  {len(seeds)} seeds** (max difference {loop_diff}) — loops are built from the stream and are not what the cap ranks.
- The whole treatment effect is `prediction_candidate`: {F['C']['prediction_candidate']} to
  {F['R']['prediction_candidate']} in failing seeds, {M['C']['prediction_candidate']} to
  {M['R']['prediction_candidate']} in improving ones. What separates them is redundancy: loop/prediction overlap rises
  {F['C']['multi_type']} to {F['R']['multi_type']} where seeds fail and falls {M['C']['multi_type']} to
  {M['R']['multi_type']} where they improve.
- This closes §8.12's boundary: coverage outside the admission window is loop coverage, and loops are not the object the
  window ranks. Admission is a conditional bottleneck — worth something when the temporal edges it selects are not
  already in the loops.
- Recorded wording defect, not a code change: `structure_edges` documents "six structure types" but has eight branches
  (`concept_candidate` and `phrase_candidate` share one).
- Exploratory, final-set composition rather than time order, no criterion and no verdict re-scored.
  `benchmarks/diagnose_structure_provenance.py`, `docs/gate13_structure_provenance.json`.

"""

for block in (SECTION, MANUAL_PARA, ROW, CHANGELOG):
    assert "{" not in block and "}" not in block, "placeholder survived"

cap = Path("docs/GATE13-PAIRED-CAPACITY-TEST.md")
text = cap.read_text()
if "### 8.13 What carries the coverage" not in text:
    cap.write_text(text.rstrip() + "\n\n" + SECTION)

man = Path("docs/USER-MANUAL.md")
text = man.read_text()
if "What carries the ratio arm's coverage" not in text:
    lines = text.split("\n")
    start = next(k for k, ln in enumerate(lines)
                 if "The failing seeds did not spend their cap worse" in ln and not ln.startswith("|"))
    end = next((k for k in range(start + 1, len(lines)) if lines[k] == ""), len(lines))
    lines[end:end] = MANUAL_PARA.rstrip("\n").split("\n") + [""]
    text = "\n".join(lines)
if "Store-time attribution: loops carry the coverage" not in text:
    text = text.rstrip() + "\n" + ROW
man.write_text(text)

chg = Path("CHANGELOG.md")
text = chg.read_text()
if "### Analysed — loops carry the coverage" not in text:
    chg.write_text(text.replace("## [0.12.0] — (unreleased)",
                                CHANGELOG + "## [0.12.0] — (unreleased)", 1))
print("written")
