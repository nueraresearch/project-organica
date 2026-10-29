# Gate 13 — the causal account, after four probes

**Status: DIAGNOSTIC RECORD (2026-10-28).** This document reconciles four
measurements of the acquisition-gate failure, states the causal account they
support, and narrows the question a V2 build would have to answer.

It does **not** revise any verdict. The six negative task families, the Phase L
protocol verdict `H3-L — INCONCLUSIVE`, the Phase L characterisation, and the
campaign's stop at Gate 13 all stand exactly as recorded.

> ### What prompted this
>
> The parallel session's Gate 13 preflight concluded that **`MAX_PREDICTIONS = 20`
> is the causal bottleneck**, on the evidence that raising the cap to 1,000
> restored coverage to 98.2 %–100 %. That conclusion was sound on its own
> evidence, but it left **three probes written and uncommitted**, and those
> probes ask whether there is a *better* fix than a bigger budget. Running them
> changes the answer — and in one direction it **contradicts** the hypothesis
> the parallel session's own uncommitted probe suggested.

**Every seed used here is diagnostic.** Amendment 3 designated `20261100`–
`20261105` as diagnostic preflight seeds; they remain diagnostic. The
confirmatory sample (`20261106`–`20261130`, 25 seeds) has not been touched.

---

## 1. Three different things are called "Gate 13", and they disagree

| What it measures | Selection rule | Coverage of the world's 112 edges | Verdict |
|---|---|---|---|
| the organism's **asserted structure** | the engine's **global** top-20 by count | **0.0000 – 0.0268** | **FAIL** (0–3 of 112) |
| the same, at raised caps | global top-K by count, K swept | 0.0000 → 1.0000 | dose-response |
| the **`precedes` table** | **top-20 *per source*** | **0.9688 – 1.0000** | **PASS** |

The third row is not a third protocol. It is a **different selection rule over
the same table** — and the whole FAIL/PASS difference is that rule. This is the
third naming collision in this project after the harness/runner pair (fixed in
`docs/ACQUISITION-ENDPOINT-AUDIT.md` §8.5); the rule that caught it is
`AGENTS.md` rule 25(c).

**The protocol's Gate 13 is the first row** — the organism's asserted
structure, under the engine's own selection.

## 2. Probe 1 — the 1-tag stimulus does not rescue it

`benchmarks/probe_1tag_gate13.py`, 6 seeds. Each event carries **one** tag
instead of two, which removes the within-cell co-occurrence pairs by
construction.

| | world edges | asserted coverage | precision | raw temporal coverage | gate 13 |
|---|---|---|---|---|---|
| 2-tag (protocol) | 112 | 0.0000 – 0.0268 | 0.35 – 0.37 | 1.0000 | 0 / 6 pass |
| **1-tag** | 128 | **0.1719 – 0.1953** (22–25 covered) | 0.3548 – 0.3731 | 0.9688 – 0.9844 | **0 / 6 pass** |

**Removing one tag per event roughly quintuples the coverage (0.00 → 0.17) and
still fails on every seed.** So the co-occurrence crowding is a real
contributor but not the whole story.

The probe's own output shows the rest of the story — the top of the
`precedes` table on the 1-tag stimulus:

```
1. type -> olive (33)          6. type -> indigo (25)
2. generation -> olive (30)    7. type -> ochre (25)
3. type -> crimson (28)        8. generation -> crimson (25)
4. type -> umber (26)          9. generation -> umber (25)
5. subject -> olive (26)      10. type -> birch (24)
```

The highest-count rows are **internal vocabulary words pointing at world
tags** — `type`, `generation`, `subject`. They are not relations of the world
at all.

## 3. Probe 2 — the capacity sweep: a dose-response, and no cheap budget

`benchmarks/run_capacity_sweep.py`, 5 seeds, caps 20 / 40 / 80 / uncapped.
The engine's own selection, only the cap changed.

| Cap | asserted coverage | intra-cell edges | **inter-cell edges** | total asserted |
|---|---|---|---|---|
| **20** (frozen) | 0.0000 – 0.0268 | 28 – 39 | **0 – 3** | 28 – 41 |
| 40 | 0.0089 – 0.0714 | 31 – 39 | 1 – 8 | 33 – 47 |
| 80 | 0.0893 – 0.1786 | 39 – 42 | 11 – 31 | 50 – 72 |
| **uncapped** | **0.9911 – 1.0000** | 52 – 53 | **188 – 192** | **240 – 244** |

Two things to read here.

**The dose-response is monotone and it is steep.** 0.00 → 0.04–0.07 → 0.09–0.18
→ 0.99–1.00. There is no cap between 20 and 80 that clears the 0.50 gate.

**At the frozen cap the law-bearing edges are not scarce — they are absent.**
Inter-cell asserted edges are **0–3** while intra-cell ones are **28–39**. The
engine has formed the world's *partition* (which tags belong together) and
essentially none of the world's *transitions*.

**"Raise the cap to 1,000" is really "remove the cap."** Full coverage needs
**240–244 asserted edges**, about **12× the engine's budget of 20**, and it
costs precision — see §5.

## 4. Probe 3 — the observation protocol: the world **is** in memory

`benchmarks/probe_observation_protocol.py`, 6 seeds × 2 stimulus shapes. It
reads the `precedes` table directly and applies top-20 **per source**.

| World | precedes rows | world-tag pairs | RAW coverage | RAW precision | FILTERED coverage | FILTERED precision |
|---|---|---|---|---|---|---|
| 1-tag | 419 – 518 | 232 – 237 (44.8 % – 56.6 %) | 0.9688 – 0.9922 | 0.2417 – 0.3031 | 0.9688 – 0.9922 | **0.5359 – 0.5427** |
| 2-tag | 366 – 405 | 232 – 240 (59.3 % – 65.6 %) | **1.0000** (all 6) | 0.3160 – 0.3497 | **1.0000** (all 6) | **0.5333** |

**The world's relations are in memory, essentially completely.** Raw temporal
coverage is 1.0000 in every 2-tag seed, and 0.97–0.99 in the 1-tag shape. This
is the same number the pilot recorded (`raw_temporal_coverage: 1.0`), now shown
to hold across every seed and both shapes.

**But the table is mostly not the world.** Only 44.8 %–65.6 % of its rows are
world-tag pairs, and the raw precision of a selection over it is 0.24–0.35.
Filtering to world-tag pairs raises precision to **0.5333** at **unchanged
coverage**.

> **The filter is an oracle.** It selects on `TAG_POOL` — the world's actual
> vocabulary — which the organism does not have. It is **not** a legitimate
> organism-side fix. Its value is that it *quantifies the headroom*: a perfect
> vocabulary filter alone would buy precision 0.35 → 0.53 at no coverage cost.

## 5. Probe 4 — the allocation rule: per-source is **not** the fix

`benchmarks/probe_allocation_rule.py` (new, 2026-10-28), 3 seeds, on the
protocol's generator. Both curves are computed on the same `precedes` table
from the same engine run, so the comparison is paired. `edges retained` is
shown beside `coverage` so that a fix which merely spends more budget is
visible as such.

| Seed | rule | K | edges retained | coverage | precision |
|---|---|---|---|---|---|
| 20261101 | global | 20 | 20 | 0.0000 | 0.0000 |
| 20261101 | global | 80 | 80 | 0.1429 | 0.2000 |
| 20261101 | global | 160 | 160 | 0.4911 | 0.3438 |
| 20261101 | global | 320 | 320 | **0.9643** | 0.3375 |
| 20261101 | per-source | 5 | 143 | 0.2946 | 0.2308 |
| 20261101 | **per-source** | **10** | **258** | **0.7232** | 0.3140 |
| 20261102 | global | 320 | 320 | **0.9464** | 0.3312 |
| 20261102 | per-source | 10 | 262 | 0.7321 | 0.3130 |
| 20261103 | global | 320 | 320 | **0.9732** | 0.3406 |
| 20261103 | per-source | 10 | 286 | 0.7679 | 0.3007 |

**This overturns the hypothesis the observation-protocol probe suggested.** A
per-source allocation does *not* rescue the benchmark at a modest budget: it
needs **258–286 retained edges** to pass, and it reaches only **0.72–0.77**
where the global rule reaches **0.95–0.97** at 320. At every budget and under
both rules, **precision never exceeds 0.3443**.

## 6. The causal account

1. **The world's relations are in memory.** The `precedes` table holds all
   112 world edges (raw temporal coverage 0.97–1.00 across every seed and
   both stimulus shapes). Nothing is missing from the substrate.
2. **The world's relations are a minority of the table, and they are not the
   high-count rows.** The table has 366–518 rows for a 16-tag world; only
   232–240 are world-tag pairs, and the world edges are roughly **a third** of
   what any selection must retain (precision ≤ 0.3443 at every budget and
   under both rules). The highest-count rows are internal-vocabulary edges
   (`type → olive`, `generation → olive`) and intra-cell pairs.
3. **Layer 1 selects on frequency, and the world is not organised by
   frequency.** `_build_predictions` sorts by raw temporal count and truncates
   at 20. At that cut, **0–3 of 112** world edges survive, while 28–39
   intra-cell edges do.
4. **Neither a modest budget nor a modest re-allocation rescues it.** Coverage
   is a steep monotone dose-response in the global cap that needs ~240 edges,
   and a per-source rule at the same nominal budget is not better.
5. **So the binding constraint is PRECISION, not capacity.** In a candidate
   space where the world's edges are about a third of the rows and are not
   clustered at the top of any frequency ordering, **no frequency-based
   selection can pick them out.** The engine's Layer 1 selects on frequency;
   the world does not co-occur in frequency order.

**The specific pollution is internal vocabulary.** The engine's `precedes` table
has **27–34 distinct sources for a 16-tag world**, because the event text
carries non-tag words (`type`, `generation`, `subject`, `evidence`) that the
engine treats as vocabulary items. That is the same failure as the taxonomy
constraint: the engine has no way to represent "a tight group of my own tags",
and no way to tell its own coined vocabulary from incidental words.

## 7. What this changes for V2

`docs/V2-CAPACITY-DESIGN-BRIEF.md` frames the V2 question as **bounded
structural allocation** — how to preserve more useful structure under a
declared budget. **The measurements say that frame is wrong.** There is no
budget to preserve more within: the problem is not that the good structure does
not fit, it is that **a frequency-ranked cut cannot tell the good structure from
the noise at any budget under ~240 edges.**

The V2 question therefore sharpens to something the taxonomy constraint was
already pointing at:

> **Can the organism identify which of its vocabulary items are its own, and can
> it rank candidates by something other than raw frequency?**

The measurements bound the two halves of that question:

- **Vocabulary.** A perfect vocabulary filter buys precision **0.35 → 0.53** at
  **unchanged coverage** (1.0000). Everything beyond that must come from a
  better ranking. A legitimate version of the filter — the organism's own
  coined vocabulary rather than the world's tag list — is the open design
  question; the oracle version is not available to it.
- **Ranking.** The world edges are spread through the table, not clustered at
  its top. A ranking that is not frequency-based is required, and the engine
  currently has no candidate criterion to offer.

This is a **narrowing**, not a design. No V2 build is authorised by this
document.

> **Extended 2026-10-29 — the separation is real and it is not sufficient.**
> A further probe (`docs/GATE13-RELATION-SEPARATION.md`) rebuilt the relation
> table offline and applied a **provenance** separation — world events only in
> the lookback window — using `event_type`, which the engine already records,
> so it is **not an oracle**. It removes **35.7 %–40.7 %** of the table, and
> **100 %** of the removed rows have a sleep-sourced `tag_from`, which
> confirms the D2 mechanism exactly. **And with every contaminated row
> removed, coverage at the frozen budget of 20 is still 0.0000–0.0446**, and
> the top 20 is still 75–100 % intra-cell. So the V2 requirement list is now
> **three** items — provenance separation, relation-family separation, and a
> ranking that is not raw frequency — and the third is the one with no
> precedent in the engine.

## 8. What this does not establish

- **It does not establish that V1 could pass Gate 13 under some other rule.**
  It establishes that the information is present and that *frequency-based
  selection cannot extract it*.
- **It does not establish a V2 design**, and it does not authorise one.
- **It does not change any verdict.** The six negative task families, `H3-L —
  INCONCLUSIVE`, the Phase L characterisation, and the campaign's stop at Gate
  13 stand.
- **It does not change the confirmatory sample.** Every seed used here
  (`20261100`–`20261105`) is diagnostic and remains diagnostic. The usable
  confirmatory sample is **25** seeds (`20261106`–`20261130`), untouched.
- **It does not rehabilitate the observational filter as a fix.** That filter
  is an oracle (§4).
- **It revises one conclusion in the parallel session's write-up.** The
  statement "`MAX_PREDICTIONS = 20` is the causal bottleneck" is *accurate as
  stated* — raising the cap does restore coverage — but it is **not the
  deepest cause**. The deeper cause is the precision of the candidate space
  (§6). "Bottleneck" and "deepest cause" are different claims, and only the
  first survives.

### One measurement caveat

The observation-protocol probe generates its **own** event stream; the
allocation probe uses the **protocol's** generator. Their `precedes` row counts
agree on two of three shared seeds (379 and 405) and differ by two rows on the
third, so the two sets of numbers are close but **not strictly paired**. The
finding in §5 rests on the allocation probe alone, which is paired within
itself.

## 9. Reproducing

```bash
# the capacity sweep (5 seeds x 4 caps; ~13 min)
python benchmarks/run_capacity_sweep.py

# the allocation-rule probe (3 seeds; ~4 min)
python benchmarks/probe_allocation_rule.py

# the 1-tag Gate 13 probe (6 seeds; ~14 min)
python benchmarks/probe_1tag_gate13.py

# the observation-protocol probe (6 seeds x 2 shapes; ~30 min)
python benchmarks/probe_observation_protocol.py
```

**Artifacts:**

- `docs/gate13_capacity_sweep.json` — §3
- `docs/gate13_allocation_rule.json` — §5
- `docs/gate13_counterfactual_audit.json` — the earlier candidate-type
  decomposition
- `docs/acquisition_single_seed_pilot.json` — Pilot 0
- `docs/GATE13-PREFLIGHT-AUDIT.md`, `docs/GATE13-PAIRED-CAPACITY-TEST.md` —
  the earlier two write-ups
