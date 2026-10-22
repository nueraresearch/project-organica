# Phase G Findings: The 90-Day Longitudinal Study, Audited Before It Began

> **Date**: 2026-10-21
> **Phase**: G (External Real-World Soak & Endurance Testing)
> **Scope**: Audit of the study infrastructure left in place by the 2026-10-20 Antigravity session, plus the substrate and stream corrections needed to make the study meaningful.
> **Status**: Infrastructure repaired. Study relaunched 2026-10-21 with a corrected event stream. One architecture amendment is proposed but **not** applied (see §7).

---

## 0. Executive summary

The 90-day longitudinal study had been running unattended for roughly 10.5 hours across four daemon runs and had produced **no usable data about Generations 5 through 8**. It was instrumenting a degenerate organism.

Four independent defects were found, each of which alone would have invalidated the study:

| # | Defect | Measured evidence | Severity |
|---|---|---|---|
| 1 | The study event stream **cannot** reach Generation 5 | 0 theories / 0 questions across 670 logged cycles; 0 contradictions anywhere | Fatal to the study |
| 2 | `tag_frequencies()` did a full-table scan every cycle | 4,826 ms/cycle at 1.65M rows, growing linearly | Fatal to a 90-day run |
| 3 | The monotonic cycle counter reset mid-run | `sleep_cycle` went 319 → 4 inside one run | Corrupts every time series |
| 4 | `start_organica.bat` truncated `organica.log` on restart | `>` redirect on a FileHandler-owned file | Destroys the longitudinal record |

Plus a substrate projection that makes the study infeasible as designed:

> The candidate table grows ~3,300 rows/cycle. At the configured 30 s interval a 90-day run is 259,200 cycles → **~370M rows ≈ 210 GB**, against 229 GB of free disk — while the O(n) scan would have cost ~12 minutes *per cycle* by the end.

All four defects are now fixed and covered by tests. The study has been relaunched.

**Addendum (2026-10-22).** Two further studies were run against the corrected build, both answering questions the 90-day study cannot:

- **§14 — the cold-start question.** *Would Generation 1 have built out the generations above it with no assistance and no code changes?* Answered empirically: G1, G4 and G6–G8 bootstrap unassisted; **G5 never does**, and the cause is proven causal rather than guessed.
- **§17 — the ablation study.** *Which mechanisms are actually doing the work?* Eleven conditions, pre-registered before the run, with a mechanism-verification stage run before any interpretation. The answer is uncomfortable and useful: sleep and the graph are foundational, **lineage is pure governance with zero behavioural effect**, and the attention economy changes what it selects without changing what the organism achieves.

Both studies are also summarised in `docs/USER-MANUAL.md` §8.1 and §8.2.

---

## 1. State reconstruction (what was actually there)

The Antigravity session of 2026-10-20 left:

- `run_continuous.py`, `metrics.py`, `dashboard_ui.py`, `observation/metrics_observer.py` — modified, uncommitted.
- `start_organica.bat`, `run_daily_observer.bat`, `run_weekly_monthly.bat`, `run_dashboard_and_api.bat` — new, uncommitted.
- Commit `3ac54a7` "Baseline observation infrastructure for 90-day longitudinal study".
- A running daemon that had stopped at 23:30:32 local on 2026-10-20 — **down for 9h 24m** at the time of this audit.

Four daemon runs are visible in the log, identified by the `cycle` counter resetting to 0:

| Run | Window (local MDT) | Cycles | Note |
|---|---|---|---|
| 1 | 12:55:14 → 12:56:34 | 3 | died after ~80 s |
| 2 | 12:56:34 → 21:47:40 | ~314 | the long run |
| 3 | 21:47:40 → 23:28:33 | ~178 | **cycle counter reset mid-run** |
| 4 | 23:28:33 → 23:30:32 | 5 | final; the new instrumented harness |

**The headline "670 cycles" in `docs/health_report_20261020.txt` is not a cycle count.** It is the number of parsed log lines (1,158 across 4 runs), and the report was generated at 19:11 — not at the end of the run. The database's own count is 504 cycles. The two figures disagree because the log counter (`cycle`) resets per process while the database counter (`sleep_cycle`) was, itself, broken (see §4).

---

## 2. Finding 1 — The G5 gap (the important one)

### 2.1 The claim under test

`CHALLENGE.md` lists nine emergence targets. G5 reads:

> **G5: Epistemic Tension** — Competing hypotheses coalesce into Theories; normalized Shannon entropy quantifies structural uncertainty in Questions.

`docs/validation_report.json` (Phase F) reports `theories: 1, questions: 1` for the Developer Workflow domain and **zero** for the other three domains. The long-running daemon reported `theories: 0, questions: 0` on every cycle.

### 2.2 Mechanism

Layer 5 (`SleepService._form_theories_and_questions`, `organica/sleep.py:1423`) groups hypotheses by subject and skips any subject with fewer than two:

```python
for subject, hyps in by_subject.items():
    if len(hyps) < 2:
        continue
```

A subject therefore needs **two competing expectations** to produce a Theory. A hypothesis is `subject → expectation`, formed from workflow component pairs and process cycles. In the study's event stream every subject kept exactly one successor, so no subject ever reached two.

### 2.3 How this was established

Not by reading the code and concluding — by instrumenting the precondition and comparing it against production.

`benchmarks/g5_gap_diagnostic.py` computes, per cycle, the **ceiling** on producible theories (the number of subjects carrying ≥2 non-structural hypotheses, which is precisely the engine's own grouping rule) and compares it to what was actually produced. The ceiling was saturated in **10/10 cycles** for every stream tested, which means the gate explains the outcome completely — no other blocker exists.

| Stream | Peak hypotheses | Distinct subjects | Subjects with ≥2 hyps | Theories | Questions | Contradictions |
|---|---|---|---|---|---|---|
| **Original study stream** | 2 | 2 | **0** | **0** | **0** | **0** |
| Phase F Developer Workflow (control) | 11 | 7 | 1 | 1 | 1 | 683 |
| Replacement candidate | 15 | 10 | 1–2 | 1 | 1 | 1,017 |

### 2.4 The second-order consequence: Law V was dead too

Zero competing expectations means zero contradictions. Contradiction count feeds Shannon entropy, which feeds EIG. Measured on the original stream: `contradiction_total = 0`, question uncertainty `0.000`, hypothesis confidence pinned at `1.0`.

**The curiosity economy never engaged.** Dreams, investigations and experiments still appeared (3–8 per cycle) but they were generated from analogy dreams over Layer-1 concepts, not from genuine epistemic tension. The study would have recorded a flat G4 line for 90 days while producing hundreds of pages of confident-looking telemetry about a mechanism that was never running.

### 2.5 Correction

`benchmarks/stream_sweep.py` scored four candidate streams on G5 sustainment, question uncertainty and experiment priority over 24 cycles with the daemon's own rotating-slice injection:

| Candidate | G5 sustainment | Mean uncertainty | Mean EIG | Mean contradictions |
|---|---|---|---|---|
| **branch_developer_and_defect** (selected) | **0.70** | 0.695 | 1.314 | 1,288 |
| phase_f_pack_all | 0.61 | 0.608 | 1.261 | 955 |
| branch_developer_only | 0.61 | 0.609 | 1.261 | 1,632 |
| branch_four_domains | 0.57 | 0.565 | 1.234 | 780 |

The selected stream keeps the same branch-point subject leading to **both** a positive and a negative outcome, so support and contradiction both accumulate and uncertainty stays non-zero.

**Counter-intuitive result worth recording:** adding the ecology and robot domains made things *worse* (0.70 → 0.57). More domains mean more workflow structures competing for the same 15-slot hypothesis budget, and the competitor hypothesis that Layer 5 needs gets truncated away. See §7.

---

## 3. Finding 2 — The substrate could not survive a 90-day run

`benchmarks/substrate_probe.py` measured the live `memory.db` directly.

```
db size          : 942.1 MB
events           : 1,654,637
  experience     :     4,556
  sleep          : 1,650,081
freelist pages   : 0 (0.0% of file — the file is live data, not unreclaimed deletes)

per-cycle substrate read costs (ms):
  tag_frequencies__FULL_TABLE_SCAN          4826.27
  recent_4000_sleep                           13.33
  load_temporal                                6.14
  load_cooccurrences                           1.29
  recent_4000_any                             11.21
  TOTAL per cycle                           4858.24
```

`MemoryService.tag_frequencies()` ran `SELECT tags FROM events` — a full scan of every row, every cycle. It was **99.7% of per-cycle cost** and grew linearly with the table. Everything else was milliseconds.

Projection at the configured 30 s interval (259,200 cycles):

- Events: ~370M rows, **~210 GB** against 229 GB free.
- `tag_frequencies()`: ~12 minutes **per cycle** by the end of the run.
- The daemon would fall permanently behind and the run would be meaningless.

Note the 362:1 ratio of internal reflection to experience. Law III was *not* violated — sleep events are correctly excluded from the co-occurrence and temporal graphs (`organica/memory.py:98`) — but the substrate accumulated every dead candidate forever.

---

## 4. Finding 3 — The cycle counter reset mid-run

`_count_prior_cycles` recovered the cycle number by scanning the **most recent 500 sleep events** for a `_sleep_meta` marker:

```python
meta_events = self.memory.recent(n=500, event_type="sleep")
```

Once the candidate population exceeded ~500 rows per cycle, the marker fell outside its own window and the function returned 0 — so the counter reset to 1 in the middle of a run. The log shows it plainly: `sleep_cycle` ran `... 316, 317, 318, 319, 1, 2, 4, 5, 6, 7, 8`.

Confirmed against the database, which contained 1,162 `sleep:meta` rows with values `1..496` then `1..8`, while the live 500-event window contained **zero** meta rows (all 500 were `sleep:loop_candidate`).

This is a self-referential feedback loop: more cognition → more candidates → the window overflows → the counter breaks. It silently corrupts the time axis of every longitudinal measurement.

---

## 5. Finding 4 — The log was truncated on every restart

`start_organica.bat` ended with:

```bat
start "Organica" /b "%PYTHON%" "%~dp0run_continuous.py" > "%~dp0organica.log" 2>&1
```

`organica.log` is owned by the daemon's own `logging.FileHandler`, opened in **append** mode. The `>` redirect therefore (a) truncated the file at every launch, destroying the longitudinal record, and (b) pointed stdout at the same file the FileHandler owns, which would have written every line twice.

---

## 6. Finding 5 — The observation pipeline had never run

- `snapshots/weekly/weekly_20261021.json` contained exactly `{}` — `weekly_aggregate()` returned `{}` on an empty parse and the writer serialized it anyway.
- `_detect_events()` searched for pipe-delimited `theory_birth=…` tokens from a **dead log format**; the log has been one JSON object per line for some time. The event journal had therefore never been created.
- `daily_snapshot()` computed "today" as the last **two cycles** — a 30-second delta labelled `births_today`.
- `development_velocity(days=7)` took the last 7 **cycles** and divided by 7 **days** — a ~5,760× understatement.
- `event_type_counts()` counted keywords in raw log text, so `"dream"`, `"experiment"` and `"hypothesis"` scored 1,158× each (one per cycle line of JSON boilerplate) while the real signal (`auth`, `session`) scored 5.

All repaired; see §8.

---

## 7. Proposed architecture amendment — NOT applied

The G5 handoff is fragile in a way that is structural, not accidental.

`MAX_HYPOTHESES = 15` is applied *after* an alphabetical sort:

```python
results.sort(key=lambda h: (h.subject, -h.confidence))
return results[:self.MAX_HYPOTHESES]
```

Two consequences, both measured:

1. **Selection is by alphabetical position, not merit.** Which hypotheses survive is decided by where their subject falls in the alphabet, not by confidence, support, contradiction, or EIG.
2. **Layer 2 markers crowd out Layer 5's inputs.** Roughly a third of the 15 slots go to `high_structural_significance` meta-concept markers, which Layer 5 explicitly discards before grouping. In the replacement stream, 15 hypotheses over 10 subjects left only 5 subjects with a *directional* hypothesis at all, and typically 0–1 with a competitor.

This is why G5 sustainment is ~70% and not ~100%, and why adding domains made it worse.

**Proposed fix (for the Phase A unfreeze, not applied here):** make the Layer-4 selection merit-aware — order by `(support + contradiction)` or by EIG rather than by subject name, and reserve a fraction of the 15 slots for directional hypotheses so meta-concept markers cannot starve Layer 5.

> **CORRECTED by §16.4.** The `no_truncation` ablation (hypothesis cap 15 → 200) changes **nothing**: G5 still emerges at cycle 2 with the same populations. Truncation is therefore **not** what blocks G5 from emerging — it only affects how many competitors survive a G5 state, and hence the duty cycle. Reclassified from "G5 unblocker" to "duty-cycle improvement". The thing that actually blocks G5 emergence is the *share-based confidence formula*, measured in §16.3.

**Why it was not applied:** Phase A froze the cognitive primitives at v1.0, and this changes which hypotheses compete — i.e. it changes cognition. The master's plan gates Generation 9 on exactly this kind of validation, so the amendment should be decided and recorded, not slipped in during a substrate repair.

---

## 8. What was changed

### Substrate (`organica/memory.py`, `organica/sleep.py`)

| Change | Purpose | Guarantee |
|---|---|---|
| `tag_counts` table, maintained incrementally | Removes the O(n) full scan | Result proven **identical** to the legacy scan |
| `sleep_cycles` table | Authoritative monotonic cycle counter | Cannot reset; survives restarts |
| `idx_events_type_time`, `idx_events_source` | O(log n) `recent()` | Behaviour unchanged |
| `prune_sleep_candidates(keep=20000)` | Bounds disk growth | Never deletes experience events or `sleep:meta`; leaves the newest 4,000 events (the organism's working memory) byte-identical |
| Backfill on open | Existing databases keep working | One-time; verified equivalent |

### Study configuration

| File | Change |
|---|---|
| `run_continuous.py` | Replacement branch-structured `STUDY_STREAM`; `EVENTS_PER_CYCLE = 8`; per-cycle retention; `substrate_rows_pruned` in the summary |
| `start_organica.bat` | `organica.log` appended, never truncated; stdout mirror moved to `console.log` |
| `.gitignore` | `*.log`, `logs/`, `INTERVAL` — unbounded run artifacts out of version control |
| `metrics.py`, `observation/metrics_observer.py`, `dashboard_ui.py` | Observation pipeline repairs (§6) |

### New artefacts

- `benchmarks/g5_gap_diagnostic.py` — the G5 gate instrumented and proven.
- `benchmarks/substrate_probe.py` — live-substrate read costs and page accounting.
- `benchmarks/substrate_scaling_analysis.py` — latency-vs-cycle fit from the real log.
- `benchmarks/stream_sweep.py` — candidate stream selection.
- `tests/test_substrate_equivalence.py` — 8 tests proving the substrate changes are behaviour-preserving.
- `docs/g5_gap_diagnostic.json`, `docs/substrate_probe.json`, `docs/stream_sweep.json`, `docs/substrate_scaling_analysis.json`.

**Test status: 13 passed.**

---

## 9. Run-1 evidence retained

Nothing from the first attempt was discarded:

- `logs/organica_run1_20261020.log` — 1,158 cycle records.
- `logs/continuous_run1_stale.log` — 1,515 errors, all from an *older* build (`_run_sleep_cycle` missing; fixed in commit `52907cc`). Stale, kept for completeness.
- `memory.db.run1_20261020` — 942 MB, 1.65M rows, the substrate described in §3.

---

## 10. Finding 6 — G5 is an oscillation, not a state

After the corrected study was launched (2026-10-21 09:08) it ran 101 cycles
before the first audit of its own output. The trajectory is the most
interesting result in this document:

```
cyc | hyps | th | q  | contra | dur_ms | subjects with >=2 non-structural hypotheses
  1 |   13 |  2 |  2 |   1047 |    615 | 5
  5 |   13 |  2 |  2 |   1141 |    793 | 4
 10 |   13 |  2 |  2 |   1706 |   3792 | 4
 15 |   13 |  2 |  2 |   2296 |  13583 | 4
 20 |    6 |  0 |  0 |      0 |   9093 | 0   <-- G5 collapsed
 25 |    5 |  0 |  0 |      0 |  15718 | 0
 35 |    5 |  0 |  0 |      0 |   8574 | 0
 50 |   15 |  3 |  3 |   7186 |   1709 | 5   <-- G5 returned
 65 |   14 |  2 |  2 |   7833 |    907 | 5
 80 |    4 |  0 |  0 |      0 |    448 | 0   <-- collapsed again
 95 |   14 |  2 |  2 |  11180 |   8657 | 5
 97 |    6 |  0 |  0 |      0 |   7854 | 0
100 |    6 |  0 |  0 |      0 |   6892 | 0

54 of 101 cycles carried at least one Theory.
```

### 10.1 The mechanism

Hypothesis confidence is computed as a *share* of the subject's outgoing flow:

```python
support      = temporal[subject][expectation]
total_flow   = sum(temporal[subject].values())
contradiction = max(0, total_flow - support)
confidence    = support / (support + contradiction)
```

and a hypothesis is discarded when `confidence < DEATH_THRESHOLD (0.15)` and it has at least 3 observations.

A subject with many successors therefore *dilutes* each of its minority expectations below 0.15 and loses them. The minority expectation survives only when the subject has roughly two successors, so that the minority's share is near 0.5.

Measured at cycle 10, the competitor hypotheses sat right on the knife edge:

```
developer  conf 0.191  support 89  contradiction 376
modified  conf 0.168  support 50  contradiction 248
report    conf 0.170  support 46  contradiction 224
suite     conf 0.180  support 83  contradiction 379
```

Every one of these is between 0.15 and 0.20. As the temporal counts grow, the share of the minority successor falls below 0.15, the competitor is pruned, the subject is left with a single expectation, and G5 dies. When the population rebuilds from a smaller base, the shares climb back above the threshold and G5 returns.

At cycle 98 the surviving hypothesis set had been rebuilt from scratch — support counts of 5–12 with zero contradictions — confirming that the collapse is a rebuild, not a decay.

### 10.2 What this means for the study

**This is a finding, not a defect to patch.** A 90-day longitudinal study of an organism whose epistemic tension *collapses and regenerates* is far more informative than a flat line, and it maps directly onto the belief-revision narrative the health dashboard already tried to tell. The oscillation is measurable, periodic, and driven by a single named threshold.

It does mean the study's headline metric should be **G5 sustainment over a rolling window**, not "theories > 0" per cycle, and it means any claim of "Generation 5 is present" should be stated as a duty cycle.

**It also sharpens the architecture amendment in §7.** The knife-edge behaviour comes from `DEATH_THRESHOLD` interacting with share-based confidence. Two candidate amendments:

1. Make Layer 4's selection merit-aware (already proposed), so a competitor with genuine evidence is not truncated away before it can be evaluated.
2. Consider whether a minority expectation should be pruned for *low share* at all, or only for lack of evidence. Under the current rule, a hypothesis can be extinguished by the very success of its sibling.

Neither is applied. Both change cognition and belong to the Phase A unfreeze.

---

## 11. Finding 7 — One fsync per candidate dominated the cycle

Profiling one sleep cycle against a copy of the live substrate:

```
4.546 s total
  3.032 s  {method 'commit' of 'sqlite3.Connection' objects}   (1,023 calls)
  1.095 s  {method 'execute' of 'sqlite3.Connection' objects}
```

`MemoryService.store()` committed on every call, and a cycle persists ~1,000 candidates (the population plus every decayed survivor re-stored by natural selection). **Two thirds of the cycle was disk sync, once per candidate.**

Fixed with a `MemoryService.batch()` context manager that groups writes into one transaction and rolls back the block if it raises. Two call sites in `SleepService.run()` now use it.

| | before | after |
|---|---|---|
| sleep-cycle wall time (live substrate, 21,049 events) | ~4,500 ms | **263 ms** |
| commits per cycle | 1,023 | 2 |

**17× faster**, and the cycle is now dominated by actual cognition rather than by fsync. Tests: 17 passed.

---

## 12. Finding 8 — Law II holds, but nothing in the repo was measuring it

Law II claims every primitive traces an unbroken chain back to Generation 0 experience events, and `CHALLENGE.md` makes it one of the nine emergence targets. **No code verified this.**

- `SleepService.get_ancestry()` walks only `_load_prior_candidates()` — the newest 4,000 sleep events — and stops at `max_depth=7`. It cannot reach a Generation 0 experience event, because experience events are not candidates.
- `cross_domain_validation.py` checks only that each `parent_id` is present among *other candidates in the same window*. It would have reported `100.0%` even if no chain ever touched raw experience.

`benchmarks/lineage_audit.py` measures the real thing: walk every candidate's `parent_ids` to a Layer 1 anchor, then check that anchor's grounding tags (`members` / `path` / `source`+`target` / `expected`+`observed`) actually appear in a Generation 0 experience event. It reports *unverifiable* (chain broken by eviction) separately from *ungrounded* (chain resolves but the root has no G0 tag), because conflating them hides which failure actually occurred.

| store | G0 events | candidates needing lineage | GROUNDED | unverifiable | ungrounded |
|---|---|---|---|---|---|
| live (bounded retention) | 2,344 | 138 | **138 (100.0%)** | 0 | 0 |
| run-1 archive (unbounded) | 4,556 | 225 | **225 (100.0%)** | 0 | 0 |

**The invariant is true.** The defect was in the verification, not the architecture — and the repo's own check was a proxy that would have passed regardless. This also retires a worry: bounding the candidate store for endurance does *not* break ancestry, because candidates are re-emitted every cycle so the working set stays populated.

The remaining exposure is presentational: the papers assert the claim while the shipped check does not test it. `benchmarks/lineage_audit.py` now does.

---

## 13. Finding 9 — Experiments are generated but never executed

Every consumer of `report.experiments` only *reads* it: `benchmark_suite.py` prints the top priority, `cross_domain_validation.py` records the peak, the domain examples print the payload. **Nothing maps an experiment to an injected event, and nothing observes whether the belief it targeted actually moved.**

This has two consequences:

1. **Law IV is never exercised.** "A dream can only become a belief if an external experiment generates empirical events that confirm its structure." With no executor, no dream or hypothesis can ever be confirmed by experiment. Beliefs only ever change through the ordinary stream.
2. **A Question can never be closed.** Its uncertainty is recomputed from a static stream, so it rises and falls with the stream's composition rather than with any resolution. The study therefore measures *epistemic tension*, not *epistemic resolution*.

The 90-day study is still worth running — tension is the interesting quantity, and §10 shows it oscillates for identifiable reasons. But any claim that Organica "actively experiments" is currently a claim about *candidate generation*, not about *action*. An executor is the missing piece, and it is a substantial design task: it needs a probe format, a mapping from probe to injected event, and a belief-delta measurement.

---

## 14. Finding 10 — The cold-start question, answered empirically

> *"Would Generation 1 have built out the generations above it, with no assistance and no code changes on our side?"*

This is the project's long-horizon question, and the 90-day study **cannot** answer it, because the current setup contains assistance at four levels that are easy to miss:

1. **Pre-seeding.** The daemon loads 48 events into an empty substrate *before* the first sleep cycle. A newborn organism does not arrive with a populated graph.
2. **An engineered branch point.** The study stream is hand-designed so one subject is followed by both a positive and a negative outcome — exactly what G5 needs.
3. **Hand-coded domain knowledge.** `memory.py` excludes `"test"` and `"file"` as tags, with the comment *"too generic for a dev env — we'll revisit this"*. A domain decision baked into the substrate, which Law I forbids.
4. **Fixed sampling.** Exactly 8 events per cycle, in a fixed rotation, with a 3-event temporal lookback.

`benchmarks/cold_start.py` removes these one at a time and records when each generation first appears. It never edits the engine — ablations are applied in-process by subclassing or rebinding module attributes.

### 14.1 Results — cycles until each generation first appears (`-` = never)

| condition | G1 conc | G1 loops | G1 pred | G2 meta | G2 proc | G3 wf | G4 hyp | **G5 th** | **G5 q** | G6 dr | G7 inv | G8 exp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `baseline` (seeded, engineered) | 1 | 1 | 1 | 2 | 2 | 2 | 2 | **2** | **2** | 2 | 2 | 2 |
| `no_branch` (seeded, unbranched) | 1 | 5 | 1 | 2 | 6 | 6 | 4 | **–** | **–** | 2 | 2 | 2 |
| `cold_start` (no seed, 1/cycle) | 6 | 8 | 5 | 9 | – | – | 9 | **–** | **–** | 9 | 9 | 9 |
| `cold_start_unbranched` | 6 | – | 8 | – | – | – | – | **–** | **–** | – | – | – |
| `real_git_history` (no seed, real stream) | 5 | 13 | 5 | 12 | – | – | 12 | **–** | **–** | 12 | 12 | 12 |
| `no_truncation` (hypothesis cap 15→200) | 1 | 1 | 1 | 2 | 2 | 2 | 2 | **2** | **2** | 2 | 2 | 2 |
| `no_dev_stopwords` | 1 | 1 | 1 | 2 | 2 | 2 | 2 | **2** | **2** | 2 | 2 | 2 |
| `wide_lookback` (temporal window 3→30) | 1 | 1 | 1 | 2 | 2 | 2 | 2 | **–** | **–** | 2 | 2 | 2 |

40 cycles per condition. Full telemetry in `docs/cold_start.json`.

### 14.2 The answer

**Partly yes — and the part that fails is specific.**

- **G1 bootstraps unassisted.** From a blank substrate, one event at a time, concepts/loops/predictions appear at cycle 5–8. No seed needed.
- **G4 and G6–G8 bootstrap unassisted.** Hypotheses at cycle 9–12; dreams, investigations and experiments alongside them.
- **G2 processes and G3 workflows did not emerge** from a 1-event-per-cycle stream in 40 cycles. A 2–3 cycle in the temporal graph needs the same tags to recur in order, and at that sampling rate the edges are too thin.
- **G5 never emerged from any unengineered stream.** Not once, in any condition without the engineered branch point — while that same condition reached G1, G4, G6, G7 and G8.

So the honest summary is: **the ladder mostly builds itself from nothing, except the generation that makes the project interesting.** G5 is the one rung that needs a cooperative stimulus.

### 14.3 The mechanism, confirmed causally

Confidence is a hypothesis's **share** of its subject's outgoing flow:

```
confidence = support / (support + contradiction)
```

A subject with many successors therefore dilutes every minority expectation below `DEATH_THRESHOLD = 0.15`, and the competitor is pruned before Layer 5 can see it. In a realistic stream every subject has *many* successors, so no subject ever has exactly two.

The `wide_lookback` ablation proves this causally. Widening the temporal window from 3 events to 30 — **changing nothing else** — destroys G5 completely, while the baseline reaches it at cycle 2. More memory context makes the organism *less* able to hold two beliefs, because a wider window spreads each subject's outgoing flow over more successors.

This also maps onto the working-memory literature: the architecture's competence at G5 depends on a **narrow** temporal window. That is a fragility, and it is measurable.

### 14.4 A correction to §7

§7 proposed that Layer 4's alphabetical truncation was "the main reason G5 sustains at ~90–100% rather than 100% with headroom." **The `no_truncation` ablation contradicts that.** Raising the hypothesis cap from 15 to 200 changes *nothing* — G5 still appears at cycle 2 with the same populations. Truncation affects how many competitors *survive* a G5 state (and therefore the duty cycle), but it is **not** what blocks G5 from emerging at all. The §7 amendment stands as a duty-cycle improvement, not as a G5 unblocker, and is reclassified accordingly.

### 14.5 What this implies for the architecture

Two findings point the same way, and both argue for **simplification** rather than more layers:

1. **Belief should be a posterior, not a share.** A Laplace- or Beta-smoothed posterior over each subject's successors would keep a genuinely split belief alive (a 50/50 split across 20 observations should stay near 0.5, not decay below 0.15 and die), would make the lookback width irrelevant, and would remove much of the need for engineered stimuli. It is also *more* human-like: human belief revision is evidence accumulation against a prior, not a normalised ratio. It is a one-formula change.
2. **G8 needs an executor.** If experiments were actually run — probe a discriminating context, inject the outcome, measure the belief delta — the organism would *generate its own competing expectations* from its own uncertainty. That is the self-build loop: the engineered branch point becomes unnecessary because the organism manufactures its own. This is the largest remaining gap (§13), and it is the one that would make "the simplest architecture" actually simplest.

**Caveat on power:** the `real_git_history` condition used 8 commit messages, because this repository has only 8 commits so far. That condition is under-powered and should be re-run on a larger, genuinely independent history (a mature repository, a system log, a chat corpus) before the conclusion is treated as settled. The unbranched-stream conditions do not have this weakness, and they agree.

---


1. **Why did the daemon stop at 23:30:32? — CLOSED.** It was terminated by a person, not a crash. The run-1 log ends on a clean cycle summary with **zero** tracebacks and **zero** ERROR-level records (a Python unhandled exception would have written a traceback to `organica.log`, because the old launcher redirected stderr there with `2>&1`). The PowerShell history contains explicit kills — `Stop-Process -Id 34488 -Force` and `Get-Process python | Where-Object {$_.Id -in @(28144, 33932)} | Stop-Process -Force` — plus repeated relaunches of `run_dashboard_and_api.bat`, which is what produced the four separate runs in the log. No sleep/wake/shutdown events fall in the window either. **504 cycles, zero errors: the daemon is stable.** What it lacks is supervision (see §15).
2. **Architecture amendment (§7)** — decide and record before Generation 9.
3. **Report G5 as a duty cycle, not a boolean.** §10 shows the organism oscillates between a G4 fixed point and a G5 state (54/101 cycles carried a Theory). Any downstream claim of "Generation 5 present" should be stated as a duty cycle over a rolling window.
4. **Lineage claim strength — RESOLVED (§12).** The invariant holds at 100% and is now measured by `benchmarks/lineage_audit.py`. The outstanding work is to replace the proxy check in `cross_domain_validation.py` with the real audit, so the published report and the shipped verification agree.
5. **No experiment executor (§13).** G8 experiments are generated and then only printed. Until something executes a probe and measures the belief delta, "active experimentation" describes candidate generation, not action, and no Question can ever be closed. This is the largest remaining design gap.
6. **Working memory is sized in events, population in candidates.** At ~3,300 candidates/cycle the 4,000-event window covers barely more than one cycle, so natural selection evaluates a partial and arbitrary slice of the prior population. Same freeze caveat as §7.
7. **`dream_counts_over_time()` keys by `cycle`**, which is not unique across daemon restarts — lossy for the same reason as §1.

---

## 15. Making the study survive 90 days

The daemon is stable but unprotected. The launcher is `start /b`, a child of a transient console, and the machine's own history shows broad `Get-Process python ... | Stop-Process -Force` sweeps — any stray kill, console close, or reboot ends the study silently, which is exactly what happened to run 1.

A Windows Scheduled Task solves this: it survives console close and logoff, and it restarts the daemon if it exits.

```powershell
$action  = New-ScheduledTaskAction -Execute 'C:\Users\monte\.local\bin\python.exe' `
                                   -Argument 'C:\Users\monte\anti\project-organica\run_continuous.py' `
                                   -WorkingDirectory 'C:\Users\monte\anti\project-organica'
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
                                     -RepetitionInterval (New-TimeSpan -Minutes 1) `
                                     -RepetitionDuration (New-TimeSpan -Days 95)
$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
                                          -ExecutionTimeLimit (New-TimeSpan -Days 95) `
                                          -StartWhenAvailable -DontStopIfGoingOnBatteries `
                                          -AllowStartIfOnBatteries
Register-ScheduledTask -TaskName 'OrganicaStudy' -Action $action -Trigger $trigger `
                       -Settings $settings -Description 'Project Organica 90-day longitudinal study' `
                       -RunLevel Highest
```

To stop it later: `Stop-ScheduledTask -TaskName 'OrganicaStudy'` and `Unregister-ScheduledTask -TaskName 'OrganicaStudy'`.

**Note on the interaction with the log:** the scheduled task writes to `organica.log` through the daemon's own append-mode FileHandler, and the counter is now monotonic across restarts, so repeated relaunches are safe. Before this fix, a relaunch would have truncated the log and reset the counter.


---

## 16. Running the study

```bash
cd C:\Users\monte\anti\project-organica

# 1. Start the daemon (appends to organica.log; never truncates it)
start_organica.bat

# 2. Watch it
tail -f organica.log            # PowerShell: Get-Content organica.log -Wait -Tail 20

# 3. Daily / weekly / monthly snapshots
run_daily_observer.bat
run_weekly_monthly.bat

# 4. Dashboard + Inception API
run_dashboard_and_api.bat
```

Useful checks:

```bash
# Is it alive, and is the cycle counter monotonic?
python -c "import ctypes,os; print(os.path.getsize('organica.log'))"

# Re-derive the G5 duty cycle from the log
python benchmarks/g5_gap_diagnostic.py --cycles 10
```

The daemon writes one JSON summary per cycle to `organica.log`. The fields that matter for this study are `theories`, `questions`, `contradiction_total`, `duration_ms` and `substrate_rows_pruned`.
---

## 17. The ablation study — which mechanisms are doing the work?

> *"The biggest risk for Organica isn't 'it doesn't work'. The biggest risk is: it appears to work because one hidden subsystem is doing all the real cognitive work."*

### 17.1 Why this study, and why it is not the same as §14

§14 asked *how much assistance does the organism need?* This asks the complementary and less flattering question: **of the mechanisms that are present, which ones are actually load-bearing?** A project whose stated goal is "the simplest possible architecture that emulates living human learning and memory perfectly" cannot answer that by asserting that every layer matters. The only way to find the ornament is to remove things and measure.

It is also the direct answer to the owner's fear that the project might be "too easy" — that it appears to work because one hidden subsystem is doing the work, or because the organism merely reflects the designer's assumptions back at them.

### 17.2 Method

Eleven conditions: a full-system reference (`O_FULL`) and ten ablations, each removing or replacing exactly one mechanism.

| ID | Ablation | What changes |
|---|---|---|
| **A** | No Sleep | all consolidation, synthesis and dream generation disabled |
| **B** | No Lineage | every candidate stored with `parent_ids` stripped |
| **C** | No Curiosity | EIG ranking and investigation prioritisation disabled (Layers 7–8) |
| **D** | No Falsification | no decay, no extinction, no belief revision; death threshold disabled |
| **E** | No Dreams | completion, analogy, mutation and conditional dreams disabled |
| **F** | No Hypothesis Layer | Generation 4 bypassed; Theories/Questions built directly from Workflows |
| **G** | No Questions | Question creation disabled, Theories kept |
| **H** | Random Curiosity | EIG ranking replaced by a random ordering of the same candidates |
| **I** | Random Sleep | every layer's output replaced by random structures of the same count |
| **J** | Memory Without Structure | raw events stored; no co-occurrence, no temporal edges |

Every ablation is applied **in-process** by subclassing `SleepService` / `MemoryService`. The engine source is never edited, so the running 90-day study is untouched and every condition provably executes the same cognitive code.

**Stimulus and protocol.** The full study stream, ingested 8 events per cycle in the same rotation as the daemon, for **300 cycles** per condition — the maturity level at which the ablation organism's structure set matches the live study's (13 hypotheses, 1 theory, 8 dreams against the daemon's 13 / 1 / 8 at 3,400+ cycles).

**Scoring is forward-looking.** Before each of the last 10 cycles' events are ingested, the substrate graph and the organism's current Layer-1 predictions are snapshotted; the events are then ingested and the snapshot scored against what actually happened. The organism is always predicting events it has not yet seen.

**Pre-registration.** Predictions for all ten ablations were written down and committed *before* the run (`docs/ABLATION-PREREGISTRATION.md`). Six measurement defects were found afterwards and are disclosed in place; **no prediction was revised**. Two specified metrics — `CY` (questions resolved ÷ generated) and `EIG*` (entropy removed by an experiment) — are structurally unmeasurable here, because nothing resolves a Question and nothing executes an experiment. They are excluded from the aggregate rather than zeroed.

### 17.3 The full system, for reference

| PA | PA_sub | IP | SCR | SS | LC | CD | NSR |
|---|---|---|---|---|---|---|---|
| 0.191 | 0.377 | 0.488 | 0.018 | 0.520 | 1.000 | 12.228 | 0.874 |

109 surviving structures; 13 hypotheses, 1 theory, 1 question, 8 dreams, 5 investigations, 5 experiments — **identical to the live daemon's population**.

### 17.4 Results

Per-metric deltas (full system minus ablated). This table, not the aggregate, is the result:

| cond | PA | PA_sub | IP | SCR | SS | LC | CD | NSR |
|---|---|---|---|---|---|---|---|---|
| A | 0.191 | -0.058 | 0.488 | n/a | n/a | n/a | n/a | n/a |
| B | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | **1.000** | 0.000 | 0.000 |
| C | 0.000 | -0.001 | 0.009 | -0.010 | 0.170 | 0.000 | -5.431 | 0.057 |
| D | 0.000 | -0.044 | 0.049 | 0.004 | -0.156 | 0.000 | 10.819 | -0.050 |
| E | 0.000 | -0.024 | 0.023 | 0.002 | -0.181 | 0.000 | 8.196 | 0.007 |
| F | 0.000 | -0.013 | -0.005 | -0.001 | 0.070 | **0.359** | 12.228 | 0.019 |
| G | 0.000 | 0.001 | -0.003 | 0.009 | 0.031 | 0.000 | -1.859 | 0.013 |
| H | 0.000 | -0.018 | 0.021 | 0.004 | -0.189 | 0.000 | 1.265 | 0.026 |
| I | **0.188** | -0.028 | **0.425** | -0.032 | -0.478 | 0.006 | -3.436 | 0.336 |
| J | 0.191 | 0.377 | n/a | n/a | n/a | n/a | n/a | n/a |

Aggregate impact (`ES_full − ES_ablated`):

| cond | ablation | ES full | ES ablated | impact | band |
|---|---|---|---|---|---|
| A | No Sleep | 49.102 | 0.000 | 49.102 | foundational |
| B | No Lineage | 49.102 | 49.102 | 0.000 | cosmetic |
| C | No Curiosity | 49.102 | 44.635 | 4.467 | cosmetic |
| D | No Falsification | 49.102 | 52.209 | -3.108 | cosmetic |
| E | No Dreams | 49.102 | 52.104 | -3.002 | cosmetic |
| F | No Hypothesis Layer | 49.102 | 48.750 | 0.352 | cosmetic |
| G | No Questions | 49.102 | 48.292 | 0.809 | cosmetic |
| H | Random Curiosity | 49.102 | 51.410 | -2.308 | cosmetic |
| I | Random Sleep | 49.102 | 34.282 | 14.819 | supportive |
| J | Memory Without Structure | 49.102 | 0.000 | 49.102 | foundational |

Final-cycle populations — **the table that actually discriminates**, because the aggregate does not count structures:

| cond | G4 hypotheses | G5 theories | G5 questions | G6 dreams | G7 investigations | G8 experiments |
|---|---|---|---|---|---|---|
| O_FULL | 13 | 1 | 1 | 8 | 5 | 5 |
| A | 0 | 0 | 0 | 0 | 0 | 0 |
| B | 13 | 1 | 1 | 8 | 5 | 5 |
| C | 15 | **3** | **3** | 8 | 0 | 0 |
| D | 7 | 0 | 0 | 3 | 3 | 3 |
| E | 6 | 0 | 0 | 0 | 0 | 0 |
| F | 0 | **6** | **6** | 8 | 5 | 5 |
| G | 13 | 1 | **0** | 8 | **5** | **5** |
| H | 5 | 0 | 0 | 3 | 3 | 3 |
| I | 15 | 1 | 1 | 0 | 1 | 0 |
| J | 0 | 0 | 0 | 0 | 0 | 0 |

Cross-domain transfer: **CDT = −0.486** over 12 domain pairs, mean shared vocabulary **0.17 tags**.

### 17.5 A blind spot in the aggregate, stated before the findings

**The ES aggregate does not count structures.** A condition that destroys half the organism's population can score "cosmetic" on ES, because no ES term counts hypotheses, theories, dreams, investigations or experiments.

Conditions **E** (No Dreams) and **G** (No Questions) are exactly this case: E ends with 6 hypotheses instead of 13 and no dreams, no theories, no questions, no investigations and no experiments; G ends with zero questions. Both score near-zero ES impact — and both are plainly not cosmetic. **The population table is part of the primary result, and the aggregate is a convenience index over six of the eight available metrics.** The per-generation survival selectivity in `docs/ablation_study.json` is the third leg.

A second, narrower caveat: **Contradiction Density counts subjects carrying two or more competing expectations among the *surviving hypotheses*.** When an ablation changes the size of the hypothesis population, CD changes mechanically. CD is therefore only comparable between conditions whose hypothesis layer is comparable — `O_FULL` versus `B` and `G` — and should not be read across `D`, `E` or `F`, where the hypothesis population itself has been removed or frozen.

### 17.6 Findings

**Finding A — Sleep and the graph are the architecture; the rest is a policy on top of it.**

`A` (No Sleep) and `J` (Memory Without Structure) are the only two conditions that reach the "foundational" band, and both reach it by collapsing to **zero structures**. The instructive part is what does *not* collapse: `A`'s substrate predictive accuracy is 0.435 against the full system's 0.377 — the graph learned the regularities *better* without sleep, because sleep adds competing structures to the same graph. Sleep is not where the learning happens. **Sleep is where the learning becomes a representation.**

`J` is the contamination check and it comes out clean: with no co-occurrence and no temporal edges, **not one structure of any kind emerges** — not a concept, not a loop, not a hypothesis. Nothing leaks in from anywhere else. That is the single most reassuring result in this study.

**Finding B — Lineage is governance, not cognition. Every other metric is exactly unchanged.**

`B` (No Lineage) produces deltas of **0.000** on PA, PA_substrate, IP, SCR, SS, CD and NSR, and identical populations (13 / 1 / 1 / 8 / 5 / 5). The *only* thing that changes is Lineage Completeness, from 1.000 to 0.000.

So Law II — "every structure traces back to raw experience" — is **load-bearing for auditability and completely inert for behaviour**. That is a genuinely useful result and it is not what the design implies: it is listed as a principle, and one might reasonably read that as a claim that the architecture depends on it. It does not. The honest formulation is that lineage is a *governance layer*, and a valuable one — it is what makes claims 3 through 8 checkable at all — but it should not be counted among the cognitive mechanisms when arguing that the architecture does something.

**Finding C — Curiosity does not drive belief formation. It drives action on belief.**

`C` (No Curiosity) removes Layers 7 and 8 entirely. The result is the opposite of what the "attention economy" framing predicts: hypotheses go **up** (13 → 15), theories **up** (1 → 3), questions **up** (1 → 3), and contradiction density goes **up** (12.2 → 17.7 per 1000 nodes, with the contradiction duty cycle rising from 61% to 65%). What disappears is only the two top layers: 0 investigations, 0 experiments.

So removing curiosity does not make the organism less curious — it makes it **more** uncertain and less able to do anything about it. Curiosity in this architecture is an *output* channel, not an input to belief formation. The belief layer does not consult it.

**Finding D — Removing falsification does not produce runaway belief growth. It produces a frozen organism. The pre-registered prediction was falsified.**

`D` was predicted to show runaway belief growth, graph bloat, theory inflation and accumulating contradictions. The measured result is the opposite in every respect: hypotheses **fall** from 13 to 7, theories and questions go to **zero**, surviving structures fall from 109 to 72, and contradiction density falls from 12.2 to 1.4 — with the contradiction duty cycle collapsing from 61% of cycles to 5%.

The mechanism is legible once you see it. With nothing ever dying, every stale candidate is re-stored forever; the candidate store fills with immortal-but-irrelevant beliefs; and because working memory is the newest 4,000 sleep events, those immortals **crowd out the current structures**. The organism does not accumulate beliefs — it stops replacing them.

That is a real architectural consequence and it is a *better* finding than the prediction: it says forgetting is not merely a cleanup mechanism, it is load-bearing for the ability to hold a *current* view. It also carries a caveat that must be stated: this ablation conflates "no extinction" with "no forgetting", because the substrate's bounded working memory is what does the crowding. An organism with unbounded memory would accumulate instead. The pre-registered prediction was wrong; the measurement stands.

**Finding E — Dreams are structurally load-bearing for everything above Layer 5, and the aggregate score cannot see it.**

`E` (No Dreams) ends with 6 hypotheses instead of 13, zero theories, zero questions, zero investigations and zero experiments — the whole upper ladder is gone. Yet its ES impact is −3.002, i.e. "cosmetic". This is Finding 5's blind spot in its purest form: **an ablation can remove the majority of the organism and score as harmless.**

The mechanism is that Layer 7 builds investigations from Questions *and* Dreams. Remove dreams and the only remaining source of investigation is the Question layer — and `E` shows that Questions alone do not carry it. Dreams are not decoration on top of the architecture; they are one of the two things feeding the attention economy.

**Finding F — Removing the hypothesis layer produces MORE theories and LESS provenance.**

`F` (No Hypothesis Layer) bypasses Generation 4 and builds Theories and Questions directly from Workflow components. The result is **6 theories and 6 questions** against the full system's 1 and 1 — six times as many — while Lineage Completeness falls from 1.000 to **0.641**, because workflow-derived theories have no parent chain to Generation 0.

This is the clearest illustration in the study of what Law II buys: it constrains *which* structures are allowed to exist, and it does so without helping any structure be better. A system without lineage produces more theories and can prove less about any of them. Note also that CD is 0.000 for `F` — a definitional artifact, since F has no hypotheses for contradictions to live in, not evidence of epistemic cleanliness.

**Finding G — Questions are not the gateway to inquiry. Dreams are.**

`G` (No Questions) was predicted to take investigations and experiments to zero along with the Questions. **It did not.** Questions go to 0; hypotheses (13), theories (1), dreams (8), investigations (5) and experiments (5) all survive unchanged.

The reason is Layer 7's inputs: investigations are built from Questions **and** Dreams, and with 8 dreams still alive the curiosity pipeline still has fuel. So the pre-registered prediction was falsified, and the finding is sharper than the prediction: **Questions are not load-bearing for inquiry in this architecture.** The copy in the ablation framework — "if experiments still emerge, questions may be unnecessary" — turns out to be correct as stated.

**Finding H — Random sleep keeps the volume and destroys the signal.**

`I` (Random Sleep) produces the same node counts as the full system but with random content: PA falls from 0.191 to **0.003**, and Information Preservation from 0.488 to **0.063**. The organism is still producing structures; it has simply stopped representing anything. Survival selectivity goes to 0.998 (everything dies every cycle, because nothing recurs) and novelty to 0.538 (random topologies are almost always new).

This is the positive control the study needed: **the sleep pipeline is not a formatting step.** Same volume, no information.

**Finding I — Random curiosity performs the same as EIG curiosity on every metric that can currently be measured.**

`H` produces **identical predictive accuracy** (PA delta 0.000), a slightly *higher* aggregate score, and a *smaller* organism (5 hypotheses, 0 theories, 3 dreams, 3 investigations, 3 experiments against 13 / 1 / 8 / 5 / 5). On the metrics that exist, choosing investigations at random is indistinguishable from choosing them by Expected Information Gain.

**But the metric that would separate them does not exist.** The metrics that could distinguish a good curiosity policy from a random one are exactly the three that are unmeasurable without an experiment executor: experiment value (entropy removed), experiment information gain, and curiosity yield (questions actually resolved). This is not a null result — it is a **blind spot with a known cause**, and it points at the same gap as Finding 9 and §13.

### 17.7 Remedies

In priority order. Every item below is a **proposal**; Phase A freezes cognitive changes, and none of these has been applied.

| # | Remedy | Why | Kind |
|---|---|---|---|
| 1 | **Build the experiment executor** (probe format → probe→event mapping → belief-delta measurement) | It is the single change that unblocks the most: it makes EIG testable against random curiosity (Finding I), it makes `CY` and `EIG*` measurable so the aggregate stops being blind, it lets a Question actually close, and it is the missing half of the self-build loop. | New capability |
| 2 | **Replace share-based confidence with a posterior** (`(support + α)/(support + contradiction + α + β)`) | Independently established by §14's `wide_lookback` ablation. It is simpler than what it replaces, keeps a split belief alive regardless of sibling count, and makes the lookback width irrelevant. | Cognitive — needs a recorded decision |
| 3 | **Stop truncating hypotheses alphabetically** | The cap decides which beliefs survive by name order, and §17.6 Finding D shows the population is what carries the system. Merit-based selection is the obvious fix; it is a cognitive change. | Cognitive — needs a recorded decision |
| 4 | **Reconsider the hypothesis cap itself** | `MAX_HYPOTHESES = 15` was chosen when the layer had a different population. 15 slots against 13–15 live hypotheses means the cap binds constantly, and the ablation shows how much rides on which beliefs make the cut. | Cognitive — needs a recorded decision |
| 5 | **Give the aggregate a population term, or stop using it** | Finding E is the argument: an ablation removed the whole upper ladder and scored −3. The per-metric table plus the population table is the honest summary. | Measurement |
| 6 | **Record Law II as governance, not cognition** | Finding B. The design documents list lineage among the principles in a way that implies behavioural importance it does not have. | Documentation |
| 7 | **Run the ablation suite again after any cognitive change** | It is now the regression test for "did we accidentally make the organism depend on us, or stop depending on something it used to need?" | Process |

### 17.8 What would falsify this section

- If the verification stage shows that a condition labelled "cosmetic" never actually perturbed the organism, its finding is void.
- If Random Curiosity turns out to have selected the *same* investigations as EIG (Jaccard ≈ 1), then Finding I is untested rather than true.
- If the contradictions in `D` turn out to be suppressed by the bounded working memory rather than by the removal of extinction, then Finding D's mechanism is wrong even though its measurement stands.
- If `E`'s collapse is caused by something other than dreams — for instance by the removal of stored dream candidates changing the working-memory composition — then Finding E's mechanism is wrong.
