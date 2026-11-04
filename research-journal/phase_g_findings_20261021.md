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
- **§17 — the ablation study.** *Which mechanisms are actually doing the work?* Eleven conditions, pre-registered before the run, with a mechanism-verification stage run before any interpretation. The answer is uncomfortable and useful: sleep and the graph are foundational, **lineage is pure governance with zero behavioral effect**, and the attention economy changes what it selects without changing what the organism achieves.

Both studies are also summarized in `docs/USER-MANUAL.md` §8.1 and §8.2.

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
| `idx_events_type_time`, `idx_events_source` | O(log n) `recent()` | Behavior unchanged |
| `prune_sleep_candidates(keep=20000)` | Bounds disk growth | Never deletes experience events or `sleep:meta`; leaves the newest 4,000 events (the organism's working memory) byte-identical |
| Backfill on open | Existing databases keep working | One-time; verified equivalent |

### Study configuration

| File | Change |
|---|---|
| `run_continuous.py` | Replacement branch-structured `STUDY_STREAM`; `EVENTS_PER_CYCLE = 8`; per-cycle retention; `substrate_rows_pruned` in the summary |
| `start_organica.bat` | `organica.log` appended, never truncated; stdout mirror moved to `console.log` |
| `.gitignore` | `*.log`, `logs/`, `INTERVAL` — unbounded run artifacts out of version control |
| `metrics.py`, `observation/metrics_observer.py`, `dashboard_ui.py` | Observation pipeline repairs (§6) |

### New artifacts

- `benchmarks/g5_gap_diagnostic.py` — the G5 gate instrumented and proven.
- `benchmarks/substrate_probe.py` — live-substrate read costs and page accounting.
- `benchmarks/substrate_scaling_analysis.py` — latency-vs-cycle fit from the real log.
- `benchmarks/stream_sweep.py` — candidate stream selection.
- `tests/test_substrate_equivalence.py` — 8 tests proving the substrate changes are behavior-preserving.
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

**It also sharpens the architecture amendment in §7.** The knife-edge behavior comes from `DEATH_THRESHOLD` interacting with share-based confidence. Two candidate amendments:

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

1. **Belief should be a posterior, not a share.** A Laplace- or Beta-smoothed posterior over each subject's successors would keep a genuinely split belief alive (a 50/50 split across 20 observations should stay near 0.5, not decay below 0.15 and die), would make the lookback width irrelevant, and would remove much of the need for engineered stimuli. It is also *more* human-like: human belief revision is evidence accumulation against a prior, not a normalized ratio. It is a one-formula change.
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

### 17.5 Mechanism verification

Run before any outcome was interpreted (`benchmarks/ablation_verify.py`, results in `docs/ablation_verification.json`). An ablation result is only meaningful if the perturbation actually happened.

#### Perturbation census

Every condition changed the organism. `B` (No Lineage) is the deliberate exception: it is a provenance ablation, so *no* population changing is the result, not a failed perturbation.

| cond | perturbation |
|---|---|
| A | confirmed — every Layer-1 population → 0 |
| B | confirmed (provenance-only: behavior unchanged is the result) |
| C | confirmed — hypotheses 13→15, theories 1→3, investigations 5→0 |
| D | confirmed — processes 10→0, workflows 10→0, hypotheses 13→7, theories 1→0 |
| E | confirmed — processes 10→0, workflows 10→0, hypotheses 13→6 |
| F | confirmed — hypotheses 13→0, theories 1→6, questions 1→6 |
| G | confirmed — questions 1→0 |
| H | confirmed — processes 10→0, workflows 10→0, hypotheses 13→5, theories 1→0 |
| I | confirmed — processes 10→0, workflows 10→0, hypotheses 13→15 |
| J | confirmed — every Layer-1 population → 0 |

#### Did Random Curiosity actually change behavior?

**Yes, and the comparison is far from vacuous.**

| | EIG policy | Random policy |
|---|---|---|
| final-selection Jaccard | **0.111** (9 selections, 1 shared) | |
| top-k precision (selected items that are in the top-k by EIG) | **1.000** | 0.584 |
| mean curiosity score of what was selected | **0.990** | 0.863 |
| mean curiosity score of the candidate pool | 0.911 | 0.868 |
| fraction of selections in the top decile | **0.475** | 0.271 |
| rank correlation (score vs. selection position) | −0.162 | +0.098 |

Two things follow, and they point in opposite directions.

**The EIG implementation works.** Its `top-k precision` is **1.000**: every single time it selected five investigations, they were the five highest-curiosity candidates available. Random managed 0.584. The ranking function is doing exactly what it was written to do, and the order it produces is genuinely driven by curiosity (rho = −0.162, negative because a higher score means an earlier position) while random selection shows no ordering effect at all (+0.098).

**And it buys nothing measurable.** With a selection that is *provably* better — top-decile hit rate 48% versus 27% — the organism's predictive accuracy was **identical** (PA delta 0.000), the aggregate score was marginally *higher* for random, and the resulting organism was smaller. So the honest statement is not "the attention economy does not work." It is: **the attention economy works perfectly as a ranking function and produces no measurable downstream benefit.** That is a sharper and more interesting claim than either "EIG is broken" or "EIG is fake," and it points at the same place as everything else: the two layers above curiosity produce candidates that nothing consumes.

#### Where do contradictions come from?

The full system generates contradiction counts in the **thousands**: the largest `contradiction_count` ever observed on a single hypothesis is **6,391** in `O_FULL`, against 425 in `D` and 554 in `D` uncapped.

| run | subjects carrying ≥2 competing expectations (mean) | (max) |
|---|---|---|
| `O_FULL`, cap 15 | 1.373 | 4 |
| `O_FULL`, cap removed | 1.373 | 4 |
| `D`, cap 15 | 0.157 | 4 |
| `D`, cap removed | 0.273 | 6 |

This resolves the question the No-Falsification result raised, and the answer is neither of the two obvious ones.

- **Possibility A is false.** Contradiction generation does *not* come from the falsification subsystem. `contradiction_count` is computed directly from the temporal graph in `_form_and_test_hypotheses` — `max(0, total_flow − support)` — with no falsification gate anywhere near it. The full system's contradiction counts are enormous.
- **Possibility B is false.** No pipeline was disabled by accident. The path from the graph to the contradiction count is a single arithmetic expression with no conditional on any ablation flag.
- **Possibility C is true, and the mechanism is now identified.** Contradiction *generation* is entirely independent of falsification; what No-Falsification suppresses is contradiction *survival* — and it does so through a path that has nothing to do with falsification at all.

The mechanism is Layer 4's alphabetical truncation. In `D`'s final population, **every** surviving hypothesis is a `high_structural_significance` marker — subjects like `developer`, `engineer`, `executed`, `modified`, `report`, `session`, `suite` — all of which sort early alphabetically. With `MAX_HYPOTHESES = 15` and the hypothesis list sorted by subject, those markers fill the budget and crowd out the genuine subject→expectation pairs, which are the ones that carry the contradiction counts. Removing the cap nearly doubles the competing-subject count in `D` (0.157 → 0.273), confirming the cap is the binding constraint there.

Note the nuance: for `O_FULL` the cap is **not** binding — uncapped gives the identical 1.373 — so competing beliefs genuinely coexist in the full system. The cap is a *latent* suppressor that becomes active precisely when the population shifts, which is why it went unnoticed until now.

**The consequence is worth stating plainly: the system's reported contradiction density, and by extension its Generation-5 duty cycle, are partly artifacts of alphabetical ordering.** Which beliefs are allowed to disagree with each other is currently decided by how their subject names sort. That is a real defect, it is now demonstrated rather than hypothesised, and it raises journal §7's proposal from "candidate defect" to "the most consequential cognitive defect found so far" — because it decides which beliefs survive, and §17.6 Finding D shows how much rides on that.

### 17.6 A blind spot in the aggregate, stated before the findings

**The ES aggregate does not count structures.** A condition that destroys half the organism's population can score "cosmetic" on ES, because no ES term counts hypotheses, theories, dreams, investigations or experiments.

Conditions **E** (No Dreams) and **G** (No Questions) are exactly this case: E ends with 6 hypotheses instead of 13 and no dreams, no theories, no questions, no investigations and no experiments; G ends with zero questions. Both score near-zero ES impact — and both are plainly not cosmetic. **The population table is part of the primary result, and the aggregate is a convenience index over six of the eight available metrics.** The per-generation survival selectivity in `docs/ablation_study.json` is the third leg.

A second, narrower caveat: **Contradiction Density counts subjects carrying two or more competing expectations among the *surviving hypotheses*.** When an ablation changes the size of the hypothesis population, CD changes mechanically. CD is therefore only comparable between conditions whose hypothesis layer is comparable — `O_FULL` versus `B` and `G` — and should not be read across `D`, `E` or `F`, where the hypothesis population itself has been removed or frozen.

### 17.7 Findings

**Finding A — Sleep and the graph are the architecture; the rest is a policy on top of it.**

`A` (No Sleep) and `J` (Memory Without Structure) are the only two conditions that reach the "foundational" band, and both reach it by collapsing to **zero structures**. The instructive part is what does *not* collapse: `A`'s substrate predictive accuracy is 0.435 against the full system's 0.377 — the graph learned the regularities *better* without sleep, because sleep adds competing structures to the same graph. Sleep is not where the learning happens. **Sleep is where the learning becomes a representation.**

`J` is the contamination check and it comes out clean: with no co-occurrence and no temporal edges, **not one structure of any kind emerges** — not a concept, not a loop, not a hypothesis. Nothing leaks in from anywhere else. That is the single most reassuring result in this study.

**Finding B — Lineage is governance, not cognition. Every other metric is exactly unchanged.**

`B` (No Lineage) produces deltas of **0.000** on PA, PA_substrate, IP, SCR, SS, CD and NSR, and identical populations (13 / 1 / 1 / 8 / 5 / 5). The *only* thing that changes is Lineage Completeness, from 1.000 to 0.000.

So Law II — "every structure traces back to raw experience" — is **load-bearing for auditability and completely inert for behavior**. That is a genuinely useful result and it is not what the design implies: it is listed as a principle, and one might reasonably read that as a claim that the architecture depends on it. It does not. The honest formulation is that lineage is a *governance layer*, and a valuable one — it is what makes claims 3 through 8 checkable at all — but it should not be counted among the cognitive mechanisms when arguing that the architecture does something.

**Finding C — Curiosity does not drive belief formation. It drives action on belief.**

`C` (No Curiosity) removes Layers 7 and 8 entirely. The result is the opposite of what the "attention economy" framing predicts: hypotheses go **up** (13 → 15), theories **up** (1 → 3), questions **up** (1 → 3), and contradiction density goes **up** (12.2 → 17.7 per 1000 nodes, with the contradiction duty cycle rising from 61% to 65%). What disappears is only the two top layers: 0 investigations, 0 experiments.

So removing curiosity does not make the organism less curious — it makes it **more** uncertain and less able to do anything about it. Curiosity in this architecture is an *output* channel, not an input to belief formation. The belief layer does not consult it.

**Finding D — Removing falsification does not produce runaway belief growth. It produces a frozen organism. The pre-registered prediction was falsified.**

`D` was predicted to show runaway belief growth, graph bloat, theory inflation and accumulating contradictions. The measured result is the opposite in every respect: hypotheses **fall** from 13 to 7, theories and questions go to **zero**, surviving structures fall from 109 to 72, and contradiction density falls from 12.2 to 1.4 — with the contradiction duty cycle collapsing from 61% of cycles to 5%.

The mechanism is legible once you see it. With nothing ever dying, every stale candidate is re-stored forever; the candidate store fills with immortal-but-irrelevant beliefs; and because working memory is the newest 4,000 sleep events, those immortals **crowd out the current structures**. The organism does not accumulate beliefs — it stops replacing them.

The mechanism verification (§17.5) pins down a second, independent cause: the contradiction collapse is **not** caused by removing extinction at all. The full system generates contradiction counts in the thousands (max 6,391 on a single hypothesis); `D`'s suppression of them comes from Layer 4's alphabetical truncation filling the 15-slot budget with `high_structural_significance` markers, crowding out the genuine subject→expectation pairs that carry the counts. Removing the cap nearly doubles `D`'s competing-subject count (0.157 → 0.273). So two separate mechanisms are in play — the frozen belief population, and the cap — and both reduce the *measured* tension.

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

**Finding I — Random curiosity performs the same as EIG curiosity on every metric that can currently be measured — and the verification shows the comparison is real.**

`H` produces **identical predictive accuracy** (PA delta 0.000), a slightly *higher* aggregate score, and a *smaller* organism (5 hypotheses, 0 theories, 3 dreams, 3 investigations, 3 experiments against 13 / 1 / 8 / 5 / 5).

The verification stage confirms this is not a vacuous comparison. The two policies overlap on only **1 of 9** final selections (Jaccard 0.111), and the EIG policy's `top-k precision` is **1.000** — every time it selected five investigations, they were the five highest-curiosity candidates available, against random's 0.584, with a top-decile hit rate of 48% against 27%.

So the EIG implementation is **not broken**. It is a perfect ranker. It selects demonstrably better candidates than random, and the organism's predictive accuracy is unchanged. The reason is that the layers above curiosity produce *candidates* that nothing consumes — and the metrics that would expose that (`CY`, `EIG*`, experiment value) are exactly the three that cannot be computed without an experiment executor. This is not a null result. It is a **blind spot with a known cause**, and it points at the same gap as Finding 9 and §13.

**Finding J — Which beliefs are allowed to disagree is currently decided by alphabetical order. This is the most consequential defect found.**

> **CORRECTION (2026-10-23, after the Phase V1.5 instrumentation audit).**
> The alphabetical rule is a **real defect** — a name-based rule that is
> frequency-correlated in this project, because the common subjects
> (`developer`, `engineer`, `executed`, `modified`, `report`, `session`,
> `suite`) are both frequent *and* alphabetically early. A controller that
> decides what to keep by sorting strings is not making a decision about
> merit. That much stands.
>
> **But two claims made here were wrong, and both are retracted:**
>
> 1. **The cap does not bind, so the sort currently changes nothing.**
>    Measured over 600 cold cycles: the Layer-4 belief pool reaches a
>    maximum of **8** against `MAX_HYPOTHESES = 15`, and the cap binds in
>    **0 of 600** cycles. Raising the cap 15 → 30 → 60 produces
>    byte-identical populations. Because nothing is ever truncated,
>    "alphabetical" and "salience" select the **same membership** in every
>    one of those cycles (they differ only in *order*, and Layer 5
>    re-sorts by support count). The parameter influence map classifies
>    `MAX_HYPOTHESES` as **INERT**. The alphabetical rule is therefore a
>    **latent** defect, not an active force — and it was not "demonstrated",
>    it was *measured to have no effect*.
> 2. **The sort was not the cause of Finding D's contradiction collapse.**
>    The verification census shows that in `D` (No Falsification) both
>    `G2 processes` and `G3 workflows` were **0**. Hypotheses are built
>    only from workflows, processes and meta-concepts, so `D`'s
>    all-marker population is fully explained by the destruction of the
>    Layer-2/3 layers — no truncation was involved. The attribution to
>    alphabetical crowding was wrong.
>
> What replaces the original claim: **the organism is starved, not
> selective.** The instrumentation audit (§19) measures retention pressure
> per layer and finds 29–61× at Layer 1 (936 loops, 621 predictions, 309
> anomalies competing for 15–20 slots, every one of them retained by a
> *popularity* rule) against **0.35** at Layer 4 (5–8 beliefs for 15
> slots). The evidence is discarded at the top and found wanting at the
> bottom. The alphabetical hypothesis rule is the same family of defect as
> the Layer-1 popularity rules, three layers downstream, and it is
> invisible only because there is nothing left to choose between.
>
> The fix is unchanged and still worth making — sort by evidence rather
> than by name — but it is a **correctness** fix to a rule that is
> currently inert, not a fix for Finding D.

The verification's contradiction analysis turned up something that had been suspected since journal §7 and is now *demonstrated*. Layer 4 truncates to `MAX_HYPOTHESES = 15` **after sorting the hypothesis list by subject name**. That means:

1. `high_structural_significance` markers — whose subjects are ordinary words like `developer`, `engineer`, `executed`, `report` — sort early and **fill the budget**, crowding out the genuine subject→expectation pairs.
2. The pairs that get crowded out are precisely the ones that carry contradiction counts.
3. So **the system's measured contradiction density, and by extension its Generation-5 duty cycle, depend partly on how subject names sort.**

For `O_FULL` the cap is not binding — uncapped gives the identical 1.373 competing subjects — so competing beliefs genuinely coexist in the healthy system. The cap is a *latent* suppressor that becomes active exactly when the population shifts, which is why it survived every earlier test and why it only surfaced once an ablation was designed to look for it.

This matters more than any other finding here, because §17.7 Finding D shows how much rides on it: which beliefs survive *is* the system. A controller that decides what to keep by sorting strings is not making a decision about merit. The fix is small — sort by evidence rather than by name — but it is a **cognitive change** and therefore frozen under Phase A.

### 17.8 Remedies

In priority order. Every item below is a **proposal**; Phase A freezes cognitive changes, and none of these has been applied.

| # | Remedy | Why | Kind |
|---|---|---|---|
| 1 | **Build the experiment executor** (probe format → probe→event mapping → belief-delta measurement) | It is the single change that unblocks the most: it makes EIG testable against random curiosity (Finding I), it makes `CY` and `EIG*` measurable so the aggregate stops being blind, it lets a Question actually close, and it is the missing half of the self-build loop. | New capability |
| 2 | **Replace share-based confidence with a posterior** (`(support + α)/(support + contradiction + α + β)`) | Independently established by §14's `wide_lookback` ablation. It is simpler than what it replaces, keeps a split belief alive regardless of sibling count, and makes the lookback width irrelevant. | Cognitive — needs a recorded decision |
| 3 | **Stop truncating hypotheses alphabetically — a real defect, but measured to be currently inert** | Finding J, as corrected. The rule is name-based and frequency-correlated, so it is wrong in principle. But the cap binds in 0 of 600 cycles, so the sort currently changes nothing — and it was **not** the cause of Finding D. Sort by evidence (a unit-free salience composite) instead, and treat it as a correctness fix, not as the fix for D. | Cognitive — authorised by the owner 2026-10-22, applied 2026-10-23 |
| 4 | **The hypothesis cap is not the constraint — upstream belief supply is** | This remedy was written on the belief that "15 slots against 13–15 live hypotheses means the cap binds constantly". That is **wrong**: `MAX_HYPOTHESES` is INERT (0/600 cycles; raising it 15→60 changes nothing). The real constraint is upstream: Layer 1 discards ~99% of its candidates (pressure 29–61×) and Layer 4 receives 5–8 beliefs. Re-target this remedy at the funnel, not the cap. | Cognitive — needs a recorded decision |
| 5 | **Give the aggregate a population term, or stop using it** | Finding E is the argument: an ablation removed the whole upper ladder and scored −3. The per-metric table plus the population table is the honest summary. | Measurement |
| 6 | **Record Law II as governance, not cognition** | Finding B. The design documents list lineage among the principles in a way that implies behavioral importance it does not have. | Documentation |
| 7 | **Run the ablation suite again after any cognitive change** | It is now the regression test for "did we accidentally make the organism depend on us, or stop depending on something it used to need?" | Process |

### 17.9 What would falsify this section

- If the verification stage shows that a condition labelled "cosmetic" never actually perturbed the organism, its finding is void.
- If Random Curiosity turns out to have selected the *same* investigations as EIG (Jaccard ≈ 1), then Finding I is untested rather than true.
- If the contradictions in `D` turn out to be suppressed by the bounded working memory rather than by the removal of extinction, then Finding D's mechanism is wrong even though its measurement stands.
- If `E`'s collapse is caused by something other than dreams — for instance by the removal of stored dream candidates changing the working-memory composition — then Finding E's mechanism is wrong.
---

## 18. Does feeling come before thinking? A proposal for a valuation layer

*Raised 2026-10-22 by the owner. This section is a **proposal**, not an applied change. Nothing here has been implemented, and Phase A freezes cognitive changes.*

### 18.1 The question

> *"Feeling comes before thinking, right?"*

The short answer for Organica is: **the signals already do, the drives do not.** That distinction is worth a page, because it is the difference between "this project needs a new layer" and "this project needs to finish a layer it already started."

### 18.2 What is already there

The intuition that Organica is missing a valuation layer is understandable but, on inspection, half wrong. Organica already computes value signals, and it already computes them **upstream of the structures they gate**:

| Signal | Computed at | Gates |
|---|---|---|
| `support`, `contradiction` | Layer 4, from the temporal graph | hypothesis admission |
| `confidence` = support/(support+contradiction) | Layer 4 | the hypothesis's own survival |
| `uncertainty` = entropy × maturity | Layer 5 | Question admission |
| `expected_information_gain` | Layer 7 | investigation and experiment ranking |
| dream `novelty` | Layer 6 | dream diversity |
| reinforcement vs. decay | `_natural_selection` | structure survival |

**Law V is already the valuation law**: *"Cognitive importance is governed by Expected Information Gain, not probability."* That is a salience rule. And the dataflow is already **valuation → belief**: a hypothesis cannot be formed without a confidence, a question without an uncertainty, an investigation without an EIG. So the proposed reordering — valuation, then hypothesis, then theory — is not a new pipeline. It is the pipeline that exists, with the valuation computation distributed across Layers 4–8 instead of named as a layer.

### 18.3 What is genuinely missing

Three things, and the ablation study names the third.

**(a) Valence.** Every signal above is *interestingness*. They are all positive scalars. There is no aversive signal anywhere in the system: nothing hurts, no belief is costly, no outcome is unpleasant. Human feeling carries valence, and the aversive side is what drives avoidance, cost-sensitive action, and most of what we would call caring. Organica can want to *know*; it cannot want to *avoid*. Note that the code already contains the shape of this — `priority = EIG / cost`, with probe 1.0, dream 0.8, mutation/conditional 1.2 — but those costs are **constants**, not **consequences**. The denominator exists; the pain does not.

**(b) Persistence.** The counts accumulate; the *valuation* does not. Attention is re-derived from the graph every cycle rather than integrated over time. There is no carried-over tension, no growing interest, no "I have been puzzling at this for twelve cycles." The consequence is already visible in the telemetry: the Generation-5 duty cycle **oscillates** (journal finding 6) rather than trending, because nothing accumulates. A drive, in the technical sense, is a state variable that integrates over time; Organica has none.

**(c) An appetite for disconfirmation.** This is the one the No-Falsification ablation exposed, and it is the most interesting. In Organica, contradiction is **derived from** the graph — `contradiction = total_flow − support` — so contradiction is *recorded, never sought*. Curiosity requires a split belief to **already exist**. There is no drive that says "go find a reason this might be wrong."

Copilot's framing of this is exactly right: *if support grows and contradictions stay at zero, what causes the system to doubt anything?* The measured answer is **nothing**.

### 18.4 The corroboration from the other side

The cold-start study (§14) says the same thing from the opposite direction. With a real, unengineered stimulus — this repository's own commit history — the organism **never generates its own competing expectations**. G5 never emerges. It *inherits* the branch point from the stimulus; it never *manufactures* one.

An organism with an endogenous appetite for disconfirmation would manufacture one. That is a falsifiable difference, and the current answer is no.

### 18.5 The proposal

Not "add a valuation layer". Three concrete steps, in this order.

1. **Name and isolate what exists.** Make the valuation computation one explicit layer whose output is a small, inspectable state — surprise, tension, novelty, coherence — instead of being recomputed ad hoc inside Layers 4–8. This is mostly a *refactor*, and mostly a clarification of Law V. It makes the ordering auditable, which is the actual point.
2. **Give the organism an executor.** It already has a probe format, an EIG score, and a cost table. What it lacks is a way to *act*. This is where valence comes from naturally: an executed probe that leaves a belief unmoved, or refutes one, is an aversive experience with a real cost attached. Until then, any valuation layer would be a second unauditable cognitive mechanism stacked on the first, and this session's own discipline forbids that.
3. **Add the disconfirmation appetite.** A drive term that seeks *unresolved tension* specifically, not merely high uncertainty. This is the missing third leg, and it is the one that would let the organism generate its own branch points.

### 18.6 The tests it must pass

A proposal that cannot fail is a belief, not an architecture. This one gets the same treatment the confidence formula got: a pre-registered prediction and an instrument that can fail.

| # | Prediction | Instrument | Current |
|---|---|---|---|
| V1 | With an appetite for disconfirmation, the organism generates its own competing expectations from an unengineered stream | `benchmarks/cold_start.py`, condition `real_git_history` | **Fails** — G5 never appears |
| V2 | Tension accumulates across cycles rather than oscillating | the G5 duty cycle over a long run | **Fails** — the duty cycle oscillates, it does not trend |
| V3 | Curiosity is *caused* by disconfirmation rather than merely correlated with it | `benchmarks/ablation_study.py`, condition `C` (No Curiosity) | **Unresolved** — removing curiosity *raises* contradiction density, which is consistent with an appetite existing but not being consulted |

**V3 is the sharpest of the three.** Finding C of the ablation study showed that removing curiosity *increases* hypotheses (13→15), theories (1→3) and contradictions (12.2→17.7), while only the two output layers disappear. That is the signature of a system that *has* tension and cannot act on it — which is what an appetite that is never consulted would look like. It is consistent with the hypothesis; it does not establish it.

### 18.7 A note on the word

"Feeling" is a loaded word, and the risk to this project is sliding into anthropomorphic claims that the measurements cannot support. The discipline should be: build **value signals** — measurable scalars with valence, persistence, and a direction — and do not claim the organism *feels* anything. `docs/EMERGENCE-CRITERIA.md` already draws that line; this section is inside it.

The defensible framing is the one the project already uses for humans: an infant arrives with substantial built-in machinery and learns essentially all of the *content*. Organica would arrive with a valuation apparatus — the machinery for deciding what matters — and learn all of the content. What it does not have is what a person has: a body, stakes, and something at stake. That is worth stating plainly, because it is both the honest limit of the comparison and the clearest statement of what an experiment executor would change.


## 19. Phase V1.5 — the instrumentation audit: where the pressure really is

### 19.1 Why this section exists

The Tier-1 campaign was specified as: *Full (alphabetical retention) vs Salience retention vs No-Contradictions vs No-Questions vs No-Dreams vs Anti-EIG, 3,000 cycles each.* The organising hypothesis was that **the retention policy is a hidden evolutionary force**.

Before running it, five very different upstream threshold settings were tried against a 400-cycle baseline. **Every one produced byte-identical results.** Two explanations are possible and they demand opposite responses:

* (a) the parameters genuinely do not matter, or
* (b) **the observation channel is saturated** — the parameter changes the candidate pool, but a layer's output cap discards the change before it can be seen.

(b) is far more likely. A whole matrix would have measured bottlenecks instead of cognition. So the machinery was measured first. This section is that measurement. It is a **measurement study, not an ablation study**: the engine is subclassed, never edited.

### 19.2 Finding 11 — the live run plateaued; the 90-day horizon buys nothing

The longitudinal run was stopped at 3,725 sleep cycles so the architecture change could land without a file-vs-process mismatch, and its per-cycle series was archived (`docs/prefix_run_series.json`).

| Series | Converged at cycle | Last 25% (931 cycles) stdev | Slope per 1,000 cycles | Distinct values |
|---|---:|---:|---:|---:|
| theories | 261 | **0.000000** | 0.0 | 1 |
| questions | 261 | **0.000000** | 0.0 | 1 |
| dreams | 162 | **0.000000** | 0.0 | 1 |
| investigations | 82 | **0.000000** | 0.0 | 1 |
| experiments | 82 | **0.000000** | 0.0 | 1 |
| hypotheses | 1,677 | **0.000000** | 0.0 | 1 |

**The organism reached a fixed point and then sat still for 3,464 cycles.** A single arm with a flat line describes nothing and identifies nothing; only contrasts can. The comparative matrix therefore replaces the 90-day single arm as the primary experiment, and the daemon becomes a *monitor* rather than a gate.

But the flat population hides a non-flat substrate. Over the same period, the summed contradiction across the retained hypotheses rose **0 to 400,550** (support 78,647), because confidence is a *share*: `support / (support + contradiction)` settles at about 0.16-0.17 for every subject even as its absolute evidence grows by orders of magnitude. **The organism did not stop accumulating evidence; it stopped converting it.** Every developmental metric in this project is defined on counts, so that divergence is currently invisible to the metric suite.

### 19.3 Finding 12 — the retention policy is inert, and the cap never binds

Measured over 600 cold cycles:

* the Layer-4 **belief** pool reaches a maximum of **8** against `MAX_HYPOTHESES = 15`; the cap binds in **0 of 600** cycles;
* raising the cap 15 to 30 to 60 gives **byte-identical** populations (6 beliefs, 5 subjects, 1 subject with 2 or more beliefs);
* because nothing is truncated, "alphabetical" and "salience" select the **same membership** in every cycle — they differ only in *order*, and Layer 5 re-sorts by support count.

`MAX_HYPOTHESES` is classified **INERT** in the parameter influence map. **The P1 experiment as specified would have compared two identical colonies.**

This corrects Finding J (17.7). The alphabetical rule remains a real defect — it decides by sorting strings, and in this project the frequent subjects are also alphabetically early, so it is a popularity rule in disguise — but it is currently a *latent* defect with **zero** causal effect, and it was **not** the cause of Finding D's collapse (D's processes *and* workflows were both 0, so its marker-only population is explained by the destroyed Layer-2/3 layers).

### 19.4 Finding 13 — the organism is starved, not selective

For every capped layer, the candidate pool **before** truncation was measured, and `retention_pressure = pool_size / cap` computed. 400 cycles, cold start, study stream.

| Layer | cap | pool mean | p95 | pressure mean | pressure p95 |
|---|---:|---:|---:|---:|---:|
| loops | 15 | 936 | 936 | **61.1** | **62.4** |
| predictions | 20 | 598 | 621 | **29.9** | **31.1** |
| anomalies | 10 | 292 | 309 | **29.2** | **30.9** |
| investigations | 5 | 8.8 | 11 | 1.77 | 2.20 |
| processes | 10 | 11.8 | 13 | 1.18 | 1.30 |
| dreams | 8 | 8.3 | 12 | 1.04 | 1.50 |
| experiments | 5 | 4.9 | 5 | 0.98 | 1.00 |
| workflows | 10 | 9.1 | 10 | 0.91 | 1.00 |
| meta_concepts | 15 | 9.0 | 9 | 0.60 | 0.60 |
| **hypotheses** | 15 | **5.3** | 8 | **0.35** | 0.53 |
| questions | 6 | 1.2 | 3 | 0.19 | 0.50 |
| theories | 8 | 1.2 | 3 | 0.14 | 0.38 |

**Layer 1 discards about 99% of its own candidates; Layer 4 has 5-8 beliefs for 15 slots.** Every over-truncated layer retains by a **popularity** rule — raw temporal count for predictions, strength for loops, dominance ratio for anomalies. The alphabetical hypothesis rule is the same family of defect three layers downstream, and it is invisible only because there is nothing left to choose between.

The measured funnel:

```
  936 loops -------------+
  621 predictions --------+-- capped by count/strength (popularity rules) --+
  309 anomalies ----------+                                                |
                                                                          v
                                    12 processes -- capped --> 10 workflows --+
                                                                           |
                                                                           v
                                                                    5-8 beliefs --> 1 theory --> 1 question
```

### 19.5 Finding 14 — eight of fourteen parameters do nothing

| Verdict | Parameters |
|---|---|
| **DECISIVE** | `DEATH_THRESHOLD` · `STABLE_THRESHOLD` · `MAX_PROCESSES` · `MAX_PREDICTIONS` |
| **POOL_ONLY** | `PREDICTION_MIN_COUNT` · `LOOP_MIN_STRENGTH` |
| **INERT** | `MAX_HYPOTHESES` · `MAX_WORKFLOWS` · `MAX_META_CONCEPTS` · `WORKFLOW_MIN_MATCHED_METAS` · `META_CONCEPT_MIN_REFS` · `CONCEPT_MIN_DEGREE` · `CONCEPT_MIN_REACH` · `PHRASE_MIN_CLUSTERING` |

Two of the POOL_ONLY cases are the smoking gun for (b): `PREDICTION_MIN_COUNT` 5 to 3 changed the prediction pool (621 to 641) and changed **nothing** downstream, because the top 20 by temporal count are the same 20.

### 19.6 Finding 15 — a richer world makes the organism WORSE

The leading hypothesis was that Organica is *complexity-limited by its environment*: a 9-tag world cannot differentiate, so a 50- or 100-tag world should widen every pool. **Measured, it does the opposite.**

| Stimulus | events | world tags | world entropy | belief pool | pressure | processes | workflows | theories |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| study stream | 48 | 41.8 | 5.06 | **5.47** | 0.365 | 10.0 | 10.0 | **1.00** |
| + 2 domains | 148 | 57.8 | 5.45 | 2.37 | 0.158 | 6.4 | 6.4 | 0.56 |
| + 4 domains | 238 | 96.8 | 6.26 | **1.41** | 0.094 | 6.1 | 6.1 | **0.00** |

More world tags, higher entropy, and 2.8 times more Layer-1 candidates — and the belief pool **collapses** and the theory count falls to **zero**. Layer-1 pressure rises from 61x to 295x.

### 19.7 Finding 16 — there is a narrow optimum, and it is in the middle

Widening the prediction cap (the one Layer-1 cap that is DECISIVE) traces the whole curve:

| `MAX_PREDICTIONS` | belief pairs | belief pool | pressure | processes | workflows | hypotheses | theories |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 (baseline) | 5.05 | 5.47 | 0.365 | 10.0 | 10.0 | 12.05 | 1.00 |
| 40 | 6.51 | 5.18 | 0.346 | 8.78 | 8.78 | 15.34 | 1.23 |
| **80** | **8.69** | **7.71** | **0.514** | 8.9 | 8.9 | 21.01 | 1.28 |
| 160 | 0.00 | 0.74 | 0.050 | **0.11** | 0.11 | 2.94 | **0.00** |
| 320 | 1.82 | 1.71 | 0.114 | 3.5 | 2.91 | 10.05 | **0.00** |

Widening Layer 1 **does** widen the belief pool, up to a point (5.47 to 7.71, +41% at cap 80). Beyond that the organism **breaks**: at cap 160 the process and workflow layers collapse to 0.11 and every theory disappears.

**And even at the optimum, retention pressure is 0.514 — still below 1.0. Gate G-P1 fails at every configuration tested.**

### 19.8 What actually controls the developmental trajectory

Findings 15 and 16 point at the same mechanism, and it is not the one that was assumed.

A process is only formed from a **reciprocal** prediction pair (`a->b` *and* `b->a`), and a 3-cycle requires `a->b->c->a`. The study stream was deliberately built with **branch points** — one subject leading to both a positive and a negative outcome — which is exactly what makes reciprocal pairs exist. The domain corpora are larger but not branch-structured in the same way, so they contribute mostly one-way pairs.

So the binding constraint is neither world *size* nor any single cap. It is **the number of distinct reciprocal structures the stimulus contains, expressed through a narrow optimum**:

* too few branch points -> 5-8 beliefs, 1 theory;
* more candidate diversity without more reciprocal structure -> the composition layers' type-diversity gates stop qualifying, processes and workflows collapse, 0 theories.

This also explains Finding 11 (the plateau) and Finding 12 (inert retention) with one mechanism: the organism is a **filter**, not a chooser. It has a stable fixed point at one theory because one subject ("session") is the only one with 2 or more competing beliefs, and nothing in the current stimulus disturbs that.

**The measurable consequence for the next campaign:** the belief pool must exceed 15 for a retention experiment to mean anything, and the belief pool is bounded by the number of distinct reciprocal structures reaching Layer 4 — currently about 8. Reaching 15 requires a **stimulus with more independent branch points**, not a wider world, not a bigger budget, and not a different retention rule.

### 19.9 What this section does to the plan

| Was planned | Now | Why |
|---|---|---|
| Run the 6-colony Tier-1 matrix | **Gated** behind G-P1 | With pressure 0.35-0.51, `FULL` and `SALIENCE_RETENTION` would be the same colony |
| Replace alphabetical retention | **Done** (2026-10-23) | The rule was wrong; it is now a named, unit-free salience policy with its own allowance for inert markers. Measured effect on current behavior: **none** — the cap does not bind — so it is a correctness fix, not a behavioral one |
| Extend the 90-day run | **Replaced** by the matrix; the daemon becomes a monitor | 3,464 cycles of zero variance (19.2) |
| Enlarge the world | **Refuted as a strategy** | A richer world made the organism worse (19.6) |
| Enlarge the budget | **Refuted as a strategy** | `MAX_HYPOTHESES` is INERT (19.5) |

### 19.10 Disclosure — two defects in our own instrumentation

Both were found by checking a measurement against the substrate it claims to describe, and both are disclosed here rather than quietly fixed.

1. **The archived contradiction series was `null`, not zero.** The archive script copied `rec["contradiction_total"]` from each daemon log record, but `run_continuous.py` never writes that key. All 3,725 archived values were `null`, which reads as "zero contradiction everywhere"; the true final value is **400,550**. The archive is now a committed tool (`benchmarks/archive_run.py`) that re-derives the totals from the hypothesis snapshot, which *is* in the record.
2. **The first audit reported the workflow layer as dead.** It read the report attribute `workflows` instead of `workflow_concepts`, so a working layer measured 0. The audit now uses an explicit name-to-attribute mapping, and a test asserts that no inline cap literals remain in the layer builders.

### 19.11 Artifacts

| Artifact | Contents |
|---|---|
| `benchmarks/development_probe.py` -> `docs/development_probe.json` | Cap-binding census, budget insensitivity, plateau analysis, vocabulary audit |
| `benchmarks/instrumentation_audit.py` -> `docs/instrumentation_audit.json` | Pre-cap pools and retention pressure, 14-parameter influence map, effective world size, funnel sweep |
| `benchmarks/archive_run.py` -> `docs/prefix_run_series.json` | The "before" series, with contradiction totals re-derived |
| `docs/FACTS-SHEET.md` | Every measured claim with its provenance, separated from assumptions |
| `docs/GATE-BOARD.md` | Gate status, the G-P1 gate, the G1-G4 perturbation ladder, the decision backlog |
| `tests/test_retention_policy.py` | 18 tests pinning the retention semantics, the marker allowance, the unit-free tension term and the contradiction-scale hook |


## 20. Validating the gate before designing the stimulus

### 20.1 Why this section exists

§19 established that the Tier-1 campaign cannot be run on the current
stimulus: retention pressure on the hypothesis layer is 0.35, so the
`FULL` and `SALIENCE_RETENTION` arms would be the same colony. The
proposed way out was to replace the stimulus with one carrying more
*branch structure* — more subjects with competing successors.

The proposed gate for that stimulus was **Multi-Belief Subject Density**:

```
MBSD = (subjects holding >= 2 active beliefs) / (all belief subjects)
```

with the binding criterion being an absolute count of >= 3 competing
subjects. That gate was a **hypothesis**, and a hypothesis is not worth
building a stimulus on. The cheapest available test was against data that
already existed: the 11 V1 ablation conditions.

The V1 harness already recorded, per cycle, `competing_subjects` (the
number of subjects holding >= 2 distinct expectations) alongside the
theory count, in `docs/ablation_study.json` →
`observations.contradiction_history`. **No new run was needed to compute
the numerator.**

### 20.2 Finding 17 — the theory count is not *predicted* by subject competition; it *is* subject competition

| Condition | mean competing subjects | max | final theories | identity holds | r(cycle) |
|---|---:|---:|---:|---:|---:|
| O_FULL Full system | 1.37 | 4 | 1 | **100.0%** | 1.000 |
| A No Sleep | 0.00 | 0 | 0 | 100.0% | n/a |
| B No Lineage | 1.37 | 4 | 1 | 100.0% | 1.000 |
| C No Curiosity | 1.83 | 4 | 3 | 100.0% | 1.000 |
| D No Falsification | 0.16 | 4 | 0 | 100.0% | 1.000 |
| E No Dreams | 0.38 | 4 | 0 | 100.0% | 1.000 |
| **F No Hypothesis Layer** | **0.00** | **0** | **6** | **18.0%** | n/a |
| G No Questions | 1.56 | 4 | 1 | 100.0% | 1.000 |
| H Random Curiosity | 1.21 | 4 | 0 | 100.0% | 1.000 |
| I Random Sleep | 1.41 | 4 | 1 | 99.7% | 0.998 |
| J Memory Without Structure | 0.00 | 0 | 0 | 100.0% | n/a |

**The identity `theories == min(competing_subjects, MAX_THEORIES)` holds in
100% of cycles in 9 of the 11 conditions.** The two exceptions are the two
conditions that are *designed* to break it:

* **F (No Hypothesis Layer)** bypasses Generation 4 entirely and builds
  theories and questions straight from workflow components. It produces
  **6 theories with 0 competing subjects**, and the identity holds in only
  18% of its cycles. This is not a failure of the identity — it is the
  proof of the *mediation claim*: theories are formed from subject
  competition, and F shows the competition can be bypassed.
* **I (Random Sleep)** randomises every layer, so it breaks the identity
  in 0.3% of cycles.

**The cross-condition correlation is much weaker than the within-cycle
identity**, and it is worth being precise about why:

```
corr(mean competing subjects, final theories)   =  0.017   (all 11)
                                                =  0.775   (excluding F)
```

The final-cycle snapshot is a noisy statistic for a quantity the project
already knows oscillates (journal finding 6), and F is a designed
exception that inverts the relationship. The per-cycle identity is the
result that generalises; the final-cycle correlation is not.

### 20.3 What this does to the proposed gate

**The gate is validated — but in a stronger form than proposed, and the
form changes.**

The numerator of MBSD is not a *predictor* of theory formation. It **is**
the mechanism. Layer 5 does nothing except coalesce, one theory per
subject holding two or more competing beliefs. Consequently:

1. **The density ratio adds no information beyond the absolute count.**
   The ratio is a function of two counts the mechanism already ties
   together, and the absolute count is what Layer 5 actually consumes. The
   gate is therefore stated as a **count**, and the density is retained
   only as a reported statistic.
2. **A second cap was found, in the same family as the first.**
   `MAX_THEORIES = 8` caps theory capacity at 8. A stimulus producing more
   than 8 competing subjects would push the surplus *invisible* to M1, M8
   and M9 — **the same measurement blind spot as the hypothesis cap, one
   layer up**. The gate therefore carries a fourth condition, **G-EXP**:
   the theory population must never reach the cap.
3. **The design target follows from the measurement, not from taste.**
   The stimulus must produce **5–7 competing subjects**:
   * at least 3, because that is the proposed bar and the minimum for a
     theory ecology worth comparing;
   * at most 7, because `MAX_THEORIES = 8` and an unsaturated theory layer
     is required for M8 and M9 to be able to see anything move;
   * with 2–3 beliefs each, giving a belief pool of roughly 12–24, which
     can cross the 15-slot hypothesis cap and satisfy G-P1.

So the target is not "more tags" and not "more volume". It is
**5–7 subjects, each with 2–3 competing successors, distributed so that
the belief pool exceeds 15.**

### 20.4 The honest caveat on all of this

Everything above is measured on **one stimulus** — the 48-event study
stream — and on ablations of it. A branch-structured stimulus is
*engineered*, in the same way the current study stream is engineered
(§14 and §2.1 of this journal both record that the original stream was
replaced precisely because it was too narrow to exercise the architecture).
Results on an engineered stimulus are evidence that the **architecture
can** support the behavior, not that it does so **unassisted**. The
unassisted question is a separate experiment, and §14's cold-start design
is the instrument for it.

The gates below are therefore stated as *preconditions for the campaign to
be informative*, not as claims about the organism.

### 20.5 Artifacts

| Artifact | Contents |
|---|---|
| `benchmarks/gate_validation.py` -> `docs/gate_validation.json` | The identity test, the cross-condition correlation, and the high-theory check, from the V1 artifact |
| `benchmarks/mbsd_census.py` -> `docs/mbsd_census.json` | The exact MBSD density (with the denominator) for all 11 conditions, re-running the V1 condition classes verbatim |
| `docs/FORCE-MATRIX-PREREGISTRATION.md` | The frozen metric contract and the four gates, committed before the campaign |

---

## 21. Milestone M0.5 — mechanism closure

### 21.1 What the milestone asked for

Five items, in the owner's words:

1. Complete the MBSD census.
2. Determine whether MBSD is a **predictor** or a **definition**.
3. Explain the r=4 / r=6 / r=10 collapse boundary. *"Don't ship 'r=4' because it
   works. Explain why 'r=4' works."*
4. Extract the surviving edge topology from the study stream.
5. Replicate that topology intentionally in the branch stimulus.

Items 1, 2 and 4 are closed below. Item 3 and item 5 depend on a single
mechanism that had to be found first, and it was.

### 21.2 Item 1 — the census is complete (11 of 11 conditions)

`benchmarks/mbsd_census.py` → `docs/mbsd_census.json`. Every V1 condition
class was re-run **verbatim** for 300 cycles with an instrument that records
the belief pool *before* retention, so the density has a real denominator
instead of a missing one.

| Cond | Intervention | subjects mean/max | subjects ≥2 mean/max | MBSD | belief pool mean/max | pressure | ≥3 abs | ≥0.50 dens |
|------|--------------|---|---|---:|---|---|:--:|:--:|
| **O_FULL** | reference | 3.53 / 5 | 1.39 / **3** | 0.392 | 4.92 / 8 | 0.33 | ✅ | ❌ |
| A | No Sleep | — | — | — | — | — | — | — |
| B | No Lineage | 3.53 / 5 | 1.39 / **3** | 0.392 | 4.92 / 8 | 0.33 | ✅ | ❌ |
| C | No Curiosity | 3.47 / 5 | 1.91 / **3** | **0.550** | 5.37 / 8 | 0.36 | ✅ | ✅ |
| D | No Falsification | 0 / 0 | 0 / 0 | 0.000 | 0 / 0 | 0.00 | ❌ | ❌ |
| E | No Dreams | 4.27 / 5 | 0.07 / 1 | 0.016 | 4.33 / 6 | 0.29 | ❌ | ❌ |
| F | No Hypothesis Layer | — | — | — | — | — | — | — |
| G | No Questions | 5.00 / 5 | 1.49 / **3** | 0.299 | 6.49 / 8 | 0.43 | ✅ | ❌ |
| H | Random Curiosity | 5.00 / 5 | 1.95 / 2 | 0.389 | 6.95 / 7 | 0.46 | ❌ | ❌ |
| I | Random Sleep | 0 / 0 | 0 / 0 | 0.000 | 0 / 0 | 0.00 | ❌ | ❌ |
| J | Memory Without Structure | 0 / 0 | 0 / 0 | 0.000 | 0 / 0 | 0.00 | ❌ | ❌ |

*A and F bypass Layer 4 by design, so there is no belief pool and MBSD is
undefined; F's 6 theories come from a different route entirely.*

What the census adds on top of §20:

1. **The gate has never been met, even as a peak, in a way that would make a
   campaign meaningful.** The ≥3-subject form is touched by 4 of the 9
   measurable conditions; the **≥5** form is met by **none**. Mean competing
   subjects never exceeds **1.95**.
2. **C (No Curiosity) is the only condition that reaches density ≥ 0.50.**
   Removing curiosity *raises* belief density — the same direction as V1's C
   row, now visible at the density level.
3. **B (No Lineage) reproduces O_FULL exactly** on every belief metric. The V1
   control holds at the density level too.
4. **E (No Dreams) has the most subjects and almost no competition** (4.27
   subjects, 0.07 with ≥2). Dreams are load-bearing for *competition*, not for
   subject count.
5. **H (Random Curiosity) has the highest mean (1.95) but never reaches 3.** A
   better mean does not mean the gate is close.
6. **D, I and J produce no beliefs at all** in 300 cycles.

### 21.3 Item 2 — the answer is **Case B: MBSD is structural, not predictive**

The milestone's two cases were:

* **Case A** — more competing subjects *causes* more theories, because the
  architecture develops richer belief structures.
* **Case B** — workflow composition *produces* competing subjects, which
  *produces* the theory count, so the theory count is mathematically
  determined by the same structure.

**The measurement says Case B, and it says it as an identity rather than a
correlation.** `theories == min(competing_subjects, MAX_THEORIES)` holds in
**100% of cycles in 9 of the 11 conditions**, 99.7% in Random Sleep, and 18.0%
in No-Hypothesis-Layer — the one condition that bypasses Layer 4 by design
and builds 6 theories with **zero** competing subjects.

Two consequences, and they are not the same kind of consequence:

1. **The density ratio is not a developmental metric.** It is a restatement of
   the count, and the count is the mechanism's input, not its output. A gate
   built on a ratio that is definitionally tied to its numerator adds no
   information.
2. **The interesting scientific question moves.** It is no longer "does more
   competition cause more theory?" — that is settled by arithmetic. It is
   **"what makes a subject hold more than one expectation at all?"** That is a
   question about the substrate, not about the metric.

This is the same shape as the V1.5 audit result: the hypothesis ("EIG is a
developmental force") died, and a sharper, smaller question replaced it
("EIG ranks perfectly and buys nothing measurable — because selection is not
the binding constraint").

### 21.4 Item 4 — the surviving edge topology of the only stimulus that works

The branch stimulus collapsed; the study stream does not. So the study
stream's surviving topology was extracted directly
(`benchmarks/branch_diag2.py`, 60 cycles, `docs/`-adjacent scratch artifact).

**Study stream — 20 distinct surviving prediction pairs** (the window is
*full* at the cap of 20, so the study stream is not window-limited):

```
developer -> suite   325   strength 0.555      suite    -> developer  304   0.589
session  -> developer 174  0.555               modified -> developer 154  0.305
developer-> executed  150  0.552               executed -> suite    146   0.494
session  -> developer 146  0.304               developer-> modified 143   0.302
suite    -> report    140  0.319               report   -> suite    136   0.491
session  -> suite     138  0.304               executed -> developer 135  0.479
developer-> session   137  0.302               suite    -> executed 134   0.318
developer-> report    131  0.302               modified -> suite    133   0.304
report   -> developer 126  0.477               developer-> suite    125   0.317
suite    -> modified  125  0.317               suite    -> session   125   0.317
+ defect->engineer, regression->engineer (the two defect-corpus tags)
```

**Every surviving edge has strength in the band 0.30 – 0.78.** That band is
the whole story: `STABLE_THRESHOLD = 0.3` is the floor, and the working
edges sit just above it.

From that window the engine produced **10 processes** — 6 two-cycles and 4
**three-cycles**:

```
['suite','modified','developer']   ['suite','session','developer']
['suite','executed','developer']   ['suite','report','developer']
```

and **10 workflows**, four of them three-component:

```
['developer','executed','suite']   ['developer','report','suite']
['developer','session','suite']     ['developer','modified','suite']
```

**The four three-component workflows all share the pair {developer, suite}.**
That pair is the *only* high-share reciprocal structure in the study stream,
and it is what produces every multi-belief subject the organism has. The
seven resulting beliefs are:

```
developer -> suite      suite -> developer      report -> developer
report   -> suite       session-> developer     session-> suite
modified -> developer
```

**This is the topology to replicate.** Not "more tags". A small set of tags
whose outgoing flow is *split*, each split holding ≥ 15% of the source's
outgoing flow, with the reciprocals landing on one or two hub tags.

### 21.5 The mechanism — two filters, and one of them is mis-scoped

Reading the engine produced a single causal chain, and it is short:

```
temporal edge (world)  →  Layer 1 prediction candidate
                        →  strength = min(1, count / source_freq)
                        →  survives to stable_prior only if strength >= 0.3
                        →  Layer 2 process (2-cycle or 3-cycle)
                        →  Layer 3 workflow (process with >= 2 meta anchors)
                        →  Layer 4 belief (ordered pair of workflow components)
                        →  belief kept only if support/total_outgoing_flow >= 0.15
                        →  Layer 5 theory (one per subject holding >= 2 beliefs)
```

Two filters decide whether a subject ever holds more than one belief, and
they are **not scoped the same way**:

* **Filter 1 (Layer 1 → stable_prior)** uses `source_freq` from
  `MemoryService.tag_frequencies()`.
* **Filter 2 (Layer 4, belief death)** uses `total_flow` from the **temporal
  graph** — world events only.

And `MemoryService.store()` builds the graph from world events only, while
the frequency counter is maintained for **every** stored event:

```python
# Only build graph edges from external experience, not internal
# sleep output.  Sleep candidates are stored but don't pollute the
# co-occurrence / temporal graphs.
if event_type != "sleep":
    self._record_cooccurrences(event.tags)
    self._record_temporal_edges(event.tags)
# Maintain the incremental tag-frequency counter. This mirrors
# exactly what a full `SELECT tags FROM events` scan would count
# (including tags contributed by sleep payloads), but in O(1)
# amortised time instead of O(total rows) per sleep cycle.
self._record_tag_counts(event.tags)
```

**So the numerator of the strength ratio is world-only and its denominator
includes the organism's own output.** The counter is a correct
*count of tag occurrences*; it is the wrong *normaliser* for a world-graph
ratio.

This is the same contamination the facts sheet measured at **60.6%** of tag
occurrences being the organism's own JSON field names (§D8), and it is
decision-backlog **row 8** — *"Is the organism's own output polluting its
input?"* — which had been carried as an open question. It is now a measured
mechanism with a located cause.

#### 21.5.1 What it does to the branch stimulus, measured

The lattice stimulus died at the first filter, and the diagnostic shows
exactly how. For the tag `alpha` (the shared hub of the lattice):

```
count   src        tgt       source_freq  ratio  survived
   930       alpha       bravo    21516  0.043  no
   877       bravo       alpha    84767  0.010  no
   331     charlie       alpha   100516  0.003  no
   312       alpha     charlie    21516  0.015  no
   306       delta       alpha     1901  0.161  YES
   299       delta       bravo     1901  0.157  YES
   116      subject       bravo     1461  0.079  YES
   115     experiment       alpha     2378  0.049  YES
```

`alpha` occurs 21,516 times in the substrate; `developer` in the study stream
occurs 585. The lattice's edges therefore have ratios of 0.003 – 0.16,
**all below the 0.3 survival floor**, and the window collapsed to **4
distinct pairs** — two of which were the organism's own field names
(`subject -> bravo`, `experiment -> alpha`).

With four surviving pairs there was no reciprocal pair, so:

```
processes: 0
workflows: 0
beliefs:   0
```

**The collapse was not a stimulus-design failure. It was a denominator
failure.** The stimulus's edges were ranked first by count (they were the
top of the temporal graph, 930 vs 118) and then destroyed by the survival
filter, because the filter's denominator included the organism's own output.

### 21.6 Item 3 — the r=4 / r=6 / r=10 boundary, explained

The first branch generator passed all four gates at r=4 and collapsed at r=6
and r=10. The reason is **not** a phase transition in the stimulus, and
this is the one place where the working hypothesis was wrong and the
measurement overruled it.

The first explanation attempted was an edge-budget story: a longer stream
produces more distinct edges, the prediction window holds 20, so the
structural edges get displaced and the supply starves. That explanation
was **tested and refuted**. The probe re-ran all three repeat counts with
the frequency scope corrected, and every one of them works:

| stimulus | scope = all (before) | scope = world (after) |
|---|---|---|
| `branch_r4` | win 5.65/21 · bel 5.43/19 · ge2 1.72/7 · **sus 0.27** · zero 0.55 | win 20/20 · bel **18.00/18** · ge2 **7.00/7** · **sus 1.00** · zero **0.00** |
| `branch_r6` | win 2.90/6 · bel 0.60/18 · ge2 0.12/7 · **sus 0.02** · zero 0.83 | win 21/21 · bel **17.95/18** · ge2 **7.00/7** · **sus 1.00** · zero **0.00** |
| `branch_r10` | win 4.57/21 · bel 5.00/19 · ge2 1.98/8 · **sus 0.28** · zero 0.72 | win 20.5/21 · bel **18.13/19** · ge2 7.13/8 · **sus 1.00** · zero **0.00** |

*(`win` = distinct surviving prediction edges · `bel` = belief pool mean/max ·
`ge2` = subjects holding ≥ 2 beliefs mean/max · `sus` = fraction of tail
cycles in which every gate holds simultaneously · `zero` = fraction of tail
cycles with no beliefs at all.)*

**There was no boundary.** r=4, r=6 and r=10 produce *the same* result once
the denominator is correct: a full prediction window, a belief pool of 18,
seven competing subjects, and **100%** of tail cycles passing every gate
simultaneously. What r changed, under the broken scope, was only how badly
the pollution happened to suppress the edges — and the difference between
"works" and "collapses" was a property of the *measurement*, not of the
stimulus.

**The generalisable lesson is the one the milestone was reaching for.**
A stimulus parameter that flips a result between "works" and "collapses"
is not a boundary condition of the system under study; it is a statement
about the instrument. The parameter was interacting with a mis-scoped
denominator, and the interaction looked exactly like a phase transition
because the denominator's pollution grows with the organism's output, which
grows with the stimulus. The owner's instruction — *"don't ship 'r=4'
because it works; explain why 'r=4' works"* — is what forced this to be
measured rather than adopted, and the measurement removed the parameter
from the design entirely.

**The correction was made to the substrate, not to the stimulus**
(`organica/memory.py`), and it is disclosed in §21.8.

### 21.7 Item 5 — the branch stimulus, designed from the surviving topology

The design rule that falls out of §21.4 and §21.5, stated as constraints
rather than as a parameter:

1. **Every subject's outgoing flow must be split**, with ≥ 2 targets each
   holding ≥ 15% of that flow (the Layer-4 death threshold) — and ideally
   ≥ 30%, so the belief is not marginal.
2. **The structural edges must all fit inside the prediction window** —
   the window is 20 slots, so the stimulus should produce well under 20
   *distinct* structural edges, not hundreds.
3. **The split must be reciprocal**, because a 2-cycle or 3-cycle is the only
   thing the process builder accepts, and a 3-cycle is the only thing that
   yields a subject with more than one expectation.
4. **The denominator must be the world's**, not the organism's.

Constraint 3 is the one that is easiest to get wrong and the one the first
generator got wrong: a workflow's components are the tags of a **3-cycle**,
and a 3-cycle gives its three subjects exactly two beliefs each. So the
unit of competing expectation is a triangle, and the stimulus must be built
out of triangles — which is what `organica/branch_streams.py` now does.

**Three disjoint triangles give exactly the derived target**, and the
measurement matched the arithmetic prediction to the unit:

```
3 triangles x 3 tags            = 9 tags, 7 subjects after overlap
3 triangles x 6 ordered pairs   = 18 distinct (subject, expectation) pairs
7 subjects x >= 2 beliefs each  = 7 competing subjects
18 / MAX_HYPOTHESES (15)        = 1.20 retention pressure
7 theories                      < MAX_THEORIES (8)  ->  G-EXP holds
```

Measured on the corrected substrate: **18.00 beliefs, 7.00 competing
subjects, 5 theories, 100% of tail cycles passing every gate
simultaneously.** The prediction was derived from the mechanism before the
run and it held.

Two lattice designs pass every gate (`L1` — 7 subjects, `L3` — 6 subjects);
two do not (`L2`/`L4` — the belief pool reaches only 14, below the 15 that
G-P1 needs). The failures are informative: the shared-hub lattices produce
*more* competing subjects per triangle but *fewer* total beliefs, because
the hub's edges carry the flow. The disjoint lattice wins on the quantity
that actually matters.

### 21.8 The correction, and what it changes

**The fix.** `MemoryService.store()` now maintains the tag-frequency counter
inside the same `event_type != "sleep"` branch that builds the
co-occurrence and temporal graphs:

```python
if event_type != "sleep":
    self._record_cooccurrences(event.tags)
    self._record_temporal_edges(event.tags)
    self._record_tag_counts(event.tags)
```

A `meta` table records the scope the counters were built with, so a
database written by an older build rebuilds its counter **exactly once**
instead of mixing two populations in one table. `tests/test_substrate_equivalence.py`
gains a scope-consistency regression test: *a sleep payload must change
neither the temporal graph nor the frequency counter that normalises it.*

**This is a behavior change and it is disclosed here.**

| | before | after |
|---|---:|---:|
| study stream, belief pool mean | 6.83 | 5.97 |
| study stream, competing subjects mean | 1.83 | **0.97** |
| study stream, theories mean | 1.42 | 1.11 |
| branch stimulus, belief pool mean | 5.43 (intermittent) | **18.00 (constant)** |
| branch stimulus, competing subjects mean | 1.72 (intermittent) | **7.00 (constant)** |

**The study stream gets slightly worse, and that is the important part.**
Under the broken scope, the pollution suppressed edges *selectively* — it
removed the low-share edges and left a concentrated set, and a
concentrated set is exactly what produces a high-share subject and a
theory. The study stream's "1 theory, 1 competing subject" was partly an
**artifact of the defect**. It is still 1 theory and 1 question; the
headline does not change, but the number is no longer a fact about the
world.

Three consequences, stated plainly:

1. **The V1 ablation results were produced on the broken scope.** The V1
   population table, the 11-condition census, and the MBSD validation all
   carry this. They are internally consistent — every condition ran on the
   same substrate — so the *comparisons* stand, but the absolute
   densities are not directly comparable to post-fix numbers. No V1
   conclusion in this journal is retracted, because every one of them is a
   comparison, and the comparisons are unaffected.
2. **The live 90-day run has a discontinuity.** It is running the
   pre-fix build. The restart at the fix is recorded in the log by the
   build marker, and the sleep cycle at which it happened is recorded in
   the manual's revision log.
3. **The fix is applied identically to all six V2 colonies**, so the
   campaign's internal comparisons are unaffected by it. It is not a
   confound *within* the campaign; it is a change of substrate *before* the
   campaign, which is what a pre-registration is for.

### 21.9 What this milestone did not settle

* **The unassisted question is untouched.** Every stimulus here is
  engineered. Whether the organism finds branch structure in the world
  without being handed it is still §14's cold-start question and needs its
  own instrument.
* **The retention policy is still unmeasured as a developmental force.** The
  gates now pass on the branch stimulus, which is the *precondition*; the
  question of whether `FULL` and `SALIENCE` differ on M1–M9 is the
  campaign's question and has not been run.
* **The cause of the original supply limitation is now a substrate scope
  mismatch, not the stimulus.** That is a satisfying answer and it is
  *also* a smaller claim than "the organism is supply-limited". It is
  still true that the world gives the organism one competing subject; it is
  no longer true that a better stimulus could have fixed that by itself.

---

## 22. Did the substrate fix change the scientific meaning of V1?

### 22.1 The question

The scope correction in §21.8 changed the substrate that produced the V1
ablation study. Every V1 conclusion was measured on the old substrate. So
the question is not "did the numbers move" — they had to — but:

> **Do the V1 conclusions still hold, and does any of them now mean
> something different?**

This is a separate question from §21, and a harder one, because a number
that moves is not a finding that moved. The method here is:

0. **Naming.** §21 says "the V2 campaign" for what is now the *Ablation Study 2
   Tier-1 matrix*, and "Organica 2" for the planned successor architecture.
   Those are different things from the package version (0.6.0, SemVer 2), and
   the three namespaces are tabulated in `CHANGELOG.md` and the user manual
   §11.6. §21's wording is left as it was written; this section uses the
   current names.

1. Re-run **all eleven V1 conditions verbatim** on the fixed substrate
   (`benchmarks/ablation_study.py --cycles 300`, the same harness, the same
   seeds) → `docs/ablation_study_postfix.json`.
2. Re-run the **exact density census** on the fixed substrate
   (`benchmarks/mbsd_census.py`) → `docs/mbsd_census_postfix.json`.
3. Compare **each condition's delta against the O_FULL reference arm**,
   computed on the old substrate and again on the new one. Every V1
   conclusion is a comparison between conditions, and all eleven conditions
   ran on one substrate, so the comparison is the thing to compare.
4. Audit the **interpretations** separately from the measurements
   (`benchmarks/v1_impact.py` → `docs/v1_impact.json`).

### 22.2 The metric-level verdict tally

`benchmarks/v1_impact.py` → `docs/v1_impact.json` compares every condition's
**delta against the O_FULL reference arm**, on the old substrate and on the
new one, for all twelve comparable scalars. Every V1 conclusion is a
comparison between conditions, and all eleven conditions ran on one
substrate, so the comparison is the thing to compare.

| Verdict | Count |
|---|---:|
| **REVERSED** | **21** |
| CHANGED MAGNITUDE | 36 |
| unchanged (both zero) | 21 |
| SURVIVED | 14 |
| GONE (was not, now zero) | 4 |
| NEW (was zero, now not) | 1 |

**Twenty-one reversals.** Most are in the small metrics (`scr` — the
structural-clarity rate, `ip` — prediction precision, `nsr` — novelty
saturation ratio), where a sign flip is a small absolute change and means
little on its own. The ones that carry meaning are concentrated in **D**,
**I**, **C**, **G** and **H**, and they are the reason this section exists.

One methodological note, because it would otherwise be a silent error: the
harness reports `n/a` for lineage completeness when a condition has no
lineage at all, and for cross-domain transfer outside the reference arm.
Those metrics are **not measurable**, not zero, and the comparison excludes
them rather than zeroing them — the same defect class as the scope issue
this section documents, caught in the tool written to document it.

### 22.3 The belief-level comparison

| Cond | Intervention | subjects ≥2 (pre) | subjects ≥2 (post) | belief pool max (pre) | belief pool max (post) | verdict |
|---|---|---:|---:|---:|---:|---|
| **O_FULL** | reference | 1.39 / **3** | 1.00 / **1** | 8 | 6 | changed magnitude |
| A | No Sleep | — | — | — | — | unchanged (Layer 4 bypassed) |
| **B** | No Lineage | 1.39 / **3** | 1.00 / **1** | 8 | 6 | **unchanged — still identical to O_FULL** |
| C | No Curiosity | 1.91 / **3** | 2.00 / **2** | 8 | 7 | changed magnitude |
| **D** | **No Falsification** | **0.00 / 0** | **6.00 / 6** | **0** | **18** | **REVERSED** |
| E | No Dreams | 0.07 / 1 | 0.81 / 2 | 6 | 7 | changed magnitude |
| F | No Hypothesis Layer | — | — | — | — | unchanged (Layer 4 bypassed) |
| G | No Questions | 1.49 / 3 | 1.00 / 1 | 8 | 5 | changed magnitude |
| H | Random Curiosity | 1.95 / 2 | 1.00 / 1 | 7 | 5 | changed magnitude |
| **I** | **Random Sleep** | **0.00 / 0** | **0.28 / 2** | **0** | **11** | **REVERSED (partially)** |
| J | Memory Without Structure | 0.00 / 0 | 0.00 / 0 | 0 | 0 | unchanged — still zero |

**D is the headline.** Pre-fix, No Falsification produced *nothing*: zero
beliefs, zero competing subjects, MBSD 0.000, and the V1 report read that
as *the organism freezes rather than bloats*. Post-fix it produces **18
beliefs over 6 subjects, every subject competing, MBSD 1.000 and a
retention pressure of 1.20** — and it is the **only** V1 condition that
clears the launch gates on the study stream.

The pre-fix zeros were not a property of removing falsification. They were
a property of the instrument.

### 22.4 The interpretation audit

The measurements are one thing; what the project *believed* because of them
is another. The second list is the one that matters, and it is short.

| # | Interpretation | Verdict |
|---|---|---|
| I1 | No Sleep is foundational | **SURVIVED** |
| I2 | Memory Without Structure is foundational | **SURVIVED** |
| I3 | No Lineage is the control | **SURVIVED** — still byte-identical to O_FULL |
| **I4** | **"No Falsification freezes the organism"** | **RETRACTED** |
| I5 | Dreams carry the upper ladder | **SURVIVED (direction), RECALIBRATED (magnitude)** |
| I6 | EIG is the only producer of investigations/experiments, and removing it helps | **SURVIVED** |
| I7 | Questions are not the gateway — dreams are | **SURVIVED** |
| I8 | EIG is a perfect ranker that buys nothing measurable | **SURVIVED as a V1 finding; the question it poses is now OPEN** |
| **I9** | **"The organism is supply-limited, not selection-limited"** | **RETRACTED as a general statement** |
| **I10** | **"`MAX_HYPOTHESES` is INERT"** | **RETRACTED as a general statement** (still true of the study stream) |
| I11 | More vocabulary makes it worse | **SURVIVED** |

**I4 — the retraction.** The V1 report said No Falsification "freezes rather
than bloats; contradiction duty 61% → 5%". Post-fix, the same condition
produces the **strongest belief supply in the entire study**: 18 beliefs,
6 of 6 subjects competing, MBSD 1.000, pressure 1.20. The interpretation is
withdrawn, and the reason is recorded rather than quietly overwritten: the
pre-fix zeros were produced by the scope defect, not by the intervention.

**I9 and I10 — the two retractions that matter most.** Both are statements
about the *architecture* that were really statements about the *stimulus*.
"The organism is supply-limited, not selection-limited" was true of the
study stream on the pre-fix substrate, and it is the reason the branch
stimulus was built. It is not a property of the architecture: on the branch
stimulus the pool reaches 18 against a cap of 15, the cap binds, and the
retention policy changes the retained competing-subject count (7
pre-retention, 5–6 post-retention). Selection is now measurable.

"`MAX_HYPOTHESES` is INERT" is the same mistake in a different place: an
instrument property, scoped to a stimulus, reported as an architecture
property. It is still true *of the study stream* and it is false of the
branch stimulus, and the honest statement is the scoped one.

**This is the pattern that keeps recurring, and it is worth naming
explicitly.** Three separate findings in this project — the contradiction
archive reading `null`, the workflow measurement reading the wrong
attribute, the r=4 "phase transition", and now the scope defect — all had
the same shape: *an instrument property was reported as a property of the
organism*. The distinguishing feature of the organism is that it is now
being checked for that failure mode before each experiment, rather than
after.

### 22.5 What did **not** change

* **Every within-V1 comparison.** All eleven conditions ran on one
  substrate before and one after. A comparison between two conditions on
  the same substrate is exactly the kind of claim that survives a change to
  the shared substrate, and §22.2's delta table confirms it.
* **The layer orderings.** Sleep → foundational. Memory → foundational.
  Dreams → upper ladder. Questions → not the gateway. Curiosity →
  investigations and experiments. These are structural, not statistical.
* **The G1–G4 perturbation ladder**, and with it the methodology that found
  every defect in this section.
* **The ranking facts about EIG** (Jaccard 0.111 against the EIG ranking,
  top-k precision 1.000 against 0.584 random). Those are properties of the
  ranking code and are not touched by a frequency estimate.
* **The plateau.** The study stream still converges and still holds one
  theory and one question.
* **The 90-day single-arm conclusion.** It remains a flat line.

### 22.6 What this means for the campaign

The Ablation Study 2 Tier-1 matrix runs on the **fixed** substrate, with the
branch stimulus, with the five gates closed and verified. Three consequences
follow from §22.4:

1. **The campaign is not a re-run of V1.** It is the first experiment in the
   project in which the retention policy *can* matter, because the belief
   cap binds. That is the P1 arm's whole point, and it was unmeasurable
   until now.
2. **No Falsification is no longer a candidate colony.** Its pre-fix
   behavior was an artifact. The six V2 colonies are unchanged from the
   pre-registration, and D is not one of them — but the reason D was
   dropped from the V2 list (it looked like a collapse) is now known to be
   wrong, and that is recorded rather than quietly fixed.
3. **Every V2 result is a measurement on a substrate whose scope has been
   verified.** The counter that normalises every edge count is scoped to
   the same population the edge counts are drawn from, and a regression
   test asserts it.

---

## 23. Ablation Study 2 — the Tier-1 matrix, and what it actually measured

### 23.1 The question this section answers

§21 closed the launch gates. §22 asked whether the substrate fix changed the
scientific meaning of V1. This section reports the matrix itself: six
colonies, 3,000 cycles each, 18,000 colony-cycles, the first experiment in
the project run under a protocol whose metrics, gates, noise floor and
sensitivity were all fixed in advance.

The full artifact is `docs/force_matrix.json`; the results document is
[`docs/FORCE-MATRIX-RESULTS.md`](../docs/FORCE-MATRIX-RESULTS.md).

### 23.2 The run

| | |
|---|---|
| Colonies | FULL, SALIENCE, NO_CONTRADICTIONS, NO_QUESTIONS, NO_DREAMS, ANTI_EIG |
| Cycles | 3,000 per colony |
| Stimulus | `lattice_L1` — three disjoint triangles |
| Seed | 20261023, one per colony |
| `PYTHONHASHSEED` | **0 in all six processes** — see §23.7 |
| Wall clock | 1,814 s for all six in parallel |
| G1 | all six code paths verified distinct *before* the run |

### 23.3 The headline: the structure is decided on cycle 1

Every colony reaches its **complete** structural configuration on the first
cycle and does not change it again for 2,999 cycles:

| Colony | pre-retention beliefs | competing subjects | retained beliefs | theories |
|---|---:|---:|---:|---:|
| FULL | 18 | 7 | 15 | 5 |
| SALIENCE | 18 | 7 | 15 | 5 |
| NO_CONTRADICTIONS | 18 | 7 | 15 | 5 |
| NO_QUESTIONS | 18 | 7 | 15 | 4–5 |
| NO_DREAMS | 18 | 7 | 15 | 4–5 |
| ANTI_EIG | 18 | 7 | 15 | 4–5 |

The steady state is **identical across all six arms** — 18 beliefs over 7
competing subjects, exactly the configuration the launch gates were built to
detect. And the evidence keeps growing the whole time:

> FULL: mean support **101.2 → 11,006.2** over the run. **+10,776%.**

**Structure flat, evidence growing by three orders of magnitude.** That is
the campaign's central measurement, and it is the sharpest form of the
question that has been open since the Phase G plateau: *is the organism
still developing, or has it reached a fixed equilibrium that merely
accumulates evidence?* On this substrate, with this stimulus, it is the
second.

### 23.4 M5 is not a rate, and the name was wrong

M5 ("development velocity") is `new items per 100 cycles`. Over 300 cycles
the FULL arm recorded **74** new items. Over 3,000 cycles it recorded **74**.
The rate fell from 24.667 to 2.467 because the **numerator stopped growing**
while the denominator grew tenfold.

> M5 was dividing a finite inventory by the run length. It was not measuring
> a velocity.

The inventory, broken down by category, is a much richer story than the
rate:

| Colony | beliefs | questions | dreams | experiments | **inventory** | rate /100 cyc | new in last 100 cyc |
|---|---:|---:|---:|---:|---:|---:|---:|
| FULL | 16 | 11 | 36 | 11 | **74** | 2.467 | **0** |
| SALIENCE | 18 | 13 | 31 | 16 | **78** | 2.600 | **0** |
| NO_CONTRADICTIONS | 20 | 12 | 31 | 16 | **79** | 2.633 | **0** |
| NO_QUESTIONS | 18 | 0 | 49 | 45 | **112** | 3.733 | **0** |
| NO_DREAMS | 18 | 13 | 0 | 13 | **44** | 1.467 | **0** |
| ANTI_EIG | 18 | 13 | 38 | 16 | **85** | 2.833 | **0** |

**Every colony discovered zero new items in its final 100 cycles.** Dreams
are the largest single category in five of six arms (36 of 74 in FULL), and
removing dreams does not merely remove the 11 dreams — it removes **30
items from the whole inventory** (44 against 74), because dreams are built
from beliefs.

### 23.5 The confound: the stimulus repeats every 9 cycles

`lattice_L1` contains **9 distinct event strings** over **7 distinct
words**, and the organism's experience **repeats every 9 cycles** — it sees
the same world 333 times in 3,000 cycles.

**A repertoire cannot grow in a world that does not change.** The flat tail
is therefore a fact about the *stimulus* as much as about the organism, and
the campaign cannot distinguish:

- *"the organism found everything the world contains and then held it"*, from
- *"the organism cannot reorganise once it has stabilised"*.

Both hypotheses predict identical numbers on this stimulus. The stimulus
was built to clear the launch gates, and it does — but a **closed, periodic
world cannot test developmental depth**, because it offers nothing to
reorganise toward. This is the most important thing the campaign
established, and it is a **stimulus** finding, not an architecture finding.

### 23.6 Two colonies whose names overstate their interventions

Disclosed because both change how the table must be read, and because both
were found by reading the engine rather than by looking at the numbers.

**`NO_CONTRADICTIONS` does not remove contradictions.**
`CONTRADICTION_SCALE` multiplies the contradiction term *in the confidence
formula* (`organica/sleep.py:1489`). The engine deliberately keeps the raw
count so that "a metric built on them still measures the world when
`CONTRADICTION_SCALE` is not 1.0", and M3 reads `raw_contradiction`. So
**M3 is near-invariant for this colony by construction** (15,951.86 against
15,938.80) — the metric working correctly, not a null. The honest name is
*contradiction not weighted in confidence*. The effect is visible where it
should be: M4 contradiction survival falls 0.9375 → 0.7500.

**`NO_DREAMS` removes 30 items from the inventory, not 11.** Its dreams count
is 0 by construction, but the dreams that *would* have been built from its
beliefs are gone too: inventory 44 against FULL's 74, and the lowest
development rate in the campaign.

### 23.7 The noise floor, and the reason the campaign pins the hash seed

The within-process seed floor is **exactly 0.00** — the engine is
deterministic given (stimulus, seed). The process-level floor is not: CPython
randomises string hashing per process unless `PYTHONHASHSEED` is pinned, and
the engine's candidate construction walks collections whose order depends on
a string hash. Measured across six processes at the same seed, **one field
moves: M5, by exactly one new item.**

That is why the campaign runs through `benchmarks/run_matrix.py`, which
launches the six colonies with the **same** `PYTHONHASHSEED=0`, so the hash
order is a fixed environmental condition applied identically to every arm
rather than an independent draw per arm. Left unpinned, hash noise would
have entered the only comparison the campaign makes.

### 23.8 M7: the retention result, and its fragility

M7 is the metric the campaign existed to make measurable, and it moves
enormously — **212 cycles under alphabetical retention against 2,990 under
salience**. Before the substrate correction it was provably uninformative,
because the belief cap did not bind.

But the mean rests on a handful of observations, and this is disclosed
rather than buried:

| Colony | mean lifetime | beliefs that **died** | censored (alive at the end) |
|---|---:|---:|---:|
| FULL | 212.0 | **1** | 15 |
| SALIENCE | 2,989.667 | **3** | 15 |
| NO_CONTRADICTIONS | 1,790.4 | 5 | 15 |
| NO_QUESTIONS | 2,978.333 | 3 | 15 |
| NO_DREAMS | 2,989.333 | 3 | 15 |
| ANTI_EIG | 2,986.0 | 2 | 16 |

**FULL's 212-cycle mean is the mean of exactly one belief.** The robust
finding underneath is simpler: **in every arm, 15 or 16 of the beliefs never
die at all.** The retention policy changes *which* beliefs persist, not how
long they last — there are almost no deaths to time.

### 23.9 The verdicts

The five pre-registered predictions, with the noise floor applied. The floor
is the **3,000-cycle** measurement: the within-process seed floor is exactly
0.00, and the process-level floor moves exactly one field — M5 — by exactly
**one new item**, which at 3,000 cycles is a rate spread of **0.033**.

| # | Prediction | Verdict | Why |
|---|---|---|---|
| **P1** | Retention policy affects development | **SUPPORTED** | 4 of 9 metrics moved beyond the floor: M3 (+34.14), M4 (−0.104), M5 (+0.133), M7 (**+2,777.667**) |
| **P2** | Contradiction is developmental fuel | **REVERSED** | M5 **rises** by 0.166 when contradiction's weight is removed |
| **P3** | Curiosity needs explicit questions | **REVERSED** | M5 **rises** by 1.266 when question creation is removed |
| **P4** | Dreams contribute to trajectory | **SUPPORTED** | M5 **falls** by 1.000 when dreams are removed |
| **P5** | EIG is orthogonal to development | **REVERSED** | Selecting the **lowest**-EIG experiment develops 0.366 **more** per 100 cycles than the highest-EIG one |

**SUPPORTED 2 · UNSUPPORTED 0 · REVERSED 3 · NOT INTERPRETABLE 0**

**The verdicts are direction-aware, and that is the whole difference.** A
naive "did the metric move?" test would have scored all five predictions
SUPPORTED and reported a clean sweep of confirmations. Three are the
*opposite* of what was predicted: contradiction and explicit questions are
not developmental fuel and not prerequisites, and EIG selection is not
merely orthogonal — on this substrate it is **counterproductive**. The
direction check is in `benchmarks/verdicts.py`.

And "not interpretable" is empty. That is a result, not luck: the
sensitivity audit and the noise-floor measurement, both done **before** the
run, are what made every one of the five predictions decidable.

### 23.10 H24 — the hypothesis this produced

> **H24. Organica's apparent developmental plateau is primarily constrained
> by environmental information content rather than by architectural inability
> to reorganise.**

Stated as a falsifiable hypothesis, with the evidence on both sides recorded,
before the experiment that tests it is run.

**Evidence FOR H24:** the inventory saturates (74 items in the FULL arm,
zero new items in the final 100 cycles of every arm); the world repeats
every 9 cycles; evidence grows +10,776% while structure does not move; the
plateau arrives *after* the world is exhausted; and all six arms converge to
the same attractor despite six different interventions.

**Evidence AGAINST H24:** none — because **H24 has not been tested.** Every
measurement above is consistent with H24 *and* with its opposite. A human
placed in nine experiences repeated forever would also converge, and that is
not a defect.

**What would falsify it:** a larger, non-repeating world still produces ~74
distinct structures, the same plateau and the same attractor.

**The experiment that decides it** is a **world-complexity ladder** — the same
organism, the same engine, the same metrics, against worlds of increasing
information content:

| Rung | World | Predicted inventory if H24 holds |
|---|---|---|
| 0 *(done)* | `lattice_L1` — 9 events, period 9 | **74** (measured) |
| 1 | medium expanding world — new events keep arriving | ≫ 74 |
| 2 | large expanding world | ≫ rung 1 |
| 3 | open-ended world — never repeats | unbounded growth, no plateau |

Measured at every rung: **inventory growth, the cumulative discovery curve,
MBSD, theories, questions, cognitive revolutions.**

| If the inventory goes | Then |
|---|---|
| 74 → 300 → 1,200 → 5,000 | The plateau was an **environmental artifact**. What this project found is a developmental system trapped inside a toy universe. |
| 74 → 74 → 74 → 74 | The plateau is **architectural**, and the architecture — not the environment — is the ceiling. |

This is a **stimulus** experiment. Nothing about the engine changes, so the
project's standing rule holds: finish learning what V1 can teach before
changing the architecture.

### 23.11 What this means

**The campaign can answer:** the organism reaches a complete, unchanging
structural state on cycle 1 in every arm and then accumulates evidence for
2,999 cycles; the retention policy is measurable at all and changes which
beliefs persist; 5 of 9 metrics can discriminate between arms and the other
4 are permanently saturated or structurally zero; the noise floor is one
item.

**The campaign cannot answer:** which colony develops faster (M5 does not
measure development velocity); whether the organism is developmentally
reorganising or accumulating evidence (the world repeats every 9 cycles);
whether the plateau is an architectural ceiling (it may be a closed world's
complete repertoire).

**The sharpest question left behind is not about the architecture:**

> Is stabilisation the desired outcome, or evidence of a bottleneck?

and answering it needs a stimulus that does not repeat — which is a change
to the experimental design, not to the engine.

## §24 — The 1,200-cycle burst horizon and the next evaluation question

**Run record.** On 2026-10-23, the core baseline and `_burst_30` curriculum
were each run for 1,200 cycles with `seed=20261023` and the existing FULL
engine. Each run used its own temporary database. The baseline inventory was
91; the burst inventory was 128. The burst arm added 8 items between cycles
601 and 1200 and 2 in its final 100 cycles. Its cumulative curve moved from
120 at cycle 600 to 128 at cycle 1200. The earlier 600-cycle artifact recorded
119, so the one-item difference at the matched horizon is consistent with
the measured process-level enumeration noise; the later +8 is the substantive
within-run change.

**Reading.** This extends the curriculum-dependent inventory beyond 119, but
falls short of the preregistered 140+ progressive-expansion band. Discovery
continues at a low rate and is slowing; neither unbounded expansion nor a
stable attractor is established. The 1,200-cycle extension itself was
exploratory, using the 600-cycle protocol and its thresholds rather than a
separate preregistration. Full per-cycle data: `docs/scale_horizon_1200.json`.

**Runner correction.** The burst generator first introduces novelty at cycle
30, then 60, and so on; a 1,200-cycle horizon includes 39 introductions and a
600-cycle horizon includes 19. The runner previously reported 40 and 20,
respectively, because it divided the horizon by 30 without accounting for
cycle zero. This affected novelty metadata and assimilation-efficiency
denominators, not the streams or inventory counts. Corrected counts are
recorded in the 600-cycle, 1,200-cycle, and scaffold pilot artifacts.

**Next research question.** The next priority is external usefulness: a frozen
train/test prediction benchmark comparing Organica with a first-order Markov
model and a recency-decayed temporal-association baseline. It will score the
same held-out events with precision, recall, F1, Brier score and log loss.
The pilot implementation is `benchmarks/heldout_prediction.py`; its output is
`docs/heldout_prediction.json`. A known-ground-truth world and recovery scores
remain a later instrument, not a result of this prediction pilot.

**First pilot result.** Train on cycles 1–200 and score cycles 201–300 after
freezing all models. On known training tags, the first-order tag Markov model
leads Organica's Generation-1 prediction candidates: F1 **0.504 vs 0.413**,
precision **0.684 vs 0.350**, and recall **0.399 vs 0.503**. Its log loss is
**0.182 vs 0.775**. Including the nine test-only tags, F1 is **0.417 vs
0.363** and log loss **0.335 vs 0.816**. The recency-decayed temporal
association model has precision **0.704**, recall **0.370**, and known-tag F1
**0.485** at the fixed 0.5 threshold.

This is a **single-seed pilot**, not an uncertainty estimate. The tested
curriculum is synthetic, the 0.5 threshold was fixed rather than tuned, and
Organica's candidate strengths are not calibrated probabilities; its Brier
and log-loss values are therefore descriptive. On this task, the simple
Markov baseline is stronger than Organica on F1 and log loss. That is a useful
negative result and motivates a multi-seed evaluation plus a separate
known-ground-truth recovery task before drawing broader conclusions.

## §25 — Known-cause recovery pilot

`organica/ground_truth_worlds.py` generates events from two hidden causes,
switches which cause is dominant every 100 cycles, and includes 10% random
noise events from a separate feature vocabulary. The generator returns cause
and regime labels separately; the benchmark ingests event text only. The gold
target is the 12 undirected feature pairs that share a latent cause. It is a
pairwise association target, not an intervention-based causal claim.

On seed `20261023`, Organica trained on cycles 1–200 (1,600 events) recovered
all 12 gold pairs, but added 10 false-positive pairs: precision **0.545**,
recall **1.000**, F1 **0.706**. The same-event co-occurrence baseline also
recovered all 12 and added 6 false positives (F1 **0.800**). The temporal
transition graph recovered all 12 but added 138 false positives (F1 **0.148**).
The simple co-occurrence model is the strongest structural-recovery baseline
in this pilot; Organica's surviving abstractions did not improve recovery.

This generator has cleanly separated feature families, one seed, and an
arbitrary minimum edge count of 5. The last 100 cycles are not ingested, and
the score does not test whether the system predicts regime changes or selects
useful interventions. The artifact is `docs/ground_truth_recovery.json`.
Next: sweep noise rates and feature overlap, vary seeds, report uncertainty,
and score both structural recovery and held-out regime prediction.

## §26 — Phase H external-validity campaign preregistration

**Frozen before the multi-seed run on 2026-10-23.** The clean, single-seed
prediction and structure-recovery pilots above informed this protocol; they
are not counted as extra independent replicates. The campaign runs seeds
20261023–20261032 with `PYTHONHASHSEED=0` and fresh disposable databases.
The prediction curriculum is deterministic and fixed across seeds, so only
Organica's sleep RNG varies for H1; the Markov baselines repeat on the same
stream. Recovery-world samples and Organica's sleep RNG both vary for H2/H3.
No cognitive engine code changes are part of this phase.

The prediction task remains fixed at train cycles 1–200 and frozen test cycles
201–300, with a 0.5 F1 threshold, 50-cycle decay half-life, and Organica,
first-order Markov, and decayed-association models. Structure recovery uses
the same 200-cycle training window, hidden labels withheld from models, a
fixed pair threshold of 5, and Organica, same-event co-occurrence, and temporal
graph baselines. Three recovery conditions are specified in
`docs/PHASE-H-PREREGISTRATION.md`: clean (10% noise, no shared features or
decoys), overlapping (20%, two shared features, 10% decoy correlations), and
stress (30%, three shared features, 25% decoy correlations). Cause dominance
continues to switch every 100 cycles.

The report will give per-seed scores, means, standard deviations, ranges, and
deterministic 10,000-resample percentile bootstrap intervals, including paired
model differences. An Organica F1 advantage is supported only when its paired
95% interval against a simple baseline lies wholly above zero; a wholly
negative interval falsifies an advantage for that task/condition, and an
interval containing zero is inconclusive. The intervals describe only the
specified synthetic seed variation. Exact campaign output:
`docs/phase_h_results.json`; completed scores and paired difficulty trends
are analyzed in §28.

While the campaign was still running and before any scores were inspected,
the preregistration was amended to add a paired clean-to-overlap and
clean-to-stress difference-in-differences for Organica's recovery F1 advantage.
This tests whether its relative position shifts with difficulty; it does not
change the worlds, models, seeds, or primary per-condition comparisons.

Before outcome inspection, the seed description was also clarified: the
held-out curriculum is deterministic, so its seeds vary Organica's seeded
sleep RNG but do not resample input data. Recovery worlds do vary across seeds.
The campaign's results must be interpreted with that distinction.

## §27 — Live study paused pending stable V1.0.0

On 2026-10-23 at 20:26 MDT, at the owner's direction, the live study daemon
was stopped after its completed continuous-run cycle **1032**
(global `sleep_cycle=5396`). Its last cycle succeeded. A read-only health
summary of the append-only log reported 5,396 cycles, zero non-monotonic
counter steps, zero failed cycles, a 309 ms median and 631 ms maximum over the
last 50 records, and 100% theory/question duty cycles over the last 200.

The daemon process is no longer active. The current database and log were
preserved; an explicit pause marker was appended to `organica.log`. The
temporary `INTERVAL` override used to let the current cycle finish was
removed. No scheduled restart was found. Collection remains paused until a
stable V1.0.0 build is ready and reviewed; whether to continue this database
or begin a fresh run is deferred to that review. The Phase H benchmarks use
separate disposable databases and are unaffected by this pause.

## §28 — Phase H: multi-seed usefulness and structure-recovery results

The preregistered campaign completed all ten seeds (20261023–20261032) under
`PYTHONHASHSEED=0`, using three workers and separate disposable databases.
The live study remained paused. Full per-seed values and deterministic
10,000-resample percentile bootstrap intervals are in
`docs/phase_h_results.json`; the protocol and decision rules are in
`docs/PHASE-H-PREREGISTRATION.md`.

### H1 — Held-out next-event prediction

On known training tags, mean F1 was **0.412605** for Organica, **0.504039**
for first-order Markov, and **0.485072** for recency-decayed association.
Markov's paired F1 lead over Organica was **0.091434**; the decayed model's
lead was **0.072467**. Each score was identical across all ten runs, so the
bootstrap intervals are degenerate. The prediction curriculum itself is a
fixed deterministic stream; the seeds varied Organica's sleep RNG, not the
input data, and the simple baselines repeat the same score. Therefore this
confirms the original pilot on that one curriculum but does **not** provide
input-world uncertainty or ten independent world replications.

### H2/H3 — Known-cause recovery league

Mean F1 with 95% bootstrap intervals:

| Condition | Organica | Same-event co-occurrence | Temporal graph |
|---|---:|---:|---:|
| Clean | 0.7041 [0.6835, 0.7250] | **0.8000 [0.8000, 0.8000]** | 0.1482 [0.1481, 0.1484] |
| Overlapping | 0.5469 [0.5150, 0.5764] | **0.7642 [0.7632, 0.7662]** | 0.2199 [0.2162, 0.2234] |
| Stress | 0.1091 [0.0991, 0.1226] | **0.7959 [0.7959, 0.7959]** | 0.2803 [0.2792, 0.2812] |

Same-event co-occurrence outperformed Organica in every condition. Organica
outperformed the temporal graph in the clean and overlapping conditions, but
the temporal graph led in the stress condition. As difficulty increased,
Organica's relative F1 position worsened. The paired change from clean to
overlapping was **−0.121** ([−0.167, −0.077]) against co-occurrence and
**−0.229** ([−0.273, −0.187]) against the temporal graph. From clean to stress,
the changes were **−0.591** ([−0.607, −0.576]) and **−0.727**
([−0.743, −0.712]), respectively. These intervals are wholly below zero,
so the hypothesis that Organica's relative recovery advantage grows in these
harder worlds is falsified under this protocol.

**Interpretation and limits.** Organica recovered measurable signal in the
clean world and beat the temporal graph there, but the simpler co-occurrence
model remained better. Its relative performance declined with shared features,
noise, and decoy correlations; the current structural machinery did not become
more useful as this generator grew harder. This is evidence about three
controlled synthetic conditions, not natural-world external validity. The
task evaluates undirected pairwise association, not causal intervention
knowledge or held-out regime prediction. H1 does not vary its input stream.

**Next experiments.** Give H1 a preregistered seed-varying curriculum or
multiple independent held-out worlds, and score held-out regime prediction.
Then test which Organica layers contribute using controlled, task-specific
ablations; do not infer layer value from the current internal inventory.

## §29 — Phase I: preregistered regime-shift detection

Before implementation or outcome generation, Phase I froze the question,
two synthetic generator families, three prediction systems, per-world
surprise threshold, 20 seed-paired shifted/control worlds per family, and a
paired restricted-delay success criterion. Before running, the interval was
amended to 97.5% with a Bonferroni adjustment across the two family-level
opportunities, scoring was clarified to cover all next-tag transitions, and
`PYTHONHASHSEED=0` was pinned. No cognitive-engine file was changed. The full
protocol is `docs/REGIME-SHIFT-PREREGISTRATION.md`.

The 80-world campaign completed with 20 shifted and 20 stationary-control
worlds in each family. Mean restricted delay (misses capped at 31 cycles):

| Family | Organica | First-order Markov | Decayed association |
|---|---:|---:|---:|
| Cause-mixture switch | 2.55 | 2.80 | 4.25 |
| Mapping-swap | 2.65 | 1.25 | 1.20 |

All systems detected every shifted cause-mixture world except decayed
association, which detected 19/20. All systems detected all mapping-swap
worlds. In cause-mixture worlds, the paired baseline-minus-Organica delay
advantage was 0.25 cycles versus Markov (97.5% interval [−0.25, 0.75]) and
1.70 versus decayed association ([−0.05, 5.75]); both are inconclusive under
the preregistered effect-size/interval rule. Stationary-control false-alarm
rates in that family were 0% for Organica, 5% for Markov, and 0% for decayed
association.

In mapping-swap worlds, the simple baselines' mean delays were shorter, but
their stationary-control false-alarm rates were each 15% (3/20), above the
preregistered 10% gate. Baseline-minus-Organica delay was −1.40 cycles for
Markov (97.5% interval [−1.900, −0.949]) and −1.45 for decayed association
([−1.950, −0.950]). Organica's control false-alarm rate was 0%. Consequently
the mapping-swap comparison cannot count as a valid baseline win, and the
primary success rule was not met in either family. The result does not
demonstrate an Organica advantage on regime-shift detection. A future
threshold calibration would be a new protocol and must be frozen before any
further outcome generation; the completed thresholds were not tuned after
inspection.

These are replications within two synthetic generator families, not evidence
across real environments. The detector uses predictive surprise and does not
isolate the causal contribution of contradiction or belief-revision layers.
Per-world alarms, thresholds, delays, and secondary internal counts are in
`docs/regime_shift_results.json`; the corresponding fact-sheet entry is §Q.

## §30 — Phase J: gradual post-shift adaptation

### Preregistration and campaign

The Phase J protocol was committed before implementation or outcome
generation in docs/PHASE-J-ADAPTATION-PREREGISTRATION.md. It specified two
gradual-transition synthetic generator families, 20 seed-paired shifted and
stationary-control worlds per family, three online prediction systems, a
shift-specific adaptation-cost comparison, a final-stable performance guard,
and 97.5% paired bootstrap intervals. The live study remained paused, all
campaign databases were temporary, and no cognitive-engine file changed.

The campaign completed all **80 worlds** across seeds 20270101–20270120 with
PYTHONHASHSEED=0 and three workers. Full per-cycle NLL, internal-count
series, and summaries are in docs/post_shift_adaptation_results.json.

### Results

Mean NLL per predicted event over the gradual-transition and post-transition
window (cycles 30–79), stationary controls over the same cycles, and their
difference:

| Family | Model | Shifted NLL | Control NLL | Adaptation cost |
|---|---|---:|---:|---:|
| Cause-mixture ramp | Organica | 6.441 | 3.944 | 2.497 |
|  | First-order Markov | 1.234 | 1.056 | 0.178 |
|  | Decayed association | 1.221 | 1.098 | 0.122 |
| Mapping-mixture ramp | Organica | 7.702 | 4.975 | 2.727 |
|  | First-order Markov | 1.350 | 0.908 | 0.442 |
|  | Decayed association | 1.207 | 0.931 | 0.276 |

Baseline adaptation cost minus Organica adaptation cost was −2.319 nats/event
for Markov (97.5% interval [−2.798, −1.865]) and −2.375 for decayed
association ([−2.853, −1.920]) in the cause-mixture family. In the
mapping-mixture family, these differences were −2.285 ([−2.700, −1.854]) and
−2.451 ([−2.865, −2.022]). Negative values favor the baselines.

The final-stable NLL guard also failed. Organica NLL minus baseline NLL over
cycles 60–79 was +4.478 against Markov ([3.944, 4.989]) and +4.500 against
decayed association ([3.967, 5.011]) in cause-mixture worlds; mapping-mixture
gaps were +3.617 ([3.018, 4.169]) and +3.796 ([3.199, 4.348]). Neither
family met either primary gate. The measured outcome is clear for these task
instances: the simple predictive baselines had much lower error, and the
benchmark provides no evidence that Organica's additional structure improved
adaptation.

### Interpretation and limits

Organica's NLL was already much higher in stationary controls, and remained
much higher during and after the transition. The paired adaptation-cost
endpoint controls for each model's stationary level, while the final-stage
guard prevents a lower shift penalty from being called useful if shifted-world
accuracy remains substantially worse. Both comparisons favor the simple
baselines. This evaluates online next-event NLL in two synthetic gradual
transitions; it does not prove that the architecture cannot help on another
task, establish natural-world performance, or identify which cognitive layer
caused the result. The self-referenced settling-time summaries are exploratory
and are not used in the primary decision.

Protocol and runner: docs/PHASE-J-ADAPTATION-PREREGISTRATION.md and
benchmarks/post_shift_adaptation.py; full results:
docs/post_shift_adaptation_results.json; fact-sheet entry: §R.

## §31 — Correction: the structural plateau is dominant, not perfect

**Why this section exists.** Regenerating the Tier-1 campaign artifact on
2026-10-24 — `docs/force_matrix.json` re-assembled from the campaign's own
per-colony part files so that it carries the per-cycle discovery series —
meant checking every published claim against the regenerated file rather than
assuming it had survived. One did not.

**What was claimed.** §23.3 stated:

> Every colony reaches its **complete** structural configuration on the first
> cycle and does not change it again for 2,999 cycles

and gave the table *18 pre-retention beliefs / 7 competing subjects / 15
retained beliefs* for all six colonies. §23.3's own table already listed
"4–5" theories for four of the arms, so some non-constancy was being
recorded; the sentence above nonetheless asserted that the configuration was
unchanged.

**What the data actually shows.** Measured cycle by cycle from
`docs/force_matrix.json` → `series`:

| Colony | cycles at 18 beliefs / 7 subjects | of the tail half | last excursion | pool values seen |
|---|---:|---:|---:|---|
| FULL | 2,964 / 2,999 (98.8%) | 100% | cycle 212 | 18, 16 |
| SALIENCE | 2,984 / 2,999 (99.5%) | 100% | cycle 221 | 18, 16 |
| NO_CONTRADICTIONS | 2,957 / 2,999 (98.6%) | 100% | cycle 163 | 18, 16, **20** |
| **NO_QUESTIONS** | **2,277 / 2,999 (75.9%)** | **95.1%** | **cycle 2,738** | 18, 16 |
| NO_DREAMS | 2,984 / 2,999 (99.5%) | 100% | cycle 185 | 18, 16 |
| ANTI_EIG | 2,943 / 2,999 (98.1%) | 100% | cycle 539 | 18, 16 |

The excursions are brief. In the five arms other than NO_QUESTIONS they last
1–17 cycles, there are 15 to 56 of them, and all of them are over by cycle
539. The **retained** belief count is genuinely exact: 15 in every one of the
2,999 cycles of every colony.

These are real per-cycle substrate states, not a recording artifact:
`pre_beliefs` is the number of belief candidates the substrate produced before
retention (`len(beliefs)` in `benchmarks/force_matrix.py`), and
`pre_subjects_ge2` counts the subjects holding at least two of them.

**Nothing else changes.** The excursions never break a launch gate. G-P1 and
G-SUP require the belief pool to *exceed* `MAX_HYPOTHESES` (15), and 16 does.
Re-verified from the regenerated artifact, cycle by cycle:

| Gate | Requirement | Result |
|---|---|---|
| G-CS | ≥ 3 subjects hold ≥ 2 beliefs | **100% of cycles, all six colonies** |
| G-P1 / G-SUP | belief pool > 15 | **100% of cycles, all six colonies** |
| G-EXP | theories < 8 | **100% of cycles, all six colonies** |
| G-SUS | all three hold in ≥ 60% of the tail half | **100% in all six colonies** |

So the gate story, the measured noise floor, the five verdicts, the inventory
totals and the +10,776% support growth all stand exactly as published.

**The correction, stated plainly.** "Structure flat, evidence growing" is true
of the *typical* arm and needs qualification for one. Five of the six arms
settle on cycle 1 and hold 18/7 for 98–99.5% of the run and for 100% of the
tail half. **NO_QUESTIONS does not**: it sits at 16/6 for 722 of its 2,999
cycles (24%), with excursions continuing as late as cycle 2,738.

**Why the exception is the interesting part.** NO_QUESTIONS is also the arm that
discovers the most — 112 items, 95% of them by cycle 977 and 99% by cycle
2,167, against 267 cycles for FULL and 22 for NO_DREAMS — and the only arm
still finding new items deep into the run. The five arms whose structure stops
moving are the five that stop discovering; the one arm that kept discovering
kept moving. That is one arm in one run, so it is a correlation and not a
cause. But it points the same way as H24: the plateau looks like the organism
having exhausted the environment, not the organism having refused to
reorganise.

**What was done.** §23.3 is left as written, because it is the record of what
was believed on 2026-10-23. The claim is corrected in place in
`docs/FORCE-MATRIX-RESULTS.md` §2, `docs/FACTS-SHEET.md` §I1 with the
measurement in a new §S, `README.md`, `CHANGELOG.md` (in 0.8.0, with a pointer
at the 0.7.0 entry), `docs/ORGANICA-V2-DESIGN-NOTES.md`,
`docs/WORLD-SCALE-PREREGISTRATION.md` and the owner manual. Every correction
points back here. The measurement is reproducible from the artifact alone:
`docs/force_matrix.json` → `series` → `pre_beliefs`, `pre_subjects_ge2`,
`beliefs`.

## §32 — Phase K: Comparative Advantage Search

**The question changed.** Six months ago the project question was *can we
make a developmental architecture?* Today it is *what class of problems
benefits from a developmental architecture?* The second question is harder
and it is the right one, and it is only answerable by looking for the task
rather than by declaring the architecture finished.

**The evidence that forced the change.** Phases H, I and J were three
preregistered attempts to show an external advantage, and all three were
negative. That is not the same as *V1 failed*. It is:

> V1 develops interesting internal structure. We do not yet know what
> problem that structure solves.

Three tasks were negative; an infinite number of tasks were not tested. The
previous framing — three failures, therefore useless — was a mistake of
inference, and the cost of making it would have been a redesign aimed at
nothing.

### The negative-results map, as it stands

**Demonstrated**

- Development occurs.
- Curriculum affects development.
- Novelty assimilation matters.
- Developmental capacity is **not fixed** — it depends strongly on the
  structure and presentation schedule of novelty (74 → 91 → 113 → 119 →
  128 under scaffolded burst curricula).
- Uniform novelty can **harm** development (frequency dilution).
- The structural plateau is primarily an **environmental** constraint
  (H24), not an architectural ceiling — with the qualification §31
  recorded.

**Not demonstrated**

- Better next-event prediction (Phase H: 0.4126 vs 0.5040 Markov).
- Better structure recovery (Phase H: loses to co-occurrence in all three
  worlds, and to the temporal graph in the stress world).
- Better regime-shift detection (Phase I: no family met its success rule).
- Better post-shift adaptation (Phase J: both gates failed in both
  families).
- Any clear external advantage over strong simple baselines.

### The decision

**No V2.** Not "not yet" — the design of a successor architecture cannot be
justified while the advantage it would provide is unknown. Designing V2
before finding the task would make V2 guesswork.

**One more phase.** Phase K is a **search**, not a test. Its question is
*what is Organica uniquely good at?* Three candidate task families, each
derived from a mechanism the project has actually measured, each scored
against the strongest simple baseline that could plausibly solve it.

| Family | Mechanism it targets | The baseline that could beat it |
|---|---|---|
| **K1 — Incremental world modeling** | question generation drives novelty assimilation | online co-occurrence, which won Phase H at 0.8000 vs 0.7041 |
| **K2 — Belief revision** | falsification and contradiction drive revision | change-point detection plus wholesale relearning, with a forgetting window |
| **K3 — Longitudinal knowledge integration** | dreams integrate beliefs into coherent structure (P4, SUPPORTED) | sliding-window co-occurrence, which must trade retention against acquisition |

The protocol is frozen in `docs/PHASE-K-PREREGISTRATION.md`, committed before
any Phase K outcome was generated. Three things in it are worth stating
here, because they are the parts that keep this phase honest:

1. **The baselines get the tuning advantage.** Every simple baseline is swept
   over a declared grid and its *best* score is the number used. A
   strawman baseline is the most likely way to manufacture a false
   positive, and it is impossible by construction here.
2. **The harness is validated before the campaign runs.** The Phase H
   held-out task is rerun through the same code, where Organica's loss is
   already known (0.412605 vs 0.504039). If the harness reports a win
   there, the campaign does not run. A control that could only confirm
   itself would be worthless.
3. **"No family confirmed" is a pre-committed terminal outcome.** Three
   more families ruled out is a legitimate, publishable result, and it does
   not authorise a V2.

The three families were chosen *because* they match measured mechanisms, and
that is a genuine risk of false positives. It is disclosed in the
preregistration rather than hidden, and it is the reason for the three
safeguards above.

**The pilot, disclosed.** The harness was run once at one seed and one tenth
of every cycle count before the protocol was frozen, to confirm it executes.
It did, and Organica was behind the baseline in all three families. That is
one seed at ten per cent of the protocol and it is **not evidence**; it is
recorded in the preregistration so that it cannot later be mistaken for a
result. It did surface one real design fact: K3's joint endpoint is
sensitive to a hard zero, so the retention and incorporation components are
reported separately in every artifact.

> **Amendment to §32, 2026-10-24 — before any Phase K outcome was generated.**
> The first run attempt was **stopped and discarded**, not completed. The
> reason was an instrument audit, not a result: every endpoint was checked
> against a **synthetic perfect model**, and K3's joint endpoint measured
> **0.667** where 1.0 is the only sensible answer. It scored each group
> against the other group's content as false positives, so a model holding
> both the scaffold and the late structure could never reach 1.0, and the
> two components contradicted each other.
>
> Six K1 seeds had completed when the defect was found; **no K3 outcome
> existed**. K1's and K2's endpoints were provably unaffected — a perfect
> model scores exactly 1.0 on both — and K1's primary endpoint was never in
> question. All thirty seeds were re-run from scratch rather than mixing
> provenances. The audit is now permanent and runs before every campaign,
> alongside the K0 control: **K0 checks that the pipeline can report a loss;
> the ceiling check checks that the metric can report a win.** A campaign
> does not start if either fails. The full amendment, with the reasoning,
> is in `docs/PHASE-K-PREREGISTRATION.md`.

## §33 — Phase K results: three families, three losses, and what the zero means

**The search failed, and that was a pre-committed outcome.** All three
candidate families came back **REVERSED**. Not one was SUPPORTED, and not one
was INCONCLUSIVE — every 98.33% decision interval lies wholly below zero, so
each is a clean loss rather than an ambiguous one. The terminal outcome **H2**
was written into the preregistration before any Phase K outcome existed:
*"three more task families are ruled out. The negative-results map grows. Do
not design V2."* It is not being reinterpreted as a near-miss.

| Family | Organica | Best simple baseline | Paired difference | 98.33% interval | Verdict |
|---|---|---|---|---|---|
| K1 — incremental world modeling | 0.5923 | 0.9360 | −0.3437 | [−0.3773, −0.3123] | **REVERSED** |
| K2 — belief revision | 0.4111 | 0.9846 | −0.5735 | [−0.6162, −0.5309] | **REVERSED** |
| K3 — longitudinal integration | 0.0000 | 0.8578 | −0.8578 | [−0.8598, −0.8571] | **REVERSED** |

Ten seeds each, `PYTHONHASHSEED=0` in every process, the engine frozen. The
baselines were given the tuning advantage deliberately: each was swept over
its declared grid — 15 co-occurrence configurations and 9 temporal-graph
configurations, 24 per seed per family — and the **best** score used.

### Robustness

Every verdict survives the two checks that could have embarrassed it. Re-running
the bootstrap with **eight different seeds** leaves all three verdicts
unchanged, so no verdict is an artifact of the hash-derived bootstrap seed the
protocol pins. Dropping the single most favorable seed, and separately the
single least favorable seed, also leaves every verdict unchanged: with ten
seeds, one outlier cannot carry any of these intervals.

### The ablations: a negative attribution

| Family | Ablation | Ablation mean | Organica − ablation | 98.33% interval |
|---|---|---|---|---|
| K1 | `NO_QUESTIONS` | 0.6018 | −0.0095 | [−0.0328, +0.0140] |
| K2 | `NO_FALSIFICATION` | 0.3870 | +0.0241 | [−0.0048, +0.0495] |
| K3 | `NO_DREAMS` | 0.0000 | +0.0000 | [0.0000, 0.0000] |

**All three intervals contain zero.** This is the more interesting half of the
result and it is a *negative attribution*: the three mechanisms the families
were built around — question generation, falsification, dreams — are **not
load-bearing** for the tasks they were supposed to carry. In K3 the ablation
arm is identical to the decimal because the score was already zero.

The attribution is within one implementation on synthetic worlds. It says these
mechanisms do not carry these tasks in Organica 1; it does not say the
mechanisms are useless.

### The K3 zero: measured, not assumed

Organica scored **exactly 0.000 on all ten K3 seeds** while a trivial
co-occurrence counter reached 0.857. A hard zero on a metric whose ceiling was
independently proved reachable needs a cause before it is reported, and three
artifacts could have faked one. All three were checked, and each check was
capable of failing.

**1. Not a reading artifact.** The harness reads structures from the final
sleep cycle's report. A per-cycle diagnostic ran one K3 world and inspected
**every** cycle's own structures: late-group pairs appear in **zero cycles out
of 150**. The late structure is never formed at any point, so this is not the
organism forming it and then losing it.

**2. Not an under-read.** The engine emits many candidate types and the edge
extractor handles a specific set. The final cycle's structures were dumped by
type and checked for late-entity tag mentions: `hypothesis`, `loop_candidate`,
`prediction_candidate`, `process_candidate`, `workflow_concept`,
`meta_concept`, `dream`, `investigation` and `experiment` mention **0 of 12**
late tags. Only `anomaly` mentions them (5 of 12) — the engine **notices** the
late structure and does not absorb it. No late structure was sitting unread in
a type the extractor ignores.

**3. Not a blanket inability to learn late structure.** A 2×2 control crossed
the two things that could decide the outcome — which group arrives first, and
which group is stronger — across five seeds:

| early weight | late weight | early group coverage (5 seeds) | late group coverage (5 seeds) |
|---|---|---|---|
| 3 | 1 *(the protocol's K3)* | 14, 16, 15, 15, 17 | **0, 0, 0, 0, 0** |
| 3 | 3 | 13, 16, 15, 15, 17 | 0, 1, 0, 0, 0 |
| 1 | 3 | 12, 14, 14, 15, 16 | **9, 11, 10, 10, 9** |
| 1 | 1 | 13, 16, 15, 15, 17 | 0, 1, 0, 0, 0 |

The late group is incorporated **only when it is strictly stronger** than the
group that arrived first. At equal strength the earlier group wins. So the
exclusion is a **salience/priority competition under a bounded belief pool**,
not a blanket inability to learn late structure — and the protocol's K3 places
the late group at weight 1 against the scaffold's weight 3.

This is exactly the risk §6 of the preregistration named *before* the run: *"a
K3 result measures retention against incorporation under a capacity limit, not
unbounded accumulation… The scaffold entities carry weight 3 and the late
entities weight 1 precisely so that the scaffold stays observable after the
novelty arrives."* The measurement confirms the caveat was load-bearing, and
the caveat is what makes the number interpretable. **Organica retains the
early scaffold (core-retention F1 ≈ 0.67) and incorporates none of the late
structure under the specified configuration.**

### What this changes

**For V2: nothing authorises a redesign, and nothing was designed.** Six task
families are now negative — H (next-event prediction), I (regime-shift
detection), J (post-shift adaptation), and K1, K2, K3. The question *"what
class of problems benefits from a developmental architecture?"* remains open,
with six families excluded.

**The negative-results map is the deliverable.** A reader can now see that
Organica 1 loses to a co-occurrence counter on all six, and that on the two
families where a mechanism was specifically ablated, the ablation changed
nothing.

**One thing this campaign does establish, and it is not a consolation
prize:** the losses are *large and stable*, not marginal. K2's baseline scores
a perfect 1.000 on eight of ten seeds. K3's is 0.857 on nine of ten. The gap
is not noise around a tie; it is a gap, and the paired intervals are tight.
Whatever advantage a developmental architecture has, it is not on these three
kinds of task, and it is not going to appear by tuning the current engine
against them.

**A caution about the ablations.** The K1 and K2 ablation intervals contain
zero, which means the ablation did not detect a mechanism effect. It does not
follow that the mechanisms are inert in general — the ablation measures them
*on these tasks*, where the organism was already losing by a wide margin, and
a mechanism cannot show an effect if the outcome is dominated by something
else.

### The next question

Six negative families is a strong signal that the *current* engine does not
have an external advantage on any task tried so far. The honest options are
(a) keep searching more task families, and (b) stop assuming the engine is the
thing being tested. This campaign supplies evidence for (b): the mechanism
attributions came back empty on the two families where they were tested, so
the next step is to establish **which internal mechanism, if any, produces
the external advantage at all** — before another family is added to the map.
That is a question about mechanism, and it is answerable without designing V2.

> **Note on the campaign's execution.** The thirty-seed matrix ran across two
> background chunks, because the harness exceeded the runtime limit of a
> single background command. The campaign was built to survive that: results
> are written atomically, an append-only live recording
> (`docs/phase_k_results.ndjson`) is flushed after every seed, and `--resume`
> skips completed seeds. No seed was lost and no seed was re-run. One
> bookkeeping note, recorded rather than hidden: the live recording contains
> **29** of the 30 seeds, because seed K1/20261023 was completed by an earlier
> harness version before the checkpoint existed and was carried into the final
> run through the results-file resume path. The results file — the
> authoritative artifact — contains all thirty, and the two files agree
> numerically on every overlapping seed.

---

## §34 — V1 synthesis: what V1 established, and what it did not

**Why this section exists.** Six task families are now negative — Phase H
(twice), I, J, and all three of Phase K's families. The project's risk has
changed shape: it is no longer a shortage of data, it is **the risk of
drawing the wrong conclusion from data that is already there.** Six negatives
are either a map of a development-first architecture's natural properties, or
a verdict on it, and the difference between those readings decides everything
after this.

**The synthesis is a separate document**, because it is a different kind of
statement from a finding: it adds no new evidence. It is
[`docs/V1-SYNTHESIS.md`](../docs/V1-SYNTHESIS.md). Every claim in it cites a
committed artifact, and it is a *reading* of the record, not an extension of
it. Nothing in it is a new measurement.

### The one-sentence conclusion

> Organica demonstrates that a development-first architecture can generate
> history-dependent cognitive structure through experience, but it has not yet
> demonstrated that those structures confer a measurable advantage on external
> tasks.

The first half is supported by direct measurement (§§2–§2.5 of the
synthesis). The second is a negative result with a specific shape — six
families, several of them large losses rather than near-misses (§3).

### The finding that most redirects the work

**The internal developmental machinery is not what drives development.** The
Tier-1 matrix found that removing contradiction, removing question creation,
and selecting the lowest-EIG candidate each *raise* development (P2, P3, P5,
all REVERSED), and the Phase K ablations agree independently on a different
task family and substrate: `NO_QUESTIONS`, `NO_FALSIFICATION` and `NO_DREAMS`
all have intervals containing zero. What moved development, consistently, was
**the curriculum and the structure of the stimulus** — not the curiosity,
contradiction and attention machinery that was designed to be the active
ingredient.

This is a negative attribution within one implementation on synthetic worlds.
It does not say those mechanisms are inert in general. It says they are not
load-bearing *here*.

### The dangerous question, and why K3 is the most informative result

> What if Organica is already doing exactly what it was designed to do?

The architecture is optimized to **accumulate and stabilise structure**, and
the matrix found exactly that: structure fixed on cycle 1 and held for 2,999
cycles while support grew +10,776%. K3 then found that the early scaffold
dominates. That may not be a bug. It may be the purest expression of the
architecture — coherence preserved at the cost of adaptability.

The 2×2 control makes this precise rather than rhetorical: the late group
**is** incorporated when it is strictly stronger than the group that arrived
first (9–11 of 18 gold pairs at late weight 3 / early weight 1, against 0–1
otherwise). So Organica is not incapable of revision; it is **priority-ordered**,
with arrival order as the tiebreak in favor of the incumbent. The deficit is
in **displacement**, not in acquisition and not in capacity.

### The question this leaves open

Not *can we make Organica smarter*, and not *what benchmark next*:

> **What properties must a developmental intelligence have to remain adaptable
> without losing coherence?**

All six previous campaigns asked *"can Organica beat a baseline?"*. The next
one should ask *"can we find and move the property that makes plasticity and
coherence trade against each other?"* — and the discipline does not change:
pre-register it, make every harness able to fail, do not relax a gate to make
a campaign runnable, record a null as a null.

**No V2 is designed and no Phase L is launched by this section.** The
preregistered terminal outcome for Phase K stands as written.

---

## §35 — The freeze, and Phase L as a measurement phase

**What this section records.** Two decisions that are not experimental
results, and are therefore recorded here rather than in a results document:
Organica 1 is **frozen**, and Phase L is opened as a **measurement** phase.

### The freeze

**Organica 1 is frozen as of the `v0.9.0` tag (2026-10-24).** The owner's
definition was precise, and it is reproduced here because the wording matters:

> "No more architectural modifications to Organica 1. The V1 engine becomes a
> fixed reference object. Everything afterwards measures it. Nothing afterwards
> quietly changes it. The v0.9.0 tag becomes the archival reference."

Note what this is **not**. It is not abandonment, and it is not "no more
commits" — the documentation, the harnesses, the benchmarks, the action
list and the owner's decisions all keep moving. It is a freeze on the
**architecture**, and only on the architecture.

**The frozen set.** `organica/sleep.py`, `organica/memory.py`,
`organica/paths.py`, `organica/streams.py`, `organica/branch_streams.py`,
`organica/scale_streams.py`, `organica/ground_truth_worlds.py` — the files
that define what Organica 1 *is* — plus the published result artifacts.
`organica/__init__.py` is deliberately **excluded**: it carries the package
version, which has to be able to move, and it holds no cognitive logic.

**The freeze is enforced, not declared.** `tests/test_v1_freeze.py` reads the
frozen files out of the `v0.9.0` tag and compares them against the working
tree. It fails, and names the difference, when one has changed. It skips
honestly, and says so, when the tag is not reachable — which is what a
shallow clone looks like.

The first version of that test compared raw bytes and **failed on thirteen
files that nobody had touched**, because this repository checks out with
`core.autocrlf` on and the working tree's line endings differ from the blob
in the tag. That was a defect in the test, not in the freeze, and it is
worth recording because it is exactly the failure mode this project has
learned to fear: a check that fires on noise trains the reader to ignore it.
The test now asks git the question that actually matters — *would committing
this file right now change it?* — by comparing the object ID that
`git hash-object --path` produces against the blob ID in the tag.

**The mechanism was proved to fire.** A frozen file was temporarily modified
and the test watched to fail, naming the file and the differing line; the
file was then restored and the test watched to pass again. A freeze that
cannot fail is decoration.

The reasoning behind enforcing it at all is this repository's own history.
The version once named a release master was not; the changelog once linked a
404; the "structure flat" claim was an overstatement; the tag-frequency
counter measured the wrong population. Every one of those was a
documentation-versus-evidence gap, and every one was caught by an instrument
rather than by reading carefully. So the freeze is an instrument too.

### Phase L: Plasticity–Coherence Measurement

**The question changed shape.** Six task families are negative. Every one of
them asked some version of *"can Organica do X?"* — prediction, recovery,
regime shifts, adaptation, world modeling, belief revision, integration. The
next phase asks a different question:

> **How much pressure is required for new structure to displace old
> structure?**

This question is not a retry. It comes out of the strongest measured
phenomenon in V1, and the measurement that opened the door is the K3 2×2
control: the late group **is** incorporated when it is strictly stronger than
the group that arrived first (9–11 of 18 gold pairs at late weight 3 /
early weight 1, against 0–1 otherwise).

That result is the whole reason this phase is worth running. "Organica cannot
revise" is a dead end — an incapacity is boring, and it suggests no
experiment. "Organica is **priority-ordered**" is a variable: it can be
measured, it can be manipulated, and it can become a theory.

**The design follows from that.** The independent variables are varied **one
at a time**, deliberately, because a boundary that moves when five things move
at once is a correlation rather than a boundary:

| Axis | Variable | Role |
|---|---|---|
| **V1** | support ratio (late : early), 8 points | **primary** — the axis the K3 2×2 already located |
| V2 | arrival timing | does an *earlier* incumbent bind harder than a *stronger* one? |
| V3 | novelty density | does a denser late stream change the threshold, or only the latency? |
| V4 | belief-cap pressure | does the bound itself set the threshold? |
| V5 | contradiction pressure | does *conflict* displace where mere novelty does not? |

**V5 is included because it could overturn the framing.** If late structure
that *contradicts* early structure displaces it while merely *new* structure
does not, then the operative variable is conflict rather than strength, and
the phase's title is wrong. That is a result, and the protocol says so in
advance rather than discovering it later.

**The endpoints are named and the criterion is not a win.** The **Displacement
Index** is `late_structure_retained / late_structure_available`; the
**Preservation Index** is `early_structure_retained / early_structure_original`;
and the **Revision Threshold** is the pressure at which DI crosses PI. The
success criterion is **a reproducible displacement curve** — DI monotone up,
PI monotone down, an interior crossing, and a bootstrap interval excluding
both endpoints — and explicitly **not** "Organica beats a baseline". No
composite score is computed; a harmonic mean is exactly what destroyed an
endpoint in Phase K.

**The instrument audits are required and permanent.** A **discrimination
control** must show that first-seen-wins scores DI ≈ 0 / PI ≈ 1 and
last-seen-wins scores DI ≈ 1 / PI ≈ 0, so the metric can tell "never
revises" from "always revises" — and an **endpoint ceiling check** must show
a perfect model reaching 1.0 on both. Both passed when the harness was built.
The campaign does not run if either fails.

**Four terminal outcomes are pre-committed**, and **none of them authorises a
V2**. "No family confirmed" was written down before Phase K so that a negative
result could not be reinterpreted as a near-miss; the same discipline applies
here.

**Launch is not run.** The protocol is frozen and committed, the harness is
built and validated, and the protocol is reviewed **before** the campaign
executes. The synthesis' strongest recommendation was to stop producing
outcomes long enough to decide exactly what property is being measured, and a
protocol that is written and then immediately run has not had that chance.

### What this section does not claim

- It does not claim the coherence–plasticity boundary **exists**. That is
  H-L1, and it is untested until the campaign runs.
- It does not claim anything about Organica 2, which is not designed.
- It does not claim the mechanism behind displacement. DI and PI describe
  *what* displaces what, not *which layer* does it. Identifying that is a
  separate phase with its own ablation design.

---

## §36 — The pilot that looked like a negative result and was not

**What this section records.** A harness finding, not a scientific result.
The Phase L pilot returned an apparently clean answer, and the answer was an
artifact. This section records what happened, because the failure mode is
more valuable than the numbers it corrupted.

### What the pilot said

The reduced-scale execution check of the Phase L harness printed eight
identical points:

```
V1 1:4 seed 20261023: DI=0.000 PI=0.611
V1 1:3 seed 20261023: DI=0.000 PI=0.611
V1 1:2 seed 20261023: DI=0.000 PI=0.611
V1 1:1 seed 20261023: DI=0.000 PI=0.611
V1 2:1 seed 20261023: DI=0.000 PI=0.611
V1 3:1 seed 20261023: DI=0.000 PI=0.611
V1 4:1 seed 20261023: DI=0.000 PI=0.611
V1 6:1 seed 20261023: DI=0.000 PI=0.611
```

Read casually, that is a strong and publishable-looking negative result:
*the late structure never displaces the early structure, at any pressure,
anywhere on the sweep.* It is exactly the shape of the Phase K K3 result —
"the early scaffold dominates" — and it would have fit neatly into the
existing story. That fit is what made it dangerous. **A result that confirms
what you already believe is the result you are least likely to check.**

### What it actually was

The support ratio was not varying anything at all.

`build_world` took the late group's arrival cycle as an **absolute** number
(150). The pilot ran at reduced scale — 150 cycles — so the late group
arrived on the last cycle of the run and never became active. The late
structure was therefore never available, so the Displacement Index had no
denominator. And `indices()` returned `0.0` for a ratio with a zero
denominator.

So the sweep ran through eight points in which **nothing could be
displaced**, and reported "nothing was displaced" eight times.

### Why the existing audits did not catch it

This is the part worth keeping.

Phase L had two instrument audits, and both passed on that broken world:

- the **discrimination control** checked that the metric can separate
  first-seen-wins from last-seen-wins — it could, because the metric was
  fine;
- the **endpoint ceiling check** checked that a perfect model can reach 1.0
  — it could, because the metric was fine.

Both audits check the **metric**. Neither checked the **design**. The metric
was working perfectly on a world in which the thing being measured was not
present. *An audit of the instrument is not an audit of the experiment.*

### The four defects

| # | Defect | Consequence |
|---|---|---|
| 1 | Late group's arrival was an absolute cycle, not a fraction of the run | at reduced scale the late group never became active; DI had no denominator |
| 2 | A ratio with a zero denominator was reported as `0.0` | "nothing was retained" was reported for conditions in which nothing was available to retain |
| 3 | The contradiction arm shared a feature of the **late** group with itself | the arm rebuilt `late_0` unchanged; the world was byte-identical with the arm on and off, so V5 measured nothing |
| 4 | The event stream was chunked at a fixed rate while the density arm varies it | at density 4.0 the engine saw 7,200 of 28,800 events while the harness reported a complete run |

Defect 2 is the one that generalises. It is the same failure as Phase K's
collapsed harmonic mean, which is why Amendment 1 was required there: a
formula that cannot represent "not measurable" will represent it as zero
rather than refuse to answer. The project rule — *unmeasurable metrics are
reported as not measurable, excluded, never zeroed* — now has a second
instance behind it, and the harness enforces it (`None`, excluded cells
counted, an arm with any unmeasurable point returns the verdict
`UNMEASURABLE` and no scientific verdict at all).

### A fifth correction: the bootstrap measured the wrong statistic

Separate from the four, and found by reading rather than by running. The RT
bootstrap was resampling the **DI−PI gap** and reporting its minimum and
maximum. The preregistration's criterion 4 asks for the **crossing
location**: *"the RT estimated from a paired bootstrap over seeds has a
99% interval that excludes both endpoints of the sweep."* The statistic
resampled is now the index of the first label at which DI overtakes PI; the
interval is a percentile interval over those locations; seeds are resampled
**paired across labels**; and "excludes both endpoints" is tested directly
against the sweep bounds.

The old implementation would have reported a confident `rt_reproducible`
on the strength of a gap statistic that has nothing to do with where the
crossing is.

### What was added: the degeneracy audit

A third instrument audit, and the one that would have stopped all of this
before a single cell ran. For every cell of every arm it checks that:

1. both groups are available for measurement — there is a denominator;
2. the support ratio actually changes the early/late event mix;
3. the contradiction arm produces a different world from the plain arm;
4. the density arm actually changes the event count.

Every check is failable by construction, and the campaign does not run if the
audit fails. It earned its place immediately: **the first version of the
audit had a scaling inconsistency with the campaign builder** (it applied the
V2 arrival label absolutely while the campaign applied it proportionally), and
the audit caught it by failing the run before anything executed. An audit
written by the same person who wrote the code under test will inherit the
code's assumptions unless it is built to disagree with them.

After the fixes, the audit reports the late group's share of the event
stream rising monotonically across the sweep — 0.132 at 1:4 through 0.579 at
6:1 — which is the property that was silently absent before.

### After the fix

The corrected pilot, same reduced scale, one seed, **never evidence**:

```
1:4  DI=0.000  PI=0.667      3:1  DI=0.500  PI=0.278
1:3  DI=0.000  PI=0.722      4:1  DI=0.667  PI=0.000
1:2  DI=0.000  PI=0.667      6:1  DI=0.667  PI=0.000
1:1  DI=0.000  PI=0.667
2:1  DI=0.167  PI=0.611
```

The axis is now live: DI rises and PI falls across the sweep, and the curves
cross somewhere between 2:1 and 3:1. **This is a one-seed reduced-scale
pilot and it is not evidence of anything** — it is a demonstration that the
harness now measures what it claims to measure. The campaign is still
awaiting the owner's protocol review, and no Phase L outcome exists.

### The transferable lesson

> **An identical value at every point of a sweep is a measurement defect
> until proven otherwise.**

Phase K had a lesson about *not* relaxing a gate to make a campaign
runnable. This one is the mirror image: the gate was fine, the metric was
fine, and the campaign would have run perfectly and produced a confident
wrong answer. The protection is not more scrutiny of the result — it is
scrutiny of the *design*, before the run, by an instrument built to
contradict the code rather than confirm it.

Recorded in AGENTS.md as rule 13, and in the preregistration as Amendment 1.

**No Phase L campaign was run, and no Phase L outcome exists.**

---

## §37 — The protocol review, and the hunt for what the pilot did not expose

**What this section records.** A decision record, written before any Phase L
outcome existed: the owner's review of the preregistration, the changes it
produced, and a pre-flight audit aimed squarely at the degeneracies the pilot
had *not* exposed.

### The review's sharpest point: DI and PI are not opposites

This is the part worth keeping, because it is a correction to the *protocol's
framing* rather than to its arithmetic.

The protocol measures two indices: DI, how much of the late structure the
organism retains, and PI, how much of the early structure it retains. It is
tempting to read a rising DI as revision. But:

| DI | PI | what it actually is |
|---|---|---|
| 0.8 | 0.8 | **coexistence** — the late structure was learned and the early structure was kept. The organism got bigger. Nothing was displaced. |
| 0.8 | 0.1 | **genuine displacement** — the late structure replaced the early one. |

K3 had already established, before Phase L was written, that **acquisition and
displacement are different phenomena**: the late group was incorporated when
it was strictly stronger, and the deficit was in *displacement*. Yet the
Phase L metrics, read naively, would not distinguish the two cases — a curve
on which DI rises while PI holds would look like success under criterion 1
and would in fact be accumulation.

So a third quantity is now reported:

> **DS = DI − PI** — the Displacement Score.

It is a **diagnostic**, and deliberately so. It is not a primary metric, it is
not a success criterion, it enters no verdict, and it is never averaged with
anything. It exists so that a reader can see, at every sweep point, whether
the organism is *replacing* or merely *accumulating*. A curve on which DS
stays near zero while DI rises is telling us something the other two indices
cannot.

### Revision latency, elevated

The same review made a second point: **two organisms can end at the same DI
and PI while behaving completely differently.** One crosses at cycle 170, the
other at cycle 590. Same endpoint, different developmental behavior. The RT
alone would not see the difference.

Revision latency — cycles from the late group's arrival until DI first
exceeds 0.5 — was already declared in §3.4 of the protocol and was not being
computed. It is now computed and reported at the same level as the RT.

**The four success criteria are unchanged.** This is the important part.
Promoting latency from a footnote to a co-primary *report* is a change in
emphasis. Adding a fifth *criterion* would have been a change in the test,
and a test that quietly gains a criterion after the fact is the same error as
a prediction revised to fit a result.

### Hysteresis: deferred, and recorded

The most interesting proposed extension was **hysteresis** — running the axis
in reverse, late → early, to ask whether the system crosses back. If it
crosses one way and not the other, that is path-dependence, and it is the
kind of thing a genuinely dynamic intelligence might show and a static one
would not.

It is **not** in this phase. The review said so itself: not necessarily
Phase L.1, but definitely a later phase. A protocol that measures one thing
well is worth more than one that measures two things imperfectly, and
doubling the campaign before the first one has run would change its shape for
no reason. It is recorded in the protocol as the natural successor.

### The interval: 98.33% → 99%

The protocol stated a 98.33% decision interval and glossed it as "Bonferroni
across the arms". Those two statements disagree, and the disagreement was
carried in from Phase K, where 0.05/3 over three families gave exactly
98.33%. Five arms gives 0.05/5 = 0.01, i.e. **99%**.

The owner's ruling: **the intent governs and the stray percentage is the
accidental constant.** The procedure — Bonferroni across the arms — is
preserved; the number is corrected. This was settled in the open, before any
outcome existed, which is the only time it could be settled honestly. Phase
K's own figures are untouched: that protocol had three families, and 0.05/3
was correct there.

### The hunt for what the pilot did not expose

Amendment 1 fixed the defects the pilot surfaced. But the pilot's four
defects were, by construction, the ones it *could* surface. The owner's
concern was the class of bug that makes a long run worthless while looking
perfect the whole way.

So the harness was audited for the degeneracies the pilot had not exposed.
Five checks, all passing:

| Check | Result | Why it matters |
|---|---|---|
| The engine is **deterministic** for a given seed | DI 0.5 / PI 0.277778, twice | without this the paired bootstrap over seeds resamples nothing |
| Different seeds give **different** results | 4 distinct results from 4 seeds | without this there is no seed variance to resample |
| Every arm has a **full denominator** | min `late_available` = 18, min `early_available` = 18, of 18 possible | a ratio over 1 or 2 is noise |
| The **V4 belief cap binds** | peak beliefs 11 → **15** (the cap) | otherwise V4 measures the engine, not the organism |
| The protocol's **factual claims hold** | Phase K's K3 really did use 600 cycles | otherwise the "direct comparison" claim is false |

The V4 check is the one that earns its place. Phase G measured the belief pool
**starved** on the live study stream — mean 5.17 beliefs, maximum 6, against
`MAX_HYPOTHESES = 15`. If the pool never fills, the belief-cap arm cannot
change anything, and a flat V4 curve would be a statement about the engine
rather than about the organism. That is precisely how V5 was inert, and it
would have been invisible to the reader. The cap **does** bind here — peak
beliefs reach 15 — and there is now a **fourth instrument audit** that keeps
this true permanently.

### Two quietly-wrong things

Worth recording because neither would have announced itself:

- The results file recorded `"python_hash_seed": "0"` **unconditionally**. It
  asserted the pinned value whether or not it was set — a false record of the
  run's conditions, in the file whose whole purpose is to be the record. It
  now records the **actual** value, records whether the pin was met, and
  warns loudly when it was not.
- The intermediate checkpoints recomputed the **10,000-replicate bootstrap
  after every cell**. The bootstrap cannot change until an arm is complete, so
  that was hours of pure arithmetic added to the run for no new information.
  The audits had the same problem in a worse form — they rebuild worlds, and
  one of them runs the engine. Both are now computed **once** and carried.

### What this section is not

It is not a result. **No Phase L outcome existed when it was written**, and
the campaign had not been run. The protocol is amended, the instruments are
audited, the run is authorised — and the answer, whatever it is, is still
ahead.

Recorded in AGENTS.md as rule 13, in the preregistration as Amendment 2, in
the facts sheet as §W, and in the manual as §8.9.

---

## §38 — The Phase L V1 result: a crossing that reproduced, and one criterion that did not

**Run:** 2026-10-25, arm V1, 80 of 80 cells, 8,057.8 s wall clock, 10 seeds
per sweep point, `PYTHONHASHSEED=0` pinned and recorded as the actual value,
decision interval 99.00%. The engine was the frozen `v0.9.0` engine, verified
unchanged by the freeze test.

**Verdict: `H3-L — INCONCLUSIVE`.** The protocol's remedy for that verdict is
*raise n; conclude nothing*. No V2 is authorised by it.

### What the run produced

| Label | DI (sd) | PI (sd) | DS | Latency | Seeds reaching DI > 0.5 |
|---|---|---|---|---|---|
| 1:4 | 0.000 (0.000) | 0.789 (0.078) | −0.789 | — | 0/10 |
| 1:3 | 0.000 (0.000) | 0.794 (0.070) | −0.794 | — | 0/10 |
| 1:2 | 0.000 (0.000) | 0.783 (0.096) | −0.783 | — | 0/10 |
| 1:1 | 0.000 (0.000) | 0.728 (0.055) | −0.728 | — | 0/10 |
| 2:1 | 0.283 (0.124) | 0.600 (0.122) | −0.317 | — | 0/10 |
| 3:1 | 0.722 (0.037) | 0.022 (0.039) | +0.700 | 347 | 10/10 |
| 4:1 | 0.739 (0.064) | 0.000 (0.000) | +0.739 | 285 | 10/10 |
| 6:1 | 0.750 (0.029) | 0.000 (0.000) | +0.750 | 236 | 10/10 |

The pilot's flat `DI = 0.000` at all eight points is gone, and its replacement
is not a flat line in the other direction either. The axis has a shape: a
preservation plateau (1:4 through 1:1, DI exactly 0.000, PI 0.73–0.79), a
transition band (2:1, DI 0.283, PI 0.600 — coexistence, not handover), and a
displacement regime (3:1 and above, DI 0.72–0.75, PI 0.022 → 0.000).

### The three criteria that were met

DI monotone increasing with range 0.750; the curves crossing at **3:1**,
interior to the sweep; and the crossing reproducible under a 10,000-replicate
paired bootstrap over seeds, whose interval is **[5.0, 5.0]** with **10,000 of
10,000** replicates finding a crossing. Eight alternative bootstrap seeds all
returned `INTERIOR`, and dropping any one of the ten seeds left the crossing at
3:1. That is as tight as an interval over eight positions can be.

### The criterion that was not met

**PI is monotone decreasing.** The mean PI *rises* from 0.789 at 1:4 to 0.794 at
1:3 — a step of +0.005 at a point whose standard deviation is 0.070 — and then
falls monotonically through the rest of the sweep. One criterion, one
violation, one point.

It would have been easy to call this noise and move on. It was not called noise
because the criterion does not have a noise clause: it is evaluated on the mean
curve, and the mean curve rises. The criterion was evaluated once by the
committed code and it failed, and the verdict that follows from the protocol's
own table is INCONCLUSIVE.

### A wrinkle in the protocol's own labels, recorded rather than exploited

The protocol describes the `H3-L` bucket as *"intervals too wide to place RT."*
That is not what happened. The RT interval is `[5.0, 5.0]`; criterion 4 passed
comfortably; the RT was never in doubt. The verdict is INCONCLUSIVE because
**criterion 2 failed**, not because the threshold could not be located.

This is worth writing down precisely because it is the kind of thing that can
quietly become a license. Nothing was re-read, relaxed, or reinterpreted: the
verdict stands as INCONCLUSIVE and the remedy (raise n; conclude nothing)
governs. But a bucket whose label and whose stated rationale have come apart is
a drafting defect in the protocol, and the next phase should say what
"inconclusive" means when the interval is narrow and a different criterion
failed. The alternative — quietly reading INCONCLUSIVE as "close enough" because
the RT was stable — is exactly the move the pre-registration exists to prevent.

### The transferable lesson

**A criterion that passes for the wrong reason is not a stronger result than a
criterion that fails for a small reason.** The RT here is as reproducible as a
crossing can be, and the phase still does not get to claim a boundary — because
the protocol asked four questions and three were answered yes. The number of
criteria satisfied is not a score. What the phase may report is: *the crossing
is real and reproducible at 3:1, and the phase's pre-registered bar was not
cleared.*

The mirror of this lesson is the one from §37: the pilot looked like a clean
negative and was an artifact; this run looks like a clean positive and is
barred by one criterion that missed by 0.005. **Both of those are the same
lesson.** The instrument either measures what it claims or it does not, and the
protocol — not the observer — decides what the number means.

### What this section is not

It is not a claim that Organica has a coherence–plasticity boundary. The
pre-registered verdict is INCONCLUSIVE and the protocol forbids concluding
anything from it. It is not a claim about capability. It is not a claim that
support ratio is *the* operative variable beyond this axis on this engine. And
it is not a license for V2: V2–V5 were deliberately not run, because no Phase L
outcome authorises a V2.

Recorded in `docs/phase_l_results.md`, in the facts sheet as §X, and in the
manual as §8.10.

---

## §39 — The raise-n run: the bar was not cleared, and now the reason is visible

**Run:** 2026-10-25, arm V1, **240 of 240 cells**, 12,738.1 s wall clock,
**30 seeds per sweep point**, `PYTHONHASHSEED=0` pinned and recorded as the
actual value, decision interval 99.00%. The n=30 campaign is a strict
**superset** of the n=10 run: the original ten seeds are the first ten of the
new list, so the 80 original cells were **reused, not recomputed** — and the
reuse was verified, all 80 byte-identical in the merged file.

**Verdict: `H3-L — INCONCLUSIVE`.** Unchanged. And this time **two** of the
four criteria are not met.

| Criterion | n = 10 | n = 30 |
|---|---|---|
| 1. DI monotone increasing | **met** | **not met** |
| 2. PI monotone decreasing | not met | not met |
| 3. DI range ≥ 0.25, crossing interior | met | met |
| 4. RT interval excludes both endpoints | met | met |

### What did not move

The Revision Threshold did not move. At n=30 it is still **3:1**, with a
paired-bootstrap interval of **[5.0, 5.0]**, **10,000 of 10,000** replicates
finding a crossing, eight alternative bootstrap seeds all `INTERIOR`, and
leave-one-seed-out leaving it at 3:1 in **30 of 30** folds. Tripling n did
not move the one quantity the phase set out to locate.

### What moved

Criterion 1. At n=10 the DI curve was monotone; at n=30 it is not, because
the top of the curve dips by −0.007 (4:1 0.722 → 6:1 0.715).

### The shape the curve actually has

The curve is a **step function**, not a ramp. Three plateaus and two
transitions:

```
DI   0.000  0.000  0.000  0.000 │ 0.204 │ 0.706  0.722  0.715
PI   0.743  0.754  0.748  0.717 │ 0.606 │ 0.039  0.000  0.000
     1:4    1:3    1:2    1:1    │  2:1  │  3:1    4:1    6:1
     └──── plateau ────┘        └──────┘ └──── plateau ────┘
```

DI is **exactly 0.000** at the four low ratios for all thirty seeds — the
late structure is never incorporated there. PI is exactly 0.000 at 4:1 and
6:1 — the early structure is entirely gone. Revision latency goes from
**0/30** seeds reaching DI > 0.5 at 2:1 to **30/30** at 3:1 (mean 356 cycles,
median 351).

### Why the two criteria failed: both failures are signs of zero

The monotone criteria are evaluated on the **mean** curve, so each is a
statement about the **sign** of an adjacent difference. The adjacent-difference
diagnostic (Amendment 3) shows what those signs actually are:

| Step | dPI (99% paired interval) |
|---|---|
| 1:4 → 1:3 (criterion 2 fails here) | **+0.011 [−0.026, +0.044]** |
| 1:3 → 1:2 | −0.006 [−0.046, +0.033] |
| 1:2 → 1:1 | −0.031 [−0.078, +0.015] |
| 1:1 → 2:1 | −0.111 [−0.157, −0.065] |
| 2:1 → 3:1 | −0.567 [−0.619, −0.522] |
| 3:1 → 4:1 | −0.039 [−0.059, −0.020] |
| 4:1 → 6:1 (criterion 1 fails here) | +0.000 [+0.000, +0.000] |

**Both failing steps have intervals that contain zero.** Every step whose
interval excludes zero is a real transition; every step whose interval
contains zero is a plateau edge. The two failures are the signs of two
differences that are not distinguishable from zero.

### The uncomfortable part: the criteria are not stable properties

Resampling the thirty measured seeds and recomputing the four criteria:

| Criterion | random 10-seed subsets | random 20-seed subsets |
|---|---|---|
| 1. DI monotone increasing | 19.3% | 16.1% |
| 2. PI monotone decreasing | 12.0% | 6.6% |
| 3. DI range ≥ 0.25 | **100.0%** | **100.0%** |
| 3b. Crossing interior | **100.0%** | **100.0%** |
| **All four together** | **2.9%** | **1.2%** |

(The n=30 figure is 0% for criteria 1 and 2 — as measured.)

So the two robust criteria are the two that hold in every resample, and the
two fragile criteria hold in 7–19%. The n=10 run's criterion-1 pass was
itself one of the lucky 19%: the n=10 result was not "three of four, close
enough" — it was one draw out of a small number of draws that happen to
satisfy a sign test at a plateau.

**This does not re-score the protocol.** The verdict stands as INCONCLUSIVE,
no boundary is claimed, and the four criteria stand as written. But the phase
can now say something it could not say at n=10: **strict monotonicity is not
a property this organism's displacement curve has.** The low end is DI =
0.000 exactly and the high end saturates at DI ≈ 0.71. More seeds cannot
turn a plateau into a ramp, so "raise n" is exhausted as a route to
satisfying criteria 1 and 2.

### And the added seeds moved the curve more than resampling should allow

The raise-n run is not "the n=10 curve plus precision". The twenty added
seeds shifted the curve consistently, and two shifts fall outside the
resampling distribution:

| Point | original 10 | added 20 | gap | p |
|---|---|---|---|---|
| DI at 6:1 | 0.750 | 0.697 | −0.053 | **0.0022** |
| DI at 2:1 | 0.283 | 0.164 | −0.119 | **0.0103** |

Every non-zero gap points the same way — the added seeds sit lower on both
DI and PI. The seed enters the world only through `random.Random(seed)` and
the entity set does not depend on it, so the seeds *should* be exchangeable;
but the campaign's seeds are **consecutive integers**, and "the first ten
consecutive seeds versus the next twenty" is exactly what
non-exchangeability looks like and also exactly what an unlucky draw looks
like. A seed-exchangeability audit was run to tell those apart: 30 fresh,
non-consecutive, pre-declared seeds at the point with the largest gap, the
same question asked of them. It is an instrument audit — it produces no
experimental claim and cannot turn this result into a boundary claim.

**The seeds are exchangeable.** The fresh scattered set gave DI 0.7241 at
6:1 — against 0.7148 for the campaign's own 30 and 0.7500 for its original
ten — a difference of +0.0093 from the campaign's 30-seed mean, **p = 0.60**
against random 30/30 splits of all 60 measured values. And the fresh set's
own arbitrary half-split gave a gap of **−0.0407** against the campaign's
**+0.0528**: similar magnitude, opposite direction. The lumpy discrete DI
distribution (multiples of 1/18) routinely produces gaps of that size under a
split, and the direction is where the luck goes.

So **the original ten seeds were an unlucky high draw, not a seed-block
artifact** — the shift between the n=10 and n=30 curves is sampling luck, and
**the paired bootstrap over seeds is sound**. The n=30 curve is the better
estimate because there are more of them, not because they were different.

### The transferable lesson

**A criterion that flips when n changes is not a measurement of a property;
it is a measurement of the draw.** This phase went in with four criteria and
came out with two of them behaving like coin flips and two of them behaving
like facts. The way to tell the two apart is not to argue about them — it is
to ask *how often does this criterion hold across random subsets of the data
I already have?* That question is cheap, it is answerable with the data in
hand, and it converts a verdict into a characterization.

The sibling lesson is the one from §38: **strict monotonicity was the wrong
shape of test for a curve that has plateaus.** The protocol asked for a
monotone ramp; the organism produced a step function. Neither of those is
the protocol's fault — the protocol asked a clear question, and the answer
was a shape it had not imagined. What the protocol *did* do was hold its
ground: it did not let the stable RT stand in for the criteria that failed,
and it did not let "raise n" quietly become "raise n until it says what I
want."

### What this section is not

It is not a boundary claim. It is not a V2 authorisation — the secondary arms
were not run, because no Phase L outcome authorises a V2. It is not a claim
that the phase failed: `H3-L` is a pre-committed outcome with a pre-committed
remedy, and the remedy has now been taken. And it is not a license to relax a
criterion after the fact. The criteria stand; the verdict stands; what
changed is that the phase can now *say what the verdict means*.

Recorded in `docs/phase_l_results.md`, in the facts sheet as §Y, and in the
manual as §8.11.

---

## §40 — The decision: publish the characterization, and stop raising n

**What this section records.** The owner's reading of the raise-n result, the
decision taken on the strength of it, and the reasoning behind that decision.
It is a decision record, not new evidence.

### The reading

> **Organica 1 does not appear to exhibit a continuous coherence–plasticity
> trade-off. It appears to exhibit regime behavior separated by a
> reproducible transition region.**

This is the owner's sentence, and it is deliberately *not* the protocol
verdict. The two answer different questions: the protocol asked whether four
pre-committed properties hold (**no** → `H3-L — INCONCLUSIVE`), and this asks
what shape the curve actually has (**a step function**).

The owner put it sharply: raising n made the result **sharper, not cleaner**.
Normally tripling a sample makes a signal emerge or disappear; here the
crossing got stronger, the threshold got stronger, the plateaus got
stronger, and the verdict stayed negative. That is not a null result — it is a
result whose shape the protocol did not anticipate.

### What survived increasing n, and what did not

**Survived:** the preservation plateau (DI exactly 0.000 for all 30 seeds
across 1:4–1:1), the transition region, the crossing at 3:1, the reproducible
RT, and the abrupt latency shift (0/30 → 30/30 between 2:1 and 3:1).

**Did not survive:** strict monotonicity — which got *weaker*, which is
exactly what you expect if it was never a property of the organism in the
first place.

### Why raising n again is not the answer

The reason to raise n in the first place was specific: there was a plausible
world where the +0.005 PI reversal was **noise around an otherwise monotone
curve**, and another where the curve was **genuinely step-shaped**. Those
worlds predict differently, and more data distinguishes them.

**It distinguished them.** At n=30 the low-end steps are each individually
consistent with zero, the plateaus are exact across all 30 seeds, and the two
monotonicity criteria fail *more* firmly, not less. The noise-around-a-monotone-
curve world is not supported.

So the campaign was not failing for want of precision. **It was failing
because the curve is not the curve the protocol expected.** A third raise would
change nothing about the thing being measured — and "raise n until it says
what I want" is the exact failure mode a pre-registration exists to prevent.
**The protocol's remedy has been carried out to its end, and the honest move
is to report the shape, not to keep buying precision on a question the data
has already answered.**

### The decision

**Publish the characterization.** Not `H2-L` — that outcome was not reached,
and the verdict stands as `H3-L — INCONCLUSIVE`. Not "boundary established" —
the protocol says that was not established. But this *was* established:

- the displacement curve is step-like;
- the threshold location is stable and reproducible;
- the monotonic assumptions are not properties of the organism.

**Then, and only then, consider the secondary axes.** They are no longer
tests of *which variable moves a smooth boundary* — they are tests of **why
the curve is step-shaped**: what sets the width and location of the transition
region. That is a more specific question than the one Phase L was written to
answer, and it is a question about regime formation.

V2–V5 remain unrun. No Phase L outcome authorises a V2, and the owner has
not authorised one.

### The dangerous question, and the answer to it

The temptation this result creates is *"a stable, reproducible threshold at
3:1 — that is a boundary, isn't it?"*

**It is not.** A threshold is a boundary only if the trade-off is a continuum
that the threshold divides. Here the curve is flat on both sides of the
crossing, and the crossing is stable for a reason that has nothing to do with a
continuum: the organism switches regimes, and the switch is reproducible. That
is a real property — and it is not the property the protocol asked for. Calling
it one would be the same category of error as re-scoring the failed criteria,
only more flattering.

The second temptation is to let "regime behavior" become a claim about
intelligence. It is not one. Phase L measured a displacement index, a
preservation index and a latency on synthetic worlds. **"Regime" describes the
shape of those curves, and nothing more.**

### Where this lives

The published characterization is **`docs/PHASE-L-SYNTHESIS.md`**, following the
`docs/V1-SYNTHESIS.md` pattern: a formal read that adds no new evidence and
cites a committed artifact for every claim. The measurement record stays in
`docs/phase_l_results.md`, the protocol verdict stays `H3-L — INCONCLUSIVE`
everywhere, and the two are kept visibly separate.

Recorded in the facts sheet as §Z, and in the manual as §8.12.

---

## §41 — The next chapter: developmental auditability, and the record that has to exist first

**What this section records.** A decision, and the specification that follows
from it. It is a decision record and a design document, not new evidence.

### The decision

The owner's reading of the raise-n result was that the project's defining
ambition is **an intelligent blank slate that learns like a human**, and that the
results so far describe *what Organica currently does*, not what the project
should aspire to. Two north stars were separated: **A** — build a blank slate
that learns like a human; **B** — build a developmental architecture and
understand its properties. For most of the project's history they looked like
one destination. Phases H through L suggest they are not.

The operational consequence is a change in what the next experiment asks:

> **Can developmental structure support transfer? Generalization? Belief
> revision? Adaptation?**

Those are narrower, more valuable questions than *can development occur?* — which
has been answered.

### Why this section is a specification and not a protocol

The three limbs that bridge from development to transfer are **predict**, **trace**
and **revise**. Two of them are measurements against the engine's own output.
The third — *trace* — is not a measurement the engine currently supports, and it
is the one that decides whether the other two mean anything: if the organism
revises, we need to be able to show **what moved, on what evidence, and against
which competing candidates**.

So the trace was specified first. The specification is
**`docs/AUDIT-TRACE-SPEC.md`**, written against the frozen engine's actual
report fields and persistence limits rather than against an idealised version of
them.

### What the engine turned out to support

| Level | Verdict |
|---|---|
| Provenance | **Available.** Parent links exist; `get_ancestry()` reads them. Bounded by depth 7 and a 4,000-event window. |
| Evidence | **Available, with a correction.** Support counts are *temporal transitions*; "contradiction" is *competing flow*. The record format as first proposed would have mislabelled both. |
| Selection | **Available, and without instrumenting the engine** — under the default `salience` policy the whole contest is reconstructible from the report's own Layer-2/3 outputs plus the persisted priors. |

The last line is the one worth keeping. The instinct was to reach for a hook
inside the engine. The engine does not need one: every input to the retention
ranking is derivable from what the engine already exposes and what the substrate
already persists. So the plan is **assembly, not instrumentation** — with a
labelled observer build held in reserve, and the non-negotiable requirement that
an observer prove that recording the trace leaves the engine's outputs unchanged.

### Two corrections this section carries

1. **A count must be named as what it counts.** `support_count` counts temporal
   transitions. `contradiction_count` is the subject's competing flow. Neither is
   a count of observations, and the difference is the difference between an
   audit record and a plausible-sounding one.
2. **A trace is not a counterfactual.** *"Candidate B would have survived
   without A"* is a replay: a separate run, a separate artifact, its own label.
   It is never a field of the trace.

### Two defects disclosed, neither patched

**D1** — `contradiction_count` is a contention measure and reads like a
contradiction count. **D2** — the temporal graph's lookback window has **no
`event_type` filter**, so a supporting transition can originate from the
organism's own previous sleep payload, while co-occurrence and tag-frequency
edges are world-scoped. Both are recorded rather than fixed: Organica 1 is
frozen at `v0.9.0`, and D2 is a genuine finding about V1's support counts, not
a bug to patch from here.

### What is not claimed

No claim that the engine is explainable. No claim of causal explanation. No
claim that the organism learns like a human — only that the record which would
let that question be asked without taking the system's word for it has been
specified, with six acceptance criteria, each able to fail.

### Addendum — the claim was tested, and the weaker arm was reported as weaker

The specification's load-bearing claim was that the selection contest is
externally reconstructible. That claim was read out of the source, and a
specification whose central claim is unverified is a guess with citations. So
it was tested, with `benchmarks/audit_trace_probe.py` — an **instrument probe**,
not an experiment about the organism: it makes no claim about what Organica
does, only about whether an outside auditor can reproduce what the engine did.

| Arm | Belief cap | Cycles | Beliefs checked | A1 | A2 | Died | Lost on rank |
|---|---|---|---|---|---|---|---|
| Default | 15 | 120 | 1,412 | 0 failures | 120/120 | 4 | 0 |
| Stress | 5 | 60 | 290 | 0 failures | 60/60 | 3 | **403** |

**The default arm was a weak test and is reported as one.** Its pool peaked at
12 candidates against a cap of 15, so the cap never bound and **no candidate
ever lost on rank** — the branch that matters most for Level 3 went unexercised.
The stress arm tightens the budget so the pool exceeds the cap, and 403
candidates were lost on rank; the reconstruction stayed exact in both arms.

**The checks can fail.** The probe's tests break the auditor on purpose —
zeroing the curiosity term, and separately dropping a tag from the temporal
graph — and require both checks to go red. They do.

**The honest limit.** One world family, one configuration, one policy. The
probe validates the *transcription* of the rules; it does not validate the
auditor on worlds it has not seen, it says nothing about the `stochastic`
policy (where the reconstruction degrades to a bound), and it says nothing at
all about learning, transfer or capability.

Recorded in `docs/AUDIT-TRACE-SPEC.md` §10, in the facts sheet as §AA8, in the
manual as §8.13, and in the artifacts `docs/audit_trace_probe.json` and
`docs/audit_trace_probe_stress.json`.

Recorded in `docs/AUDIT-TRACE-SPEC.md`, in the manual as §8.13 and finding 18,
in the facts sheet as §AA, and in `AGENTS.md` as rule 17.

---

## §42 — The roadmap, and the rule that keeps the trace from becoming a second inventory

**What this section records.** A framing, and one rule adopted with it. It is a
decision record, not new evidence.

### The framing

Read against the whole arc, the project has moved through a coherent
progression:

| Stage | What it established |
|---|---|
| **V1** | Developmental properties: development occurs, history matters, curriculum matters, stable regimes emerge. |
| **Phase L** | Regime behavior with a stable transition region — and the protocol verdict and the characterization kept as separate artifacts. |
| **Development audit trace** | The developmental *decision* becomes reconstructible by an outside investigator. |
| **Next** | Can experience produce knowledge that **transfers, predicts and revises**? |

*What structures exist* → *what develops and survives* → *why it survived* →
*whether what it developed is usable in a new situation*.

The shift worth naming is not "can the system explain itself?" but **"can an
external investigator reconstruct what happened?"** — a stronger and much harder
standard, and one that most systems could not even aspire to.

### The rule

An audit layer is attractive, and attractive things become projects. The trace
could become the new displacement curve: built, extended and admired without
ever adjudicating a question the project wanted answered. Then it would be a
*second* inventory, and the project would have swapped one measurement habit for
another.

**So the rule is pre-committed, not aspirational:** the next protocol's success
criteria must contain at least one **trace-derived diagnostic**, and a result
that fails it **fails the protocol even if the headline behavior is correct.**

**The first instance is the disqualifier:**

> **A predicted-correct result whose supporting evidence is self-sourced is not
> a transfer result.**

This is the first concrete use of D2 — the temporal graph's lookback window has
no `event_type` filter, so a belief's support can come from the organism's own
previous sleep payload. A defect that can *defeat a claim* is worth more than a
defect that is merely recorded, and this is what turns D2 from a disclosed
limitation into a live scientific instrument.

**And the second guard:** the trace's own metrics — evidence-trace
completeness, lineage completeness, selection reproducibility — are
**diagnostics of the instrument**. Reported; never criteria. An audit layer
earns its keep by adjudicating a live question, not by accumulating
completeness.

### One precision, recorded

The framing *memory → development → auditability → intelligence* should not be
read **causally**. Auditability is an epistemic addition to the *study*, not a
developmental stage on the path to intelligence: nothing about the organism
becomes more capable because its history can be audited. What the project
*does* have is a real and unusual property — Organica preserves lineage,
parent links, generation counters and a 4,000-event working window — and that
property is what makes the audit possible. Whether lineage preservation is
*necessary* for capable development, or merely *sufficient* for auditable
development, is an open question, and it is not settled by this work.

Recorded in `docs/AUDIT-TRACE-SPEC.md` §11, in `AGENTS.md` as rule 18, in the
manual as §8.14 and finding 19, and in the facts sheet as §AA9.

---

## §43 — The probe's headline was ahead of what it verified, and the correction produced a measurement

**What this section records.** A review of the audit-trace probe, three
corrections to the specification, and a new acceptance criterion. It is a
correction record, not new evidence about the organism.

### The gap

The probe's first version reconciled the **aggregate** `precedes` table against
the engine's reported support counts. That demonstrates the auditor reproduces
Organica's *counts* and its *selection decisions*. It does **not** demonstrate
that it can identify the individual experiences behind a count — the aggregate
table does not preserve which events contributed each count, or whether they
were world events or the organism's own output. The specification had claimed
the stronger thing. **The claim was narrowed to the measurement, and the
stronger thing was made a separate test.**

**The result is now named for what it is: aggregate evidence reconciliation and
selection reconstruction passed.** Event-level attribution is now **A7**,
measured with a passive store-time observer.

### Three corrections, each verified against the source before being written down

1. **A cycle returns 14 candidate lists, not 13.** The specification's own field
   list had 14 entries under a heading that said 13.
2. **The lookback window includes the event being stored.** `store()` inserts
   the row *before* recording edges, and the window is
   `ORDER BY time DESC LIMIT 3` — so the window is the event itself plus two
   others, and **within-event tag pairs also become temporal edges**. The
   specification's first replay rule ("the three events immediately preceding
   e") was wrong.
3. **A post-hoc replay from the final log cannot reconstruct the window.** The
   engine's query has **no `rowid` tiebreak**, so under equal timestamps the
   window is not determined by the schema, and sleep-candidate rows are
   **pruned** from the log. No timestamps tied in the probe run (48 of 48
   distinct; `time.time()` showed ~0.5 ms effective resolution), but ties are
   not excluded by the schema. **Event-level attribution therefore requires a
   passive store-time observer** — and the observer's own guard must mirror the
   engine's `event_type != "sleep"` rule.

### Results

| Arm | A1 aggregate evidence | A2 selection | A7 event-level attribution | Died | Lost on rank |
|---|---|---|---|---|---|
| Default (cap 15) | 1,412 beliefs, 0 failures | 120/120 cycles | 1,412 beliefs, 0 failures, 244 edges reconcile | 4 | 0 |
| Stress (cap 5) | 290 beliefs, 0 failures | 60/60 cycles | 290 beliefs, 0 failures, 241 edges reconcile | 3 | **403** |

**A4 behavior invariance passes**: observer on and observer off produce
byte-identical reports apart from the wall-clock `ran_at`.

**What the stress arm does and does not show.** It shows the auditor can
reconstruct a **binding-cap decision** — that the ranking, not merely the pool,
is reproduced. It does **not** show that the cap commonly decides outcomes: in
the default arm it never bound at all. The honest statement is *the auditor
handles the case in which the cap decides*, not *the cap decides often*.

### D2 is now a measurement, not a worry

Of 307,857 attributed support transitions in the default arm, **53,980 (17.5%) were
self-sourced** — their prior event was the organism's own sleep payload rather
than a world event. The stress arm gives 15.3%. So on this world, roughly **one belief-support
transition in six rests on the organism's own output.** That is the baseline
against which the pre-committed disqualifier is read (§42): the criterion is
about the support *carrying a claim*, not about this average.

### The probe found two defects in itself

Its first observer attributed transitions for **sleep** events as well as world
events — the engine deliberately skips those — so the attributed totals ran an
order of magnitude above the aggregate counts, and A7 caught it. And its first
invariance check compared whole reports including `ran_at`, a wall-clock
timestamp, so two identical runs differed for a reason that had nothing to do
with behavior. Both were the auditor's errors; both were found by the checks
rather than by inspection.

**The generalisable lesson, now AGENTS rule 17(d):** *an aggregate is not an
attribution.* A check that reconciles a count against a count verifies the
arithmetic, not the provenance. **Name the resolution of every check** —
aggregate, transition, or event — because a check at one resolution does not
license a claim at another.

Recorded in `docs/AUDIT-TRACE-SPEC.md` (§2.1, §3.3, §5, §6, §10, §11), in the
manual as §8.13, in the facts sheet as §AA10, and in `AGENTS.md` as rule 17(d).

---

## §44 — The denominator was wrong, and the correction changed what the number was about

**What this section records.** A second review of the audit-trace probe: a
correction to its most quoted number, and a forced-tie arm. It is a correction
record, not new evidence about the organism.

### The denominator

The probe reported the share of *self-sourced* support transitions at **17.5%**.
That figure pooled the support of every reported belief across every cycle in
which that belief was reported. A belief's support count is **cumulative** — it
is the number of transitions on that edge so far — so a transition that
occurred early is counted again in every later cycle where the belief
survives. The pooled number is therefore a count of **support references**,
not of distinct evidence. It is a valid weighted view; it is not the share of
unique transitions.

**Three views, kept apart:**

| View | Default arm | Stress arm | What it is |
|---|---|---|---|
| **Distinct evidence behind reported beliefs** | **802 / 4,481 = 17.9%** | 384 / 2,521 = 15.2% | each transition once, restricted to the edges that back a reported belief. **The disqualifier's figure.** |
| Pooled support references | 53,980 / 307,857 = 17.5% | 4,554 / 30,529 = 14.9% | the same support counted once per belief per cycle it appears in |
| All distinct transitions recorded | 5,436 / 12,583 = 43.2% | 2,692 / 6,291 = 42.8% | every transition the observer saw, including edges no reported belief rested on |

**Correcting the denominator moved the headline only slightly** — 17.5% to 17.9% — and
that agreement is worth stating plainly: the two views were not telling
different stories.

**But the correction surfaced a separate and much larger number**: across all
12,583 distinct transitions the observer recorded, **43.2% are self-sourced** —
transitions on edges that no reported belief ever rested on. Those are the
organism's own tag-to-tag edges, the substrate of its self-generated output.
**43.2% of the organism's entire distinct transition surface is its own output, against 17.9% of the
evidence actually behind its claims.** Two surfaces, two numbers, and the trace
must report both rather than let one stand in for the other.

### A number that was wrong, and said so

An intermediate figure of **42%** was quoted before the population was pinned
down. That was the *unrestricted* distinct set — every transition the observer
recorded — and it was **not** the share of evidence behind reported beliefs.
The correct figure for the disqualifier is **17.9%**. The 42% is a real
number about a real surface, but it was quoted for the wrong surface, and the
error is recorded rather than quietly replaced.

### The forced-tie arm

The engine's lookback query is `ORDER BY time DESC LIMIT 3` with **no
tie-breaker**, so the schema does not determine which rows a tied window
selects. The forced-tie arm patches the clock so every four consecutive stores
share a timestamp, producing **479 stores with a genuinely tied window**, and requires the
observer to reproduce the engine's choice anyway.

**It does.** A7 stays exact: 2,589 distinct transitions, 241 aggregate edges reconciling,
0 mismatches; A1 692 beliefs / 0 failures; A2 60/60 cycles.

**The honest statement, which is narrower than "ties are fine":** the
**implementation** is deterministic for identical queries over identical data,
so the observer's re-run selects the same rows the engine selected. The
**schema** still does not determine the window under a tie, and a replayer
that did not observe at store time could not rely on it. The observer is the
reason, not a proof about the engine.

### The test that keeps the views apart

A new test requires the distinct view to be genuinely deduplicated: the
distinct total must be strictly less than the weighted total, and each view's
internal sum must balance. Seven tests now cover the four axes, four of them
deliberately broken variants that must go red.

Recorded in `docs/AUDIT-TRACE-SPEC.md` (§3.3, §6, §10, §11), in the manual as
§8.13, in the facts sheet as §AA11, and in the artifacts
`docs/audit_trace_probe.json`, `docs/audit_trace_probe_stress.json` and
`docs/audit_trace_probe_tie.json`.

---

## §45 — What the figure is about, and what the disqualifier now asks

**What this section records.** Two refinements from a third review of the
audit-trace work, and the one that matters most: **the disqualifier was
restated as a per-claim rule.**

### The population, stated precisely

The **17.9%** is a share of the **union of the unique evidence transitions behind beliefs reported during
the run** — deduplicated, and restricted to the edges those beliefs rested on.
It is **not** a per-claim share: a particular claim's own support can be far
more or far less self-sourced than the run-level figure. And it is **not**
evidence that self-sourced support caused an incorrect prediction — nothing
yet demonstrates that.

**A run-level share cannot carry a per-claim claim.** So the disqualifier is
now written against the claim itself, in four conditions fixed in advance:

1. Report the world/self split for the **claim's own** support.
2. A **majority** of that support must be world-derived.
3. Its self-sourced share must be **no higher than the run's baseline rate**
   for beliefs.
4. The comparison is against the claim, never the organism in general, and a
   failed condition **fails the protocol even if the prediction was correct**.

**Why the rule is conservative, and why that is stated rather than hidden.** The
contamination is now **measured, not shown to be consequential**. The
disqualifier is therefore a statement about *what counts as evidence of
transfer*, not a claim that the organism is damaged by its own output. That is
also precisely why it is pre-committed: a criterion that only bites once the
harm has been demonstrated would never bite at all.

**And the question this leaves open is now measurable:** whether a claim's
self-sourced share predicts its correctness. The trace is the first instrument
that can ask it. It is not asked here.

### The observer's window match: an implementation match, not a schema guarantee

The engine runs `SELECT tags FROM events ORDER BY time DESC LIMIT 3`. The
observer runs the **same ordering clause and limit** with a **wider
projection** — `id, time, event_type, tags, rowid` — so that the contributing
rows can be identified. The two are **not byte-identical SQL**, and SQLite
does not promise a stable order among rows that tie on `time`.

The correct statement is therefore: **the observer's window matched the
engine's in every tested case, as an empirical match on the tested SQLite
implementation** — and the evidence for that match is **A7's exactness**,
because a window mismatch on any store would have broken the reconciliation.
The forced-tie arm pushes on this deliberately: **479 stores with a genuinely tied window, 0 mismatches**.

**The 60-cycle forced-tie artifact is committed** as
`docs/audit_trace_probe_tie.json` — 60 cycles, 479 tied windows,
A1 692 beliefs / 0 failures,
A2 60/60 cycles,
A7 692 beliefs / 0 failures with 241 aggregate edges reconciling.

### A note on the review itself

One qualification in it was checked against the repository and did not hold:
the forced-tie artifact was already committed, and the 60-cycle figures in the
specification are that artifact's own. The other two qualifications were
correct, and both were adopted. The record is updated in place rather than
quietly — which is the same discipline the work is about.

Recorded in `docs/AUDIT-TRACE-SPEC.md` (§3.3, §10, §11), in the manual as
§8.14, in the facts sheet as §AA12 and §AA13, and in the artifact
`docs/audit_trace_probe_tie.json`.

---

## §46 — A threshold that judged its own data, and a window that was an order of magnitude wrong

**What this section records.** A fourth review of the audit-trace work, and
two real defects it caught: one in a pre-committed rule, one in a number this
project had been asserting.

### The threshold that judged its own data

The per-claim transfer rule's third condition read: *a claim's self-sourced
share must be no higher than **the run's baseline rate** for beliefs.* That
has a circularity in it. If the baseline is computed on the same run being
judged, then a run whose beliefs happen to be unusually self-sourced relaxes
the very criterion meant to constrain it — and the criterion's own outcome
feeds back into the threshold it is measured against. A threshold derived from
the data it judges is not a threshold.

**The reference rate is now frozen: 17.9%**, the distinct-evidence self-sourced share
measured on the calibration probe (default arm, 120 cycles). Two rules, fixed
now: it is **not recomputed on the evaluated run**, and it may only be
**re-calibrated on data that is not being judged**, with any re-calibration
recorded before the next protocol runs.

**And it is a provisional calibration value, not a precise universal cutoff.**
It rests on one run, one world, one policy (`salience`, the default). The
honest description of the condition is *"no more self-sourced than the
reference claim's support was"* — a comparison against a fixed calibration,
with all the fragility that implies.

### The window that was an order of magnitude wrong

This project asserted, in the specification and in the manual, that the
4,000-event cognition window spanned "roughly 40–130 cycles". That was a
**guess** about how many sleep events a cycle stores.

**Measured: the engine stores 2,374.68 sleep events per cycle, so the window spans 1.7 cycles.** The
estimate was wrong by more than an order of magnitude, and the correction is
recorded rather than quietly fixed.

The consequences point in opposite directions and both matter:

- A lineage that **keeps being produced** stays inside the window, because
  candidates are re-stored every cycle. Active lineages may resolve far better
  than 1.7 cycles of history suggests.
- A lineage that **stops being produced** is gone within about 1.7 cycles. The
  developmental history of anything the organism has moved on from is
  **unrecoverable** — not slowly censored, simply not there.

### A3's definition, fixed before it is measured

A criterion whose definition is written after the measurement is not a
criterion. So A3's definition is now written down:

**The two graphs stay separate.** Level 1 is developmental lineage —
candidate → candidate via `parent_ids` — and it **terminates at Layer 1**; no
parent link points at an event. Level 2 is evidential linkage — claim →
transitions → events. Level 1 answers *"where did this structure come from?"*;
Level 2 answers *"what evidence supports it?"*. **Success in one cannot stand
in for success in the other**, and asking ancestry to reach events would be
asking Level 1 to prove something it was never designed to represent.

**Three quantities, reported separately:** *lineage reachability* (share of
extant structures resolving back to Layer 1 within depth 7); *evidence linkage*
(share of extant claims whose support resolves to event ids with a world/self
split); and a *truncation split* — **aged out** (**a persistence problem**) /
**depth-truncated** (**a representation problem**) / *no parent* / *missing
record* (**a data defect**, and the one that would matter most).

**The key outcome is not the percentage.** It is whether the incompleteness
reflects **the architecture's actual developmental history** or **the
observer's retention limit**.

### Fidelity is not sufficiency

The review made one more distinction worth keeping: the probe demonstrates
that an auditor reproduces **the implemented rule**, including under a binding
cap — it does **not** establish that an intact reconstruction is a *uniquely
correct account of why a belief arose*. A reconstruction can be exactly
faithful to the algorithm and still be a shallow account of development: it
explains the arithmetic of selection, not why the structures formed. That is a
separate validation question, and A3 is where it begins.

### The question this leaves open

Whether self-sourced support *hurts*, and in what way. The candidate outcomes
— **correctness**, **persistence**, **revision resistance**, **confidence
inflation**, **false-positive rate** — are named in the specification and
pre-committed to nothing. It is a characterization study, not a protocol.

### A defect the review process caught in itself

While checking the round's edits, the substitution step found **six literal
`{...}` placeholders already committed in the specification** — `{ties}`,
`{t_dist:,}`, `{t_edges}`, `{t_cycles}`, `{t_a1:,}`, `{t_a2}` — left in
the text by the second and third review rounds, which wrote template prose
without substituting the artifact values. A seventh (`{share:.1f}`) was
introduced by this round's own script and caught before it was committed.

The placeholders sat inside sentences that assert results: *"producing
**{ties}** stores with a genuinely tied window"*, *"**The artifact is
committed:** ... {t_cycles} cycles"*. In a document that is read as a
measurement record, a literal `{ties}` reads as a number that was never
computed — it looks like a value the author was unable to produce, when in fact
the value existed in a committed artifact the whole time.

**Corrected in place, from the artifacts, not by hand:** {ties} → **479**,
`{t_dist:,}` → **2,589**, `{t_edges}` → **241**, `{t_cycles}` → **60**, `{t_a1:,}` → **692**,
`{t_a2}` → **60**, `{t_a7:,}` → **692**, `{share:.1f}` → **17.9%**. A standing check now does this: **`tests/test_doc_placeholders.py`**
scans the guarded document set for unsubstituted placeholders, asserts that
none survive, and carries its own proof-of-firing.

**The lesson is narrower than "be careful".** The third review round read this
specification closely enough to catch an over-strong claim about a denominator,
and still did not notice six literal braces — because a placeholder is *silent*.
It does not look wrong in a diff. It looks like a sentence. What caught it was
a mechanical substitution step run over the file, not another careful read.

Which is the point: **a check that must be run beats a check that must be
remembered.** Reading harder does not find braces; a substitution pass with a
leftover-assertion does.

Recorded in `docs/AUDIT-TRACE-SPEC.md` (§10, §11, §12), in the manual as
§8.14, in the facts sheet as §AA14–§AA16, in `AGENTS.md` as rule 19, and in
the artifact `docs/audit_trace_probe.json` →
`A7_event_level_attribution.cognition_window`.

---

## §47 — The window was not the constraint, and the specification said it was

**What this section records.** A3 — the ancestry check — was built against the
definition fixed in advance in spec §12, and the measurement corrected the
specification's own reasoning.

### The measurement

An ancestry auditor walks each cycle's reported structures' parent chains
against the engine's own cognition window and classifies every branch that
fails to resolve. Two links, kept apart: **Level 1** (developmental lineage,
terminating at Layer 1 — no parent link points at an event) and **Level 2**
(evidential linkage, reaching events).

- **Lineage reachability: 1.000** — 8,061 of 8,061 structures resolve back to Layer 1 within
  depth 7.
- **Evidence linkage: 1.000** — 1,412 of 1,412 claims resolve to event ids with a world/self
  split.
- **Honesty errors: 0.**
- **Truncation split (structures):** aged out 0 / depth-truncated 0 /
  no parent 0 / missing record 0.
- **Branch-level counts:** layer-1 resolved 25,168 / aged out 105 / depth-truncated 0 /
  no parent 0.

The stress arm (3,240 structures) and the forced-tie arm (3,988 structures)
both return 1.000.

**The two counts must be read together.** The structure-level split is empty,
but 105 branches were aged out. Every structure resolves because each has at least one parent
branch still inside the window. An empty split is not "nothing aged out" — it
is "nothing failed to resolve". Both are reported for that reason.

### The correction

Spec §12 said the window was **"the more likely binding constraint"**, on the
reasoning that it spans only 1.7 cycles. **That was wrong.**

**Surviving candidates are re-stored every cycle.** Layer-1 candidates go
through the natural-selection decay path (`sleep.py:1784-1800`), which writes a
decayed copy of every surviving prior candidate; higher-layer candidates are
re-derived by the report and added back from the stable prior
(`sleep.py:476-509`). So an ancestor that is still alive stays inside the
window no matter how old it is. **A lineage's depth is not bounded by the
window's recency.**

What the window bounds is the history of anything that **died**. A candidate
that decays below the death threshold is pruned and never stored again; its
last store leaves the 4,000-event window, and the parent link that pointed at
it becomes unresolvable. That is the 105 aged-out branches.

The correction is recorded in §12 and §13 rather than quietly fixed — the same
way every other correction in this project has been.

### How much history does Organica actually keep?

**Measured: the window's content age is at most 1 cycle, spanning 2 distinct cycles.** The
window holds 3,998 candidates; the oldest was last stored one cycle ago. A *dead* structure's
history is unrecoverable almost immediately; a *living* one's is recoverable
indefinitely. The difference is the decay rule, not the window.

### A3's key question, answered

§12 asked whether the incompleteness reflects the architecture's developmental
history or the observer's retention limit. The answer is that **there is no
incompleteness at the engine's window**, and the reason is sharp:

> **The observer's limit and the architecture's limit are the same limit. The
> engine's cognition window *is* its memory. An investigator cannot recover
> more developmental history than Organica retains, because there is no more
> to recover.**

That cuts both ways. It is good news for the trace — the auditor reconstructs
the lineage of everything the organism still holds, exactly, with no honesty
errors. And it is a hard ceiling on the project's distinguishing property:
**developmental provenance in Organica 1 has the horizon of the organism's own
memory.** A claim of developmental provenance reaching further back than the
organism's own window would be a claim about a history that does not exist.

### The sweeps, and what a category that never fires means

Both sweeps are diagnostics of the instrument, never criteria.

- **Window sweep:** 1.000 at the engine's window; 0.971 at 100 candidates (2
  aged out); 0.000 at 25–50 (68 aged out).
- **Depth sweep:** 1.000 at depth 7; 0.985 at depth 5; 0.809 at depth 3; 0.221
  at depth 1 (53 depth-truncated).

So **"aged out" and "depth-truncated" are both reachable**, and **the engine's
depth limit of 7 is not binding** — the chains are shorter than it. A category
that never fires is a category that has not been tested.

### Two defects the build caught in itself

Both were found by the checks rather than by inspection, and both are recorded
here because the project's rule is that corrections are documented, not
quietly updated.

1. **The observer mis-classified `meta_concept` candidates as cycle markers.**
   The candidate payload's source is `sleep:meta_concept`, and the check used
   `source.startswith("sleep:meta")` — which matches the marker prefix and
   therefore excluded every meta candidate from the record of what had ever
   been stored. The consequence was spurious **"missing record"** verdicts on
   perfectly ordinary parent links. The engine distinguishes these with an
   **exact** comparison (`source != "sleep:meta"`, `sleep.py:881` and
   `memory.py:472`), and the observer now does too.
2. **The window sweep sliced the wrong end of the window.** `recent()` orders
   by `time DESC`, so the newest candidates are at the FRONT of the list. The
   sweep took the back, and so reported the reachability of the *oldest*
   candidates. The sweep now takes the front, and a test pins the ordering so
   it cannot regress.

Recorded in `docs/AUDIT-TRACE-SPEC.md` (§6 status, §12 correction, §13), in
the manual as §8.15 and finding 21, in the facts sheet as §AA18–§AA19, in
`AGENTS.md` as rule 21, and in the artifacts as `A3_ancestry_honesty`.

---

## §48 — Carried or re-derived: two diagnostics that changed the acquisition design

**What this section records.** The owner pushed on the A3 result and asked a
better question than "how long is the history window": **what determines
whether a structure continues to be regenerated?** Two read-only diagnostic
probes were run to answer it, and they changed both the mechanism claim and
the shape of the experiment that follows.

### Diagnostic 1: is the lineage carried, or re-derived?

A surviving structure's parent set is identical in **94.5%** of 3,883 structure-cycles.
My first reading was "carried forward" — the edge set rides along with the
node. **That reading was wrong, and the second diagnostic corrected it.**

### Diagnostic 2: what do those links actually point at?

For every parent link, the state of the parent at the moment of the link:

| State of the parent | Share of 8,416 links |
|---|---|
| **Active** — re-derived from current experience in that same cycle | **87.2%** |
| **Carried** — alive in the window but not re-derived that cycle | **12.8%** |

**So the lineage is re-derived, not carried.** The identical parent sets are
*deterministic re-derivation* — the same content key produces the same
parents — not copied edges. A carried lineage would have shown a high share
of links pointing at structures that were **not** re-derived. It does not.

This is the correction the measurement discipline exists for: I stated a
mechanism from one number, and the second number refuted it.

### The engine's survival rule is asymmetric across layers

This turned out to be the fact that matters most, and it was in the source all
along.

`_natural_selection` (`sleep.py:1752-1802`) is the survival mechanism. It
reinforces a structure whose key current experience re-produced, and otherwise
decays it ×0.8 and prunes it below `DEATH_THRESHOLD = 0.15`. **But
`_candidate_key` returns `""` for every type except concept, phrase, loop and
prediction** (`sleep.py:1804-1817`). So **nothing above Layer 1 is ever
decayed or pruned by that path.**

- **Layer 1** survives only if current experience keeps producing its content
  key. This is "persistent reconstruction" proper — and it is a **hand-written
  rule**, not an emergent property.
- **Layers 2–4** are never decayed. They persist as rows while they stay in
  the window, and are re-formed with **recomputed parents** when the
  composition rules re-form them. Hypotheses die by their own rule (`1499`).

**So "persistent reconstruction" is accurate for Layer 1 and misleading for
Layers 2–4**, where continuity is closer to row persistence with re-derived
edges. The experiment must not treat "the structure survived" as one thing.

### The trace shows the present lineage, not the historical one

A candidate's identity is a content hash (`_make_id`, `sleep.py:45-48`) and
**does not include the parent set**. Higher-layer structures are re-formed
every cycle with parents recomputed. So **the same content identity can carry
a different lineage later** — measured, `meta_concept`'s parent set changed in
57 of 207 structure-cycles while its identity was unchanged.

**Consequence, and it is a hard limit on the trace's strongest claim:** the
lineage the trace shows is the organism's **current** descent. It is not
evidence of the descent as it was when the structure formed. "Reconstruction
of surviving developmental state" is right; "developmental history" is not.

### What the owner changed in the design

The owner's critique was threefold, and all three were right:

1. **Removing a parent may block future regeneration without collapsing an
   existing descendant.** So survival must be measured as a **time course**,
   and the analysis must be able to detect a **crossover** — content that
   persists and then stops being useful unless it is re-derived — rather
   than a level difference at one moment.
2. **Removing a parent from the observer's reconstruction is not the same as
   removing it from the organism's state.** The first tests the audit trace;
   only the second tests the maintenance mechanism. So the design is a
   **2 × 2 × 3 factorial**: parent {removed, not} × source experiences
   {removed, not} × removal applied to the {observer, organism}.
3. **R3 must track content identity, not row identity.** A new row may be the
   same structure re-instantiated; a persistent row may simply be retained.
   In this engine the id *is* a content hash, so identity and row are
   separable — and the measurement above separates them.

Plus a fourth point that follows from the framing: **if continuity is
persistent reconstruction rather than archival recall, then a perfect-recall
system with no re-derivation is the harder baseline, not the easier one.** So
the design adds a **replay learner** — it stores the episodes verbatim and
regenerates nothing — scored on the same three outcomes. If Organica beats it
on *"structure that remains useful after the experience is gone"*, that is a
result worth the project. If it does not, "persistent reconstruction" is
decoration and must be reported as such.

### Status

Pre-registered in `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`, committed
before any cell is run, with the two diagnostics explicitly quarantined as
**design inputs, not predictions** so that the factorial's predictions remain
pre-committed. The sharpest prediction is computed from the source rather
than fitted: a Layer-1 structure whose key stops being produced is pruned
after `⌈log(0.15 / c) / log(0.8)⌉` cycles — 4 from `c = 0.3`, 6 from `c = 0.5`.

Recorded in the manual as §8.16 and finding 22, in the facts sheet as
§AA20–§AA22, in `AGENTS.md` as rule 22, and in the pre-registration itself.

---

## §49 — The review of the acquisition plan, and five defects it found

**What this section records.** The acquisition pre-registration was reviewed
before any cell was run. Five defects were found, and the plan was rewritten as
**Revision 2**. Two of the defects would have made the study's headline
meaningless, and one of them was a metric that had been carried over from
another study without asking what it measures.

### Defect 1 — the endpoint was the wrong metric

Revision 1 scored task support with **DI**. DI is
`late_structure_retained / late_structure_available`
(`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md` §3.1) — **structural
displacement**. It does not measure whether a belief predicts the world.

**A metric imported from another study can measure a completely different
quantity, and nothing about DI looks wrong until someone asks what it
measures.** Revision 2 uses a ground-truth prediction score: for each
evaluation event and each tag in a **fixed vocabulary**, predict whether that
tag appears in the next event; ground truth is the observed next event; the
denominator is fixed so no learner can gain by scoring on a different set.
Primary metric **F1 at 0.5**, with balanced accuracy and Brier co-reported.

### Defect 2 — "source experiences removed" did not say what survived it

Ingest accumulates **`cooccurrences`** and **`tag_counts`** on every world
event (`memory.py:282`, `306`), and those outlive the event rows. So deleting
the acquisition episodes does not delete everything derived from them.

**This is not automatically a bad design** — deleting raw episodes while
retaining the compressed graph is a meaningful condition, arguably the right
one. What was wrong was the *description*: the plan called it "source
experiences removed" without saying which derived memories remain. It is now
named **"episode removal with learned graph retained"**, the retained set is
listed explicitly, and **the same rows are removed from every learner's
store** — which is what makes the comparison about *reconstruction versus
replay* rather than about *different access to evidence*.

### Defect 3 — the cell matrix was not specified

The heading said "2 × 2 × 3", §4.3 added a baseline on top of six cells, and
the prediction table listed five rows (`P-obs × E-rem` missing). Revision 2
publishes **one table with the exact number of runs** — **10 per seed, 30 seeds,
180 engine runs** — and a prediction for every cell, with `P-none × E-pres`
stated as the untreated baseline rather than an extra cell on top of six.

### Defect 4 — it was not an executable plan

Now pinned: the generator and its parameters, the target relation, the phase
boundaries (with the regime switch landing exactly on the follow-up boundary),
the seeds and sample size, the quantitative decision rule, and — for both
baselines — the algorithm, the tuning grid, the memory accounting and the
test-time procedure.

**"Same memory budget", operationally:** identical raw rows and identical
removal for every learner, with **derived state deliberately not equalised**,
because derived state *is* the mechanism under test. And the asymmetry that
remains runs **against** Organica: in the `E-pres` cells the comparison
learners can read the raw episodes Organica's cognition window has dropped.
**A win for Organica is therefore conservative.**

### Defect 5 — the audit build had no stop condition

The remaining work is smaller than the roadmap implied. **A1, A2, A3, A4 and A7
are closed and are not reopened. Only A5 and A6 remain**, and the stop
condition is now explicit: close them, regenerate the three probe arms, then
**tag, freeze and stop** — after which **no feature may be added to the
instrumentation**. A new requirement goes to the study's wish-list. The
instrumentation may be *fixed* if it is found wrong, but not *extended*.

### The owner direction, recorded

**V2 is not cut. The live study is not restarted. V2–V5 are not run. No
further open-ended audit work.** The sequence: **finish the audit build → freeze
it → run the acquisition experiment → compare against the replay learner →
publish whatever happens → only then discuss V2.**

### The charter drift, and what was done about it

`docs/DESIGN_LAWS.md` **Law II** reads: *"Every cognitive primitive must trace
an unbroken, deterministic DAG of `parent_ids` back to Generation 0 empirical
events."*

**The engine has never done that.** The A3 auditor measured it: the
`parent_ids` chain **terminates at Layer 1** — concepts, phrases, loops,
predictions — which are built from tags. **No parent link points at an event.**
The structure→event link exists only as *counts*, and the audit-trace
specification has said so since it was written.

The README's restatement was corrected. **The law itself is left as written,
with the discrepancy disclosed in the specification as D3** — because the
frozen engine's constitution is **the owner's decision, not a documentation
fix**, and this journal does not amend a charter.

### Two smaller drifts, fixed in the same pass

- The audit-trace specification said *"all six"* acceptance criteria where the
  table lists **seven**.
- The manual's status table was dated **2026-10-23** while the file recorded
  2026-10-26 work. It is refreshed, and **dated supersessions** were added to
  the README, `ROADMAP.md` and the V1 synthesis, so a new reader can tell what
  the project is doing now.

Recorded in `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` (Revision 2), in
the manual as §2 and §8.17 and finding 23, in the facts sheet as §AA23–§AA26,
in `AGENTS.md` as rule 23, and in the audit-trace specification as §6, §7 (D3)
and §9.

---

## §50 — The five claims, narrowed, and what a summary owes its checks

**What this section records.** A review of the project's own *summary* — not of
its measurements — found five sentences that were wider than the checks behind
them. All five were corrected, and the corrections were made **before the
acquisition experiment ran**, so the next study does not have to carry an
overstatement inherited from the previous one.

**Why the summary is where this defect lives.** The project's discipline has
always been aimed at the *measurement*: measure, don't infer; pre-register;
never revise a prediction to fit a result. That discipline has to reach the
**headline** as well, because the headline is the thing a reader takes away
and repeats to someone else. A measurement that is right and a sentence that
is wrong about it are separate failures, and only the second one is
invisible in the artifacts — a wrong sentence looks exactly like a right one
in a diff. This is the same shape as the defect the acquisition-plan review
found two days earlier, where **`DI` — an endpoint imported from another study
— measured a completely different quantity from the one it was asked about**.
There the wrong metric was in a *plan*; here the wrong wording was in the
*headline*, and it had already shipped into the README and three synthesis
documents.

### The five corrections

**1. "Revision exists" → "structural displacement exists."** Phase L's
`DI`/`PI` are structure-retention indices. They measure whether later
*structure* displaces earlier *structure*. They say nothing about whether a
*belief* was corrected against ground truth. That question has been measured
separately, head-to-head against a strong baseline, and Organica **lost**:
**0.4111** against the best simple baseline's **0.9846**, difference
**−0.5735**, 98.33% interval **[−0.6162, −0.5309]**, **REVERSED**. So the
project has a sharp, reproducible *structural displacement* result and a clean
*belief revision* loss, and the earlier wording let the first be read as
evidence for the second. It is not.

**2. "The 3:1 transition is remarkably stable" → "stable within this defined
experiment."** The crossing did not move when n tripled, survived a
10,000-replicate paired bootstrap at **[5.0, 5.0]**, survived eight
alternative bootstrap seeds, and survived leave-one-seed-out in **30 of 30**
folds. But the alternative bootstrap seeds **re-draw from the same measured
seeds** — they test **resampling stability, not new worlds** — and
leave-one-seed-out is the same kind of check on the same data. The scope is
therefore: *this engine, this world family, this support-ratio axis*. **3:1 is
not a general threshold for Organica**, and the number should not be quoted as
one.

**3. "Path dependence" → path dependence supported, strict order dependence not
tested.** The curriculum, scaffold, burst-assimilation and long-horizon
results all show the same thing: change the schedule, change the outcome. But
those comparisons vary the event **multiset and the order together**. An
organism that merely accumulated evidence into a commutative bag would also
look path-dependent under a schedule change, so the current evidence does not
separate "order matters" from "content matters". Isolating order requires
holding the multiset fixed and permuting only the order — and that comparison
has **not** been run.

**4. "Transfer is open" → no positive transfer has been demonstrated, and the
measured cross-domain result was negative.** Cross-domain transfer is
**−0.4863** across **12 domain pairs**, mean shared vocabulary **0.17 tags**:
the substrate is lexical co-occurrence, so there is no representation above
the tag that could cross a vocabulary boundary. **Other forms of transfer
remain untested.** So the honest sentence has two halves — the measured axis
is negative, and the untested axes are untested — and the earlier "open" hid
the first.

**5. "An independently auditable developmental record" → independently
*reconstructed*, not independently *replicated*.** What the trace establishes
is that an outside reader, given the report and the substrate, can rebuild the
developmental decision and check it. No second laboratory has reproduced this
work, and nothing in the repository is a replication result. Two further limits
sit alongside it: the trace reconstructs the organism's **surviving, current**
structures rather than the full history of their development, and **A5 and A6
are still pending**, so the audit layer is not finished.

### The compressed state, and why it is the framing

> *Organica demonstrably changes its internal structure as experience and
> curriculum change. Under one tested pressure axis, later structures can
> abruptly displace earlier ones. The project has built a strong instrument for
> auditing surviving state and implemented decisions. It has not yet shown that
> these structures yield useful knowledge or positive transfer; the acquisition
> experiment could address that, and its metric and memory-removal conditions
> are now pinned — it is pre-registered and not yet run.*

That sentence keeps the achievement — development is real — while protecting
the next experiment from being asked to prove more than it measures. It is
now the project's opening framing in the README, and it is the framing this
journal will be read against.

### What did not change

The protocol verdict `H3-L — INCONCLUSIVE` stands. The Phase L
characterization stands. The six negative task families stand. No number was
recomputed, no artifact was re-read, and no criterion was reinterpreted: this
was a correction to language, made against the existing record and recorded
rather than quietly applied.

Recorded in the README, `docs/PHASE-L-SYNTHESIS.md` (§2.2, §2.3a, §3.3, §8),
`docs/V1-SYNTHESIS.md` (§2.2, §3, §5, §9), `docs/AUDIT-TRACE-SPEC.md` (§10,
§11), `docs/EMERGENCE-CRITERIA.md` (§4), the manual as §2, §8.18, finding 24
and six new common misreadings, the facts sheet as §AB1–§AB7, and
`AGENTS.md` as rule 24.
---

## §51 — The endpoint did not test the claim; the benchmark was rebuilt; and the campaign stopped at its own gate

**What this section records.** A review of the acquisition pre-registration
found that its endpoint could not measure what the study claims to measure.
Every one of the five objections was checked against the code and the frozen
generator, and **every one was confirmed**. Two further defects were found
that the review did not raise. A third was found in the *redesign*, and it
changed the study's structure.

This is the same class of defect that killed earlier Organica hypotheses, one
level up. There, a *plan* used a metric (`DI`) that measured something else.
Here, a *plan* asked the world a question the world could not answer, and
would have scored the answer as though it did.

### What the review objected to, and what the measurements showed

**1. The task and the readout were measuring different things.** The frozen
generator draws each event's cause **independently** — the regime changes
which cause is *more common*, but consecutive events are not coupled. Measured
on the frozen world, holding the regime fixed:

| | P(next = same cause) | P(next = that cause) | difference |
|---|---|---|---|
| regime 0, `cause_a` | 0.7903 | 0.7761 | **+0.0142** |
| regime 0, `cause_b` | 0.1148 | 0.1375 | **−0.0227** |
| regime 1, `cause_a` | 0.1597 | 0.1342 | **+0.0254** |
| regime 1, `cause_b` | 0.7712 | 0.7668 | **+0.0044** |

So within a regime the causes are independent, to within 3 percentage points.
The apparent dependence in the raw numbers (0.6966 vs a 0.4551 marginal) is
**Simpson's paradox** — the shared regime block, not any coupling between
consecutive events. And the relation that the endpoint's gold set encodes
describes features co-occurring **within** one event: in the follow-up
window, a same-cause partner of the context appears in the next event only
**0.2969** of the time, while **0.3214** of next-event tags are carried over
from the context event itself. **A within-event relation does not predict the
next event.** The endpoint was asking the world a question the world never
asserted an answer to.

**2. F1 at a fixed 0.5 threshold is degenerate here — worse than suspected.**
The most common feature's next-event probability is about **0.38**. So a
*calibrated* model never crosses 0.5 and predicts nothing, while Organica's
edge readout emits hard 0/1. Scored on the frozen world's follow-up window:

| model | F1@0.5 | Brier |
|---|---|---|
| calibrated (knows the true law) | **0.0000** | 0.1080 |
| frozen-at-acquisition marginal | 0.0000 | 0.1591 |
| hard graph readout, one direction | 0.3703 | 0.1961 |
| hard graph readout, symmetric | 0.3963 | 0.2353 |
| constant zero | **0.0000** | 0.1397 |

**The Bayes-optimal model scores exactly what the trivial model scores.**
F1 at 0.5 was measuring *threshold behavior*, not knowledge quality. The
reviewer's phrasing — that F1 might compare threshold behavior rather than
learning quality — is confirmed without qualification, and the endpoint was
unusable as specified.

**3. The readout was directed; the target relation was not.**
`edges_implied_by_structures` adds concept and phrase member pairs in **one
list direction** (`for i, a in enumerate(members): for b in members[i+1:]`).
The gold same-cause pairs are **undirected**. On the frozen world, **10 of 12**
gold pairs appeared in exactly one direction — the direction is the order the
tags happened to land in the event text, not a property of the relation.

**4. The "fixed-rule ceiling" was not a prediction ceiling.** Knowing the gold
same-cause pair set tells you which features co-occur *within* an event. It
does not tell you the conditional distribution of the *next* event, which
needs the regime and the cause frequencies. The generator's marginal for a
dominant-cause tag in the follow-up regime is **0.3825**, and the gold pair
set carries **no** frequency information at all. The ceiling was a **relation
oracle** being used as a **prediction ceiling**.

**5. Retention and transfer were one number with two names.** The 110–149
window is labelled RETENTION in the phase table and is also used as TRANSFER
in the prose, while the study-level rule gates on them separately. A frozen
state scored before the switch and the same state scored after it are
**different numbers** (measured Brier **0.1583** pre-switch vs **0.1081**
post-switch), and the design only had the second one. A failure would have
been undiagnosable: it could not have distinguished "did not retain" from
"did not transfer".

### Two further defects the review did not raise

**6. The frozen engine never forms a group concept in that world.** Reading
the source: `_find_communities` is connected components on the co-occurrence
graph, and `_build_concepts` makes one concept per component, and
`edges_implied_by_structures` asserts **every pair** among a concept's
members — so a concept *would* generalize to pairs never directly
co-observed. But `_classify` requires a concept to have
`degree >= 4 and clustering <= 0.4 and predictive_reach >= 4`, and a group
defined *by* co-occurrence has **clustering 1.000** — the opposite of what
the concept rule asks for. Measured over the frozen world's 12 tags: **all
twelve classify as `unclassified`; zero concepts form.** The engine's
taxonomy has no category for "tight group". A feature sweep confirmed it is
not a threshold-tuning accident:

| features per cause | co-occurrence degree | concepts formed | relation F1 |
|---|---|---|---|
| 4 (the frozen world) | 3.0 | **0** | 0.3158 |
| 5 | 3.7 | **0** | 0.5714 |
| 6 | 4.5 | **0** | 0.5600 |
| 8 | 6.2 | **0** | 0.4444 |

Above the degree threshold and still zero concepts, because clustering stays
at 1.0. And the readout's edges came overwhelmingly from **3,604
`loop_candidate`s** and **0** concept candidates — so the graph being scored
was a **temporal adjacency** graph, not a group-relation graph. The endpoint
was asking about group structure and the readout was supplying sequence
structure.

**7. The generator's regime switch is relation-invariant.** The gold
same-cause pair set is **identical in both regimes** — the same causes, the
same feature sets; only which cause is *dominant* changes. So a
relation-scored endpoint **cannot** distinguish pre-switch from post-switch by
itself, and the transfer limb would have to be scored on a different
observable than the relation set. The world and the endpoint were pulling in
different directions.

### Three measurements that superseded the first redesign

The first redesign built a law-governed transition world and a new endpoint.
Three later measurements changed what that world could be used for. The
numbers below replace an earlier, pre-alignment set (a "ceiling" of 0.3382 /
0.3146) that no longer describes the instrument.

**A. The metric's shape, not just its threshold.** The house scoring rule
excludes `target == source`. With that exclusion the base rate is
**0.329263**; without it, **0.402159** — while the ceiling barely moves
(**0.224231** to **0.230751**). So the exclusion **shrinks the baseline's
handicap** while leaving the target nearly untouched. Measured headroom
against the base rate is **0.171408** in the self-cells shape and
**0.105032** in the house shape. The exclusion is not cosmetic; it decides
how much room the study appears to have.

**B. The readout was the limiter, not the organism.** The same frozen
structures (3,996 candidates, 10 of 16 vocabulary tags present) were scored
two ways:

| readout | house shape | self-cells shape |
|---|---|---|
| ad-hoc (0.9 for a neighbour, ~0.1/k) | 1.302721 | **1.655377** |
| base rate | 0.329263 | 0.402159 |
| backoff-smoothed graph, alpha 2.0 on a **tuning split** | **0.277761** — 0.9784 of span | **0.362233** — 0.9592 of span |
| ceiling (knows the law) | 0.224231 | 0.230751 |

The ad-hoc readout scores **worse than the base rate**; the backoff-smoothed
readout on the *same structures* reaches 0.9784 of the achievable span. Two
earlier readings of this comparison — −0.579, and then 0.940 — were
superseded; the committed artifact records 0.277761 against a 0.224231
ceiling. **The readout was the limiter.** And a readout that can turn 0.2778
into 1.3027 without the structures changing is an instrument defect, because a
scoring defect is indistinguishable from a learning failure.

**C. The redesigned world's law is first-order Markov — so counting and
understanding were not separable.** Against the strongest simple baselines,
all selected on a tuning split:

| predictor | log-loss (house shape, retention) |
|---|---|
| ceiling (knows the law) | 0.224231 |
| cell counter (strongest baseline) | 0.229878 |
| tuned bigram / decayed bigram | 0.240949 / 0.240949 |
| base rate | 0.329263 |
| grouping oracle (knows only which group it is in) | 0.252139 |
| first-order Markov on raw rows | 0.251693 |
| trivial | 2.706801 |

Headroom over the base rate is **0.105032** and would have passed the probe's
own 0.05-nat bar. Headroom over the **strongest** baseline is **0.005647**,
and would not. A plain bigram sits **0.027462** from the ceiling. The
grouping oracle alone captures **0.8679** of the span.

**The world's law *is* first-order Markov, so a bigram table is its natural
learner: "understood the law" and "counted transitions" are not separable by
a next-event score alone.** That world was therefore reclassified
**CALIBRATION / CONTROL**, not a generalization benchmark.

### The compositional task — a benchmark that can fail

A new task was built to measure what the transition world could not:
generalization to a **withheld combination** of familiar elements. Four
cells in a 2 × 2 grid of two latent factors, 4 tags each (16 total); the law
is that the successor cell differs in exactly one factor (flip-P 0.65 /
flip-Q 0.35, rotating at the regime switch); the tag-to-cell mapping is
**randomised per world**. One held cell per world has its flip-P transitions
removed **from the training stream only** — the held cell's tags remain
visible as contexts (155–202 context events per world), so the withheld thing
is a *combination*, not a tag.

Thirty independent worlds, seeds 20261200–20261229, all checks pass:

| gate | what it establishes | measured |
|---|---|---|
| **G1** | the ceiling beats the **strongest** simple baseline, with the **lower** uncertainty bound clearing 0.05 nats | gap **+0.1035**, 99 % interval **[+0.0996, +0.1074]**; binding baseline bigram in **23 / 30** worlds, cell counter in **7** |
| **G2** | a positive control holding the rule reaches the ceiling | exact |
| **G3** | a broken-rule control is clearly worse | ≥ **+0.1015** worse |
| **G4 / G4b / G4c / G4d** | the withheld combination is genuinely absent from training; the held cell is still observed; every flagged event is excluded; the split is not empty | all pass |
| **G5** | monotone in structure: ceiling < cell counter < base rate | every world |
| **G6** | the held cell varies across worlds | 4 distinct held cells |
| **G7** | **the withheld combination is what creates the gap** | held-cell **+0.1963** [+0.1901, +0.2033] vs other cells **+0.0425** [+0.0411, +0.0444] — **4.6×** |

**G7 is the load-bearing gate.** Without it, G1 could be passing because of
generic estimation error. With it, the headroom is demonstrably
*generalization* headroom on the withheld combination specifically.

A sensitivity, reported and not gated: a control with the right structure but
the two transition weights swapped is only **+0.0307** worse [+0.0283,
+0.0332]. The endpoint resolves the law's **structure** sharply and its
**weights** only weakly — a resolution fact that bounds what any result on
this task may claim.

> **The +0.1035 is the benchmark's headroom, not an Organica margin.** The
> compositional probe runs **no engine** and scores no learner. It answers
> *"is there room for something better than transition counting?"* — yes.

### The acquisition gate — where the campaign stopped

The instrument gate passed; the organism-side gate did not.

| seed | asserted structure coverage | raw temporal coverage | verdict |
|---|---|---|---|
| `20261100` (exploratory) | 0 / 112 = **0.0 %** | 112 / 112 = **100 %** | FAIL |
| `20261101`–`20261105` (diagnostic) | **0.0 % – 2.7 %** (0–3 of 112) | 112 / 112 = **100 %** | FAIL |

The world **is** in memory; the organism did not **assert** it. The cause is
one named bound: `_build_predictions` sorts candidates by raw temporal count
and truncates at `MAX_PREDICTIONS = 20`, and on this stimulus the two tags of
a cell co-occur in every event of that cell, so within-cell pairs
out-count the cross-cell transitions that carry the law and take all 20 slots.
The counterfactual audit confirmed the split: on seed `20261101` the 22
asserted `prediction_candidate` edges were 22 intra-cell and 0 inter-cell,
with **0 / 112** world overlap.

**The treatment is decisive.** Raising **only** the cap to 1,000 — same
engine, same observation stream, same five seeds, every other constant
identical — gives **98.2 %–100 %** coverage and clears the gate every time.
The failure is a **capacity limit**, not a missing signal and not a readout
defect. Downstream selection does not discard the cross-cell predictions
once admitted: they survive natural selection and decay across 110 cycles.

**Organica's readout lost.** Pilot 0, seed `20261100`, with identical raw
exposure for every learner:

| learner | retention | transfer | revision |
|---|---|---|---|
| **Organica** | **0.453018** | 0.453886 | 0.463391 |
| Replay | 0.347521 | 0.349592 | 0.351989 |
| Statistical | 0.347273 | 0.350723 | 0.352194 |
| base rate | 0.409581 | 0.409529 | 0.406084 |
| Bayes ceiling | 0.276259 | 0.272383 | 0.275208 |

Organica scored **worse than the baselines did after their episodes were
deleted** (the 0.403045 floor those cells collapse to). That is coherent
with the cause rather than surprising: the asserted structure is mostly
within-cell co-occurrence, so the readout answers *which cell the context is
in* when the task asks *which cell comes next*.

**Transfer was not measured, and it is not a transfer failure.** A seed that
fails acquisition is reported `acquisition_failed`, and transfer is reported
as not measurable. The campaign stopped at the gate; the 600-cell factorial
did not run.

### An instrument defect found while reconciling the two results

Two different functions implemented "Gate 13" under one name. The runner
evaluated the **asserted** basis, as the pre-registration's Amendment 1
requires, and failed correctly. The harness evaluated the **raw temporal**
basis, returned **100 %**, and passed — on the same seed, on the same world.
Its test asserted `passed is True`.

So the harness contained a gate that **could not fire** on the very condition
the study exists to detect. A check that cannot fire is decoration; a gate
that passes while the protocol's gate of the same name fails is worse than
decoration, because it authorises a study the protocol says is not
measurable.

**Fixed.** The harness now computes both figures, gates on the asserted one,
records `coverage_basis = "asserted_structure"`, and exposes the cap-raised
treatment so the failure can be *attributed* rather than merely observed.
The test was rewritten so that the "normal run" expectation for Gate 13 is a
**failure**, the treatment arm is asserted to **pass**, and the aggregate
prerequisite check is asserted to report the gate-13 failure at the
preregistered threshold.

### One bookkeeping consequence, recorded rather than rewritten

The pre-registration's Amendment 2 defined the confirmatory sample as thirty
seeds, `20261101` through `20261130`. Amendment 3 then designated
`20261101`–`20261105` as diagnostic preflight seeds. **Five of the thirty
confirmatory seeds are now diagnostic**, leaving a usable confirmatory sample
of **25**. The frozen amendment text is not rewritten; the consequence is
recorded here, and any future campaign must re-specify its seed set rather
than inherit one that has been partly spent.

### The lessons

**1. A benchmark must be able to fail, and so must the question it asks.** A
pre-registration can pin the seeds, the sample size, the cell matrix and the
decision rule with perfect care and still be measuring nothing — because the
*world* and the *endpoint* were never checked against each other.

**2. Run the perfect model *and the strongest simple model*, and require the
lower uncertainty bound of the gap across independent worlds.** The first
lesson was "run the perfect model and the trivial model". That was not
enough: the perfect-versus-trivial check **passed** on a world where a bigram
table was within 0.0275 nats of the ceiling. A base rate is the weakest
possible comparator. The gate that would have caught the real problem is
cheap — one more baseline over a declared grid, and a bootstrap over worlds
instead of a single number.

**3. The metric choice and the readout choice are not separable.** A hard 0/1
readout loses to the base rate under log-loss even when it holds the world's
exact edge set. Only a proper scoring rule with a soft, tuning-split-calibrated
readout can measure anything — and the readout has to be proved against the
construct *before* it is used to diagnose a learner.

**4. A grading-only control is not a control set.** "Knows the grouping"
reaches 0.87 of the achievable span. The headroom must be measured against
the strongest comparator, and the strongest comparator is often something
nobody named in the protocol.

**5. A benchmark's headroom is not a learner's margin.** The compositional
probe's +0.1035 nats is the room between the ceiling and the best simple
model. It is not what any learner achieved. Two numbers on the same task
answering two different questions are not a contradiction, and reading one as
the other is how a task-validity result gets reported as a capability result.

**6. Two gates can share a name and disagree.** The harness's Gate 13 and the
protocol's Gate 13 returned 100 % and 0.0 % on the same seed. The difference
between the two figures *was* the finding. A named gate that is implemented
twice has to be reconciled against the protocol, not against the first
implementation found.

This is the same lesson as the `DI` endpoint defect, one level up: there, a
metric imported from another study measured a different quantity; here, a
metric from the house scoring code measured a different quantity than the
claim, on a world that could not supply the quantity at all. **The endpoint
is part of the hypothesis, and it is the part that most often goes unchecked.**
---

## §52 — "Bottleneck" is not "deepest cause": the acquisition failure is a precision limit, not a capacity limit

**What this section records.** §51 established that the endpoint was wrong and
that the campaign stopped at Gate 13. The parallel session's write-up named the
cause as **`MAX_PREDICTIONS = 20`** — the prediction-candidate cap — on the
evidence that raising it to 1,000 restored coverage to 98.2 %–100 %. That
conclusion was sound on its own evidence, but it left **three probes written
and uncommitted**, and those probes ask whether there is a *better* fix than a
bigger budget.

Running them, and adding a fourth, changes the answer. **The cap is the
proximate bound. The deepest cause is precision.** All seeds used here are
diagnostic (`20261100`–`20261105`, designated by Amendment 3); the confirmatory
sample (`20261106`–`20261130`, 25 seeds) is untouched.

### Three different things are called "Gate 13", and they disagree

| What it measures | Selection rule | Coverage of the world's 112 edges | Verdict |
|---|---|---|---|
| the organism's **asserted structure** | the engine's **global** top-20 by count | **0.0000 – 0.0268** | **FAIL** (0–3 of 112) |
| the same, at raised caps | global top-K by count, K swept | 0.0000 → 1.0000 | dose-response |
| the **`precedes` table** | **top-20 *per source*** | **0.9688 – 1.0000** | **PASS** |

The third is not a third protocol. It is a **different selection rule over the
same table**, and the entire FAIL/PASS difference is that rule. This is the
third naming collision in this project, after the harness/runner pair fixed in
§51; the rule that caught it is the one written down in §51.

### Probe 1 — the 1-tag stimulus does not rescue it

Each event carries **one** tag instead of two, removing the within-cell
co-occurrence pairs by construction.

| | world edges | asserted coverage | precision | raw temporal coverage | gate 13 |
|---|---|---|---|---|---|
| 2-tag (protocol) | 112 | 0.0000 – 0.0268 | 0.35 – 0.37 | 1.0000 | 0 / 6 pass |
| **1-tag** | 128 | **0.1719 – 0.1953** | 0.3548 – 0.3731 | 0.9688 – 0.9844 | **0 / 6 pass** |

Removing one tag per event roughly **quintuples** the coverage and still fails
on every seed. The probe's own output shows the rest — the top of the
`precedes` table on the 1-tag stimulus:

```
1. type -> olive (33)          6. type -> indigo (25)
2. generation -> olive (30)    7. type -> ochre (25)
3. type -> crimson (28)        8. generation -> crimson (25)
4. type -> umber (26)          9. generation -> umber (25)
5. subject -> olive (26)      10. type -> birch (24)
```

The highest-count rows are **internal vocabulary words pointing at world
tags**. They are not relations of the world at all.

### Probe 2 — the capacity sweep: a dose-response, and no cheap budget

Five seeds, caps 20 / 40 / 80 / uncapped, engine's own selection, only the cap
changed.

| Cap | asserted coverage | intra-cell edges | **inter-cell edges** | total asserted |
|---|---|---|---|---|
| **20** (frozen) | 0.0000 – 0.0268 | 28 – 39 | **0 – 3** | 28 – 41 |
| 40 | 0.0089 – 0.0714 | 31 – 39 | 1 – 8 | 33 – 47 |
| 80 | 0.0893 – 0.1786 | 39 – 42 | 11 – 31 | 50 – 72 |
| **uncapped** | **0.9911 – 1.0000** | 52 – 53 | **188 – 192** | **240 – 244** |

**At the frozen cap the law-bearing edges are not scarce — they are absent.**
Inter-cell asserted edges are **0–3** while intra-cell ones are **28–39**: the
engine has formed the world's *partition* (which tags belong together) and
essentially none of the world's *transitions*. And "raise the cap to 1,000" is
really "remove the cap" — full coverage needs **240–244** asserted edges, about
**12×** the engine's budget of 20.

### Probe 3 — the observation protocol: the world **is** in memory

Six seeds × two stimulus shapes, reading the `precedes` table directly with
top-20 **per source**.

| World | precedes rows | world-tag pairs | RAW coverage | RAW precision | FILTERED coverage | FILTERED precision |
|---|---|---|---|---|---|---|
| 1-tag | 419 – 518 | 232 – 237 (44.8 % – 56.6 %) | 0.9688 – 0.9922 | 0.2417 – 0.3031 | 0.9688 – 0.9922 | **0.5359 – 0.5427** |
| 2-tag | 366 – 405 | 232 – 240 (59.3 % – 65.6 %) | **1.0000** (all 6) | 0.3160 – 0.3497 | **1.0000** (all 6) | **0.5333** |

The world's relations are in memory **essentially completely** — the same
`raw_temporal_coverage: 1.0` the pilot recorded, now shown to hold on every
seed. But only 44.8 %–65.6 % of the rows are world-tag pairs, and the raw
precision of a selection over the table is 0.24–0.35. Filtering to world-tag
pairs raises precision to **0.5333** at **unchanged coverage**.

> **The filter is an oracle.** It selects on the world's own tag list, which
> the organism does not have. It is **not** a legitimate fix. Its value is that
> it *quantifies the headroom*.

### Probe 4 (new) — the allocation rule: per-source is **not** the fix

Both curves computed on the same `precedes` table from the same engine run, so
the comparison is paired. `edges retained` is shown beside `coverage` so that a
fix which merely spends more budget is visible as such.

| Seed | rule | K | edges retained | coverage | precision |
|---|---|---|---|---|---|
| 20261101 | global | 20 | 20 | 0.0000 | 0.0000 |
| 20261101 | global | 80 | 80 | 0.1429 | 0.2000 |
| 20261101 | global | 160 | 160 | 0.4911 | 0.3438 |
| 20261101 | global | 320 | 320 | **0.9643** | 0.3375 |
| 20261101 | per-source | 5 | 143 | 0.2946 | 0.2308 |
| 20261101 | **per-source** | **10** | **258** | **0.7232** | 0.3140 |
| 20261102 | global | 320 | 320 | **0.9464** | 0.3312 |
| 20261103 | global | 320 | 320 | **0.9732** | 0.3406 |
| 20261103 | per-source | 10 | 286 | 0.7679 | 0.3007 |

**This overturns the hypothesis the observation-protocol probe suggested.** A
per-source allocation does *not* rescue the benchmark at a modest budget: it
needs **258–286 retained edges** to pass, and reaches only **0.72–0.77** where
the global rule reaches **0.95–0.97** at 320. At every budget and under both
rules, **precision never exceeds 0.3438**.

### The causal account

1. **The world's relations are in memory.** The `precedes` table holds all 112
   world edges (raw temporal coverage 0.97–1.00, every seed, both shapes).
2. **They are a minority of the table, and they are not the high-count rows.**
   366–518 rows for a 16-tag world; only 232–240 are world-tag pairs; the
   world's edges are roughly **a third** of what any selection must retain
   (precision ≤ 0.3438 at every budget, under both rules). The top of the table
   is internal-vocabulary edges and intra-cell pairs.
3. **Layer 1 selects on frequency, and the world is not organized by
   frequency.** At the global top-20 cut, **0–3 of 112** world edges survive
   while 28–39 intra-cell edges do.
4. **Neither a modest budget nor a modest re-allocation rescues it.** Coverage
   is a steep monotone dose-response needing ~240 edges; a per-source rule at
   the same nominal budget is not better.
5. **So the binding constraint is PRECISION, not capacity.** In a candidate
   space where the signal is a third of the rows and is not clustered at the
   top of any frequency ordering, **no frequency-based selection can pick it
   out.**

The specific pollution is **internal vocabulary**: the `precedes` table has
**27–34 distinct sources for a 16-tag world**, because the event text carries
non-tag words (`type`, `generation`, `subject`, `evidence`) that the engine
treats as vocabulary items. That is the same failure as the taxonomy
constraint of §51: the engine has no way to represent "a tight group of my own
tags", and no way to tell its own coined vocabulary from incidental words.

### The lessons

**1. A bounded selection is not a selection rule. Before enlarging a budget,
check that the ranking can find the signal at all.** The first diagnosis named
a bottleneck; the deeper diagnosis named a precision limit. The difference cost
four probes. The cheap check is three measurements: the **coverage ceiling** of
the ranking with the budget removed, the **precision at each budget**, and the
same curves under a *different* allocation rule. If precision is flat and low
across budgets and rules, the defect is the **candidate space**, and the
design question is "can this be ranked by something other than frequency?" —
not "how much budget?".

**2. The proximate bound and the deepest cause are different claims, and the
project had been using them interchangeably.** "Raising the cap restores
coverage" was true; "the cap is the cause" was true; "the cap is the deepest
cause" was **not** established, and the V2 brief was written on the
unestablished version. A brief that inherits the shallowest available account
of a failure inherits its shallowest question.

**3. A hypothesis suggested by a probe must be tested by a probe, not adopted
because it is the more hopeful reading.** The observation-protocol probe
suggested that a per-source allocation would fix things; the paired
allocation-rule probe refuted it. The refutation is the finding.

**4. An oracle filter quantifies headroom; it does not propose a fix.** The
world-vocabulary filter buys precision 0.35 → 0.5333 at no coverage cost, and
it selects on information the organism does not have. Its legitimate
counterpart — *the organism identifying its own vocabulary* — is the real
question, and it is open.

**5. A measurement that refutes the plan is not a failure of the plan; it is
the plan's first result.** The V2 capacity brief's premise ("bounded
structural allocation") was measured and did not hold. That is worth more than
a brief whose premise nobody checked.

**What does not change.** The six negative task families, the Phase L protocol
verdict `H3-L — INCONCLUSIVE`, the Phase L characterization, and the
campaign's stop at Gate 13 stand exactly as recorded. **No V2 build is
authorised.** The V2 question is narrower and sharper than it was: can the
organism identify which of its vocabulary items are its own, and can it rank
candidates by something other than raw frequency?

→ `docs/GATE13-CAUSAL-ACCOUNT.md`; `docs/gate13_capacity_sweep.json`;
`docs/gate13_allocation_rule.json`; `docs/V2-CAPACITY-DESIGN-BRIEF.md` addendum
---

## §53 — The audit build is closed, tagged and frozen

**What this section records.** The audit build's stop condition, written in
§49, was executed on 2026-10-28. This is the project's first **executed** stop
condition, and the record of it is in six places rather than one, because a
freeze that only the changelog knows about is not a freeze.

### The condition, and that it was met

§49 set the condition explicitly: *close A5 and A6 only (A1, A2, A3, A4 and A7
are closed and are not reopened), regenerate the three probe arms, then **tag,
freeze and stop**.* All four steps are done.

| Step | Status | Evidence |
|---|---|---|
| **A5** — field honesty | **closed** | `tests/test_audit_trace_probe.py::test_a5_field_honesty_fails_on_mislabelled_count` — a rendered record calling competing flow "contradictory observations" **fails the build** |
| **A6** — trace / counterfactual separation | **closed** | `tests/test_audit_trace_probe.py::test_a6_counterfactual_separation_fails_on_counterfactual_field` — a trace containing a counterfactual claim **fails the build** |
| **Three probe arms regenerated** | **done** | default, stress and forced-tie (479 stores with a genuinely tied window; 0 mismatches) |
| **Tag, freeze, stop** | **done** | tag **`audit-trace-v1`** |

Both new criteria were closed with the property the project insists on: **a
check that cannot fire is decoration.** Each has a test that deliberately
breaks the property and asserts that the build catches it.

### The tag, and the namespace decision behind it

The owner was asked how the freeze should be recorded, and chose
**`audit-trace-v1`** — an **instrumentation-only** tag — leaving the **package
version 0.10.0 untagged**.

That choice keeps the project's three version namespaces separate, which
`CHANGELOG.md` states as a rule rather than an accident:

| Namespace | Form | Current |
|---|---|---|
| Package version | `0.x.y` | **0.10.0, unreleased and untagged** |
| Architecture generation | *Organica 1*, *Organica 2* | **Organica 1**, frozen at `v0.9.0` |
| Research campaign | *Ablation Study 1*, *Ablation Study 2* | **Study 2 in flight** |

The instrumentation is not a release of the package, and tagging it as one
would have made `v0.10.0` a published artifact that nobody had asked to
publish.

### Verification at the freeze

**128 tests pass** · **83 anchors, 0 broken** · **1,142 document paths, all
exist** · the live study **untouched at 5,396 sleep cycles** with no
`organica.log`. The live daemon stays paused, and Organica 1 stays frozen at
`v0.9.0`.

### Where the freeze is recorded

A freeze only binds if the reader finds it, so the record is in **six** places:
the audit-trace specification (§9, §10), the README banner and its
"what auditable means" note, the user manual (§2 status row, the stop-condition
paragraph, findings 23 and 25), the facts sheet (AA26, AB5), `AGENTS.md` rule
23(c), and `CHANGELOG.md`. The manuscripts were updated too — paper 02 and the
papers index both said "A5/A6 remain open", which had become false.

**Journal §50 is a frozen record and was not rewritten.** It says "A5 and A6
are still pending"; that was true on 2026-10-26 and remains the historical
truth of that date. This section records the change, as §51 recorded the change
to the framing sentence.

### The lesson

**A stop condition is only real once it has been executed, and a freeze that
lives in one document is not a freeze.** The condition was written in §49 and
carried through the spec, the manual, the facts sheet and the README as a
*plan* for weeks. It took a review to notice that the plan had quietly become
the status in four different places — and the papers were still claiming
"A5/A6 remain open" while the spec said they were met. Every statement about
a build's completion state is a claim, and claims have to be corrected against
the record when the record moves.

**Corollary — the same discipline applies to the tag.** A tag is a permanent,
public, *immutable* claim about what a commit contains. Which namespace it
belongs to is therefore not a naming detail; it is a claim about what was
released, and it was put to the owner rather than decided by the agent.

### What does not change

- **Organica 1 remains frozen** at `v0.9.0`; `organica/` is not modified.
- **The live study remains paused** at 5,396 sleep cycles.
- **The acquisition campaign remains stopped at its gate** (§51), and the
  deeper causal account stands (§52). No transfer or revision result exists.
- **No V2 build is authorised.** The V2 question is narrower and sharper — can
  the organism identify which of its vocabulary items are its own, and can it
  rank candidates by something other than raw frequency? — and that is all
  that changed.
- **Law II of `docs/DESIGN_LAWS.md` remains as written**, with the discrepancy
  disclosed as D3. The frozen engine's constitution is the owner's decision.

→ `docs/AUDIT-TRACE-SPEC.md` §9, §10; `tests/test_audit_trace_probe.py`;
tag `audit-trace-v1`
---

## §54 — The separation is real, it is oracle-free, and it is not enough

**What this section records.** §52 established that the acquisition failure is
a **precision** limit, not a capacity limit. This section records the probe
that tested the sharpest open question: *can world relations be separated from
engine-generated relations, without modifying the frozen engine?*

**All seeds are diagnostic** (`20261101`-`20261103`). The confirmatory sample
(`20261106`-`20261130`, 25 seeds) is untouched.

### The mechanism, located

`organica/memory.py::store()` gates the **trigger**:

```python
if event_type != "sleep":
    self._record_cooccurrences(event.tags)
    self._record_temporal_edges(event.tags)
```

but `_record_temporal_edges` builds its **window** with an unfiltered query
(`memory.py:332`):

```python
rows = self._conn.execute(
    "SELECT tags FROM events ORDER BY time DESC LIMIT ?", (lookback,)
).fetchall()
```

A **world** event triggers recording and takes its `tag_from` from whatever rows
precede it — sleep rows included. This is **D2** in the audit-trace spec, which
disclosed the mechanism but had not measured its consequence.

### The substrate is 99.5 % the engine's own output

| Seed | world events | sleep events | ratio | `precedes` rows |
|---|---|---|---|---|
| 20261101 | 756 | **152,186** | **201x** | 373 |
| 20261102 | 761 | **235,271** | **309x** | 379 |
| 20261103 | 772 | **263,533** | **341x** | 405 |

The engine stores one sleep event per candidate per cycle. After 110 cycles it
has written **two to three hundred times** as many rows about its own thinking
as about the world. Its cognition window (`recent(n=4000, event_type="sleep")`)
is therefore almost entirely its own output — which is by design, and is not a
defect in itself. It does, however, set the scale of the problem.

### What the separation removes

The probe rebuilds the table offline and applies the engine's own rule. **Its
own proof-of-firing: the rebuilt table must match the engine's table exactly,
or the probe refuses to report.** It matched on all three seeds.

| Seed | rows removed | share of the table | **of those, sleep-sourced `tag_from`** | rows left |
|---|---|---|---|---|
| 20261101 | 133 | **35.7 %** | **100.0 %** | 240 |
| 20261102 | 139 | **36.7 %** | **100.0 %** | 240 |
| 20261103 | 165 | **40.7 %** | **100.0 %** | 240 |

**Every row the separation removes has a sleep-sourced `tag_from`.** The
contamination is not a hypothesis about what might be happening; it is exactly
the D2 mechanism, and it is a third to two-fifths of the relation table. The
remaining 240 rows are precisely the world-tag pairs (16 tags x 15).

### And it is not enough

Each table selected by the engine's own Layer-1 rule — global top-20 by count.

| Seed | table | coverage | precision | intra-cell | inter-cell | rank of first world edge |
|---|---|---|---|---|---|---|
| 20261101 | raw (engine) | 0.0000 | 0.0000 | 20 | 0 | 30 |
| | filtered LIMIT 3 | **0.0000** | 0.0000 | 20 | 0 | 35 |
| | filtered LIMIT 4 | 0.0179 | 0.1000 | 18 | 2 | **16** |
| 20261102 | raw (engine) | 0.0089 | 0.0500 | 19 | 1 | 18 |
| | filtered LIMIT 3 | **0.0000** | 0.0000 | 20 | 0 | 34 |
| | filtered LIMIT 4 | 0.0357 | 0.2000 | 16 | 4 | **8** |
| 20261103 | raw (engine) | 0.0000 | 0.0000 | 18 | 2 | 53 |
| | filtered LIMIT 3 | **0.0000** | 0.0000 | 20 | 0 | 37 |
| | filtered LIMIT 4 | 0.0446 | 0.2500 | 15 | 5 | **8** |

**With every contaminated row removed, the world's edges still do not reach the
top 20**, and the top 20 remains 75-100 % intra-cell.

The separation **does** move the world's edges up sharply — the first world
edge goes from rank 30 / 18 / 53 to **16 / 8 / 8** under LIMIT 4 — and that is
still not enough to clear the gate.

**A first edge at rank 16 is one edge arriving, not the world's relations
arriving.** The distribution beside it is what matters: under the engine's own
global count-ranked selection the world's 112 edges are **spread through the
table, not clustered at its top**.

| Selection (global count-ranked) | world edges recovered, of 112 |
|---|---|
| top 20 — the engine's own budget | **0 – 1** |
| top 40 | **0 – 2** |
| top 80 | **8 – 16** |
| top 160 | **36 – 55** |
| top 320 — about 16× the engine's budget of 20 | **106 – 109** |

(`docs/gate13_allocation_rule.json`, 3 seeds.) The five-seed capacity sweep puts
the cap at 40 at **1 – 8 of 112** and the frozen cap of 20 at **0 – 3 of 112**
(`docs/gate13_capacity_sweep.json`). *Corrected 2026-10-30:* the first-edge rank
was previously reported without this distribution, which made the ranking problem
look nearly solved.

### Why the remaining competition is intra-cell

A cell's two tags co-occur in **every** event of that cell, so an intra-cell
pair accumulates a count of the order of (events / cells). The world's
transitions are individual tag-level transitions under a cell-level law, so a
specific tag pair follows the law only a fraction of the time. The two
populations differ by roughly an order of magnitude in count, and a global
count-ranked cut of 20 is consumed by the first population entirely.

**This is why two probes seemed to disagree about which mechanism dominates.**
In the **1-tag** stimulus an event carries one tag, so there are no intra-cell
co-occurrence pairs to compete — and there the crowding **is** the internal
vocabulary (first world edge at rank 31; the top 30 rows all `internal->world`,
verified). In the **2-tag** stimulus the internal vocabulary is removed and the
crowding **is** the intra-cell pairs. **Each world shows one dominant
mechanism, and they are different mechanisms.** The rank is a first case, not a distribution — the world's edges are spread
through the table rather than clustered at its top (the table above).

### What this settles

1. **Provenance mixing is real, measured, and exactly as D2 described** —
   35.7 %-40.7 % of the relation table, with 100 % of the removed rows
   sleep-sourced.
2. **The separation is available without privileged knowledge.** It uses
   `event_type`, which the engine already records on every event. It is not an
   oracle — unlike the world-vocabulary filter of §52, which selects on
   `TAG_POOL` and is therefore not an organism-side fix.
3. **Separating the families is NOT sufficient.** "Useful structure exists
   below the selection boundary" is **true**; "separating the families would
   recover it" is **false**.

### The V2 requirement list is now three, not two

1. **Provenance separation** — the world relation table must not contain
   relations sourced from the organism's own output. One filtered lookback
   query; the information is already in the schema.
2. **Relation-family separation** — co-occurrence and transition relations
   must not compete for the same budget. The `cooccurrences` and `precedes`
   tables are already separate; they are re-mixed downstream, in Layer 1.
3. **A ranking that is not raw frequency** — even with (1) and (2) done, the
   world's transitions are out-ranked by its own co-occurrence by roughly an
   order of magnitude, because the two differ in *frequency* and not in *kind*.

**Requirement 3 is the one with no precedent in the engine, and it is the one
§52's capacity sweep showed cannot be bought with budget:** precision never
exceeds 0.3438 at any budget under either allocation rule. Requirement 1 is
the cheapest and is a single query filter.

**No V2 build is authorised.** The target narrowed from "relation-family
separation" — one requirement — to three, and the hard one is now identified.

### The lessons

**1. A disclosed mechanism is not a measured one.** D2 named the unfiltered
lookback and nobody had quantified its consequence. When it was quantified, it
was **a third to two-fifths of the relation table**, and the substrate turned
out to be **99.5 % the engine's own output**. A disclosure earns the defect a
name; it does not earn it a size.

**2. "Separation" is a family of claims, and the useful one is the one you
can act on without privileged knowledge.** The first separation measured
(yesterday's) filtered on the *world's* tag list and was an **oracle** — it
quantified headroom and proposed nothing. This one filters on `event_type`,
which the engine already stores, and is therefore a **candidate change** as
well as a measurement. The difference is not academic: an oracle cannot
become a design.

**3. Removing a contaminant can reveal the next contaminant, and you have to
keep going.** With 100 % of the engine-generated rows removed, the gate still
failed, and the reason had changed from "the engine's own vocabulary" to "the
world's own co-occurrence". A probe that stopped at "we removed the
contamination and the gate still fails" would have reported a dead end; the
useful report is "we removed it, the crowding changed identity, and here is
the new one."

**4. Separate the mechanisms before designing for them.** The 1-tag and 2-tag
worlds show *different* dominant crowding. A single fix aimed at one of them
would have looked like a partial success in the other world and invited a
second, contradictory diagnosis.

### What does not change

The six negative task families, the Phase L protocol verdict `H3-L —
INCONCLUSIVE`, the Phase L characterization, and the campaign's stop at Gate
13 all stand. Every seed used is diagnostic and remains diagnostic. The frozen
engine is untouched — the probe rebuilds the table offline. And Law II of
`docs/DESIGN_LAWS.md` remains as written, with the discrepancy disclosed as
D3.

→ `docs/GATE13-RELATION-SEPARATION.md`; `docs/gate13_relation_separation.json`;
`benchmarks/probe_relation_separation.py`; manual finding 27
---

## §55 — The ranking requirement: every criterion the engine already stores was
tested, and all of them fail

**What this section records.** §54 left three V2 requirements, the third being
"a ranking that is not raw frequency" — the one the causal account had called
the hard one, with no precedent in the engine. It turned out to have a
precedent, and the precedent is the finding.

**All seeds are diagnostic** (`20261101`-`20261103`). The confirmatory sample
(`20261106`-`20261130`, 25 seeds) is untouched.

### The precedent: the engine already computes the criterion

`organica/sleep.py:1139-1160`:

```python
ratio = count / max(source_freq, 1)
...
strength=min(1.0, ratio),
evidence={"temporal_count": count, "source_frequency": source_freq,
          "target_frequency": freqs.get(tag_to, 0), "ratio": round(ratio, 3)},
...
candidates.sort(key=lambda p: p["evidence"]["temporal_count"], reverse=True)
```

The engine computes a **frequency-normalized** criterion, stores it in every
candidate's evidence, uses it for **survival**, and then sorts by **raw count**
for **admission**. `memory.py:264-281` calls the normalization "load-bearing
rather than cosmetic". So requirement 3 might need no new idea — and every
criterion the probe tested uses only fields the engine **already stores**.

### The grid

Two tables x two frequency scopes x five criteria x three seeds = **60 cells**.
The raw table's offline reconstruction must match the engine's table exactly,
or the probe refuses to report; it did, on every seed.

**The best cell in the entire grid reaches coverage 0.0804 at precision 0.4500.
The gate is 0.50.**

| table | scope | criterion | best coverage | precision |
|---|---|---|---|---|
| raw | world_freq | `count` *(the engine today)* | 0.0089 | 0.0500 |
| raw | world_freq | `ratio` / `cosine` / `pmi` | **0.0000** | 0.0000 |
| raw | world_plus_self_freq | `target_ratio` | 0.0625 | 0.3500 |
| filtered | world_freq | any | 0.0089 | 0.0500 |
| **filtered** | **world_plus_self_freq** | **`ratio` / `pmi`** | **0.0804** | **0.4500** |

Neither fix works alone. Together they take coverage from **0.0000 to 0.0804**
and precision from **0.0000 to 0.4500**, and flip the intra/inter balance from
20/0 to roughly 8-15/5-13 — the world's cross-cell relations enter the
selection for the first time in meaningful numbers. **And they are still six
times short of the gate.**

### Why each scope fails, measured

A diagnostic printed the selected edges with every number behind them.

**Under the engine's own scope:** `type -> cedar`, count 48, world-frequency
**0**, self-frequency 158,183, **ratio 48.0000** — exactly the raw count.
Because `_record_tag_counts` is inside the `if event_type != "sleep":` block,
**`tag_counts` is world-scoped** and the engine's own words have **no
frequency entry**; `freqs.get(tag_from, 1)` returns 1, so `ratio = count`.
**The engine's normalized criterion is undefined for exactly the edges it
would need to discriminate, and ranks them first.**

**Under a self-inclusive scope:** the failure runs the other way. The world's
tags appear in the engine's own sleep output constantly — `sable` 2,601
times, `olive` 7,753, `maple` 35,986, `cedar` 52,070 — so the world's tags
acquire enormous denominators and are penalised. The best world edge by the
same criterion is `sable -> fern` at ratio **0.0177**, against `mutation ->
cedar` at **0.1654**.

**Both scopes fail, for opposite reasons, and the reason underneath both is
the same: the engine's sleep output names the world's tags.** The world
vocabulary and the engine's own vocabulary are not separable **by frequency in
either direction**, because they are not separable at all in the substrate —
the organism talks about the world using the world's words.

### What this settles

1. **Requirement 3 is not "find a better formula."** Every formula built from
   the engine's own stored fields was measured, and all of them fail, in both
   scopes, on both tables, on every seed.
2. **The discriminator cannot be a per-tag statistic.** It must be a
   **relation-level** property: *which event did this relation come from*.
3. **The two fixes are complementary and jointly necessary**, and even
   together they are six times short of the gate.
4. **The engine's own normalized criterion is actively harmful on this
   table.** `ratio` is not a neutral alternative to raw count here; on the raw
   table it is worse, because the frequency it normalises by is absent for
   exactly the contaminated rows.

### The V2 requirement list, restated in terms of what each fix touches

1. **Provenance separation (relation-level).** One filtered lookback query —
   `memory.py:332` — and `event_type` is already in the schema. Cheapest, and
   oracle-free.
2. **A relation-level criterion, not a tag-level one.** After the provenance
   filter, the remaining competition is between the world's **own** relation
   families: intra-cell co-occurrence and cross-cell transition. **No per-tag
   frequency statistic can separate those**, because they involve the same
   tags. The discriminator has to be structural — for example, whether a
   source's target is its *unique* successor or *one of several*.
3. **Relation-family separation.** The `cooccurrences` and `precedes` tables
   are already separate in the substrate; they are re-mixed downstream, in
   Layer 1.

**Requirement 2 is the one with no precedent, and it is now the one with a
measured dead end.**

### The lessons

**1. "The engine has no precedent for this" is a statement about the code, not
about the space of solutions.** The engine *did* compute a normalized
criterion — and using it would have been worse than the thing it replaces.
The precedent was there; it was simply not the one anyone expected, and
checking it changed the requirement from "invent a criterion" to "the
criterion you can compute is the wrong one".

**2. A normalization can be undefined exactly where it is needed, and the
symptom is a ranking that prefers the contamination.** `ratio = count /
max(source_freq, 1)` looks defensive, and the default of 1 looks safe. It is
safe for the tags the counter knows and *catastrophic* for the tags it does
not — and the tags it does not know are the ones the criterion must
discriminate. A denominator with a silent default is a hole with a plausible
shape.

**3. When a criterion cannot be computed, the honest report is "cannot be
computed", not "does not work".** The two scopes failed for opposite
reasons — one because the engine's own words had no frequency, the other
because the world's tags had too much. Reporting either as "the criterion
does not work" would have been true and useless; the useful statement is
that **the quantity the criterion needs is not available in the substrate**,
and the discriminator has to be relation-level instead.

### What does not change

The six negative task families, the Phase L protocol verdict `H3-L —
INCONCLUSIVE`, the Phase L characterization, and the campaign's stop at Gate
13 all stand. Every seed used is diagnostic and remains diagnostic. The frozen
engine is untouched — every number comes from an offline reconstruction
validated against the engine's own table. And no V2 build is authorised: this
records what requirement 2 must **not** be, not a design for it.

→ `docs/GATE13-RANKING-CRITERION.md`; `docs/gate13_ranking_criterion.json`;
`benchmarks/probe_ranking_criterion.py`; `benchmarks/probe_ranking_mechanism.py`;
manual finding 28
---

## §56 — The closure was recorded in six places, and two documents still said the opposite

**What this section records.** The owner read the paper directory and the V2 design
brief, and found two documents still asserting that the audit build was unfinished
after it had closed, frozen and been tagged on 2026-10-28. This section records the
correction, the publication plan that followed from the same reading, and the two
lessons.

### The drift, measured

The closure of A5 and A6 had been written into **six** places: the audit-trace
specification §9/§10, the README banner, the manual §2/§8.17, facts sheet AA26/AB5,
AGENTS rule 23(c), and the CHANGELOG.

Two documents still said the opposite:

- **Paper 02 contradicted itself.** Its abstract ended *"A5 field honesty and A6
  separation of trace from counterfactual remain pending; the audit instrumentation is
  not yet frozen"* and its §3 was titled *"Remaining acceptance work"* — while its own
  draft-status line said *"A5/A6 closed and the audit layer frozen at `audit-trace-v1`
  on 2026-10-28"* and its conclusion said *"A5/A6 are now closed (2026-10-28) and the
  instrumentation is tagged and frozen"*.
- **The V2 design brief's §4.3 was headed *"The audit build is nearly, but not fully
  closed"*** and its body listed A5 and A6 as *"Still open"*. Five further passages
  carried the same state: build gate 4 was unmarked, the gate-5 annotation said
  *"gates 4 (A5/A6) and the study itself remain open"*, the §10 corrections table said
  A5/A6 *"remain open"*, the §11 table treated their closure as a future event, and the
  superseded banners in `ROADMAP.md` and `docs/V1-SYNTHESIS.md` described the audit
  build as unfinished and the pre-registration as Revision 2.

**Eleven passages across four documents** were corrected. Paper 02's abstract, §3 and
draft-status line; the V2 brief's §4.3 heading and body, build gate 4 (now marked
**EXECUTED (2026-10-28)**), the gate-5 annotation, the §10 corrections table and the
§11 table; and both banners.

### Lesson 1: six agreeing places do not compensate for two disagreeing ones

The closure had been recorded in six places, and the count was treated as the
guarantee. It was not a guarantee at all — the check was **never made**. Two
documents said the opposite, and one of them said it *about itself*, which is worse
than being out of date: an out-of-date document misleads only the reader who follows
it, while a self-contradicting document teaches the reader that its own sentences
cannot be relied on, and that distrust then extends to the sentence that was right.

The sweep also needs a **named criterion** rather than suspicion. Here the criterion
was available and simple: **one status, stated in every document that states it.** The
audit build's closure is a single boolean; every sentence that asserts it must agree.
That criterion is checkable, and it found eleven sentences that did not.

### Lesson 2: the papers are the publication surface, and the index must carry the plan

The same reading produced the publication plan, and it is now in `papers/README.md`:

- **Paper 01** — the honest empirical V1 account: developmental structure forms,
  external advantage has not been demonstrated, Task 2 stopped at acquisition and
  transfer was not measured.
- **Paper 02** — the bounded audit-trace result: reconstruction of tested surviving
  state from the engine's stored state.
- **Paper 00** — separately, as a position paper, only after its broad claims and its
  literature framing are audited.
- **Papers 03 and 04** — held: mechanism *proposals*, not demonstrated-efficacy results.
- **Papers 05 and 06** — historical, until their claims are rechecked, and **no claim in
  either is currently strengthened by recent work — neither should be described as if it
  were**. Paper 05 in particular **cannot** be presented as evidence that the system
  prevents self-contamination: its strict-firewall claim conflicts with the measured
  sleep-sourced relations (D2, quantified in `docs/GATE13-RELATION-SEPARATION.md`). Paper
  06's major lifecycle, stability and lineage claims remain unverified against the current
  evidence.

Paper 01's **core question is "can developmental structure emerge in Organica 1?"** — one
question, answered rigorously, with the negative external-task results included as the
boundaries of the answer, and **not** an attempt to cover every probe. The accurate next milestone is **making the first two submission-ready**, not publishing them as they stand.

And the correction of the record: the **Phase L characterization, the V1 synthesis and
the audit artifacts are research records, not manuscripts.** They are not additional
papers in `papers/`. The inventory stays **seven manuscript files, zero published**.

Paper 01 was renamed to match its revised title
(`01_developmental_structure_formation.md`), Paper 02 was revised to academic grade,
and the house style is now **American English**.

The corpus was then organized as **two maps kept side by side**, because the three-layer view orients a reader but does not decide what gets published: a **research-program map** (theory, proposed mechanisms, empirical findings) and a **publication map** (which manuscript can make a coherent, evidence-backed contribution now). And every claim now carries one of **four** statuses — *supported within this scope*, *mixed / context-limited*, *reversed*, *not established / not measured* — because a claim that was not established is **not** a claim that was refuted, and *reversed* is a stronger statement than merely unsupported. Paper 01's central question was narrowed to match, and it no longer covers every probe. Paper 05 might instead become a paper about the **limits or failure** of cognitive isolation, but that would be a new thesis rather than a revision.

### What does not change

No measurement is altered by any of this. The six negative task families, the Phase L
verdict `H3-L — INCONCLUSIVE`, the acquisition gate failure, and the transfer result
of *not measurable* all stand as recorded. Every seed used in the mechanism probes
remains diagnostic, and the confirmatory sample is untouched. The frozen engine is
untouched.

→ `papers/02_persistent_structural_provenance.md`; `papers/README.md`;
`docs/ORGANICA-V2-DESIGN-BRIEF.md` §4.3, §7, §10, §11; `ROADMAP.md`;
`docs/V1-SYNTHESIS.md`; manual findings 29 and 30; facts sheet AD1–AD2
---

## §57 — The first audit of the two theoretical manuscripts, and what it found

**What this section records.** The owner's publication framing put Paper 00 and Paper 05
outside the active submission queue pending review. This section records the first pass
of that review — what was checked, what failed, and what was corrected — and it records
that the review is **not finished**.

### Paper 00: two verified factual defects

**The generation count.** Paper 00 said *"In Project Organica, this hierarchy spans eight
generations"* and then presented a table with **nine** rows, G0 through G8. The project's own
architecture specification names the structure correctly: **"The 8 Generational Primitives"**,
with **G0: Experience** as the substrate and G1–G8 as the eight primitives. The position
paper's count was wrong against itself and against the code.

Paper 01's first draft made the same error — it wrote "eight generations" over a nine-item
list — and was corrected in the same pass. That is the second time this turn that a
consistency check between two documents caught an error in a document written minutes
earlier.

**Law II.** Paper 00 states Law II as one of six inviolable laws:

> **II. Provenance.** Every structure carries explicit, verified `parent_ids` traceable to
> G0 events.

The frozen engine does **not** satisfy that. The `parent_ids` chain **terminates at Layer
1** — concepts, phrases, loops and predictions are built from tags — and the structure to
event link exists only as **counts**. This is the project's own **D3**, disclosed in the
audit-trace specification and left open because the frozen engine's constitution is the
owner's decision, not a documentation fix. Paper 00 asserted the law with no disclosure
at all, which is the same sentence that had to be removed from the README in the earlier
drift review.

**Both were corrected in place**, with the D3 disclosure carried inline rather than
omitted. Paper 00's **remaining** broad claims and its literature framing are **not
audited**, and the manuscript is **not ready to circulate**.

### The abstract's claim, against the record

Paper 00's abstract offers a narrower, falsifiable claim: that the architecture *"can
spontaneously generate concepts, causal predictions, recurring processes, falsifiable
hypotheses, epistemic curiosity, counterfactual imagination, and prioritized empirical
inquiry."* The **forms** of the last three exist — G5–G8. The **efficacy** does not:

- Phase K's matched mechanism ablations came back empty. `NO_QUESTIONS` −0.0095
  [−0.0328, +0.0140]; `NO_FALSIFICATION` +0.0241 [−0.0048, +0.0495]; `NO_DREAMS` +0.0000
  [0.0000, +0.0000]. **All three intervals contain zero.**
- **Law IV is never exercised.** Experiments are generated, every consumer only prints
  them, and **no Question can ever close**. The study measures epistemic *tension*, not
  *resolution*.

So the generation of curiosity, dreams and inquiry is **not demonstrated** — which is a
different statement from "not attempted", and the paper's framing needs it.

### Paper 05: the core guarantee is contradicted by the measurement

Paper 05's abstract claims its strict firewall *"ensures zero synthetic self-contamination
across indefinite life cycles"* and offers *"mathematical bounds and architectural guarantees
proving that systems respecting CIP maintain stable representations over infinite sleep
iterations."*

The measurement says otherwise. **17.9%** of the distinct supporting transitions behind
reported beliefs (802 of 4,481) are **self-sourced**, and **43.2%** of all distinct
transitions the observer recorded (5,436 of 12,583) are the organism's own output, entering
the temporal substrate through the **unfiltered lookback window** (D2, quantified in
`docs/GATE13-RELATION-SEPARATION.md`).

This is why Paper 05 is not merely out of date. Its thesis is the negative of what was
measured, and the repair is not an update — it is a **new thesis**: *the limits of
cognitive isolation in Organica V1*.

### The lesson

**A position paper is audited against the code, not against the prose.** The two documents
most likely to be circulated are the two least checked against the engine, because neither
is a measurement record and so neither is covered by the harness. And the first finding of
such an audit is usually a **count or a law the record already contradicts** — because
those are the claims a reader cannot check for themselves.

### What does not change

No measurement is altered. The six negative task families, the Phase L verdict
`H3-L — INCONCLUSIVE`, the acquisition gate failure and the transfer result of *not
measurable* all stand. The frozen engine is untouched. Paper 00 and Paper 05 are **not**
ready to circulate, and Paper 00's remaining claims are **not** audited.

→ `papers/00_intelligence_through_structural_descent.md`;
`papers/05_cognitive_isolation_principle.md`; `docs/architecture.md`;
`docs/AUDIT-TRACE-SPEC.md` §7 (D3); manual finding 31; facts sheet AD3
---

## §58 — The historical record, normalized to American English, with the change proven

**What this section records.** The owner confirmed that the frozen records stay right under a
spelling normalization, and authorized closing that gap. **234 words across 25 files** were
normalized — including the preregistrations, the measurement records and the frozen journal
sections — and the change was **proven** to be spelling-only rather than asserted to be.

### Three proofs, run against `HEAD` for every changed file

1. **Non-target content byte-identical.** Every British-or-American target word is replaced by
   the *same* token on both sides, so the comparison sees only the non-target bytes and the
   token positions. Identical on all 23 changed files.
2. **The sequence of numeric literals identical.** No number changed, moved, appeared or
   disappeared — in any file.
3. **Structure identical.** The same count of headings, table rows, list items and lines.

Inline code spans were never rewritten, so no identifier, file path, tag, test name or
constant was touched. The frozen engine and every protocol's substance are untouched.

### The bug worth recording

The first pass reported **"remaining: 0"** — and it was **wrong by 88 occurrences**. The sweep
and its verification shared a document-wide code-span regex, `` `[^`]*` ``, which mis-aligns when
backticks are unbalanced across a line: the "code span" it matched ran past its closing backtick
into ordinary prose, so the sweep **skipped prose it should have rewritten**, and the same
mis-pairing then **failed to count what was skipped**. Both halves were wrong in the same
direction, so the check agreed with the writer.

The bug surfaced only because a **second, differently implemented** check — a raw-text scan with
no span logic at all — disagreed with the first. The fix was per-line backtick pairing (exact
for balanced lines) plus the raw scan as an independent witness. The final state is **0
remaining under a raw scan**.

**A verifier that reuses the writer's parser inherits the writer's bug. A check that cannot
disagree with its own writer is not a check.** This is the same shape as the acquisition
harness, where two implementations of one gate name disagreed by 100% versus 0.0% on the same
seed and world: the disagreement was the finding, and the fix was to make the two
implementations reconcile against the protocol rather than to trust one of them.

### What does not change

Every number, claim, verdict, date, method, seed and decision rule in the repository is
unchanged. The six negative task families, the Phase L verdict `H3-L — INCONCLUSIVE`, the
acquisition gate failure and the transfer result of *not measurable* all stand as recorded. The
frozen engine is untouched; the live study remains paused at 5,396 sleep cycles.

→ manual finding 32; facts sheet AD4; `git diff HEAD` (23 files)
---

## §59 — Paper 00's audit, completed: the constitution, measured against the code

**What this section records.** The owner asked for the audit of Paper 00's broad claims to be
finished, not just the two defects that happened to be noticed. It was finished, by reading the
six laws in `docs/DESIGN_LAWS.md` against the frozen engine and the V1 record. **Two of the six
laws are contradicted by the implementation, one is untested on its own terms, and one is
contradicted in direction.**

### Law III — violated in exactly the way it was written to prevent

The design law states:

> *Internal cognitive operations (sleep consolidation, dream generation, hypothesis pruning) must
> never pollute the empirical experience graphs.*
> - Event logs must partition internal reflection (`event_type="sleep"`) from external observation.
> - **Co-occurrence graphs and temporal precedes matrices are strictly computed on non-sleep events.**

The second bullet is the requirement, stated exactly. And the engine does not meet it.
`memory.py::_record_temporal_edges` gates the **trigger** on `event_type != "sleep"`, but its
**lookback window** is ungated:

```sql
SELECT tags FROM events ORDER BY time DESC LIMIT ?
```

So a world event can take its source tag from a sleep row. Sleep output re-enters the empirical
graph at **201×–341×** the world's own event count, and the contamination is **35.7%–40.7%** of
the relation table with **100.0%** of the removed rows sleep-sourced (D2,
`docs/GATE13-RELATION-SEPARATION.md`).

**This is the same defect that contradicts Paper 05's "zero synthetic self-contamination"
guarantee.** One measured mechanism, two documents claiming different things about it.

### Law V — wrong twice, formally and empirically

**Formally.** The law states one expression, $\text{EIG} = \text{Uncertainty} \imes (1.0 +
\text{Novelty})$. The engine computes it two ways: `uncertainty * (1.0 + novelty)` for questions
(novelty fixed at 0.50), and `uncertainty * d.novelty` — **no `1.0 +`** — for dreams, whose
uncertainty is `1.0 - confidence`. So the single expression is not what the engine computes for
half its cases.

*Corrected 2026-10-30:* the LaTeX escapes in the expression above were written into this
journal as **literal tab characters** rather than as `\t`, so the formula rendered as
broken text and its braces read as unsubstituted template placeholders. The escapes are
restored here. **No claim in this section changes** — the expression, the two engine
computations and the conclusion are unchanged; only the rendering was repaired. The
repository's doc-placeholder guard is what caught it, and the defect was present in the
committed record before this pass.

**Empirically.** The pre-registered prediction **P5 (EIG-orthogonal) is REVERSED**: selecting the
*lowest*-EIG experiment develops **more** than selecting the highest-EIG one. The mechanism
exists; its direction is opposite to the law's claim. The sibling predictions were
**P1 retention SUPPORTED**, **P2 contradiction-is-fuel REVERSED**, **P3 curiosity-needs-questions
REVERSED**, **P4 dreams-contribute SUPPORTED** — **2 SUPPORTED, 3 REVERSED, 0 UNSUPPORTED, 0 NOT
INTERPRETABLE** (`docs/verdicts.json`).

### Law IV — the baseline holds, the path is never exercised

Dreams are created with confidence **0.04–0.06**, matching the design law's baseline, so that
clause holds. But the law's operative clause — *a dream can only become a belief if an external
experiment generates empirical events that confirm its structure* — is **never exercised**: the
engine generates experiments and **never executes them** (every consumer only prints them), so no
question can ever close. The mechanism is present and its path is untraveled.

### Law VI holds, and Law I was not separately audited

Decay thresholds are **0.3** (stable) and **0.15** (death). Law I was not audited in this pass and
is reported as such rather than assumed.

### Also corrected

- The abstract's *"unbroken lineage to the raw experience"* is false (D3 — the chain terminates at
  Layer 1).
- The abstract's *"causal predictions"* overstates the engine's own words: `memory.py` calls the
  temporal edges *"the organism's first approximation of causality"*. The abstract now says
  **temporal predictions**.
- **D4, a new disclosed defect.** The engine's stored `generation` field agrees with
  `docs/architecture.md` for **G1** and is **one lower for every primitive from G2 upward**:
  meta-concepts and processes `generation = 1`, workflows `2`, hypotheses `3`, theories and
  questions `4`, dreams `5`, investigations `6`, experiments `7`. No document states the field's
  mapping, so this is an **undocumented offset**, not a violated claim — but the generation table
  in Paper 00 is the public description, and anyone reading a stored candidate beside it would
  mis-map. The audit-trace specification is frozen at `audit-trace-v1` and was **not** edited to
  carry D4; the disclosure lives in the fact sheet (AD5) and the manual (finding 33).
- The reference list's titles were the **old** names, and its *"Associated pre-prints"* label was
  false: the inventory is **seven manuscript files, zero published**. The list now names each
  manuscript with its status.

### The lesson

**A constitution that has never been audited against its implementation is a description of an
unimplemented architecture.** Two laws broken, one unexercised, one reversed — and every one of
them was found by *writing the auditor*, not by arguing. That is the strongest evidence this
program has produced for its own thesis, and it would have been invisible to any review that
read the laws and the code side by side without measuring the code's behavior.

**A law that cannot be violated is not a law; a law that has never been tested is not yet a
claim.**

### What does not change

No measurement is altered. The six negative task families, the Phase L verdict
`H3-L — INCONCLUSIVE`, the acquisition gate failure and the transfer result of *not measurable*
all stand. The frozen engine is untouched; `docs/DESIGN_LAWS.md` and
`docs/AUDIT-TRACE-SPEC.md` were not edited.

→ `papers/00_intelligence_through_structural_descent.md` §3.1; `docs/DESIGN_LAWS.md`;
`docs/AUDIT-TRACE-SPEC.md` §7; `docs/architecture.md`; `organica/memory.py`;
`organica/sleep.py`; `docs/verdicts.json`; manual finding 33; facts sheet AD5

## §60 — A hand-transcribed table drifted from its artifact, and the repair was defective too

**What this section records.** A publication-pass review of the Pilot-0 readout found that the
10-cell score matrix in `docs/PILOT-0-INSTRUMENTATION-AUDIT.md` §2 — a table whose entire
authority is that it came from `docs/acquisition_single_seed_pilot.json` — had been
**transcribed by hand**, and that **18 of its 36 values disagreed with that artifact** in the
fourth and fifth decimal of log-loss. The artifact never changed. The table did.

### What was wrong

The artifact carries the Pilot-0 readout for all ten cells plus two reference models. Its
values are identical in **both** commits that carry it — `89b0744` (2026-10-28) and `4ceeab4`
(2026-10-29) — verified by extracting the values at each revision. The matrix in the audit
document disagreed with it in **18 of 36** values, every one in the fourth or fifth decimal, the
largest gap **6.7×10⁻⁵**.

The disagreements were not random. They fell on the **Organica** cells (1–6) and on the two
**reference** rows, and left the two baseline cells (7–10) and the retention column of cells 1,
4, 5 and 6 untouched — the signature of a copy made from one earlier reading of the numbers
rather than from the artifact.

Six of the drifted values had been inherited by
`papers/01_developmental_structure_formation.md` §4.7, and six more each by the five-row
learner summaries in `docs/ACQUISITION-ENDPOINT-AUDIT.md`,
`docs/ORGANICA-V2-DESIGN-BRIEF.md`, `docs/FACTS-SHEET.md` (AC7),
`research-journal/phase_g_findings_20261021.md` and `research-journal/_journal_entry_51.md`.

### What the correction revealed about the correction

The first repair was itself written by hand, and it **made the table worse in a different
way**: the script that replaced the drifted rows **replaced the two reference rows** (Bayes
ceiling, base rate) with **duplicate copies of cells 7 and 8**. The table went from *18 wrong
values* to *twelve rows in which two were duplicates and two references were missing*.

Nothing about that defect is visible to a reader. The table still had the right shape, the right
headers and the right-looking numbers, and a diff against the previous revision shows only
changed cells. It was caught by one thing only: **running the table against the artifact
mechanically**. The table is now **regenerated from the artifact** rather than patched, and the
check is permanent — `tests/test_readout_tables.py` asserts every document that restates the
readout against the artifact, and includes four assertions that the checker itself can fail.

### The lesson

**A table transcribed from an artifact is a new claim, and it needs a mechanical check against
that artifact.** The artifact is the machine-written record. A hand-copied table is a *second*
claim that carries the artifact's authority without carrying its evidence, and every discrepancy
sits in the fourth decimal where nobody looks.

The prior verification script reported "0 failures" because it never covered these cells. That is
the real failure mode: **a verification suite that has not been extended is a claim that nothing
new is wrong**, not a claim that nothing is wrong.

And the second-order lesson is the one this project needed: **a repair written by hand is
another hand transcription, and it fails the same way.** The fix for a transcription defect is a
generator, not a better transcription.

### What does not change

No measurement is altered and no verdict moves. Organica's readout still loses to both
baselines on the Pilot-0 seed, the E-rem floor is still **0.403045**, the acquisition gate
still fails, and transfer is still *not measurable*. The frozen engine is untouched.

→ `docs/acquisition_single_seed_pilot.json`; `docs/PILOT-0-INSTRUMENTATION-AUDIT.md` §2.1;
`tests/test_readout_tables.py`; `papers/01_developmental_structure_formation.md` §4.7;
manual finding 34; facts sheet AD6

## §61 — The publication pass: citations that were read, and figures that can fail

**What this section records.** Two manuscripts were brought to academic grade. Paper 02's §2 now
carries inline citations and a **References** section of **five** sources; every one was read
against a primary source rather than recalled. Eight figures were generated for Papers 01 and 02
by a dependency-free generator that **asserts every value it draws against the artifact it came
from**.

### Citations: only what was read

Each of the five sources was fetched and read on 2026-10-29:

- **ACM Publications (2020)**, *Artifact Review and Badging* v1.1 — the source of the **Results
  Reproduced** versus **Results Replicated** distinction Paper 02 uses, including the
  Publications Board's 2020 **interchange** of the two definitions to adopt the NISO standard.
- **Bau, Liu, Wang, Zhu & Torralba (2020)**, *Rewriting a Deep Generative Model*, ECCV 2020
  (oral) — the inversion-by-latent-embedding construction that Paper 02's §2 sets against
  Organica's inverse-construction account.
- **Elhage, Nanda, Olsson et al. (2021)**, *A Mathematical Framework for Transformer Circuits*,
  Anthropic — mechanistic interpretability as reverse engineering, the authors' own statement
  that they "remain a very long way from being able to fully reverse engineer such models", and
  the scope limit to attention-only models of two layers or fewer.
- **Moreau & Missier (eds.) (2013)**, *PROV-DM: The PROV Data Model*, W3C Recommendation — the
  provenance model that Paper 02's §2 positions the audit trace against.
- **Shumailov, Shumaylov, Zhao, Papernot, Anderson & Gal (2024)**, *Nature* 631(8022):755–759 —
  model collapse on recursively generated data, **with its Author Correction**
  (*Nature* 640(8058):E6, 2025) disclosed. The correction fixes a notation typo in the
  theoretical-intuition section ("αi = γi = 0" should read "βi = γi = 0") and **does not touch
  the empirical claim** Paper 02 cites.

**One candidate citation was dropped.** The Elhage paper's *faithful versus sufficient*
distinction is the natural citation for one of Paper 02's §2 claims, and it is almost certainly
in the paper. It was nonetheless **not cited**, because no readable copy could be found: the
available PDF's page 4 is empty — the Introduction and Figure 1 are missing — and neither
`pypdf` nor `pdfplumber` recovers it (137,658 characters extracted; zero occurrences of
"faithful" or "sufficient"). **Cite only what was read.** A citation that cannot be verified is
a claim about a document nobody has read.

### Figures: a program that draws a claim must be able to fail

`benchmarks/figure_papers.py` writes **eight** dependency-free SVGs. It is not a plotting-library
wrapper — the SVG is hand-written, following the convention already set by
`benchmarks/figure_campaign.py` — and it is built to fail:

- **It asserts its values.** Every number a figure draws is checked against the committed
  artifact before the figure is written, so a figure cannot drift from the published result.
- **It checks its canvas.** Every x, y, cx and cy is bounds-checked against the canvas.
- **It checks its text.** Every `text()` call is estimated for width overrun; two figures
  failed this check during the build and were shortened.
- **It parses its own XML.** Before writing, the SVG is parsed with `xml.etree.ElementTree`.

That last guard was added because of a real failure: an early build emitted `font-style:italic`
as a bare attribute, which is malformed XML, and **the renderer stopped after the first bar** — a
figure that silently drew a third of itself. A figure that silently draws nothing is worse than
no figure, because a missing figure is noticed.

### The lesson

**A figure is a program that draws a claim, so it must be able to fail** — and the same is true
of a citation. Both are claims about the record, made in a form that review reads visually or
trustingly, and both fail silently when the machinery underneath is wrong. The defense is the
same in each case: **make the claim checkable against its source, mechanically.**

**Cite only what was read.** A reference list is a set of claims about what other people wrote.
Verified against the source, it is evidence. Verified against memory, it is a guess with a
citation attached.

### What does not change

No measurement is altered. The eight figures draw the **committed** results; the five citations
support **existing** claims; and the manuscripts' verdicts — `H3-L — INCONCLUSIVE`, the failed
acquisition gate, the *not measurable* transfer result — are unchanged. Paper 00 remains
accurate and **not yet** the recast position paper the project needs, and Paper 05 remains
outside the active submission queue.

→ `papers/01_developmental_structure_formation.md`;
`papers/02_persistent_structural_provenance.md` §2 and References;
`benchmarks/figure_papers.py`; `docs/figure_p*.svg`;
`docs/acquisition_compositional_gate.json`; `docs/acquisition_single_seed_pilot.json`;
`docs/phase_l_results.json`; `docs/phase_k_results.json`; `docs/gate13_capacity_sweep.json`;
`docs/audit_trace_probe*.json`; manual finding 35; facts sheet AD7

## §62 — The first world edge was reported without the distribution beside it

**What this section records.** The owner reviewed the project's own reporting of the Gate 13
ranking failure and found one claim that was true but incomplete in a way that mattered: the
**rank of the first world edge** was reported — *rank 31* in the 1-tag stimulus, *rank 30 /
18 / 53* in the 2-tag seeds, and *rank 16 / 8 / 8* after the LIMIT-4 separation — **without
the distribution of the world's edges behind it**. A first edge appearing early in a frequency
ordering reads as though the world's relations are *nearly* reachable by raising a budget.
They are not.

### What the distribution is

Under the engine's own global count-ranked selection, the world's 112 edges are **spread
through the table, not clustered at its top** (`docs/gate13_allocation_rule.json`, 3 seeds,
the global rule):

| Selection (global count-ranked) | world edges recovered, of 112 |
|---|---|
| top 20 — the engine's own budget | **0 – 1** |
| top 40 | **0 – 2** |
| top 80 | **8 – 16** |
| top 160 | **36 – 55** |
| top 320 — about 16× the engine's budget of 20 | **106 – 109** |

The five-seed capacity sweep puts the cap at 40 at **1 – 8 of 112**, and the frozen cap of 20
at **0 – 3 of 112** (`docs/gate13_capacity_sweep.json`).

The distribution is now carried beside the rank in `docs/GATE13-RELATION-SEPARATION.md` §4,
in this journal's §54, in manual finding 27 and in the changelog.

### A quoted figure that did not survive contact with the artifact

While preparing the correction, the figure *"cap 40 recovers 4 – 8 of 112"* — which had been
quoted in correspondence — was found **not** to be what the artifact says. The five-seed
sweep gives **1 – 8 of 112** at cap 40 (per seed: 4, 7, 1, 2, 8). The correction therefore
**restates the figure from the artifact** rather than carrying the quoted one forward. A
number that cannot be traced to an artifact is not a weaker claim; it is not a claim.

### What does not change

No measurement is altered and no verdict moves. The first-edge ranks are correct as recorded;
the artifact-backed ranges are what the documents now carry beside them. The conclusion is
unchanged and is now stated with its distribution: **no frequency-based selection can find the
world's relations**, because they are a third of the rows and are not clustered at the top of
any frequency ordering. The frozen engine is untouched.

### The lesson

**A first edge at rank *N* is one edge arriving, not a set arriving.** This is the same
discipline as *"a benchmark's headroom is not a learner's margin"* and *"the proximate bound
and the deepest cause are different claims"*: a threshold, a first case and a headline
statistic are all single points, and **the set is the claim**. Reporting the first edge alone
made the ranking problem sound nearly solved; the distribution shows it needs roughly **16×**
the engine's budget and a ranking rule the engine does not have.

### The Law II ruling (owner, 2026-10-30)

The owner has ruled on the **Law II** discrepancy: **keep it disclosed, and do not amend the
law yet.** The amendment waits on a question the owner has framed explicitly — *is Law II a
design requirement, or a description of V1's actual behavior?* Those two readings imply
different amendments, and rewriting the law to match the frozen engine would erase the
distinction that makes the discrepancy meaningful. `docs/DESIGN_LAWS.md` is therefore **not**
edited, and the disclosure stays where the audit put it: facts sheet AD5, manual finding 33,
and `papers/00_intelligence_through_structural_descent.md` §Law II.

→ `docs/gate13_allocation_rule.json`; `docs/gate13_capacity_sweep.json`;
`docs/gate13_relation_separation.json`; `docs/GATE13-RELATION-SEPARATION.md`;
`docs/GATE13-CAUSAL-ACCOUNT.md`; `docs/USER-MANUAL.md` findings 27 and 36;
`docs/FACTS-SHEET.md` AD8; `papers/README.md`

## §63 — Paper 01's citations, and the lesson that carries none

**What this section records.** Paper 01 was the last of the two active manuscripts with its
citations still open. This section records the audit that closed it: what was read, what
each source is cited for, and the one lesson that is deliberately left uncited.

### What was read

Seven sources, each retrieved on 2026-10-30 and read at the level its claim requires.

| Source | Read as | Cited for |
|---|---|---|
| Bengio et al. (2009), *Curriculum learning*, ICML | the authors' abstract | the definition of curriculum learning — examples presented in a meaningful order rather than at random |
| Wang, Chen & Zhu (2021), *A survey on curriculum learning*, IEEE TPAMI | the arXiv record (arXiv:2010.13166v2) | curriculum as a training strategy whose effect on the trained model is a measured quantity |
| Button et al. (2013), *Power failure*, *Nat Rev Neurosci* 14(5) | the abstract and the PubMed record | low power reduces the chance of detecting a true effect and the likelihood that a significant result reflects one |
| Simmons et al. (2011), *False-positive psychology*, *Psychol Sci* 22(11) | the Crossref-deposited abstract and the Europe PMC record | flexibility in data collection, analysis and reporting inflates the actual false-positive rate above the nominal one; disclosure is the prescribed remedy |
| Jacobs & Wallach (2021), *Measurement and fairness*, FAccT '21 | the authors' abstract | the mismatch between the construct a study means to measure and the operationalization it computes |
| Davis & Goadrich (2006), *The relationship between Precision-Recall and ROC curves*, ICML | the authors' abstract | on skewed data a precision–recall curve gives the more informative picture, though ROC-space and PR-space dominance coincide |
| Saito & Rehmsmeier (2015), *The precision-recall plot is more informative…*, *PLOS ONE* 10(3) | the open-access PLOS abstract | a ROC curve's visual interpretability is deceptive about reliability on imbalanced data |

### The lesson that carries no citation

The second of §5.4's four lessons — *compare against the strongest simple baseline, and
take the headroom from the ceiling* — is **this project's own rule**, and it reports only
Organica 1's own numbers. It is therefore stated in the manuscript as the project's rule,
with no external reference attached, and the judgment is recorded rather than left silent.
Two further candidate sources for it could not be located in any bibliographic record and
are not cited.

### A correction, disclosed

An **erratum** to Button et al. was published in *Nature Reviews Neuroscience* 14(6):451
on 15 April 2013 (https://doi.org/10.1038/nrn3502), and it was read. It corrects the
definition of *R* on page 366, which reads in the corrected version as *"the pre-study odds
(that is, the odds that a probed effect is indeed non-null among the effects being
probed)"*. It touches neither the abstract nor the power conclusions cited in Paper 01, and
it is disclosed in the manuscript's source notes.

### The lesson

**"Cite only what was read" is a rule about the limit, not only about the citation.** Two
of the seven sources were reachable only as their authors' abstracts, because the ACM
Digital Library's full text is not retrievable in this environment. They are cited only for
what those abstracts state, and the limit is written down where a reader will find it. A
reference list that does not say *how far* a source was read is a list that invites the
reader to assume more than was checked.

→ `papers/01_developmental_structure_formation.md` §4.1, §5.4, References;
`papers/README.md`; `docs/USER-MANUAL.md` finding 37; `docs/FACTS-SHEET.md` AD9

---

## §64 — Correction (2026-10-30): the cold-start table no longer reproduces, and the engine did not change

**What was found.** A verification pass re-ran the documented checks on the frozen engine.
`docs/cold_start.json`, generated 2026-10-21, no longer reproduces: its `cold_start`
condition records **no G5 for the whole run**, and every retrievable engine reaches **G5 at
cycle 10**. The row in §14 above (`cold_start` … G5 `–`) is therefore a record of the
2026-10-21 run, not a description of the engine anyone can run today.

**What was ruled out, one at a time.** The artifact and the rerun agree on the parameters
that matter — `--cycles` 40, `events_per_cycle` `[8,8,1,1,1,8,8,8]`, seededness
`[T,T,F,F,F,T,T,T]`, a 48-event stream for `cold_start` — and on the **schema**: the same
top-level keys, the same condition keys, and the same twelve `final_populations` classes,
including `G2 processes` and `G3 workflows`, which the old artifact carries with value `0`.
The extra leaves in the rerun are populations that now emerge, not new fields. Run-to-run
nondeterminism is ruled out (two consecutive runs: 0 structural differences), hash
randomization is ruled out for emergence (`PYTHONHASHSEED=0` vs `1`: one non-emergence leaf,
`experience_events` 111,697 → 111,758), and the interpreter is ruled out (3.13.15 and 3.14.7
produce identical emergence keys for all eight conditions).

**What the timeline says.** The artifact is dated 2026-10-21. The earliest engine retrievable
from the repository is tag `v0.6.0`, dated 2026-10-23, and **it already shows the current
profile** — `cold_start` G5 at 10, `cold_start_unbranched` deepest 12, `real_git_history`
never. The freeze at `v0.9.0` (2026-10-24) is therefore **not** the cause; the change predates
it. The commits between 2026-10-21 and 2026-10-23 are not published — `master` history was
rewritten on 2026-10-29 and the deepest fetchable chain is 11 commits ending at 2026-10-29 —
so the transition cannot be bisected. Whether the 2026-10-21 measurement was correct for a
then-current engine, or was itself anomalous, cannot be decided from the surviving evidence.
Both readings remain open; the record does not choose between them.

**What changed as a result.** `docs/cold_start.json` and `docs/g5_gap_diagnostic.json` were
re-measured on the frozen engine and the documents that restate them were regenerated from
the artifact: manual §8.1's table, the §121 headline, decision 4's control claim, finding 10,
`docs/FACTS-SHEET.md` B1 and the `docs/GATE-BOARD.md` status line. Two claims were narrowed
rather than merely renumbered: `real_git_history` does reach G2 processes and G3 workflows
(at cycle 14) and G4 at cycle 6, so "G2, G3 and G5 never emerge unassisted" is false; and
`no_dev_stopwords` is no longer byte-identical to baseline (1 theory / 1 question against
2 / 2), so the causal demonstration rests on `no_truncation` being identical and
`wide_lookback` destroying G5.

**What did not change.** The engine. `v0.9.0` and `HEAD` are behaviourally identical by
`tests/test_v1_freeze.py`, `real_git_history` still never reaches G5, and the confidence-share
mechanism is still the explanation the `wide_lookback` row supports. No verdict was re-read.

→ `docs/USER-MANUAL.md` §8.1 and its revision log; `docs/cold_start.json`;
`docs/g5_gap_diagnostic.json`; `docs/FACTS-SHEET.md` B1; `docs/GATE-BOARD.md`;
`.scratch/verify/REPORT.md`

## §65 — Correct structure is not enough: the formation-vs-utilization campaign, and a bar that was not what the protocol called it

**What was run.** The amended protocol's 30 confirmatory seeds
(`20261101`–`20261130`), both tasks, four arms (A, B, C, S) and the frozen
comparators: **60 units, 240 arm runs**, engine **0.10.0**, no engine file
changed. The campaign ran through `python .scratch/run_campaign_resumable.py
--seeds 30 --workers 10`, a resumable wrapper over the harness's own
`run_task_seed`; every unit was checkpointed, no unit failed or was re-run, and
the artifact was assembled with the harness's own `analyse()` and renderer. The
per-unit timings sum to **12.72 worker-hours**; the wall clock was **4,690 s**
on 10 workers. All **60/60** units are `campaign_ready`.

**The verdict.** Both formed arms lose transfer on both tasks, so §7's "both
lose" cell fires on both: **"utilization fails even with correct structure"** →
**V2 targets the use path (retrieval / activation / readout)**. The summary claim
is **not supported**. The failing limbs are **transfer and retention**.

| Task | Arm | Retention | Transfer | Revision |
|---|---|---|---|---|
| T1 | B (cap 1,000) | −0.0302 | −0.0296 | +0.0877 |
| T1 | C (cap 1,000 + support) | −0.0267 | −0.0262 | +0.1002 |
| T2 | B (cap 1,000) | −0.0797 | −0.0795 | −0.0676 |
| T2 | C (cap 1,000 + support) | −0.0230 | −0.0227 | +0.0007 (tie) |

`d = bar − arm`; positive favours the arm. Intervals are 98.33 % percentile
bootstraps over 10,000 replicates, paired by seed (n = 30). The full eighteen-cell
table, including A, is in the results document.

**A notation defect, disclosed.** §7 writes `d = score(arm) − score(best
baseline)` and then states the win rule as a lower bound above zero; lower
log loss is better, so the two sentences use opposite orientations. The
artifact and the results document use `d = bar − arm`, positive favours the
arm, which is the orientation the win rule requires (`paired_bootstrap`'s
docstring says so). No interval, verdict or criterion changes; the protocol
is not edited.

**The label is not the magnitude.** C closes **65.2 %** of arm A's transfer gap
on T1 and **79.9 %** on T2 (retention 65.2 % / 79.6 %), leaving **0.0262** and
**0.0227** nats. It improves over B by **0.0034** (T1) and **0.0568** (T2). It
wins T1 revision by **0.1002** — against Replay, the bar there, which cannot
revise — and ties T2 revision (+0.0007 [−0.0012, +0.0026]). The verdict says C
does not clear the bar; it does not say the organism makes no use of the
structure, and it does not say the structure is not there.

**The bar was not "data-only".** The protocol's question and §12.5 call the
comparator *"the strongest data-only learner"*. On T2 the bar is the
**cell-level latent-state counter**, and `fit_cell_counter` takes `tag_to_cell`
from the generator; its docstring says the structure is *"here granted"*. It is
a declared member of the statistical-learner family (acquisition protocol §6.3),
so this is a naming defect, not a deviation from the committed comparator set —
but the name is wider than the thing. The verdict does not depend on it: post
hoc, C still loses T2 transfer to Replay by **0.0208** [−0.0224, −0.0192] and to
the bigram by **0.0187** [−0.0205, −0.0168]; on T1 the bar is Replay and C loses
by **0.0262** [−0.0275, −0.0249]. C's oracle is also the stronger one — the
generator's full transition support against the counter's four-cell map — so the
loss is not an artifact of the baseline being handed more.

**What the campaign can and cannot support.** It can support a statement about
where the defect is: the arm that was given the law still lost, so the target is
the use path, not candidate selection or admission precision. It cannot support
"the engine cannot use structure" (C closes most of A's gap and wins T1
revision); discovery (C is given the support; B is the discovery arm, and B also
loses); a self-sourcing result (B's graph still contains B's sleep rows, and C
inherits it under Amendment 1); "the engine with this filter installed" (C is a
counterfactual trajectory at fixed evidence); a localization inside the use path
(the experiment names the path, not the binding component); generality beyond
T1/T2; or a V2 authorisation.

**Audits.** 60/60 units ready. A1 coverage: T2 A **0.0000–0.0625** vs B/C
**0.9643–1.0000**; T1 A **0.1553–0.2549** vs **0.8812–0.9935**. A2: **473,351**
(T2) and **612,005** (T1) permitted candidates, **0** mismatches, the cap never
bound. A3: B precision **0.3182–0.3394** on T2 (band 0.3543), C admission 1.0.
A6: shuffled transfer **0.4957–0.5052** vs C **0.3569–0.3726**, Layer-1 coverage
0.0. A7: **94.0–96.2 %** (T2) and **96.2–97.7 %** (T1) of readout weight from
Layer 1. A8: **2,539,326** (T2) and **2,408,224** (T1) eligible-pair checks,
**0** mismatches, own-table symmetric difference **17–93** / **0–19** edges
(unread). A3 and A6 are not applicable on T1, with the reasons recorded before
the campaign.

**Provenance correction.** The artifact's `command` field initially named the
harness's `--campaign` path, which was not the command that ran. It was
re-assembled from the same 60 unit files with the wrapper's command; `status`,
`results`, `audits` and `analysis` are identical to the first assembly, and the
correction is disclosed in the artifact (`assembly_note`, `assembled_utc`) and
in the results document. No measurement changed.

**Why this is a finding and not only a result.** The protocol asked where the
defect is, and the answer is the use path because the arm that was given the law
still lost. The shape of the answer is the finding: correct structure closes
most of the gap, and the residual is small, consistent, and not attributable to
candidate selection. The second finding is about the instrument: **a
comparator's name is part of its definition**, and "data-only" did not describe
the T2 bar. Neither changes the verdict; both change what a reader should take
from it. The general lesson is the one from §16 and AGENTS rule 24, applied to a
pre-committed verdict: **a label and its magnitude are different claims**, and
the label must not stand in for the effect size. "Utilization fails" is the
protocol's verdict; 65–80 % of the gap closed is the measurement beside it.

→ `docs/formation_utilization_results.md` (generated from the artifact);
`docs/formation_utilization.json` / `.md`; `docs/FORMATION-UTILIZATION-
PREREGISTRATION.md` §7, §12; `docs/USER-MANUAL.md` §8.21 and finding 39; AGENTS
rule 24.

## §66 — The record is corrected, and the diagnostic is pre-registered: D0 before room, room before mechanism

**The record claim.** The formation-utilization campaign established that weak transfer despite
correct internal structure is an observed ceiling condition and selected the use path as the target
of investigation. It did not identify the binding component of that path and therefore did not, by
itself, satisfy the mechanism requirement for a V2 build authorization.

**What the correction is, and what it is not.** Section §65 measured the campaign and named the
use path. What it could not do — and did not do — is say which component of that path binds. Three
documents were still written as if the ceiling condition had never been observed. The V2 design
brief's §11 row said *"NOT OBSERVED: R1 did not pass; the structure was never formed"*; gate 5 said
the specific failure had not been demonstrated because the acquisition campaign stopped at its own
acquisition gate; and §12 said no V2 result existed. The acquisition campaign's statement was true
of the acquisition campaign. It stopped being true of the project on 2026-10-30, when arm C held the
generator's support at fixed evidence and still lost transfer on both tasks (T1 −0.0262, T2
−0.0227).

The row is **preserved and marked superseded**, not rewritten. The replacement says what was
observed, keeps the old sentence visible beside it, and gives the date. Gate 5 now reads
**specific-failure condition met; mechanism condition not**. §12 gains a bullet that says the
campaign selects the use path and does not authorise a build. That is the whole correction: no
measurement changed, no verdict was re-read, and no claim was widened. The record claim is the
sentence the three documents now share.

**Why a correction is a finding.** A project's documents are part of its instrument, and an
instrument that says "not observed" after the observation has landed is broken in the direction
that matters least visibly: it does not contradict the data, it simply stops carrying it. The V2
brief is the document a V2 decision is made from. Leaving it stale would have meant the decision
was made against the 2026-10-28 record while the 2026-10-30 result sat in a different file. The
general lesson is the one from §16 and AGENTS rule 24, applied to the *record* rather than to a
headline: **a claim that was true of an earlier campaign is not a claim about the project**, and
the correction must name the campaign it was true of.

**The diagnostic, and why it is ordered the way it is.** The next step is
[`docs/USE-PATH-DIAGNOSTIC-PREREGISTRATION.md`](docs/USE-PATH-DIAGNOSTIC-PREREGISTRATION.md),
frozen before any cell runs. Its first question is not *which component binds?* It is *is there
measurable room in the use path at this evidence?* The order is:

```
D0 reproduction  ->  room estimate  ->  mechanism mapping
```

**D0 is a validity gate, not a control.** It must reproduce the campaign's arm-C scores for all 30
seeds and all three limbs within `1e-4`. If it does not, the decomposition is of a different object
than the one that produced the ceiling result, and the only honest outcome is **AUDIT REQUIRED** —
no room estimate, no mechanism mapping. A failed denominator check invalidates a variant; a failed
D0 check invalidates the object being analysed.

**The self-test found the campaign's missing hash seed before the run.** The engine is hash-order
sensitive. Without `PYTHONHASHSEED=0`, the diagnostic's first re-run drifted from the campaign by
**4.7e-4** (retention 2.8e-4, transfer 2.0e-4, revision 4.7e-4) and the asserted structure differed
by 30 edges; with the pin it reproduced **exactly**. The campaign artifact was produced under that
seed and its command did not record it. That is a provenance defect in the campaign, not a
difference in any measurement, and the D0 tolerance was not changed to accommodate it. Amendment 1
to the diagnostic protocol pins the seed, the runner refuses to start without it, and the artifact
records it. The campaign's verdict stands; its reproducibility is now stated rather than assumed.

**The room comes before the component.** The ceiling is the generator's true conditional on the
same contexts. If the room between it and the pinned readout is below `0.01` nats on both tasks and
no variant helps, the outcome is **EVIDENCE-LIMITED**: the use path has no measurable room at this
evidence, and the target moves upstream to formation / estimation / evidence quality. That is a
successful result, not a failure of the run — it can disprove a class of use-path V2 concepts before
implementation.

**The component arms are observer-side re-scorings, not interventions.** D1 restricts the asserted
graph to Layer-1 edges (retrieval/provenance); D2 re-weights the same edges by type with **declared
constants** — Layer 1 `1.0`, every other type `0.5` — and no fitting, no calibration, no influence
from the campaign's seeds; D3 sweeps the smoothing α, selected only on `20261099`; D4 replaces the
backoff with a direct conditional with a declared add-one constant; D5 is the ceiling. D2 is
constants-only for a reason: a type weighting chosen after seeing a score would be a tuned
retrospective analysis wearing a diagnostic's name.

**What the diagnostic can and cannot do.** It can select a component for a V2 **brief**. It cannot
authorise a V2 build. C is still given the support and reads B's evidence, so a component candidate
is a hypothesis for a confirmatory protocol, not a deployable fix. B remains the discovery arm, and
the formation limitation is untouched. The owner's build decision is separate, dated, and not
supplied by any result in the diagnostic.

**Status at freeze time (superseded by §67).** Pre-registered and frozen. No diagnostic cell had been run. The result was to be written
to `docs/USE-PATH-DIAGNOSTIC-RESULTS.md` from the artifact, with the D0 gate as its first section.
**No V2 build is authorised.**

→ `docs/USE-PATH-DIAGNOSTIC-PREREGISTRATION.md`; `docs/use_path_diagnostic_freeze.json`;
`docs/ORGANICA-V2-DESIGN-BRIEF.md` §9.8, gate 5, §11, §12; `docs/USER-MANUAL.md` §8.22 and action
15; `benchmarks/use_path_diagnostic.py`; `tests/test_use_path_diagnostic.py`; AGENTS rules 13, 19,
23 and 24.

## §67 — The use-path diagnostic ran, and its own validity gate stopped it: AUDIT REQUIRED

The diagnostic was pre-registered and frozen at `a700e83` (Amendment 1, the `PYTHONHASHSEED=0`
pin; the freeze record is `2b70a2e`) and ran on 2026-10-30 over all 60 units (30 seeds × 2 tasks).
D0 asked it to reproduce the formation-vs-utilization campaign's arm-C scores on all three scored
limbs within `1e-4`. It did not: **162 of 180** seed-limbs agree, **18 fail**, and the largest
absolute difference is **0.004386** (T1 seed `20261128`, revision). The failures are **8 seeds**,
not one bad seed — T1 `20261125`, `20261128`, `20261129`; T2 `20261118`, `20261120`, `20261121`,
`20261123`, `20261130` — and they span all three limbs. Seventeen of the eighteen differences are
below `2e-3`; the 0.004386 cell is the outlier. The pre-committed outcome is therefore **AUDIT
REQUIRED**: no room estimate, no variant effect, no component, and no `evidence-limited`
conclusion. Every other control passed: the D2 constants are the declared 1.0/0.5 and cannot be
influenced by the campaign seeds; every admitted unit had an attribution and a denominator.

**The likely cause, and it is not a use-path finding.** The engine stores each event with
`time.time()`, which has coarse enough resolution that a cycle's rows can share a timestamp;
`MemoryService.recent()` orders by `time DESC` with no `rowid` tiebreak; `_load_prior_candidates()`
reads the newest 4,000 sleep rows; and the harness's `structure_edges()` keeps the first snapshot
per candidate id. A different tie order therefore keeps a different snapshot, which is enough to
move a readout by the observed amount. The code already uses `rowid DESC` in
`prune_sleep_candidates()`, so the omission is specific to `recent()`. **This is a code-path
hypothesis, not an established cause**: the campaign artifact did not record the tie order, and the
falsifier — an in-process `recent()` with a `rowid DESC` tiebreak re-run twice on a failing seed —
has not been run.

**Why the gate should stop the run.** The diagnostic exists to decompose *the object that produced
the ceiling result*. Eighteen failures at `1e-4` mean the object being decomposed is not that
object, and a room estimate or a component mapping computed on it would be a decomposition of a
different world. The tempting alternative — widen `1e-4` after seeing the failures, or report
D1–D5 anyway under an "exploratory" label — is exactly the move rule 19 and the campaign's own D0
forbid. The gate firing is the instrument working, not the study failing. It is also finding 23's
lesson in its intended direction: a check that cannot fire is decoration, and this one fired on the
condition the study existed to detect.

**What stands and what does not.** The V2 record correction stands: the campaign's ceiling condition
is observed, the specific-failure condition of gate 5 is met, and the use path is the target. The
*mechanism* condition is not met, no component was selected, and **no V2 brief follows**. The
result document's first section is the gate; the generator refuses to emit a mechanism section when
D0 fails. The next step is the reproduction audit, not another diagnostic cell and not a V2 design.

→ `docs/USE-PATH-DIAGNOSTIC-RESULTS.md`; `docs/use_path_diagnostic.json`;
`docs/USE-PATH-DIAGNOSTIC-PREREGISTRATION.md`; `docs/ORGANICA-V2-DESIGN-BRIEF.md` §9.8, gate 5,
§12; `docs/USER-MANUAL.md` §8.22 and actions 15–16; `benchmarks/use_path_diagnostic.py`;
`tests/test_use_path_diagnostic.py`; AGENTS rules 13, 19, 23, 24 and 28.

→ §68 records the later audit observation and the refined audit design.

**Superseded on the cause (2026-10-30, §69).** §69 ran this hypothesis's falsifier. The `rowid` tiebreak changes neither the per-type table nor any score, and both read orders reproduce their own runs 3/3 on all eight failing seeds, so tie order is **not supported** as the cause and is no longer the leading hypothesis. The D0 verdict and everything else in §67 stand.

## §68 — Audit observation: the candidate table is a leading forensic indicator for the D0 mismatch, and the reproduction audit design (2026-10-30)

**Status.** The formation-vs-utilization campaign's conclusion that V2 must target the use path remains operative. The use-path diagnostic could not reconstruct the campaign object to its pre-registered D0 tolerance and therefore halted before variant decomposition. The current evidence concerns the reconstructability of the campaign object, not the campaign's recorded verdicts, and the question of whether the use path has measurable room was never reached. The next step is a controlled reproduction audit using paired no-tiebreak and rowid-tiebreak runs on the failing seeds, with the campaign's recorded per-type candidate table as the intermediate endpoint, to determine whether retrieval-order instability is causal, merely correlated, or irrelevant.

**What stands, what is blocked, what is unreached.** The campaign's recorded verdicts stand. A1–A8 pass or are not applicable by their committed scope (A3 and A6 are N/A on T1); none failed, so the campaign's internal logic is not in question. What is blocked is the decomposition of the campaign object into a component: D0 fired before D1–D5, so no variant effect, room estimate or component is reported. What is unreached is the room question itself. The gap is in the reproduction relationship between the campaign artifact and the diagnostic re-run; the missing tie order is campaign-side metadata, and the re-run is the other half, so neither side is assigned the cause yet.

**The mechanical check.** The campaign artifact already records the C arm's frozen-candidate table at `results[].arms.C.per_type`; the diagnostic records the same table at `records[].per_type`. Both are produced by `candidate_summary()` in `benchmarks/acquisition_runner.py`. `python benchmarks/use_path_diagnostic.py --structure-check` matches the units by `(task, seed)` and compares the tables **before** joining the D0 outcome, so the join cannot influence whether the tables are identical. The output is `docs/use_path_diagnostic_structure.json`; its `cross_tab` is the sole source of the counts below.

**Cross-tab (source: `docs/use_path_diagnostic_structure.json`):** 51 identical/pass, 0 identical/fail, 8 different/fail, 1 different/pass.

**What the pattern does and does not mean.** Every failing unit has a different frozen-candidate table; no unit with an identical table fails; and T2 `20261122` differs structurally while all three scores stay inside the D0 tolerance. The exception is the negative control, not an anomaly: a perfect separation would be a reason to suspect hidden coupling, while one structural difference that does not reach the score is the shape a real checkpoint should have. The pattern is descriptive. It localises the divergence to the frozen candidate set, before scoring; it does not establish why the set differs. Tie order remains the leading hypothesis, not a cause. The campaign ran from an uncommitted working tree and the committed harness is later, so a stable code-revision difference is the first alternative to exclude. And counts can show *that* the set differs, not *which* candidate: neither artifact records candidate IDs or the tie order.

**The audit design.** Three layers, in order.

1. **Repeatability.** N no-tiebreak runs and N `rowid`-DESC-tiebreak runs per failing seed; compare within each arm, not only across arms.
2. **Structural reproduction.** Compare each arm's per-type table with the campaign's. Stop here if the candidate population does not reproduce; a score comparison on a different candidate set is not an attribution.
3. **Score reproduction.** Only after layer 2.

The four outcomes are: no-tiebreak unstable and tiebreak stable → ordering is the destabilizer; both stable and both differ from the campaign → look upstream of retrieval order, beginning with the code revision; tiebreak reproduces the campaign's table and scores → the campaign's effective order is consistent with `rowid` DESC; tiebreak unstable → the nondeterminism is upstream of retrieval order.

The structural checkpoint is pre-committed **in the audit**. It is not retrofitted into the diagnostic's D0: D0 remains score-based, the protocol is unchanged, and the audit is a separate instrument whose purpose is attribution, not effect estimation.

**What is not claimed.** No mechanism, no room estimate, no campaign re-score, no V2 brief and no V2 build. The per-type table is an audit instrument, not evidence about the use-path question.

→ `docs/use_path_diagnostic_structure.json`; `docs/use_path_diagnostic.json`; `docs/formation_utilization.json`; `benchmarks/use_path_diagnostic.py --structure-check`; `tests/test_use_path_diagnostic.py`; `docs/USER-MANUAL.md` §8.22; §67.

**Follow-up (2026-10-30, §69).** The audit designed here ran and returned the pre-declared *both stable, both differ* outcome: the `rowid` tiebreak is inert and both read orders are repeatable, so tie order is not supported as the cause. §69 records it.

## §69 — The tie order is not the cause: the reproduction audit on the eight failing seeds (2026-10-30)

**What was asked.** §68 committed the three-layer audit before it ran: repeatability under the shipped read order and under a `rowid DESC` tiebreak, then reproduction of the campaign's per-type candidate table, then — only if the table reproduced — reproduction of its scores. The question was whether retrieval-order instability was causal, merely correlated, or irrelevant to the D0 mismatch.

**What ran.** Eight failing seeds, two configurations, three repeats each: 48 runs, each against a fresh database through the same B-then-C path the diagnostic used, with `PYTHONHASHSEED=0` asserted at startup and inherited by every worker. The tiebreak is applied by temporarily replacing `MemoryService.recent()` in-process and restoring it; `organica/` is not edited. The self-test fires the tiebreak on two equal-timestamp rows and proves the method is restored; an incomplete set of runs is refused rather than analysed. The artifact is `docs/use_path_audit.json`; the result document is `docs/USE-PATH-AUDIT.md`, generated from it.

**Audit counts (source: `docs/use_path_audit.json`):** `seeds=8 repeats=3 runs=48 no_tiebreak_stable=8 tiebreak_stable=8 arms_agree=8 digests_agree=8 campaign_no_match=0 campaign_tie_match=0 diagnostic_no_match=8 diagnostic_tie_match=8 layer3_entered=0`

**Instrument check.** Both configurations reproduce the diagnostic's per-type table and all three D0 scores exactly on 8/8 seeds, to the diagnostic artifact's six-decimal rounding. The audit is therefore a re-run of the object D0 failed on, not a different measurement.

**Layer 1 — repeatability.** Each configuration reproduces its own per-type table in 3/3 runs on 8/8 seeds. The repeats are independent databases with independent wall-clock timestamps; they share the pinned hash seed, which is the declared constant. There is no run-to-run instability to explain on these seeds.

**The intervention is inert.** The no-tiebreak and `rowid DESC` configurations produce identical per-type tables and identical scores on 8/8 seeds. The tiebreak is a real change to the query — the self-test fires it — but on these worlds it changes nothing the run reads. A cause cannot be a difference that makes no difference.

**Layer 2 — structural reproduction.** Neither configuration reproduces the campaign's per-type table on any of the eight seeds (0/8 and 0/8). The deltas are structural, not a single drifted score: unique candidate counts move in both directions, and the edge weights move with them. T2 `20261118` is the sharpest case: its asserted-edge count and coverage are identical to the campaign's, and its candidate composition still differs. The checkpoint is doing work a score or coverage comparison cannot do.

**Layer 3 — not entered.** The design compares scores only after the candidate population reproduces. It did not, so the score differences (largest **0.004386**, T1 `20261128`, revision) are recorded as observations, not as a reproduction result.

**The verdict.** Retrieval-order instability is **not supported** as the cause of the D0 mismatch. The `rowid`-tiebreak hypothesis, as §67 stated it, does not survive its own falsifier: adding the tiebreak did not move the object, and the object is repeatable without it. The divergence is upstream of `recent()`'s tie order. This is the pattern §68 pre-declared as *both stable and both differ* → look upstream of retrieval order, beginning with the code revision; the audit follows that rule rather than inventing one after seeing the result.

**What the audit does not name.** The upstream cause is not identified. Two candidates remain, both campaign-side and both unrecorded: a campaign-time harness revision — the harness was uncommitted when the campaign ran and was committed later, so git cannot show what the campaign executed — and the campaign's execution environment, which the artifact does not record (neither the hash seed nor the tie order). The structure check constrains the first: 51 of 60 campaign units reproduce their table under this same pinned code, so a code difference that affected every unit is excluded; a difference that acts only on ordering-sensitive units is not, and neither is an environment difference. The audit does not separate them.

**What this changes.** §67's sentence naming tie order as the likely cause is superseded by this audit; the manual's §8.22 and actions 15–16 are corrected in the same turn. D0 remains fired, the diagnostic remains `AUDIT REQUIRED`, and no room estimate, mechanism, component or V2 brief follows. The campaign's recorded verdicts stand.

**What would settle it.** A hash-seed sensitivity sweep on one failing seed is the cheapest next test: if the per-type table moves across hash seeds, the campaign's unrecorded environment is sufficient to explain the mismatch; if it does not, the campaign-time code is the remaining candidate and needs a campaign-time copy rather than another re-run. The sweep was not run here. The audit's stop condition was the three layers it committed to, and adding a fourth after seeing the result would be a new instrument, not this one.

**The lesson.** An intervention must vary the thing it claims to vary. The self-test proved the tiebreak fires on a synthetic tie — that proved the hook, not the hypothesis. The hypothesis only became testable when the same intervention was run on the real seeds and the object was compared before and after; and then it failed, because the intervention made no difference. The second lesson is about missing metadata: when the record is incomplete, enumerate every unrecorded upstream quantity, not only the one the first story names. Here the tie order, the hash seed and the campaign-time code were all unrecorded, and the audit can exclude only the first.

→ `docs/USE-PATH-AUDIT.md`; `docs/use_path_audit.json`; `benchmarks/use_path_audit.py`; `tests/test_use_path_audit.py`; `docs/USE-PATH-DIAGNOSTIC-RESULTS.md`; `docs/use_path_diagnostic_structure.json`; `docs/USER-MANUAL.md` §8.22 and actions 15–16; §67; §68; AGENTS rules 13, 19, 23, 24.

## §70 — Correction (2026-10-31): the Gate 13 precision ceiling was 0.3438, and a number that starts with the same digits is not that number

**What this section records.** A ceiling that had been quoted as **0.3443** in fourteen documents, in four code files, and inside the formation-utilization campaign artifact's own A3 blocks was **0.3438**. The correction is recorded here with the evidence that it is a transcription error, the evidence that it changed no verdict, and the evidence that the obvious repair would have corrupted real measurements.

**The artifact.** `docs/gate13_allocation_rule.json` measures precision for both allocation rules, `global_top_k` and `per_source_top_k`, across three seeds and every budget: **36** measurements. The maximum is **0.3438** — seed `20261101`, global rule, `k=160`, coverage **0.4911**. The string `0.3443` occurs in **no** Gate 13 artifact. The value the project had been quoting was therefore a hand transcription, and it had been copied into the campaign artifact's A3 blocks, into `benchmarks/formation_utilization.py`'s `PRECISION_CEILING`, into `benchmarks/figure_papers.py`'s Figure 5 caption, into `tests/test_formation_utilization.py`, and into fourteen documents.

**The correction changed no verdict.** Audit A3 holds arm B's Layer-1 precision to the band `ceiling ± 0.01`. Across all **30** T2 campaign units the highest arm-B Layer-1 precision is **0.3394** — below the lower edge of the band under either constant (**0.3343** under 0.3443, **0.3338** under 0.3438). Every A3 verdict is unchanged, and the campaign's verdicts stand.

**The obvious repair would have corrupted measurements.** `0.3343` is both the derived lower band edge and the *measured* Layer-1 precision of four campaign units; six further measurements merely *begin* with `0.3443` (`0.344397`, `0.344345`, `0.344324`, `0.344364`) or `0.3543` (`0.354312`). A blanket string replacement would have rewritten eight real numbers. The result artifacts were therefore corrected **by field path** — the A3 block's prose and its derived `band_upper` only — the originals were preserved beside them (`docs/formation_utilization_pre_correction.json`, `docs/formation_utilization_timing_pre_correction.json`) with a `correction_note`, and every measurement was compared before and after. `docs/formation_utilization_timing_pre_amendment.json` and its rendered document were left as they are: they are a preserved historical record, not a statement about the ceiling.

**The lesson.** A ceiling is a measurement like any other and inherits the same failure: written once by hand and then copied, it becomes a number nobody measured. Rule 29 now says so, and it adds the second half — that a number which merely *begins* with the same digits is not that number, and that a correction to a published artifact must be made by field path, with the original kept and the measurements compared.

→ `docs/gate13_allocation_rule.json`; `docs/formation_utilization.json`; `docs/formation_utilization_pre_correction.json`; `docs/formation_utilization_timing.json`; `benchmarks/formation_utilization.py`; `benchmarks/figure_papers.py`; `docs/GATE13-CAUSAL-ACCOUNT.md`; `docs/FACTS-SHEET.md` AD10; `docs/USER-MANUAL.md` finding 40; AGENTS rule 29.

## §71 — The eight failing seeds are a hash-order artifact: the campaign's candidate population is now named

**What this section records.** The use-path diagnostic returned AUDIT REQUIRED: D0 failed on 18 seed-limbs across eight seeds. The per-type candidate **counts** were known; the candidate **identity** was not. This section records the answer to the owner's question of 2026-10-31 — *why does the campaign artifact contain a C-arm candidate population that no current deterministic reconstruction reproduces?* — and the membership audit that answers it.

**The campaign artifact carries no candidate identity.** Not one candidate ID appears in `docs/formation_utilization.json`, `docs/use_path_diagnostic.json` or `docs/use_path_audit.json`; the campaign artifact records a per-type table of `unique_count` and `edge_weight` and nothing more. The campaign-side population is therefore recoverable only by re-running the campaign harness and keeping the run whose fingerprint equals the campaign's. That was the pivotal unknown, and it is now settled.

**The code is excluded, by provenance and then by measurement.** `git diff a95305d HEAD -- organica/` is empty: the engine is byte-identical to the state the campaign ran against, and `a95305d` (2026-10-25 09:21 -0600) precedes the campaign's generation stamp (2026-10-31T02:09:33Z). Every file the harness executes was last modified before the campaign ran. The one file whose campaign-time state is not pinned by a commit — `benchmarks/formation_utilization.py`, committed 89 minutes after the campaign finished — is closed by measurement rather than by argument: under the committed code, with the hash seed varied, the campaign's own per-type table is reproduced **exactly** on **8 of the 8 failing seeds**. The code state is sufficient to produce the campaign's population, so the divergence is not in the code.

**The environment is the hash seed.** The engine iterates sets of strings, and CPython randomises string hashing per process unless `PYTHONHASHSEED` is pinned. The use-path audit and the diagnostic pinned `PYTHONHASHSEED=0`; the campaign artifact records neither the hash seed nor the tie order, and the campaign ran with `--workers 10`, so each of its worker processes carried its own hash seed. Sweeping the hash seed reproduces the campaign's population exactly on **8 of 8** failing seeds, and the control seed's population is the same at every one of the 16 hash seeds swept.

**The membership.** Across the eight failing seeds, **252** candidate IDs are present in the campaign and absent from the current reconstruction, and **288** are present in the reconstruction and absent from the campaign; **1804** are on both sides. The names are in `docs/candidate_membership_audit.json` and in `docs/CANDIDATE-MEMBERSHIP-AUDIT.md`.

| Task | Seed | Hash seeds that reproduce the campaign | Both | Missing (campaign only) | Added (reconstruction only) | First differing cycle |
|---|---|---|---|---|---|---|
| T1 | 20261125 | 2, 5, 9, 15 | 254 | 35 | 65 | 11 |
| T1 | 20261128 | 7, 8, 10, 12, 13, 14 | 234 | 63 | 75 | 3 |
| T1 | 20261129 | 2, 5, 9, 15 | 231 | 62 | 64 | 2 |
| T2 | 20261118 | 1, 2, 4, 5, 9, 10, 14 | 227 | 9 | 7 | 5 |
| T2 | 20261120 | 13 | 215 | 21 | 11 | 5 |
| T2 | 20261121 | 2, 4, 5, 6, 8, 9 | 210 | 32 | 36 | 5 |
| T2 | 20261123 | 8, 10, 12, 14 | 212 | 20 | 14 | 5 |
| T2 | 20261130 | 2, 3, 9, 15 | 221 | 10 | 16 | 5 |

The differences, by type:

| Task | Seed | Type | Missing | Added |
|---|---|---|---|---|
| T1 | 20261125 | anomaly | 6 | 7 |
| T1 | 20261125 | dream | 5 | 9 |
| T1 | 20261125 | experiment | 2 | 4 |
| T1 | 20261125 | hypothesis | 3 | 6 |
| T1 | 20261125 | investigation | 2 | 4 |
| T1 | 20261125 | loop_candidate | 3 | 9 |
| T1 | 20261125 | prediction_candidate | 0 | 9 |
| T1 | 20261125 | process_candidate | 5 | 5 |
| T1 | 20261125 | question | 2 | 3 |
| T1 | 20261125 | theory | 2 | 4 |
| T1 | 20261125 | workflow_concept | 5 | 5 |
| T1 | 20261128 | anomaly | 12 | 11 |
| T1 | 20261128 | dream | 8 | 14 |
| T1 | 20261128 | experiment | 5 | 5 |
| T1 | 20261128 | hypothesis | 5 | 8 |
| T1 | 20261128 | investigation | 5 | 5 |
| T1 | 20261128 | loop_candidate | 3 | 7 |
| T1 | 20261128 | meta_concept | 1 | 0 |
| T1 | 20261128 | prediction_candidate | 3 | 4 |
| T1 | 20261128 | process_candidate | 5 | 5 |
| T1 | 20261128 | question | 5 | 5 |
| T1 | 20261128 | theory | 6 | 6 |
| T1 | 20261128 | workflow_concept | 5 | 5 |
| T1 | 20261129 | anomaly | 6 | 8 |
| T1 | 20261129 | dream | 8 | 8 |
| T1 | 20261129 | experiment | 6 | 6 |
| T1 | 20261129 | hypothesis | 10 | 12 |
| T1 | 20261129 | investigation | 6 | 6 |
| T1 | 20261129 | loop_candidate | 2 | 0 |
| T1 | 20261129 | meta_concept | 1 | 1 |
| T1 | 20261129 | prediction_candidate | 2 | 2 |
| T1 | 20261129 | process_candidate | 4 | 4 |
| T1 | 20261129 | question | 5 | 6 |
| T1 | 20261129 | theory | 6 | 7 |
| T1 | 20261129 | workflow_concept | 6 | 4 |
| T2 | 20261118 | anomaly | 0 | 1 |
| T2 | 20261118 | dream | 2 | 0 |
| T2 | 20261118 | experiment | 2 | 1 |
| T2 | 20261118 | hypothesis | 1 | 1 |
| T2 | 20261118 | investigation | 2 | 1 |
| T2 | 20261118 | loop_candidate | 1 | 2 |
| T2 | 20261118 | meta_concept | 1 | 1 |
| T2 | 20261120 | anomaly | 1 | 1 |
| T2 | 20261120 | dream | 4 | 2 |
| T2 | 20261120 | experiment | 5 | 2 |
| T2 | 20261120 | investigation | 5 | 2 |
| T2 | 20261120 | loop_candidate | 2 | 2 |
| T2 | 20261120 | process_candidate | 2 | 1 |
| T2 | 20261120 | workflow_concept | 2 | 1 |
| T2 | 20261121 | anomaly | 6 | 5 |
| T2 | 20261121 | dream | 5 | 7 |
| T2 | 20261121 | experiment | 6 | 8 |
| T2 | 20261121 | hypothesis | 1 | 1 |
| T2 | 20261121 | investigation | 6 | 8 |
| T2 | 20261121 | loop_candidate | 5 | 4 |
| T2 | 20261121 | meta_concept | 1 | 1 |
| T2 | 20261121 | process_candidate | 1 | 1 |
| T2 | 20261121 | workflow_concept | 1 | 1 |
| T2 | 20261123 | anomaly | 2 | 2 |
| T2 | 20261123 | dream | 2 | 1 |
| T2 | 20261123 | experiment | 4 | 2 |
| T2 | 20261123 | investigation | 4 | 2 |
| T2 | 20261123 | loop_candidate | 2 | 1 |
| T2 | 20261123 | process_candidate | 3 | 3 |
| T2 | 20261123 | workflow_concept | 3 | 3 |
| T2 | 20261130 | anomaly | 3 | 2 |
| T2 | 20261130 | dream | 1 | 4 |
| T2 | 20261130 | experiment | 1 | 2 |
| T2 | 20261130 | investigation | 1 | 2 |
| T2 | 20261130 | loop_candidate | 4 | 4 |
| T2 | 20261130 | process_candidate | 0 | 1 |
| T2 | 20261130 | workflow_concept | 0 | 1 |

**Where the two sets first diverge.** The two populations part company early — cycle **2** (T1/20261129); cycle **3** (T1/20261128); cycle **5** (T2/20261118, T2/20261120, T2/20261121, T2/20261123, T2/20261130); cycle **11** (T1/20261125) — measured from arm C's per-cycle admitted candidate stream, which is the membership as it was decided, cycle by cycle. Arm B's own table matches the campaign's under the reproducing hash seed on **8 of the 8** failing seeds, and differs from it under the pinned hash seed on **8 of the 8**. Arm C reads arm B's recorded temporal graphs, so on those seeds the divergence enters in the shared acquisition-and-sleep path and arm C inherits it through the graphs it reads, rather than in arm C's admission filter.

**The controls.** The baseline run at the pinned hash seed reproduces the use-path audit's recorded reconstruction on **every** type of **every** seed (no), the control seed's population is identical at every hash seed swept with **0** candidate-ID differences in total, and the runs that reproduce the campaign agree with one another on the candidate IDs (yes). The audit is therefore able to return "identical" as well as "different", and the membership it reports is determined by the artifact rather than by a guess.

**A correction to the earlier reading.** An earlier build of this audit reported T1/20261125 as reproducing the campaign at the pinned hash seed, with no membership difference and no first differing cycle. The cached run it read for that pair was not a measurement: it carried the campaign's per-type table. Recomputed, it disagrees — and it agrees, on every type, with the reconstruction the use-path audit had already recorded independently. The rebuilt artifact is the one of record; the earlier one is superseded.

**What this does not establish.** It does not re-score D0, and it does not change the campaign's verdict. It says where the two candidate populations came from; it does not say what the D0 limb scores would be under the campaign's hash seed, which is a separate measurement that has not been made, and it does not name a single order-dependent code path. The sweep covers hash seeds 0–15; a seed outside that range would produce a different population, and the campaign's own hash seeds are not recoverable, only its population.

→ `docs/candidate_membership_audit.json`; `docs/CANDIDATE-MEMBERSHIP-AUDIT.md`; `benchmarks/candidate_membership_audit.py`; `docs/formation_utilization.json`; `docs/use_path_audit.json`; `docs/USE-PATH-AUDIT.md`; `docs/USE-PATH-DIAGNOSTIC-RESULTS.md`.

## §72 — The candidate pool at the divergence cycle, named

**What this section records.** §71 established where the campaign's candidate population and the current reconstruction's part company — at sleep cycles 2 to 11, depending on the seed — and named the candidate IDs that differ. It could not say **which candidates were in the pool at that cycle**, because the engine's 4,000-row sleep window it captured is a snapshot of the read-back at the arm's snapshot point, two or three cycles before the end of the run, while the divergences are early. This section records the instrument that closes that gap, and what it found.

**The capture is addressed, and the addressing is proved.** The sleep service reads its window once per cycle, and the harness's arm loop adds exactly two reads outside the cycle loop, so the i-th window read of an arm is the i-th cycle of that arm. That correspondence is not assumed: the engine stores one `sleep:meta` event per cycle carrying that cycle's number, and the window is read newest-first, so **the newest cycle marker in the i-th window must carry cycle i**. The instrument refuses to report a window whose marker does not say so, and **16 of 16** captured window pairs here are addressed by their own marker.

**Correction (2026-11-01): the table that follows is the cycle *before* the divergence.** §72 recorded it as "the pool at the divergence cycle", and it is not: `first_divergence()` stores a zero-based index, the capture read window index *k* as cycle *k*, and window index *i* is engine cycle *i*, so every pool below is one cycle early. The 2026-11-01 re-measurement in `docs/divergence_cycle_capture.json` reads the divergence cycle and the cycle before it and replaces this report's numbers; the table is kept here as what was measured on 2026-10-31. It is still a real comparison — both sides are read at the same cycle — but the cycle it names is the one before the admitted streams part company, not the one at which they do.

**What the re-measurement found (2026-11-01).** At the divergence cycle itself the two sides hold the **same set** of candidate IDs in **0 of 16** arm-pairs and the same order in **0 of 16**: membership differs everywhere. The earlier reading — the same set in **11** of 16, and on **3** seeds the same set *and* order while the admitted stream still differed — is what the preceding cycle shows. That matters beyond the labelling: the inference in §73 that the difference must therefore arise **inside** the cycle rested on those identical pools, and it does not survive. At the cycle where the admitted streams part company, the pools have already parted company too. What remains open is not whether the pools differ at the divergence, but **when, and by what step, they first came to differ** — which is a sharper question than the one this instrument was built to answer.

**The pool at the divergence cycle.** | T1 | 20261125 | 11 | B | 280 | 274 | 272 | 8 | 2 | no | no |
| T1 | 20261125 | 11 | C | 260 | 255 | 252 | 8 | 3 | no | no |
| T1 | 20261128 | 3 | B | 37 | 37 | 37 | 0 | 0 | yes | no |
| T1 | 20261128 | 3 | C | 37 | 37 | 37 | 0 | 0 | yes | no |
| T1 | 20261129 | 2 | B | 39 | 39 | 39 | 0 | 0 | yes | no |
| T1 | 20261129 | 2 | C | 39 | 39 | 39 | 0 | 0 | yes | no |
| T2 | 20261118 | 5 | B | 28 | 28 | 28 | 0 | 0 | yes | no |
| T2 | 20261118 | 5 | C | 8 | 8 | 8 | 0 | 0 | yes | yes |
| T2 | 20261120 | 5 | B | 59 | 61 | 55 | 4 | 6 | no | no |
| T2 | 20261120 | 5 | C | 23 | 22 | 22 | 1 | 0 | no | no |
| T2 | 20261121 | 5 | B | 62 | 61 | 61 | 1 | 0 | no | no |
| T2 | 20261121 | 5 | C | 18 | 18 | 18 | 0 | 0 | yes | no |
| T2 | 20261123 | 5 | B | 23 | 23 | 23 | 0 | 0 | yes | no |
| T2 | 20261123 | 5 | C | 4 | 4 | 4 | 0 | 0 | yes | yes |
| T2 | 20261130 | 5 | B | 37 | 37 | 37 | 0 | 0 | yes | no |
| T2 | 20261130 | 5 | C | 10 | 10 | 10 | 0 | 0 | yes | yes |

**The pool holds the same candidates and a different order — for most seeds.** This is a different finding from the membership one, because a pool is a sequence and not just a set. Across the 16 arm-pairs, the two sides hold the **same set** of candidate IDs at the divergence cycle in **11** of them and the **same order** in only **3**; in **8** the candidates are identical and the order is not. By arm: arm B holds the same set in 5 of 8 and the same order in 0 of 8; arm C holds the same set in 6 of 8 and the same order in 3 of 8. So the divergence between the two populations is, for most seeds, **not a difference in which candidates existed — it is a difference in the order they were read in**.

**Correction (2026-11-01) — this paragraph is a measurement one cycle early, and its conclusion reverses.** What was claimed: the pools hold the same candidates and differ in order, so the divergence is an ordering difference for most seeds. Why it was wrong: `candidate_membership_audit.first_divergence()` stores `first_cycle` as a zero-based index, while this capture read window index *k* as cycle *k*, so every pool above is the cycle **before** the divergence. How it was derived: the audit's own guard (`ok = (marker == index) if index > 0 else (marker is None)`) and 16 of 16 `addressed: true` addresses fix window index *i* to engine cycle *i*, so the correct pair is `(index + 1, index)`. What remains after the correction: re-measured at the divergence cycle itself (`OBSERVER_VERSION` 3, 16 runs, 0 cached), the two sides hold the **same set** in **0 of 16** and the **same order** in **0 of 16** — membership differs everywhere. The order-only reading, and with it the inference that the divergence lies *inside* the cycle rather than in the pool, does not survive.

**Correction (2026-11-01) — this paragraph is a measurement one cycle early, and its conclusion reverses.** What was claimed: the pools hold the same candidates and differ only in order. Why it was wrong: `candidate_membership_audit.first_divergence()` stores `first_cycle` as a zero-based index, while this capture read window index *k* as cycle *k*, so every pool above is the cycle **before** the divergence. How it was derived: the audit's own guard (`ok = (marker == index) if index > 0 else (marker is None)`) and 16 of 16 `addressed: true` addresses fix window index *i* to engine cycle *i*, so the correct pair is `(index + 1, index)`. What remains: re-measured at the divergence cycle itself (`OBSERVER_VERSION` 3, 16 runs), the two sides hold the **same set** in **0 of 16** and the **same order** in **0 of 16** — membership differs everywhere, so the order-only reading and its inference that the difference lies *inside* the cycle do not survive.

**Three seeds show the pool identical in set *and* order — and the divergence is still there.** For T2 / 20261118, T2 / 20261123, T2 / 20261130 in arm C, the two sides' pools at the divergence cycle are identical candidate-for-candidate and in the same sequence, and arm C's admitted stream still differs at that cycle. For those, the divergence cannot be attributed to the pool at the divergence cycle at all: the same candidates, read back in the same order, were available, and the difference arose inside the cycle. This is the sharpest thing the capture says, because it is a negative result about the pool and a positive localisation of the divergence at the same time.

**Two orders, and the capture measures one of them.** The engine reads its window back with `ORDER BY time DESC` and no rowid tiebreak (`organica/memory.py:390`), so the pool arrives as a sequence and the capture measures that sequence. Inside the cycle, the candidate list is assembled from that sequence in an order that is *not* the sequence: the tags of each prior candidate are collected into a `set` (`organica/sleep.py:1201`) and the candidates of each tag into another (`organica/sleep.py:1223`, `distinct_ids = list(set(cid for cid, _ in refs))`). Set iteration order over strings follows the process's hash seed, so two processes reading the *same* pool assemble it in *different* orders. That is the mechanism the identical-pool seeds point at, and it is the same mechanism §71 identified from the outside.

**The order parts company at the divergence cycle.** The capture holds the window for the cycle before the divergence as well, so it can say whether the reordering *is* the divergence or merely preceded it. Where the two sides' pools were identical in set and order at the previous cycle and identical in set but different in order at the divergence cycle, the two are the same event. That holds in **6** of the 16 arm-pairs.

| Task | Seed | Cycle | Arm | Previous cycle — same set / same order | This cycle — same set / same order | The reordering coincides with the divergence |
|---|---|---|---|---|---|---|
| T1 | 20261125 | 11 | B | no / no | no / no | no |
| T1 | 20261125 | 11 | C | no / no | no / no | no |
| T1 | 20261128 | 3 | B | yes / no | yes / no | no |
| T1 | 20261128 | 3 | C | yes / no | yes / no | no |
| T1 | 20261129 | 2 | B | yes / yes | yes / no | yes |
| T1 | 20261129 | 2 | C | yes / yes | yes / no | yes |
| T2 | 20261118 | 5 | B | yes / yes | yes / no | yes |
| T2 | 20261118 | 5 | C | yes / yes | yes / yes | no |
| T2 | 20261120 | 5 | B | no / no | no / no | no |
| T2 | 20261120 | 5 | C | no / no | no / no | no |
| T2 | 20261121 | 5 | B | yes / no | no / no | no |
| T2 | 20261121 | 5 | C | yes / yes | yes / no | yes |
| T2 | 20261123 | 5 | B | yes / yes | yes / no | yes |
| T2 | 20261123 | 5 | C | yes / yes | yes / yes | no |
| T2 | 20261130 | 5 | B | yes / yes | yes / no | yes |
| T2 | 20261130 | 5 | C | yes / yes | yes / yes | no |

**What entered and what left, since the cycle before.** - **T1 / 20261125, cycle 11** — since the cycle before, the campaign side gained 48 and lost 45; the current side gained 43 and lost 44.
  - campaign side gained: `anomaly_23b63138`, `anomaly_54edd873`, `anomaly_7291f90a`, `anomaly_ae98fe13`, `anomaly_c9ea3d58`, `dream_cond_81149fad`, `dream_cond_bbedbdd9`, `dream_mut_3f2f69c4`, `dream_mut_eed6dbe9`, `exp_48d69d81`, `exp_51248508`, `exp_6a2dbdd3`, `exp_773fe6b0`, `hyp_0834bc52`, `hyp_2ff50859`, `hyp_33f01105`, `hyp_5be3da66`, `hyp_8f1c7481`, `hyp_a3c4b048`, `hyp_b3c6c90d`, `hyp_c36bbb91`, `hyp_cecbe745`, `inv_02e7b18b`, `inv_1f070e58`, `inv_2177d7b0`, `inv_af1a9d80`, `loop_0834bc52`, `loop_33f01105`, `loop_69e70153`, `meta_cfd90af8`, `pred_050c5ef4`, `pred_b67853a9`, `process_0834bc52`, `process_33f01105`, `process_45ba4f3d`, `process_5be3da66`, `question_4081f8ec`, `question_5dcbf6cd`, `question_69e70153`, `question_f88106c4`, `theory_4081f8ec`, `theory_5dcbf6cd`, `theory_69e70153`, `theory_f88106c4`, `workflow_0834bc52`, `workflow_33f01105`, `workflow_45ba4f3d`, `workflow_5be3da66`
  - current side gained: `anomaly_23b63138`, `anomaly_54edd873`, `anomaly_7291f90a`, `anomaly_c9ea3d58`, `dream_cond_0f32fe15`, `dream_cond_81149fad`, `dream_mut_3f2f69c4`, `dream_mut_eed6dbe9`, `exp_48d69d81`, `exp_51248508`, `exp_773fe6b0`, `hyp_0834bc52`, `hyp_2ff50859`, `hyp_33f01105`, `hyp_5be3da66`, `hyp_8f1c7481`, `hyp_a3c4b048`, `hyp_b3c6c90d`, `hyp_c36bbb91`, `hyp_cecbe745`, `inv_02e7b18b`, `inv_1f070e58`, `inv_af1a9d80`, `loop_0834bc52`, `loop_33f01105`, `loop_69e70153`, `meta_cfd90af8`, `pred_050c5ef4`, `pred_b67853a9`, `process_0834bc52`, `process_33f01105`, `process_45ba4f3d`, `process_5be3da66`, `question_4081f8ec`, `question_5dcbf6cd`, `question_69e70153`, `theory_4081f8ec`, `theory_5dcbf6cd`, `theory_69e70153`, `workflow_0834bc52`, `workflow_33f01105`, `workflow_45ba4f3d`, `workflow_5be3da66`
  - campaign side lost: `anomaly_27da00e9`, `anomaly_28d771b0`, `anomaly_41f383df`, `anomaly_4a426aff`, `anomaly_54bbc07a`, `anomaly_85adf0bb`, `anomaly_931689a6`, `anomaly_b17cef4a`, `anomaly_b55ed761`, `anomaly_cbe369ec`, `anomaly_d1f50b4c`, `anomaly_e604a0c2`, `anomaly_efd4670a`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_cond_45ba4f3d`, `dream_mut_55337662`, `exp_14f62bf0`, `exp_4963470c`, `exp_4e8f09df`, `exp_ed2c60fa`, `hyp_18e1d6f5`, `hyp_45ba4f3d`, `hyp_5711aaab`, `hyp_aa517900`, `hyp_aeff9bcd`, `hyp_b516bed8`, `hyp_c86f2f15`, `inv_6111b8d8`, `inv_7c1ea7a8`, `inv_8b05d0b5`, `inv_b28ec89c`, `process_8e76c158`, `process_c9409791`, `process_e70d60c0`, `question_0cc6644f`, `theory_17655226`, `theory_27da00e9`, `theory_bef66e35`, `theory_d73713a5`, `theory_f2459dc9`, `workflow_7ff50e2b`, `workflow_c9409791`, `workflow_e70d60c0`
  - current side lost: `anomaly_27da00e9`, `anomaly_28d771b0`, `anomaly_41f383df`, `anomaly_4a426aff`, `anomaly_54bbc07a`, `anomaly_85adf0bb`, `anomaly_931689a6`, `anomaly_b17cef4a`, `anomaly_b55ed761`, `anomaly_cbe369ec`, `anomaly_e3f06f4a`, `anomaly_e604a0c2`, `anomaly_efd4670a`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_cond_45ba4f3d`, `dream_mut_55337662`, `exp_14f62bf0`, `exp_4963470c`, `exp_4e8f09df`, `exp_ed2c60fa`, `hyp_18e1d6f5`, `hyp_45ba4f3d`, `hyp_5711aaab`, `hyp_aa517900`, `hyp_aeff9bcd`, `hyp_b516bed8`, `hyp_c86f2f15`, `inv_6111b8d8`, `inv_7c1ea7a8`, `inv_8b05d0b5`, `inv_b28ec89c`, `process_8e76c158`, `process_c9409791`, `process_e70d60c0`, `theory_17655226`, `theory_27da00e9`, `theory_bef66e35`, `theory_d73713a5`, `theory_f2459dc9`, `workflow_7ff50e2b`, `workflow_c9409791`, `workflow_e70d60c0`
- **T1 / 20261128, cycle 3** — since the cycle before, the campaign side gained 28 and lost 0; the current side gained 28 and lost 0.
  - campaign side gained: `anomaly_2f69dab0`, `anomaly_d81bba30`, `anomaly_eb5eb07e`, `anomaly_f98b9a8a`, `dream_analogy_2996247c`, `dream_analogy_456a14f9`, `dream_analogy_a9ca2e7b`, `exp_a1917fa9`, `exp_b805662b`, `exp_eb3f20a6`, `hyp_34e4a7fb`, `hyp_5ec1ef7e`, `inv_6cdc4284`, `inv_7bc8a3f5`, `inv_ab46b17a`, `loop_417da26f`, `loop_d81bba30`, `loop_fc1dfe44`, `meta_2655399a`, `meta_fd8ed7f1`, `phrase_e2484dcd`, `pred_1908f98b`, `pred_417da26f`, `pred_5242671c`, `pred_b38b643c`, `pred_fc1dfe44`, `process_34e4a7fb`, `workflow_34e4a7fb`
  - current side gained: `anomaly_2f69dab0`, `anomaly_d81bba30`, `anomaly_eb5eb07e`, `anomaly_f98b9a8a`, `dream_analogy_2996247c`, `dream_analogy_456a14f9`, `dream_analogy_a9ca2e7b`, `exp_a1917fa9`, `exp_b805662b`, `exp_eb3f20a6`, `hyp_34e4a7fb`, `hyp_5ec1ef7e`, `inv_6cdc4284`, `inv_7bc8a3f5`, `inv_ab46b17a`, `loop_417da26f`, `loop_d81bba30`, `loop_fc1dfe44`, `meta_2655399a`, `meta_fd8ed7f1`, `phrase_e2484dcd`, `pred_1908f98b`, `pred_417da26f`, `pred_5242671c`, `pred_b38b643c`, `pred_fc1dfe44`, `process_34e4a7fb`, `workflow_34e4a7fb`
- **T1 / 20261129, cycle 2** — since the cycle before, the campaign side gained 32 and lost 0; the current side gained 32 and lost 0.
  - campaign side gained: `anomaly_07edbffc`, `anomaly_e5da7fbd`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_analogy_b0a67091`, `exp_14f62bf0`, `exp_296eb82c`, `exp_4e8f09df`, `exp_ed2c60fa`, `hyp_23c7c1fa`, `hyp_9e19432e`, `inv_2395dfbb`, `inv_6111b8d8`, `inv_8b05d0b5`, `inv_b28ec89c`, `loop_1908f98b`, `loop_313a43d6`, `loop_417da26f`, `loop_b58e2626`, `meta_548a4251`, `meta_b1601f69`, `phrase_b58e2626`, `pred_1908f98b`, `pred_313a43d6`, `pred_417da26f`, `pred_5242671c`, `pred_972d3173`, `pred_d22148a4`, `pred_de4bea22`, `process_23c7c1fa`, `workflow_23c7c1fa`
  - current side gained: `anomaly_07edbffc`, `anomaly_e5da7fbd`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_analogy_b0a67091`, `exp_14f62bf0`, `exp_296eb82c`, `exp_4e8f09df`, `exp_ed2c60fa`, `hyp_23c7c1fa`, `hyp_9e19432e`, `inv_2395dfbb`, `inv_6111b8d8`, `inv_8b05d0b5`, `inv_b28ec89c`, `loop_1908f98b`, `loop_313a43d6`, `loop_417da26f`, `loop_b58e2626`, `meta_548a4251`, `meta_b1601f69`, `phrase_b58e2626`, `pred_1908f98b`, `pred_313a43d6`, `pred_417da26f`, `pred_5242671c`, `pred_972d3173`, `pred_d22148a4`, `pred_de4bea22`, `process_23c7c1fa`, `workflow_23c7c1fa`
- **T2 / 20261118, cycle 5** — since the cycle before, the campaign side gained 7 and lost 0; the current side gained 7 and lost 0.
  - campaign side gained: `anomaly_7a9d11ec`, `anomaly_9218f450`, `anomaly_f55ba952`, `anomaly_fe1fa533`, `loop_e6f8a3e6`, `pred_53a54188`, `pred_a908d7e0`
  - current side gained: `anomaly_7a9d11ec`, `anomaly_9218f450`, `anomaly_f55ba952`, `anomaly_fe1fa533`, `loop_e6f8a3e6`, `pred_53a54188`, `pred_a908d7e0`
- **T2 / 20261120, cycle 5** — since the cycle before, the campaign side gained 6 and lost 0; the current side gained 6 and lost 0.
  - campaign side gained: `anomaly_0f9a2c29`, `anomaly_29e93ad4`, `anomaly_3329a612`, `loop_18e1d6f5`, `loop_57b28f60`, `pred_fc1dfe44`
  - current side gained: `anomaly_0f9a2c29`, `anomaly_29e93ad4`, `anomaly_3329a612`, `loop_18e1d6f5`, `loop_57b28f60`, `pred_fc1dfe44`
- **T2 / 20261121, cycle 5** — since the cycle before, the campaign side gained 4 and lost 0; the current side gained 4 and lost 0.
  - campaign side gained: `anomaly_2cb3d759`, `anomaly_3b873ad2`, `anomaly_a382afab`, `loop_a5f498cc`
  - current side gained: `anomaly_2cb3d759`, `anomaly_3b873ad2`, `anomaly_a382afab`, `loop_a5f498cc`
- **T2 / 20261123, cycle 5** — since the cycle before, the campaign side gained 3 and lost 0; the current side gained 3 and lost 0.
  - campaign side gained: `anomaly_156c72ae`, `anomaly_54d9f6f7`, `anomaly_ba445078`
  - current side gained: `anomaly_156c72ae`, `anomaly_54d9f6f7`, `anomaly_ba445078`
- **T2 / 20261130, cycle 5** — since the cycle before, the campaign side gained 8 and lost 0; the current side gained 8 and lost 0.
  - campaign side gained: `anomaly_2020d089`, `anomaly_30647f48`, `anomaly_41a060d2`, `anomaly_f2052a36`, `loop_63ac32e2`, `pred_7498423f`, `pred_a6f80540`, `pred_c39ad859`
  - current side gained: `anomaly_2020d089`, `anomaly_30647f48`, `anomaly_41a060d2`, `anomaly_f2052a36`, `loop_63ac32e2`, `pred_7498423f`, `pred_a6f80540`, `pred_c39ad859`

**The capture reproduces.** The sixteen parts were written twice, by two independent processes at the same hash seeds, and compared field by field: **16 of 16 identical**. The capture is a measurement that can be taken again.

**Two limits, stated.** 2 of the 16 captured window pairs were already at the engine's 4,000-row cap, so for those the pool is a truncated view of the candidate history rather than the whole of it; the artifact records which, and the reader can tell the two apart. And a pool is the **input** to the decision, not the decision: this names what the organism had in front of it when the two populations parted company, and it does not decompose the ranking that turned that pool into an admitted set.

**What this does not establish.** It does not re-score D0 and it does not change any verdict. It does not name a single causal candidate, and it does not establish that the order difference *caused* the admitted-stream difference: the pool differs in order, and the admitted stream differs, but the link between them is the engine's ranking, which this instrument observes and does not decompose — nor the assembly step that precedes the ranking. The supported claim is the narrower one: **at the cycle where the populations part company, the two sides differ in membership in 16 of 16 arm-pairs and in read-back order in 16 of 16.** *(Corrected 2026-11-01: this paragraph closed on "on three seeds the pool is identical and the divergence is still there", which was measured one cycle before the divergence; re-measured at the divergence cycle no arm-pair holds the same set, so the identical-pool clause is withdrawn while the narrower claim above is what the artifact supports.)*

→ `docs/divergence_cycle_capture.json`; `docs/DIVERGENCE-CYCLE-CAPTURE.md`; `benchmarks/divergence_cycle_capture.py`; `docs/candidate_membership_audit.json`; `docs/CANDIDATE-MEMBERSHIP-AUDIT.md`; journal §71.

## §73 — The construction-order hypothesis, pre-registered

**What this section records.** The candidate-membership audit (§71) established where the campaign's candidate population and the current reconstruction's part company, and the divergence-cycle capture (§72) named the candidate pool at that cycle and the order it was read back in. It also recorded a negative result about the pool: for **3** arm-C pairs the two sides' pools at the divergence cycle are identical **in set and in order**, and arm C's admitted stream still differs at that cycle. For those, the difference arose inside the cycle.

**What the engine's construction does with order.** Reading the frozen source finds four places where the construction depends on a sequence the hash seed changes. `_score_tags` iterates a **set of strings** and then stable-sorts on `frequency`, an integer that ties constantly, so equal-frequency tags keep the set's order (`organica/sleep.py:904-920`). The temporal graph is read with `ORDER BY count DESC` and **no tiebreak**, over a table with no index on `count`, so tied rows come back in scan order — insertion order (`organica/memory.py:379-385`, `:122-127`) — and the graph is built in that order (`organica/sleep.py:871-875`). `_build_predictions` stable-sorts on `temporal_count` alone (`organica/sleep.py:1139-1160`). And `_build_anomalies` sorts its targets on the count alone, so among equal counts **the first in the graph's order becomes the anomaly's expected tag** — that one changes a candidate's *content*, not only its position (`organica/sleep.py:1167`). The composite assembly iterates sets throughout (`organica/sleep.py:1201`, `:1217`, `:1223`).

**What does not bind, stated because the opposite is the obvious guess.** The harness overrides the predictions cap only: `CAP_A = 20`, `CAP_B = 1_000` (`benchmarks/formation_utilization.py:195-196`). Arms B and C therefore keep every prediction the builder produces, and the `MAX_PREDICTIONS = 20` truncation **does not bind** in the campaign's arms. The eight failing seeds are not eight seeds whose predictions were cut at twenty.

**Identity is not at risk.** `_make_id` is a SHA-256 of the key parts (`organica/sleep.py:45-48`), so a candidate's id is identical in both runs wherever its inputs are. The divergence is not a slot getting a different name; it is the same candidates assembled differently — and, at the anomaly site, a different candidate assembled at all.

**The hypothesis, pre-registered.** **H1** — the eight failing seeds' divergence enters through **order-sensitive candidate construction**: the engine assembles its candidates from sequences whose order the hash seed changes, so the same world produces different candidate lists. **H2 (the strong form)** — canonicalising that order removes the divergence: with the harness assembling candidates from canonically ordered inputs, the eight failing seeds' per-type tables become **hash-seed invariant**.

**Predictions.** **P1** — at the divergence cycle, the two sides' assembled lists differ for at least one candidate type, and the difference is visible in a builder's **pre-sort** sequence. **P2** — the control seed's assembled lists are identical at every hash seed, for every type. **P3** — under the canonicalised-order intervention, the eight failing seeds' per-type tables become hash-seed invariant.

**Falsification criteria.** **F1** — if the canonicalisation leaves the tables still varying with the hash seed, the order channel is not sufficient and **H2 is refuted**; the search moves on rather than being re-tuned. **F2** — if the canonicalisation changes the **control** seed's table at a fixed hash seed, the intervention is not equivalent, the experiment is confounded, and no conclusion may be drawn from it. **F3** — a type whose assembled list is identical in membership and order on both sides at every cycle up to the divergence cycle is **excluded** as the site.

**The instrument.** Two arms. Arm A is a read-only observer that persists, per type and per cycle, the assembled list in order, its pre-sort sequence where the builder has one, the cap that was applied, the tie structure at the cap boundary, and the graph's order — and reports the first position at which the two sides differ, and whether the difference is in the order, in the membership or in a candidate's content. It inherits the capture's addressing rule: a window whose position is not witnessed by the engine's own cycle marker is refused, not reported. Arm B canonicalises the construction order in the harness only — the graph's rows by `(tag_from, tag_to)`, the composite inputs by sorted iteration — and asks the decisive question: do the eight failing seeds' tables become hash-seed invariant?

**Controls.** **C1** the control seed stays invariant under the observer and byte-identical under the intervention at a fixed hash seed. **C2** the observer is behaviour-neutral: a run with it and a run without it produce identical per-type tables and identical admitted streams. **C3** the capture is deterministic across processes. **C4** the intervention changes only the order, checked per cycle and per type.

**What this does not decide.** No engine file changes, no D0 re-scoring, no V2 design, no acquisition cells, and Organica 1 stays frozen at `v0.9.0`. The brief is a plan and a pre-registration; the measurement has not been made. §72's counts — 16 arm-pairs, the same set in 11, the same order in 3, identical in set and order in 3 — are the record this plan starts from.

→ `docs/DIVERGENCE-MECHANISM-BRIEF.md`; `docs/divergence_cycle_capture.json`; `benchmarks/formation_utilization.py`; `organica/sleep.py`; `organica/memory.py`; journal §71; journal §72.

## §74 — The construction-order experiment ran, and its own control stopped it

**What this section records.** The experiment pre-registered in §73 and in `docs/DIVERGENCE-MECHANISM-BRIEF.md` was run on 2026-11-01 against the frozen engine at `711f04d`. Arm A observed every builder; Arm B canonicalised the construction order in the harness only. **No engine file was changed.** The artifact is `docs/divergence_mechanism.json`, the instrument `benchmarks/divergence_mechanism.py`, the report `docs/DIVERGENCE-MECHANISM-RESULTS.md`; 36 part files carry the raw per-cycle records and their checksums.

**Arm A answered a different question than the brief asked.** On **8 of 8** failing seeds the first builder whose assembled sequence differs between the two hash seeds is `_score_tags`, at **cycle 1** — and it is the same on the **control** seed. That is not a discovery about the divergence: `_score_tags` iterates `set(freqs) | set(cooc) | set(temporal)`, a set of strings, and then stable-sorts on `frequency`, an integer that ties constantly, so its position order is the hash seed's on the first cycle of every run. The instrument's first-difference rule therefore reports the *earliest order-sensitive site*, which is a property of the code, not the site at which the two sides part company.

**Correction (2026-11-01): the admitted streams first differ at the audit's cycle, and there is no offset.** On **8 of 8** seeds the harness's admitted prediction streams first differ at the engine cycle the membership audit names, not one after it. The report originally stated that they differ at the audit's `divergence.first_cycle` **+1** and explained the +1 as two conventions being one apart. **That explanation was wrong, and it is kept here rather than deleted.** *What was claimed:* a systematic one-cycle offset between the two instruments' numbering, attributed to the audit counting the cycle in which the stored table is read while this instrument counts `run()` calls from the first. *Why it was wrong:* there is no offset and no convention difference. `candidate_membership_audit.first_divergence()` sets `first_cycle = index` over `c_cycle_digests`, a **zero-based** list, while every cycle number these instruments report is one-based; both read the same `fu.run_arm` capture, so audit index 11 and engine cycle 12 are the same cycle. *How the correction was derived:* by reading the consumer against the producer, and then checking it independently — this instrument's `admitted_first_difference_cycle`, computed from its own one-based loop over fresh captures, equals the audit's index + 1 on 8 of 8 seeds, which is the base difference and nothing else. *What the deleted reading cost:* the field `admitted_same_at_divergence` was computed from `admitted[cycle - 1]` — the very cycle the audit **defines** as the divergence — so it was guaranteed true on every seed. **A metric that cannot be false is not evidence**, and it is now replaced by `audit_cycle_reproduced`, which can fail. *What remains:* the audit's recorded divergence cycle is **reproduced on 8 of 8 seeds by a second instrument on fresh captures**, which is **analytical reproduction, not independent experimental replication**; the eight builders' order-variable construction at cycle 1 is unchanged; the pool comparisons that were taken one cycle early are corrected in `docs/divergence_cycle_capture.json`. **No claim about a delay between construction order and admission survives this correction, in either direction**, and none may be derived from this design: the audit defines its divergence cycle as the first cycle whose admitted streams differ, so a second instrument finding them differing there confirms the recording and measures no interval.

**What the correction cost the experiment, stated plainly.** The correction did not just relabel a table. It removed the observation the mechanism experiment was pre-registered to explain. The experiment was designed to explain why two populations with the same candidates produced different admissions; at the cycle the admitted streams part company the candidates are not the same, so that question no longer has a subject. The site it located — `_score_tags`, order-sensitive from cycle 1 on every seed including the control — remains a real property of the code and remains the earliest such site the observer wraps, but it is now a fact about candidate **construction**, not about the divergence. The open question is narrower and has not been run: **at what earliest cycle do the two candidate populations first differ, and which operation introduces that difference?**

**Arm B was not admissible.** P3 was **not met** (0 of 8 seeds became hash-seed invariant) and F1 fired. **F2 fired too**: the canonicalisation changes the control seed's builder sequences at a fixed hash seed. By the pre-registration, F2 takes precedence — no conclusion may be drawn from Arm B — and Arm A explains why F1 had to fire: the brief's intervention canonicalises the **temporal graph** and the **composites**, while the first order channel is `_score_tags`, upstream of both and deliberately untouched. An intervention that starts downstream of the channel cannot remove it, so F1's firing is evidence about the **scope of the intervention**, not about H2.

**The controls.** C3 held: a part rewritten by a second process at the same hash seed is identical field for field. **C1 did not.** *Corrected 2026-11-01.* §74 originally reported C1 as held, because the control seed's *admitted stream* is identical at every cycle across hash seeds while its builder sequences differ. C1 as pre-registered required the control's **assembled lists** to be identical at every hash seed (§6 of the brief, via P2), and P2 is **not met**: the control's builders differ too, from the first cycle. The admitted-stream invariance is a real observation about a *different* quantity, read after the criterion had failed, and it is recorded as that and not as a held control. Keeping a control's name while changing its quantity re-scores a protocol after the fact (rule 14).

**What this does not decide.** H2 is **untested in an admissible form**. No D0 re-scoring, no V2, no acquisition cells, no engine change; Organica 1 stays frozen at `v0.9.0`. The next instrument needs an intervention at the **first** order-sensitive site — a total order on the tag scores or a canonical iteration order for the tag set — and a control that holds before its tables are read.

→ `docs/divergence_mechanism.json`; `docs/DIVERGENCE-MECHANISM-RESULTS.md`; `benchmarks/divergence_mechanism.py`; `docs/DIVERGENCE-MECHANISM-BRIEF.md`; journal §73.

## §75 — The onset question is pre-registered: when do the candidate populations first differ?

**What this section records.** A plan, committed before any run, for the next observer in the D0 reproduction line. The brief is `docs/ONSET-INSTRUMENT-BRIEF.md`; nothing in it has been run. **This section is the pre-registration**, and it is written before the instrument exists.

**Why the question changed.** §74's correction removed the observation the construction-order experiment was pre-registered to explain. At the divergence cycle the two sides do not hold the same set of candidates (0 of 16 arm-pairs), so the question *why do identical pools admit differently* no longer has a subject. What survives is narrower and is directly supported by the artifact in hand: **at what earliest cycle do the two candidate populations first differ, and what entered or left at that cycle?**

**What brackets it.** In `docs/divergence_cycle_capture.json` (`OBSERVER_VERSION` 3), 11 of 16 arm-pairs hold the same set at *k−1* and a different set at *k*, so for those the onset lies in **(k−1, k]**. Five arm-pairs already differ at *k−1* — T1/20261125 both arms (k=11), T2/20261120 both arms (k=5) and T2/20261121 arm B (k=5) — so for those the onset is at or before *k−1* and no existing measurement bounds it. Zero arm-pairs hold the same set at *k*.

**Amendment, 2026-11-01, before any run.** P1 as first written — that the eleven bracketed arm-pairs reach onset at exactly *k* — cannot fail: the bracket already fixes identical pools at *k−1* and different pools at *k*, and cycles are integers, so onset is *k* by arithmetic. It is a consistency check folded into F1, not a prediction, on the same principle that retired `admitted_same_at_divergence`. **P1 is withdrawn as a prediction and retained below as written; the predictions are P2 and P3.**

**Predictions, fixed in advance (as committed).** **P1** the 11 bracketed arm-pairs reach onset at exactly *k*. **P2** the five unbracketed arm-pairs reach onset strictly before *k−1*, and a specific cycle is located for at least 4 of the 5. **P3** more than half of the arm-pairs reach onset later than cycle 1.

**Falsification criteria.** **F1** if re-capturing cycles *k* and *k−1* does not reproduce the artifact's `set_identical` values on all 16 arm-pairs, the instrument is inadmissible and no onset may be reported from it. **F2** if the control seed's two hash-seed runs differ in membership at any cycle, the membership difference is generic to hash-seeded construction and carries no information about the D0 divergence. **F3** a window that fails its marker check is reported as **not measured**, never as a differing pool. **F4** if the onset cycle's transition record is empty while the sets are reported as differing, the finding is withdrawn rather than explained.

**Controls.** **C1** the control seed shows identical pools at every cycle and an onset of none. **C2** every window used carries the marker that addresses it, and the count of addressed windows equals the count used. **C3** the parts are written twice by independent processes and compared field by field. **C4** the cycles *k* and *k−1* pools equal the existing artifact's on IDs, not merely on counts.

**Reporting rules, fixed 2026-11-01 before any run.** The eleven bracketed arm-pairs are **witness cases**, not findings: their onset is arithmetic once the bracket holds, so they belong beside F1 as instrumentation validation, and a summary that cites "onset = k in 11 of 16" as a result repeats the defect this pass removed. For any search case that bottoms out at cycle 1 the admissible claim is **onset ≤ 1**, present from the first observable cycle, never "introduced at cycle 1" — there is no cycle 0 window, and claiming resolution the instrument does not possess is the error the indexing corrections were about. The five search cases carry the scientific content.

**What it will not establish.** It will not name the operation that introduces the difference. A candidate entering the pool at cycle *c* is evidence that an upstream write changed at *c*, not that a named function is responsible; locating the operation is a separate observer and is not attempted here. No engine change, no D0 re-scoring, no H2 test, and the mechanism experiment is not reopened. Organica 1 stays frozen at `v0.9.0`.

→ `docs/ONSET-INSTRUMENT-BRIEF.md`; `docs/divergence_cycle_capture.json`; journal §72; journal §74.

## §76 — The onset was measured: every pool divergence is an insertion, and the gauge that should have checked it cannot fire

**What this section records.** The experiment pre-registered in §75 and `docs/ONSET-INSTRUMENT-BRIEF.md` was run on 2026-11-01 against the frozen engine at `711f04d`: **18 worker runs, 0 cached**. Artifact `docs/divergence_onset.json`, report `docs/DIVERGENCE-ONSET.md`, instrument `benchmarks/divergence_onset.py`, which reuses the corrected capture's worker and its marker-witnessed addressing rule unchanged. **No engine file changed.**

**F1 passed.** Re-capturing cycles *k* and *k−1* reproduced `docs/divergence_cycle_capture.json`'s `set_identical` values **and its pool IDs** on **16 of 16 arm-pairs**. The onset instrument is therefore measuring the same thing the corrected capture measured, and the walk-back is licensed.

**C1 is void, and that is the most important defect in this run.** The audit records the control seed T1/20261101's campaign hash seed and baseline hash seed as **0 and 0** — the same seed. The two control runs are one configuration, so the comparison is a run against itself and cannot fail; it returned "identical pools in 24 of 24 measured cycles", which is what comparing a run with itself must return. **F2 is therefore not adjudicated**, and the onsets below are characterised, not yet shown to be specific to the failing seeds. This is AGENTS rule 25's defect — a check that cannot fire is decoration — caught by the run it was supposed to guard.

**P2, as pre-committed.** Of the **five** search arm-pairs, **four** reached onset strictly before *k−1*: T1/20261125 both arms at **cycle 3** (against *k* = 12), T2/20261120 both arms at **cycle 4** (against *k* = 6). The fifth — T2/20261121 arm B — reached onset at **cycle 5**, which *is* *k−1*, so it is located earlier than the divergence cycle but not strictly before *k−1*. The clause "at least 4 of 5 located" is met; the blanket "strictly before *k−1*" holds for 4 of 5. All five were located at a specific cycle.

**P3 met.** Every one of the 16 arm-pairs has its onset at cycles **3–6**; none bottoms out at cycle 1, so no claim depends on the unobservable cycle 0.

**The finding: divergence is insertion, never replacement.** Across the 16 arm-pairs with a located onset, **zero candidates left a pool** at the cycle it first differed. Every onset is the pool *gaining* candidates — 70, 47, 62 at the largest T1 transitions, 2–32 across T2 — and the two arms of a seed transition at the same cycle while differing in how many candidates enter (T2/20261118: arm B 20, arm C 2; T2/20261130: B 32, C 28). Members are not displaced by hash order; candidates are *admitted into* the pool that the other side never produced.

**What this does not establish.** It does not name the operation. A candidate entering at cycle *c* means an upstream write changed at *c*; the write's identity is a separate observer, and the fact that `_score_tags` is order-sensitive from cycle 1 is not evidence that it causes an insertion at cycle 3 or 4. With C1 void, the onsets are also not yet shown to be absent on a seed that does not diverge. H2 remains untested, D0 is not re-scored, and Organica 1 stays frozen at `v0.9.0`.

→ `docs/divergence_onset.json`; `docs/DIVERGENCE-ONSET.md`; `benchmarks/divergence_onset.py`; `docs/ONSET-INSTRUMENT-BRIEF.md`; journal §75.

## §77 — The distinct-seed control ran, F2 fired, and the onset result is inadmissible by its own pre-registration

**What ran.** `--control-only --control-seeds 0,1`: the control seed T1/20261101 captured at two hash seeds — **2 runs, 0 cached**. The pair was declared before the run because the audit's own control pair is hash seed 0 on both sides, which cannot fail.

**The result.** The control seed's pools **differ**. Of 24 measured cycles, **3 differ in membership** — all on **arm B**, at **cycles 10, 11 and 12** — and 4 differ in order. The other 21 are identical.

**F2 fires, and by the pre-registration the instrument is inadmissible.** F2 says: *if the control seed's two hash-seed runs differ in membership at any cycle, the membership difference is generic to hash-seeded construction and carries no information about the D0 divergence.* That is what happened. The onset numbers remain measured facts about these 16 arm-pairs, and the insertion observation remains a fact about pool construction — but neither may now be attributed to the divergence, because a seed that does not diverge also produces membership differences under two hash seeds.

**What is left, stated precisely and not more strongly.** The control differs at cycles **10–12 on one arm**; the failing seeds differ at cycles **3–6 on both arms**. That is a difference in *pattern*, and it is the only basis on which a further test could be built — as its own pre-registration with its own control, not as a reinterpretation of this run. **A result that has just failed its control cannot be rescued by noticing that the failure looks different in shape**; that observation is a hypothesis, and it is recorded as one.

**What this costs and what it does not change.** It costs the divergence-specific reading of the onset measurement, which was never secured. It does not change F1's reproduction, the insertion observation as a fact about pools, the withdrawn identical-pool premise, the mechanism experiment's status, H2's untested status, or the frozen engine. **No engine file changed. D0 is not re-scored.**

→ `docs/divergence_onset.json`; `docs/DIVERGENCE-ONSET.md`; journal §76; `docs/ONSET-INSTRUMENT-BRIEF.md`.

## §78 — Freeze point: the divergence line stops on a record that was narrowed four times

**The decision.** The owner called the freeze point on **2026-11-01**, after the fourth correction in this line. Nothing further is read out of the existing artifacts. The next question is a new instrument and a new observation target, not another reinterpretation of measurements already in hand.

**What the four corrections had in common.** Identical pools at divergence (withdrawn); the one-cycle lag (withdrawn); the divergence-specific reading of the onset measurement (inadmissible, F2 fired); and C1 as a passed mechanism control (failed as pre-registered, P2 not met, and reported as held by substituting a different quantity). **None of them was a failed replication.** In every case the artifact already carried the narrower fact, and the wider claim was added on top of it — rule 24's defect, at the headline. That the same failure recurred four times is a property of how the record was being written, not of the measurements, and it is the reason the surviving claims are worth something.

**What stands, at its scope.** The development audit and its reconstructions (evidence, selection, surviving lineage, revision); path dependence and the stable revision regimes; candidate populations diverge under hash-seeded variation, and those cycles are analytically reproducible (F1 16/16); pool divergence appears as insertion rather than replacement; `_score_tags` is the earliest hash-sensitive builder **observed by the current instrumentation**, including on the control seed (`criteria/P2/per_type/B/score_tags: false`, and `criteria/F2/per_type_unchanged/B/score_tags: true` for the intervention). The admitted-stream invariance on the control seed is an observation on **one seed at hash seeds 0 and 2**, recorded post hoc, not a passed control.

**What the record no longer says.** Identical pools at divergence; a one-cycle lag; a systematic offset; an inside-the-cycle account of divergence; a divergence-specific reading of the onset measurements. Those five are **withdrawn claims**. **C1 as a passed control** is not one of them: it is a fourth category, a pre-registered criterion evaluated once and not met, and it sits beside the observations rather than among the retractions (§79).

**The next question, and why it is a different kind of question.** Which upstream write admits candidate tags at cycles 3–6? Answering it requires an observer that does not yet exist: one that names the **store-time write**, rather than the earliest builder that consumes its ordering. `_score_tags` is the earliest hash-sensitive builder the instrumentation can see, and whether it is **causal or merely earliest-visible** is explicitly open. No existing artifact can settle it, which is exactly the condition for a freeze rather than another reading.

**Vocabulary, per rule 26.** Nothing withdrawn here is *refuted*. Those items are **not established**, which is a weaker and different statement; C1 is **failed as pre-registered**, which says the control did not meet its own criterion and says nothing about whether the admitted stream is invariant — it is.

No run was made in this turn. No measurement changed.

## §79 — The claim map at the freeze point, and the limit the observer must keep

**The map, in three buckets plus one.** Supplied by the owner on 2026-11-01 after the C1 correction, and checked here against the artifacts rather than accepted.

*Supported within scope.* Development; path dependence; revision; stable revision regimes; the four audit reconstructions (evidence, selection, surviving lineage, revision); candidate populations diverge under hash-seeded variation; those cycles are analytically reproduced (F1 16/16); pool divergence appears as insertion rather than replacement; `_score_tags` is the earliest hash-sensitive builder **observed by the current instrumentation**, including on the control seed (`criteria/P2/per_type/B/score_tags: false`, with `criteria/F2/per_type_unchanged/B/score_tags: true`); admitted-stream invariance on **one control seed at hash seeds 0 and 2**.

*Not established.* That `_score_tags` is causal; the divergence-specific interpretation of the pool-onset measurements; H2; the early/both-arm versus late/single-arm pattern as an explanatory mechanism; any timing claim about when the causal write occurs.

*Withdrawn.* Identical pools at divergence; the one-cycle lag; a systematic offset; the inside-the-cycle divergence premise.

**A fourth bucket, kept separate from the third.** The owner's first map filed C1 under *withdrawn*; it was moved out on 2026-11-01 and the owner has since adopted this four-bucket form. *Withdrawn* means a claim was made and the evidence stopped supporting it, while C1 is a **control verdict** — the criterion was evaluated once by the committed code and was not met (`P2.met: false`), and a control's failure says nothing about the organism. The record therefore keeps *failed as pre-registered* as its own bucket, which is the only arrangement in which both statements below can be made plainly.

**The separation that must not be collapsed again.**

- The **control failed**: C1 required the control seed's assembled lists to be identical at every hash seed; P2 is not met; the control's builders differ from cycle 1.
- The **observation survives**: the control seed's admitted stream is identical at every cycle across hash seeds 0 and 2 (`P2.admitted_stream_identical: true`).

Both are artifact facts, they concern different quantities, and they are now separate sentences in `docs/DIVERGENCE-MECHANISM-RESULTS.md` §6, journal §74 and manual finding 44. The observation is supported **within scope** — one seed, one hash-seed pair, read post hoc — and it is not evidence that the control passed.

**Earliest observed is not earliest causal.** The capture observer wraps `MemoryService.recent` (the sleep-window read) and `fu.run_arm` (the arm runner); the mechanism instrument records the builders' own sequences. What this sees is therefore: the rows a cycle's window returned, the candidate sets derived from them, the builders' outputs, and the admitted stream. What it does not see: how the store ordered those rows before returning them, how the sets feeding `_score_tags` were assembled upstream, and **which write admitted a tag into the store in the first place**. `_score_tags` being the earliest hash-sensitive builder in every artifact the project has is a statement about the instrument's reach; it cannot be promoted to where the divergence originates, and this section is where that promotion is refused.

**What the next instrument's success condition is.** Not *"`_score_tags` caused it"* — that would repeat the defect this line has spent four corrections removing, one level down. It is: **"`_score_tags` did not cause it"**, stated by a store-time observer that can name the admitting write or name a different one. An instrument that can only confirm the earliest builder it is already built to see measures its own construction.

**The result space the next observer must be able to reach.** An observer that can only ever rediscover `_score_tags` is not testing a hypothesis; it is tracing its own field of view. The design requirement is therefore that **all three outcomes be reachable and distinguishable**: **(A)** an upstream write *before* `_score_tags`; **(B)** `_score_tags` itself; **(C)** no identifiable write. If only (B) is reachable, the instrument is not discriminating, and that is a failure at design time rather than at readout, which is the only point at which it can still be fixed cheaply. `_score_tags` has survived every round so far partly because every instrument has been positioned where `_score_tags` is visible.

**Amendment, same day.** This section first reproduced the map with C1 under *withdrawn*, and §78 listed it among the retractions. The owner adopted the four-bucket form above on 2026-11-01, so C1 now sits only under *failed as pre-registered*, and the result-space requirement is added. No measurement is affected and no artifact changed.

**What makes outcome (C) admissible, stated before the observer exists.** *"No identifiable write"* can otherwise mean two opposite things - **every write was observed and none explains the insertion**, or **the observer never saw the causal write** - and those are not nearby conclusions: one is a result, the other is a broken instrument. The pre-registration must turn the difference into fields, not an inference: record `observed_writes`, `reconciled_writes` (against what the store actually accepted) and `explaining_write`. **(C) is admissible only when `observed_writes == reconciled_writes` and `explaining_write` is none.** Where the denominator does not reconcile, the verdict is **indeterminate** - reported as indeterminate, never folded into (C), because an unmeasurable quantity reported as a zero is the fabrication rule 13(b) names. Without this, (C) is an absorbing bucket: it will eventually absorb an instrument failure and read as a finding.

**Naming caution, before it ships.** The two readings must **not** be labelled (C1) and (C2). This line already uses **C1**, **C2** and **C3** for the mechanism brief's three controls (the control seed, the observer's behaviour-neutrality, and determinism), so both proposed labels would have collided, not just one; a third C1 in the same documents would be the defect rule 8 describes, a name a reader takes literally that means something else. Use words - *C-accounted* and *C-unaccounted* - so the distinction survives being quoted without its surrounding paragraph.

No run was made in this turn and nothing here is a new measurement.

## §80 — The store-time observer's core is built, and its neutrality control passed

**What was built.** `benchmarks/store_time_observer.py` wraps `MemoryService.store`
in process (no engine file touched, restored in `finally`), records every admitting
call with the cycle it belongs to, its **stage** (ingest or cycle construction), a
digest of the content and whether the store accepted a row, and reconciles observed
calls against accepted rows per cycle. Planned in
`docs/STORE-TIME-OBSERVER-BRIEF.md`; the plan is unchanged.

**Two defects were caught before any verdict could be read, and both are the same
family the line has been correcting.**

- **Cycle attribution.** The first draft used the number of sleep-window reads as
  the cycle number and reported **162 cycles for a six-cycle run**: a window read
  is not a cycle. Attribution now comes off the engine's own `sleep:meta` marker,
  which carries the cycle number and is written before that cycle's candidates, and
  a construction write with no marker before it is reported **unattributed** rather
  than given a guessed number. On the control run: **349,502 writes**, every
  one attributed, **1,280 ingest writes** in **160**
  pre-cycle buckets of **8** each.
- **A reconciliation rule that could not fire.** The first rule compared the net
  delta against the accepted rows. A call that stored nothing contributes zero to
  both sides, so a silently empty write *reconciled*: a unit test in
  `tests/test_store_time_observer.py` caught it. The rule now requires
  `net == accepted == observed` per cycle, and it holds on the real run —
  **349,502 accepted** against **349,502 observed**, no
  removals.

**What passed.** Neutrality is **identical** on the admitted stream and the temporal
reads with and without the wrapper (127.8 s for the pair); the
comparator is proved to fire on an injected difference; the markers are contiguous
from cycle 1 to **160**; and every cycle reconciles. Full record:
`docs/store_time_observer_self_test.json`.

**What this is not.** It is **not** a result about divergence, and no verdict has
been read. The verdict pass (attribution of a pool difference to a named write) and
the **known-positive control (C1 / F4)** — the control seed's own cycles 10–12 —
are **not built**. Until F4 passes, the brief's rule stands: the observer is
inadmissible for verdicts, and the freeze on the divergence findings is untouched.

**Method note, since this is the first stage-4 correction in the line.** Both defects
above were found with **no artifact and no measurement affected**: the cycle error by
noticing that a six-cycle run reported 162 cycles, and the reconciliation rule by a
unit test written before the control was run. That is the cost difference the freeze
point predicted, observed rather than asserted.

**Amendment, same day: the per-call record is kept, not just summarised.** The run's
database is disposable, so a summarised record loses exactly the detail a later
question would need. `--trace` now writes every admitting call to
`docs/store_time_observer_trace.jsonl.gz` — **349,502 calls**, gzip JSONL, **1.12 MB**, with
**48,672 distinct content digests** factored into a header table so each
row is five fields: cycle, accepted, digest index, stage, source. `load_trace()` in
the observer reads it back with the digests resolved. The trace corresponds to
`docs/store_time_observer_self_test.json`, which records the same run.

## §81 — The known-positive control passes: the observer explains the control seed's own difference

**What ran.** `--known-positive`: the control seed T1/20261101, arm B, at hash seeds
**0 and 1**, capturing the read-back window at engine cycles **10, 11 and 12** and
every write to the store in the same runs. **2 runs, 0 cached**, 93.3 s in
parallel. Artifact: `docs/store_time_observer_f4.json`.

**Addressing is witnessed, not assumed.** The windows carry their own markers: hs0 and
hs1 both report markers **10, 11, 12** at reads 10, 11
and 12, over 162 sleeps reads each.

**The result.** All three cycles differ, with the pool sizes equal on each side:
10 (230/230), 11 (250/250), 12 (283/283). The differences are **10: 4, 11: 4, 12: 4** candidates respectively — an equal number each
way, which is what an insertion-plus-removal pair looks like from the pool's side.

**Every difference is attributed.** 12 candidate-writes across the
three cycles were found in the offering side's write record at that cycle and **absent
from the other side's**, with stage **construction** and type **dream**.
So on this known-positive case the observer names the write, and the answer is a
**construction write**, not an earlier ingest write — outcome **(B)** in the brief's
result space.

**What this does and does not mean.** It means the observer can resolve a membership
difference the record already contains, which is what C1 / F4 was for: without it an
"indeterminate" or "no write explains it" verdict would be uninterpretable. It is
**not** a result about D0: this is the control seed's own hash-seed difference at
cycles 10–12, and the failing seeds' divergence is untouched. The verdict pass over
those seeds is **not built**, and no divergence verdict has been read.

**The control earned its keep before it passed.** The first F4 attempt returned
`not_measured` on every cycle: the window index was incremented **before** the read, so
every window sat one read off its own marker and was refused. A control that could not
fire would have let the verdict pass run against an instrument that never addressed a
cycle. This is the second time in this build that an off-by-one at the observation
boundary was caught by a check rather than by a result.

**Amendment, same day: F4 is now gated on reconciliation as well as attribution.**
The first decision was taken on attribution alone, which is the defect this line
keeps removing: a cycle whose write counts do not reconcile cannot tell "no write
explains it" from "the observer missed the write", so attribution from such a cycle
is uninterpretable. `f4_decision()` now requires both, in order — every affected
cycle reconciles on both sides, then at least one difference is traced to a named
write. Re-run under that rule the control still **passes**: all three cycles
reconcile, all twelve differences remain attributed, outcome (B). The stronger rule
did not change the verdict, which is what makes it usable. The frozen record is
`docs/F4-RESULTS.md`.

**Correction, same day: the control's outcome is (B) *unlocalized*, not (B).** I
first wrote outcome (B), which in the brief means *the `_score_tags` write was
identified*. The observer's stage split is binary — ingest vs construction — so it
establishes that the differing candidate is written by the cycle's own
construction rather than by ingest, and it does **not** separate `_score_tags`
from the rest of `_store_candidates`. That is enough for a control (can it see the
thing?) and not enough for a verdict label on a failing seed. If the measurement
needs (B) proper, the stage split has to reach inside construction first — which
is a build change, to be pre-registered before it is run, not a reading of this
result. `docs/F4-RESULTS.md` §7 carries the correction; §4's PASS stands.

## §82 — F5 passes the finer split, and (B) is restated because it named a write that does not exist

**The defect was in the bucket, not the instrument.** Bucket **(B)** of the
observer brief is *"the `_score_tags` write is identified"*. Reading the frozen
engine to build the split settled it: `_score_tags` makes **no store call**
(`organica/sleep.py:904-922`) — it builds `_TagScore` records, sorts them on
`frequency`, returns the list. There is no such write on any seed, in any cycle.
An observer reporting (B) would be reporting a write that does not exist, and the
brief had been carrying an unsatisfiable bucket since it was written.

**The restatement, pre-registered before the run** (`docs/STORE-TIME-OBSERVER-BRIEF.md`
§9, committed first): (B) becomes *a write emitted by one of the two builders that
consume this cycle's tag scores*, `_build_concepts` or `_build_phrases`. Those are
the only construction steps taking `tag_scores` as an argument. The restatement is
narrower than "construction" and it is not a causal claim: both builders also
consume the graphs, so it locates the write and says nothing about which input
made the difference.

**The split.** Two engine-derived axes per write: **phase** — whether the call
passed through `_store_candidates` (a cycle-pool write) or outside it (a survivor
re-store during natural selection, `sleep.py:453-460`) — and **type**, from the
`sleep:<ctype>` source the engine already stamps. Phase is read from the frame
stack at the wrapped call, never from a counter, and it is needed because natural
selection re-stores survivors through the same per-type writer: type alone cannot
separate a candidate built this cycle from one carried over.

**F5, and its result.** Neutrality was re-proven with the frame walk installed
(C2 re-run: `admitted` and `temporal_reads` identical to the unobserved run,
**349,502** accepted calls, 0 unreconciled cycles, 136.5 s). The control run then
reported **17** distinct labels across both hash seeds, and all **12** attributed
candidates carry **`pool:dream`**. Conditions 1-3 hold, so **F5 passes**, and F4
still passes.

**The prediction was recorded and it held.** §9 predicted `pool:dream` because
`_generate_categorized_dreams` consumes workflows, processes, meta_concepts,
questions and the two graphs — **not** tag scores. `prediction_met: true`. So on
the control seed **outcome (B-restated) is not reached**: the differing candidate
is construction at Layer 6 and carries no tag-score dependence.

**The gate fired first on my own wiring, and that is the reason to trust it.** The
first F5 run returned `failed: 12 attributed candidate(s) carry no label` — the
label existed in the per-candidate record but the attributed entry carried only
`stage`. Had the gate passed when labels were missing, this run would have
produced a fine-looking table of `(B-restated): no` for the wrong reason.

**What this does not establish.** Nothing about D0. One seed, one hash-seed pair,
one differing type; a differing candidate on a failing seed may be tag-scored, and
the control's answer does not constrain it. What is established is an instrument
property: the observer can name the builder behind a differing candidate, and
(B-restated) is a reachable bucket rather than an unreachable name.

→ `docs/F4-RESULTS.md` §7-§8; `docs/STORE-TIME-OBSERVER-BRIEF.md` §9;
`docs/store_time_observer_f4.json`; `benchmarks/store_time_observer.py` (version 2).

## §83 — The verdict pass ran, and the answer is not `_score_tags`

**Two passes, and why.** The pre-registered pass (§10) ran at hash seeds 0 and 1
and returned `no_difference_at_pair` on **all five** cells — the windows were
addressed and identical (268/268, 98/98, 82/82). That is an input error, not a
result: `docs/candidate_membership_audit.json` records the pair each seed was
measured at, and I had taken 0/1 by analogy with F4/F5 instead of reading it. The
correction is pre-registered in brief §11 and the null-pair artifacts are kept
unchanged. **The divergence is pair-specific**, which is itself a fact worth
having: at 0/1 these five cells have identical candidate populations.

**The corrected pass** ran the same five cells at the recorded pairs (0/2, 0/13,
0/2). Artifacts: `docs/store_time_observer_verdicts_pairs.json`,
`docs/STORE-TIME-OBSERVER-VERDICTS-PAIRS.md`.

| Cell | Pair | Cycle | Diff/attributed | Labels | Reconciled | Outcome |
|---|---|---|---|---|---|---|
T1 / 20261125 / B | 0/2 | 12 | 27/27 | `pool:anomaly`, `pool:dream`, `pool:experiment`, `pool:hypothesis`, `pool:investigation`, `pool:loop_candidate`, `pool:prediction_candidate`, `pool:question`, `pool:theory` | yes | construction_other:pool:anomaly+pool:dream+pool:experiment+pool:hypothesis+pool:investigation+pool:loop_candidate+pool:prediction_candidate+pool:question+pool:theory
T1 / 20261125 / C | 0/2 | 12 | 27/27 | `pool:anomaly`, `pool:dream`, `pool:experiment`, `pool:hypothesis`, `pool:investigation`, `pool:loop_candidate`, `pool:prediction_candidate`, `pool:question`, `pool:theory` | yes | construction_other:pool:anomaly+pool:dream+pool:experiment+pool:hypothesis+pool:investigation+pool:loop_candidate+pool:prediction_candidate+pool:question+pool:theory
T2 / 20261120 / B | 0/13 | 6 | 14/8 | `pool:anomaly`, `pool:dream`, `pool:experiment`, `pool:investigation`, `pool:prediction_candidate`, `restore:loop_candidate` | yes | indeterminate
T2 / 20261120 / C | 0/13 | 6 | 14/8 | `pool:anomaly`, `pool:dream`, `pool:experiment`, `pool:investigation`, `pool:prediction_candidate`, `restore:loop_candidate` | yes | indeterminate
T2 / 20261121 / B | 0/2 | 6 | 6/6 | `pool:anomaly`, `pool:dream`, `pool:prediction_candidate` | yes | construction_other:pool:anomaly+pool:dream+pool:prediction_candidate

**What it found.** Every reconciling cell that could be resolved attributed **all**
of its differences to a write: 88 differences across the cells, 76 attributed, with
no cell landing in `C_accounted`. The labels are construction writers —
`pool:anomaly`, `pool:dream`, `pool:experiment`, `pool:hypothesis`, `pool:investigation`, `pool:loop_candidate`, `pool:prediction_candidate`, `pool:question`, `pool:theory`, `restore:loop_candidate` — and **not one of them is tag-scored**: `pool:concept_candidate` and
`pool:phrase_candidate` appear in **no** cell's attributed set. On these three
seeds, at the cycles where their populations part company, **(B-restated) is not
reached**. The writes that differ are the higher-layer builders (predictions,
anomalies, loops, hypotheses, dreams, investigations, experiments) plus the
question and theory writers.

**The cell that did not resolve, and it is reported as such.** T2/20261120 at
0/13 has **14** differences and only **8** attributed, with its writes fully
reconciling. By the pre-registration that is **`indeterminate`**, not "mostly
explained" and not `C_accounted`. Its labels include `restore:loop_candidate` —
the first measured instance of a **survivor re-store** offered on one side only,
which is exactly the case the phase axis was built to separate from a cycle-pool
write. That single label is the reason to keep the two-axis split.

**Arm C is not independent evidence.** The C cells reproduce the B cells exactly
(268/271 and 27/27; 98/98 and 8/14), which is expected rather than reassuring: arm
C reads arm B's per-cycle temporal graphs and filters on the support set, so where
B's writes differ, C inherits the difference. The agreement confirms the write
record is consistent across the staged run; it says nothing extra about C's filter.

**What this does not establish.** That `_score_tags` is or is not causal. It does
not appear as a write in any resolved cell — because it writes nothing at all —
and the builders that do differ consume graphs and prior structures as well as, or
instead of, tag scores. **H2 remains untested**; D0 is not re-scored; Organica 1
stays frozen at `v0.9.0`. The measurement is one cycle per cell, three seeds, one
hash-seed pair each, and a window comparison — not the admitted stream, whose
counts differ from the window's by construction.

**The instrument's own record.** Both controls passed before this ran (§78-§82),
the first pass's failure was diagnosed as an input error within the hour, and the
one cell that could not be resolved was left `indeterminate`. That is the shape the
brief asked for, including the part where the answer is not the one the mechanism
line was built to look for.

→ `docs/STORE-TIME-OBSERVER-VERDICTS-PAIRS.md`; journal §82; brief §10-§11.

## §84 — The six unattributed differences were written one cycle before the window opened

**A post-hoc diagnostic, and it is not a verdict.** T2/20261120 at hash seeds 0/13
resolved 8 of its 14 differences and was left `indeterminate` (§83). This section
asks one question about the other six: were they written earlier in the run, after
the cycle, or never written at all? Artifact:
`docs/store_time_observer_lineage.json`; instrument:
`benchmarks/store_time_observer.py --lineage`. **The cell remains
`indeterminate`.** Nothing here converts it, and nothing here is causal.

**The answer, and it is uniform.** All **6** unattributed candidates were written
at cycle **4**, exactly one write each, on the side whose pool holds them, and
**never on the other side at any cycle of the run**. The pre-registered search
window is the divergence cycle and the one before it — cycles **6 and 5** — so
their write sits **one cycle before the window opens** (its earliest searched
cycle is 5) and **two cycles before the divergence itself** at cycle 6.

**The contrast inside the same cell, read from the artifact.** What separates the six is not
their first write — three attributed candidates are *also* first written at cycle 4 — but
whether the candidate is written **again** inside the window. All six unresolved candidates
have exactly **one** write, at cycle 4, and are never written again in the run. The three
cycle-4 candidates that *did* resolve were written two or three times, reaching cycles 5 or 6.
Of the remaining five attributed: exactly **one** first appears at cycle **5** (the window's
outer edge) and **four** are re-stored on more than a hundred cycles (155, 155, 156, 213), so their records
exist on both sides; the other starts at cycle 6.

**Correction, same day, against the artifact.** This section first said the writes lay two
cycles outside the window, that two attributed candidates first appear at cycle 5 and that
six are re-stored every cycle. The artifact says one cycle before the window, one candidate,
and four. Every figure above is read from `docs/store_time_observer_lineage.json`; the
reading is unchanged — a candidate written once, before the window, and never again, is
invisible to a two-cycle search.

**What this changes.** Not the cell's outcome — `indeterminate` is what the
pre-registration says for a partial explanation, and re-reading it as "explained by
an earlier write" would be re-scoring a protocol after seeing the result (rule 14).
What it changes is the **diagnosis of the limitation**: this is not an observer that
could not see the write. It is a search window narrower than the lead time between
a candidate being stored and the pool diverging. A wide-window rule would have to be
pre-registered and applied to **all** cells, not just this one, and it is not run
here.

**What this does not establish.** Anything about mechanism, H2, or D0. It is a
statement about where in the write record six candidates appear, on one seed, at one
pair, at one cycle.

→ `docs/store_time_observer_lineage.json`; journal §83; brief §10-§11.

## §85 — The mechanism plan re-run: Arm A is unchanged, and Arm B-prime passes its first gate

**Correction, same day: this section's gate-1 result is void.** `canonical_score`
was never implemented at `e2206e5` — the mode was an argparse choice with no code
behind it, so the "0 differences in 168 comparisons" below compared `observe` against
`observe`. The paragraph that follows calling my advance prediction wrong is itself
wrong: with the intervention actually applied, **F2 fires, 125 of 168 comparisons**, as
§11 predicted. See §87 and `docs/divergence_arm_b_prime_AUDIT.md`. The text below is
kept as written rather than deleted, because it is the record of what I concluded from
an instrument that was not running.

**Arm A, across its planned cases, adds nothing new — and that is the result.** The
eight failing seeds and the control at their recorded pairs are all cached from
§74: the sweep reported **0 runs, 18 cached**. Its finding therefore stands
unamended — `_score_tags` is the earliest order-sensitive builder on 8 of 8 failing
seeds *and on the control*, from cycle 1 — and §74's reading of it stands with it:
that is a property of candidate construction, not evidence about where the
divergence begins. Re-running the arm would not have changed that, so it was not
re-run.

**Arm B-prime, pre-registered in brief §11 before it ran.** Arm B canonicalised the
temporal graph and the composites, both *downstream* of `_score_tags`, which is why
§74 could not attribute anything to it. B-prime extends the same harness-side
intervention to the site Arm A located: in canonical modes the tag scores get a
total order (`(-frequency, tag)`). Gate 1 is F2 — the control seed's per-type table
must be unchanged at a **fixed** hash seed — and it runs **before any failing seed
is measured**, because an intervention that moves the control is the classic way to
manufacture a confirmation.

**Gate 1's result.** Control seed T1/20261101, hash seed 0, `observe` against
`canonical_score`, 168 comparisons over arms B and C, cycles 1-12: **0
differences** (none), the first in arm B at none. **F2 does not fire.**

**Gate 1 passes, and the conflict I predicted did not occur.** §11 recorded in
advance that F2 would probably fire, on the reasoning that the control's builders
are not hash-seed invariant (P2 failed as pre-registered, §74/§79) so a
canonicalising intervention must move its order. **That prediction was wrong, and it
is recorded as wrong rather than deleted.** At hash seed 0 the control's recorded
tables are identical across all 168 comparisons, `score_tags` included: the engine's
own order there already coincides with the total order `(-frequency, tag)`.

**What that does and does not license.** F2 does not fire, so Arm B-prime is
admissible at gate 1 and the plan proceeds to C2 and C3 before any failing seed is
measured. It does **not** license anything about H2: one control seed, one hash seed,
cycles 1-12, and an intervention that happened to be a no-op there. The lesson is in
the prediction, not the gate — the control's hash-seed dependence is a statement
about *two seeds compared*, and it does not tell you what an intervention does at
*one* seed, which is why deriving the second from the first was a mistake.

**Unchanged.** The T2/20261120 cell stays `indeterminate`; the window is not widened;
D0 is not re-scored; Organica 1 stays frozen at `v0.9.0`.

→ `docs/divergence_arm_b_prime_f2.json`; `docs/DIVERGENCE-MECHANISM-BRIEF.md` §11;
journal §74, §79.

**Gates 2 and 3, appended the same day.** **C2** — observer neutrality: a `quiet` run
and an `observe` run at the same hash seed produce identical admitted streams on both
arms. **C3** — determinism: a repeat `observe` run at hash seed 0 is identical in the
recorded tables and in the admitted streams. No part was refused by the addressing
rule in any of the four runs. With F2, that is all three pre-gates passed, so gate 4 —
the eight failing seeds at their recorded pairs, under the intervention — is what the
plan calls for next. Artifact: `docs/divergence_arm_b_prime_gates.json`.

**What three passing pre-gates still do not establish.** That H2 holds. They establish
that the intervention is admissible to be tested: it does not move the control at a
fixed hash seed, it does not change behaviour when merely observed, and it is
deterministic. P3 is answered by gate 4 or not at all.

## §86 — Arm B-prime across the eight seeds: F1 fires

**Correction, same day: this section's result is void.** It measured the unimplemented
mode, so "F1 fires" is an observe-against-observe comparison that reproduces Arm A's
signature exactly. With the intervention implemented, gate 4 returns **8 of 8 seeds
invariant, 0 differences — P3 holds and F1 does not fire** — and the control gate F2
fires, so under §11's pre-recorded stop rule **no conclusion may be drawn from the
arm**. Both readings are in §87; neither is a verdict about H2.

**The order channel, canonicalised at all three sites, is not sufficient.** At
least one failing seed still records tables that differ across its own hash-seed
pair: **0 of 8 seeds invariant**, so **F1 fires and H2 is refuted in its strong
form**.

**Where it still varies.** T1/20261125 still differs at 90 cycles ({'arm': 'B', 'cycle': 1, 'membership_same': True, 'type': 'score_tags'}). The seeds that still differ, and by how much, are in
`docs/divergence_arm_b_prime_sweep.json`; the largest is listed first. Under the
brief's stop rule this closes the order channel rather than inviting a re-tuned
intervention, and the search moves on.

**What F1 firing does not say.** That order is irrelevant — the control and the
record's earlier reproduction results stand — only that canonicalising these three
sites does not remove the variation. It does not re-score D0 and does not touch
V1's deficits.

→ `docs/divergence_arm_b_prime_sweep.json`; journal §74, §79, §85.

**An open anomaly, appended before this section is relied on.** Every seed's first
difference sits at **cycle 1**, in `score_tags`, with **identical membership** — which
is Arm A's signature, not what a total order on tag scores should produce. Inspecting
one seed's cycle-1 record makes the anomaly concrete: T1/20261125 records
`... indigo, fern, cedar` at hash seed 0 and `... indigo, cedar, fern` at hash seed 2,
diverging first at position **5**.

Under the intervention's own key, `(-frequency, tag)`, those two orders can only
differ if the two sides' **frequency values differ**: equal frequencies are broken
alphabetically, and `cedar` precedes `fern` in that order. If that is what the parts
show, then at cycle 1 the divergence enters in the **counts the tags are scored on**,
not in the order they are iterated — a different quantity from the one this arm was
built to move — and F1's firing would be a statement that the intervention addresses
the wrong quantity rather than a refutation of the order channel.

**The check that settles it has not been run.** It is one comparison — the two sides'
`frequency` for those tags at cycle 1 — and it is the next thing to do. Until it is,
F1 stands as *fired by the pre-registered code* and is **not** read as closing the
order channel. This paragraph exists because the alternative was to let a
suspicious-looking result become a conclusion by being written down first.

→ `.scratch/divergence_mechanism_parts/canonical_score_T1_20261125_hs{0,2}.json`
(regenerable); `docs/divergence_arm_b_prime_sweep.json`.

## §87 — Implementation-to-artifact audit: the arm that was a label

**The finding.** Arm B-prime's mode `canonical_score` existed only as an argparse
choice. `CANONICAL_MODES` did not appear in the file at all; `_load_temporal` gated
the graph on `self.MODE == "canonical"`; `_compose_meta_concepts` gated on
`self.MODE != "canonical"`; and `_score_tags` recorded `[s.tag for s in out]` from
`super()` and returned it untouched, with no sort by `(-frequency, tag)` anywhere on
the path. The mode was therefore **behaviourally identical to `observe`**, and every
generation-1 artifact inherited a label with no mechanism behind it: F2's 0 of 168,
C2's and C3's passes, and gate 4's "F1 fires".

**How it was caught, and by what.** Not by a gate — by reading a result that looked
wrong for a reason. Every seed's first difference sat at cycle 1 in `score_tags` with
identical membership, which is Arm A's signature; and one seed's sides ordered
`fern`/`cedar` differently, which under the intervention's own key required the
*frequencies* to differ. The frequency check showed they do not: `cedar = 1` and
`fern = 1` on both sides, and the documented order collapses the two lists. So the
differences were hash order among tied scores, and the intervention that was supposed
to break those ties was not running.

**The correction to my own correction.** §85 as committed on the day declared my §11
prediction wrong, on the strength of the 0-of-168 gate. That reading was itself
produced by the broken instrument, and it is the more embarrassing of the two errors:
I explained a null result by my own reasoning rather than by checking whether the
intervention had executed. The lesson is the one this record keeps relearning — **a
measurement that contradicts a prediction is a reason to audit the instrument before
rewriting the prediction.**

**What now runs, and the telemetry that proves it.** `CANONICAL_MODES` exists and both
canonical branches test membership; `_score_tags` sorts the engine's returned value by
`(-frequency, tag)` *before* recording; every score record carries `score_intervention`
with `total_order_applied`, `graph_canonical` and `adjacent_ties`; and
`ORGANICA_NO_RECORD=1` disables recording so C2 can compare the same build with the
trace on and off. Measured: `total_order_applied` true in every record, **153**
adjacent ties broken on the control and **203** on the sweep seeds — the
intervention has work to do, and it did it.

**Generation 2.** C2 neutral on both arms; C3 deterministic; **F2 fires, 125
of 168 comparisons**; gate 4 returns **8 of 8 seeds
invariant, 0 differences — P3 holds, F1 does not fire.**

**Why that is not a result about H2.** §11 pre-registered the stop rule and the
conflict in the same section: F2 requires the control's table unchanged at a fixed
hash seed; the control's order is itself hash-seed dependent (P2 failed as
pre-registered, §74/§79); so a real canonicalisation must move it, and F2 and P2
cannot both hold. **They cannot both hold, and F2 is the one that fired.** Under the
gate as written, the arm is inadmissible by its own control and no conclusion may be
drawn from it — including, importantly, **no conclusion against H2**.

**What the numbers look like, stated as fact and not as a softened verdict.** Of the
125 control differences, 79 are order-only and 46 change membership;
by type (order-only / membership-changing): `loops` 0/22, `meta` 0/22, `anomalies`
14/2, `predictions` 19/0, `score_tags` 22/0, `temporal_read` 24/0, `concepts` 0/0.
A membership-restated F2 would therefore return a **different** gate result, which is
exactly why restating it now is the owner's decision and not mine — doing it after
seeing that P3 holds would be choosing a criterion after seeing the data.

**Decision open (owner).** Restate F2 in membership terms, or abandon Arm B-prime.
Until one is chosen, the arm stays inadmissible, `T2/20261120` stays `indeterminate`,
the window stays unwidened, and D0 stays unscored.

**The repository-level lesson.** The defect was not a wrong number; it was a
**name** — a mode, a docstring and an artifact label that all described an
intervention nobody had written. A record cannot catch that by being careful. It
catches it by requiring every artifact to carry telemetry of its own mechanism, which
is now what `score_intervention` does at this site, and by treating a
prediction-contradicting null as a prompt to audit the instrument first.

→ `docs/divergence_arm_b_prime_AUDIT.md`; `docs/divergence_arm_b_prime_{f2,gates,sweep}_v2.json`;
`benchmarks/divergence_mechanism.py`.

## §88 — Arm B-prime closed by decision, and the record it leaves

**Closed, not resolved.** The owner closed the arm as inadmissible under §11's
pre-registered stop rule. F2 is **not** restated and the arm is **not** run again. The
tempting move — rewrite the gate in membership terms now that 125 of
168 control comparisons are known to split 79 order-only to 46
membership-changing, and now that the sweep returned 8 of 8 invariant —
is refused, because a gate chosen after the data is not a gate.

**What is kept, and in what category.** The 8-of-8 invariance is
recorded as a **diagnostic observation**: this intervention, on these seeds, at these
pairs, removed the cross-hash-seed variation the instrument can see. It is **not**
evidence for H2 (the control moved, so the arm is inadmissible) and **not** evidence
against it (an inadmissible arm tests nothing). **Hash-invariant is not correct** —
stability under an arbitrary total order says nothing about whether the order is the
one the organism should have.

**The line is stopped.** Hash-order effects may return only under a new protocol that
measures invariance *and* membership effects on fresh seeds with criteria fixed
beforehand. Until such a protocol exists, no further B-prime runs.

**What this cost, and what it bought.** Two days of instrumentation, one void
generation, and one lesson the record did not previously hold in this form: **a
contradiction between a prediction and a measurement is a reason to audit the
instrument before rewriting the prediction.** §85 committed the opposite reflex in
writing, which is why it is corrected there rather than quietly dropped.

→ `docs/divergence_arm_b_prime_AUDIT.md` §7.

## §89 — A protocol draft for reusable knowledge, and nothing run

The owner's next target is the question the acquisition study never reached: **can
Organica's formed structure be used as reusable knowledge?** The answer is not in the
record — the acquisition study stopped at its acquisition gate and reported transfer
*not measurable*, which is neither a failure nor a success.

`docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` is a **draft**, labelled as such: it
commits no run, and §0 asks the owner to choose between a formally named diagnostic
variant (`V1.1-cap`) and leaving V1 frozen with its capacity limit recorded as a
finding. Three things it fixes that the earlier campaigns got wrong or left implicit:

- **The formation gate must be able to fail, and its failure must be informative** —
  coverage against the generator's support, measured on the final store, with the
  threshold fixed from calibration data rather than from the run it judges.
- **The baselines must be named for what they are granted.** The utilization campaign's
  T2 bar was a cell counter handed the latent cell map; calling that "data-only" was
  recorded as a naming defect. The draft forbids the phrase and requires each
  comparator's grant to be stated beside its score.
- **Capacity and ordering changes are variants, never adjustments.** Any change to
  `MAX_PREDICTIONS` or to the ordering of candidate construction is formally named,
  built in `benchmarks/`, labelled in every artifact, and may never be described as
  V1 or folded into the frozen reference.

No cell has run, no harness has been extended for it, and the draft is not a
preregistration until the owner signs §0.

## §90 — The transfer manipulation is feasible, but not the way the draft proposed

**The review was right on three counts.** (a) The draft pointed at
`organica/ground_truth_worlds.py`, the older hidden-cause generator; the transition
worlds are `benchmarks/acquisition_world.py` (four groups) and
`benchmarks/acquisition_compositional.py` (four cells, the one the utilization campaign
ran). (b) The compositional generator's existing `trainable` mask withholds the
**stored** event while still generating it and advancing the hidden state, so stored
events end up adjacent across a gap the world never had — not a conditioned stream, and
reusing it would have manufactured adjacency and called it a world. (c) The unit was
ambiguous: the law has **eight** directed cell transitions and **128** tag pairs, while
the **112** is the *group* world's tag-level count, so "25 %" meant two of eight or 28
of 112 depending on which document a reader had.

**What the generator-only check found.** Six criteria were fixed before any subset was
evaluated. The draft's own rule — every fourth transition, `(0,1)` flip_q with `(1,1)`
flip_q — **fails**: the permitted graph is not strongly connected, cells `(0,0)` and
`(1,0)` are unreachable, and two permitted transitions drop to 0–1 instances in 720
events. All **28** two-transition subsets were evaluated, **16 are feasible**, and the
adopted rule is the first of them — withhold `(0,0)` flip_p with `(0,1)` flip_q — with
strong connectivity, every cell in and out, all four contexts present, the sparsest
permitted transition seen **36** times, consecutive pairs genuine, and **130** and **66**
instances of the two withheld transitions in a 100-cycle test window against a floor of
20.

**What this is, and is not.** A feasibility result about a generator, established
without an engine or a study cell. It is **not** evidence about the organism, and it does
not begin the campaign: no harness exists, and the rule is now declared in advance
rather than assumed. The fallback — report the limb as held-out generalization if no
subset were feasible — was written before the enumeration and did not need to be used.

**One check of my own was wrong, and is corrected here.** The first version of the
consecutive-event check compared each event's successor against the *next* event's
successor rather than against its own start, so it returned false on a stream that was
consecutive. Recorded because a broken check that fails loudly is luck, and the same bug
in a check that happened to pass would have gone unnoticed.

→ `benchmarks/reusable_knowledge_feasibility.py`;
`docs/reusable_knowledge_feasibility.json`; `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md`
§3.1.

## §91 — A seed leak and a schedule mismatch, and the promotion they delayed

**Two defects in the feasibility record, both found on review of the pushed version.**

**(a) A confirmatory seed selected the rule.** The check used `20261206` as its test seed
while selecting among all 28 candidate withholding rules, and the protocol had designated
`20261206–20261225` as confirmatory. A seed that informed a design choice is burnt for
confirmatory use; keeping it would have meant a rule chosen on a seed that later counted
as untouched evidence. Fixed by re-running the check on the **calibration seeds only**
(`20261201–20261205`), marking `20261206` **diagnostic**, and moving the confirmatory set
to `20261207–20261226` so n = 20 is preserved instead of quietly becoming 19.

**(b) The schedule was not the protocol's schedule.** The check used 90 formation cycles
and a 100-cycle test window. The module's own schedule is warmup `0–19` plus acquisition
`20–109` — 110 cycles of formation exposure — with the transfer limb scored on cycles
`150–199`, a 50-cycle window. The check now conditions **both** formation phases and
verifies the floor inside the **real generated world's** transfer window.

**Result under corrected conditions.** 16 of 28 subsets remain feasible and the adopted
pair is unchanged — `(0,0)` flip_p with `(0,1)` flip_q — with the sparsest permitted
transition seen **38** times and at least **30** instances of each withheld transition in
the 50-cycle transfer window, met on every calibration seed. The pair therefore survives
on evidence independent of the burnt seed; its earlier selection is superseded rather than
reused.

**Promotion.** §0 was already signed, §12 closed the four review points, and §13 closes
these two defects, so `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` is now a
**preregistration** (Revision 2). Next, in order: build the harness, run the calibration
pass on the five calibration seeds, then the confirmatory cells. **No cell has run and no
harness exists**; Organica 1 stays frozen at `v0.9.0`.

**Why this is the second time in two days.** The B-prime audit (§87) was the same shape —
a label that outran its mechanism. Here the label was a seed's status: a number that had
already been spent still being described as fresh. Cheap to fix now, unrecoverable after
the campaign.

→ `benchmarks/reusable_knowledge_feasibility.py`;
`docs/reusable_knowledge_feasibility.json`; `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md`
§3.1, §8, §13.

## §92 — Two definitions fixed before the harness, because one would have made a gate unreachable

**Gate F's denominator.** Counting coverage against the law's whole 128 tag-pair relations
would have capped the achievable value at 0.75, since the 32 withheld
relations are absent from formation by design — so a 0.95 threshold would have failed
every arm and measured nothing. Gate F therefore counts the **96 available** relations,
with the withheld 32 excluded from numerator and denominator and scored only by the
transfer limb. This is the same defect as a gate that cannot fire, inverted: a gate that
cannot pass. Either way the study would have been unmeasurable, and it would have looked
like a result.

**The ceiling.** The ceiling is the **full latent-rule holder** — the law plus the
generator's two-tags-per-event rule, giving 0.325 for a flip_p successor and 0.175 for a
flip_q successor, in closed form with nothing to estimate. The oracle-admitted arm is
demoted to a **mechanism arm**: informative about admission filtering at fixed evidence,
and never a ceiling, because it receives the support of the answer rather than the law.

**Why both had to be settled first.** Both are definitions a harness encodes, and either
could have been chosen after seeing a number — the denominator by noticing which one the
arms pass, the ceiling by preferring the comparator the arms beat. Fixing them now, in an
amendment that says what it supersedes, is the only point at which the choice is free.

→ `docs/reusable_knowledge_gate_definitions.json`;
`docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` §2, §4, §9, §14.

## §93 — The variant fixed at 1,000, calibration gated on all five, and one arm deferred rather than approximated

**Capacity fixed at `MAX_PREDICTIONS = 1,000`.** Formation has been demonstrated at that
capacity (asserted coverage 98.2–100 %) and not at the published 20 (0.0–2.7 %), so it is
the only value at which this protocol's Gate F has a precedent. Fixing it before the build
means the capacity cannot be re-chosen after a result; a different value is a different
variant.

**Gate F governs calibration on V1.1 only, all five seeds required.** Calibration is a
go/no-go at n = 5, where each seed is a fifth of the evidence, so one failure stops the
study before a confirmatory seed is touched. Confirmatory keeps the rate rule already in
§2 — 15 of 20. The two rules are deliberately different and neither may be swapped for the
other afterwards; writing both down here is what makes that checkable.

**The oracle-admitted arm is deferred, not approximated.** Its candidate-level rule was
never specified to a reproducible standard, and the B-prime failure (§87) was an arm whose
mechanism existed only as a label. It is excluded from both passes, no verdict may cite it,
and it can only return through an amendment that states the rule before any cell runs.

**A build fact, so the harness cannot quietly reuse the wrong machinery.** The existing
generator and runner carry the earlier **one-transition** mask (1 of 8) and the
storage-skip pattern §3.1 rejects; the conditioned sampler is new work in `benchmarks/`.
Five build items are now enumerated in §10, with the parameters in
`docs/reusable_knowledge_variant.json`.

**Still not started.** No harness, no calibration, no cells. Organica 1 stays frozen at
`v0.9.0`.

→ `docs/reusable_knowledge_variant.json`;
`docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` §4, §6, §10, §15.

## §94 — The harness exists, the calibration gate passes on five of five, and the margin is partial

**Built.** `benchmarks/reusable_knowledge.py` implements the five items of §10:
the conditioned sampler (the withheld transitions are never *generated*, so no
event is skipped and no adjacency is manufactured — the `trainable` mask is
retired), the Gate F audit over the 96 available relations with its precision
companion, the retention and withheld-only transfer limbs, the closed-form
latent-rule holder, and the comparator sweep with the cell counter kept
privileged. The oracle-admitted arm was not implemented, as §15.3 requires.

**The audit can fail, and was shown to.** Four checks: the endpoint separates the
ceiling from a one-transition learner; Gate F fires when ~10 % of the available
relations are dropped; no withheld transition appears in any formation exposure;
no limb has an empty denominator. All four pass on every calibration seed, and
`tests/test_reusable_knowledge.py` pins them at the generator level.

**Calibration, V1.1-cap(1000), `20261201–20261205` — 5 of 5 pass Gate F.**
Minimum coverage 0.9792 (seed 20261202, 94 of 96); the other four are
0.9896–1.0000. Per §15.2 this is a go/no-go and it cleared, so the study may
proceed to the confirmatory set. **No confirmatory seed was run.**

**What the transfer limb showed, stated at calibration strength only.**

| seed | Gate F (covered / 96) | Organica transfer | best primary | ceiling | Organica − best primary |
|---|---|---|---|---|---|
| 20261201 | 1.0000 (96/96) | 0.5957 | decayed_bigram 0.7709 | 0.3726 | +0.1752 |
| 20261202 | 0.9792 (94/96) | 0.6033 | decayed_bigram 0.7717 | 0.3795 | +0.1684 |
| 20261203 | 0.9896 (95/96) | 0.5985 | decayed_bigram 0.7684 | 0.3691 | +0.1699 |
| 20261204 | 1.0000 (96/96) | 0.6006 | decayed_bigram 0.7622 | 0.3760 | +0.1616 |
| 20261205 | 1.0000 (96/96) | 0.5982 | decayed_bigram 0.7418 | 0.3690 | +0.1436 |

Organica is better than the best primary comparator on every calibration seed
(worst margin +0.1752 nats) and worse than the ceiling on every one, the ceiling
lying 0.2231 to 0.2294 nats below it. So the readout recovers part of the law's
advantage on the withheld transitions and not all of it — a partial margin, not a
transfer result. Calibration is n = 5 and one seed is a fifth of the evidence;
the 15-of-20 confirmatory rate is the measurement, and it has not been run.

→ `docs/reusable_knowledge_calibration.json`;
`docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` §16;
`benchmarks/reusable_knowledge.py`; `tests/test_reusable_knowledge.py`.

## §95 — The calibration now names its variant, the attribution share is a criterion, and the engine is hash-sensitive

**Two protocol defects closed before the confirmatory set.** Both were found by review,
not by a failure, and both would have authorised a campaign the protocol did not describe.

**1. A capacity override could authorise seeds under a label it never ran.** The harness
took `--cap` and labelled every artifact `V1.1-cap(1000)`, and `confirmatory_allowed()`
read only `all_seeds_passed`. A calibration at another capacity would therefore have
unlocked the confirmatory seeds and been written up as the calibrated variant. Fixed on
three sides: the label is now derived from the capacity (`variant_label`), calibration
refuses any capacity but 1,000 with a non-zero exit, and the guard checks the artifact's
`cap`, `variant` and seed set as well as its Gate F, audit and attribution flags, naming
the field that fails. This is AGENTS rule 25's "two gates with one name" defect one level
up: one name, two quantities.

**2. The readout's evidence had no attribution rule.** The readout sums edge weight over
every structure type, so a transfer margin could rest on concepts, loops, phrases or
hypotheses rather than on the Layer-1 predictions the study forms. §17 now makes the
**attribution share** — Layer-1 weight over total weight — a criterion with a **0.50**
minimum, the formation-utilization campaign's A7 operating point, adopted before any
confirmatory seed and not chosen from these numbers. On the five calibration seeds the
share is 0.9848–0.9866 (Layer-1 carries 12,076–12,157 of
12,248–12,334 total weight), so the margin that was measured is at least
carried by the structure type it is attributed to. That is a diagnostic at n = 5, not a
transfer result, and the criterion still has to be met on all twenty confirmatory seeds.

**The first control for it could not fire, and was replaced.** The initial companion cut
Layer-1's weight to a tenth of itself and recomputed the share; on a real cell that returns
**0.88**, still far above the minimum, because Layer-1 is most of the weight — decoration
of exactly the kind rule 25 describes. The control is now the counterfactual in which the
readout holds no Layer-1 evidence at all, which returns 0.0 by construction and is asserted
at the generator level. Audit `E5` checks it on every cell.

**3. A calibration that passes twice can pass differently.** Adding the attribution
measurement re-ran the five calibration seeds, and seed `20261204` returned transfer
**0.6025** where the committed artifact said **0.6006**; the other four reproduced exactly.
A same-process probe ruled out ordering and repeat effects — the same seed run four times
in one process returned 0.60055 every time — and fixed hash seeds reproduce bit-identically
across values. The engine's candidate ordering is built from sets of strings, so the score
is hash-sensitive: an unset `PYTHONHASHSEED` gives a nominal seed that is not one seed.
Calibration now refuses to run without a fixed hash seed and records its value in the
artifact (canonical artifact: `0`). The divergence is disclosed rather than smoothed away,
and the figures in §16, §94 and §17 are regenerated from the artifact the guard actually
checks — which is worth stating plainly: before this fix, the committed calibration table
was a number no one could reproduce exactly.

**Consolidation.** There is one worktree and one branch in this checkout, and
`HEAD == FETCH_HEAD == fe5f056` after the previous push, so there was nothing to reconcile
and no duplicate implementation to retire: the "second clone" was this session's earlier
state at `95fc329`, and the harness it lacked is the one committed here. V1 stays frozen at
`v0.9.0`; V1.1-cap(1000) remains a benchmark-side variant with its own label, artifact and
protocol, and the two are not pooled (§17.3).

**State after this work.** Gate F 5 of 5; audit 5 of 5 checks on every seed, each shown to
be able to fail; attribution share at or above the minimum on all five; artifact records
`authorises_confirmatory: true`, cap 1,000, label `V1.1-cap(1000)`, hash seed `0`.
**No confirmatory seed has been run.**

→ `docs/reusable_knowledge_calibration.json`; `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md`
§17; `benchmarks/reusable_knowledge.py`; `tests/test_reusable_knowledge.py`.

## §96 — The revision limb is implemented, the trace-derived diagnostic is measured, and it closes the study

**What was missing.** §5 of the protocol defines three limbs and calls a revision-held-out window a
co-primary; the harness scored two. And the protocol had no **trace-derived** diagnostic, which
AGENTS rule 18 requires of the next study's criteria — §17's attribution share counts structure
types, not evidence provenance, and those are different questions.

**Revision, implemented as §5 defined it.** After formation the organism is exposed to the
revision-learning window (200–250) under the rotated law with the same two transitions withheld, the
readout is frozen again, and the revision-test window (250–300) is scored. `revision` covers the
whole window; `revision_held_out` is the co-primary and covers only the withheld transitions, which
stay held out because the learning window is conditioned as well. Held-out pairs per seed:
82–110. Organica scores 0.6309–0.6618 on the co-primary against
0.7529–0.7814 for the best comparator and
0.3193–0.3266 for the rotated law's ceiling. That is the same shape as
transfer: better than the comparators, well short of the law. **It is calibration, not a result.**

**The diagnostic, and the stop.** A store-time observer repeats the engine's own lookback query —
`SELECT tags, event_type FROM events ORDER BY time DESC LIMIT 3`, which includes the event just
stored — after every write, and labels each support transition world or self. On the asserted edges
of the readout, **0.4092–0.4155 of the formation readout's supporting
transitions are self-sourced**, and 0.4129–0.4167 for the revision readout;
sleep payloads reached the lookback window in 218–218 stores per seed, so the
mechanism is present and the measurement is not vacuous. The maximum was declared at **0.25** before
it was measured, and it fails on all five seeds. The artifact records
`authorises_confirmatory: false` and the confirmatory set stays closed.

**Why this is the right outcome rather than a setback.** The study exists to ask whether formed
structure is usable on evidence it never saw. Roughly two-fifths of the readout's support for those
predictions comes from the organism's own previous sleep payload rather than from the world. By the
project's own pre-committed rule, a predicted-correct result resting on self-sourced support is not
a transfer result — so the honest state is *not attributable*, and the alternative is to relax a
threshold the moment it binds, which is precisely the failure rule 14 records. §16 said Gate F
cleared and the study proceeds; it did clear, and the diagnostic stopped the study before any
confirmatory seed. No threshold moved, and no confirmatory seed ran.

**A defect found while building it.** The first revision patch let the formation readout's base rate
be computed over formation **plus** revision events — a denominator that had seen a window the
readout is later scored on. It was caught by comparing against the committed calibration (transfer
moved from 0.5957 to 0.5725 on seed 20261201) and fixed by smoothing each readout only on what the
organism had seen at the time it was frozen; the transfer numbers returned exactly to their
committed values.

**State.** Gate F 5 of 5; audit 7 of 7 checks on every seed, each shown able
to fail; attribution 0.9848–0.9866; support provenance 0.4092–0.4155 against 0.25 →
**confirmatory closed**. `tests/test_reusable_knowledge.py` covers the revision stream, its
denominators, the provenance control and the hash-seed guard.

→ `docs/reusable_knowledge_calibration.json`; `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` §18.

## §97 — The provenance measure is reconciled with the per-claim rule, and the stop survives the correction

**What was wrong with §96's measure.** It summed all of the readout's asserted edges into one
share, and the audit-trace specification says in as many words that a run-level figure is not a
per-claim share (§3.3) and writes its disqualifier as a per-claim rule (§11). It also counted
support references — one increment per store — where the spec reserves the **distinct** count for
the disqualifier. So the finding was narrower than §96 implied: about two-fifths of the measured
**transition support associated with asserted edges** was self-sourced. It did not establish that
the transfer predictions relied on self-sourced evidence claim by claim.

**Reconciled.** The observer now keeps distinct prior event ids per edge, split world/self, and the
criterion is applied claim by claim — every Layer-1 prediction and every hypothesis the readout
asserts — against the reference **frozen from the audit-trace build at 17.9 %** (802 of 4,481
distinct transitions, default arm), never recomputed on this run. A claim must have measurable
support, be no more self-sourced than that reference, and be mostly world-derived.

**The corrected measurement is worse for the study, not better.** 604–1277 measurable
claims per seed, of which 264–592 fail
(43.7–52.4 %); the maximum per-claim share is 1.0000, so some claims
rest entirely on the organism's own output. The run-level distinct share is
0.4209–0.4287 (6,732–6,806 world vs 4,947–5,051 self
transitions), which replaces §96's reference-counted 0.4092–0.4155 as the diagnostic figure.

**What survives, and what it costs.** `authorises_confirmatory` is false; the confirmatory set
stays closed; Gate F still passes 5 of 5 and the audit passes 8 of 8 checks on every
seed, including a new `E8` that checks the per-claim rule is measurable and that its all-self
control fails. The rule that now blocks the study is the one that was committed for this purpose
before the study existed — not a threshold invented after a number arrived. §18.3's stop is
unchanged; only the measure it rested on has been corrected to the resolution the rule is written
at.

**The timing is recorded, not argued.** The §17 attribution threshold was added after the transfer
margin was visible; the §18 aggregate band was declared before *its* measurement but after that
margin too; the per-claim reference is frozen from a different build and predates this protocol.
Their weights are not equal, and the artifact now records which figure gates and which merely
reports.

→ `docs/reusable_knowledge_calibration.json`; `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` §19;
`docs/AUDIT-TRACE-SPEC.md` §11.

## §98 — Three defects in the per-claim measurement, and what survived them

**The unit was wrong.** §97 keyed each claim's support by the source event, so repeated transitions
out of one prior event collapsed into one. The audit-trace observer defines a distinct transition as
the pair (prior event, target event) — spec §3.3 — and the frozen 17.9 % reference is a count of
those. Comparing a source-event count against a transition-pair reference is the offence rule 19
prohibits, one level down: the numbers are not of the same kind. Keyed correctly, distinct support
rises to 12,076–12,157 and the run-level share falls to 0.4092–0.4155.

**The control did not run the code.** `control_all_self_fails` compared a boolean built from two
literal arguments, and the audit checked the boolean. It never passed a claim through the evaluator,
so it could not fail for the reason a control exists. It now builds an all-self support map over the
same claim set and judges it with the same function; `E8` checks that the control's claims equal the
population, all fail, and reach a maximum share of 1.0. The rebuilt check reported failure the moment
the population's field names changed, which is the behaviour an instrument check should have.

**The scope is decided rather than assumed.** The rule governs every claim the readout asserts,
because a prediction for a scored pair comes from the asserted structure through smoothing, not from
a claim about that pair. The narrower population — claims about the withheld relations themselves —
has 0–20 claims, 0–20 of them measurable, and on 2 of
5 seeds none at all, so it cannot be the criterion; it is reported beside it. Unmeasurable
claims are excluded and reported, with a declared 50% measurable floor below which the rule
is reported not evaluable rather than passed; the measured fraction is 0.9711–0.9765.

**What survives.** 254–576 of 604–1277 measurable claims still fail per
seed (42.1–52.1 %), shares still reach 1.0000, the revision limb adds
282–510 failures, and `authorises_confirmatory` is still false. The 264–592 count is
withdrawn rather than quietly updated: on the corrected unit every seed fails slightly fewer claims
(592, 348, 332, 264, 336 → 576, 346, 326, 254, 332), so the defect did not
manufacture the failure — and the record should show the defect and its repair, not a number that
moved without explanation. The instrument passes 8 of 8 checks; the criterion fails.

→ `docs/reusable_knowledge_calibration.json`; `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` §20.

## §99 — The observer's target identity was reading the wrong row, and the counts survive it

The per-claim measurement had one more defect, in the instrument rather than the arithmetic: the
support observer took the **target** event of every transition from `rows[0]` of its own lookback
query (`ORDER BY time DESC LIMIT 3`). That query has no `rowid` tiebreak and there is no index on
`events.time`, so when timestamps tie, its first row is not guaranteed to be the event just stored.
Every transition of such a store would then be filed under a different event — and the per-claim
rule would judge claims on transitions they never had. The engine's own store already returns the
event, so the observer now resolves the target by a keyed lookup on the primary key
(`stored_rowid(mem, event.id)`) and uses the window only to identify source events. The stored row
remains a legitimate source, because `_record_temporal_edges` runs after the insert and the engine
sees its own event in the window.

**The tie arm is not enough on its own, and saying so is the point.** Forcing one timestamp per
four stores gives 5 tied windows in 6 stores on SQLite 3.45.1, and the observer names the stored
row on every transition. But on this build `rows[0]` *also* agreed with the stored row in all 6
stores — the defect was latent, not misfiring, and an empirical tie test alone would have cleared
it. So the second test wraps the connection and returns the tied window with the stored row last,
an order SQLite may legitimately choose; it asserts that the reordered rows really do tie on
`time`, that `rows[0]` is then a different event, and requires the recorded target to be the
stored one regardless. That test fails on the old rule and
passes on the new one.

**Nothing moved.** Calibration was rerun and reproduced `docs/reusable_knowledge_calibration.json`
byte for byte: the real runs use a wall clock, so no tied window arose. 254–576 of 604–1277
measurable claims still fail per seed, `authorises_confirmatory` is still false, and the audit is
still 8 of 8. The confirmatory seeds have not been touched.

→ `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` §20.6; `tests/test_reusable_knowledge.py`.

## §100 — The study closes at calibration, and the postmortem's first labels claimed more than the data

The per-claim rule failed on all five calibration seeds, so the study is **closed at calibration**:
no confirmatory seed runs under this protocol, no threshold is revised, §98's verdict stands, and the
closure is recorded in the protocol (§20.7) rather than inferred from an `authorises_confirmatory`
field. That part is settled.

**The postmortem, and its own correction.** The five cells were re-read with a support classifier that
separates circular restatement, field-name involvement and non-schema content
(`docs/reusable_knowledge_postmortem.json`). Its first version labelled any transition with *one*
field-name endpoint as `schema` — which reads as "the transition is between two field names" — and
labelled the remaining content `content_relayed`, which asserts a world origin. Neither label was
supported by the code or the data, and both were replaced before the artifact informed any design
decision: `field_name_both` is the encoding alone, `field_name_one` mixes one field name with one
content tag, and `content_unresolved` records non-schema content whose origin is **not traced**.

With the corrected labels, on the same five cells:

- **Circular self-support is negligible**: 8 formation and
  7 revision transitions have the payload asserting the very pair.
- **Pure encoding does not fail the claims**: excluding transitions between two field names rescues
  0 of 1,834 failing formation claims and 0 of 1,792 revision
  claims.
- **Field-name involvement is real, and structurally one-sided**: excluding every transition that
  touches a field name also rescues 0 and 0, so the two counterfactuals agree on these
  cells. `field_name_both` is 0 / 0 because a transition's target is always a tag of the
  world event just stored (the observer records only after world stores), so a field name can only ever
  be the prior tag. The encoding's footprint is entirely `field_name_one` (15,576 / 20,876); the
  old label's error was descriptive rather than numerical, which is exactly the kind of error that
  survives a check that only compares counts.
- **The largest class is unresolved in origin**: `content_unresolved` accounts for
  44,897 of 60,525 formation and
  60,695 of 81,624 revision self transitions, and the payloads
  carry 2340 parent ids and 0 event
  references — no path from a payload back to the world events behind it. So these cells cannot say
  whether that content is world-rooted.

**What that leaves.** The disqualifier measures whether the immediately preceding event was the
world's; that stands, and it is why the study stops. It does not show circular support, and — after the
correction — it does not show world-rooted relayed support either. The next move is a separately named
variant with its own preregistration and fresh calibration seeds, and the measurement that would
separate the two designs is a provenance rule that follows a support tag to the world event that
introduced it. These cells cannot supply that; they can only say that the current rule cannot.

The rule did not move: the per-seed failing counts reproduced calibration exactly
(576, 346, 326, 254, 332), `rule_unchanged: true`, `authorises_confirmatory: false`,
asserted before the artifact is written and checked by a test.

→ `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` §20.7; `docs/reusable_knowledge_postmortem.json`.

## §101 — The next instrument is a provenance tracer, and its controls found two bugs before any real data

The closed study's rule asked whether the immediately preceding **event** was the world's. The
postmortem then showed that the largest class of self-sourced support carries non-schema content
whose origin the payloads do not record. So the next question is not "which learner variant", it is
"can support be traced from a claim, through the parent structures it names, back to world
observations?" — and that question gets an instrument before it gets a protocol.

`benchmarks/provenance_trace.py` follows `parent_ids` breadth-first from a claim, cycle-safe and
depth-capped at the engine's own `get_ancestry(max_depth=7)`, and classifies the chain by whether its
**ancestors** carry tags the world also uses:

- `world_rooted` — every ancestor carries world vocabulary and at least one terminal exists;
- `mixed` — some ancestors do, some do not;
- `self_only` — none does;
- `unresolved_missing_records` / `unresolved_cycle` / `unresolved_depth_truncated` /
  `unresolved_nothing_resolved` / `unresolved_no_ancestry` — with the reason kept, because a chain
  that silently drops an unresolvable ancestor would look complete when it is not.

**The resolution is the point, so it is stated rather than implied.** Structures reference each other
by **structure id**, never by event id. So `world_rooted` means *every ancestor carries tags the world
uses* — not *descends from observation X*. That is weaker than event-level provenance and stronger
than "the row was stored during sleep", and the status vocabulary keeps the difference visible instead
of compressing it into a boolean.

**Controls first, and they earned it.** The instrument was run on ancestry known by construction
before touching data:

| control | status | expected |
|---|---|---|
| `cycle` | `unresolved_cycle` | `unresolved_cycle` |
| `depth_capped` | `unresolved_depth_truncated` | `unresolved_depth_truncated` |
| `missing_parent` | `unresolved_missing_records` | `unresolved_missing_records` |
| `mixed` | `mixed` | `mixed` |
| `self_only` | `self_only` | `self_only` |
| `vocabulary_removed_flips_control` | `self_only` | `self_only` |
| `world_derived` | `world_rooted` | `world_rooted` |

Two design defects were caught by those controls, neither of which a real-data run would have made
obvious:

1. **The index has to include the claim itself.** Built from ancestors only, every claim resolved to
   "nothing", which looks like a data absence rather than an instrument bug.
2. **Grounding must exclude the claim's own words.** Judged on all nodes, a claim that names a world
   tag is `world_rooted` by definition — the fixture labelled self-only came back `mixed`, and the
   cause was the claim's own surface words counting as its ancestry. Grounding is now judged on
   ancestors, and a claim with no parent links is `unresolved_no_ancestry`, not `self_only`.

The mutation control matters as much as the fixtures: emptying the world vocabulary flips the
world-derived control to `self_only`. A tracer that cannot change its answer would be decoration
(AGENTS rule 25).

**What this is not.** No threshold, no verdict, no seeds, no artifact claiming a finding: the module's
own summary says `instrument diagnostic; no threshold and no verdict`. The closed study stays closed,
its failure stays a failure, and the confirmatory seeds stay untouched. The next step is a **new
preregistration with fresh seeds**, written after deciding which status distribution would count as
evidence — a decision that has to be made before the tracer is pointed at a world, not after.

→ `benchmarks/provenance_trace.py`, `tests/test_provenance_trace.py`;
`python -m benchmarks.provenance_trace --controls`.

### Extension, same day: a resolved branch must not hide an unresolved one

The first control set tested **isolated** defects, and that was not enough. A claim with one valid
world-tagged parent and one missing parent still reached a terminal, so `trace()` returned
`world_rooted` and reported the missing record only in a field nobody reads as a status. The same
masking applies to a cycle or a truncation on a second branch. The controls now include the mixed
lineages, and **10 controls** run:

| control | status | expected |
|---|---|---|
| `cycle` | `unresolved_cycle` | `unresolved_cycle` |
| `depth_capped` | `unresolved_depth_truncated` | `unresolved_depth_truncated` |
| `missing_parent` | `unresolved_missing_records` | `unresolved_missing_records` |
| `mixed` | `mixed` | `mixed` |
| `self_only` | `self_only` | `self_only` |
| `self_only_with_cycle` | `self_only_incomplete` | `self_only_incomplete` |
| `vocabulary_removed_flips_control` | `self_only` | `self_only` |
| `world_derived` | `world_rooted` | `world_rooted` |
| `world_rooted_with_depth_truncation` | `world_rooted_incomplete` | `world_rooted_incomplete` |
| `world_rooted_with_missing_parent` | `world_rooted_incomplete` | `world_rooted_incomplete` |

The fix is in the status, not in a footnote. Any missing, cyclic or truncation-cut branch appends
`_incomplete` to the grounding verdict — `world_rooted_incomplete`, `mixed_incomplete`,
`self_only_incomplete` — and the result carries `defects` (which branch failed and how) and
`complete`. `nodes` and `terminals` still summarise what resolved, because losing the resolved
branch would be the opposite error; but **only a complete lineage may be read as `world_rooted`.**
A test pins that: the three clean fixtures come back with `complete: true` and no defects, and the
three mixed ones never do.

This is still an instrument, not a study: no threshold, no verdict, no seeds, and the tracer has not
been pointed at real data.

### Extension 2, same day: convergence is not a cycle

The traversal marked **any** repeated node as a cycle. A diamond lineage — two parents sharing one
ancestor — revisits that ancestor legitimately, so a complete multi-parent chain was reported
`_incomplete`. That is the worse direction of error for this instrument: it would have under-counted
`world_rooted` on exactly the multi-parent graphs the engine produces most.

Cycle detection is now a colour DFS over the collected edges. Only an edge into a node that is still
on the current path is a loop; a node reached again after it has been fully explored is convergence,
explored once and recorded black. **11 controls** run:

| control | status | expected |
|---|---|---|
| `cycle` | `unresolved_cycle` | `unresolved_cycle` |
| `depth_capped` | `unresolved_depth_truncated` | `unresolved_depth_truncated` |
| `diamond_shared_ancestor` | `world_rooted` | `world_rooted` |
| `missing_parent` | `unresolved_missing_records` | `unresolved_missing_records` |
| `mixed` | `mixed` | `mixed` |
| `self_only` | `self_only` | `self_only` |
| `self_only_with_cycle` | `self_only_incomplete` | `self_only_incomplete` |
| `vocabulary_removed_flips_control` | `self_only` | `self_only` |
| `world_derived` | `world_rooted` | `world_rooted` |
| `world_rooted_with_depth_truncation` | `world_rooted_incomplete` | `world_rooted_incomplete` |
| `world_rooted_with_missing_parent` | `world_rooted_incomplete` | `world_rooted_incomplete` |

The diamond control requires `world_rooted`, `complete: true`, `cycle: false`, and the shared ancestor
counted exactly once in `nodes`. A second control puts a genuine loop beside a diamond and requires
the loop still to be reported — convergence must not be able to mask a cycle either. Both are tests,
not remarks.

`world_rooted` keeps the meaning it was given: **vocabulary overlap along a complete ancestor chain**,
not proof of descent from a particular world observation. Nothing here has been run on real data.

## §102 The tracer pointed at the calibration cells: the claims it scores carry no ancestry

The plan was committed first — `docs/PROVENANCE-ANALYSIS-PLAN.md` at `c5b4d49e` — so the reading of
these counts was fixed before the counts existed. All 11 controls passed
before the tracer was pointed at a cell. Seeds `20261201–20261205`, cap
`1000`, `PYTHONHASHSEED=0`. Artifact: `docs/provenance_diagnostic.json`; the results
document beside it is rendered from that artifact by `--report`, not typed. No threshold, no
verdict, no confirmatory seed touched.

### What the snapshots hold

| type | limb | claims | complete `world_rooted` | incomplete | unresolved |
|---|---|---|---|---|---|
| `prediction_candidate` | formation | 1581 | 0 | 0 | 1581 |
| `hypothesis` | formation | 63 | 14 | 49 | 0 |
| `prediction_candidate` | revision | 1596 | 0 | 0 | 1596 |
| `hypothesis` | revision | 57 | 13 | 44 | 0 |

**The claim type the study scores is stored without parent links.** All 1581 formation and
1596 revision `prediction_candidate` structures resolve zero ancestors — `unresolved_no_ancestry`
at depth 0 — and no claim in either snapshot is `unresolved_missing_records`
(0 / 0). So this is
not a dangling-parent defect: those structures record no parents at all. `LAYER1_TYPE` is
`prediction_candidate`, which means the population the per-claim rule and the transfer limb are
about is exactly the population this walk cannot enter, and the postmortem's
`content_origin: unresolved` now has a structural mechanism behind it rather than only a missing
event reference: the readout's own structures do not record what they were built from.

`hypothesis` structures do carry lineage. 63 formation and 57 revision, each a
seven-ancestor chain that resolves to terminals inside the cap — 0 /
0 cut by our own depth cap, which is to say none.
14 formation and 13 revision are complete
`world_rooted`; the rest are `world_rooted_incomplete`: 39 formation and
41 revision carry a cyclic branch, 23 and
9 a parent absent from the snapshot (a claim can carry both).
No claim anywhere is `self_only` and none is `mixed`.

### What that does not show

Every resolved ancestor carried world vocabulary, and that is the whole of it. A hypothesis is
composed from its members, so a chain reaching world tags is close to true *by construction* for
that type; and a chain that shares vocabulary with the world is consistent with descent from an
observation **and** with self-generated content that reuses world words. The plan fixed this
reading before the numbers arrived: `world_rooted` is vocabulary overlap across a complete ancestor
chain, not observation-level provenance. Nothing here shows the links track world evidence.

### The branch the plan pre-committed

96.2 % of formation claim-typed structures (1581 of 1644) and 96.6 % of revision ones
(1596 of 1653) cannot be traced at all. By the plan's own reading, written in advance,
this is the **mostly-unresolved** branch: the missing lineage is in what the engine records, not in
the walk, and the next instrument would have to record a structure's origin at store time instead of
reconstructing it from ids. Nothing here licenses a confirmatory study, and the closed study is
untouched — `confirmatory_allowed()` still returns `(False, 'the per-claim support-provenance rule
did not pass on every calibration seed')`.

### One instrument change, and its check

The harness gained `run_engine(collect_structures=...)`, off by default, so the read-only walk can
see the payloads the readout already loads. It cannot change a scored quantity, and that is checked
rather than asserted: seed 20261201 re-run with the flag off reproduced the committed counts —
asserted pairs 327, revision-asserted 328,
temporal 393.

### Amendment, same day: three counting units, and a sentence withdrawn

A review found a unit mismatch in the section above, and it is real. The tracer
deduplicates a structure's per-cycle snapshots by id before counting, while the study's
per-claim rule passes the **raw** candidate list to `_claim_edges`, which drops ids and
counts one row per cycle a structure survived. For seed 20261201 the study counts
1313 formation and
656 revision claim rows,
where this trace reported 329
and 328
unique claim structures. Those were never the same quantity.

**The sentence "the population the per-claim rule and the transfer limb are about is
exactly the population this walk cannot enter" is withdrawn.** It was wider than the
check behind it: the structure types overlap, the counting units do not, and the study's
rows also include `hypothesis` structures, which do carry lineage.

What stands, at the resolution it was measured: every unique `prediction_candidate`
structure carries no parent links, and deduplication only collapses rows that share an
id, so no raw prediction row can have had them either ── the structural observation is
unchanged, its scope is now stated.

The diagnostic reports all three levels, and it reconciles the lowest against the study's
own selector: `_claim_edges` on the same raw payloads must equal the tracer's raw-row
count, or the run aborts. Summed over the five cells:

| unit | formation | revision |
|---|---|---|
| raw stored claim rows with an asserted edge (the study's count) | 3942 | 3640 |
| raw stored claim rows (all claim-typed rows) | 3942 | 3640 |
| unique structure ids | 1644 | 1653 |
| unique asserted edges | 1623 | 1638 |
| unique asserted edges with a complete `world_rooted` claim | 14 | 13 |

| seed | study claim rows (f / r) | unique structure ids (f / r) | unique asserted edges (f / r) | rows per structure, max |
|---|---|---|---|---|
| 20261201 | 1313 / 656 | 329 / 328 | 324 / 325 | 4 |
| 20261202 | 680 / 684 | 340 / 342 | 335 / 337 | 2 |
| 20261203 | 658 / 1002 | 329 / 334 | 325 / 331 | 2 |
| 20261204 | 622 / 632 | 311 / 316 | 309 / 315 | 2 |
| 20261205 | 669 / 666 | 335 / 333 | 330 / 330 | 2 |

No new cell was run: the same five calibration cells were re-read. The closed study's
verdict, the confirmatory set and every threshold are untouched, and there is still no
threshold here to touch.

### Amendment 2, same day: parent links counted per snapshot, not per structure

The previous amendment closed by saying "no raw prediction row can have had them either".
That was not established by the check offered: deduplication keeps the highest-generation
snapshot of an id, and says nothing about what its earlier snapshots held. The review that
raised it was right, and every raw `prediction_candidate` and `hypothesis` snapshot from the
same five cells has now been counted, with the two questions kept apart — did an id **ever**
carry parent links, and does its **latest** snapshot carry them:

| type | limb | raw rows | rows with parents | unique ids | ids ever with parents | ids with parents in the latest snapshot | ids whose parents appear only in earlier snapshots |
|---|---|---|---|---|---|---|---|
| `prediction` | formation | 3792 | 0 | 1581 | 0 | 0 | 0 |
| `hypothesis` | formation | 150 | 150 | 63 | 63 | 63 | 0 |
| `prediction` | revision | 3515 | 0 | 1596 | 0 | 0 | 0 |
| `hypothesis` | revision | 125 | 125 | 57 | 57 | 57 | 0 |

**The count agrees with the withdrawn sentence, and it is now measured rather than
inferred.** No raw `prediction_candidate` snapshot carries parent links at any cycle,
so every one of the 7307 raw prediction rows has none —
the deduplicated walk was evidence for the structure it walked, and this is evidence
for the population. The distinction still mattered: the sentence was withdrawn because
the check behind it could not support it, and a claim that turns out true by luck of
the data is still a claim that had no check behind it.

No threshold, no verdict and no new cell: the same five calibration cells were re-read, and
the closed study's status is untouched.

## §104 A prospective formation-provenance instrument, and the study it licenses

The ancestry tracer answered its narrow question and cannot answer the next one: prediction
structures on the calibration cells never recorded parent links, so no walk reaches their
origins. `benchmarks/formation_provenance.py` records origins instead of reconstructing
them — at the sleep cycle that forms a candidate, it writes down which stored events
supplied the asserted tag pair and whether their source rows were world events or the
organism's own sleep payloads. The hook calls the engine's own `_build_predictions` and
returns its list unchanged; 8 synthetic controls pass, including three
that can fail (deleting the world transitions flips `pair_mixed` to `pair_self_sourced`; a
mutating subclass is caught by the neutrality comparison; reinforcing an edge raises its
recorded world transitions from 6 to 9). The unit is a transition, and
`pair_unattributed` is reported as its own category rather than as zero support.

`docs/FORMATION-PROVENANCE-PREREGISTRATION.md` then fixes the study: the difference in
held-out success between `pair_world_attributed` candidates and candidates whose origin
includes a self-sourced row, 98.33 % interval, lower bound above zero, a permutation arm
that must fail, and four gates. Seeds are fresh (`20270101`–`20270120`), and no closed seed
is read. An association there would not mean the knowledge is useful or reusable, and
nothing in it reopens the closed study. No cell has run under it.

## §105 G13-D: capacity and world-only provenance together, once

Authorized by `docs/DECISION-V2-SCOPE.md` D2; the dated plan
(`docs/G13-D-DIAGNOSTIC-PLAN.md`) was committed at `c1c46dd` **before** the run. Seeds
20261101, 20261102, 20261103, 20261104, 20261105 only; `alpha = 256.0` held fixed in both arms as a constant, not an intervention;
both overrides in process; `git diff --stat -- organica/` empty.

**The provenance intervention was verified before any score was read.** The world-only
lookback removed every `precedes` source tag that occurs in no world event: the baseline
arm carries 11–18 such source tags on every seed, the g13d arm carries zero.

**Correction, recorded the same day and before any interpretation.** The capacity check
did not test what it claimed. It counted prior candidates of all types — 3,998 in both
arms — so it cannot show that the prediction cap bound, and the artifact now records that
check as *not measured*. What is verified about capacity is structural only:
`SleepService` truncates predictions to `self.MAX_PREDICTIONS` (20 in the baseline, 1,000
in the diagnostic subclass). The paired result is therefore a statement about the
**combined** condition; it is not decomposed into a capacity part and a provenance part,
and no second run was made to recover that decomposition. The per-seed artifact entries,
the five per-seed caches and the aggregation code were normalised the same day so the
capacity check reads *not measured* everywhere rather than only at the top level;
regenerating the artifact from cache reproduces identical scores.

Paired difference, g13d minus baseline, house shape (negative is better):

| seed | retention | transfer-diagnostic | revision |
|---|---|---|---|
| 20261101 | -0.0311 | -0.0332 | -0.0435 |
| 20261102 | -0.0333 | -0.0294 | -0.0413 |
| 20261103 | -0.0299 | -0.0312 | -0.0429 |
| 20261104 | -0.0258 | -0.0296 | -0.0410 |
| 20261105 | -0.0280 | -0.0293 | -0.0471 |

All **15 of 15** unique seed × window comparisons are negative — 30 of 30 counting the
metric shape, which coincides exactly here; the pooled means are
retention **-0.0296**, transfer-diagnostic
**-0.0305** and revision
**-0.0432** log-loss. The two metric shapes coincide exactly
on this readout, so the self-cells column adds no separate information here.

Absolute house-shape log-loss, baseline / g13d:

| window | 20261101, 20261102, 20261103, 20261104, 20261105 |
|---|---|
| retention | 0.4467 / 0.4156 | 0.4552 / 0.4219 | 0.4544 / 0.4245 | 0.4534 / 0.4276 | 0.4556 / 0.4276 |
| transfer_diagnostic | 0.4554 / 0.4223 | 0.4546 / 0.4252 | 0.4522 / 0.4210 | 0.4485 / 0.4189 | 0.4575 / 0.4282 |
| revision | 0.4697 / 0.4262 | 0.4617 / 0.4205 | 0.4650 / 0.4221 | 0.4628 / 0.4218 | 0.4718 / 0.4247 |

Fixed references, transfer-diagnostic:

| reference | 20261101, 20261102, 20261103, 20261104, 20261105 |
|---|---|
| replay learner (reference) | 0.3430 | 0.3446 | 0.3358 | 0.3349 | 0.3424 |
| cell counter (reference) | 0.3406 | 0.3430 | 0.3341 | 0.3327 | 0.3404 |
| Bayes ceiling (reference) | 0.2744 | 0.2742 | 0.2683 | 0.2714 | 0.2711 |

**What this is, and what it is not.** It is a diagnostic of the frozen engine's failure
mode under the two confounds the decision record named: on these five seeds the combined
condition scored better than the frozen baseline in every paired cell, which is a
statement about log-loss on three windows and nothing wider. It applies no threshold,
establishes no acquisition or transfer result, does not reach relation-family separation
or a non-frequency ranking, and authorizes no V2 build and no confirmatory campaign. The
closed acquisition preregistration, its Gate 13 threshold, the Task 2 stopped verdict and
every confirmatory seed assignment are unchanged. This thread stops here; broader work
needs a new recorded owner decision.

## §106 The provenance study ran: an association, and only an association

The preregistered design block ran first, on `20270101`–`20270105`, and evaluated no
endpoint. All three design gates passed: at least one non-`pair_unattributed` candidate
formed on every seed; the design-mean yield projects to **4422**
world-attributed and **8874** self-including candidates over the
fifteen confirmatory seeds, against the 30-per-arm floor; and the recording hook reproduced
the engine's own candidates exactly on the study build — **3998** candidates
compared by id, strength and count, identical. The first neutrality check failed on a list
versus tuple difference introduced by caching; that was a defect in the check, not in the
engine, and it is fixed rather than absorbed.

The confirmatory run then held on `20270106`–`20270120`, once, under the committed protocol.
Held-out success was the preregistered binary: the asserted pair occurs at least once in
cycles 150–200, a window the organism is never shown.

| arm | hits | n | rate |
|---|---|---|---|
| `pair_world_attributed` | 1938 | 4280 | 0.4528 |
| `origin_includes_self` | 2036 | 8528 | 0.2387 |

Difference **+0.2141**, 98.33 % interval **[+0.1959, +0.2281]**, lower bound above zero.
The interval is a percentile interval from 10,000 cluster-bootstrap resamples of the fifteen
seeds, because candidates within a seed are not independent; that method is recorded in the
artifact. The permutation control, which shuffles origin labels within seed and cycle,
returned **+0.000359** with interval **[-0.016244, +0.016023]**
— it includes zero, as it must. `pair_unattributed` never occurred in this run
(**0** candidates), so the exclusion rule was idle and the two arms are the
whole population.

**What this means.** Among the candidates this engine formed on these worlds, the recorded
provenance of a prediction's pair is associated with whether that pair occurs in a window the
organism was never shown: world-attributed pairs appear in that window about twice as often
as pairs whose origin includes the organism's own sleep payload. That is the endpoint the
protocol pre-committed, and it cleared its bar without a threshold being touched.

**What it does not mean, and the protocol said so before the run.** It does not mean the
knowledge is useful or reusable — an association with held-out occurrence is not the closed
study's margin, and provenance alone is never evidence of usefulness. It does not mean the
content originated in the world: `pair_world_attributed` says the source rows were world
events, not that the tags were first learned there. It does not reopen the closed study, whose
verdict, seeds and thresholds are untouched. It is not a functional test of whether developed
structure helps: the outcome is occurrence in a held-out window, not predictive performance
against an equally exposed baseline. And it is an observation, not an intervention.

The functional question therefore remains open, and it needs its own protocol: origins captured
at formation, held-out prediction scored against baselines given the same exposure, and an
external-use outcome. Nothing here authorizes it.

## §107 Robustness of the provenance association: descriptive only, verdict unchanged

These checks read the cached per-candidate records the confirmatory run wrote. No cell was
re-run, no threshold was applied, and no new success rule was created; the registered
difference, interval and verdict are untouched. Their purpose is narrower: does the pooled
association depend on one seed, and does it survive comparing candidates at the same recorded
evidence count? The registered permutation preserved seed and cycle but not `temporal_count`,
so frequency and provenance were not separated by the control.

**Per seed.** All **15 of 15** confirmatory seeds show a positive difference, ranging
**+0.1461** to **+0.2435**; the pooled value is **+0.2141**. The
association is not carried by a single world.

**Leave one seed out.** Removing any one seed leaves the pooled difference between
**+0.2117** and **+0.2187**, positive in **15 of 15** folds.

**By evidence count.** Across the **17** strata that hold both arms, the
within-stratum difference is positive in **17 of 17**, and the
stratum-weighted difference is **+0.2384**. So the direction is present at
comparable transition counts, not only where world-attributed candidates happen to carry more
evidence. This is the closest the existing data come to separating provenance from frequency.

**What it does not add.** No causal claim: these are observational strata, not an
intervention. No claim of usefulness: held-out occurrence is still not predictive performance
against an equally exposed baseline. No reopening of the closed study. If anything, the
uniformity raises the bar for the next protocol — an association this stable across seeds and
counts is worth testing functionally, and not worth calling utility.

## §108 The next protocol is functional, and it is committed before the harness exists

The provenance thread ended where it had to: an association with held-out occurrence, stable
across seeds, folds and evidence counts, and explicitly not a measure of usefulness. The
project's open question is the functional one, and `docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md`
now fixes it before anything runs.

Three choices matter, and each is defensive. **The score is a probability, not an occurrence
count:** mean log-loss per held-out tag pair, in nats, on the closed protocol's window
(cycles 150–200) as the primary and the withheld-relation subset as the co-primary. **The
baselines are tuned and equally exposed:** the comparator sweep with its declared grid, best
configuration selected on a tuning split excluded from the fit, and every arm fitted on the
same 110-cycle stream. **The bar is the upper bound:** the 98.33 % interval on Organica minus
the strongest baseline must lie below zero, so an interval containing zero is reported as no
improvement detected rather than as equivalence.

Capacity 1,000 and `alpha = 256.0` are carried over unchanged, from the G13-D scope and from
calibration on `20261099`; neither is retuned. Seeds are fresh (`20270201`–`20270220`, design
and confirmatory), disjoint from every seed this repository has used, and the design block
evaluates no endpoint.

The provenance instrument appears here only as a diagnostic, with a pre-committed
disqualifier: if the margin is carried mainly by support whose source rows are the organism's
own sleep payloads, the result is not a transfer result even if it clears the bar. The
diagnostic can disqualify a claim; it can never manufacture one.

**The harness is not built.** The provenance runner scores occurrence, not probability, and
reusing it would silently substitute the old question for the new one. The build is defined by
§2–§7 of the preregistration, has a stop condition, and may not start before this document is
committed.

## §109 The functional protocol's three undefined clauses, fixed before the build

The preregistration was sound in its question and incomplete in its measurement contract, and
the review said so before any code existed. Three clauses could not be implemented without
interpretation; all three are now settled in Amendment 1, committed with the protocol and
before the harness.

**Exposure and tuning.** The text said every arm was fitted on 110 cycles and that the last
15 were excluded from every fit. Both cannot hold. The rule now follows the closed protocol's
comparator: the 15 cycles are excluded from *selection* only, the winning baseline
configuration is refit on all 110 rows, and Organica develops online over the same 110 cycles
with no fit step. No arm is fitted on fewer rows than another, and the tuning split buys
selection honesty rather than a data advantage.

**The score.** "Log-loss per held-out tag pair" was imprecise. The endpoint adopts the closed
`score(exclude_self=True)` unchanged: one cell per source tag against every vocabulary tag,
the source-equals-target cell kept in the denominator with label zero, and the mean taken over
event pairs times source tags times vocabulary. Two-tag events contribute two source tags, not
two pairs; there are no sampled negatives.

**The disqualifier.** The share is computed on the same scale as the endpoint: per-cell
improvement on realised held-out transitions, split by the pair's recorded world and self
counts. A pair is world-majority only if `world > self`, so a tie counts against the claim; a
self-majority share of 0.50 or more withholds the transfer claim, and an unattributed share of
0.50 or more reports the margin as not attributable. `P = 0` is not evaluable, never zero.

None of this changes a seed, a gate, the capacity, alpha, the endpoint or its bar. The build
still does not exist, and no cell has run.

## §110 The disqualifier earns a gate of its own

Amendment 1 made the provenance rule computable but left it unproven able to fire. G3 tests the
ceiling against a one-transition learner and a degraded readout; G4 tests that recording is
neutral. Neither could show the new rule withholding a claim, so the one clause that exists to
constrain the headline result was, in gate terms, decoration — the defect rule 25(c) names.

G6 now requires synthetic fixtures, before any study seed: world-majority passes; self-majority
withholds and labels the result *not a transfer result*; unattributed withholds as *not
attributable*; an empty positive margin is *not evaluable*. The boundary fires at exactly 0.50
and not at 0.4999; ties (`world == self`) count as self-majority; and relaxing the threshold to
0.90 must stop the self-majority fixture from withholding. That last assertion is what
distinguishes a working rule from a fixture that trivially passes: if the fixture cannot be made
to stop withholding, it was never driving the outcome.

The review also caught that §11.3 named a "baseline" while the study has two windows. §11.5 fixes
both: attribution runs against the same strongest comparator that supplies the §4 bar, at its
selected configuration and refit on all 110 rows, per cell, with no per-seed re-selection; and
the primary and co-primary windows are computed separately, never pooled, with the claim withheld
if either window's share reaches the threshold. Design-seed statuses audit the function; they are
never a result.

No cell has run; the build remains unstarted.

## §111 The bar pointed two ways, and only one of them was right

§4 fixed the endpoint as `delta = log-loss(Organica) − log-loss(baseline)`, negative meaning
Organica scored better, and put the bar at the **upper** bound of the 98.33 % interval below
zero. §9, describing what a pass would mean, said the margin's **lower** bound cleared zero.
Those are not two phrasings of one criterion: for a negative-is-better difference they describe
opposite outcomes, and the reviewed text would have licensed a claim from evidence that Organica
was reliably *worse*.

The defect is the same family as the widened headline (rule 24): the measurement was right and
the sentence carrying it was not, and no numeric check would ever have fired, because §4 and §9
were each internally consistent. It was found by reading the two sections side by side, which is
what a protocol review is for.

§9 now states the upper bound, says explicitly why the direction is not incidental, and defines
the co-primary result in three named outcomes rather than the undefined "also moved": **moved**
(upper bound of its own interval below zero), **did not move** (interval contains zero, so a
primary pass is held-out generalization only and the word transfer is withheld), and **moved the
wrong way** (lower bound above zero, reported as reversed on that window rather than as a null).
Neither window gates or re-scores the other.

`tests/test_functional_preregistration.py` now asserts that the phrase "lower uncertainty bound"
appears nowhere in the protocol, and that §9 contains the upper-bound bar and all three movement
outcomes — so the two directions cannot drift apart again without a failing guard.

No cell has run. The harness build is next, and the protocol does not expand further.

## §112 The scoring layer, built against a gate that can fail

The functional harness began where it should: at the measurement contract, not at the engine. The
first commit is the pure scoring layer — cells, per-cell loss, the four attribution outcomes — and
the G6 fixtures it must satisfy. It imports no engine module and reads no study seed, so the gate
runs before a cell exists.

The layer reproduces the house scorer rather than reimplementing it by memory. `score` iterates one
cell per (source, vocabulary target) with the source-equals-target cell held at label zero, and the
tests compare it with `acquisition_baselines.score` in both shapes to 1e-6 on three random fixtures.
Writing that comparison caught a real interface fact: the house scorer intersects the vocabulary, so
it requires a set and raises on a list. The harness accepts either and normalises.

G6 fires on six cases: world-majority passes; self-majority at 0.60 withholds as *not a transfer
result*; unattributed at 0.75 withholds as *not attributable*; an empty positive margin is *not
evaluable* with null shares rather than zeros; the boundary withholds at exactly 0.50 and does not at
0.4999; and a tie is self-majority. A seventh case is the one that keeps the others honest: relaxing
the threshold to 0.90 must stop the 0.60 fixture from withholding, so the fixture is what drives the
outcome. `tests/test_functional_structure.py` adds the meta-check — replacing the rule with one that
never withholds must make the gate raise.

The engine binding is not written. A design seed has not been scored and the harness is not complete;
what exists is the part that can be proved before the expensive part runs.

## §113 A stop rule that forbade its own precondition

§10 said no cell of any block may run until the harness and its gates are committed and the design
block has passed. The design block is five seeds; it cannot pass without running them. The rule was
written to keep the endpoint out of reach, and what it actually did was make step one unstatable:
either the design run is a violation of the protocol, or the protocol's own gate is unreachable.

The fix is to say what the blocks are for, in order, rather than to name one condition that covers
both. Step one builds and commits the harness and proves the gates fire. Step two runs the design
block only, and is explicitly an instrument audit: liveness, denominators, the harness-can-fail
control, instrument neutrality, the recorded disqualifier status. Step three is the confirmatory
block, and it is conditional on step two, which is what the original sentence was reaching for.

The substantive clause is the one about what a design seed may produce. A design run still computes
scores — a liveness gate needs a readout to be live, and a denominator gate needs a denominator — so
"scores are not read as a result" cannot be left as a promise. §10 now says the endpoint of §4 is
**not formed** on a design seed: no `delta` against the strongest baseline, per seed or pooled, and
no design number quoted outside a gate diagnostic labelled as one. §11.5's disqualifier status is
the single exception, because the amendment pre-commits recording it; it is recorded as a wiring
check, not as a share.

This is the second wording defect found in the same part of the protocol, and both were the same
kind: a sentence that reads as strict while removing the ability to execute it. The guard is a
three-line ordering assertion, because the defect is invisible to a careful read — the sentence
looked like exactly the discipline it was undoing.

## §114 Built, gated, and the rule it was built to enforce is broken

The engine binding exists: one formation run per design seed, the calibrated readout frozen at
the end of 110 cycles, both windows of §2 scored, gates G1–G5 around the instrument. The design
block ran once, on `20270201`–`20270205`, in 164 seconds, and passed every gate. That is the
first half of this note and the less interesting half.

The second half is what the wiring reported. The disqualifier of §11.3 wants, for every realised
held-out cell the readout improves, a share of that improvement carried by self-sourced support,
and it withholds when that share reaches 0.50. On the first design seed the primary window's
positive-margin cells split 7 world-majority, 113 self-majority,
291 unattributed; the co-primary window splits 0, 113,
291. Both withhold.

The co-primary result is not a surprise about this world — it is a consequence of what that
window *is*. The 32 withheld relations are withheld from formation, so no formation record can
carry them as world transitions; the provenance map holds 13 of them and all 13 are sleep rows.
Every improvement the readout makes on those relations is therefore unattributed **by
construction**, the unattributed share is 1.0 before a single number is read, and the rule
withholds on every world. The instrument is not broken; the rule, applied to that window, cannot
return anything else. §11.5 defined the co-primary window and the share separately and this
interaction was not followed through.

The primary window is the same defect in weaker form. All 96 available relations are recorded,
but the margin concentrates on the rare pairs — the same cells that carry the transfer window —
so 291 of 411 positive-margin cells are unattributed.

Three ways out exist and every one of them is a re-scoring: lower the unattributed threshold
(forbidden by §4's spirit and by rule 19's logic), drop unattributed cells from the denominator
(after seeing that they dominate), or exempt the co-primary window from the unattributed clause
(after seeing that it always trips). None is taken here. The harness, the protocol's constants,
the seeds and the bar are unchanged; no confirmatory seed has been generated, fitted or scored;
and the decision is recorded as the owner's, because it is an amendment to a rule committed
before the numbers existed.

What the design block was for is exactly this: the §10 sequence put the instrument ahead of the
endpoint so that a defect in the *rule* could surface before the one confirmatory run rather
than after it. It did.

## §115 A status about the measure, and a lock that claimed more than it kept

Two corrections to §114, both found by reading the artifact rather than the prose.

**The transfer limb's status is now recorded in the terms it can actually be stated in.** Not
"transfer failed", not "no transfer": *not attributable under the current provenance measure*. The
co-primary window's relations were withheld from formation, so no world row could have carried
them. The record shows this cleanly across the five design seeds — 96 of 96 available relations
present, 92–96 world-majority; 12–16 of 32 withheld relations present, 0–0 world-majority.
Sleep-only pairs are self-majority by §11.3's definition, absent pairs are unattributed, and the
rule withholds on either. The unattributed share is above 0.50 before a score exists.

That distinction is the whole point of the entry. A withholding rule that cannot fire on a claim
says nothing about the claim; treating its output as a negative result would be exactly the
mistake Phase L's degeneracy audit was built to prevent, one level up. The limb is scored, and what
the score would mean — were it attributable — is not answerable here.

**The lock claimed more than it kept.** §10 said the endpoint is "not formed" on design seeds. The
wiring step computes Organica's and the baseline's loss on every realised cell of both windows and
subtracts them, because §11.3's share is defined on that difference. Those per-cell differences
are the endpoint's building block; they exist, and saying they did not was false. What the lock
actually keeps is the statistic and the verdict: no pooled `delta`, no comparison with §4's bar on
a design seed, no direction. The protocol now says that, the artifact has `endpoint_boundary` with
the two lists, and the numbers the design block produced are labelled **endpoint-derived
diagnostics**. Fixing the sentence in the safe direction — narrowing the claim — is a defect fix,
not a re-scoring, and it is disclosed here and in the manual.

**The recommendation, flagged as the owner's decision.** Run the confirmatory block. §1 asks about
held-out prediction, not transfer; the co-primary was added to ask whether a margin survives on
unseen relations, and that question is unanswerable under this measure whether or not the block
runs. Not running leaves §1 unmeasured too. What the run cannot do is support the word transfer,
and a report of it must say so on the first line rather than in a footnote.

## §116 Two sentences that could not both be true

§10 step 2 said the disqualifier could not make or withhold a claim on a design seed. §10.1, three
paragraphs later, reported that it withheld. §10.2 said the co-primary unattributed share was above
0.50 "before any score is read", when the share is computed from per-cell paired losses and those
losses had been read, by the code and by the write-up.

Both are the same defect: a sentence written to keep the endpoint out of reach, describing a
boundary the measurement cannot have. §11.3's share is a ratio over paired losses. There is no
version of the diagnostic that does not require them, so there is no version of the design run that
does not compute the endpoint's building block. The honest boundary is on the statistic — the
pooled `delta`, the comparison with §4's bar, any direction — and it was already operating; what
was wrong was the description of it.

What is now recorded, in four lines in §10.3: computed, per-cell paired losses for both arms on
realised cells of both windows, plus window and tuning losses; withheld, the pooled `delta`, the
bar comparison, direction, and every confirmatory statistic; inspected, those losses, by the
attribution, by G3 and by this document; concluded, that the current measure cannot certify the
co-primary claim, a statement about the instrument that the coverage counts support on their own.

One consequence is worth naming, because it is why the distinction matters rather than being
pedantic. A lock announced as absolute invites a reader to assume that a diagnostic built on the
locked quantity cannot have been run — so the finding of §114 would look like it came from
nowhere, or worse, like it came from a rule the record says was never applied. The reconciliation
is what makes the finding traceable to a measurement instead of an inference.

For the record: the transfer measure's status is `not attributable under the current provenance
measure`; a design-seed status is labelled an instrument reading in the artifact
(`verdict_on_the_study: false`), because no confirmatory claim exists yet for it to withhold; and
nothing in the correction changes a threshold, a score, a seed or a gate.

## §117 The confirmatory run: no detectable advantage on the whole window, a large one where it cannot be certified

The block ran once, on `20270206`–`20270220`, n = 15, in 432 s. Every seed chose the
same baseline family on its tuning split, so one comparator supplied the bar throughout.

**Primary: no improvement detected.** Pooled `delta` -0.003818 nats, interval
[-0.010802, 0.002863] over 10000 cluster-bootstrap resamples. Per-seed deltas
span -0.027099 to 0.015468 with both signs present, so this is a null
result and not a near miss: the formed structure did not beat a tuned bigram on held-out prediction
by a detectable margin.

**Co-primary: -0.359327 nats the other way, and not a transfer result.** The interval
[-0.369382, -0.345823] lies entirely below zero, so the readout is much better than the
baseline on the withheld relations. The attribution then returns `not_attributable` — world
0.000000, self 0.299193, unattributed 0.700807 — which is the outcome §10.2 predicted
before the block ran, for the reason it gave: those relations were withheld from formation and
cannot acquire world-source support. The transfer claim is withheld.

The asymmetry is the finding, and it needs care rather than enthusiasm. The engine's readout is far
better where the world's combination was never shown, and indistinguishable where it was. Two
readings are available and only one is supported: (a) the readout carries an inductive advantage on
the withheld relations that a counting baseline cannot have, or (b) the readout is better wherever
the baseline is starved of counts, which is the same statement with no advantage at all. The
provenance share cannot separate them, because it is exactly the measure whose blind spot is these
cells. What can be said is narrower and still interesting: the advantage is concentrated on the
cells the baseline cannot count, and it is large there.

**What is not claimed.** No transfer; no equivalence; no statement that the engine forms nothing
useful. The primary window's own margin is 0.698500 unattributed, so the
diagnostic cannot certify that one either. The closed reusable-knowledge study is untouched, and its
transfer failure is neither confirmed nor reversed here.

**The process point.** The design block earned its place: it found that the co-primary could never
be attributed before the confirmatory run spent itself, and the run then produced exactly the
outcome the audit predicted for that limb. The verdict language was fixed in §4 and §9 before any
number existed, and it has not been re-read since.

## §118 Closing the record: statements written before the run

The result is frozen. Nothing here touches it, and the freeze is now a sentence in §10.4 rather
than an intention: no re-run, no seed added or dropped, no threshold, constant or gate adjusted in
the light of the numbers.

Two statements had not caught up, and both fail the same way as §116 — a sentence that reads as
discipline while describing a state that has passed. **§11.4**, written with the amendment, said
"No cell has run, and none may run until the harness and these definitions are committed
together". True when written, false by the time anyone would read it next. It now says it in the
past tense and points at the two records, so a pre-commitment clause cannot be mistaken for a
claim that nothing happened. **The harness docstring** said the endpoint's losses are "not
computed, not printed and not stored" on a design seed. §10.3 had already corrected that in the
protocol and the docstring had not — which matters more, because the docstring is what a person
reads immediately before running the file.

Two further sentences were stale for the same reason and went in the same pass: the status header
still said the engine binding was not built, and the docstring described a design-only module. All
four are corrections of description, not of measurement: no number, threshold, seed or gate
moved, which is exactly why they could be made after the run without re-scoring it.

The pattern across §115, §116 and §118 is the same defect three times: documents written to
constrain a future, and then the future arrives. Each correction narrowed a claim rather than
widening a permission, and each was disclosed in the manual the same day. A record allowed to
drift once the numbers exist is not a preregistration, so the drift is repaired in the open.

## §119 The record becomes a manuscript section

The benchmark is closed and the finding is stated in the three terms it can bear: **primary**, no
improvement detected over the tuned baseline, with an interval crossing zero and per-seed margins
carrying both signs; **withheld relations**, a large favorable score that is **not attributable**
under the preregistered provenance measure, so no transfer claim in either direction; and **no
further runs, no threshold changes**.

Paper 01 now carries it as §4.10, positioned as the test the acquisition study could not reach: a
capacity where structure actually forms, a baseline tuned on a split excluded from its fits, a
decision rule committed before the harness existed, and an audit of that harness on design seeds
whose scores were not read as a result. The section reports the design block's five gates, the one
confirmatory run, and the provenance result with its two surviving readings — an inductive advantage
a counting baseline cannot have, or an advantage that exists only where counting is starved. The
paper does not choose between them, because the instrument that would separate them does not exist.

Two claim-status rows were added rather than folding the result into an existing one: *an advantage
on held-out prediction at capacity 1,000* is **not established**, and *transfer on withheld
relations* is **not established** with the reason attached. Neither is a refutation, and the paper
says so in the vocabulary the project fixed for exactly this purpose.

The publication index records the same two rows and updates Paper 01's status only. **V2 design
stays deferred** until the manuscript states plainly what V1.1 did and did not demonstrate — which
§4.10 now does; the deferral is the owner's sequencing, not a conclusion of this entry.

## §120 The structural-contribution question, fixed before a harness exists

The frozen study left the project with a gap it could not close with the instrument it had. The
withheld relations showed a large favorable score and the provenance measure could not attribute
it, because relations withheld from formation cannot carry world-source support — a property of
the measure, not a verdict on the engine. One question survives that, and it needs no provenance
row at all: **is the advantage carried by which edge is where?**

The draft in `docs/STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md` answers it by ablation. Four arms,
one formation stream, one scoring rule: the full readout; the same readout with an empty edge table,
which is the base-rate backoff and is checked to equal `m(b)` rather than asserted; a
degree-preserving rewiring of the same table; and the tuned bigram. The edge-removed arm measures
the contribution of having edges at all. The rewired arm measures the contribution of the pairing.
The bigram sits beside the criterion, not inside it, because a degree-matched graph can beat a
tuned bigram as easily as a learned relation can.

The rewiring rule is the part that had to be written first, and it is written as code rather than
described: Maslov–Sneppen double-edge swaps, ten attempts per edge, targets exchanged and
weights left with their sources. That preserves the node set, the edge count, per-source out-degree,
per-target in-degree and the weight multiset, and it does **not** preserve the pairing or, therefore,
each row's total weight. The asymmetry is deliberate and disclosed: `W(a)` is not one of the
structural statistics this graph declares, and preserving it would mean preserving something no
one claimed as structure. Twenty-five draws per seed, mean pre-specified, the best draw never used,
the draw distribution reported so a mean cannot hide a bimodal set of graphs.

Two things in the draft are there to stop it flattering itself. First, the control is gated: if more
than a fifth of the `(source, target)` pairs survive the rewiring, the graph is too close to the
original for the comparison to mean anything and the study stops. Second, the outcome table names
all five combinations of the three bounds before a number exists, including the one that would
require the current interpretation to be rethought — content mattering against a rewired graph
while edges in general do not help. That row is the hardest to explain away later, which is why it
is fixed now.

None of this reopens the frozen study. Its finding stands in three statements, its numbers are not
re-read, and the draft says so. The seeds are fresh (`20270301`–`20270305` design,
`20270306`–`20270320` confirmatory), the bar, the table and the rewiring rule are frozen in the
text, and no harness is built. The order is the one that worked before: fix the rule, build and
audit, spend the design block, and only then the one confirmatory run.

## §121 The control the protocol required cannot exist on the readout it was written for

The design block did what a design block is for. Five fresh seeds, four arms, two windows, and the
gates of §8 ran before any contrast was formed — and **gate S3b failed on all five**, not because
the rewiring code was wrong but because the graph it was written for does not have the shape the
rule assumed.

The formed readout is dense. On seed `20270301` it has **333 edges over 24 source tags and 17 target
tags**: `86–87 %` of every pair those tags could form. A Maslov–Sneppen swap exchanges two targets
and refuses the exchange if the resulting pair already exists — and on this graph almost every
exchange produces a pair that is already there. Of 2,000 attempts on that seed, **1,631 were refused
for a duplicate**, 161 for a self-loop, 81 because both edges left the same source and 118 because
both arrived at the same target; **nine swaps landed**. The rewired arm came out `0.954407`–`0.960961`
identical to the full readout across the five seeds, against the `0.20` the gate requires.

The deeper point is not the algorithm. A perfect, fully-mixed sample from the degree-preserving
space would retain about `0.82` of the pairs, because with 17 targets and a mean out-degree near 14
there is almost nothing left to vary: `Σ kₐ² / T / edges ≈ 13.9 / 17`. **The rule and its gate are not
mutually satisfiable at this density**, so the "rewired" arm cannot be a control here whatever
samples it — which is exactly the failure AGENTS rule 13(a) calls a dead design: a gate that cannot
fire is decoration, and a control that cannot differ is the same thing wearing a different name.

What the audit did *not* find is a broken measurement. Gate S3c's oracle plant — a readout built
from the scored window itself — separated cleanly: `0.378707` against `0.487589` for the edge-removed
arm and `0.443569` for the rewired arm. The harness detects a contribution when one exists, and it
detects it through the two ablations that could not be built here. S1, S2, S3a (`max abs gap 0.0`),
S4, S5 and S6 passed on every seed; the edge-removed arm was verified to be the base-rate backoff
rather than assumed to be, and the draw determinism and weight/degree invariants held for all 125
graphs.

Two corrections were made during the audit and both are disclosed. The first pass failed S2 on an
arithmetic error of mine — the expected cell count used the pair count where the frozen protocol
uses the summed context tags, halving the denominator — corrected and the block re-run, with no arm
loss or other gate outcome changed. The record also gained the two density fields the argument
needs.

No contrast was formed, no outcome row was read, and no confirmatory seed was generated. The arm
losses in the artifact are labelled gate diagnostics for that reason, and they are not a result in
either direction. Two amendments would make the question answerable — a weight-level null that keeps
the pairs and permutes which one carries which weight, or closing the study at the identifiability
limit — and both are stated in §12.4 as the owner's decision. Neither the frozen study nor its
numbers moved, and the second-world-family clause is now §11: a result here would be a result about
one world family, and a broader claim needs its own preregistration.

## §122 — The structural-contribution study is closed at the design gate (2026-11-02)

The decision on §121's open question, recorded before any further number was computed.

**The decision:** keep the preregistration unchanged and close the study at the failed design gate.
No confirmatory run. The owner's reasons, in their own structure:

1. **The density finding is the result.** The readout is too close to a complete bipartite graph for
   the preregistered degree-preserving rewiring to produce a sufficiently different control.
2. **The 20 % overlap limit is not relaxed.** Relaxing it after seeing that the control failed would
   turn a failed control into a different experiment — the bar would then have been set by the
   result it guards, which is the one thing §10 and the repository's threshold rule exist to prevent.
3. **The weight-level shuffle is not substituted into this study.** It preserves every pair, so it
   tests whether edge *strengths* matter rather than whether the learned *pairings* matter. That is a
   worthwhile and different question, and it needs its own preregistration and success criterion. If
   pursued, the owner's design is to shuffle weights **within each source row**, preserving `W(a)`
   together with the topology, so the test isolates which existing pair carries which strength.

So the record is: stopped at **S3b**; topology-level contribution **not identifiable with this
readout and null**; **no confirmatory result**; nothing spent. This is the outcome §10's stop rule
was written to produce — a design that cannot build its own control, found before the confirmatory
seeds were touched, and closed rather than amended into a different experiment.

Two things it is not. It is not a null about the formed structure: no contrast was formed, so the
question is *unavailable*, not answered against. And it does not reopen anything frozen — the
functional-structure study's §10.4 result stands, and no transfer claim exists in either direction.

The edge-strength question is now named and deliberately not opened. If it is opened later it gets
its own document, its own gates and its own seeds; the formulation above is recorded so it does not
have to be reconstructed from this one.

## §123 — Paper 01's submission package is built and checked; the upload is the owner's (2026-11-02)

The owner's decision was to stop adding internal experiments and put V1 in front of reviewers,
Paper 01 first. This entry records what "submission-ready" turned out to require, and what it
does not include.

**Rendering found eight defects, all in the build, none in the manuscript.** `pdflatex` was not
available in this environment; pandoc 3.5 and TinyTeX were installed into the home directory and
the committed pipeline was used unchanged apart from the fixes below. The first build produced a
23-page PDF that was wrong in ways only a log and an extraction check show: the title typeset
twice (once as a numbered section, 61 pt into the margin), LaTeX numbering the headings on top of
the manuscript's own numbers, ten `\texttt` paths that were single unbreakable boxes (the widest
140 pt into the margin), a fatal microtype error without scalable fonts, and — the one that
mattered most for a deposit — **no Unicode map**, so the text did not extract: **0 of 34** section
signs survived and "confirmed" extracted as "con rmed". `\input{glyphtounicode}` plus
`\pdfgentounicode=1` fixed it: 34 of 34, and "confirmed" intact. The final Paper 01 build has
**0** LaTeX errors and **0** overfull boxes.

**The evidence check found a real gap.** The deposit's software record was archived at `v0.10.0`,
and Paper 01 §4.10 — added after that tag — cites
`docs/functional_structure_confirmatory.json` and `docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md`.
`python benchmarks/deposit_bundle.py --check` therefore reported **38 cited, 2 missing**: the
deposit could not have carried the evidence its own manuscript cites. The fix is not to drop the
citations. The record is now archived from the commit at version **0.11.0**, with the resolved SHA
in the manifest; **no tag or release is cut**, because tagging is the owner's act. The check now
returns **38 of 38**.

**What is built.** `.scratch/deposit/` holds the software archive
(`project-organica-v0.11.0.tar.gz`), the Paper 01 record (manuscript as PDF and Markdown, five
figures as vector PDF, `SHA256SUMS`, `DEPOSIT-MANIFEST.json`) and the Paper 02 record (manuscript,
PDF, three figures, checksums), plus the top-level manifest carrying the commit and the
cited-artifact check. `tests/test_paper_numbers.py`, `tests/test_svg_to_pdf.py`,
`tests/test_readout_tables.py` and `tests/test_doc_placeholders.py` pass (121 tests), so every
number in the rendered manuscript is still checked against the artifact it came from.

**What is not done, and cannot be from here.** The upload. A Zenodo deposit mints a public DOI,
and that is the owner's account and the owner's act; nothing in this repository publishes. Paper
02 renders (14 pages, 0 errors) and is bundled, but its wide audit tables still overrun the margin,
which is the next typesetting task rather than part of Paper 01's package.

## §124 — Paper 02 is typeset clean, and both papers travel with a reproduction bundle (2026-11-02)

Paper 02 carried 21 overfull boxes, all in four tables. The cause was one line in the render
escape: `make_code_spans_breakable` returned every span without a `/` unchanged, and the
acceptance-criteria table is three columns of test names — single 40-character tokens with
no slash in them — so the column had no break opportunity at all and the widest row ran
**209 pt** into the margin. The rule now turns on length rather than shape: over 24
characters is broken between characters, as `\seqsplit` does, and shorter spans break only
at a slash or an underscore escape.

Two tables could not be fixed by breaking. Pandoc divides the measure evenly, so the
nine-column ancestry table gives each column 41 pt while its header says "Reachability",
which is 58 pt of word. No portrait size that is still readable recovers a 40 % shortfall, so
tables of seven columns or more are now set on a landscape page (`pdflscape`), where the same
fractions have room. The threshold is seven, not six: Paper 01's two six-column tables set
perfectly well in portrait, and rotating them cost three pages for nothing. A 103-character
comment line in Paper 02's script block — 61 pt over — is set at `footnotesize` rather than
wrapped, because a wrap in a block a reader may copy is a line break that is not in the
command, and shortening the comment would be editing the manuscript to fix a rendering
defect.

**The result:** Paper 02 renders to 17 pages with **0** LaTeX errors and **0** overfull
boxes, two of those pages landscape; Paper 01 is unchanged at 23 pages, 0 and 0. Both PDFs'
text extracts without broken ligatures and with the section sign intact.

**The reproduction bundle.** `benchmarks/deposit_bundle.py` now builds a fourth bundle that
is not a Zenodo record: `reproduction/` carries `REPRODUCE.md`, `ENVIRONMENT.json`, both
PDFs and `SHA256SUMS`. It names the archived commit (a version string does not check out and
a commit does), the Python, pandoc and pdfLaTeX versions that built the papers, the four
commands that regenerate the figures and the PDFs in order, each paper's expected page
count, size and hash, and what the bundle does **not** reproduce: the experiments, whose
numbers are frozen in committed artifacts, and the upload. `tests/test_deposit_bundle.py`
grew from three bundles to four and asserts that the PDFs it carries are byte-identical to
the ones the paper records list.

## §125 — The deposited PDFs carried no title in their own metadata (2026-11-02)

The two PDFs were read as files, not as sources, and both opened with `/Title`, `/Author`, `/Subject` and
`/Keywords` **empty** — only pdfTeX's producer string and hyperref's creator line were set. The words were
all on page 1, which is why nothing had caught it: a manuscript can look complete and still arrive
untitled. What an empty Info dictionary costs is not cosmetic. A viewer's title bar, a reference manager's
import, and the metadata block a preprint server or repository displays all read those four fields, so the
deposited artifact would have been filed as an untitled, unattributed document whose searchable record
said nothing about what it was.

The cause is that hyperref sets none of them unless it is asked. The tempting one-word repair is the
`pdfusetitle` package option, and it is wrong here: it copies `\title` and `\author`, this template's title
is a `\parbox{0.86\textwidth}`, and the metadata would have received the markup instead of the words. The
values are therefore passed explicitly — `PDF_INFO` in `benchmarks/render_papers.py` carries a title,
subject and keywords per paper, the plain author name is taken from the `**Author:**` line before the ORCID
and address are typeset into it, and the template sets all four with `\hypersetup`.

The check matters more than the repair. `verify_pdf_info` reads the four strings back out of the built
PDF — pdfTeX writes the Info dictionary uncompressed as literal strings, so a reader for its escapes is a
dozen lines of standard library and no new dependency — and raises if any of them is missing or different
from what was asked for. It was made to fire on a deliberately wrong title before it was trusted, because
a check that has only ever passed is a check that has not been tested. Both papers then rebuilt identically
in layout: **23** and **17** pages, **0** LaTeX errors, **0** overfull boxes, with the same 34 of 34 section
signs extracting and the same figures in the same places.

One thing this does **not** establish, and the pipeline document now says so where a reader will meet it:
nothing in this build has ever rendered a page to an image. The log says there are no overfull boxes and
the extraction says the words are there, and neither is a person looking at the page — so figure placement,
caption collisions, page breaks, and Paper 02's two landscape tables remain **unverified visually**, and are
recorded as such rather than as passed.

## §126 — The PDF title could drift from the paper's own title (2026-11-02)

Setting the document properties moved the title into a second place. The manuscript's level-one heading still
says what the paper is called, and `PDF_INFO` says it again for the PDF, so a future retitle would have to
remember both — and a stale half looks exactly like a correct one. The cheap guard is to stop keeping the
second copy independent: `verify_title_matches` derives the expected title from the heading, strips the
project's "Paper N:" label (which is the repository's name for the manuscript, not the paper's name), and
fails the build on a mismatch before pandoc or pdflatex run. The heading is the source of truth, so the
repair when it fires is either the heading or `PDF_INFO`, and the message names which.

It was made to fire on a deliberately stale title before being trusted, and `tests/test_pdf_titles.py` keeps
that case alongside the two assertions that both papers currently agree and that the declared titles are
distinct. Both PDFs then rebuilt byte-identical to the previous build (385,296 and 302,835 bytes), which is
the point: a guard that changes nothing about the artifact it guards.

## §127 — The deposit records named the papers by titles the papers do not carry (2026-11-02)

Two records had drifted in the one field a citation prints. `zenodo/paper-01-preprint.json` said
*"Developmental structure formation in Organica 1: a preregistered account of what the engine grows, and what
it does not"*, and `zenodo/paper-02-preprint.json` said *"Persistent structural provenance in Organica 1: what
survives, what is reconstructable, and what is not"*. Neither string appears anywhere in the PDF it describes:
the documents carry *Developmental Structure Formation in Organica 1* and *Reconstructing Evidence and
Selection from Organica's Surviving State*. The record is what a DOI resolves to and what a reference manager
imports, so the drift would have published two papers under names their own first pages contradict — the defect
§126 closed between the heading and `PDF_INFO`, one layer out, in the metadata that leaves the repository.

The repair keeps the descriptive phrase where it belongs. Both titles are now the documents' titles, and the
subtitle material lives in `description`, where it is not a claim about what the document is called. Paper 01's
description also predated §4.10 — it described the acquisition benchmark stopping at its gate and said nothing
about the confirmed capacity-1,000 test — so it now reports that result with its numbers: pooled margin
-0.003818 nats, 98.33 % interval [-0.010802, 0.002863] crossing zero, per-seed margins of both signs, and a
withheld-relation margin of -0.359327 that the preregistered provenance measure returns as *not attributable*,
so no transfer claim in either direction. A record that omitted that would have advertised the paper as older
than it is.

`tests/test_pdf_titles.py` now asserts that each paper's record title equals `PDF_INFO`'s, which is itself
asserted equal to the manuscript heading. The title therefore has one source of truth and two generated
dependents, and `docs/ZENODO-DEPOSIT.md` states the rule where a depositor will read it.

**And the pages, at last, were looked at.** A rasteriser (PyMuPDF in a scratch virtual environment — not a build
dependency; the build still needs nothing beyond pandoc and pdflatex) rendered all 40 pages of both PDFs to
images, and each was inspected. **Paper 01 is visually clean:** the page 4→5 boundary is table 3.1 closing and
table 3.2 opening with its header repeated, every table keeps its rules intact across the break, the
claim-status table repeats its header on page 16, and all five figures render as vectors with captions and
source lines. Its only blemish is cosmetic: page 9 leaves about a third of the sheet blank because Figure 2's
float could not fit beside its caption.

**Paper 02 is not clean, and its defects are layout, not content.** A fenced code block splits across pages 7–8
and leaves two orphaned lines above "4. Results". Page 12 carries the heading "4.3 Ancestry honesty (A3)" and
nothing else, because the section's table was moved to a landscape page. The two landscape pages (9 and 13) set
their table at the top of an otherwise empty sheet, with the page number rotated to the table's orientation, and
neither carries a caption — and no table in the document has a numbered caption, which for a paper whose tables
carry its results is the defect that matters most. All of it is downstream of `landscape_wide_tables()`, which
exists because the acceptance-criterion table otherwise ran 209 pt into the margin: that fix removed the overrun
and cost the section flow. Two suspected defects were checked and dismissed — the text blocks that appear to
overrun the page box are the rotated page numbers, not overflow.

Paper 02 stays labelled unverified visually until those three are fixed and looked at again, and a human
confirmation of the renders is still owed for both papers.

## §128 — Paper 02's three layout defects were all one decision, and fixing it properly took three attempts (2026-11-02)

The 40-page review in §127 found three defects in Paper 02 and located all three downstream of one
function. This is the repair, and what it cost.

**One cause.** `landscape_wide_tables()` existed because pandoc divides the measure evenly, so the
nine-column ancestry table gave each column 41 pt at 11 pt while its header word "Reachability" is
58 pt, and the table ran 17 pt into the margin. Wrapping it in `pdflscape`'s `landscape` environment
removed the overrun. `pdflscape` breaks the page at both ends of that environment, and every defect
the review found follows from that single property: the `4.3 Ancestry honesty (A3)` heading was
typeset at the foot of the portrait page and its table began the next, because the break came
immediately after the heading; and each three-row table sat at the top of an otherwise blank rotated
sheet whose page number was rotated with it. The table never needed a wider page. It needed a smaller
size, and the page break was the price of getting one.

**The measurement that settles it.** Nine columns at `\footnotesize` with `\tabcolsep` at 4 pt gain
32 pt of text over the original setting, and the widest header word is 38 pt in a 43 pt column at
`\scriptsize`. Nothing is dropped, no column is merged, and the table stays in the running text.

**Two of the three attempts were wrong, and the second was wrong in the way that matters.** The first
portrait attempt applied `\footnotesize` to every wide table and produced exactly one overfull box:
`Reachability`, 4.31 pt over, because a p-column cannot hyphenate a word into a width with no room
for any of its pieces. Size is now a function of column count — seven and eight columns get
`\footnotesize`, nine or more get `\scriptsize` — which is a rule about the measure rather than a
patch for one word. The second attempt kept the heading with its table by putting a `\filbreak`
before the heading, and the rebuilt PDF still had the heading alone at the foot of page 9 with its
table overleaf: `\filbreak`'s −200 penalty is a *suggestion*, the heading fitted where it was, and
the break between the heading and the table's first row won. That is the same defect the landscape
pages were traded for, reintroduced by a plausible-looking primitive. It is only visible in a render.

**What works.** `\keepwithnext{110pt}`, in the template, measures the space left on the page and takes
a forced break before the heading when the heading and table cannot both fit — the technique
`needspace.sty` uses, written out because that package is not in this TinyTeX installation. Applied
to both wide tables, both headings now sit on the same page as their table (8 and 10), verified by
locating the heading and the table's first column in the extracted text of each page rather than by
eye. Code blocks are set with fancyvrb's `samepage=true`, so the reproduction block that split after
its eighth line now sits whole on page 8.

**The result.** Paper 02 goes from 17 pages to **14** — the three pages that landscape cost are gone —
with 0 LaTeX errors and 0 overfull boxes, no landscape page, no page under 120 extracted characters,
and no page whose last line is a section heading. Paper 01 is byte-identical at 23 pages, 0 and 0:
it has no table of seven columns or more, so nothing in this pass touches it.

**Two defects were found while looking and are not fixed, because neither is layout downstream of the
landscape decision.** First, every figure carries *two* captions: pandoc's `implicit_figures` gives
each image a numbered caption from its alt text, and the manuscript also carries its own bold
`**Figure N.**` paragraph, so the page shows "Figure 2: Figure 2. The self-sourced share…" above the
author's real caption. The fix is a pandoc reader flag, but it changes figure placement in **both**
papers — Paper 01 would need its 23 pages re-reviewed — so it is not a Paper 02 edit. Second, Figure
3's annotation text is clipped at the image's right edge: the figure PDF's page is 810 pt wide and its
extracted text reaches x = 812.3, but the visible cut is well inside that, so a clip region in the
figure is cutting a sentence mid-word. That lives in `benchmarks/figure_papers.py` and
`benchmarks/svg_to_pdf.py`, not in the manuscript.

Paper 02 remains **unverified visually** by this repository's own standard: the defects were found by
looking at renders, the fixes were confirmed by looking at renders, and the owner's confirmation is
still what turns "checked here" into "verified".

## §129 — A reviewer's revised report on Paper 01 was checked item by item: three real defects, one misreading (2026-11-02)

The report's seven prioritized revisions were each checked against the code and the
committed artifacts rather than adopted.

**1. The tuning split. The report is right that the manuscript contradicts the
preregistration, and wrong about which side is wrong.** The preregistration contradicts
*itself*: §3 says the last 15 formation cycles are "excluded from every fit", while §11.1
says "those cannot both hold" and adopts the other reading — configurations are fitted
without the split and ranked *on* it, then the winner is **refit on all 110 cycles**.
`comparator_sweep` does exactly that (`fit_rows = rows[:-TUNING_CYCLES*EVENTS_PER_CYCLE]`,
then `fit_bigram(rows, ...)` for scoring). The manuscript's clause — "the tuning split was
excluded from *selection* only" — misdescribes both halves: the split **is** the selection
signal, and it is **not** excluded from the final fit. It now states the two-stage
procedure, notes that the refit gives the baseline the larger sample and never the smaller,
and records that §3's restatement is superseded by §11.1. No value, gate, bar, seed or
outcome changes, and the deviation cannot favour Organica.

**2. The crossing is a grid location, and the paper said so only obliquely.** The report is
right: `crossing_index` returns the first sampled index at which DI > PI, so `[5.0, 5.0]`
is an interval over sweep positions. §4.4 now states that the data place the crossing
*between 2:1 and 3:1*, that 3:1 is the first sampled point above parity (0.706 against
0.039), and that this is not an interpolated threshold estimate.

**3. The Phase L amendment was not in the manuscript.** Amendment 2 (2026-10-25, committed
before the primary axis ran) replaced a stated 98.33 % interval — α = 0.05/3, Phase K's
factor carried over into a five-arm phase — with **99 %**. Now recorded in §3.5, with the
fact that Phase K's own 98.33 % figures are unaffected.

**4. The seed-exchangeability audit was already an instrument audit, and the report asks
for what it already is.** `docs/phase_l_results.md` §7.1 reports that thirty fresh,
non-consecutive seeds at 6:1 landed on the pooled value (DI 0.7241 against 0.7148,
*p* = 0.60) and that the fresh set's own arbitrary half-split carried the opposite sign —
so the n=10 curve was an unlucky high draw, not a seed-block artifact. It changes no
criterion and no verdict; the manuscript now carries it under that label, with its numbers.

**5 and 6. The missing evidence tables were added, to the extent the record supports them.**
§4.1 now carries the one quantitative curriculum contrast in the record (core baseline 91
vs `_burst_30` 128 at 1,200 cycles, seed `20261023`; 119 at 600), states that the 1,200-cycle
extension was exploratory rather than preregistered, and says plainly that the remaining
schedule comparisons carry **no pooled effect size or interval** — which is why the paper
had none. §4.6 now tabulates Phase H, H-recovery, Phase I and Phase J with task, metric,
seeds and outcome, and names Phase H's fixed curriculum as the reason its ten seeds re-run
one stream rather than sampling ten worlds. §1.1 now states that the claim is **structure
formation**, not the project's stronger emergence criterion — which also requires use and
derivation from experience — and points at `docs/EMERGENCE-CRITERIA.md`.

**7. The figures were worse than reported.** `docs/figure_p01_displacement_curve.pdf` went
to press with **six** sweep points and no title: it was a stale render of an older version of
the figure, while the text and caption describe all eight ratios and the manuscript embeds
the **PDF**, not the SVG the generator writes. Three more figure PDFs carried text 2–9 pt
past the page edge — `Statis`, `(99%`, and a stray `9`. Two causes, both fixed: the PDFs
were rendered with a font substitution wider than Helvetica, and `figure_papers.py`'s
overflow guard estimated text width as `len(s) * size * 0.52`, which under-predicts
digit- and parenthesis-heavy strings by about a fifth. The guard now uses Helvetica advance
widths and refuses a label that would overrun; all eight paper figures were re-rendered from
the current SVGs at exactly the page sizes the committed files had (verified: every page
size matches, no span crosses the edge, all eight labels and the crossing annotation are
present).

**Two more figure defects turned up while fixing those, and both are general.** Every
figure carried **two** captions — pandoc's `implicit_figures` builds one from the image's alt
text, and each manuscript also writes its own bold `**Figure N.**` paragraph — so a page read
`Figure 2: Figure 2. Every adjacent step …`. And because the image was a float, it could leave
its caption behind: in the 25-page build Figure 2 was carried onto a page of its own, centred
under a quarter-page of white, while its caption stayed on the page before. `pin_figures` now
rewrites each figure as `[H]` (float.sty) and drops the duplicated caption, so one caption sits
directly beneath its figure. Verified on both PDFs: no page carries a doubled caption, and every
page with an image also carries the caption for it.

**The report's one misreading:** it says the deposit's Markdown links point at SVGs outside
the archive. `benchmarks/render_papers.py` rewrites every `../docs/*.svg` link to the PDF
beside it at build time (`IMAGE_RE`), so what ships and what is typeset are the PDFs.

**Cost.** Paper 01 now renders to **25 pages**, not 23 — the two added tables — with 0 LaTeX
errors and 0 overfull boxes. Paper 02 is unchanged at 14.

## §130 — The strength-assignment harness now passes its end-to-end audit, and it failed once first (2026-11-02)

The replacement for the closed structural-contribution study exists: `docs/STRENGTH-ASSIGNMENT-PREREGISTRATION.md`,
`benchmarks/strength_assignment.py` (the intervention, its invariants, its plants and its outcome
table) and `benchmarks/strength_assignment_harness.py` (the engine binding), with the design block
run on `20270401`–`20270405`. **No confirmatory seed has been read**; the block `20270406`–`20270420`
is untouched.

**The intervention.** Each source row's weights are permuted among that row's own targets. Node set,
edge pairs, out-degree, in-degree, every row's weight multiset and every row total are identical by
construction and asserted on every draw; only which target inside a row carries which weight changes.
That is the question the closed study could not ask, because its null had to change the graph while
preserving degrees and at this density those requirements are mutually unsatisfiable — 95–96 % of
pairs survived rewiring.

**It failed its first audit, and the failure was worth having.** S2 failed on all five seeds with the
readout unchanged while 90 % of edges moved. The cause was not the permutation: on the
**withheld-relation** window the readout is nearly all backoff — **372** realised cells, **6 (1.6 %)**
with a formed edge from source to observed target — so only six cells could respond to any
permutation, and 3 of 25 draws left the one informative weight in place by chance. Gate S2 had been
written as "every draw must change the readout", which is the wrong statistic for a random
permutation, and the window was the wrong window for this question — the closed study used the
withheld window because a counting baseline has no counts there, but a weight permutation needs
weights on the observed pairs, and on that window there are almost none.

**Amendment A1, pre-outcome and disclosed.** The primary window became the **full** held-out window
(cycles 150–200), the withheld window became a secondary diagnostic that gates nothing, and S2 gained
a **coverage floor of 0.50** — a design-identifiability floor, not a result threshold — while its
per-draw minimum became a reported quantity. Both changes were made with the coverage numbers
(1.6 % against 77.1 %) in hand, which the amendment states rather than presenting as anticipation.
The bar (lower bound of the 98.33 % interval on `d_shuffled` strictly above zero), the direction, the
four outcome labels, the intervention, the draws and the seed blocks did not move.

**The re-run passed every gate on every seed:** coverage **77.1 %–81.4 %**, median largest
probability change **0.0926–0.1125**, moved share **0.898–0.906**, **zero** draws that moved nothing,
and the layer's **11 fixtures** — including a negative plant with **nonconstant** weights whose
observation set is closed under the permutation, which changes the loss by **exactly zero** and fails
when that closure is broken (0.603 nats). The artifact carries `deltas: null`: the design block forms
no contrast and reads no label.

**One diagnostic is recorded rather than interpreted.** On `20270401` the full window scored
**0.433694** against a shuffled mean of **0.444691** — the shuffled assignment scored *better* by
0.011 nats on that one seed. It is one design seed, it is not the endpoint, and if it survives the
confirmatory block it lands in §6's fourth row, which was written before the number existed. Recording
it is the point: a design block that reports only its passes is a design block that has started
selecting.

**What this does and does not establish.** The harness now demonstrates, end to end and on the frozen
engine, that the intervention changes the intended variable and only it, that it can detect a
contribution that is present, that it can reach zero when the design is exchangeable, and that its
arms share one denominator and one engine run. It establishes **nothing about Organica**: the
confirmatory block is unspent, and a result there would still be narrower than a topology claim.

## §131 — The title page printed its own line breaks, and only a rendered page showed it (2026-11-02)

The owner's review of the Paper 01 deposit reported three visible defects on the **23-page** build:
literal `\\` between the author, ORCID and email on the title page; doubled figure captions
("Figure 1: Figure 1."); and Figure 4's right-hand panel clipped at the page edge.

**One of the three was still live.** The doubled captions were fixed when `pin_figures` stopped
pandoc's `implicit_figures` caption being typeset beside the manuscript's own (journal §129), and
Figure 4's page now runs x = 75.6–536.4 inside a 612 pt page with both panels complete — that defect
was the stale, font-substituted figure PDF, replaced when all eight figures were re-rendered.

**The author line was real, and it is the interesting one.** `prepare()` replaced each em dash with
`" \\ "` in the metadata, expecting a LaTeX break. Pandoc parses metadata values as markdown and
escaped the pair, so the title page printed the two characters: the build had done exactly what it
was told, and the instruction was wrong. Nothing in the log, the overfull-box count or the
placeholder scan could show it, because the page was not overfull, not missing and not templated —
it was simply wrong in the one place a reader looks first. Fixed with a sentinel (`@AUTHORBREAK@`)
that pandoc passes through untouched and `fix_author_breaks` replaces with `\\` on the build copy;
the build now **fails** if the sentinel survives, and `tests/test_author_line.py` asserts the
sentinel is used, that the rewrite produces a break, and that a surviving sentinel stops the build.

**Repackaged.** Both PDFs rebuilt (Paper 01 **25 pages**, Paper 02 **14**, 0 LaTeX errors, 0 overfull
boxes in each), the deposit bundle regenerated, `sha256sum -c` clean inside it, and the downloadable
archive rebuilt from the new files. Verified mechanically on both PDFs: no literal backslash pair on
a title page, no page carrying a doubled caption, no span past the right text margin, and every
figure page's drawing extent inside the page box.

## §132 — The scaling ladder: resolution or replication (2026-11-02)

**Question.** The owner's diagnosis was that the experimental unit may be too
small per run to separate a real structural effect from noise, and their
insistence was that scaling data per run is not scaling runs. That is answerable
without a larger experiment: from one world you can estimate the within-run
sampling error, and from several you can estimate the between-world spread. The
two are different numbers and only the first responds to a longer window.

**Protocol first.** `docs/SCALING-LADDER.md` §1–§6 were fixed before any cell ran:
the scaled unit is the **scored window** at constant 110-cycle exposure (a longer
formation stream is a different intervention and is not tested); the endpoint is
the paired per-event-pair log-loss delta against the strongest tuned comparator;
`rho` = within-run SE / between-world SD decides the verdict at ≤ 0.50, ≥ 1.00, or
between; the curve is expected at exponent −0.5 ± 0.15; and the required number
of runs is derived from `sqrt(between²/n + within²)`, reported as unreachable when
the within-run term alone exceeds the target.

**The curve (five fresh methodology worlds, 20270501–20270505).** Within-run SE
falls 0.008830 → 0.001450 as pairs grow 399 → 6,399; the fitted exponent is
**−0.577** (r² 0.928), inside the band. Between-world SD is 0.012157 at 1× and
0.010247 at 16×: sixteen times the data moved it 16 %, inside what five worlds can
resolve. So `rho` falls 0.726 → 0.296 → 0.276 → 0.243 → 0.142 for one reason —
the numerator shrank — and the between-world term, which is a property of the
worlds, does not respond to window length at all. Block-to-i.i.d. ratios of
0.54–0.85 rule out positive temporal clustering, so the per-observation error bar
was not optimistic.

**The verdict is "both", and the ordering is the finding.** At 1× the within-run
SE (0.008830) is 1.18× its own delta (0.007468) — a single run cannot establish
the sign of what it measured — and the derived n is **not reachable**: no number
of runs reaches half the between-world SD, because one run's noise already floors
it. From 2× on, `rho` ≤ 0.30 and 6.16 → 4.35 worlds suffice. Fix resolution once
(score ≥ 100 cycles), then spend on worlds. Running more worlds on the frozen
50-cycle window would multiply an estimate each run cannot resolve.

**What it does not say.** Not that the readout beats the comparator: at 16× the
delta is +0.004817 against a between-world SD of 0.010247 over five worlds, a
pooled SE of 0.004582 — about 1.05× the delta. One world (20270504) is negative at
every scale; 4 of 5 worlds and 15 of 20 quarters are positive. That is a
description of five worlds, not evidence of an advantage, and the between-world SD
is itself uncertain at n = 5. The 1× cell is also not the frozen world's 150–200
window: the law is held at LAW_R0 throughout so no generating process rotates
inside a scored window (declared in the artifact's caveats).

**A defect found while building it.** The first run scored nothing: `SCALES` gives
a window *length* (50 × factor) and `_pairs` takes an *end cycle*, so the 1× window
was `150 → 50` — empty. Empty per-pair lists then averaged to a `StatisticsError`,
which is the only reason it was not read as a null. The module now raises on an
empty window, because a dead axis that returns no observations looks exactly like
an axis with no effect (rule 13c).

**Consequence for the plan.** Any study whose margin is compared across worlds
carries seed-level noise of about this size on this endpoint — 0.011–0.013, so a
pooled margin over k worlds is ± ~0.012/√k, ~0.0031 at k = 15. That is planning
arithmetic on a different contrast, not a measured property of the
strength-assignment endpoint, and it is recorded as such.

## §133 — The sign criterion replaces the ratio, and the 100-cycle threshold survives on a different argument (2026-11-02)

The owner challenged §132's threshold: within-run SE over delta is above one at 100 and
200 cycles and first falls below at 400, so a ratio-based reading does not support 100. The
challenge is right that the ratio is not a criterion, and wrong that 100 cycles fails.

`SE/delta` is a t-statistic. Through the normal CDF the five ratios read **0.80, 0.82, 0.74,
0.79, 0.62**, so a ratio of 1.18 is not a run that cannot resolve itself - it is 0.80 - and
the 200-cycle row is worse than the 50-cycle row only because the *pooled* delta fell there
(0.003536 - 0.002085). That is a between-world movement in the numerator, and dividing it by
a shrinking denominator mixes the two scalings the ladder exists to separate.

`benchmarks/scaling_ladder.sign_resolution` answers the owner's question directly and costs
no seed: `--reanalyse` reads the stored cells of the same five worlds (20,000 replicates).
Both uncertainties are propagated - the run's own `se_block`, and the world's effect, drawn
from the widest scale **other than the one being judged**, so no cell is graded against its
own estimate and the 16x row is judged against 8x rather than against itself. The estimate
of P(a run reports its own world's sign) is **0.855 at 50 cycles (worlds 0.780-0.917; one of
five at 0.90)**, **0.977 at 100 (0.917-0.997; five of five)**, then 0.961, 0.974 and 0.944.
The relation is not monotone beyond 2x, and 0.95 would not be met by 2x (minimum world
0.917); both are disclosed rather than smoothed.

The second question is the one the ladder's between-world wall predicts. Agreement with the
**block's** sign is 0.694, 0.780, 0.761, 0.770, 0.720 - never above 0.78, and lower at 16x
than at 2x. One world's effect is negative, so a run inside it can be perfectly resolved and
still disagree with the average, and no amount of observing that world changes it. The two
scalings differ in **ceiling**, not only in efficiency.

**Amendment.** The recommendation stands at 2x (100 cycles); its justification is replaced
by the sign criterion. `docs/SCALING-LADDER.md` §8 carries the analysis; rows 1-7 and the
verdict are unchanged. This is a re-analysis of the same five worlds: it refines a
measurement decision and creates no evidence, and the third axis - changing the generating
configuration - remains untested.

## §134 — The sign estimator was audited against known truths, and the 100-cycle target is provisional (2026-11-02)

The owner accepted §133's distinction and challenged two things in the number it left standing: the 0.90
target was chosen after the ladder ran, and the reference estimate is not independent of the estimate it
judges, because the scored windows are nested. Both are correct in principle, and the second is the one
worth computing.

`benchmarks/scaling_ladder.audit_sign_estimator` (`--audit`, artifact `docs/sign_audit.json`) runs five
checks on the stored cells. **Nesting:** the judged window and its reference share 6.2 % to 50.0 % of the
larger window's pairs, a correlation of 0.164 to 0.562 under independent pairs (0.562 at 16x, where the
containment reverses and the judged window is the longer one). It does not bias `p`, because conditional on
a world's effect a run's error is its own and the reference's likelihood depends only on its own standard
error; it does make the five rows dependent comparisons, so the §8 curve is not a monotone dose-response
test. **Reference rule:** at 2x the probability is 0.976 with leave-one-out, 0.946 with a fixed 8x reference
and 0.898 with a fixed 4x one, clearing 0.90 for 5, 3 and 3 worlds. The "all five clear" statement is
therefore conditional on using the most precise reference available. **Calibration:** against known truths,
with reference cells carrying their own error and fresh runs drawn from the truth, the worst error is 0.068
over effects of 0.25-4 SE(1x), and it runs conservative for resolved effects rather than optimistic. The
zero-effect cells are excluded, not scored: with no sign to report the estimator returns 0.856 at 16x where
the realised frequency is 0.497, and that is kept as a diagnostic of the degenerate case rather than
counted as an error. **Threshold:** 2x clears 0.90 for five worlds and 0.95 for four; 1x clears 0.95 for
none.

**The audit found two defects in its own first version**, both of the kind the project keeps finding: the
nesting formula divided by the judged window's variance unconditionally and returned a correlation of 1.78
at 16x, which is impossible and was read as a finding for one run; and the zero-effect cell was scored as a
0.359 calibration error when the quantity is undefined. Both are fixed in the committed code, and both show
why the audit had to be a program rather than a paragraph.

**Status.** 100 cycles remains the recommendation (§133) and is now labelled **provisional**: a declared
convention naming a reference rule and a threshold, not a validated minimum. The claim it supports is "a
run resolves its own world's sign after 100 cycles"; the claim it does not support is "the effect is
established", because block-level agreement stays near 0.78 and only more worlds move that. No seed spent,
no engine run, no confirmatory block authorised.

## §135 — The 100-cycle window is adopted as a provisional convention, and both ceilings are reported (2026-11-02)

§133 established the sign criterion; §134 audited it and found the target convention-dependent and the
reference rule decisive. The owner adopted the criterion anyway. This entry records what was written down
and, more importantly, what it does not claim.

**The rule** (`docs/SCALING-LADDER.md` §10): a new methodology block scores at `2x` — 110 cycles of
formation exposure, 100 scored — unless that block's design record, written before it opens, predicts the
sign-resolution probability of the window it proposes under a **named reference rule** and says why the
`2x` default is wrong for it. The bar is per-world: `p` at or above 0.90 for every world.

**It is provisional, and the record says so in the same breath.** §9 puts `2x` at 0.976 with the
leave-one-out reference (0.977 where §8 ran it; the difference is Monte Carlo, not a correction), 0.946
with a fixed `8x` reference and 0.898 with a fixed `4x` one — five, three and three worlds clearing. At a
0.95 target four of five clear. Naming the reference rule in the rule itself is the consequence: "all five
worlds clear" holds only against the most precise reference available, so a block that uses another one
has to say so before it runs.

**`rho` is demoted.** Within-run SE over between-world SD stays in the report because it describes the two
uncertainties in one number, but it no longer sets the threshold: §133 showed it is a t-statistic whose
numerator moves with the pooled delta.

**Both numbers are mandatory**, because they differ in ceiling rather than in efficiency: per-world sign
resolution (0.917–0.997 across worlds at `2x`) and agreement with the pooled sign (0.780, never above 0.78
at any window). A claim about an average effect must carry the pooled estimate over worlds with its
uncertainty; it must not be reported as one run's outcome.

**What the adoption does not do.** It re-scores nothing, keeps V1's frozen 50-cycle labels intact,
allocates no confirmatory seed, and leaves the third axis untested — whether an effect survives a change
of generating configuration is still unknown, and the artifact's `not_measured` list (three items) says so.
The decision is cheap because it is a measurement convention: it buys a defensible window without
spending a seed.

## §136 — The per-world criterion is a conjunction, and that is recorded as a known limitation (2026-11-02)

The owner accepted §135's adoption and raised the consequence the rule does not handle: `every world at
or above 0.90` is a **conjunction**. Worlds are separate runs, so if the distribution of per-world
resolution is unchanged, adding worlds lowers the probability that the criterion is satisfied. Taking the
weakest value measured at `2x` (0.917) as every world's value, a five-world block clears with
probability **0.648**, a ten-world block **0.420**, a twenty-world block **0.177**. Planning arithmetic, labelled
as such: it assumes independence across worlds and an identical per-world probability, which is exactly
the assumption that would hold if the criterion's difficulty were purely a counting effect.

That matters because the rule exists to certify that a study's own runs are resolved, and larger studies
need that certification more, not less. A bar that tightens with n therefore works against its own
purpose, and §10 now says so.

**What was done: recorded, not changed.** The owner's instruction was to keep the adopted rule and log the
limitation for the next methodological review rather than quietly altering the convention mid-study, and
that is what `docs/SCALING-LADDER.md` §10 does. The review's options are named without being adopted: place
the bar on the mean, the median or a lower quantile of per-world resolution, or keep the minimum and accept
the shrinkage. `tests/test_scaling_ladder.py` asserts the note is present and that its three probabilities
match the artifact, so neither the limitation nor its arithmetic can disappear in a later edit.

No rule was relaxed, no seed was spent, and the confirmatory block remains unauthorised.

## §137 — The measurement framework is frozen, and the next experiment waits on a claim choice (2026-11-02)

The owner's review accepted the methodological work and named the risk it now carries: apparatus growth
outpacing the question. Between §130 and §136 the project added candidate-membership auditing,
strength-assignment controls, sign-resolution estimation, scaling analysis, reference-sensitivity
auditing and record safeguards. Each earned its place on its own; together they are now large enough that
another tool is more likely to be a refinement than a test.

**Recorded as given, not as a preference:** freeze the methodological baseline — no change to the
measurement framework without a justification tied to a scientific question; define the next claim before
designing anything; obtain independent review of the definitions, estimators, comparator selection,
controls and interpretation; then design the conditions experiment; then preregister, execute once and
evaluate without re-scoring.

**The question this leaves open, and why nothing was designed this turn.** Four ambitions are on the
table: (1) structural organisation produces measurable behavioral advantage; (2) the architecture produces
explainable, traceable decisions; (3) changes in internal structure produce identifiable changes in
behavior; (4) these combine into a different model of machine intelligence. They are nested, not
interchangeable, and the record supports them unequally. (1) is exactly where six task families came back
negative against baselines given the tuning advantage. (2) is partially established — Paper 02's claim is
that surviving state is reconstructible, not that complete history is. (3) already has a measurable
relation: K3's displacement result and the audit trace both tie a structural property to a behavior.
(4) is a framing claim, and no experiment settles it.

Naming the choice is the record's job here; making it is the owner's, so §137 stops at naming it, with
the recommendation that (3) is the one the frozen engine can actually test. Standing constraints restated
and not relaxed: no confirmatory seed allocated, V1 frozen, the conditions axis untested, and the
100-cycle convention still provisional (§§135–136).

## §138 — The structure-to-behavior claim is adopted at Level 2, and its design record exists before a seed does (2026-11-02)

§137 recorded the framework freeze and named four candidate ambitions. The owner confirmed the third —
changes in internal structure produce identifiable changes in behavior — as a **working** hypothesis, with
one refinement that changes what the experiment may conclude: distinguish association, prediction, and
causal influence, and make **prediction** the objective. `docs/STRUCTURE-BEHAVIOR-DESIGN.md` is that
record, written with no seed named.

**What it fixes.** The predictor is Phase L's `DI = late_retained / late_available`, with the
zero-denominator cell reported not measurable and excluded (the defect that produced the pilot's fake
`DI = 0.000` sweep). The outcome is `revision_held_out` — next-tag prediction on cycles 250–300 under the
rotated law, restricted to transitions withheld from formation **and** revision learning, named for what
it measures rather than for what it evokes. The predictor is measured at cycle 110–150, the outcome on a
later window, and the design requires the disjointness of the two pair sets to be *measured and printed*
rather than asserted, because disjointness-by-construction is right until an index is off by one.

**The level discipline is the substantive addition.** Level 1 is a correlation between structure and
behavior; Level 2 adds that the structure was measured earlier and the behavior on genuinely held-out
events; Level 3 requires manipulating the structural variable while controlling the rest. This design
reaches Level 2 and says so in the document that will carry the result, because a stable relation here
licenses "predicts" and nothing stronger. Level 3 needs an in-process arm that changes the structural
quantity and nothing else — the strength-assignment pattern — and is named as later work rather than
smuggled into the analysis.

**Configurations, and the gate that keeps them honest.** Three secondary configurations reuse the frozen
engine: presentation (block versus burst), hub structure, and cause-world ambiguity. Each needs its own
withheld-transition set enumerated under the same pre-written criteria; a configuration whose analogue
cannot be enumerated is dropped with the omission reported, never given the primary set, which would score
a different quantity under the same name.

**Falsifiers, both directions.** A: the relation is absent or reversed where the structure is present.
B: the relation's sign flips across configurations while `DI` is measured identically — the outcome that
would locate the behavior in the configuration rather than the structure. Persists, weakens, disappears
and reverses are all pre-committed findings; "weakens across conditions" is a result, not a failure to be
re-analysed.

**Nothing is authorised.** No seed is named; the 100-cycle convention is a declared deviation for this
endpoint and requires a predicted sign resolution under a named reference rule before seeds; and the
independent review of §8 — `DI`'s denominator policy, the `WITHHELD` set surviving the rotation, the
readout calibration, the comparator sweep, the overlap guard's ability to fail, and the level wording —
must be recorded before anything runs.

## §139 — The premise “structure has not been shown to predict anything held out” was too strong by one noun (2026-11-02)

The owner's assessment of §138 was that the project has the ingredients of the structure-to-behavior
hypothesis but has never tested it. Checked against the artifacts, that is right about the behaviour and
wrong as stated: `docs/formation_provenance_study.json` is a confirmatory, preregistered, 15-seed, run-once
result with all four gates passed, and it reports an **association detected** —

| arm | rate | hits / n |
| --- | --- | --- |
| `pair_world_attributed` | 0.4528 | 1938 / 4280 |
| `origin_includes_self` | 0.2387 | 2036 / 8528 |

difference **0.214061**, 98.33 % interval **[0.195886, 0.228119]**, permutation control including zero.

**What that study established is structure and the world's later content**, not structure and behaviour.
Its outcome is *occurrence* — whether the candidate's asserted pair appears in cycles 150–200, a window
the organism was never shown — which is a property of the event stream. This design's outcome is
*response*: what the organism's readout predicts on transitions it never saw. The study's own
`does_not_establish` list opens with “that the knowledge is useful or reusable”, which is exactly the
behavioural half that remains open.

**Consequence for the record, not for the hypothesis.** §2a of
`docs/STRUCTURE-BEHAVIOR-DESIGN.md` now states the position in three lines: structure ↔ future world content
is established once for provenance at candidate level in one configuration (0.214, interval above
zero); structure → the organism's own later behaviour is established for no structural variable; and the
stability of either across generating configurations is not established at all. The design is therefore
neither a first association test nor a repetition of one, and the sentence it would license if positive is
the one the project has never been able to write — that structure predicts what the organism does, not
merely what the world contains. No seed allocated; the review gate and the declared deviation stand.

## §140 — The design record was missing the two guards the prior study already had (2026-11-02)

Comparing §2a against the study it cites found a defect in §138's record. The formation-provenance study
passed four gates, one of them a permutation control; the design record had a null and two falsifiers but no
permutation control, and it treated disjoint pair sets as though they made the predictor and the outcome
independent.

**They do not, because one instrument produces both.** `DI` counts pairs the readout predicted, and
`revision_held_out` scores what that same readout predicts, so a relation could be a statement about how much
structure exists rather than which structure it is. §4 now requires a **mechanical baseline** — the outcome
regressed on structural size and the base rate — and says that a relation surviving the pair guard but not
the size baseline must be reported as a size effect. §6 carries a **permutation control** that shuffles `DI`
across worlds and must return an interval containing zero, with the provenance study's G3 as the template
(its permuted difference was 0.000359 on an interval spanning zero).

**The record can now be checked rather than believed.** §9 lists three commands: one printing the
artifact's verdict, difference, interval and arm rates; one running this document's own tests; one showing
the commit that carries it. That is the cheapest part of the review packet and the part that does not depend
on anyone's good faith.

This is the second defect found by comparing the design against an existing artifact rather than against its
own intentions — the first was §139's premise. Both were in the record, not in the hypothesis. No seed
allocated.

## §141 — The independent review is written down as a rubric, with the author excluded by rule (2026-11-02)

The owner set the review as the condition on seeds and named what it must establish. The task in writing it
down was to make it impossible to pass by politeness.

**`docs/INDEPENDENT-METHODS-REVIEW.md`** carries the five questions and, for each, the part of the design
that answers it and what would count as a defect — so an item cannot be marked on impression. Measurement
independence points at §4's pair guard and size baseline, §6's permutation control and §7's
shared-instrument limit; held-out validity at the temporal order and the measured disjointness; falsifiability
at both falsifiers and the four pre-committed outcomes, including the sign flip.

**Eligibility is exclusionary.** Five criteria, and two named exclusions: the agent that wrote the design
record cannot review it, and the owner — who chose the hypothesis — cannot stand in for a reviewer. Anyone
who wrote the reusable-knowledge scoring, the Phase L index or the provenance harness is ineligible for the
independence item, because those instruments are what that item interrogates. Conflicts are declared rather
than disqualifying; an undeclared conflict is.

**The rubric has three outcomes and one asymmetry.** Approved, approved with conditions, rejected. Passing to
the next stage requires the same reviewer to re-assess the conditioned items; a rejection is recorded verbatim
and cannot be argued into an approval inside the record. Conditions must be written as changes specific
enough to re-review, with the document's own example of the difference between "make the control stronger"
and a testable requirement.

**The safeguard is structural.** The reviewer sees no data from this design, because none may exist until the
outcome is recorded; if an item needs data, design-block data only and declared. Two gates remain outside the
review and are not discharged by approval: the endpoint sign-resolution computation the 100-cycle deviation
requires, and the withheld-set enumeration for whichever secondary configurations survive.

No reviewer has been appointed. The record's §7 is empty, and the manual row says so.

## §142 — The protocol is finished and the review package is assembled; the paper is deliberately not written (2026-11-02)

The owner separated three things that serve different purposes — the protocol, the review package, the paper
— and asked for the first two before any seed. Writing them found what the design record had been missing
for a reviewer: not the hypothesis, which was precise, but the **statistical model** a referee would ask for.

**What the protocol gained.** Its nine required elements now open the document with pointers to their homes.
§6 carries the model: Spearman rank correlation as the primary statistic (n is small, the relation need not
be linear), the standardized OLS slope as an effect size beside it, a 10,000-replicate bootstrap over worlds
at 98.33 %, reported per configuration and never pooled. It carries the decision rule (present / absent /
reversed, and persists / weakens / disappears / reverses), the size baseline as a *competing predictor* rather
than a diagnostic, and the sign-resolution clause: the block may not open until the probability of recovering
a world's true relation with the correct sign is computed from design-block cells under a named reference
rule, with 0.90 on the weakest world as the bar, and no value recorded yet.

**§10 is new and is the part that makes the protocol falsifiable in practice.** Seven observed outcomes are
mapped to the sentence the record may carry: supported, mixed, not supported, reversed, size effect, design
defect, inconclusive. Two of those forbid a result outright — a non-null permutation control or a non-empty
pair overlap means the defect is the finding. A positive result licenses *predicts*, and *causes*, *produces*
and *drives* are reserved for a Level 3 design.

**The package** is `docs/REVIEW-PACKAGE.md`: five components with paths, the prior-evidence summary with
artifact pointers (0.214061 for structure ↔ world content, −0.5735 for the reversed belief-revision task),
what it deliberately omits, the commands that check it, and the reviewer's reading order.

**No paper.** A protocol paper would invite a proposal to be read as a finding, and the project has spent
enough of its history learning that lesson. The decision is deferred until there is something substantive to
report.

## §143 — The sign resolution is computed, and it says the block must be 48 worlds per configuration (2026-11-02)

The protocol left one number unrecorded: the probability that a block recovers the relation with the correct
sign. Computing it was the gate on seeds, and it has now been computed without an engine and without a seed.

**The estimator had to be rebuilt for this endpoint, not borrowed.** The ladder's `sign_resolution` asks a
per-world question — if this run scored one world, how often would it report that world's sign correctly —
because its estimand is a within-world delta. This block's estimand is a rank correlation *across* worlds, so
the unit of inference is the block. Borrowing the per-world formula would have produced a number that looked
like the ladder's and answered a different question, which is the failure rule 23(a) records. What is
simulated instead is the protocol's own decision rule: worlds from a Gaussian copula at a stated rank
relation, an interval by resampling worlds at 98.33 %, resolved only when the interval excludes zero
with the predicted sign. Fisher's z is computed beside it over six cells and agrees to within 0.052, so
the closed form is a check rather than the answer.

**The reference rule is named and it is deliberately not an effect size.** It is *the smallest relation of
interest*, 0.50: the weakest relation the design would call predictive. Anything else — a
plausible-looking 0.4 carried over from some other artifact — would have made the answer a function of a
guessed effect, and the block would then have been sized by a guess and tested for it.

**The result is larger than the project's habits.** 48 worlds per configuration to clear
0.90 at 0.50 (p = 0.902); 21 worlds for 0.70, 32 for
0.60, 79 for 0.40, 144 for 0.30. Three configurations therefore need **144 runs**. At
20 worlds the block could only resolve relations of 0.70 and above, which is a different hypothesis than the
one the design states.

**So the size is a decision, and it is now written as one.** Shrinking the block means either shrinking the
claim to a larger relation or lowering the bar, and both are protocol changes made before the block opens and
recorded with their own justification. If the size were chosen after this table, the design would have picked
its own effect size — the defect §10 exists to prevent.

**Three reasons the number is an upper bound**, all in the artifact's `limits`: `DI`'s own measurement error
attenuates the observed correlation and is not modelled; worlds are treated as exchangeable where §5's block
structure may not provide it; and a secondary configuration's outcome distribution is not the primary's, so no
number transfers. The honest reading is "at best 0.902", not "90 %".

No seed is allocated. The new action row puts the size decision in front of the owner.

**One defect caught while writing this entry, recorded because it is the kind that hides.** The first version
of the edit replaced §6 from the sign-resolution paragraph to the §7 heading by index, which silently
deleted the null hypothesis, the permutation control and both falsifiers — the paragraphs that make the
protocol falsifiable at all. Nothing about the diff looked wrong: the section still ended under a header and
still read as prose. `tests/test_structure_behavior_design.py` failed on the missing phrases and the tail was
restored from the committed version. The lesson is the standing one: the guard found it, and it was found only
because the guard asserts phrases rather than reading for sense.

## §144 — The bound was stated backwards for the world count, and attenuation is now priced (2026-11-02)

The owner's review of §143 found one substantive defect and it was in the sentence that told a reader how to
use the number. The artifact had said the computed probability is "an upper bound" without saying of what,
and it was printed beside a world count. Read as a claim about the count, that inverts the result: a bound
on how many worlds you might need, when the truth is a floor on how many you need.

**The direction, stated properly.** Measurement error in `DI` attenuates the observed relation. A run that
would show 0.50 with a perfect instrument shows less with a noisy one, so a block of 48 resolves the
relation *less* often than the simulation says, and more worlds are needed — not fewer. The computed
probability is an upper bound; the computed minimum n is a floor. The same holds for dependence between
worlds, which narrows the interval and overstates the probability. Both omissions push one way, and it is
the direction that costs runs.

**Attenuation, priced rather than waved at.** No error model is fitted, and pretending one is would be a
worse defect than the omission. What the artifact now carries is one stated assumption — classical error in
one variable, bivariate normal, a latent 0.50 appearing as 0.50 × reliability — and its consequence:
reliability 1.00 needs 48 worlds per configuration, 0.90 needs 61, 0.80 needs 79, 0.70 needs 105,
0.60 needs 144. `DI`'s reliability is measured nowhere in this project, so the table is the price of an
unmeasured quantity, and measuring it is now a prerequisite the record owes the reviewer rather than a
detail for later. At 0.80 the block is 79 worlds per configuration, not 48.

**What 0.902 is not.** Not a posterior probability that the hypothesis is true, not a p-value, not a
false-positive rate, not a property of the engine, and not a statement about a latent relation. It is the
simulated frequency with which this decision rule resolves a relation of that size under the stated
assumptions, on the relation as measured.

**Exchangeability is now an assumption with a diagnostic attached.** Per-configuration analysis removes
across-configuration clustering and says nothing about dependence within a configuration, which would
arrive as state carried between seeds or as worlds drawn from related conditions. So the block must report,
before reading the relation, the dependence of `DI` and of the outcome on seed order, and resample
contiguous blocks of seeds if that dependence is non-negligible, reporting both intervals.

**What did not change.** The numbers 48 / 79 / 32 / 21 / 144 stand; the reference rule stands; no seed is
allocated and the block's size remains undecided. The status is provisional, and the reviewer is to see the
floor and the attenuation table together — not the floor alone, which is how a constraint becomes a budget.
The owner also did not certify the implementation, having read the report rather than `af1f74c`; the review
that matters is still the independent one, and this entry is a correction, not a completion.

## §145 — The package is finished and the request is written, and it is unsent (2026-11-02)

The owner asked how the independent review is actually obtained, and offered the hypothesis that one writes
a paper and requests review in it. That is the wrong instrument and the reason is worth recording: journal
review asks whether a contribution is publishable, arrives after the data, and takes months; this gate asks
whether the experiment should be run, must arrive before the data, and needs three hours from one person. A
paper about the protocol would also invite it to be read as a finding, which is the reading the project has
refused twice.

**What changed is the handover, not the claim.** `docs/REVIEW-PACKAGE.md` now carries the feasibility result
as a component rather than leaving it in the protocol: the 48-world floor at a 0.50 relation, the
attenuation table (1.00 → 48, 0.90 → 61, 0.80 → 79, 0.70 → 105, 0.60 → 144 worlds per
configuration), the admission that `DI`'s reliability is measured nowhere, and the exchangeability
diagnostic. The package also states the command that reproduces its own claims from a pinned commit, because
the repository is public and a reviewer should not have to accept a bundle.

**The review brief is reconciled with that.** The sign-resolution computation was listed as a gate outside
the review; it is now discharged, recorded in the package, and the reviewer is asked to check it. One gate
remains outside: the withheld-transition enumeration for whichever secondary configurations survive.

**A letter exists and has not been sent.** `docs/REVIEW-REQUEST.md` is the one-page request, with the five
fields the sender must fill, the two facts a reviewer should see before forming a view, the eligibility
rules, and the statement that a rejection will be recorded verbatim. Writing it was the point at which the
project stopped being able to say it had no way to ask.

**What this entry does not claim.** No reviewer exists. Section 7 of the brief is still empty. No seed is
allocated, no size chosen, and the two papers remain unpublished and out of this lane. The remaining work is
someone else's decision to accept, and the project's to record.

## §146 — Why the review needs a person, and what a machine pass is worth (2026-11-02)

The owner asked the direct question: why not have another AI do the independent review, since the package
already exists. Two things are true and they point in different directions, so both are recorded.

**The machine pass is worth having.** A model that did not write the design is not anchored by the reasoning
that produced it. It will read all 373 lines and every cited artifact, it costs nothing to run twice, and it
cannot be talked into a view by the author, because the author is not in the room. The prompt for it is
`docs/AI-REVIEW-PROMPT.md`: five rubric questions, verdicts with the supporting artifact quoted, severity,
the check that would settle each objection, and three closing sections including the strongest single
objection to running the experiment at all.

**It cannot be the review, and the reason is accountability rather than ability.** §2 asks for a reviewer
who can say no and is answerable for it; §7 records an affiliation, declared conflicts and a signature.
A model approves at no risk, cannot be asked to defend the approval a year later, cannot decline to
approve, and has no standing to be cited as the person who examined the design before it ran. Filling
§7's fields from a model would be a fabricated provenance — the same defect class as the hand-copied
precision ceiling in §29, where a number looked right and named nothing.

**A gate that cannot refuse is decoration.** Rule 25(c) is about gates that pass while the protocol's gate of
the same name fails; this is the degenerate case, a gate whose only possible answers are yes and yes with
caveats. The human review is asynchronous, slow, and can end in refusal; that is not a cost of the process,
it is the mechanism.

**What the machine pass may not do**, now written into the brief as §9: discharge the gate, be cited as
the review, see anything that requires the engine or the six months of history behind the design, or fill
§7. A blocking finding is fixed and logged with the model's wording attached; a clean pass is recorded as
a fact about one failure mode, not as a certificate.

**A false objection avoided.** Before writing the prompt, the outcome's denominator was checked rather than
assumed: `revision_held_out` is scored on 98–110 held-out pairs per seed (`docs/reusable_knowledge_calibration.json`),
not on the two `WITHHELD` entries, so the "outcome is measured on two items" objection that would have been
the first thing a reviewer raised is simply false. The general point stands and is why the prompt's first
rule is *check artifacts, not prose*.

## §147 — The owner offered to sign, then offered his partner; the primer is the part that helps (2026-11-02)

Two offers arrived in one breath, and both are worth answering precisely because both are generous.

**"I will stake my name."** The owner chose the hypothesis, the level and the sequence, so a signature from
him would have the record say that the reviewer of his own judgement found his judgement sound. §2 already
forbids that, and the paragraph was written before this conversation, which is the only reason it is not
just a preference being overruled now.

**"My partner will sign."** This one is worse rather than better, and the reason is not a technicality: the
fifth eligibility rule is *no stake in a positive result*, and a partner's stake is not an undeclared
interest that disclosure could cure — it is the relationship. Recording it would produce a review that
looks independent and is the least independent reading available, and every later citation of it would carry
that unstated fact.

**What was useful in the request.** "Metabolisable" is the real problem with the package, and it is not about
the partner: the document set was written by people deep inside the project, for people deep inside the
project. `docs/REVIEW-PRIMER.md` now states the claim in one sentence, defines both measurements without
jargon, names the shared instrument and the 48-run floor with its attenuation rather than softening either,
lists what would count against the hypothesis before anyone runs it, and says in as many words that "no" is
an available answer. The package, the brief and the request letter all point at it first.

**What this does not change.** No signature exists, §7 is empty, no seed is allocated, no size is chosen.
If the owner decides to run without the review, that is a waiver and will be recorded as one — the protocol
says a review cannot be waived for schedule, so a waiver has to be an explicit decision with its cost
written next to it, not an absence that later reads like an approval.

## §148 — The attenuation rule was the wrong rule, and the dependence direction was an assumption (2026-11-02)

Two corrections, both from the owner's review, both of the kind that only a second reader finds.

**The attenuation table used a product rule that no textbook states.** It computed observed = latent ×
reliability. For classical error in one variable the Pearson correlation is multiplied by sqrt(reliability),
not by the reliability; and because this endpoint's estimand is Spearman, the Pearson factor then has to be
mapped through the bivariate-normal relation `rho_s = (6/pi) asin(rho_g/2)`. Multiplying a rank correlation by
a reliability is a plausible-looking operation that produces a number nobody can check, which is exactly the
defect class this project keeps finding in its own artifacts.

**What the corrected curve says.** Reliability 1.00 → 48 worlds per configuration, 0.90 → 54, 0.80 → 62, 0.70 → 72,
0.60 → 85, 0.50 → 104, 0.40 → 131, 0.30 → 177. The old table gave 48 / 61 / 79 / 105 / 144, so it overstated the loss at
every level — the 0.80 case moves from 79 to 62. The direction of the floor claim survives, because noise still
raises the requirement; the magnitudes a reviewer is shown do not. The curve is computed by `observed_spearman`
and independently checked by Monte Carlo on samples of the block's own size, agreeing to within 0.021.

**A caveat that has to travel with it.** The model is classical, independent error in a bounded ratio. `DI` is
not a Gaussian measurement, so this is a sensitivity curve under a declared model, not a correction of the
requirement. It says how far the requirement moves as reliability varies; it does not say what reliability is.
That stays unmeasured and remains the prerequisite.

**The dependence claim was an assertion wearing a mechanism's clothes.** The protocol said within-configuration
dependence "narrows the interval and overstates the probability — the same direction as attenuation, never the
safe one". That is a statement about a dependence structure nobody had simulated. It has now been simulated:
a shared component with intraclass correlation 0.00, 0.10 and 0.20, resampled both as individual worlds and as
contiguous blocks. The differences in resolution probability are +0.033, +0.000, -0.013 — inside Monte-Carlo noise at 150
simulations, and not all one way. So the record now says the direction depends on the structure and has not been
established here, and the block's diagnostic reports both intervals rather than leaning on an assumed sign.

**What did not change.** No engine ran, no seed was spent, no size was chosen, §7 is still empty. The 48-world
reference figure is untouched because it is the reliability-1.0 row. The package, the protocol and the primer
were regenerated from the artifact rather than edited by hand, so the numbers cannot drift between them.

## §149 — `DI` is a state at a time, and the protocol's window is contested (2026-11-02)

The owner paused the sample-size discussion until the construct was settled, on the reasoning that a
reliability estimator cannot be chosen before it is known what the number is supposed to represent.
`docs/DI-CONSTRUCT-AUDIT.md` answers the five questions from the 240 stored Phase L records (eight
configurations x 30 seeds, 600 cycles each), and `benchmarks/di_construct_audit.py` writes every number it
quotes to `docs/di_construct_audit.json`. No engine ran, no seed was spent, and no coefficient was computed.

**What the number is.** `DI = late_retained / late_available` from `phase_l_campaign.py::indices()`, and the
trajectory is a **per-cycle snapshot, not an accumulator** — the function's own docstring says so. The
distinction is not pedantic: 1,598 single-cycle decreases occur across the 240 trajectories and only 122 of
240 are non-decreasing over their whole length, so "the report omitted this pair" and "retention decayed"
are the same event to this instrument. The denominator is 18 pairs in every record and every stored value is
an integer multiple of 1/18, so the resolution floor is 0.0556 — one pair.

**Which construct it is.** Not a stable trait: arrival is cycle 150, and mean `DI` is 0.0 at cycles 0, 100
and 200. Not a trajectory in the protocol's sense: the protocol takes one number at the end of a window. It
is a **state at a designated time**, and in these records it is a slow transition — mean 0.0002 at cycle
300, 0.110 at 400, 0.241 at 500 and 0.293 at the last cycle, with per-arm median first-reach from 424.5 to
586. Only once it settles is it configuration-like: ICC 0.890 over cycles 400-600, 98.5 % of between-run
variance carried by the arm label, 121 of 240 exactly constant, and four of eight arms at 0.000.

**The window is the finding that matters.** Applied to these records the protocol's 110-150 is pre-arrival
and returns **240 identical zeros** — one distinct window mean, zero variance. The matched 40-cycle
post-arrival window (150-190) is 234/240 all-zero, 99.85 % of cells zero, ICC 0.068. So the window as
written measures the floor, and under either absolute or proportional scaling the transition does not fit
in 40 cycles. §2 of the design record now carries a dated note recording the window as **unresolved**
rather than rewriting it: a design parameter is corrected by the owner on evidence, not by an audit editing
itself into the record.

**Can error be separated from developmental change?** Not in these records, and the reasons are structural
rather than statistical: there is nothing to separate at the protocol's offset, nothing has started at the
matched offset, the asymptote's variance is the configuration (so a coefficient there would re-report the
arm ordering), the 18-pair denominator caps the resolution, and a per-cycle snapshot makes omission and
decay the same observation. The estimator that matches a state at a time is **parallel forms at a fixed
window** — two disjoint late-pair sets scored on the same cycles — and the records contain one late-pair set
and one reading per cycle, so no parallel form exists inside them. Reporting a split-half coefficient would
have answered a question this audit shows to be ill-posed, and supplied the number the sample-size
calculation needs for a reason that does not survive inspection. None was reported.

**What did not change.** No seed allocated, V1 and its results untouched, the sample-size discussion still
paused, `docs/INDEPENDENT-METHODS-REVIEW.md` §7 still empty, no reviewer approached. The review gate has one
more thing it must be told: the predictor's window is contested.

## §150 — Stage A of the measurement window: the transition had not finished, and the endpoint has a pair of range (2026-11-02)

The owner separated window selection from validation and asked five Stage A questions of the existing records
before any confirmatory run. `docs/DI-MEASUREMENT-WINDOW.md` answers them, with
`benchmarks/di_window_design.py` writing every number to `docs/di_window_design.json`; no engine, no seed, no
coefficient, no window adopted.

**Emergence is arm-dependent, and four arms are dead.** Median first sustained non-zero reading: 329 (`6:1`),
362 (`4:1`), 404 (`3:1`), 539 (`2:1`). The four late-disadvantaged arms show **one** non-zero reading in 30 runs,
at the arrival boundary, and none sustained: **117 of the 240 runs never leave zero at all**. That is AGENTS 13a
in its exact form — on those arms the endpoint measures nothing — so they are out of scope for this measurement
rather than a low-`DI` condition.

**The record contains no asymptote.** Among the 119 runs that move, the median settle cycle (the last cycle
differing from the run's own final value by a pair) is **586 of 600**, the maximum is 599, and **25 to 27 of 30
runs per arm are still changing in the last 50 cycles**. The run ends inside the transition. This is why Stage A
proposes no cycle number: any number read off these records encodes where the run stopped, which is the same
error as 110-150 in the other direction.

**The dynamic range is the larger finding.** Within-configuration SD of the 40-cycle window mean never exceeds
2.02 pairs and is **0.44 pairs** at the settled window, against a one-pair floor; **at least 97 %** of predictor
variance is between configurations at every window from 460 cycles on. A within-configuration rank correlation
would rest on about one pair of spread while the same predictor moves six or more pairs across arms. The ICC of
0.890 is **not a repeatability coefficient** — each world is read once — and this is the concrete reason it could
not be one.

**Schedule.** A settled measurement followed by the protocol's 50-cycle learning and 50-cycle test needs **686**
cycles against a 150-cycle run: 4.6x too short for the sequence the protocol specifies.

**What Stage A proposes instead of a window:** runs long enough to contain the asymptote (length declared
before, asymptote demonstrated after), a window placed after it with a declared tolerance, two disjoint late-pair
sets so reliability can eventually be asked as parallel forms and resolution can be finer than 1/18, and the
predictor's within-configuration spread reported beside every relation. The trajectory-summary alternative
(onset, slope, area) is named as scientifically attractive and as a **different construct** that requires its own
audit: it must not arrive as a side effect of moving a window.

**Stage B is specified and not authorised.** Fresh methodology worlds on seeds disjoint from Phase L and from
every confirmatory block, four pre-committed criteria judged whole (non-degenerate; resolution of at least two
pairs; asymptote consistency; measurement before learning with an empty pair overlap), and a failure rule that
rejects the window rather than shrinking the claim. No seed allocated, V1 untouched, the sample-size discussion
still paused, and the review gate unchanged.

## §151 — The primary predictor becomes onset, and "settle" is separated into three criteria (2026-11-02)

The owner decided that the next design phase should treat **transition dynamics** as the primary candidate
construct and keep the settled state as a separate, unresolved construct. `docs/DI-TRANSITION-CONSTRUCT.md` is
the audit that decision requires, with `benchmarks/di_transition_construct.py` writing every number to
`docs/di_transition_construct.json`. It reads **no behavioural endpoint**: the summary is chosen on measurement
grounds, before any outcome is examined, so the choice cannot be a selection on results.

**Why onset, and why not the other two.** Measured on the same 240 records: **slope** is not estimable from a
record whose transition may still be running — its rank correlation between the full fit and a fit truncated at
cycle 450 is **-0.315**, i.e. the ordering of worlds by rate *reverses* when the observation ends early.
**Exposure** (mean `DI` over the run, in pairs) is defined for every record and rank-stable under truncation
(0.925), but its value is defined *relative to an integration interval*, and the interval's length is the one
parameter this project has not been able to fix; keeping it primary would build the open question into the
predictor. **Onset** (first cycle from which ten consecutive readings are non-zero) is defined in 119 of 120 runs
of the four configurations that express structure at all, varies within `6:1` with SD **12.4 cycles** over a
range of 65 on a one-cycle grid, and cannot change because the run stopped early. Onset and exposure
rank-correlate at **-0.932** across configurations, so choosing onset keeps the ordering and discards only the
interval dependence.

**A correction to §150's row.** Stage A compared the settled window's within-configuration SD of 0.44 pairs to
"a resolution of one pair". That compared a **40-cycle mean** to a **single-cycle quantum**: the mean moves in
steps of 1/(18 x 40) pairs, so 0.44 pairs is real spread of about eight single-cycle quanta, not a value sitting
on a floor, and the "removes the dynamic range" conclusion is **withdrawn**. What survives from that section is
narrower and still true — the settled window is 98 % arm-determined, so a *pooled* relation would be an arm
effect restated. The decisive defect is not the spread but that there is no settled state to measure. This is
rule 24's failure mode in the project's own work: the measurement was right and the sentence around it was
wider than the check.

**Settling, separated into the three criteria it had been conflating.** (a) entry into a one-pair band around
the run's own final value: median **587** of 600, max 599 — retrospective, since the final value is where the
observation stopped. (b) persistence in that band: median **13 cycles**; 37 runs reach 30, 17 reach 50, 4 reach
100. (c) no meaningful remaining trend over the last 100 cycles: median **2.0 pairs** (range -4.0 to +9.0), with
**23** of 119 runs below half a pair and **96** at two pairs or more, none between. Only **4 of 119** runs satisfy
(b) at 50 cycles and (c) together. So the project's "settle" statistic was measuring a short quiet patch, and
the word **asymptote** is retired: a future run may claim one only if both conditions are declared before it runs
and both are met afterwards.

**Scope and boundary.** Onset is out of scope in `1:1`-`1:4` because those worlds express no sustained `DI` at
all (AGENTS 13a), which is a statement about the world, not a null about the organism. The ordering is preserved
and made stricter: onset is a cycle index, its ten-cycle sustention must complete before revision learning
begins, no behavioural cycle may contribute to it, and any co-reported exposure interval must be declared in
advance.

**Stage B remains unauthorised**, with its four criteria restated for a cycle-valued predictor (non-degenerate,
onset SD of at least 3 cycles, the stopping criterion met in every claimed configuration, and the ordering with
no behavioural cycle in any predictor). No seed, no world, no run. The 240 records, the protocol's window, the
construct audit's verdict on `DI` as a state at a time, and the review gate are all untouched.

## §152 — Onset is defined precisely enough to run, and the `1:x` arms are classified rather than dropped (2026-11-02)

**The owner endorsed onset and asked for three closures before authorisation.** The audit had argued for onset
on measurement grounds; what it had not done was write the event in a form a second person could apply without
asking a question, separate measurement eligibility from scientific scope, and evaluate the resolution criterion
where it is claimed rather than on the pool. All three are now in §3 of the construct record, and the artifact
carries them as computed quantities rather than prose: `benchmarks/di_transition_construct.py` writes
`onset_conventions`, `onset_convention_counts`, `sustention_sensitivity`, `eligibility`, `accounting` and
`stage_b_measurement_criteria` into `docs/di_transition_construct.json`.

**The event.** Onset is the first cycle of the qualifying sustained run — not the first cycle on which `DI` is
non-zero. The distinction is not pedantic in this record: **99** of the 119 onsets are also the record's first
non-zero cycle and **20 are not**, one of them by **279 cycles**. A convention anchored at the first non-zero
reading would have moved a sixth of the values, and one world by nearly half a trajectory. The anchor is
confirmed only when the tenth consecutive reading lands, so the predictor's availability cycle is nine cycles
later and the latest confirmation is cycle **598** of 600. Before confirmation, a short run ended by a zero does
not qualify and does not move the anchor — **2,353** such interrupted attempts occur across 24 records, which is
`DI` oscillating around zero — and the search resumes after the zero rather than being back-dated. A missing
reading breaks the run and is never read as non-zero; no record contains one, so that convention is declared for
future runs and is vacuous here. A run still non-zero where the record ends with fewer than ten readings is
censored: **0** records are censored that way, **4** are censored with an interrupted attempt (the one-cycle
arrival blips in `1:x`), and **117** never produce a reading to qualify. 119 + 4 + 117 = 240.

**The rule is swept, because it is part of the measure.** Halving the sustention rule to 5 changes three onsets
by at most 25 cycles; doubling it to 20 changes one by 13 and loses two definitions. The medians move by two
cycles at most. The rule does not manufacture the ordering, and it remains a declared constant Stage B must
freeze — the sweep bounds its influence, it does not license choosing it later.

**Eligibility is a measurement fact; scope is the claim.** All eight configurations are now reported, with the
ineligible four counted rather than removed: **240 records, 120 in the four configurations with sustained
emergence, 120 in the four without, 0 dropped.** The claim is written as *evaluated among configurations in
which sustained structure emerges*, and the `1:x` classification stays a property of those worlds (AGENTS 13a)
rather than a missing denominator. This is rule 24 applied before the fact: the claim is cut to what the
measurement reaches, and what it does not reach stays visible.

**The criterion is evaluated where it is claimed.** The 3-cycle SD floor and the 90 % defined-share criterion are
computed inside each of the four configurations, with IQR, range and distinct-value counts beside them. All four
pass, and not narrowly — smallest SD 12.4 cycles against a floor of 3, tightest defined share 0.967 against
0.90. The distribution keeps the pass honest in the other direction: only **17–27 %** of onsets lie within ±3
cycles of their own configuration's median, and 18–27 of each 30 are distinct values, so the SD is broad spread
rather than a floor plus a few outliers. `6:1` is closest to the floor and would be the first to fail.

**The boundary is now written against availability, not the anchor.** Because the anchor is retrospective, the
behavioural limb may not begin at the anchor cycle; it begins after the confirmation cycle, and the run must
then extend through the protocol's 50-cycle learning and 50-cycle test. The run length is set by the organism's
emergence plus a fixed margin — the property the settled-state window lacked, because that window had to be
chosen before anything had emerged.

**Stage B is still not authorised.** No seed, no world, no run. The four criteria, the failure rule, the 240
records, the protocol's 110–150 window, the construct audit's verdict and the empty review gate are untouched.
The owner's instruction was that the study can be authorised against a fixed, independently measurable predictor
rather than an evolving interpretation of one. The predictor is now fixed in code and in counts; the next
decision is his.

---

## 153. The threshold sweep is checked on the ordering, and the behavioural clock is fixed

**Why this section exists.** The owner accepted the three closures of §152 as a defensible completion of the
Stage A construct-definition work — onset reproducible, eligibility accounted, dispersion meaningful — and did
**not** treat the predictor as validated. Two items remained before the design could go to the review gate: the
sustention sweep established that the *median* was stable, which says nothing about whether an individual world
keeps its rank; and the boundary written against the confirmation cycle means behavioural learning begins at a
different absolute cycle in different worlds, which is an exposure-time problem if it is left unstated.

**The sweep, checked where it matters.** The rank ordering of onset is now compared across the 5-, 10- and
20-cycle rules within each claimed configuration, with the pairwise inversions and the records whose eligibility
appears or disappears:

| configuration | ρ 5 vs 10 | ρ 10 vs 20 | ρ 5 vs 20 | worst rank shift | records whose eligibility changes |
| --- | --- | --- | --- | --- | --- |
| `6:1` | 1.000 | 1.000 | 1.000 | 0 | 0 |
| `4:1` | 1.000 | 1.000 | 1.000 | 0 | 0 |
| `3:1` | 0.979 | 1.000 | 0.979 | 9 | 0 |
| `2:1` | 0.990 | 0.987 | 0.972 | 6 | 2 |

**No configuration's verdict changes** under either alternative rule — the two measurement criteria pass in all
four configurations at all three rules — so the ordering of worlds is reproducible under a rule the study did not
choose. But reproducible is not identical: in `3:1` and `2:1` individual worlds move by up to 9 and 6 rank
positions of 30, and **2 runs** defined at ten cycles are undefined at twenty, both in `2:1`, where the defined
share under the doubled rule lands on exactly **0.900** — the criterion itself. That is a marginal pass, not a
comfortable one, and it is the second reason the ten-cycle rule is frozen before the run rather than swept during
analysis: a sweep performed after the outcome is visible could move two runs out of a denominator and turn a
criterion into a judgement call.

**The clock, fixed before the run.** The predictor is available at the confirmation cycle, so the behavioural
limb opens the cycle after it: a **one-cycle** margin, which is the earliest legal cycle rather than a taste
parameter, because confirmation is the last structural reading the onset rule reads. With the protocol's 50-cycle
learning and 50-cycle test the follow-up is **100** cycles, identical in every world, and every behavioural
observation reports both its absolute cycle and its cycles since confirmation. Disjointness is checked, not
asserted: **0 of 119** behavioural cycles fall at or before a world's confirmation.

**The two clocks are separated on purpose, and the separation is the estimand.** The behavioural *opportunity* is
equal — same margin, same phases, same duration. The developmental *age* at which it opens is not: across the 119
moving runs the first behavioural cycle ranges from **299 to 599**, a span of 300 cycles. A predictor of
developmental age would compare unequal windows at equal absolute time; this design compares equal windows at
unequal developmental age, which is what a claim about behaviour *after structure emerges* is about. Both clocks
travel with every observation so that a reader can see which one a result is stated in, and no result may be
reported in both.

**The clock's cost is measured on the record rather than assumed.** Each world's run must extend through
confirmation + 101 cycles. The slowest world in hand confirms at 598, so its run needs **699** cycles, and only
**91 of 119** runs would fit a post-confirmation follow-up inside a 600-cycle run — in `2:1`, **1 of 29**. A
Stage B run therefore cannot use a fixed 600-cycle horizon. The horizon must be each world's own confirmation
cycle plus 101, or a pre-declared maximum confirmation cycle plus 101 applied to every world. A fixed horizon that
ends mid-follow-up would reproduce the Phase L defect that made late structure unmeasurable (AGENTS 13) in a
worse form: the follow-up would be *shortest* for the worlds that emerged latest, which are exactly the worlds a
relation between late emergence and behaviour is most informative about.

**What is claimed, and what is not.** The measurement properties are established: onset is reproducible, its
eligibility and per-configuration dispersion are accounted for, its ordering survives the sustention rule, and
its clock is declared and disjoint from the outcome. **No relation to behaviour has been computed** — by design,
because the construct must be chosen before the outcome is read. **Stage B remains unauthorised**: no seed, no
world, no run; the 240 records, the protocol's 110–150 window, the construct audit's verdict and the empty review
gate are untouched. The next step the owner named is the independent review gate, not the run.

---

## 154. The behavioural horizon: an index is not a count

**What was questioned.** The record said the follow-up runs from confirmation + 1 through confirmation + 100 —
100 cycles inclusive — and that the run horizon is confirmation + 101. Those two statements read as one cycle
apart, and the owner asked for the difference to be reconciled against the code rather than smoothed in prose.

**What the code says.** The follow-up is **100 behavioural cycles**, from index c + 1 through index c + 100
inclusive: (c + 100) − (c + 1) + 1 = 100. The horizon is **101 readings** measured from the confirmation index, for
one reason only: a run of length L holds indices 0 … L − 1, so a run that contains index c + 100 has length
c + 101. The slowest world in hand confirms at index 598, its last behavioural cycle is **index 698**, and its run
needs **699 readings**. So the owner's 698 and the record's 699 are the same span counted from zero and from one —
the count of behavioural cycles was never wrong, and no number in the record changed.

**Why it is still worth fixing.** The discrepancy was manufactured by unstated indexing, which is the cheapest way
for a one-cycle error to enter a protocol and the hardest to see afterwards: both sentences were true of the code
and false of each other. Four changes make it mechanical rather than remembered. The artifact now carries
`last_behavioural_index_max`, `behavioural_cycle_count`, `inclusive_span_cycles` and the two offset fields beside
`run_length_needed_cycles`. The code derives each horizon as that run's own last index plus one rather than as its
start plus a duration. The build asserts the inclusive-span identity, and the test asserts that the run length
equals the last index plus one, so the two conventions cannot drift apart in a later edit. And §3.1 states the
convention once — cycle numbers are zero-based indices into the stored trajectory, so "598 of 600" is index 598 of
a 600-reading run — with §6.2 tabulating the 100 cycles and the 101 readings side by side.

**What this does not change.** The 600-reading record still cannot host a post-confirmation follow-up in 28 of its
119 moving runs (`2:1`: 28 of 29), the horizon must still be set per world from its own confirmation cycle rather
than fixed, and **Stage B remains unauthorised**. The reconciliation resolved a representation, not a finding.

---

## 155. A protocol whose size is a consequence of its claim

**What this section adds.** `docs/STAGE-B-PROTOCOL.md` is the complete Stage B protocol, written for the
independent review gate and authorised by nothing. It inherits the onset predictor, the eligibility and
dispersion rules and the behavioural clock from the construct record rather than restating them, because a
protocol that copies a constant is a second place for it to drift.

**The block size is the part worth recording.** Three numbers are fixed before any data: the smallest relation
worth calling predictive (0.50 rank correlation), the project's 98.33 % decision level, and the bar that a block
must resolve such a relation in 90 % of runs. Solving the decision rule for those gives **48 worlds per
configuration** at full reliability — and the closed form reproduces the published sign-resolution floor for this
endpoint exactly, which is what licenses using it for the attenuated case.

**Onset's reliability cannot be measured the usual way.** The engine is deterministic per seed, so re-running a
world is not a replication and there is no test–retest estimate to be had. The nearest measurable question is
whether two different sustention rules put the same world in the same place, and the construct record already
answered it: ρ ≥ **0.972** across every pair in every claimed configuration. Treating that agreement as a lower
bound on reliability attenuates the target effect to **0.4757**, and the same rule then asks for **54** worlds per
configuration: **216** in total across the four claimed configurations, co-equal.

**Cost, in the currency the project actually spends.** With the horizon set per world at confirmation + 101
readings, and using Phase L's median confirmation per configuration as the estimate of where fresh worlds will
emerge, the block costs **111,996** cycles — **0.7778** of Phase L's 144,000, for a fifth as many worlds. The
saving is not a trick: it comes from not running every world to a fixed 600 and truncating the follow-up for the
late ones.

**The seed block is proved, not asserted.** `20270601`–`20270820`, **220** candidate seeds, checked at every
build against every integer filed under a seed key in all 71 artifacts that carry one — **192** seeds (an undercount: the walker missed seeds held in lists; **222** is the figure measured in §165), **0
overlap**. A later artifact that consumes one of these seeds breaks the protocol's own test, which is the point:
the check must be run, not remembered.

**Two rules are pre-committed because they close the two doors this project has walked through before.** The
aggregation rule requires the predicted relation in **every** claimed configuration; anything less is *mixed* and
is not supported as stated, so the protocol cannot report whichever configuration performed best. And a censored
world is **never replaced**: the denominator is reported as realised, so a block of 54 cannot quietly become a
search for 54 that worked. If attrition takes a configuration below the 48-world floor, the outcome is
*inconclusive* — never *null*.

**What the reviewer receives includes the corrections.** The package carries the withdrawn Stage A dynamic-range
claim, the 20-of-119 anchor lag, the two runs whose eligibility depends on the sustention rule, the
index-versus-count reconciliation, and the four block-level criteria that failed elsewhere and were reported
rather than re-scored. A record that shows only its final favourable numbers has hidden its reasoning.

**The state is unchanged where it matters.** No seed is allocated, no world is generated, no run is started, and
**no relation between onset and behaviour has been computed** — that remains the whole point of fixing the
predictor first. **Stage B is not authorised**, and §7 of `docs/INDEPENDENT-METHODS-REVIEW.md` is still empty.
The next act is a review, not a run.

---

## 156. A robustness statistic is not a reliability coefficient

**What was wrong.** §155 sized the Stage B block by treating the construct record's **0.972** as a reliability
coefficient in a classical attenuation model: 0.50 was attenuated to 0.4757, and 48 worlds per configuration
became 54. The owner's review caught the substitution, and it does not survive contact with what the number is.
The 0.972 is the rank agreement between onset measured under a 5-cycle and a 20-cycle sustention rule. Those two
measurements come from **the same trajectories**, share nearly all their measurement information, and differ in
*operational definition* rather than through independent random error. The statistic therefore bounds the
rule-choice component of measurement error and nothing else. It establishes that **the ordering of worlds is
robust to the sustention rule**, which is a real and useful fact about the predictor; it does not establish the
reliability of onset, and using it as though it did was a substitution the calculation could not detect because
it is arithmetically well-formed.

**Why there is no measurement to fall back on.** The engine is deterministic per seed, so re-running a world is
not a replication. Onset cannot be given a test–retest estimate, in principle rather than for want of effort.
Any protocol that needs a reliability coefficient here must **declare** one, and declaring one silently — inside a
derivation that looks like arithmetic — is how an assumption acquires the authority of a measurement.

**What the protocol does instead.** It states that reliability is unmeasured, declares a planning assumption,
and prints the entire ladder so the assumption can be replaced rather than argued: reliability 1.00 → 48 worlds
per configuration, 0.90 → 54, 0.80 → 62, 0.70 → 72, 0.60 → 85, 0.50 → 104, 0.40 → 131, 0.30 → 177. The block is
sized at **0.50**, the weakest predictor still worth testing — below it the measure carries less signal than
error — so the block cannot be accused of assuming a good instrument. **416 worlds** in total, at an estimated
**215,696** cycles, **1.4979×** Phase L: larger than the withdrawn 216-world figure, which is exactly the cost of
not assuming a good instrument. If the reviewer accepts 0.70, the block is 288 worlds; that substitution is the
reviewer's to record, not the author's to choose.

**A check found on the way, worth keeping.** The ladder is computed from the copula mapping in
`docs/STRUCTURE-BEHAVIOR-DESIGN.md` §6, `rho_s = (6/pi) asin(rho_g / 2)`, attenuating the *latent* correlation
and mapping back. Implementing it the other way round — attenuating the observed value directly — moves the
target at full reliability and silently asks for 52 worlds where the published floor says 48. Done correctly, the
recomputed ladder reproduces the published table at **every** row (48, 54, 62, 72, 85, 104, 131, 177), which is a
check on both documents; the test asserts each row, so a drift in either the mapping or the rounding shows up as a
failure rather than as a plausible-looking table.

**The two other items, closed as asked.** The candidate block is now **700000001**–**700000420** — a plain
integer block, deliberately not date-like, so no reader mistakes it for calendar values. The **416** worlds are
**pre-assigned** 104 per configuration before any run, the **four** spares (`700000417`–`700000420`) are recorded
as **unused**, and **substitution is prohibited**: a censored world does not release its seed, and the spares are
never drawn. Without that rule the gap between 416 planned worlds and 420 candidate seeds would have been an
ambiguity in the attrition policy rather than a margin. And §3 of the protocol now names the code that defines the
endpoint — `benchmarks/reusable_knowledge.py` for what is scored and `benchmarks/formation_provenance_study.py`
for which transitions are withheld — with the quantum/count gate explicitly still open, because a reviewer is
being asked whether the endpoint can resolve the claim at all.

**State unchanged.** No seed is allocated, no world is generated, no run is started, and **no relation between
onset and behaviour has been computed**. **Stage B is not authorised**, and §7 of
`docs/INDEPENDENT-METHODS-REVIEW.md` is still empty. The withdrawal is recorded in the protocol, the artifact, the
manual and the reviewer's history, because a design record that shows only its final numbers has hidden its
reasoning.

---

## 157. A non-zero count is not a resolution test

**What the review demanded.** The owner accepted the reliability correction and moved the critical question to
the endpoint: is `revision_held_out` fine enough, and variable enough, to resolve the smallest effect the protocol
claims? The request was specific — the quantum computed from the scoring implementation, the distribution of
available withheld transitions, a demonstration that ρ = 0.50 is resolvable, and a rule for an endpoint that
turns out coarse, sparse or undefined.

**What the cells say.** The design-block cells in `docs/reusable_knowledge_calibration.json` carry **82 to 110**
withheld transitions per world, median **106**. The outcome is a proportion over those transitions, so the
quantum is one divided by the count: **0.009434** at the median, with **107** distinguishable levels. Against a
deliberately *tight* outcome spread — an SD of 0.05, about a tenth of what a proportion near one half would have,
so the comparison is a floor rather than a flattering case — the effect gap at ρ = 0.50 is **0.05**, which is
**5.3 quanta**. On this evidence the endpoint is **not too coarse** for the claim.

**What that does not show, stated in the same paragraph.** Two limits, both of which a favourable reading would
want to skip. The cells are **design-block**, declared as such and not confirmatory, so the number describes the
instrument on the worlds that already exist, not on Stage B's worlds. And **granularity is not variability**: the
count bounds how finely the score *can* move and says nothing about whether it *does* move across worlds. A
perfectly resolved endpoint on which every world scores the same produces no relation and no power. Only the run
can show that, which is why the gate stays open.

**So the gate stays open, and gets rules instead of a paragraph.** Four failures are now pre-committed: **too
coarse** (a quantum larger than the effect gap) and **too sparse** (fewer than half the planned worlds at 40 or
more withheld transitions) each stop the run before it starts; **saturated** (a configuration whose realised
outcome SD is below two quanta) is unmeasurable there and is excluded and reported, never scored as a null; and
**undefined** (zero withheld transitions) is excluded by the existing `E6` gate and never zeroed, per AGENTS 13b.
The four-configuration enumeration **is** the gate; §3.1 is the reason to expect it to pass, not the pass.
`resolution_confirmed` remains `false`.

**Three words the owner asked to have separated.** The previous revision said the seeds were "assigned" in one
paragraph and that no seed was "allocated" in another, and both were true of different things: **pre-assigned**
means mapped to a configuration in the protocol, as a plan, with nothing spent; **allocated** means released for an
executed run; **reserved** means deliberately not used, which is what the four spares are. The glossary now says so
in the protocol and in the artifact, because a reader who has to decide whether a protocol contradicts itself has
already stopped trusting it.

**And a qualification on the assumption itself.** 0.50 is a **declared planning assumption, not an established
lower bound**. The argument that reliability below 0.50 leaves more error than signal lives inside the assumed
model; it does not establish that onset's true reliability is at least 0.50, which is unmeasured and unmeasurable
here. **104 worlds per configuration is therefore the requirement conditional on that assumption**, and the
protocol now says so in those words, with the reviewer free to reject the assumption without proposing a
replacement — the ladder prints the consequence of every row so a rejection is a recorded change rather than a
negotiation.

**State unchanged.** No seed is allocated, no world is generated, no run is started, and **no relation between
onset and behaviour has been computed**. **Stage B is not authorised**; §7 of
`docs/INDEPENDENT-METHODS-REVIEW.md` remains empty, and the endpoint gate remains the first thing a reviewer
should interrogate.

---

## 158. A gate that cannot be staffed is not a gate

**The owner's finding.** The independent review was the last thing between a frozen protocol and a run, and the
owner reported it as the thing now stopping the research. He is right about the fact: §2 excludes the author, the
owner, and anyone with a stake, and requires statistical competence, so the candidate pool is small — and **no
eligible reviewer can be found**. An eligibility rule that admits nobody is not a strict gate, it is a closed
door, and a closed door is not a constraint on anything except the project.

**What was decided, and what it costs.** The middle route: a **machine pre-pass** on the frozen protocol, recorded
against a named model and commit; then the owner's dated authorisation; then allocation. Recorded in
`docs/DECISION-STAGE-B-SEQUENCE.md`, stated beside §11 in the protocol's §13 and beside §6 in the brief's §10.

The cost is specific and belongs in the same paragraph as the benefit. The review uniquely caught one class of
defect: an endpoint measuring a different quantity than the claim, an intervention that does not say what it
leaves behind, a build with no stop condition — rule 23's three, found before a cell ran. A model pass buys down
that class **with an instrument that cannot refuse**. Asked whether a plan it has just read is acceptable, it will
find reasons to say yes; the mitigation is adversarial framing, two model families, and the demand that every
number trace to an artifact. That reduces the failure rate. It does not remove it, and the record says so rather
than letting a clean transcript be read as a certificate.

**What did not move, because the temptation is to let it.** §7 stays empty — it records a person, and a signature
filled by a model is fabricated provenance. The §2 criteria are unchanged: they were found unsatisfiable in
practice, not wrong in principle. The pass cannot be cited as the review that preceded the run. And **Stage B is
still not authorised**: no seed allocated, no world generated, no relation computed. The decision is about who
signs and when, and nothing else.

**One repair that came out of the same turn, and it matters more than it looks.** The machine prompt was still
aimed at `docs/STRUCTURE-BEHAVIOR-DESIGN.md` at commit `1051313` — the design record, not the protocol, and a
commit from before the block was resized, the 0.972 was withdrawn, the endpoint's granularity was measured and the
seeds were re-minted. A reviewer following it would have examined a design that no longer exists and never seen a
single correction. It now names `docs/STAGE-B-PROTOCOL.md` and the artifact set the protocol itself hands a
reviewer, and it says which document is inherited rather than under review. **A pointer to the wrong artifact is
the cheapest way to be reviewed and learn nothing**, and it would have been invisible: the prompt looked complete,
the repository was public, and the file it named existed.

## 159. The pre-pass earned its place, and the first thing it caught was a gate measuring the wrong quantity

The machine pre-pass was run on 2026-11-03 and returned three blocking findings. The transcript is
`docs/AI-REVIEW-2026-11-02.md`, recorded against Manus at commit `39adb24`, and it is **one model family** — the
prompt asks for two, so step 1 of the sequence is not complete, and nothing downstream of it may be treated as
complete either.

Three defect classes the independent review exists to catch, found by the instrument that was substituted for it.

**The endpoint-resolution gate was computed for an endpoint this protocol does not have.** §3.1 said the outcome
was "a proportion over the withheld transitions, so the endpoint's quantum is one divided by that count", and
derived a quantum of 0.009434, 107 levels and a 5.3-quanta margin from the design-block cells. The scorer returns
an averaged pairwise log loss: `acquisition_compositional.score()` accumulates binary log loss over each context
source crossed with the vocabulary, divides by the cell count, and `reusable_knowledge.limbs()` stores that as
`revision_held_out`. The model's sentence: "The endpoint is scored as averaged pairwise log loss, but its
resolution is defended as if it were a proportion with a one-transition quantum. The central pre-run check can
therefore pass or fail for the wrong reason." That is rule 23a exactly — a metric carrying another study's
question — and the check was pointing at a scale that does not exist. The quantum, the level count and the
5.3-quanta claim are **withdrawn**; §3.1 now names the scale, says what the withheld count actually buys (the
precision of a per-world mean), and restates the four gate rules on quantities that can be measured: twice a
world's standard error against the effect gap for *too coarse*, realised across-world SD against twice the median
per-world standard error for *saturated*. `resolution_confirmed` was false before and is false now; what changed
is that the sentence behind it is true.

**The pointer sent a reader to a different selector.** §3's table named `formation_provenance_study.py`'s
`held_out_pairs()` and `PHASE_TRANSFER` as the definition of what is withheld. That helper returns that study's
own observed ordered tag pairs; the endpoint is scored on events selected by `reusable_knowledge.py`'s `WITHHELD`
set inside `limbs()`'s `held_only()`. The model: "That helper instead returns observed ordered tag pairs occurring
in the transfer phase; it is not the `WITHHELD` cell-transition rule or the revision-test scoring selector used by
`reusable_knowledge.py`." Fixed in the table, in the artifact's `implementation_to_inspect`, and in the test that
had been asserting the wrong pointer. The related limit is recorded rather than papered over: `limbs()` selects by
fixed phase indices and Stage B's window is onset-relative, so disjointness is established by the pre-run
enumeration — not by reading calibration code.

**The ladder was a closed form, and the analysis is a bootstrap.** §6 sized the block with Fisher's z; §5 builds
its interval by resampling worlds at 98.33 %. The record already contained the discrepancy at one cell and had not
followed it: at 48 worlds and ρ = 0.50 the artifact gives 0.9018 for the closed form and 0.85 for the simulated
bootstrap. The objection was that no result established the promised resolution at the planning point. It is now
measured at every row (`benchmarks/stage_b_resolution_simulation.py`, `docs/stage_b_resolution_simulation.json`),
and the implementation reproduces the existing artifact's 0.85 within Monte-Carlo noise before it is trusted at
0.50. **At the planning row the committed rule gives 0.895 ± 0.008 against the 0.90 bar** — the block does not
clear its own bar at the point estimate; it sits about one standard error from it. Two larger sizes, on the same
rule: 112 gives 0.914 ± 0.010 and 120 gives 0.931 ± 0.009.

**What was not done, and why.** 104 was not quietly raised to 112. The ladder is the published construction, and
sizing it on the bootstrap re-derives every row including the 48-world floor that `STRUCTURE-BEHAVIOR-DESIGN` §6
treats as its reference — that is a change to the design record with a cost in seeds and cycles, and it is the
owner's decision, not an erratum an agent may slip in. It is recorded in §6.3 as **open**, with the prices beside
it. The lesson is the one this project keeps relearning in new clothes: **a closed form tuned to return 0.90 at
every row cannot also be the evidence that 0.90 is reached.** The ladder was never wrong arithmetic; it was
answering for the wrong interval.

**Nothing moved that must not.** §7 stays empty. Stage B is still unauthorised: no seed allocated, no world
generated, no relation computed, the engine and V1 untouched. The transcript is one model family's reading and is
not citable as a review. The sequence is at step 1, and it restarts at step 1 because a blocking finding was
found — which is what `docs/DECISION-STAGE-B-SEQUENCE.md` said would happen.

## 160. The second pass caught a correction that never reached the artifact, and a tie read as a decision

The same model family was run again, this time against `b9c73a7`. It found three things, and all three were true.

**The first is the one worth keeping.** §3.1 had withdrawn the `1/count` quantum, and `stage_b_protocol.py` was
still emitting into the artifact the sentence "the endpoint's quantum (one held-out transition)". The document had
been corrected and the generator had not, so the artifact contradicted the paragraph that describes it — and the
test passed throughout, because it asserted only that `resolution_requirement` contained "does not start". That is
a check that survives the very defect it exists to prevent. A correction is not applied until every place that
**emits** the withdrawn sentence has been changed, and the check must assert the *absence* of the old claim rather
than the presence of a neighbouring one (AGENTS 20 and 24, applied to a generated artifact rather than to a
document). Both are now true: the requirement names the endpoint as an averaged log loss, and the test asserts the
quantum wording is gone.

**The second was mine, and it is the more familiar failure.** The simulation's own Monte-Carlo standard error spans
the 90 % bar at both 104 (0.895 ± 0.008, 0.7 SE below) and 112 (0.914 ± 0.010, 1.4 SE above). The protocol said 104
"does not clear" and that 112 and 120 "both clear". That was wider than the check: at its own precision the
simulation separates only 120 (3.6 SE). What it establishes is a direction of bias in the closed form and a price
for each size; what it does not establish is which side of the bar 104 and 112 are on, and the document no longer
says. The same pass caught the artifact's claim that 300 bootstrap replicates instead of 10,000 is "slightly
conservative" — an assertion nothing measured. It is replaced by the mechanical fact (the lower edge is the 3rd
smallest of 300 replicates, where 10,000 give the 84th of 10,000) and by an explicit statement that the direction of
the bias is unmeasured.

**The third reconstructs the gate's arithmetic**, and it is the one that changes a rule rather than a sentence.
`2 × 0.50 × 0.05` is a linear-model contrast between two worlds two across-world SDs apart in onset; a rank
correlation does not imply it, and the artifact now carries the three conditions beside the number instead of
presenting it as derived. More seriously, `score()` averages pairwise binary log loss over every context source
crossed with the vocabulary and returns one rounded `ll / n`, so the 82–110 withheld transitions are not 82–110
independent contributions: they are the denominator of a per-world mean, and the SD of scored cells divided by
`√cells` was never the per-world standard error the `too_coarse` rule needed. That substitution is withdrawn. The
granularity gate now reads **open** rather than *informed*, two of its four rules are recorded as not evaluable
before a precision measurement exists, and §5 requires each configuration to report the realised across-world SD
and a per-world standard error from a cluster bootstrap over withheld transitions before any interval is read.

The block-size decision is untouched and still the owner's: nothing here selected a size. And two passes from one
family are still one family — the same reader twice, which is what the two-family rule exists to prevent. Step 1 of
the sequence remains incomplete. **Stage B remains unauthorised:** no seed allocated, no world generated, no
relation computed, engine and V1 untouched.

## 161. The gate now has a method, and the method says the answer depends on a distribution that does not exist yet

The second pass left `too_coarse` unable to be evaluated: `s/√N` over scored cells was a substitution, because
`score()` averages context x source x vocabulary cells and the withheld transitions are not independent
contributions. So the gate was written as **undetermined** and the next step was to build the measurement it names,
not to argue about the number.

`benchmarks/stage_b_endpoint_precision.py` does exactly that and nothing more. Each withheld transition is a
cluster — its cells move together, because the same vocabulary is scored under every transition — and the world's
score is a ratio estimator, so the bootstrap resamples transitions and recomputes the ratio. It runs on the five
consumed calibration cells, with no engine and no seed, and it reproduces the house scorer's aggregate exactly, which
is the check that it is measuring the same quantity rather than a similar-looking one.

At first the gate looks passable. Twice the per-world standard error is **0.009 to 0.011 nats** when the readout is
the exact latent rule — comfortably inside the 0.05 gap — and the cell-level `s/√N` would have agreed, since
clustering makes it *smaller* there (0.6×). But the benchmark's own control tells the other story: with the
wrong-law readout, the failure the task exists to catch, twice the standard error is **0.059 to 0.071**, above the
gap, and the cell-level figure is now **1.4×** too small. The two readouts bracket plausible quality and the bracket
**straddles** the gap.

That is the finding, and it is better than a pass would have been. The gate's answer is not a property of the
count; it is a property of how heavy-tailed the readout's losses are, and that distribution does not exist until a
world runs. So a pre-run gate stated on precision alone would have been passing or failing on an assumption wearing
a measurement's clothes — the same defect as the quantum, one level up: the old rule borrowed the count, this one
would have borrowed the ceiling. The gate stays **undetermined** for Stage B, the method is discharged on
design-block cells, and §5 requires the same cluster bootstrap on the claimed configurations, reported before any
interval is read.

Stop condition, declared so this does not become a programme: the probe is closed once it reports per-world
standard errors for the five design-block cells under both readouts. It may be fixed if found wrong, not extended.
**Stage B remains unauthorised** — no seed allocated, no world generated, no relation computed.

## 162. The block is 120, and the rule that chose it was written before the number was read

The owner delegated the block-size decision and asked for a recommendation, so the first thing to fix was the rule,
because a size picked after looking at which one clears is the defect the project keeps finding elsewhere.

The tension is now explicit. The ladder solves the block in Fisher's z; the analysis resamples worlds; and the
simulation of the committed rule puts the ladder row at **0.895 ± 0.008** against a 0.90 bar. So 104 does not fail —
its interval spans the bar — but it does not clear it either, and a design whose own declared analysis sits at its
own declared bar is a design that will be read as underpowered no matter what the run shows. Raising it by "the
first size that clears" would be arbitrary; 112 clears on the point estimate and not on its lower bound, so that
rule would pick 120 only by luck.

The rule therefore reads the lower bound: **the smallest tested size whose lower 1.96-sigma Monte-Carlo bound
clears 0.90**. At 112 that bound is 0.894, below the bar; at 120 it is 0.914, above it. 120 is chosen, by code
(`block_floor_rule` in `docs/stage_b_protocol.json`), with the build failing if no tested size qualifies. Two honest
limits: only 112 and 120 were ever simulated, so the rule selects among tested sizes rather than among all integers,
and 120 is therefore the smallest *tested* size that qualifies; and the rule is not a power calculation — it is the
project's existing simulation, read at its lower bound instead of at its point estimate.

What it costs and what it does not change. 480 worlds instead of 416, 248,880 cycles instead of 215,696
(**1.7283×** Phase L instead of 1.4979×), seeds 700000001–700000480 pre-assigned 120 per configuration, the four
spares now 700000481–700000484. The ladder is untouched — the 48-world floor and every row, including the 104 at the
planning assumption, stay as published — because editing the ladder to match the block would destroy the one
artifact that lets a reader recompute the block without trusting the prose. Jumping to the ladder's next row (131 at
an assumed reliability of 0.40) was rejected for the same reason the assumption matters: it would claim a worse
instrument than the protocol declares.

**Stage B remains unauthorised.** No seed is allocated, no world was generated, and no relation between onset and
behaviour has been computed.

## 163. The block is 180, because the rule should have governed the conjunction all along

The second machine-family pass made one observation that survived checking, and it invalidates the number I recorded
a few hours earlier. The ladder's bar is stated per configuration — "90 % of blocks must resolve a relation of that
size" — but §7's outcome table requires the predicted sign with an interval excluding zero **in every claimed
configuration**. The claim's success criterion is a conjunction, so the probability that the study can report its own
required result is the product across the four configurations, not the per-configuration share the ladder prints.

At 120 that product is `0.931⁴ = 0.752`. I had sized the block on 0.931. That is not a rounding disagreement; it is a
one-in-four chance of spending the block and being unable to report the criterion it was sized for, and it is the
same substitution the project keeps catching elsewhere — a quantity read at the wrong scope.

The rule was therefore restated and re-applied before any world ran: **the smallest tested size whose lower
1.96-sigma bound on `p⁴` clears 0.90**. The simulation already had the rows to price it. 112 → 0.914 per
configuration, conjunction 0.697; 120 → 0.931, 0.752; 150 → 0.975, 0.904 with a lower bound of 0.847; 160 → 0.978,
0.913, lower bound 0.859; 180 → 0.998, 0.990, lower bound **0.971**; 200 → 0.995, 0.980, lower bound 0.953. 150 and
160 are the rows that justify a lower-bound rule: both clear 0.90 on the point estimate and neither clears it on the
lower bound.

So the block is **180 worlds per configuration — 720 worlds, 373,320 cycles, 2.5925× Phase L**, seeds
700000001–700000720 with four spares at 700000721–700000724. That is 2.7 times the 104-world ladder row, and the cost
is the price of a claim that needs all four configurations rather than an average of them.

Two limits, recorded rather than implied: only the six tested sizes were simulated, so 180 is the smallest tested
size and not provably the smallest; and the multiplication assumes the configurations resolve independently, which
follows from each being its own worlds under its own seeds — a coupling would make the estimate optimistic.

The ladder remains untouched, including the 48-world floor and the 104 at the planning assumption, because a reader
must be able to recompute the block without trusting my prose. `block_floor_rule.by_size` now carries both quantities
for every tested size, so the conjunction can be checked against the per-configuration share directly.

**Stage B remains unauthorised.** No seed is allocated, no world was generated, and no relation between onset and
behaviour has been computed.

## §164 — The seed-disjointness scan's width is measured, not assumed (2026-11-03)

A further machine pass reported that the seed-disjointness scan is incomplete. The scan is real and it is narrow: it
reads every `*.json` directly under `docs/`, and nothing else. `docs/` has no subdirectory, so today nothing is missed
— but "nothing is missed" was an assumption about where artifacts live, held in the same place as a check that is
supposed to be mechanical, which is exactly the arrangement rule 20 warns about.

The fix is not a wider prose claim. `benchmarks/stage_b_protocol.py` now runs the identical rule over every other
JSON in the tree (excluding `.venv`, `.scratch`, `artifacts` and caches) and records two facts in
`docs/stage_b_protocol.json` under `seeds.scan_outside_docs`: how many files it read, and which of them name a seed.
The block-disjointness assertion is taken against the union, so a stray artifact outside `docs/` cannot slip a builder
seed past the check unnoticed. On this tree the union adds nothing — the consumed figure stays at 192 seeds across 71
docs artifacts — which is the point: the narrower scan is now licensed by a recorded measurement rather than by
memory. `docs/STAGE-B-PROTOCOL.md` §9 states the scope and the reason, and `tests/test_stage_b_protocol.py` asserts
that the outside-docs field is present, empty and consistent with the block.

Three other claims in the same pass were checked against the code and are not defects at HEAD: the `1/count` quantum
was withdrawn at `e6334dc` and the artifact now forbids stating the requirement that way; the 0.50 reliability is
already declared a planning assumption and explicitly "unmeasured" in §6; and the `b9c73a7` record's parentage is
correct — `e6334dc` is that commit's parent, not a sibling. The pass's transcript is not in the repository, so its
findings are recorded here by disposition and not quoted.

## 165. The seed scan's walker was itself wrong, and forty seeds were invisible to it (2026-11-03)

The previous entry recorded a correction to the seed-disjointness scan's *width*. Re-reading the first Manus pass
showed the sharper defect underneath it, in the walker: `_consumed_seeds()` descended into lists but collected an
integer only when it sat directly under a seed-naming key, so an artifact storing `{"seeds": [1000, 1001]}` — the
commonest shape in this corpus — contributed nothing. The published "192 consumed seeds across 71 artifacts" was an
undercount, not a fact, and it was quoted in the protocol, in the manual, and in the journal entry that reported the build as though it were a measurement.

Measured with a walker that pulls every integer under a seed-naming key however deeply it nests, and excluding
`docs/stage_b_protocol.json` (which records this block and would otherwise overlap itself): **222 seeds across 75
artifacts**, and **0 overlap** with the 724-seed block — still none, which is why no seed moved and the block stands.
Forty seeds across eight artifacts had been invisible, including the whole `reusable_knowledge_gate_definitions.json`
seed set and 30 in `use_path_diagnostic_freeze.json`.

The lesson is the one the repository keeps relearning: a check that walks a structure must be tested on the shape the
corpus actually uses, not on the shape it is easy to imagine. `_harvest_seeds()` is now that shape, the union with
artifacts outside `docs/` is what the overlap assertion runs against, and `tests/test_stage_b_protocol.py` derives the
prose figure from the artifact so the sentence cannot drift from the number again. **The finding was correct when it
was made and it stayed correct for three days while two passes read past it** — the quantum finding in the same
transcript was stale, this one was not, and only the code could tell them apart.

## 166. The owner authorised Stage B on two words, and the record is where the two words are expanded (2026-11-03)

The owner authorised Stage B: *"i authorize it"*, given in reply to the statement that step 2 of the sequence was
the only open step and his alone. The decision is recorded in `docs/AUTHORISATION-STAGE-B.md`, dated, against commit
`d16d8ae`, with the scope taken from the protocol's own §D6 checklist rather than from the agent's sense of what he
probably meant.

What that authorises is specific: four configurations, 180 worlds each, 720 worlds, 373,320 cycles, seeds
`700000001`–`700000720`, four spares never drawn, substitution prohibited, and the predictor, endpoint, falsifiers,
outcomes and analysis exactly as committed. What it does not do is equally specific, and each item was written
because the authorisation could otherwise be read as covering it: it **allocates nothing**, it does **not** answer
the precision gate, it does **not** decide a configuration's eligibility, it does **not** turn the 0.05 effect gap
into an identity, and it does **not** fill §7 or make the three machine passes an independent review.

**The sequence now stops at step 3 for a mundane reason: there is no harness.** `benchmarks/` holds the protocol
generator, the resolution simulation and the endpoint-precision probe. None of them generates a Stage B world or
scores an endpoint, and the parameter space the protocol fixes puts the sample well beyond a unit test — 720 worlds
with per-world horizons of 100 behavioural cycles plus confirmation. So the authorisation permits a run that cannot
yet start, and writing the runner is the next piece of work rather than an afterthought to the signature.

One property of the record is deliberate and worth stating here: it says that the wording is the agent's and the
decision is the owner's, and that it **may be narrowed before the run but not widened afterwards**. A two-word
assent does not enumerate six conditions, and the honest way to record it is to name the checklist it is being read
against, mark who wrote which part, and give the owner the chance to cut anything he did not intend.

## 167. The predictor and the outcome live in different worlds, and that is where the run stops (2026-11-03)

Building the runner for the authorised campaign found the defect that no amount of harness code can fix. `DI` — the
predictor — is `late_retained / late_available` against the Phase L scale-stream family, which is why §2's eligibility
table can quote median onsets of 539, 404, 362 and 329 cycles: those are 600-cycle worlds with an early group and a
late group. `revision_held_out` — the outcome — is the compositional cell family's revision-test score, on cycles
250–299 of a **300-cycle** world with a rotated law and two withheld cell transitions.

The compositional world has no early or late group, so `DI` is undefined there; the scale world has no revision phase,
so the outcome cannot be scored there. `docs/STRUCTURE-BEHAVIOR-DESIGN.md` §5 names the compositional family as
primary; the protocol's four configurations and their onset statistics come from the scale family. And the clocks
settle it: §4 puts the behavioural window at confirmation + 1 to + 100, while the fastest configuration confirms at a
median of 329 on a world that ends at 300. **The specified run would not produce a weak result — it would produce no
observation.**

This is a design defect found after authorisation and before allocation, which is the cheapest place to find one. It
does not weaken the claim, the block, the endpoint's definition or the authorisation. It does mean the next move is a
dated owner decision between two repairs that are not interchangeable: keep the predictor and define a new held-out
endpoint on the scale stream (which then needs its own resolution check), or keep the endpoint and define onset on a
quantity that exists in the compositional world (which discards `DI`, §2's table and the block's derivation). A
harness cannot make that choice, and a harness written with either default would be choosing the experiment after the
authorisation — the exact defect this project keeps finding in its own work.

## 168. The withheld set saturates, so option A needs a world that withholds by construction (2026-11-03)

Option A redefined Stage B's outcome on the family the predictor lives in: `held_out_next_tag`, mean pairwise log
loss on the behavioural test window over ordered tag transitions formation never exhibited. The first thing measured
was the size of that set, and it is zero on every design-block cell in every configuration: the formation window
already contains every ordered pair the test window uses. The scale-stream vocabulary is small and twelve events a
cycle for a few hundred cycles saturate the pair space, so "transitions the organism never saw" is an empty category
there.

This is the useful kind of null. It says the withholding cannot be a **scoring** rule on this family; it has to be a
**world** rule — declare the transitions, refuse them during formation by conditioned sampling — which is exactly what
the compositional family does and why its endpoint had a non-empty scored set. It also says the world so built is a
different stimulus, so it inherits the obligations that came with `WITHHELD`: criteria written before the enumeration,
a degeneracy audit proving reachability and a live axis, and its own precision measurement once the set is non-empty.

No seed was spent, no world generated and nothing about the claim, predictor, block or authorisation moved. The gate
that matters is unchanged and still open, and it is now open on a named piece of work.

## 169. The withheld set exists now, and the audit that made it existable had to fail first (2026-11-03)

§168 said withholding on the scale stream could not be a scoring rule, only a rule of the world. The world now
exists: one declared directed entity transition, `early_0 -> late_0`, refused by resampling while the organism is
exposed and permitted from the test window on, so the stream keeps its length, its timing and its adjacency. 16
ordered tag pairs follow by construction — absent from formation (0) and present in the behavioural window (88),
while an open world's formation shows 288 of them — with 82 compensations standing as proof the intervention fired.

Two things about how it got here are worth keeping. **The first version withheld the transition for the whole run**,
which is the obvious way to write it and the wrong one: the test window then had no withheld transition either, and
the audit returned `the_scored_set_is_reachable: false` instead of a score. A score would have been meaningless and
plausible-looking; the check that refused to produce one is the only reason it is not in the record. **The second
version's audit ran in a world shorter than its own window position**, and the empty slice again read as an empty
scored set until the audit sized its world to the window it measures. Both were caught by the same five predicates,
which is what a degeneracy audit buys when it is written before the number it guards.

The precision gate now has a basis: twice the per-world standard error is 0.0019 to 0.0067 nats over 200
cluster-bootstrap replicates on twelve design-block cells, against a 0.05 gap. And the block moves rather than lifts:
the outcome has a world, the predictor does not, because this world is a reconstruction of the scale family rather
than the frozen generator and **no `DI` onset has been measured on it**. Placing onset on this family is now the only
thing between the authorisation and a run.

## 170. The onset harness exists and has produced nothing, which is the honest state of it (2026-11-03)

§169 left one measurement between the authorisation and a run: `DI` onset on the world that carries the outcome. The
instrument for it is written -- frozen engine over the withholding world, per-cycle `DI` trace, the protocol's onset
rule with the 5- and 20-cycle rules carried beside it, censoring rather than boundary placement, an early stop a
margin after the onset found, and a wall-clock budget.

It has produced no onset. A 40-cycle probe took 8.24 s; a 160-cycle cell did not return inside this environment's
command limit, and neither did a 430-cycle cell nor four cells in parallel. Per-cycle cost is not linear over that
range, and the limit kills the process whether or not it is detached -- so the obstacle is a machine that will not run
a cell to completion, not a question about the design.

The temptation is to write the measurement up from a short world, or to report the short probe's zeros as a missing
onset. Both would be fabrications: a compressed world is a different world, and a trajectory that stops before the late
group has had time to be learned has not shown that onset is absent -- it has shown that the run stopped. So nothing is
reported, the predictor stays unmeasured, `status.blocked_before_run` stays true, and the module is committed with the
budget flag so the measurement is one unattended run away.

## 171. The resumable onset measurement completed on the withholding world (2026-11-03)

The harness was made resumable and run in bounded sessions. It completed all twelve cells on the three consumed
design-block seeds, with no seed from the confirmatory Stage B block allocated. The full per-cycle trajectories and
cell records are in `docs/stage_b_onset_withholding.json`. All 12 cells had a qualifying 10-cycle onset; the 5-,
10- and 20-cycle rules agreed in every cell; each configuration had three distinct onsets. The medians were 530
(`2:1`), 309 (`3:1`), 276 (`4:1`) and 226 (`6:1`) cycles, with ranges 91, 49, 40 and 14 cycles. The configuration
medians differ by 304 cycles.

This is the predictor measured on the reconstructed withholding world only. It is not the Phase L onset distribution,
does not score the behavioral outcome, and establishes no predictor–outcome relation. It does not clear the protocol's
other recorded blocker or authorize the confirmatory run. The earlier entry above records the truthful state before
this measurement was completed; it is superseded on that status point by this entry, not erased.

## 172. The resume path is proven, and one planned horizon is too short for a measured onset (2026-11-03)

The resumable harness was the last untested part of the onset instrument: a cell can outlive a command limit, so it
snapshots the engine database every ten cycles, writes the `DI` trace every cycle, and on the next run resumes from the
snapshot and replays the tail. `tests/test_stage_b_onset_resume.py` now pauses a cell one cycle after its snapshot and
requires the resumed trajectory to equal the uninterrupted one cycle for cycle, with the world shortened so that `DI`
varies; it also requires a resume whose database was not restored to be refused or to diverge, and it shows both refusal
guards fire (progress without a snapshot; a checkpoint from other inputs).

Two mutations were run against the module rather than argued about. Deleting the tail replay, and deleting the restored
RNG state, both leave the trajectory **unchanged** on that world, so those two variants are equivalent
re-implementations and no behavioural test can tell them apart. The second is explained rather than merely observed:
`organica/sleep.py` draws from `_rng` in exactly one place, `_stochastic_retain`, which runs only under
`HYPOTHESIS_RETENTION = "stochastic"`. The engine's default is `salience` and no Stage B module changes it, so the
`rng_state` field in every checkpoint of this harness is a snapshot of a generator nothing draws from -- harmless, and
load-bearing only once a stochastic retention arm exists. The defect the equality check exists for is a resume from a
substrate that was never restored, and that one is caught.

The same pass read the completed artifact against the protocol's own clock and found a cell the horizon does not cover.
§4 fixes the horizon per world at confirmation + 101, and the harness plans each world at its configuration's Phase L
confirmation index: 539 for `2:1`. Of the **12** measured cells, **11** have `onset + 101` inside the world
built for them and **1** does not: `2:1` seed **20261023** confirms at **602**, which needs **703** cycles
against the **640** built. It is also the only cell whose onset arrives after the withholding lifts at
confirmation + 50 (**589**), so its `DI` onset may be a response to the intervention being released rather than
development under it. Nothing is re-scored and no constant is changed: these are consumed design-block seeds, no Stage B
seed was allocated, and whether a world is built to a high quantile of onset, to a per-world horizon, or under an
eligibility rule that excludes a truncated follow-up is a design decision for the owner. Journal §171's completion
stands; this entry adds what the measurement implies for the run's clock.

## 173. The three Stage B decisions are recorded, and none of them allocates a seed (2026-11-03)

The owner approved the three actions §172 and §D12 left open. They are now recorded against the artifact rather
than in prose alone, and each one is a decision about permission and design, not a new measurement.

**The world family.** The run uses the withholding world, and `revision_held_out` is scored there on its declared
withheld tag pairs at the world's own behavioural window. The two quantities that §D8 found defined in different
families now live in one world: `DI` onset is measured on it and the withheld endpoint's per-world standard error
is measured on it. `status.blocked_before_run.blocked` is false, with the world named and the reason the run
still cannot start recorded beside it -- no runner exists, no seed is allocated, and the eligibility rule is not
implemented in a runner.

**The horizon.** The rule is an eligibility rule rather than a longer block: a world is eligible iff
`onset + 101 <= its horizon`, and a world whose follow-up would not fit is reported with its onset and horizon
and excluded from the relation, never truncated. On the twelve measured cells it excludes **1** (`2:1`, seed
**20261023**, onset **602**, horizon **640**). No horizon, block size, seed or total changes: the block stays at 720
worlds and 373,320 cycles. What is bought is that no follow-up is ever short; what is given up is that
late-emerging worlds leave the relation, which is the direction the design cares about most, so the exclusion
count is reported per configuration rather than absorbed.

**The granularity gate.** Confirmed, on the measurement rather than on an argument: twice the per-world standard
error is **0.0019 to 0.0067** nats against the 0.05 assumed gap, in every design-block cell of the withholding world,
across the four claimed configurations. `resolution_confirmed` is true with the evidence named beside it, and the
two limits are kept: the cells are design-block, and the saturated rule still consumes the run's own precision.

Nothing here re-scores a result or reopens a verdict. The onset measurement remains what §171 recorded, the block
remains unallocated, and the next act is the runner's -- not the analysis's.

## 174. The Stage B runner exists, and it refuses to spend an unallocated seed (2026-11-03)

The last item between the recorded design and worlds existing was an executor. `benchmarks/stage_b_runner.py` is that executor, and it is deliberately narrower than a campaign script: it takes one world at a time, records the per-cycle `DI` trajectory, applies the protocol onset rule through the harness's own sustained-run detector, applies §4's eligibility rule (`onset + 101 <= horizon`), and only then scores the outcome -- the withheld pairs that occur in the world's own behavioural window, with the readout frozen at onset and no refit. `revision_held_out` is the house pairwise log loss on that window, and a window with no withheld pair is not measurable rather than zero.

The analysis is §5's, implemented once: Spearman within configuration, a percentile bootstrap over worlds at 98.33 %, the standardised slope beside it, a permutation control, and a structural-size baseline, with the claim supported only if the predicted relation holds in **every** configuration. A configuration short of that is MIXED, and the artifact says why: the number of configurations satisfied is not a score.

The guard is the part worth defending. The 720 seeds are pre-assigned, not allocated, and the runner refuses any pre-assigned seed until `docs/stage_b_allocation.json` records the allocation; the four spares are refused unconditionally. Its self-test (11 controls, no engine) checks that both refusals fire, that the eligibility boundary is exact, that an empty window is not measurable, that a planted relation is detected, that the permutation control on the same data includes zero, that a flat outcome is not detected, and that one configuration short of the conjunction reports MIXED rather than SUPPORTED. No confirmatory world ran and no seed was allocated; a smoke run on a consumed design-block seed exercises the engine path.

## 175. The smoke run found the window in the wrong place, and the fixed window is the one (2026-11-03)

The runner was committed with a claim I had not executed -- that a smoke run on a consumed design-block
seed exercises the engine path. Executing it found a defect rather than confirming the claim.

The first version placed the behavioural window at the **measured** onset plus learning, which follows
§4's sentence that "the window follows the event". Against this world that is unimplementable: the world is
generated before any onset is measured, and its declared transition is released on the **planned**
confirmation clock, so a window placed at an early onset sits inside the withheld period. The cell returned
**0** withheld occurrences and the outcome was reported not measurable -- correctly, as not measurable rather
than zero, which is the only reason the defect was visible instead of silent.

The window is now the protocol's fixed one: learn the 50 cycles after the planned confirmation, then test
the next 50. With that placement the same cell scores: onset **233** -- the same onset
`docs/stage_b_onset_withholding.json` records for it -- **32** withheld
occurrences over **896** scored cells, mean loss **0.148461**. The record is
`docs/stage_b_runner_smoke.json`, labelled as not a measurement.

What this does **not** change: the predictor, the endpoint's definition, the eligibility rule's arithmetic
(`onset + 101 <= horizon` is now read as "the onset precedes the window", which the same inequality gives),
the block, the seeds, or any verdict. What it corrects is a sentence's reading and one module's
implementation, and it is disclosed because an implementation that quietly chose a different window would
be choosing the experiment after the authorisation.

## 176. The runner can use the machine's workers, and the guard still refuses before any of them start (2026-11-03)

The executor was sequential and restarted from zero. Both were chores, not design choices, and both are
fixed in `benchmarks/stage_b_runner.py` without touching the protocol.

**Resumption.** Each cell is written to `cell_<configuration>_<seed>.json` as soon as it finishes, and
`--cell` reloads it before running anything (`--no-cache` forces a re-run). `--all` treats a cached cell as
done **only if it completed**: a cell that stopped at its time budget is `complete: false`, so a paused cell
stays pending and the next invocation continues it rather than skipping a world that never finished. That
distinction is a test, not a comment.

**Workers.** `--workers N` runs the cells through a process pool. The order of operations is the point: every
job's seed passes `assert_runnable` **before the pool is constructed**, so an unallocated block or a reserved
spare refuses the whole batch without starting a single worker. A guard that fired inside the workers would
have spent work before refusing, and a run that spends anything must have been authorised as a whole. Each
cell now records its `pid`, so parallelism is visible in the artifact instead of inferred from timing.

**Smoke, on consumed design-block seeds only.** Two `6:1` cells at two workers reproduced the sequential
onsets exactly -- seed 20261024 onset **219**
(`pid` 13723) and seed 20261025 onset
**226** (`pid` 13724) -- matching
`docs/stage_b_onset_withholding.json` for both. Wall clock **115.1** s against **228.78** s of
engine time summed over the two cells, i.e. the two cells really overlapped. The record is
`docs/stage_b_runner_smoke.json` under `parallel_smoke`, labelled `not_a_measurement`.

What did not change: the endpoint, the predictor, the eligibility rule, the block, the horizons, the seeds or
any verdict. Nothing confirmatory ran, no seed was allocated, and `--all` still refuses until the owner
creates `docs/stage_b_allocation.json`.

## 177. One configuration ran end to end, and the analysis refuses to turn three design cells into a claim (2026-11-03)

The executor had never produced an analysis at all: cells ran, nothing consumed them. The three `6:1`
design-block cells are now scored and assembled -- seed 20261024 onset **219** loss **0.149471**, seed 20261025 onset **226** loss **0.151855**, seed 20261023 onset **233** loss **0.148461** -- and
`benchmarks/stage_b_runner.py --assemble --out docs/stage_b_runner_design_block.json` reports
Spearman **-0.5** on 3 scored cells with a 98.33 % interval
**[-1.0, 1.0]**, slope **-0.2898**, permutation interval **[-1.0, 1.0]** and a
size baseline of **-0.5**.

The sign agrees with the prediction for these three worlds (earlier onset, lower loss in two of three pairs),
and that is worth exactly nothing: with three points the interval spans the whole range of the statistic, so
`predicted_sign_held` is false and no configuration can satisfy §5's conjunction.

**A defect the assembly exposed, and the labelling fix.** The aggregator returned **NOT SUPPORTED** for an
assembly covering 1 of the four configurations, because its last branch fires whenever no claimed
configuration holds the sign -- including when most configurations never ran. That string is a claim about the
hypothesis, and it was being produced by an assembly that had not run the protocol. The rule now returns
**NO VERDICT: PARTIAL ASSEMBLY** whenever fewer than all four configurations carry worlds. This is disclosed
as a change made **after** the assembly was read: it removes a claim rather than adding one, it changes no
threshold, endpoint, seed or executed result, and every previous branch -- all four holding, one short, none
holding, no world -- is unchanged and still exercised by the self-test.

**What this is not.** Three consumed design-block seeds, one configuration, and not a measurement of anything
the protocol claims; the artifact says so in its own `what_this_is`. No seed is allocated, no confirmatory
world exists, and `--all` still refuses until `docs/stage_b_allocation.json` is created by the owner. The
assembly was written to its own path so `docs/stage_b_runner.json` stays reserved for an actual run.

## 178. The design-block assembly is a seventy-sixth artifact, and the prose figure had to follow it (2026-11-03)

Writing `docs/stage_b_runner_design_block.json` was the first time this thread added an artifact that names
consumed seeds, and the protocol's own scan noticed: the artifact count behind the disjointness proof went from
**75** to **76**, because the assembly names seeds 20261023, 20261024, 20261025.

**Nothing else moved.** The three seeds were already in the corpus, so `consumed_total` stays **222**, the
overlap with the candidate block stays **empty**, and the block, the spares and the sample size are untouched.
The count that changed is a count of *files read*, not of seeds discovered -- a distinction worth stating,
because "76 artifacts" beside "222 seeds" invites the reader to assume a new seed arrived.

The prose sentence in `docs/STAGE-B-PROTOCOL.md` §10 had to be regenerated because it is **quoted from the
artifact by a test**: `test_the_seed_block_is_preassigned_spares_named_and_substitution_closed` builds the
sentence from `consumed_total` and `disjoint_proved_against` and asserts it appears in the protocol. It failed
the moment the artifact changed, which is the guard working -- the sentence cannot drift from the number, and a
reader was not the one who caught it. The two full-suite failures this produced were reported honestly rather
than hidden by re-running until green: the first test run after the commit failed, the artifact was regenerated
from its own generator, and the prose was updated to the regenerated figure.

## 179. The block is a day's serial work on this machine, and the projection says what it cannot see (2026-11-03)

The three design cells make the block's cost answerable, and `benchmarks/stage_b_runner.py --estimate`
answers it from those cells rather than from a guess: 20261023 (101.0 s over 429 cycles), 20261024 (114.92 s over 429 cycles), 20261025 (113.86 s over 429 cycles). Each of them processes
`cycles_run + 50` = 429 cycles (the confirmation clock, the learning window, the test window), giving
**0.235431** to **0.267879** seconds per cycle with a mean of **0.256239**.

Projected over the block's **720** worlds -- **366120** cycles, since each configuration's horizon is
its confirmation clock plus the 101 windows -- that is **26.06** h serial (range **23.94** to
**27.24** h from the three observed rates), or **26.22** / **13.11** / **6.56** /
**3.28** h at 1, 2, 4 and 8 workers on this 8-CPU VM. Per configuration: `2:1` 8.19 h, `3:1` 6.46 h, `4:1` 5.92 h, `6:1` 5.5 h.

**What the projection cannot see, stated in the artifact itself.** Cost is assumed proportional to cycles
processed. That assumption is untested by construction: all three measured cells are the same configuration
and therefore the same cycle count, so nothing here distinguishes a per-cycle cost from a per-world cost, and
world generation is charged at the cycle rate because three cells cannot separate the two. The efficiency
factor **0.994** is measured at two workers only; the four- and eight-worker rows assume
it holds.

**Why it was worth writing down.** The block was previously an open-ended cost, and a cost nobody has
estimated is a reason not to start. At **3.28** h on this machine the block fits inside a working day
with eight workers, or a little over a day as four batches at four workers; that is a fact the owner needs
before deciding whether to allocate, and it changes nothing about whether the run is authorised. The estimate
is `docs/stage_b_cost_estimate.json`, `planning_only` and `no_seed_allocated` are both true in it, and no
confirmatory world exists.

## 180. The cost is not exactly per cycle, and the check that says so is weaker than it looks (2026-11-03)

§179 projected the block from three cells of one configuration and said, in the artifact, that it assumed cost
is proportional to cycles. That assumption is now tested, and it **fails the rule it was given**: cost per
cycle is not the same across configurations.

The cells: 10 cells over four configurations, two or three each. Per-configuration rates are
`2:1` **0.282144–0.318279**, `3:1` **0.298313–0.31119**,
`4:1` **0.295498–0.295563**, `6:1` **0.235431–0.270373**,
so no single interval covers all four and `proportional_within_measured_range` is **false**. The fitted
intercept is **-33.93** s and the fit is worth little either way: every cell sits at one of
four cycle counts, so the slope (**0.354538**) is carried almost entirely by the
between-configuration differences it is supposed to detect.

**The confound, stated because it is not in the cells.** The measurements were taken under different loads --
one cell alone, some at two workers, some at four -- and a cell records no worker count. So the gap between
`6:1` and the rest may be configuration or may be contention. One pair was measured in the same session at the
same worker count: `2:1` seed 20261025 at **185.79** s over 639 cycles
(**0.290751** s/cycle) and `6:1` seed 20261025 at **115.99** s over
429 cycles (**0.270373**), a **7.5 %** difference with `6:1` cheaper. That
is the largest horizon gap in the block, so the constant-rate model is right to about that much and no better.

**The estimate is therefore revised, not defended.** With all 10 cells the mean is
**0.286542** s/cycle, giving **29.14** h serial
(range **23.94–32.37**) and
**29.32/14.66/7.33/3.67**
h at 1/2/4/8 workers. §179's **26.06** h is **superseded**: it came from the three `6:1` cells, which are the
cheapest per cycle of the four configurations, so it was optimistic by the amount this check measures.

What the check cannot do: it cannot separate a per-cycle from a per-world charge, because no cell varies its
cycle count inside a configuration. A sharper design would run one configuration at two different learn-window
lengths, and that would change the protocol rather than measure its cost.

## 181. The owner allocated the block, and the guard's own control had to be re-pointed (2026-11-03)

The owner asked for the allocation record. `docs/stage_b_allocation.json` now records **720** seeds,
**700000001**–**700000720**, in four chunks of 180, with the four spares **700000721**–**700000724**
excluded and `substitution_allowed` **false**. The seeds were copied from
`docs/stage_b_protocol.json`'s `seeds.preassigned` by `range(first, last+1)` and never typed, and the file
records who allocated it, when, against which authorisation, and that **it runs nothing**: a seed is spent when
its world is generated.

**A defect the allocation exposed, in the control rather than the guard.** The self-test's first check was
"`assert_runnable(700000001)` must raise", i.e. it read the *live* record. That was a correct control while
nothing was allocated and it becomes a **failing** control the moment the owner does the authorised thing --
the check would have reported the guard as broken for behaving correctly. `assert_runnable` now takes an
optional `record`, and the control asks what the guard does under an empty allocation, under a record that
names the seed, and under one that does not. The lesson generalises past this file: **a control that reads
production state measures the state, not the rule**, and it inverts exactly when the state changes for good
reasons. The batch-level test that the guard refuses before any worker starts now installs an empty record the
same way.

**The record is checked against the pre-assignment, not trusted.** A new test rebuilds the block from the
protocol artifact, asserts the record equals it seed for seed, asserts no spare appears anywhere in it, and
asserts the guard accepts the first and last seed of the block. A hand-edited record that added a spare, a
seed outside the block, or a duplicate therefore fails the suite rather than quietly widening the run.

Nothing has been run. The block is **runnable** for the first time, at a projected **29.14** h serial or
**3.67** h at eight workers on this machine, and invoking it is still a deliberate act.

## 182. The allocation record broke the seed scan by existing, and it is excluded for the same reason the protocol artifact is (2026-11-03)

Writing `docs/stage_b_allocation.json` made the suite red: **17** errors in
`tests/test_stage_b_protocol.py`, every one of them the disjointness scan reporting an overlap. The scan
harvests every seed-numbered integer under `docs/*.json`, and the allocation record now holds all **720**
seeds of the block, so the block overlapped itself -- the same circularity the protocol artifact is already
excluded for, arriving through a new file.

The fix is the existing rule applied to the second file that names the block: `EXCLUDED_ARTIFACTS` now holds
`docs/stage_b_protocol.json` and `docs/stage_b_allocation.json`, and `self_artifact_excluded` says so. With the
exclusion the artifact regenerates to **222** consumed seeds across **76** artifacts
with **0** overlap: identical to the committed state before the allocation existed, which is the
point -- allocating the block spends nothing and consumes nothing.

**Two process notes, both about how the failure surfaced.** The first full-suite run after the allocation
reported the errors and still let a commit through: the command chain ended at a heredoc, and the shell treated
the next line as a new command rather than the continuation of the `&&` list, so a pin commit naming a hash
that did not carry the work was created. It was never pushed; it was dropped before anything left the machine,
and the commits now carry the content first and the pin second. The lesson is the same one this journal keeps
recording in other forms: **a chain is not a check**. `set -e` in a script file is.

## 183. The block can be split across machines, and the only honest number for another machine is a cell run on it (2026-11-03)

The block is 720 independent cells: `run_cell(config, seed)` touches nothing but its own scratch
database, and each result is one JSON file under `.scratch/stage_b_runner/`. Nothing in the design couples
seeds, so splitting the work costs the analysis nothing -- §5's conjunction runs over assembled cells, wherever
they were produced.

**What splitting needed.** `--cell` runs one world and `--all` runs everything; neither is a shard. `--all` now
takes `--shard K/N`, which partitions the 720 cells **interleaved** (`jobs[K-1::N]`) rather than in contiguous
blocks, so every shard covers all four configurations and a spread of seeds; a machine that dies takes a sample
with it, not a configuration. The allocation guard still runs over a shard's seeds before any worker starts.

**Merging is a copy.** Move `cell_*.json` from every machine into one `.scratch/stage_b_runner/` and run
`--assemble --out docs/stage_b_runner.json`. An assembly missing a configuration still reports
`NO VERDICT: PARTIAL ASSEMBLY`.

**Timing, and what is measured.** On this 8-CPU VM the measured rate is 0.235431–0.318279 s per cycle
(mean 0.286542), giving **29.14** h serial and **3.67** h at eight workers. A different machine has
**no measured rate until a cell runs on it**; the honest projection is
`29.14 h x (your seconds per cycle / 0.286542) / (your cores x 0.994)`. Reading a spec sheet instead
would be a guess with a number attached.

## 184. A shard's half-block would have read as SUPPORTED, and the verdict rule now counts worlds (2026-11-03)

Adding `--shard K/N` created a failure the feature itself makes easy to reach. A shard is interleaved, so it
carries **all four configurations** with about **90** worlds each rather than 180. `analyse` decided whether an
assembly was complete by asking whether every configuration had *any* worlds, so a half-block satisfied it --
and on a half-block that happened to show the relation, the verdict would have been **SUPPORTED** on half the
evidence. The rule was checking the shape of the assembly, not its size.

**The fix is a second condition, not a new rule:** a configuration counts as complete only at `PER_CONFIG`
worlds, and the claim verdict requires all four complete. Anything less reports
`NO VERDICT: PARTIAL ASSEMBLY`, and the result now carries `worlds_expected_per_configuration` beside each
configuration's `worlds`, so a reader can see the shortfall rather than infer it.

**The self-test had to grow with it.** Its planted relation was 40 cells per configuration, which was a full
configuration under the old rule and is not one now -- the `SUPPORTED` branch would have gone quiet while still
passing, which is exactly the failure mode the rule exists to prevent. The planted sets are now `PER_CONFIG`
cells at the declared sign, and a new test drives a **half**-block of all four configurations and requires
`NO VERDICT: PARTIAL ASSEMBLY`.

**Sequencing, disclosed.** This was found by re-reading my own change before pushing it: the shard commit was
written, the full suite passed (**770** tests), and the hazard was noticed in the verdict logic rather than by
a test. The test that would have caught it did not exist, and now does. The block's total is unchanged --
**720** cells, **29.14** h serial or **3.67** h at eight workers at
0.286542 s per cycle -- and nothing has run.

## 185. An uncommitted artifact is not evidence in another workspace, and a result travels as numbers that must be re-checked (2026-11-04)

The block's result was reported in prose -- four correlations, four intervals containing zero, a verdict -- while the
cells and the assembly lived in one uncommitted local checkout. Another workspace at the **same commit** therefore
showed the ten design and smoke cells and nothing else, and the report could not be checked from it. Neither side was
lying; the *artifact* was invisible, and an invisible artifact is indistinguishable from an absent one to anyone who
was not sitting at that machine.

**The general rule this produces.** A result enters the record with its artifact in the **same commit**, or it is not
yet in the record. This is the provenance half of Rule 20: Rule 20 says a document that states a number must contain
the number, and the corollary here is that the number must also contain a *path*, and the path must resolve in a
checkout other than the author's. A summary is a pointer, and a pointer to a file that exists on one laptop is a
dead pointer everywhere else -- which is how a real run can look invented without anyone having invented anything.

**The instrument.** `--verify PATH` audits an assembly where it lives: that every seed is in the allocation, that no
spare was drawn, that each configuration has its **180** worlds, that the eligibility field agrees with
`onset + 101 <= horizon`, that no cell reports an outcome it marked unmeasurable, that each trajectory has as many
points as the cell claims cycles, and then it recomputes §5's analysis from the cells and compares Spearman,
interval, worlds and verdict field by field with what the file reports. It generates nothing, so it costs seconds
rather than the block's **29** hours, and it can be run by the person holding the artifact as easily as by the person
reviewing it.

**Status of the reported verdict.** It is **not** recorded here. The cells are not in any commit, so the numbers are
a report rather than an artifact, and the difference is exactly what this entry is about. When the assembly is
committed the verifier decides: if every check passes, the verdict is recorded with the availability limitation that
`2:1` carried, and if a check fails, the failure is named rather than smoothed.

## 186. The Stage B block ran and the pre-registered relation is not supported (2026-11-04)

The 720 allocated worlds ran. The prediction was one-sided and written before the run: **earlier onset predicts a
lower held-out log loss**, so a supported result requires a negative Spearman with a 98.33% interval excluding zero
in every configuration. The assembled verdict is **NOT SUPPORTED**.

| configuration | worlds | scored | ineligible | censored | Spearman | 98.33% interval | width | sign held |
|---|---|---|---|---|---|---|---|---|
| `2:1` | 180 | 47 | 133 | 49 | +0.1819 | [-0.1950, 0.5277] | 0.7227 | no |
| `3:1` | 180 | 180 | 0 | 0 | -0.0328 | [-0.2106, 0.1502] | 0.3608 | no |
| `4:1` | 180 | 180 | 0 | 0 | -0.0507 | [-0.2173, 0.1168] | 0.3341 | no |
| `6:1` | 180 | 180 | 0 | 0 | -0.1077 | [-0.2812, 0.0745] | 0.3557 | no |

720 worlds, 587 of them scored. Only `2:1` departs from 47 / 180 scored:
**133** of its worlds were ineligible and **49** never produced a
sustained onset. The permutation control -- onset shuffled across worlds within each configuration -- returned
intervals containing zero everywhere:

| configuration | permutation interval |
|---|---|
| `2:1` | [-0.3521, 0.3594] |
| `3:1` | [-0.1781, 0.1797] |
| `4:1` | [-0.1757, 0.1786] |
| `6:1` | [-0.1766, 0.1779] |

**What this says.** The relation is not supported in any configuration, and `2:1`'s coefficient is positive. That
positive sign is **not** a reversal in this project's vocabulary: a reversal would need an interval excluding zero in
the opposite direction, and `2:1`'s interval is wide enough to contain both signs. The honest reading is that
earlier onset does not predict a lower held-out log loss here, with `2:1`'s null carrying the least information --
its interval is **0.7227** wide against **0.3557** for `6:1`, because 47
worlds cannot resolve what 180 can.

**The `2:1` shortfall is structural, not an accident of the run.** Its eligibility ceiling is `onset + 101 <= 640`,
i.e. onset at most **539**, and 539 is *exactly* the planned confirmation cycle for that configuration. Any `2:1`
world whose onset arrives after the planned confirmation -- the majority -- cannot be paired with a 101-cycle
outcome and is excluded by §D13's own rule rather than truncated. The design block had already shown this
(onsets 511 and 530, one censored). This arm was therefore half-dead by construction, and its result should be read
as under-powered rather than as evidence against the prediction.

**Verified before recording.** `--verify docs/stage_b_runner.json` re-derived the analysis from the cells at the
file's own 10,000 replicates: 720 cells, 180 worlds in each configuration, no spare drawn,
every Spearman and interval identical, and the verdict recomputed as **NOT SUPPORTED**. The artifact and this entry are
in the same commit; the numbers above are substituted from the artifact, not transcribed.

**Repair, same turn.** Recording the result put the 720 allocated seeds inside `docs/`, and the seed scan duly found
the block *inside its own artifact*, so the protocol check failed: an assembly is a record of the block, not a
consumer of a pre-assigned seed. `docs/stage_b_runner.json` now joins the protocol artifact and the allocation
record in `EXCLUDED_ARTIFACTS`. With the exclusion the scan reads **76** artifacts and **222**
consumed seeds with **0** overlap, and every configuration's seeds are still pre-assigned, still disjoint,
and the four spares still unused. Without it the scan would have read **77** artifacts and reported
720 consumed seeds that this block owns -- a genuine false positive on a correct run.

**The clock, measured against the arm it was set for.** With this design, `horizon - 101` is *equal* to the planned
confirmation cycle in every configuration, so eligibility reduces to `onset <= planned confirmation` exactly. The
scoreable fraction of an arm is therefore the fraction of its onsets that arrive no later than the clock the
protocol set for it -- which makes the clock a design parameter, not a formality:

| configuration | planned confirmation | onset median | onset max | scored |
|---|---|---|---|---|
| `2:1` | 539 | 547 | 579 | 47 |
| `3:1` | 404 | 333 | 379 | 180 |
| `4:1` | 362 | 276 | 307 | 180 |
| `6:1` | 329 | 232 | 259 | 180 |

`2:1`'s 131 observed onsets run from 479 to 579 with median **547**, and
its clock was set at **539** -- below the middle of its own distribution, because the design block had seen
onsets 511 and 530 and the population median is higher. So 47 of 180 worlds qualified, 49 never produced
a sustained onset, and **84** produced one between 540 and 589: observed,
ineligible, and unusable. The other three arms sit comfortably below their clocks (medians 333,
276 and 232 against 404, 362 and
329), which is why they scored 180 of 180.

**What this means for re-running `2:1`.** Running the same design again cannot fix it: the ceiling is the clock, so
a second run reproduces roughly 47 of 180 by construction, and more worlds buy the same fraction. Moving the
clock instead would recover those 84 worlds -- a planned confirmation of 589 scores
**131** of 180 at 9.9 h for the arm against
9.2 h -- but even then the interval would shrink only by
`sqrt(47/131)`, from 0.7227 to about **0.4329**, which still spans zero around the observed
+0.1819. A re-centred `2:1` is a new question with a new clock, a new prediction and a new
allocation of seeds; it is not a second attempt at this verdict, and the four spares stay undrawn.

## 187. Re-running four cells showed the engine's cycle-level output is hash-order dependent (2026-11-04)

`--verify` recomputes §5 from the committed cells. It never asks the engine to produce them again, so
"the analysis is right" and "the engine would do it again" were two claims, and only the first had been
tested. Four cells -- the 90th of each configuration's block, fixed before anything was re-run, so the
choice could not favour a match -- were re-executed by `run_cell` on this machine.

| configuration | seed | onset (assembly -> re-run) | eligible | score | cycles differing |
| --- | --- | --- | --- | --- | --- |
| `2:1` | 700000090 | 562 -> 552 | no -> no | -- -> -- | 10 of 589 |
| `3:1` | 700000270 | 326 -> 332 | yes -> yes | 0.154001 -> 0.154001 | 35 of 454 |
| `4:1` | 700000450 | 279 -> 279 | yes -> yes | 0.147971 -> 0.147971 | 0 of 412 |
| `6:1` | 700000630 | 259 -> 250 | yes -> yes | 0.147733 -> 0.147733 | 71 of 379 |

**1** of the four reproduced bit-identically. In the other three the trajectory diverges from the
cycle where the sustained run is detected and the onset moves by up to **10** cycles; in every
measurable cell the score is identical to six decimals, and no cell's eligibility changes.

**It is not randomness in the world or the readout.** A cell run twice inside one parent process is
bit-identical, with the hash seed pinned and unpinned. It is `_score_tags` in `organica/sleep.py`: the tag
set is built as `set(freqs) | set(cooc) | set(temporal)` and then ordered by frequency with Python's
stable sort, so equal-frequency tags keep an iteration order that follows the process's string hash seed.
One cell run once per seed shows it directly: `PYTHONHASHSEED` 0, 1, 2, 3, 4, 5 give onsets
250, 259, 250, 259, 250, 259 -- alternating -- with a score of 0.147733 in every run.

**What this licenses, and what it does not.** The committed onsets are reproducible to a few cycles rather
than bit-identically, and the block is one draw from that behaviour. The aggregate effect was **not
measured** -- four cells cannot estimate how often a shift of this size carries a cell across its clock --
and an unmeasured quantity is not a zero. It does not re-score the verdict: every interval contains zero
by far more than these shifts, and the three measurable cells scored identically. It does mean that an
exact-reproduction claim has to be qualified, which is why §4.8's cross-machine step now checks the score
rather than demanding one onset.

`docs/stage_b_results.md` is the standalone result document; `docs/stage_b_rerun_check.json` carries the
four cells, their trajectory hashes, the replicate pairs and the seed sweep.

The check's artifact names four allocated seeds, so it joins the assembly and the allocation record in
`EXCLUDED_ARTIFACTS`: the scan reads 76 artifacts and 222 consumed seeds with or without it, and the
exclusion is a named path in that tuple rather than an implication of the count.

## 188. The jitter's size is a defined measurement now, and it has not been run (2026-11-04)

The reproduction check showed the engine's cycle-level output depends on the process's hash order; it could
not say how much that matters for the block, and §D15 keeps the dependence in the frozen engine rather than
patching it. `docs/STAGE-B-JITTER-DIAGNOSTIC.md` is the measurement that closes the gap, committed before it
is run.

Its cost is bounded because the question is narrow. Eligibility is `onset + 101 <= horizon`, so a cell can
change its eligibility only if its onset lies within the observed displacement of its clock -- and the
observed maximum is 10 cycles. From the committed assembly, 38 of the 671 scored
cells sit inside that band (2:1 38, 3:1 0, 4:1 0, 6:1 0); those are enumerated exactly, and the rest of the block is sampled
positionally at every 20th seed (33 cells) to measure the displacement distribution and to
test the ceiling the band rests on. Total 3 redraws, 213 cell-runs, 111,363 cycles.

The part worth keeping is the control: if any sampled cell moves further than 10 cycles, the band was
too narrow, the diagnostic is void and nothing is read from it. Without that, "no cell flipped" would mean
only that the band had been chosen small enough.

No cell has been run for it, so it changes no number in this journal, in the assembly or in the result
document.
