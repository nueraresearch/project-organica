# The competence rule, in force — one page, by reference

**Date:** 2026-11-15

**Status:** `READING — NOT A DECISION; ADDS NOTHING, CHANGES NOTHING, FREEZES NOTHING`

**Scope:** which record makes each part of the A1 competence rule bind, and which parts do not bind yet. This page states
**no constants**. Every value lives in the adopted record it links, and a page that repeated one would be a second place
to keep it right.

## What this page is, and what it cannot do

A reading of committed records, written because the rule is spread across several and a reader should not have to
reconstruct the set from the index. It has no authority of its own: **if this page and a record disagree, the record is
right and this page is wrong.** It freezes no manifest, reserves no seed, changes no threshold, authorises no cell and
records no result.

## What binds

| Part of the rule | Binds in | In one line |
| --- | --- | --- |
| The row the gate scores | [`DECISION-A1-C1-UNIT`](DECISION-A1-C1-UNIT.md) | one directed target edge in one seed; rows are never pooled across seeds |
| What makes a target row competent | [`DECISION-A1-C8-NMIN`](DECISION-A1-C8-NMIN.md), its *Unit* row | both of the row's baseline paths must be present at the recorded no-arm baseline |
| The floor on competent rows per seed | the same record | stated in its contract table — named here, not restated |
| The threshold the rate is read against | the same record | stated there, unchanged by that decision |
| The endpoint cap the block is constructed under | the same record | stated there, unchanged by that decision |
| That a block short of the nominal size is not automatically VOID | the same record, which supersedes answer 1 of the draft rule | the floor replaces exact-N; a short block is a different resolution, not a weaker copy |
| That the estimand is the rate, not the block size | the same record | N is a resolution attribute of the measurement, disclosed per seed |

## What does not bind yet

- **Nothing, as of 2026-11-15.** The selection procedure was the last item here; it binds now through the record
  adopted that day. The clause-by-clause wording in
  [`A1-C2-C8-COMPETENCE-RULE`](A1-C2-C8-COMPETENCE-RULE.md) is still stamped `DRAFT` and is not itself binding — it
  is the wording the adopted records took up, and a reader who needs the rule should cite those records.

## Where the constants live, and why not here

[`DECISION-A1-C8-NMIN`](DECISION-A1-C8-NMIN.md) carries the floor, the threshold and the endpoint cap in one table, under
an owner signature. That is the only place they are stated as binding. This page names them and names no values, so it
cannot drift from the record: there is nothing here to drift.

## How to check this page

```bash
python -m pytest tests/test_a1_competence_rule_page.py -q
```

The check asserts that every decision this page cites resolves on disk and is `ADOPTED` in `docs/decisions.json`, that
the draft it calls a draft is cited as one, and that the page contains none of the constants — the last one being the
property that makes "by reference" a claim rather than a style.

## What this page cannot tell you

The block sizes, the per-seed pools, and whether C8 passes. Those are measurements and records, not readings: read
[`DECISION-A1-C8-NMIN`](DECISION-A1-C8-NMIN.md) for the floor, the freeze acts for the blocks, and
[`a1_c8_target_selection_competent.json`](a1_c8_target_selection_competent.json) for what the construction found.
