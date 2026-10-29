# Gate 13 — relation separation: what it removes, and what it does not

**Status: DIAGNOSTIC RECORD (2026-10-29).** This document records the probe
that asked the project's sharpest open question: *can world relations be
separated from engine-generated relations, without modifying the frozen
engine?*

The answer is **yes, the separation is real and exactly as predicted — and no,
it is not sufficient.** Both halves matter, and the second half is the finding.

All seeds used here are diagnostic (`20261101`–`20261103`, designated by
Amendment 3). The confirmatory sample (`20261106`–`20261130`, 25 seeds) is
untouched.

---

## 1. The mechanism, located

`organica/memory.py::store()` gates the **trigger**:

```python
# Only build graph edges from external experience, not internal
# sleep output.  Sleep candidates are stored but don't pollute
# the co-occurrence / temporal graphs.
if event_type != "sleep":
    self._record_cooccurrences(event.tags)
    self._record_temporal_edges(event.tags)
```

but `_record_temporal_edges` builds its **window** with an unfiltered query:

```python
rows = self._conn.execute(
    "SELECT tags FROM events ORDER BY time DESC LIMIT ?", (lookback,)
).fetchall()
```

So a **world** event triggers recording and takes its `tag_from` from whatever
rows precede it — **sleep rows included**. This is disclosed as **D2** in
`docs/AUDIT-TRACE-SPEC.md`: *"the temporal graph's lookback window has no
`event_type` filter, so a supporting transition can originate from the
organism's own previous sleep payload."*

It was disclosed but not measured. Now it is measured, and the measurement is
larger than the disclosure implied.

## 2. The substrate is 99.5 % the engine's own output

| Seed | world events | sleep events | ratio | `precedes` rows |
|---|---|---|---|---|
| 20261101 | 756 | **152,186** | **201×** | 373 |
| 20261102 | 761 | **235,271** | **309×** | 379 |
| 20261103 | 772 | **263,533** | **341×** | 405 |

The engine stores one sleep event per candidate per cycle, so after 110 cycles
it has written **two to three hundred times** as many rows about its own
thinking as it has rows about the world. Its cognition window
(`recent(n=4000, event_type="sleep")`) is therefore made almost entirely of its
own output — which is by design, and is not a defect in itself.

But it means the substrate the world is supposed to be recorded in is
overwhelmingly the engine's own descriptive machinery.

## 3. What the separation removes

The probe rebuilds the `precedes` table offline and applies the engine's own
rule. It carries its own proof-of-firing: the rebuilt table must **match the
engine's table exactly**, or the probe refuses to report. It matched on all
three seeds.

| Seed | rows removed | share of the table | **of those, sleep-sourced `tag_from`** | rows left |
|---|---|---|---|---|
| 20261101 | 133 | **35.7 %** | **100.0 %** | 240 |
| 20261102 | 139 | **36.7 %** | **100.0 %** | 240 |
| 20261103 | 165 | **40.7 %** | **100.0 %** | 240 |

**Every single row the separation removes has a sleep-sourced `tag_from`.**
The contamination is not a hypothesis about what might be happening; it is
**exactly** the D2 mechanism, and it is a third to two-fifths of the relation
table.

The remaining 240 rows are precisely the world-tag pairs (16 tags × 15).

## 4. And it is not enough

Three tables, each selected by the engine's own Layer-1 rule — global top-20
by count — from the same engine run.

| Seed | table | coverage | precision | intra-cell | inter-cell | rank of first world edge |
|---|---|---|---|---|---|---|
| 20261101 | raw (engine) | 0.0000 | 0.0000 | 20 | 0 | 30 |
| | **filtered LIMIT 3** | **0.0000** | 0.0000 | 20 | 0 | 35 |
| | **filtered LIMIT 4** | 0.0179 | 0.1000 | 18 | 2 | **16** |
| 20261102 | raw (engine) | 0.0089 | 0.0500 | 19 | 1 | 18 |
| | **filtered LIMIT 3** | **0.0000** | 0.0000 | 20 | 0 | 34 |
| | **filtered LIMIT 4** | 0.0357 | 0.2000 | 16 | 4 | **8** |
| 20261103 | raw (engine) | 0.0000 | 0.0000 | 18 | 2 | 53 |
| | **filtered LIMIT 3** | **0.0000** | 0.0000 | 20 | 0 | 37 |
| | **filtered LIMIT 4** | 0.0446 | 0.2500 | 15 | 5 | **8** |

**With every contaminated row removed, the world's edges still do not reach
the top 20.** The top 20 remains 75–100 % intra-cell.

The separation **does** move the world's edges up sharply — the first world
edge goes from rank 30 / 18 / 53 to **16 / 8 / 8** under the LIMIT-4 variant.
That is a large improvement in *rank*, and it is still not enough to clear the
gate.

### Why the remaining competition is intra-cell

A cell's two tags co-occur in **every** event of that cell, so an intra-cell
pair accumulates a count of the order of (events ÷ cells). The world's
transitions are individual tag-level transitions under a cell-level law, so a
specific tag pair follows the law only a fraction of the time. The two
populations are separated by roughly an order of magnitude in count, and a
global count-ranked cut of 20 is consumed by the first population entirely.

**This is why the two probes disagree about which mechanism dominates.**
In the **1-tag** stimulus an event carries one tag, so there are no
intra-cell co-occurrence pairs to compete — and there the crowding *is* the
internal vocabulary (first world edge at rank 31, top 30 rows all
`internal→world`). In the **2-tag** stimulus the internal vocabulary is
removed and the crowding is the intra-cell pairs. **Each world shows one
dominant mechanism, and they are different mechanisms.**

## 5. What this settles, and what it leaves open

### Settled

1. **Provenance mixing is real, measured, and exactly as D2 described.**
   35.7 %–40.7 % of the relation table is the engine's own descriptive
   vocabulary, and **100 %** of the removed rows are sleep-sourced.
2. **The separation is available without privileged knowledge.** It uses
   `event_type`, which the engine **already records on every event**. It is
   not an oracle — unlike the world-vocabulary filter of
   `docs/GATE13-CAUSAL-ACCOUNT.md` §4, which selects on `TAG_POOL` and is
   therefore not an organism-side fix.
3. **Separating the families is NOT sufficient.** At the frozen budget of 20,
   with every contaminated row removed, coverage is **0.0000–0.0446**.
   "Useful structure exists below the selection boundary" is **true** and
   "separating the families would recover it" is **false**.

### Open

4. **Whether separating the families is sufficient *given* a non-frequency
   ranking.** The two are entangled: if candidates were ranked by something
   other than raw count — informativeness about a relation rather than its
   frequency — the intra-cell pairs would stop monopolising the budget, and
   the provenance filter would then be a *second* requirement rather than a
   sufficient one. **That combination has not been measured**, and it is now
   the sharpest question the project can put to a small probe.
5. **Whether the substrate should be 99.5 % self-generated.** Not a defect
   in itself — the window is meant to be the engine's own state — but it sets
   the scale of the problem: the world's relations are a minority in a
   substrate that is almost entirely the organism's own account of itself.

## 6. What this changes for V2

The V2 question was, after §52 of the journal: *can the organism identify
which of its vocabulary items are its own, and can it rank candidates by
something other than raw frequency?*

It is now **three** requirements, and they are concrete:

1. **Provenance separation.** The world relation table must not contain
   relations sourced from the organism's own output. One filtered lookback
   query; the information is already in the schema.
2. **Relation-family separation.** Co-occurrence and transition relations
   must not compete for the same budget. The `cooccurrences` and `precedes`
   tables are already separate — they are re-mixed downstream, in Layer 1.
3. **A ranking that is not raw frequency.** Even with (1) and (2) done, the
   world's transitions are out-ranked by its own co-occurrence by roughly an
   order of magnitude, because the two differ in *frequency* and not in
   *kind*.

**Requirement 3 is the one with no precedent in the engine, and it is the
one that yesterday's capacity sweep showed cannot be bought with budget:**
precision never exceeds 0.3443 at any budget under either allocation rule.

**No V2 build is authorised by this document.** It narrows the target from
"relation-family separation" — one requirement — to three, and identifies
which of them is the hard one.

## 7. What this does not establish

- **It does not establish that any V2 would work.** It establishes what a V2
  would have to do.
- **It does not change any verdict.** The six negative task families, the
  Phase L protocol verdict `H3-L — INCONCLUSIVE`, the Phase L
  characterization, and the campaign's stop at Gate 13 all stand.
- **It does not change the confirmatory sample.** Every seed used is
  diagnostic and remains diagnostic.
- **It does not reopen the frozen engine.** The probe rebuilds the table
  offline; `organica/` is untouched and Organica 1 remains frozen at
  `v0.9.0`.
- **It does not rehabilitate the world-vocabulary filter as a fix** — that
  filter remains an oracle (§5, point 2).
- **The LIMIT-4 variant's advantage is measured, not explained.** The probe
  reports that a four-row world window finds the world's edges at rank 8–16
  where a three-row window finds them at rank 34–37. Why the deeper window
  helps is not established, and the window depth interacts with the harness's
  event ordering, so it should not be read as a tuned parameter.

## 8. Reproducing

```bash
# the relation-separation probe (3 seeds; ~6 min)
python benchmarks/probe_relation_separation.py
```

**Artifacts:**

- `docs/gate13_relation_separation.json` — this probe's results
- `docs/gate13_allocation_rule.json` — the allocation-rule probe
- `docs/gate13_capacity_sweep.json` — the capacity sweep
- `docs/GATE13-CAUSAL-ACCOUNT.md` — the causal account this extends
- `docs/GATE13-PREFLIGHT-AUDIT.md`, `docs/GATE13-PAIRED-CAPACITY-TEST.md` —
  the earlier two write-ups
