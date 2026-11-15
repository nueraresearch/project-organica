# The two C8 repairs — cap change or tag-count change — and what each costs

**Date:** 2026-11-15

**Status:** `OPTIONS FOR OWNER DECISION — NOTHING IN FORCE; NO CELL, NO FREEZE, NO GRANT`

**Scope:** what the two structural repairs would buy and cost *now*. No threshold moves here, no manifest freezes, no cell runs. The numbers are read from committed artifacts plus one declared count on the existing competent pools; nothing new was measured.

## The question has changed, and the framing has to change with it

These two repairs were live while C8 was blocked. They are not any more: [`DECISION-A1-C8-NMIN-1`](DECISION-A1-C8-NMIN.md) sets the floor at **17** competent rows and makes C8 adjudicable on **all six seeds** at 20 / 17 / 20 / 20 / 18 / 20. So neither repair is required for adjudicability.

What is still open is narrower and worth stating exactly: **two seeds field fewer than the nominal twenty** (`20740102` at 17 because 18 is impossible, `20740105` at 18 because the declared constructor does not find 20). Each repair buys the *nominal label back on every seed*, at a cost that is different in kind — one changes a selection rule inside the same world, the other changes the world.

## Option 1 — raise the endpoint cap (3 → 4)

Capacity on sixteen tags is `16 × cap / 2`, so the ceiling rises from 24 to 32 relations. Measured on the existing competent pools, by the declared construction at each cap:

| Seed | Cap 3 | Cap 4 | Cap 5 |
| --- | ---: | ---: | ---: |
| `20740101` | 21 | 27 | 32 |
| `20740102` | **17** | **20** | 23 |
| `20740103` | 23 | 30 | 34 |
| `20740104` | 22 | 29 | 33 |
| `20740105` | **18** | **22** | 25 |
| `20740106` | 21 | 26 | 28 |

**Cap 4 makes twenty reachable on every seed**, so the nominal block is restored with the same pool, the same world and the same baseline.

**What it costs — and it is not the arithmetic, it is the dependence.** A 20-row block already uses **13–16 of the 16 tags** at cap 3, with a maximum tag load of **3**. Raising the cap does not spread the block over more tags; it puts a **fourth row on a tag that already carries three**. Distinct tags at twenty rows move by at most one (15 → 16 on one seed, down one on another). So the price is not "more tags touched" but "more rows sharing the tags already touched": the twenty rows become more correlated, and C8's per-seed rate is then computed over rows that are not independent draws. The gate's resolution is nominal — twenty rows — while its *effective* sample is smaller, and nothing in the current contract corrects for that.

Secondary cost: the cap is a published rule constant, so changing it is a recorded rule change with a new selection digest, and the earlier artifacts' target sets stop being comparable to the new block.

## Option 2 — increase the tag count (16 → more)

**Measured at 28 tags: it fails.** Candidate edges rise 161% (383 → 1000) while K-available rows rise **0.8%** (242 → 244) and A&K density falls **63.2% → 24.4%**, leaving 15–26 competent rows per seed against 20 required; the preflight is `FAIL 0/6` (`A1-K-DILUTION-1`, `A1-LARGER-UNIVERSE-CANDIDATE-1`). K is window-limited, so a larger universe spreads a fixed window over more relations.

**Counts between 16 and 28 are unmeasured.** The mechanism predicts monotone dilution, so the option's plausible range is "worse than 16 and better than 28", not "better than both" — but that is a prediction, not a measurement, and it should not be spent as if it were.

**The cost is larger than the density figure.** The tag count *is* the world: every committed A1 artifact — candidate universe, 36-cycle boundary, baseline availability, competence pools, C1 ceilings, C4 exposure — is specific to the 16-tag world and its seed blocks. A tag change does not adjust the preparation; it **retires** it and starts the freeze chain again from a new universe, new baseline and new block. That is the whole six weeks of preparation, not a parameter.

## The comparison, in one place

| | Cap 3 (current) | Cap 4 | 28 tags |
| --- | --- | --- | --- |
| 20 rows on every seed | no (17, 18 on two seeds) | **yes** | no (15–26 competent) |
| C8 adjudicable | **yes, at ≥17** | yes, at 20 | no |
| C8's effective dependence | max 3 rows per tag | **max 4 per tag** | n/a — fails earlier |
| Preparation retained | — | **yes, same world** | **no — new universe** |
| Measured? | yes | pool counts only (above) | yes, `FAIL 0/6` |
| Threshold change | none | none (a rule constant, not a threshold) | none |

## Recommendation, marked as one

**Take neither, and keep cap 3 with the adopted at-least-17 floor.** C8 is already adjudicable on six seeds; both repairs buy a label — "twenty on every seed" — and each charges for it. The cap change charges in **dependence**, quietly: the only thing the extra edge buys is a fourth row on a tag that already has three, which is precisely the sort of unmeasured assumption that C8 exists to avoid making. The tag change charges the entire preparation and is measured fatal at its only measured point.

If the owner wants the nominal block restored anyway, **cap 4 is the cheaper of the two by a wide margin** — same world, same pool, no threshold moved, one rule constant and a new digest — provided the dependence cost is declared in the act: twenty rows over thirteen-to-sixteen tags with up to four rows per tag, so the per-seed rate is a rate over correlated rows and its nominal resolution overstates its effective one.

## What would change this

A measured effective sample size for a 20-row block at cap 4 — how much of C8's resolution survives the fourth row per tag — would turn the dependence cost into a number and make the choice a comparison rather than a preference. A world at 20–22 tags with A&K density held above 50% would make the tag option live; nothing in the record suggests such a world exists, and the dilution result is the reason.

## Reproduce

```bash
python -m benchmarks.a1_competence_filter_draft --check    # competent pools and cap-3 witnesses
```

The cap-4 and cap-5 ceilings above are the declared construction run on those same committed pools at `limit = 4` and `5`; the tag-count figures are `A1-K-DILUTION-1` and `A1-LARGER-UNIVERSE-CANDIDATE-1`. No engine ran.
