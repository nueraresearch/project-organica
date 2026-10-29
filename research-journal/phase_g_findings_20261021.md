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

### 17.5 Mechanism verification

Run before any outcome was interpreted (`benchmarks/ablation_verify.py`, results in `docs/ablation_verification.json`). An ablation result is only meaningful if the perturbation actually happened.

#### Perturbation census

Every condition changed the organism. `B` (No Lineage) is the deliberate exception: it is a provenance ablation, so *no* population changing is the result, not a failed perturbation.

| cond | perturbation |
|---|---|
| A | confirmed — every Layer-1 population → 0 |
| B | confirmed (provenance-only: behaviour unchanged is the result) |
| C | confirmed — hypotheses 13→15, theories 1→3, investigations 5→0 |
| D | confirmed — processes 10→0, workflows 10→0, hypotheses 13→7, theories 1→0 |
| E | confirmed — processes 10→0, workflows 10→0, hypotheses 13→6 |
| F | confirmed — hypotheses 13→0, theories 1→6, questions 1→6 |
| G | confirmed — questions 1→0 |
| H | confirmed — processes 10→0, workflows 10→0, hypotheses 13→5, theories 1→0 |
| I | confirmed — processes 10→0, workflows 10→0, hypotheses 13→15 |
| J | confirmed — every Layer-1 population → 0 |

#### Did Random Curiosity actually change behaviour?

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

So Law II — "every structure traces back to raw experience" — is **load-bearing for auditability and completely inert for behaviour**. That is a genuinely useful result and it is not what the design implies: it is listed as a principle, and one might reasonably read that as a claim that the architecture depends on it. It does not. The honest formulation is that lineage is a *governance layer*, and a valuable one — it is what makes claims 3 through 8 checkable at all — but it should not be counted among the cognitive mechanisms when arguing that the architecture does something.

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
| 6 | **Record Law II as governance, not cognition** | Finding B. The design documents list lineage among the principles in a way that implies behavioural importance it does not have. | Documentation |
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
| Replace alphabetical retention | **Done** (2026-10-23) | The rule was wrong; it is now a named, unit-free salience policy with its own allowance for inert markers. Measured effect on current behaviour: **none** — the cap does not bind — so it is a correctness fix, not a behavioural one |
| Extend the 90-day run | **Replaced** by the matrix; the daemon becomes a monitor | 3,464 cycles of zero variance (19.2) |
| Enlarge the world | **Refuted as a strategy** | A richer world made the organism worse (19.6) |
| Enlarge the budget | **Refuted as a strategy** | `MAX_HYPOTHESES` is INERT (19.5) |

### 19.10 Disclosure — two defects in our own instrumentation

Both were found by checking a measurement against the substrate it claims to describe, and both are disclosed here rather than quietly fixed.

1. **The archived contradiction series was `null`, not zero.** The archive script copied `rec["contradiction_total"]` from each daemon log record, but `run_continuous.py` never writes that key. All 3,725 archived values were `null`, which reads as "zero contradiction everywhere"; the true final value is **400,550**. The archive is now a committed tool (`benchmarks/archive_run.py`) that re-derives the totals from the hypothesis snapshot, which *is* in the record.
2. **The first audit reported the workflow layer as dead.** It read the report attribute `workflows` instead of `workflow_concepts`, so a working layer measured 0. The audit now uses an explicit name-to-attribute mapping, and a test asserts that no inline cap literals remain in the layer builders.

### 19.11 Artefacts

| Artefact | Contents |
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
can** support the behaviour, not that it does so **unassisted**. The
unassisted question is a separate experiment, and §14's cold-start design
is the instrument for it.

The gates below are therefore stated as *preconditions for the campaign to
be informative*, not as claims about the organism.

### 20.5 Artefacts

| Artefact | Contents |
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

**This is a behaviour change and it is disclosed here.**

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
   behaviour was an artifact. The six V2 colonies are unchanged from the
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
| 74 → 300 → 1,200 → 5,000 | The plateau was an **environmental artefact**. What this project found is a developmental system trapped inside a toy universe. |
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
protocol pins. Dropping the single most favourable seed, and separately the
single least favourable seed, also leaves every verdict unchanged: with ten
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

The architecture is optimised to **accumulate and stabilise structure**, and
the matrix found exactly that: structure fixed on cycle 1 and held for 2,999
cycles while support grew +10,776%. K3 then found that the early scaffold
dominates. That may not be a bug. It may be the purest expression of the
architecture — coherence preserved at the cost of adaptability.

The 2×2 control makes this precise rather than rhetorical: the late group
**is** incorporated when it is strictly stronger than the group that arrived
first (9–11 of 18 gold pairs at late weight 3 / early weight 1, against 0–1
otherwise). So Organica is not incapable of revision; it is **priority-ordered**,
with arrival order as the tiebreak in favour of the incumbent. The deficit is
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
artefact. This section records what happened, because the failure mode is
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
other at cycle 590. Same endpoint, different developmental behaviour. The RT
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
quietly become a licence. Nothing was re-read, relaxed, or reinterpreted: the
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
negative and was an artefact; this run looks like a clean positive and is
barred by one criterion that missed by 0.005. **Both of those are the same
lesson.** The instrument either measures what it claims or it does not, and the
protocol — not the observer — decides what the number means.

### What this section is not

It is not a claim that Organica has a coherence–plasticity boundary. The
pre-registered verdict is INCONCLUSIVE and the protocol forbids concluding
anything from it. It is not a claim about capability. It is not a claim that
support ratio is *the* operative variable beyond this axis on this engine. And
it is not a licence for V2: V2–V5 were deliberately not run, because no Phase L
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
artefact** — the shift between the n=10 and n=30 curves is sampling luck, and
**the paired bootstrap over seeds is sound**. The n=30 curve is the better
estimate because there are more of them, not because they were different.

### The transferable lesson

**A criterion that flips when n changes is not a measurement of a property;
it is a measurement of the draw.** This phase went in with four criteria and
came out with two of them behaving like coin flips and two of them behaving
like facts. The way to tell the two apart is not to argue about them — it is
to ask *how often does this criterion hold across random subsets of the data
I already have?* That question is cheap, it is answerable with the data in
hand, and it converts a verdict into a characterisation.

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
remedy, and the remedy has now been taken. And it is not a licence to relax a
criterion after the fact. The criteria stand; the verdict stands; what
changed is that the phase can now *say what the verdict means*.

Recorded in `docs/phase_l_results.md`, in the facts sheet as §Y, and in the
manual as §8.11.

---

## §40 — The decision: publish the characterisation, and stop raising n

**What this section records.** The owner's reading of the raise-n result, the
decision taken on the strength of it, and the reasoning behind that decision.
It is a decision record, not new evidence.

### The reading

> **Organica 1 does not appear to exhibit a continuous coherence–plasticity
> trade-off. It appears to exhibit regime behaviour separated by a
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

**Publish the characterisation.** Not `H2-L` — that outcome was not reached,
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

The second temptation is to let "regime behaviour" become a claim about
intelligence. It is not one. Phase L measured a displacement index, a
preservation index and a latency on synthetic worlds. **"Regime" describes the
shape of those curves, and nothing more.**

### Where this lives

The published characterisation is **`docs/PHASE-L-SYNTHESIS.md`**, following the
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
| **Phase L** | Regime behaviour with a stable transition region — and the protocol verdict and the characterisation kept as separate artefacts. |
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
that fails it **fails the protocol even if the headline behaviour is correct.**

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

**A4 behaviour invariance passes**: observer on and observer off produce
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
with behaviour. Both were the auditor's errors; both were found by the checks
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
pre-committed to nothing. It is a characterisation study, not a protocol.

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
characterisation stands. The six negative task families stand. No number was
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
F1 at 0.5 was measuring *threshold behaviour*, not knowledge quality. The
reviewer's phrasing — that F1 might compare threshold behaviour rather than
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
members — so a concept *would* generalise to pairs never directly
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
**CALIBRATION / CONTROL**, not a generalisation benchmark.

### The compositional task — a benchmark that can fail

A new task was built to measure what the transition world could not:
generalisation to a **withheld combination** of familiar elements. Four
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
*generalisation* headroom on the withheld combination specifically.

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
| **Organica** | **0.453018** | 0.453912 | 0.463372 |
| Replay | 0.347521 | 0.349592 | 0.351989 |
| Statistical | 0.347273 | 0.350723 | 0.352194 |
| base rate | 0.409581 | 0.409511 | 0.406124 |
| Bayes ceiling | 0.276259 | 0.272365 | 0.275176 |

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
rules, **precision never exceeds 0.3443**.

### The causal account

1. **The world's relations are in memory.** The `precedes` table holds all 112
   world edges (raw temporal coverage 0.97–1.00, every seed, both shapes).
2. **They are a minority of the table, and they are not the high-count rows.**
   366–518 rows for a 16-tag world; only 232–240 are world-tag pairs; the
   world's edges are roughly **a third** of what any selection must retain
   (precision ≤ 0.3443 at every budget, under both rules). The top of the table
   is internal-vocabulary edges and intra-cell pairs.
3. **Layer 1 selects on frequency, and the world is not organised by
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
verdict `H3-L — INCONCLUSIVE`, the Phase L characterisation, and the
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
would have made `v0.10.0` a published artefact that nobody had asked to
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
mechanism, and they are different mechanisms.**

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
exceeds 0.3443 at any budget under either allocation rule. Requirement 1 is
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
INCONCLUSIVE`, the Phase L characterisation, and the campaign's stop at Gate
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

The engine computes a **frequency-normalised** criterion, stores it in every
candidate's evidence, uses it for **survival**, and then sorts by **raw count**
for **admission**. `memory.py:264-281` calls the normalisation "load-bearing
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
**The engine's normalised criterion is undefined for exactly the edges it
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
4. **The engine's own normalised criterion is actively harmful on this
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
about the space of solutions.** The engine *did* compute a normalised
criterion — and using it would have been worse than the thing it replaces.
The precedent was there; it was simply not the one anyone expected, and
checking it changed the requirement from "invent a criterion" to "the
criterion you can compute is the wrong one".

**2. A normalisation can be undefined exactly where it is needed, and the
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
INCONCLUSIVE`, the Phase L characterisation, and the campaign's stop at Gate
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
