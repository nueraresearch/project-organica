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
