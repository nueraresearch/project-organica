"""Write the exploratory 20/5-split diagnosis into the capacity record, the manual and the changelog.

Every number is read from `docs/gate13_ratio_seed_split.json`; nothing is typed. Idempotent: each insertion is skipped if
its marker is already present. Asserts that no placeholder survives in any block it writes.
"""
from __future__ import annotations

import json
from pathlib import Path

ART = json.loads(Path("docs/gate13_ratio_seed_split.json").read_text())
T = ART["group_table"]
S1, S2 = ART["spread"]["block1"], ART["spread"]["block2"]
C = ART["correlation_uplift_vs_delta"]
F = ART["failing_seeds"]

fail_uplift = ", ".join(f"{f['uplift']:.2f}" for f in F)
up_ge_02 = [f for f in F if f["uplift"] >= 0.20]
worst = min(F, key=lambda f: f["delta"])
hi = max(F, key=lambda f: f["uplift"])


def g(var, field):
    return T[var][field]


SECTION = f"""### 8.11 Why the benefit varies: an exploratory look at the 20/5 split (2026-11-06)

Diagnostic only. `benchmarks/diagnose_ratio_seed_split.py` pairs the cap-20 pool diagnostics already stored in both block
artifacts against the paired coverage delta, and asks whether block 2's 20 improving and 5 non-improving seeds differ on
any property of the candidate pool. Artifact `docs/gate13_ratio_seed_split.json`. **This is not a test and it re-scores
nothing:** the two groups are defined by the outcome they are compared on, the failure group has 5 members, and no
criterion here was pre-registered.

**The dispersion is real.** Block 1: {S1['positive']} positive, {S1['zero']} zero, {S1['negative']} negative, sd
{S1['sd']:.4f}, mean {S1['mean']:.4f}, median {S1['median']:.4f}. Block 2: {S2['positive']} positive, {S2['zero']}
zero, {S2['negative']} negative, sd {S2['sd']:.4f}, mean {S2['mean']:.4f}, median {S2['median']:.4f}, range
{S2['min']:.4f} to {S2['max']:.4f}. The median rose while the mean fell: the treatment still produces its typical gain
(the median is larger than block 1's) but produces it on fewer seeds, and now loses ground on some.

**Pool structure does not separate them.** On the count tie block ({g('count_tie_rows', 'improved_median'):.0f} rows
against {g('count_tie_rows', 'not_median'):.0f}, permutation p = {g('count_tie_rows', 'perm_p'):.4f}), on the number
of distinct ratio values ({g('R_distinct', 'improved_median'):.0f} against {g('R_distinct', 'not_median'):.0f}, p =
{g('R_distinct', 'perm_p'):.4f}), on the ratio-to-count distinct-value ratio ({(g('distinct_ratio', 'improved_median')):.2f}
against {(g('distinct_ratio', 'not_median')):.2f}, p = {g('distinct_ratio', 'perm_p'):.4f}) and on cap-20 control
precision ({(g('C_prec', 'improved_median')):.4f} against {(g('C_prec', 'not_median')):.4f}, p =
{g('C_prec', 'perm_p'):.4f}) the two groups are indistinguishable. The one variable that separates at conventional levels,
the size of the ratio arm's asserted set ({g('R_asserted', 'improved_median'):.0f} against
{g('R_asserted', 'not_median'):.0f}, p = {g('R_asserted', 'perm_p'):.4f}), is downstream of the outcome rather than a
property of the pool: the arm asserts more rows when its ordering finds more to assert. It cannot be read as a cause.

**The ranking improves; the improvement does not convert.** Top-20 world-edge density uplift does differ — medians
{(g('uplift', 'improved_median')):.2f} against {(g('uplift', 'not_median')):.2f}, mean difference
{(g('uplift', 'mean_diff')):.4f}, permutation p = {g('uplift', 'perm_p'):.4f} — and across both blocks it correlates with
the coverage delta: pooled r = {C['pooled']['pearson']:.3f} ({C['pooled']['pearson_ci95'][0]:.3f} to
{C['pooled']['pearson_ci95'][1]:.3f}, n = {C['pooled']['n']}, r² = {C['pooled']['r_squared']:.3f}), block 1 r =
{C['block1']['pearson']:.3f} ({C['block1']['pearson_ci95'][0]:.3f} to {C['block1']['pearson_ci95'][1]:.3f}) and block 2
r = {C['block2']['pearson']:.3f} ({C['block2']['pearson_ci95'][0]:.3f} to {C['block2']['pearson_ci95'][1]:.3f}). The
correlation is weak, it explains about {C['pooled']['r_squared'] * 100:.0f} percent of the variance, and block 2's
interval contains zero. And the failing seeds are not seeds where the ordering failed: their uplift is {fail_uplift} —
{len(up_ge_02)} of the five at or above 0.20, including {hi['seed']}, whose delta is {hi['delta']:+.4f} despite the group's
largest uplift. The largest loss, {worst['seed']} at {worst['delta']:+.4f}, had no uplift at all. Nor is the comparison
lost on a degraded control: the failure group's cap-20 precision (median {(g('C_prec', 'not_median')):.4f}) is not below
the improving group's ({(g('C_prec', 'improved_median')):.4f}).

**What this supports, and what it does not.** It does not support candidate-pool structure — tie-block size, distinct-value
count, ratio diversity — as the moderator of the treatment's benefit; on this evidence those are the wrong variables. What
it does support is narrower: the ratio ordering reliably finds a denser top-20, that density carries a small amount of
information about the eventual coverage gain, and the conversion from the one to the other is not determined by it. The
remaining candidates are dynamic — the order in which the cap is spent relative to which edges become assertable, and what
a seed's assertion path does with a denser top-20 — and none of them is measured here. Testing any of them needs a fresh
allocation, a pre-registered moderator and a bar fixed before the cells are run. The 20/5 split can generate that
hypothesis; it cannot adjudicate it.
"""

MANUAL_PARA = f"""**The 20/5 split after block 2 is not explained by candidate-pool structure (exploratory).** Pairing the stored
cap-20 pool diagnostics against the coverage delta: the five non-improving seeds are indistinguishable from the twenty that
improved on tie-block size ({g('count_tie_rows', 'improved_median'):.0f} vs {g('count_tie_rows', 'not_median'):.0f} rows,
p = {g('count_tie_rows', 'perm_p'):.4f}), distinct ratio values ({g('R_distinct', 'improved_median'):.0f} vs
{g('R_distinct', 'not_median'):.0f}, p = {g('R_distinct', 'perm_p'):.4f}) and cap-20 control precision
({(g('C_prec', 'improved_median')):.4f} vs {(g('C_prec', 'not_median')):.4f}, p = {g('C_prec', 'perm_p'):.4f}). The top-20
density uplift does differ (medians {(g('uplift', 'improved_median')):.2f} vs {(g('uplift', 'not_median')):.2f}, p =
{g('uplift', 'perm_p'):.4f}) and correlates weakly with the delta (pooled r = {C['pooled']['pearson']:.3f}, r² =
{C['pooled']['r_squared']:.3f}), but {len(up_ge_02)} of the five failures still received a denser top-20 and the largest
loss ({worst['seed']}, {worst['delta']:+.4f}) received no uplift at all. So the variability is not a property of the pool:
the ordering finds better rows and the benefit does not follow from it. Diagnostic only — no criterion, no verdict moved;
confirming a moderator needs a fresh allocation and a bar fixed before the run. §8.11 of the capacity record;
`docs/gate13_ratio_seed_split.json`.
"""

ROW = f"""| 2026-11-06 | **Exploratory: the 20/5 split in block 2 is not explained by candidate-pool structure.** Paired cap-20 diagnostics vs the coverage delta leave the five non-improving seeds indistinguishable from the twenty improving ones on tie-block rows ({g('count_tie_rows', 'improved_median'):.0f} vs {g('count_tie_rows', 'not_median'):.0f}, p = {g('count_tie_rows', 'perm_p'):.4f}), distinct ratio values ({g('R_distinct', 'improved_median'):.0f} vs {g('R_distinct', 'not_median'):.0f}, p = {g('R_distinct', 'perm_p'):.4f}) and control precision ({(g('C_prec', 'improved_median')):.4f} vs {(g('C_prec', 'not_median')):.4f}, p = {g('C_prec', 'perm_p'):.4f}); the top-20 uplift does separate (medians {(g('uplift', 'improved_median')):.2f} vs {(g('uplift', 'not_median')):.2f}, p = {g('uplift', 'perm_p'):.4f}) and correlates weakly with the delta (pooled r = {C['pooled']['pearson']:.3f}, r² = {C['pooled']['r_squared']:.3f}), but {len(up_ge_02)} of the five failures still got a denser top-20 and the largest loss had no uplift at all. Diagnostic, not a test; nothing re-scored. `benchmarks/diagnose_ratio_seed_split.py`, `docs/gate13_ratio_seed_split.json`; §8.11 capacity record. |
"""

CHANGELOG = f"""### Analysed — the 20/5 split is not a pool-structure effect (2026-11-06)

- Block 2's five non-improving seeds are indistinguishable from the twenty that improved on every pool property measured:
  tie-block rows ({g('count_tie_rows', 'improved_median'):.0f} vs {g('count_tie_rows', 'not_median'):.0f}, p =
  {g('count_tie_rows', 'perm_p'):.4f}), distinct ratio values ({g('R_distinct', 'improved_median'):.0f} vs
  {g('R_distinct', 'not_median'):.0f}, p = {g('R_distinct', 'perm_p'):.4f}), ratio-to-count distinct ratio
  ({(g('distinct_ratio', 'improved_median')):.2f} vs {(g('distinct_ratio', 'not_median')):.2f}, p =
  {g('distinct_ratio', 'perm_p'):.4f}) and control precision ({(g('C_prec', 'improved_median')):.4f} vs
  {(g('C_prec', 'not_median')):.4f}, p = {g('C_prec', 'perm_p'):.4f}).
- Top-20 density uplift does differ ({(g('uplift', 'improved_median')):.2f} vs {(g('uplift', 'not_median')):.2f}, p =
  {g('uplift', 'perm_p'):.4f}) and correlates weakly with the coverage delta (pooled r = {C['pooled']['pearson']:.3f},
  r² = {C['pooled']['r_squared']:.3f}; block 2 alone {C['block2']['pearson']:.3f}, interval spanning zero) — but
  {len(up_ge_02)} of the five failures still got a denser top-20, and the largest loss ({worst['seed']},
  {worst['delta']:+.4f}) got no uplift at all. A better ranking is necessary-looking and not sufficient.
- The only variable that separates at conventional levels, the ratio arm's asserted-set size (p =
  {g('R_asserted', 'perm_p'):.4f}), is downstream of the outcome rather than a property of the pool, so it explains nothing.
- Explicitly exploratory: groups defined by the outcome, n = 5 failures, no pre-registered criterion, no verdict re-scored.
  Confirming a moderator needs a fresh allocation and a bar fixed in advance.
  `benchmarks/diagnose_ratio_seed_split.py`, `docs/gate13_ratio_seed_split.json`.

"""

for block in (SECTION, MANUAL_PARA, ROW, CHANGELOG):
    assert "{" not in block and "}" not in block, "placeholder survived in a written block"

cap = Path("docs/GATE13-PAIRED-CAPACITY-TEST.md")
text = cap.read_text()
if "### 8.11 Why the benefit varies" not in text:
    cap.write_text(text.rstrip() + "\n\n" + SECTION)

man = Path("docs/USER-MANUAL.md")
text = man.read_text()
if "The 20/5 split after block 2 is not explained" not in text:
    lines = text.split("\n")
    start = next(k for k, ln in enumerate(lines)
                 if "Block 2 is the first comparable block" in ln and not ln.startswith("|"))
    end = next((k for k in range(start + 1, len(lines)) if lines[k] == ""), len(lines))
    lines[end:end] = MANUAL_PARA.rstrip("\n").split("\n") + [""]
    text = "\n".join(lines)
if "Exploratory: the 20/5 split in block 2" not in text:
    man.write_text(text.rstrip() + "\n" + ROW)
else:
    man.write_text(text)

chg = Path("CHANGELOG.md")
text = chg.read_text()
if "### Analysed — the 20/5 split is not a pool-structure effect" not in text:
    marker = "## [0.12.0] — (unreleased)"
    chg.write_text(text.replace(marker, CHANGELOG + marker, 1))

print("written")
