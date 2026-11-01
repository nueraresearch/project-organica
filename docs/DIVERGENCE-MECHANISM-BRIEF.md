# The next instrument — where the two sides first part company

> **What this document is.** A plan, written and committed **before** any run,
> for the next observer in the D0 reproduction line. It is not a finding and it
> is not a decision about V2, the campaign, or D0. Its only commitment is that
> the hypothesis and the observations that would refute it are fixed in
> advance, in this file, before the first measurement.

**Status: PLANNED, NOT BUILT.** Nothing described here has been run. Every
statement about the engine below is a reading of the frozen source; every
statement about the record is a citation to a committed artifact. Where this
document names a *site*, it means *a site read from the code*, and §4 is
where the part that has not been measured is named as such.

**Which "the next instrument"?** This is the next *observer* in the D0
reproduction line — the line that asks why eight seeds of the 30-seed campaign
do not reproduce. It is **not** the acquisition campaign (600 cells, never
run, HELD behind the gate), **not** V2 or any other architectural work
(Organica 1 is frozen and `tests/test_v1_freeze.py` enforces it), and **not** a
new research phase. It is a read-only observer plus one intervention applied
to the *harness*. **It changes no engine file.**

---

## 1. The one question

**At the cycle where the two admitted streams first differ, where in the
engine's candidate construction do they first differ — in which candidate
type, in which builder, and is the difference in the order, in the membership,
or in a candidate's content?**

That is the whole question. It is narrower than "why did the seeds fail", and
it is the next thing the record can actually answer, because the record now
holds the cycle, the population and the order, and holds nothing about the
construction that turned one into the other.

---

## 2. What the record already says, and what it does not

| Established | Source |
|---|---|
| The eight failing seeds are a **hash-order artifact**. The engine is byte-identical to the campaign-era state, and the committed code reproduces the campaign's own candidate population exactly on all eight seeds once `PYTHONHASHSEED` is varied. | `docs/candidate_membership_audit.json`; journal §71 |
| The two populations part company at sleep cycles **2 to 11**, depending on the seed. | `docs/candidate_membership_audit.json` → `divergence.first_cycle`; journal §71 |
| At the divergence cycle the pool holds the **same set** of candidate IDs in **11 of 16** arm-pairs and the **same order** in only **3**; in **8** the candidates are identical and only the order differs. | `docs/divergence_cycle_capture.json`; journal §72 |
| For **3** arm-C pairs (T2/20261118, T2/20261123, T2/20261130) the two sides' pools at the divergence cycle are identical **in set and in order**, and arm C's admitted stream still differs there. | `docs/divergence_cycle_capture.json`; journal §72 |

**The gap this plan closes.** The capture names what the organism had in front
of it and the order it read it back in. It does **not** decompose the step
that turned that into the admitted stream, and it does not observe the order
the construction actually used. The last row above is the sharp edge: on
those three pairs the pool is the same and the result is still different, so
the difference arose **inside** the cycle.

**What this plan does not reopen.** The code is excluded by provenance and by
measurement; the campaign's hash seed was never recorded; D0 is not re-scored;
the acquisition cells stay HELD.

---

## 3. The construction, read from the frozen source

This section is code reading, and every claim in it is checkable at the cited
line. **None of it is a measurement.** Whether any of these sites is
*exercised* on the failing seeds is §4's question.

### 3.1 The engine builds its candidates from hash-order-dependent sequences

Four sites in the construction path, in the order the cycle reaches them.

**(a) The tag scores.** `organica/sleep.py:904-920` — `_score_tags()`:

```python
all_tags = set(freqs) | set(cooc) | set(temporal)
for tag in all_tags:                       # a set of strings: hash order
    ...
    scores.append(score)
scores.sort(key=lambda s: s.frequency, reverse=True)
```

The iteration is over a **set of strings**, and the sort key is `frequency` —
an integer that ties constantly. `list.sort` is stable, so **equal-frequency
tags keep the set's iteration order**. The *content* of a `_TagScore` is
order-independent; its **position** is not.

**(b) The temporal graph.** `organica/memory.py:379-385` — `temporal_edges()`:

```sql
SELECT tag_from, tag_to, count FROM precedes WHERE count >= ? ORDER BY count DESC
```

`precedes` is `PRIMARY KEY (tag_from, tag_to)` (`organica/memory.py:122-127`)
and there is **no index on `count`** — the only indexes in the schema are on
`events` (`memory.py:129`, `:168`, `:171`). The rows are scanned in table
order, which for a rowid table is insertion order, and the query specifies
**no order among rows with equal counts**. `organica/sleep.py:871-875` then
builds the graph in exactly that order.

**(c) The predictions.** `organica/sleep.py:1139-1160` — `_build_predictions()`:

```python
for tag_from, targets in temporal.items():
    for tag_to, count in targets.items():
        if count >= self.PREDICTION_MIN_COUNT:      # 5, sleep.py:329
            candidates.append(PredictionCandidate(...))
candidates.sort(key=lambda p: p.evidence["temporal_count"], reverse=True)
return candidates[:self.MAX_PREDICTIONS]           # 20, sleep.py:357
```

Again a stable sort on a key that is **not total**. Equal-count predictions
keep the graph's order, which is (b)'s order.

**(d) The anomalies — and this one changes a candidate's *content*.**
`organica/sleep.py:1162-1186` — `_build_anomalies()`:

```python
sorted_targets = sorted(targets.items(), key=lambda x: -x[1])
top_tag, top_count = sorted_targets[0]
```

The key is the count alone, so among tags with equal counts **the first in
the graph's order becomes the anomaly's expected tag**. The anomaly's
*identity* — its id, its expected/observed pair — therefore depends on the
order, not only its position.

**(e) The composites.** `organica/sleep.py:1201`, `:1217`, `:1223` —
`_compose_meta_concepts()`: the tags of each prior candidate are collected
into a `set`, iterated as a set, and the candidates of each tag come out of
`list(set(...))`. Hash-order dependent throughout.

### 3.2 The caps — and the one that does *not* bind here

The engine truncates every candidate type: concepts, phrases, loops (15),
anomalies (10), meta-concepts (15), processes (10), workflows (10), hypotheses
(15), theories (8), questions (6), dreams (8), investigations (5), experiments
(5), predictions (20) — `organica/sleep.py:328-359`.

**The harness overrides the predictions cap only.**
`benchmarks/formation_utilization.py:195-196`: `CAP_A = 20`, `CAP_B = 1_000`.
Arms B and C therefore keep **every** prediction the builder produces, and
the predictions truncation **does not bind** in the campaign's arms. The other
engine caps — and the sites at (d) and (e) — are untouched by the harness and
apply in every arm.

This is worth stating plainly because the opposite assumption is the obvious
one, and it is wrong: **the eight failing seeds are not eight seeds whose
predictions were cut at twenty.** They are eight seeds whose *construction*
saw a different order.

### 3.3 Identity is not at risk — position and content are

`_make_id` (`organica/sleep.py:45-48`) is `sha256` of the key parts. A
candidate's id is identical in both runs wherever its *inputs* are identical.
So the divergence is not "the same slot got a different name"; it is "the same
candidates were assembled differently", and at site (d) "a different candidate
was assembled at all".

### 3.4 The harness already computes much of what the instrument needs

`benchmarks/formation_utilization.py:488-514` — `_AdmissionSleepService`
overrides `_build_predictions`. It raises the cap to `10**9`, takes the
engine's **full pre-cap list**, records it as `pre_cap` with each candidate's
`evidence` (which carries `temporal_count`), records the pre-filter
`eligible` set, and *then* applies the arm's own slice. The per-cycle
admitted stream the membership audit digests is the prediction list.

So for the predictions, the data for the analysis is **already computed and
simply not persisted**. For the other types it is not computed at all, and
the instrument has to reach it.

---

## 4. The hypothesis, and what would refute it

> **H1.** The eight failing seeds' divergence enters through **order-sensitive
> candidate construction**: the engine assembles its candidates from sequences
> whose order the hash seed changes, so the same world produces different
> candidate lists.
>
> **H2 (the strong form).** Canonicalising that order removes the divergence:
> with the harness assembling candidates from canonically ordered inputs, the
> eight failing seeds' per-type tables become **hash-seed invariant**.

H1 names a class of mechanism; **the instrument's job is to locate the site**,
and it is designed to do that without being told where to look. H2 is the
decisive experiment: it either holds, or the channel is refuted.

**Pre-registered predictions.** Committed before the first run.

| | Prediction |
|---|---|
| **P1** | At the divergence cycle, the two sides' assembled lists differ for **at least one** candidate type, and the difference is visible in a builder's **pre-sort** sequence — i.e. it is present before any sort or cap. |
| **P2** | The **control** seed's assembled lists are **identical at every hash seed**, for every type. |
| **P3** | Under the canonicalised-order intervention of §5 Arm B, the eight failing seeds' per-type tables become **hash-seed invariant**. |

**Pre-registered falsification criteria.**

| | Refutation |
|---|---|
| **F1** | If the canonicalised-order intervention leaves the eight seeds' tables **still varying** with the hash seed, the order channel is not sufficient and **H2 is refuted**. The search moves on rather than being re-tuned. |
| **F2** | If the canonicalisation changes the **control** seed's table at a fixed hash seed, the intervention is not equivalent, the experiment is confounded, and **no conclusion may be drawn from Arm B** until the intervention is re-specified. |
| **F3** | If a candidate type's assembled list is identical, in membership **and** order, on both sides at every cycle up to and including the divergence cycle, that type is **excluded** as the site. |

F2 is a control the harness can fail, and it is stated in advance because an
intervention that changes the control is the classic way to manufacture a
confirmation.

---

## 5. The instrument

Two arms, in this order. Arm A is cheap and decides whether Arm B is worth
running. **A commit precedes Arm A**, carrying this document's predictions and
falsification criteria unchanged.

### 5.1 Arm A — observational: locate the site

A new read-only script, `benchmarks/layer1_cut_capture.py` (name to be
settled when it is built), running the harness's arms B and C under the two
hash seeds exactly as `benchmarks/divergence_cycle_capture.py` does — the
same sequence, the same fresh database per worker, the same arm-C admission
basis. It persists, at the divergence cycle and the cycle before, for **every
candidate type the engine builds**:

- the assembled list **in order**, with each candidate's id and the field
  that sorts it;
- the **pre-sort** sequence where the builder has one, so the two can be
  compared;
- the **cap** the builder applied and whether the list was truncated at it;
- the **tie-block structure at the cap boundary**, where there is one;
- the temporal graph **as read**, in order, and the `stable_prior` read-back
  order.

From those it reports, per type and per side: the first position at which the
two sides' lists differ; whether the difference is **order**, **membership**
or **content**; and the type and builder it happened in.

**The addressing rule is the one the capture already proved.** The capture
refused any window whose newest `sleep:meta` marker did not carry the cycle
it claimed to be in, and 16 of 16 window pairs were addressed by their own
marker. The new instrument inherits that rule: a capture whose position is
not witnessed by the engine's own cycle marker is **refused, not reported**.

**No engine file changes.** The observer lives in the benchmark process and
reads what the harness computes; where it has to reach a builder the harness
does not already record, it wraps the builder rather than editing it.

### 5.2 Arm B — interventional: canonicalise the order

In the harness only, make the construction order canonical, and re-run the
eight failing seeds at each hash seed:

1. **The graph.** Have the harness read the temporal edges in a canonical
   order — by `(tag_from, tag_to)` — rather than in the table's scan order.
   The rows and their counts are unchanged; only their order is.
2. **The composites.** Have the harness build the composite candidates from
   canonically ordered inputs, replacing the set iteration with a sorted one.

This is the smallest change that removes the order channel *at its source*,
and it is applied where the engine's own file is frozen. It is deliberately
**not** "add a tie-break to every sort": that would be a different and much
larger intervention, and this one is falsifiable by the same control.

Then ask the decisive question: **do the eight failing seeds' per-type tables
become hash-seed invariant?**

---

## 6. Controls

| | Control | What it must do |
|---|---|---|
| **C1** | The **control seed** (T1/20261101) | Reproduces at every hash seed today. Its assembled lists must be identical at every hash seed (P2), and its per-type table must be byte-identical at a fixed hash seed under the intervention (F2). |
| **C2** | **Behaviour-neutrality of the observer** | A run with the observer and a run without it produce identical per-type tables and identical admitted streams. The harness already has this check for its own recording subclass; the new observer must pass the same one. |
| **C3** | **Determinism of the capture** | Two runs at the same hash seed in separate processes produce identical captured data. The capture instrument already does this: its sixteen parts were written twice and compared field by field, 16 of 16 identical. |
| **C4** | **The intervention is scoped** | The canonicalised run must equal the unpatched run wherever the order was already canonical. Checked per cycle and per type, not only in aggregate. |

A baseline may never be handicapped, and every harness here needs a control it
can fail.

---

## 7. What this will and will not establish

**Will**, if the predictions hold:

- **the site**: the candidate type, the builder, and the line of the engine
  where the two sides first construct differently;
- whether the difference at that site is in the **order**, in the
  **membership**, or in a candidate's **content**;
- whether the order channel **is** the whole story, which Arm B answers
  either way.

**Will not**:

- re-score D0, or change any verdict;
- estimate room, or name a mechanism for V1's measured deficits;
- modify `organica/` — Organica 1 stays frozen, and the freeze test stays
  green;
- say anything about the acquisition campaign, which remains HELD;
- establish that a canonical order would make the *campaign's* numbers right.
  It establishes that the *engine* stops depending on storage order. Whether
  the campaign's own table was the correct one is a separate question and is
  **not** answered here.

**If H2 is refuted** (F1), that is a result, not a failure: the plan exists to
be able to fail, and the record will say so in the same way it says
everything else. A refutation closes the order channel and moves the search,
rather than re-tuning it.

---

## 8. What this does not decide

No V2 design, no architecture change, no campaign, no new research phase, no
version bump, no release. Organica 1 stays frozen at `v0.9.0`. D0 stays fired
and the use path stays the target. The acquisition cells stay HELD behind
their gate.

---

## 8a. Disclosure (2026-11-01) — appended after the run; sections 1-8 are unchanged

**What this plan started from was measured one cycle early.** The record it cites is the 2026-10-31 divergence-cycle capture, which reported the two sides holding the **same set** of candidate IDs in **11 of 16** arm-pairs, the **same order** in **3**, and identical in set *and* order on **3** seeds while the admitted streams still differed. That was `OBSERVER_VERSION` 2. `candidate_membership_audit.first_divergence()` stores `first_cycle` as a **zero-based** index and window index *i* is engine cycle *i*, so those pools are the cycle **before** the divergence and the capture labelled them with the divergence cycle's number.

Re-measured at the divergence cycle itself (`OBSERVER_VERSION` 3, 16 runs), the two sides hold the same set in **0 of 16** arm-pairs and the same order in **0 of 16**: membership differs everywhere. **There are no identical pools at the divergence cycle for this experiment to explain**, so the premise that the difference must arise *inside* the cycle is withdrawn rather than refuted.

**This plan is left exactly as committed.** Its hypothesis, two forms, three predictions, three falsification criteria and four controls were fixed before the run and are judged against it; the record of that run is journal §74 and `docs/DIVERGENCE-MECHANISM-RESULTS.md`. What the run located — `_score_tags`, order-sensitive from cycle 1 on every seed including the control — stands as a property of candidate **construction**, and is not evidence about where the divergence begins. The question this brief would have to be rewritten to ask is narrower: **at what earliest cycle do the two candidate populations first differ, and which operation introduces that difference?**

---

## 9. Cost and order of work

| Step | Cost |
|---|---|
| Commit this plan | — |
| Arm A — 16 worker runs (8 seeds × 2 hash seeds) | The same shape as the capture's v2 rebuild: 16 runs, about 30 minutes at 4 workers on this machine (7.5 GB RAM; the cap is ~5). |
| Arm B — 8 seeds × N hash seeds, canonicalised | The same order as the membership audit's 144-run sweep. |
| Write-up | Journal §74, a manual finding, a facts-sheet row, a CHANGELOG entry, and the artifact plus its generated report. |

Order matters more than speed here: **Arm A before Arm B**, because Arm A
locates the site and Arm B is only worth its cost if the order channel is
still the live hypothesis after Arm A has looked.

---

## 10. What was read, and how far

Read in full, on 2026-10-31, from the frozen engine at the `v0.9.0` tag:

- `organica/sleep.py` — the cycle (`run`, lines 436-569), the tag scoring
  (`_score_tags` 904-920), the Layer-1 builders (`_build_concepts` 957-,
  `_build_loops` 1076-1137, `_build_predictions` 1139-1160, `_build_anomalies`
  1162-1186), the composite assembly (`_compose_meta_concepts` 1192-1225 and
  the `stable_prior` loops at 463-509), the constants (328-359, 421), and
  `_make_id` (45-48).
- `organica/memory.py` — the schema (113-128), the indexes (129, 168, 171),
  `temporal_edges` (379-385), `recent` (387-397), and the neighbouring queries
  (353-377).
- `benchmarks/formation_utilization.py` — the arm caps (195-196),
  `_AdmissionSleepService` (439-514) and `_fresh_db` (517-522).

Read from committed artifacts: `docs/candidate_membership_audit.json`,
`docs/divergence_cycle_capture.json`, `docs/use_path_audit.json`, journal
§§69-72, and `docs/CANDIDATE-MEMBERSHIP-AUDIT.md`,
`docs/DIVERGENCE-CYCLE-CAPTURE.md`.

Nothing in this document is recalled from memory. Every engine statement
cites a line; every record statement cites an artifact.

---

→ `docs/candidate_membership_audit.json`; `docs/divergence_cycle_capture.json`;
`benchmarks/formation_utilization.py`; `organica/sleep.py`; `organica/memory.py`;
journal §71; journal §72.
