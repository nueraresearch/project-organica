# The store-time observer — which write admits the extra candidate

> **What this document is.** A plan, committed **before any run**, for the next
> observer in the D0 reproduction line. It is not a finding, and it is not built.
> Its only commitment is that the question, the result space, the reconciliation
> rule, the controls and the falsification criteria below are fixed here, in this
> file, before the first measurement.

**Status: PLANNED, NOT BUILT.** Nothing described here has been run. Every
statement about the record cites a committed artifact; every statement about the
engine is a reading of the frozen source at `v0.9.0`.

> **Status note, 2026-11-01 (appended; the plan above is unchanged).** The
> **core is now built** (`benchmarks/store_time_observer.py`) and its neutrality
> control has passed: the observed and unobserved runs agree on the admitted
> stream and the temporal reads, the comparator is proved to fire on an injected
> difference, and every cycle reconciles. The **known-positive control (C1 / F4)
> now passes**: on the control seed at hash seeds 0 and 1 it attributes all
> twelve candidate differences at cycles 10-12 to construction-stage writes, with
> every window witnessed by its own marker
> (`docs/store_time_observer_f4.json`). **F5 passes too:** with the finer split of
> §9 installed and neutrality re-proved, 17 distinct labels were observed and all
> twelve attributed candidates carry `pool:dream` — the pre-registered finding that
> on the control seed (B-restated) is not reached. The **verdict pass over the
> seeds is still not built**, so no divergence verdict has been read. Controls are committed as
> `docs/store_time_observer_self_test.json` and `docs/store_time_observer_f4.json`.

**Why this instrument and not another correction.** The divergence line is frozen
(journal §78). Four corrections removed claims that were wider than their checks,
and the one that survived — pool divergence appears as **insertion** rather than
replacement — is a fact about pools, not about the operation that produces them.
Every instrument built so far sits **downstream of the write**: the capture
observer wraps `MemoryService.recent` and `fu.run_arm`, and the mechanism
instrument records builders' outputs (journal §79). None of them can see a
candidate enter the store. The question that survives is therefore not another
reading of existing artifacts; it needs a new observation surface.

---

## 1. The one question

**At the cycle where the two candidate pools first differ, which store-time write
admits the candidate that one side holds and the other does not — and was that
candidate offered to the store differently, or offered identically and accepted
differently?**

Not *"_score_tags caused it"* — the mechanism instrument already measured what
`_score_tags` does, and it is order-sensitive from cycle 1 on every seed.
Not *"when did the divergence begin"* — the onset instrument is inadmissible for
that (F2 fired). Not *"no write explains it"* unless §4's reconciliation holds.

## 2. What is already known, and what it brackets

- **The divergence is an insertion.** 18 runs, 0 cached: pool differences appear
  as candidates entering and leaving, and at the first differing cycle the sets
  are not equal on 16 of 16 arm-pairs (`docs/divergence_onset.json`,
  `docs/DIVERGENCE-ONSET.md`).
- **The onset measurement cannot be attributed to D0.** F2 fired: the control
  seed's own two hash-seed runs differ in membership at cycles 10–12 on arm B.
  That removes a **timing** claim. It does not remove the insertion facts, which
  are about pools.
- **The earliest hash-sensitive builder the instrumentation can see is
  `_score_tags`**, on 8 of 8 failing seeds and on the control seed
  (`criteria/P2/per_type/B/score_tags: false`), and canonicalisation does not
  touch it (`criteria/F2/per_type_unchanged/B/score_tags: true`).
- **The mechanism experiment's control failed** (C1 / P2): the control seed's
  assembled lists are not identical across hash seeds. Nothing about cross-seed
  invariance is inherited from that experiment except the per-type facts above.
- **The known-positive case.** The control seed under hash seeds 0 and 1 already
  differs — membership, arm B, cycles 10, 11, 12. An observer that cannot explain
  a difference the record already contains is blind, and §6 makes that fatal
  rather than merely disappointing.

## 3. The instrument

One passive wrapper, no engine change, scratch database per worker.

**The write surface, from the frozen source.** `MemoryService.store`
(`organica/memory.py:244`) is the admitting call; it dispatches into
`_record_tag_counts` (287), `_record_cooccurrences` (306) and
`_record_temporal_edges` (321). `record_sleep_cycle` (443) advances the counter
and `prune_sleep_candidates` (452) removes candidates.
`SleepService._store_candidates` (`organica/sleep.py:1916`) calls `store` once for
the cycle payload and `_store_single_candidate` once per candidate type.

**What is recorded, per call.** The cycle it belongs to (`latest_sleep_cycle`),
its ordinal within that cycle, `event_type`, the candidate type and id, a digest
of the content, the tag list, and **whether the row was accepted**, taken from the
delta in `MemoryService.count()` across the call. The record is a list, not a
summary: the point of this instrument is that a call can be named.

**Reconciliation is a measured quantity, not an assumption.** At every cycle the
instrument records `observed_writes` (calls the wrapper saw), `reconciled_writes`
(rows the store accepted) and, where a difference is explained,
`explaining_write` (the ordinal and id of the call responsible).

**Behaviour neutrality is proved, not asserted** (rule 17c). A run with the
observer and a run without it must produce identical per-type tables and identical
admitted streams, as the mechanism instrument's own control did. The neutrality
check must be built to fail: it is tested against a deliberately order-changing
observer, and the test passes only if it fires on that one.

## 4. The result space, fixed in advance

| Outcome | Meaning | Required fields |
|---|---|---|
| **(A) upstream write** | the responsible write is an ingest write (`event_type` other than the cycle's candidate batch), earlier than the cycle's construction. The store held a different candidate *before* scoring. | `explaining_write` names an ingest write |
| **(B) construction write** | the responsible write is a candidate write inside the cycle's candidate batch — the construction path supplied it and `_score_tags` sits on that path. | `explaining_write` names a candidate write |
| **(C-accounted)** | every write in the window was observed **and reconciled**, and no write explains the difference. | `observed_writes == reconciled_writes`, `explaining_write` none |
| **Indeterminate** | the denominator does not reconcile, or the responsible write's stage cannot be located, or the known-positive case is not found. | `observed_writes != reconciled_writes`, or no verdict |

**(C-accounted) is admissible only when the writes reconcile and no call explains
the difference.** Where they do not reconcile the verdict is **indeterminate**,
which is a first-class outcome and may never be folded into (C-accounted) or
counted as a null. An unmeasurable quantity reported as a zero is the fabrication
rule 13(b) names, and a bucket that can absorb an instrument failure will.

The two readings are named with words rather than letters because `C1`, `C2` and
`C3` already name the mechanism brief's controls; a third `C1` would repeat the
label defect rule 8 warns about.

## 5. Predictions, fixed in advance

**P1 — the difference is upstream of the store's admission on most seeds.** For at
least 5 of the 8 failing seeds, the candidate one side holds is **absent from the
other side's write record at that cycle**: it was never offered, rather than
offered and rejected.

**P2 — where a candidate is offered on both sides, it is accepted on both.**
Across all measured seeds, at most 2 arm-seeds show a candidate offered with
identical content and admitted on one side only. If more do, the store's own
admission is a live site and (B) is not the whole story.

**P3 — the located write is an ingest write (A) more often than a construction
write (B).** On the seeds where a write is identified at all, (A) is the verdict on
at least half.

Each of these can fail, and P1, P2 and P3 are not arithmetically entailed by
anything already in the record. P3 in particular is the one that would *not*
flatter the surviving `_score_tags` finding.

## 6. Falsification criteria

**F1 — the observer changes behaviour.** If a run with the wrapper does not
reproduce the unobserved run's per-type tables and admitted streams, the observer
is inadmissible and no verdict may be reported from it.

**F2 — the writes do not reconcile.** At any cycle where
`observed_writes != reconciled_writes`, that cycle's verdict is **indeterminate**.
It may not be reported as (C-accounted), and no seed-level verdict may be
aggregated across an unreconciled cycle.

**F3 — the explaining write is chosen by a search declared after the record is
seen.** The search space is fixed here: **the candidate's write records at the
divergence cycle and at the cycle before it.** Naming a write outside that window,
or re-ordering candidate writes until one looks responsible, invalidates the
verdict.

**F4 — the known-positive case is missed.** The control seed was captured at hash
seeds 0 and 1 and its pools differ at cycles 10, 11 and 12 on arm B. If the
observer cannot locate a write behind **at least one** of those cycles, the
observer is blind to the thing it was built to see, and the instrument is
inadmissible — the same shape of check as F2 in the onset brief, where a control
that cannot fire makes the instrument decoration (rule 25).

**F5 — a null is reported without the denominator.** A report of "no write
explains it" while any cycle is unreconciled is withdrawn rather than explained.

## 7. Controls

- **C1 — known-positive.** The control seed at hash seeds 0 and 1, cycles 10–12,
  arm B: the observer must locate a write behind at least one known membership
  difference. This is the only control here that can fail on a case the record
  already contains, and it is therefore the sharpest.
- **C2 — behaviour-neutrality.** With and without the wrapper, identical per-type
  tables and identical admitted streams; the check is proved to fire against a
  deliberately order-changing observer.
- **C3 — determinism.** Two processes at the same hash seed produce identical
  write records, compared field by field, with the observer-version field set
  aside.
- **C4 — reconciliation.** `observed_writes == reconciled_writes` at every cycle
  reported, with the per-cycle counts committed alongside the verdicts.

## 8. What this will and will not establish

**Will.** For each seed where a verdict is reached: **which write** admitted the
differing candidate, and whether it is an ingest write (A) or a construction write
(B) — that is, whether the pool differed because the store held something else
before scoring, or because the cycle's own construction supplied something else.

**Will not.** It will not re-score D0, revise the onset result, reopen the
mechanism experiment, or modify `organica/`. It will not establish that any write
is *causal* in the counterfactual sense: a located write is a **location**, and
the report may say "this write admitted the candidate", never "this write caused
the divergence". Where (A) holds, the sentence allowed is *the candidate was
admitted by an earlier ingest write, so the construction path did not supply it* —
**not** *`_score_tags` is not order-sensitive*, which is false and already
measured.

**Why this counts as the good outcome.** (A) or (C-accounted) would mean the
answer is **not** `_score_tags`, which is the outcome the current record makes
reachable but does not predict. An instrument whose only possible answer is the
builder it was built to watch measures its own field of view.

## 9. Cost and order of work

| Step | Cost |
|---|---|
| Build the wrapper, the reconciliation fields and the neutrality check | One benchmark, standard library only, no engine change |
| Run: 8 failing seeds × 2 hash seeds, plus the control seed × 2 hash seeds | **18 runs, 0 cached.** The mechanism experiment's 18 runs took 846 s at 4 workers; expect the wrapper to add little. |
| Verification | C2, C3 and C4 first; **F4 before any verdict is read** |
| Write-up | Journal section, a manual finding, a facts-sheet row, a CHANGELOG entry, the artifact and its generated report |

Order matters: **C2 and F4 before any verdict.** An observer that changes the run,
or cannot find a difference the record already contains, is measuring itself.

## 10. What was read, and how far

Read on 2026-11-01, from the frozen engine at `v0.9.0`: `organica/memory.py` — the
method list and the bodies of `store` (244), `_record_tag_counts` (287),
`_record_cooccurrences` (306), `_record_temporal_edges` (321), `record_sleep_cycle`
(443), `prune_sleep_candidates` (452), `recent` (387), `count` (492) and
`latest_sleep_cycle` (431); `organica/sleep.py` — `_store_candidates` (1916) and
its calls into `store`, `record_sleep_cycle` and `_store_single_candidate`, and the
`self.memory.*` read sites at 439, 866, 873, 878 and 898. Read from the record:
`docs/divergence_onset.json`, `docs/DIVERGENCE-ONSET.md`,
`docs/divergence_mechanism.json` (`criteria.P2`, `criteria.F2`),
`docs/DIVERGENCE-MECHANISM-RESULTS.md`, `docs/divergence_cycle_capture.json` and
journal §§74–79. No engine file was modified to write this plan.

---

→ `docs/divergence_onset.json`; `docs/DIVERGENCE-ONSET.md`;
`docs/divergence_mechanism.json`; `docs/DIVERGENCE-MECHANISM-RESULTS.md`;
journal §78; journal §79; `organica/memory.py`; `organica/sleep.py`.

---

## 9. Amendment, pre-registered before F5 ran: the finer split, and a restatement of (B)

**Why this amendment exists.** Writing the F4 result exposed a defect in the
brief's own result space, not in the observer. Bucket **(B)** is defined as *"the
`_score_tags` write is identified"*. **`_score_tags` issues no store call.** It
takes `(freqs, cooc, temporal)`, builds `_TagScore` records, sorts them on
`frequency` and returns the list (`organica/sleep.py:904-922`). There is no write
there to identify, on any seed, in any cycle, ever. Bucket (B) as worded is
therefore **unsatisfiable by construction**, and an instrument that reported it
would be reporting a write that does not exist.

**What (B) is restated to mean, before any seed is measured.** A write emitted by
one of the two builders that consume this cycle's tag scores:
`_build_concepts` and `_build_phrases` (`organica/sleep.py:447-448`). Those are the
only construction steps that take `tag_scores` as an argument; `_build_loops`,
`_build_predictions` and `_build_anomalies` take the graphs, and every higher
layer takes prior candidate structures. So:

> **(B-restated):** the differing candidate's write is emitted by a builder whose
> content derives from this cycle's tag scores — source
> `sleep:concept_candidate` or `sleep:phrase_candidate`.

This is narrower than "construction" and it is the narrowest claim the engine's
call structure supports. It is **not** a causal claim about the scoring function:
those builders also consume the graphs, so (B-restated) locates the write, and
says nothing about which of the builder's inputs made the difference.

**The split.** Every sleep write is labelled on two engine-derived axes:

- **phase**, from the engine's own call structure — whether the call passed
  through `_store_candidates` (a cycle-pool write) or not (a re-store of a
  survivor during natural selection, `organica/sleep.py:453-460`). Read from the
  Python frame stack at the wrapped call; no engine change, no disk patch.
- **type**, from the source tag the engine already stamps: `sleep:<ctype>`.

Labels are therefore `pool:<ctype>`, `restore:<ctype>`, `marker`, `ingest`. The
`pool`/`restore` distinction matters because natural selection re-stores decayed
survivors **through the same per-type writer**, so type alone cannot tell a
candidate built this cycle from one carried over.

**F5, the check this split must pass before any seed is measured.** Run on the
control seed at hash seeds 0 and 1, cycles 10-12, exactly as F4:

1. **Reconciliation first**, as in F4: every affected cycle reconciles on both
   sides, or the observer is inadmissible regardless of labels.
2. **The split is live**: at least **two** distinct `pool:` labels occur in the
   run. A label scheme that collapses to one value measures nothing (rule 13c),
   and this condition can fail.
3. **No attributed candidate is unlabelled**, and none carries two labels.
4. **The outcome is read in the restated space**: (A) ingest write;
   (B-restated) `pool:concept_candidate` or `pool:phrase_candidate`;
   otherwise the write is construction at a named layer; C-accounted and
   Indeterminate unchanged.

**Prediction, recorded before the run.** The F4 control's differing candidates are
`dream_mut_*`, built by `_generate_categorized_dreams`, which consumes
`workflows, processes, meta_concepts, questions, cooc, temporal`
(`organica/sleep.py:575-583`) — **not** tag scores. So the prediction is:

> the control's differing candidates are labelled **`pool:dream`**, i.e. outcome
> **(B-restated) is NOT reached on the control seed**, and the control resolves as
> "construction, Layer 6, not tag-scored".

If instead they come back as `pool:concept_candidate` or `pool:phrase_candidate`,
the prediction is **wrong** and is recorded as wrong. Either result passes F5 if
conditions 1-3 hold: F5 tests the *instrument*, and the label is the measurement.

**Stop condition.** This build closes when F5 passes. No further sub-division of
construction may be added afterwards; a finer split is a new pre-registration.

---

## 10. Pre-registration, committed before the verdict pass ran

**Cells.** The five search cases, with the divergence cycle each already has on
record in `docs/divergence_onset.json`:

| Case | Task | Seed | Arm | Divergence cycle | Entered |
|---|---|---|---|---|---|
| 1 | T1 | 20261125 | B | 12 | 70 |
| 2 | T1 | 20261125 | C | 12 | 70 |
| 3 | T2 | 20261120 | B | 6 | 11 |
| 4 | T2 | 20261120 | C | 6 | 5 |
| 5 | T2 | 20261121 | B | 6 | 23 |

**Hash seeds: 0 and 1**, the pair F4 and F5 ran on.

**Arm C is not standalone.** `run_arm` for arm C requires `admission = prep["support"]`
and `fixed_temporal = <arm B's per-cycle temporal graphs>`; the campaign runs B
first and hands its graphs to C (`benchmarks/formation_utilization.py:1273-1277`).
So a C cell is run as a **staged pair inside one process per hash seed**: B, its
graphs captured, then C reading them. Both stages are observed, and the C cell's
verdict is read from the C run's writes.

**The comparison.** At the recorded cycle, the two hash seeds' write-back windows
are compared by candidate id. A candidate present on one side only is looked for
in that side's write record at the cycle **or the cycle before** (the brief's
window), and must be **absent** from the other side's record in the same window to
count as attributed.

**Reconciliation, first.** A cell is interpretable only if both sides reconcile at
the cycle (`observed == accepted == net`). Otherwise its outcome is
`indeterminate`, whatever it might have attributed.

**The outcome space, and no fifth bucket:**

| Outcome | Condition |
|---|---|
| `no_difference_at_pair` | the windows are identical at this hash-seed pair |
| `A` | every difference attributed, all labels `ingest` |
| `B_restated` | every difference attributed, at least one label tag-scored |
| `construction_other:<labels>` | every difference attributed, none tag-scored |
| `C_accounted` | differences exist, none attributed, writes fully reconciled |
| `indeterminate` | unreconciled, or **partially** attributed |

`no_difference_at_pair` is declared here, before the run, because it is a real
possible result and must not be silently folded into `C_accounted`: if the
divergence does not reproduce at hash seeds 0 and 1, the cell measured nothing and
says so. A partial explanation is `indeterminate`, never "mostly explained".

**Stop condition.** This pass runs once, over these five cells. No cell is added,
dropped or re-run on the basis of its outcome, and no sixth bucket is introduced.

