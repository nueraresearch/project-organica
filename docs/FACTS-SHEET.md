# Organica — Facts Sheet

**Purpose.** Separate what has been *measured* from what is *assumed*. Every
claim below is tagged with its provenance so it can be re-checked. Claims
without a provenance tag live in §F (assumptions) or §G (gaps) — never in §A–§E.

**How to re-check.** Every §A–§E number is reproducible from a committed
artifact in `docs/` or a committed script in `benchmarks/`. The four
measurements added on 2026-10-22 are reproducible in one command:

```bash
python benchmarks/development_probe.py --cycles 600
```

**Rule.** A number is a fact here only if a script produced it. If a
plausible explanation exists but was not measured, it is an assumption and
it is in §F.

---

## A. Architecture and substrate — MEASURED

| # | Fact | Evidence |
|---|------|----------|
| A1 | The core is standard-library only. `requirements.txt` lists no runtime dependency. | `docs/clone_check.json` → `core_dependencies` |
| A2 | A fresh clone from GitHub imports and runs with no install step. | `docs/clone_check.json` → `import_organica` |
| A3 | A fresh clone passes **8/8** verification checks: clone, import, core deps, pytest (**17 passed**), `build.py`, **9/9** examples, `study_health`, live-study isolation. | `docs/clone_check.json` (2026-10-22T21:11:21Z) |
| A4 | Lineage integrity is **100%**: 138 of 138 candidates that require a lineage anchor are grounded in Generation-0 experience tags; 0 ungrounded, 0 unverifiable-evicted. | `docs/lineage_audit.json` |
| A5 | The sleep-cycle counter is monotonic: **3,725 cycles, 1…3725, no gaps, no regressions.** | `memory.db` → `sleep_cycles` |
| A6 | A clone cannot touch the live substrate: its scratch directory resolves inside the clone by construction. | `docs/clone_check.json` → `live_study_untouched` |

## B. Development and emergence — MEASURED

| # | Fact | Evidence |
|---|------|----------|
| B1 | In the cold-start study, **G1, G4, G6, G7 and G8 bootstrap unassisted**; **G5 never does** in any of the 8 conditions. | `docs/cold_start.json` |
| B2 | **The live run converged and then stopped moving.** Over the last 931 cycles (25% of the run) and the last 372 cycles (10%), every population series has **stdev 0.000000, slope 0.0 per 1,000 cycles, and exactly one distinct value.** | `docs/development_probe.json` → `plateau` |
| B3 | Convergence points: theories & questions constant from cycle **261**; dreams from **162**; investigations & experiments from **82**; hypotheses from **1,677**. | same |
| B4 | **The population is flat while the evidence behind it grows without bound.** Raw contradiction across the retained hypotheses rose 0 → **400,550** while support reached 78,647, over a run whose population never changed after cycle 261. | same → `plateau.contradiction` |
| B5 | Confidence is a **share**, so it converges: every subject's confidence settles at ≈0.16–0.17 even though its absolute evidence grows by orders of magnitude. | `docs/prefix_run_series.json` final snapshot (e.g. `developer` support 19,679 / contradiction 93,960 → conf 0.1732) |
| B6 | Cross-domain validation returns **PASS** with 100% lineage integrity in all 4 domains — but peak question uncertainty is 0.9957 in Developer Workflow and **0.0** in the other three. | `docs/validation_report.json` |
| B7 | Emergence status: Level 0 evidenced, Level 1 **measured-negative**, Level 2 measurable, Level 3 pending designer protocol, Level 4 partial, Level 5 **not evidenced** (no experiment executor), Level 6 structurally excluded. | `docs/EMERGENCE-CRITERIA.md` |

> **B2 + B4 together are the most consequential pair on this sheet.** The
> organism did not stop accumulating evidence; it stopped *converting* it.
> Any metric defined only on population counts is blind to that difference.

## C. Ablation campaign V1 — MEASURED

Protocol: 11 conditions × 300 cycles, full study stream, 8 events/cycle
(identical cadence to the daemon), **forward-looking** scoring (the last 10
cycles are scored against events the organism had not yet seen), applied
**in-process** by subclassing — the engine source was never edited for the
campaign. Source: `docs/ablation_study.json`, protocol described in
`docs/ABLATION-PREREGISTRATION.md`.

Reference condition (O_FULL): `pa` 0.1910 · `pa_substrate` 0.3770 ·
`ip` 0.4880 · `scr` 0.0183 · `ss` 0.5196 · `lc` 1.0000 ·
`cd` 12.2283 · `cd_duty_cycle` 0.6133 · `cdt` −0.4863 ·
`nsr` 0.8738 · `es` 49.102 (excludes `cdt`).
Final population: 13 hypotheses, 1 theory, 1 question, 8 dreams,
5 investigations, 5 experiments.

| Cond | Intervention | `es` impact | Band | Read |
|------|-------------|------------:|------|------|
| A | No Sleep | +49.102 | **foundational** | Without consolidation there is nothing at all. |
| J | Memory Without Structure | +49.102 | **foundational** | Without edges there is nothing at all. |
| I | Random Sleep | +14.819 | supportive | Random structure recovers much of the aggregate — the *shape* matters more than the *content*. |
| C | No Curiosity | +4.467 | cosmetic | Removing EIG **raises** belief count (13→15 hyps, 1→3 theories) and removes only the two output layers. |
| G | No Questions | +0.809 | cosmetic | Questions→0 while investigations and experiments survive. |
| F | No Hypothesis Layer | +0.352 | cosmetic | Bypassing G4 yields **6 theories** instead of 1 — the layer was suppressing, not enabling, theory formation. |
| B | No Lineage | 0.000 | cosmetic | Every metric identical; lineage is governance, not cognition. |
| H | Random Curiosity | −2.308 | cosmetic | Random ordering ≈ EIG ordering. |
| E | No Dreams | −3.002 | cosmetic | Dreams carry the upper ladder, but the aggregate index scores their removal "cosmetic". |
| D | No Falsification | −3.108 | cosmetic | Freezes rather than bloats: 13→7 hypotheses, theories→0, contradiction duty 61%→5%. |

| # | Fact | Evidence |
|---|------|----------|
| C1 | **Mechanism verification (perturbation census) confirmed every condition actually perturbed the system.** Random Curiosity Jaccard overlap **0.111**; EIG top-k precision **1.000** vs random **0.584**; mean selected score 0.990 vs 0.863; top-decile hit 0.475 vs 0.271. | `docs/ablation_verification.json` |
| C2 | **EIG is a perfect ranker that buys nothing measurable.** Selection quality is high and the developmental outcome is unchanged. | same |
| C3 | Contradiction generation is **independent of falsification** (max per-hypothesis contradiction count 6,391). | same |
| C4 | Two pre-registered predictions were **falsified** and are recorded as falsified, not revised: (D) no-falsification was predicted to bloat, it froze; (G) questions were predicted to gate investigations, they do not. | `research-journal/phase_g_findings_20261021.md` §17 |
| C5 | **The aggregate `es` index does not count beliefs.** It counts structures, so an ablation that removes most of the organism can score "cosmetic". The per-metric delta table and the population table are the primary result; `es` is a convenience index. | `docs/ABLATION-PREREGISTRATION.md` §8 |
| C6 | `cy` and `eig_star` are **structurally unmeasurable** (no experiment executor exists) and were **excluded, not zeroed**. Zeroing them would have deflated every score by ~30%. | same |

## D. Selection pressure is currently **inert** — MEASURED (2026-10-22)

This is the section that changes the research plan.

| # | Fact | Evidence |
|---|------|----------|
| D1 | The Layer-4 hypothesis cap (`MAX_HYPOTHESES = 15`) **never truncates** in the reference configuration: **0 of 600** cold cycles. Belief pool max **8**, mean **5.31**. | `docs/development_probe.json` → `cap_census` |
| D2 | Raising the cap **15 → 30 → 60 changes nothing** — identical belief counts, subject counts and theory-eligible subject counts. | same → `budget_insensitivity` |
| D3 | **Therefore the retention policy has no causal effect today.** With nothing truncated, "alphabetical" and "salience" select the *same membership*; they differ only in *order*, and Layer 5 re-sorts by support count. | same → `cycles_policies_differ_membership: 0` |
| D4 | Independently corroborated by an already-committed artifact: the cold-start study's `no_truncation` condition produced final populations **identical to `baseline`**. | `docs/cold_start.json` |
| D5 | **The hypothesis layer is mostly inert markers.** Every steady-state cycle holds **13 hypotheses = 7 `high_structural_significance` markers + 6 real beliefs**, over 5 subjects. Markers are **53.8%** of the slots. | `docs/development_probe.json` → `cap_census`; substrate audit |
| D6 | **Exactly one subject ("session") carries ≥2 beliefs.** Layer 5 needs ≥2 beliefs on one subject to form a theory — which is precisely why there is exactly **one** theory and **one** question. | same |
| D7 | The cap is *not* inert in general: in two ablated V1 conditions (C, I) the hypothesis count reached **15** — the cap. It is inert specifically in the reference configuration. | `docs/ablation_study.json` |
| D8 | **The raw tag vocabulary is mostly the organism's own schema.** 63 distinct tags; **60.6%** of all tag occurrences are the JSON field names of stored candidates (`type` 548,902 · `generation` 545,177 · `evidence` 412,335 · `strength` 308,771 …). | `docs/development_probe.json` → `vocabulary` |
| D8a | **But the pollution does not reach the cognition layers.** `MemoryService.store()` refuses to build graph edges from sleep output (`if event_type != "sleep"`), so the co-occurrence and temporal graphs — and therefore every prediction, meta-concept, process and workflow — contain **world tags only**. All 400 most-recent predictions, meta-concepts, processes and workflows use zero schema tags. | `organica/memory.py` `store()`; substrate audit |
| ~~D8b~~ | ~~The pollution is therefore confined to `tag_counts`, which feeds only the **frequency estimates** used for tag scoring — not the temporal structure. A real but secondary defect, not the cause of anything in §D.~~ **RETRACTED 2026-10-23 — see D8c.** The first half was right (the graphs are world-only); the conclusion was wrong. | superseded by D8c |
| **D8c** | **The pollution was not confined to scoring — it was the denominator of a survival filter, and it was the cause of the supply limitation.** `tag_counts` is the source of `source_freq`, and `source_freq` is the denominator of the Layer-1 edge strength `ratio = count / source_freq`. The **numerator** was world-only and the **denominator** was not, so the two sides of the ratio measured different populations, and the survival filter discarded the world's own structure in favor of whatever the organism happened to say about itself. Measured consequence: a branch stimulus collapsed to **4 surviving edges** (2 of them schema tags), **0 processes, 0 workflows, 0 beliefs**. Corrected 2026-10-23 — the counter is now scoped to world events, like the graph it normalises. | `docs/freq_scope_probe.json`; journal §21 |
| **D8d** | **The apparent r=4 / r=6 / r=10 "phase transition" was an artifact of D8c.** With the counter scoped correctly, all three repeat counts give the *same* result: a full prediction window, a belief pool of 18, seven competing subjects, and **100%** of tail cycles passing every gate. There was no boundary; the parameter was interacting with the measurement. | `docs/freq_scope_probe.json` |
| **D8e** | **Consequence for §D6.** The study stream's "exactly one subject carries ≥2 beliefs" was *partly an artifact* of D8c: the pollution suppressed edges selectively, leaving a concentrated set, and a concentrated set is what produces a high-share subject and therefore a theory. After the correction the study stream holds **0.97** competing subjects on average (was 1.83) and **5.17** beliefs (was 6.83). The headline — one theory, one question — does not change, but the number is no longer a fact about the world. | `docs/gate_check.json`; journal §21.8 |
| D9 | The belief *subjects* are a strict subset of the marker anchors: markers anchor on {suite, session, report, modified, executed, engineer, developer}; beliefs live on {session×2, suite, report, modified, developer}. | substrate audit, `docs/development_probe.json` |

## D2. The instrumentation audit — WHERE the pressure actually is

`benchmarks/instrumentation_audit.py` measures each capped layer's candidate
pool **before** truncation, then computes

```
retention_pressure = pool_size / cap
```

`< 1.0` no pressure · `1–2` weak · `2–5` useful · `> 5` strong.
400 cycles, cold start, study stream. Source: `docs/instrumentation_audit.json`.

| Layer | cap | pool mean | p95 | max | pressure mean | pressure p95 | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| loops | 15 | 936 | 936 | 936 | **61.1** | **62.4** | hard over-truncation |
| predictions | 20 | 598 | 621 | 621 | **29.9** | **31.1** | hard over-truncation |
| anomalies | 10 | 292 | 309 | 309 | **29.2** | **30.9** | hard over-truncation |
| processes | 10 | 11.8 | 13 | 13 | 1.18 | 1.30 | weak |
| dreams | 8 | 8.3 | 12 | 21 | 1.04 | 1.50 | borderline |
| experiments | 5 | 4.9 | 5 | 5 | 0.98 | 1.00 | none |
| workflows | 10 | 9.1 | 10 | 10 | 0.91 | 1.00 | none |
| meta_concepts | 15 | 9.0 | 9 | 9 | 0.60 | 0.60 | none |
| **hypotheses** | 15 | **5.3** | 8 | 8 | **0.35** | 0.53 | **none — G-P1 FAILS** |
| questions | 6 | 1.2 | 3 | 3 | 0.19 | 0.50 | none |
| theories | 8 | 1.2 | 3 | 3 | 0.14 | 0.38 | none |

**The organism is starved, not selective.** Layer 1 throws away ~99% of its
own candidates (pressure 29–61×) while Layer 4 has 5–8 beliefs for 15 slots
(pressure 0.35). The caps are mismatched: evidence is discarded at the top
and found wanting at the bottom.

**The funnel, measured end to end:**

```
  936 loops ─┐
  621 predictions ─┼─ capped by count/strength (popularity rules) ─┐
  309 anomalies ─┘                                                 │
                                                                   ▼
                                    12 processes ── capped ──▶ 10 workflows ──▶
                                                                   5-8 beliefs ──▶
                                                                   1 theory ──▶
                                                                   1 question
```

Each arrow is a cap, and each cap's retained set is chosen by a *popularity*
rule — raw temporal count for predictions, strength for loops, dominance
ratio for anomalies. The hypothesis layer's alphabetical rule is the same
family of defect, three layers further down, and it is currently invisible
only because there is nothing left to choose between.

## D3. Parameter influence map — which knobs actually do anything

14 tunable parameters, each varied once against a 400-cycle baseline.
Classification: **DECISIVE** (changed the final outputs) · **POOL_ONLY**
(changed the candidate pool; the cap hid it) · **INERT** (changed nothing).
Source: `docs/instrumentation_audit.json` → `audit1_parameter_influence`.

| Parameter | Baseline → variant | Verdict | What moved |
|---|---|---|---|
| `DEATH_THRESHOLD` | 0.15 → 0.25 | **DECISIVE** | beliefs → 0, theories → 0, questions → 0 |
| `STABLE_THRESHOLD` | 0.3 → 0.2 | **DECISIVE** | belief pool 5.05 → 6.00 |
| `MAX_PREDICTIONS` | 20 → 40 | **DECISIVE** | belief pool 5.05 → **6.51**, hypotheses 12.05 → 15.34, theories 1.00 → 1.23 |
| `MAX_PROCESSES` | 10 → 25 | **DECISIVE** | processes 10 → 13, belief pool 5.05 → 6.00 |
| `PREDICTION_MIN_COUNT` | 5 → 3 | POOL_ONLY | prediction pool 621 → 641, outputs unchanged |
| `LOOP_MIN_STRENGTH` | 5 → 2 | POOL_ONLY | loop pool 936 → 1092, outputs unchanged |
| `MAX_HYPOTHESES` | 15 → 40 | INERT | nothing — the cap never binds |
| `MAX_WORKFLOWS` | 10 → 25 | INERT | nothing — workflows are bounded by the process count |
| `MAX_META_CONCEPTS` | 15 → 30 | INERT | nothing — only 9 are ever composed |
| `WORKFLOW_MIN_MATCHED_METAS` | 2 → 1 | INERT | nothing — the gate already passes |
| `META_CONCEPT_MIN_REFS` | 3 → 2 | INERT | nothing — the *type-diversity* gate binds, not the ref count |
| `CONCEPT_MIN_DEGREE` | 4 → 2 | INERT | nothing |
| `CONCEPT_MIN_REACH` | 4 → 2 | INERT | nothing |
| `PHRASE_MIN_CLUSTERING` | 0.7 → 0.5 | INERT | nothing |

**The one result that reorders the plan:** `MAX_HYPOTHESES` is **INERT**.
The hypothesis cap — the thing the P1 experiment was built around — has no
effect whatsoever. The cap that *does* have an effect is `MAX_PREDICTIONS`,
and it acts by feeding the belief layer: raising it 20 → 40 moves the belief
pool from 5.05 to 6.51.

**What this means, stated plainly.** The owner's working hypothesis was
"the retention policy is currently acting as a hidden evolutionary force."
The measurement says it is not acting at all. It is a *latent* defect — a
name-based rule that would matter if the pool ever exceeded the cap — but
the cap never binds, so the rule is inert. Re-sorting a list that is never
cut down changes nothing but its order.

**And the audit says the hypothesis cap is the wrong place to look
entirely.** `MAX_HYPOTHESES` is INERT (§D3). The pressure in this organism
is at Layer 1, where 29–61× more candidates exist than there are slots, and
every one of those layers retains by a popularity rule. The
alphabetical-hypothesis rule is the same defect three layers downstream,
waiting for enough input to become visible.

## E. Corrections to the record

| # | Correction | Detail |
|---|------------|--------|
| E1 | **The archived contradiction series was null, not zero.** `.scratch/archive_prefix.py` copied `rec["contradiction_total"]` from the daemon's log record, but `run_continuous.py` never writes that key. All 3,725 archived values were `null`, which reads as "zero contradiction everywhere" — the true final value is **400,550**. The archive script now re-derives it from the hypothesis snapshot, and `docs/development_probe.json` re-derives it again independently. | `docs/prefix_run_series.json`, `docs/development_probe.json` |
| E2 | **Finding J was wrong about the mechanism.** Journal §17.7 claimed the alphabetical truncation caused No-Falsification's contradiction collapse. The verification census shows D's **processes and workflows were both 0**, and hypotheses are built only from workflows + processes + meta-concepts — so D's all-marker population is explained by the destroyed Layer-2/3 layers, **not** by alphabetical crowding. The alphabetical sort remains a real, frequency-correlated, name-based arbitrariness defect, but it was **not** the cause of D's result. | `research-journal/phase_g_findings_20261021.md` §17.7 — corrected in §19 |

## F. Assumptions currently load-bearing — NOT MEASURED

| # | Assumption | If it is wrong |
|---|------------|---------------|
| F1 | **One seed per V1 condition; no variance estimate is claimed.** The artifact says so explicitly. | Any per-metric delta smaller than seed noise is uninterpretable. Most V1 "cosmetic" findings are in this danger zone. |
| F2 | The `es` aggregate is treated as a summary of the organism. | It counts structures, not beliefs (C5), so it can read "cosmetic" for a near-total ablation. |
| F3 | Population counts are a proxy for development. | **Known false in part** (B2/B4): counts were flat while evidence grew 400,550-fold. Any count-only metric inherits this blind spot. |
| F4 | The 48-event study stream is an adequate stimulus. | Its vocabulary bounds how many distinct subject→expectation pairs can exist. Whether a richer corpus changes the developmental picture is **untested**. |
| F5 | Population *stability* indicates developmental stasis rather than developmental equilibrium. | Both readings fit a flat line equally well. Distinguishing them needs a metric on evidence flow, not counts — see §G3. |
| F6 | The four calibration domains are representative. | No claim is made beyond those 4 domains. |

## G. Known gaps

| # | Gap | Consequence |
|---|-----|-------------|
| G1 | **No experiment executor.** Experiments are generated but never run. | No Question ever closes; EIG can never pay off; `cy` and `eig_star` are unmeasurable. This is the single highest-value missing piece. |
| G2 | **No cross-domain transfer evidence** (Level 1 measured-negative). | Nothing shows the organism generalises. |
| G3 | **No metric on evidence flow.** Every developmental metric is a count. | The plateau/evidence-growth divergence (B4) is currently invisible to the metric suite. M3 (contradiction density) is the candidate to fix this. |
| G4 | **One organism, one run, flat.** No longitudinal data beyond 3,725 cycles, and that run stopped moving at cycle 261. | No claim about behavior at 10⁵+ cycles is supported — and the plateau argues the current build would not differ there. |
| G5 | **Retention has never been tested under pressure** — the belief pool has never exceeded the cap in the reference configuration. | Gate **G-P1** fails: hypothesis retention pressure is 0.35, and `MAX_HYPOTHESES` is INERT (§D3). The Tier-1 "FULL vs SALIENCE" experiment as specified would measure two identical colonies. |
| G6 | **Commercial track: unresolved.** Entity, IP ownership, open-source license position and the authorization memo all require counsel. Customer problem unvalidated (no interviews). | Tracked in `docs/GATE-BOARD.md`. |

---

## H. Corrections that changed the plan

1. **The 90-day single-arm goal can be shortened.** The run plateaued at cycle 261 (7% of its length) with zero variance thereafter. A single arm with a flat line describes nothing and identifies nothing; only contrasts can. The comparative matrix replaces it as the primary experiment; the daemon becomes a monitor, not a gate. → `docs/GATE-BOARD.md`
2. **The hypothesis budget is not the lever.** It can be raised, and raising it changes nothing (D1–D2). `MAX_HYPOTHESES` is INERT (§D3). The lever is **belief supply upstream**.
3. **P1 as specified is degenerate.** Retention pressure on the hypothesis layer is 0.35 (§D2), so "FULL vs SALIENCE" compares two identical colonies (G5). Gate **G-P1** must pass before P1 means anything.
4. **The bottleneck is not where we were looking.** Pressure is 29–61× at Layer 1 and 0.35 at Layer 4 (§D2). The organism discards ~99% of its own evidence at the top and then has almost nothing to reason over at the bottom. **The caps are mismatched.**
5. **Most "important" parameters do not participate in any decision.** 8 of 14 are INERT — including the two that were the subject of the whole campaign (§D3). A parameter that never changes an output should not be given a row in an experiment plan.
6. **Our own instrumentation had a defect that would have produced a false result.** The archived contradiction series stored `null` for all 3,725 cycles (reads as "zero contradiction"; true value 400,550), and the audit initially reported the workflow layer as dead because it read the report field `workflows` instead of `workflow_concepts`. Both were caught by checking a measurement against the substrate it claims to describe, and both are disclosed here rather than quietly fixed. (E1, and §D3 note)
7. **"9-tag world" needs refining.** The temporal world is 42 tags; only ~9 reach the composition layers — and that is a *consequence* of the Layer-1 caps, because meta-concepts are composed only from candidates that survived them. The narrow world is downstream of the over-truncation, not an independent fact about the stimulus.

---

## I. The Tier-1 matrix — MEASURED (2026-10-23)

Protocol: 6 colonies × 3,000 cycles = **18,000 colony-cycles**, `lattice_L1`
stimulus, seed 20261023, `PYTHONHASHSEED=0` in all six processes.

| # | Fact | Evidence |
|---|------|----------|
| **I1** | **The structure is decided on cycle 1.** Every colony reaches 18 pre-retention beliefs, 7 competing subjects and 15 retained beliefs on the first cycle, and all six arms converge to the **same** attractor despite six different interventions. **Corrected 2026-10-24 (journal §31, measured in §S):** the *retained* belief count is exactly 15 in all 2,999 cycles of every colony, but the pre-retention pool dips to 16/6 and returns — in 98.1–99.5% of cycles for five arms and only **75.9%** for `NO_QUESTIONS`. "Holds that configuration for 2,999 cycles" was an overstatement. | `docs/force_matrix.json` → `series` |
| **I2** | **Evidence grows by three orders of magnitude while structure does not move.** Mean support 101.2 → 11,006.2 in the reference arm, **+10,776%**. | same |
| **I3** | **M5 ("development velocity") is not a rate.** It is `new items ÷ run length`. The reference arm discovered **74** items over 300 cycles and **74** over 3,000; the "velocity" fell from 24.667 to 2.467 because the numerator stopped growing. Every colony discovered **zero** new items in its final 100 cycles. | `docs/discovery.json` |
| **I4** | **The stimulus repeats every 9 cycles.** `lattice_L1` is 9 distinct events over 7 distinct words; the organism sees the same world 333 times. A repertoire cannot grow in a world that does not change. | `benchmarks/discovery_report.py` → `stimulus_facts` |
| **I5** | **The inventory, broken down:** FULL 74 (16 beliefs, 11 questions, 36 dreams, 11 experiments) · SALIENCE 78 · NO_CONTRADICTIONS 79 · NO_QUESTIONS 112 · NO_DREAMS 44 · ANTI_EIG 85. Removing dreams removes **30** items, not 11, because dreams are built from beliefs. | `docs/discovery.json` |
| **I6** | **5 of 9 metrics can discriminate between arms.** M1, M6 and M8 are **saturated** (a theory in 2,999 of 3,000 cycles; generation 7 everywhere; equal population stability). M9 is **structurally zero**. The full-run audit returns the same verdict as the 300-cycle pilot. | `docs/metric_sensitivity.json` |
| **I7** | **The measured noise floor is one item.** Within one process the seed floor is exactly 0.00; across six processes at the same seed, **one** field moves — M5 — by exactly one new item (rate spread 0.033 at 3,000 cycles). Every other field is bit-identical. | `docs/process_noise_3000.json` |
| **I8** | **The five pre-registered predictions: 2 SUPPORTED, 3 REVERSED, 0 UNSUPPORTED, 0 NOT INTERPRETABLE.** P1 retention (SUPPORTED) · P2 contradiction-is-fuel (**REVERSED**) · P3 curiosity-needs-questions (**REVERSED**) · P4 dreams-contribute (SUPPORTED) · P5 EIG-orthogonal (**REVERSED**). Removing contradiction or questions *raises* development velocity; selecting the lowest-EIG experiment develops *more* than selecting the highest-EIG one. | `docs/verdicts.json` |
| **I9** | **`NO_CONTRADICTIONS` does not remove contradictions.** `CONTRADICTION_SCALE` multiplies the contradiction term in the *confidence formula*. M3 reads the raw count by design, so M3 is near-invariant for this colony **by construction**. The honest name is *contradiction not weighted in confidence*. | `organica/sleep.py:1489`; `benchmarks/force_matrix.py:230` |
| **I10** | **M7's spread is fragile and is reported as such.** The reference arm's 212-cycle mean rests on **one** observed belief death (15 of 16 censored); the salience arm's 2,989.667 rests on three. The robust finding is that 15–16 of the beliefs never die in any arm. | `docs/force_matrix.json` → `M7_mean_hypothesis_lifetime` |

> **I1, I2 and I4 together are the most consequential pair on this sheet.**
> The organism reached a fixed equilibrium on cycle 1 and accumulated evidence
> for 2,999 more cycles — but in a nine-event world. The plateau is
> consistent with *the organism exhausted the environment*, and that is not
> the same statement as *the organism cannot develop*. Every metric defined
> only on population counts is blind to that difference.

## J. H24 — the hypothesis the matrix produced — NOT YET TESTED

> **H24. Organica's apparent developmental plateau is primarily constrained
> by environmental information content rather than by architectural inability
> to reorganise.**

**Evidence for:** I3 (inventory saturates, zero new items in the final 100
cycles) · I4 (the world repeats every 9 cycles) · I2 (evidence grows while
structure does not move) · I1 (all six arms converge to one attractor).

**Evidence against: none — because H24 has not been tested.** I1–I10 are all
consistent with H24 *and* with its opposite. A human placed in nine
experiences repeated forever would also converge, and that is not a defect.

**What would falsify it:** a larger, non-repeating world still produces ~74
distinct structures, the same plateau, and the same attractor.

**The experiment:** a world-complexity ladder — small finite (done, 74
items) → medium expanding → large expanding → open-ended — measuring
inventory growth, the cumulative discovery curve, MBSD, theories, questions
and cognitive revolutions. If the inventory goes 74 → 300 → 1,200 → 5,000,
the plateau was environmental; if it stays 74, the plateau is architectural.

Full statement: `docs/FORCE-MATRIX-RESULTS.md` §11; journal §23.10.

## K. The substrate's structural bandwidth — MEASURED (2026-10-23)

Measured while designing the H24 ladder, *before* the ladder was run. These
are properties of the engine, and they are the reason the ladder's rungs
are shaped the way they are.

| # | Fact | Evidence |
|---|------|----------|
| **K1** | **Hub degree 3 is the optimum, and the usable range is narrow.** One hub shared across N triangles: the hub's best edge ratio falls 1.00 (N=2) → 0.75 (N=3) → 0.56 (N=4) → 0.44 (N=5) → 0.35 (N=6) → 0.31 (N=8) → **0.185 (N=12)**, against a `STABLE_THRESHOLD` of 0.3. Structure is best at N=3 (15 beliefs, 17 pre-retention, 6 competing subjects) and **collapses to zero at N=12**. | `docs/hub_degree_probe.json` |
| **K2** | **The Layer-1 prediction window (`MAX_PREDICTIONS = 20`) binds before the belief cap does.** Layer 1 ranks temporal edges by count and keeps the top 20; the Layer-2 process builder finds 3-cycles only among those 20. When many triangles are equally frequent the top 20 is an arbitrary subset, so complete 3-cycles are rare. Measured: 4 hubs × 3 triangles (48 edges) left ≈5 edges per hub, and **competing subjects fell from 5.98 to 1.50**. More structure in the world produced *less* structure in the organism. | `benchmarks/scale_ladder.py`; `benchmarks/branch_diag2.py` |
| **K3** | **A tag must be at least four letters.** The engine extracts tags with `re.findall(r"\b[a-zA-Z]{4,}\b", ...)`. A first version of the ladder numbered its leaves (`ta0`); every leaf was silently invisible, the ladder measured nothing, and the null looked like a result. Caught by verifying the perturbation happened before interpreting. | `organica/scale_streams.py`; `AGENTS.md` rule 9 |
| **K4** | **A consequence for V2's design, not a change to the engine:** a world that keeps offering new structure must keep a small number of structures *frequent*, so the top-20 window always contains complete triangles, while new structure arrives around them. Scaling the world by hub *degree* scales a quantity the survival filter is actively eating. | `docs/WORLD-SCALE-PREREGISTRATION.md` §3 |

> **K1 and K2 together are the reason the Tier-1 stimulus looks the way it
> does.** `lattice_L1` has one hub at degree 3 — 12 edges, inside the 20-edge
> window, with a hub ratio of 0.75, comfortably above the 0.3 threshold. It
> is not an arbitrary choice; it is close to the only shape the substrate can
> currently hold structure in. **That is an architectural bandwidth limit, and
> it is the first measurement that bears directly on H24.**

---

## L. The H24 Scale Ladder — pilot result — MEASURED 2026-10-23

Protocol: 300 cycles per rung, `colony=FULL`, `seed=20261023`. Rungs 0–2
completed. Rung 3 stopped early due to a bootstrapping defect (disclosed in
`docs/WORLD-SCALE-PREREGISTRATION.md` §7.3). Engine unchanged.

| # | Fact | Evidence |
|---|------|----------|
| **L1** | **Increasing environmental variety while holding `MAX_PREDICTIONS = 20` fixed decreased developmental inventory.** Rung 0 (3 triangles, 1 hub): **91 items**. Rung 1 (12 triangles, 4 hubs): **66 items**. Rung 2 (48 triangles, 16 hubs): **56 items**. A 16× increase in distinct world structures produced a 38% decrease in cumulative inventory. | `docs/scale_ladder.json`; `docs/WORLD-SCALE-PREREGISTRATION.md` §7.1 |
| **L2** | **Theories and questions decreased in step with beliefs.** Rung 0: 10 theories, 10 questions. Rungs 1 and 2: 4 theories, 4 questions. The upper layers did not compensate for the lower-layer loss. | same |
| **L3** | **Discovery ceased entirely in the final 100 cycles for Rungs 1 and 2.** `new_in_last_100_cycles = 0` for both. Rung 0 still showed 3 new items in its final 100 cycles. | same |
| **L4** | **The simple version of H24 — more world → more development — is not supported by this pilot.** The direction of the effect was the opposite of what an unconstrained environmental hypothesis predicts. | same; `docs/WORLD-SCALE-PREREGISTRATION.md` §7.1 |
| **L5** | **L4 does not falsify H24.** H24 says the plateau is constrained by environmental *information content*. The pilot tested *environmental variety under uniform frequency*. A world with structure-selective frequency (stable scaffold + incremental novelty) is a different test and has not been run. H24 remains open. | `docs/WORLD-SCALE-PREREGISTRATION.md` §7.1, §8 |
| **L6** | **Architectural efficiency collapses with world size under uniform frequency.** Normalising inventory against the number of distinct triangles in the world: Rung 0 = 91/3 = **30.3 items per triangle**; Rung 1 = 66/12 = **5.5**; Rung 2 = 56/48 = **1.17**. A 16× increase in available world structure produced a **26× decrease** in structure extracted per unit world. | `docs/scale_ladder.json` |
| **L7** | **The failure propagates bottom-up through the developmental ladder.** Beliefs fell first (17 → 12 → 10), then theories and questions collapsed together (10 → 4 → 4), then dreams (52 → 28 → 24). The degradation matches the causal chain: the prediction window starves processes, processes starve workflows, workflows starve beliefs, beliefs starve theories and questions, theories and questions starve dreams. Later layers do not partially compensate for earlier losses — they amplify them. | same |
| **L8** | **This is a dilution test, not a scale test.** Rungs 1 and 2 held attentional capacity (`MAX_PREDICTIONS = 20`) and all thresholds fixed while flooding the prediction window with competing patterns. A fair scale test would hold *competition per slot* fixed. The pilot's result is therefore a property of the stimulus design, not of the architecture's ceiling. | `docs/WORLD-SCALE-PREREGISTRATION.md` §7.2 |
| **L9** | **The architecture responds strongly to stimulus structure.** The fact that inventory falls monotonically (91 → 66 → 56) with world complexity under dilution, rather than plateauing immediately, shows the architecture is sensitive to its environment in a mechanistically predictable way. This is not a sign of fragility; it is the property that makes a scaffold + novelty experiment interpretable. | same |

> **L1–L4 together are a clean inversion of the naive expectation**, and
> they are a measured fact: more world, less mind, under the uniform-variety
> regime. The mechanism that would explain this is stated separately in §L-M
> (assumption) because it has not been directly tested.

## L-M. The frequency-dilution mechanism — PROPOSED, NOT TESTED

This is the mechanism hypothesis that explains L1–L4. It is an assumption,
not a fact, and it lives here rather than in §L because it was not directly
measured by the pilot.

| # | Assumption | If it is wrong |
|---|------------|----------------|
| **LM1** | The inventory decrease is caused by **frequency dilution through `MAX_PREDICTIONS = 20`**: when N triangles are uniformly frequent, their 3N directed edges compete equally for 20 slots; an arbitrary top-20 rarely contains a complete 3-cycle; without a complete 3-cycle no process, workflow, or belief forms. | If raising `MAX_PREDICTIONS` to 40 does not recover the Rung-1 inventory, the dilution mechanism is not sufficient and another ceiling is binding. |
| **LM2** | A **stable scaffold** (3 frequently-repeating triangles holding the top-20 window) plus **incremental novelty** (one fresh triangle per K cycles, introduced infrequently enough to be visible when it arrives) would allow the inventory to grow beyond 91. | If a scaffold + novelty world produces inventory ≤ 91 regardless of novelty rate, the mechanism is wrong and the ceiling is architectural. |

**What would confirm LM1:** the Rung-1 inventory (66) rises to near Rung-0
levels (91) when `MAX_PREDICTIONS` is doubled to 40, holding everything
else fixed.

**What would confirm LM2:** the scaffold + novelty experiment (§8 of the
preregistration) produces cumulative inventory > 91 and growing, with
theories and questions tracking the novelty arrival rate.

**What would falsify both:** a scaffold + novelty world with `MAX_PREDICTIONS
= 40` still produces inventory ≤ 91. In that case the ceiling is
architectural — not the prediction window, and not the stimulus shape.

---

## M. Burst Assimilation and Recurrence Scaffolding — MEASURED (2026-10-23)

Protocol: 100 cycles, `colony=FULL`, `seed=20261023`, exact apples-to-apples
comparison between Rung 0 (Core only) and Burst Assimilation (Core + 1 new triangle
every 30 cycles with an 8-cycle concentrated burst, then sustained alongside core).

| # | Fact | Evidence |
|---|------|----------|
| **M1** | **Scaffolding prevents the multi-layer collapse.** In a 300-cycle scaffolded run (`docs/scale_ladder_scaffold.json`), theories stayed high (13–14 vs 4 in uniform variety), questions remained active (11–13 vs 4), and beliefs reached 18 across all rungs. | `docs/scale_ladder_scaffold.json` |
| **M2** | **Passive single-exposure novelty fails to clear early-stage filters.** In `scaffold_stream`, novelty introduced 1× every K cycles had raw event count 1, which was silently rejected by `PREDICTION_MIN_COUNT = 5` and `STABLE_THRESHOLD = 0.3`. Total inventory grew only 91 → 95 across 300 cycles. | `organica/scale_streams.py`; `docs/scale_ladder_scaffold.json` |
| **M3** | **Burst reinforcement successfully clears Layer 1 and drives upward developmental emergence.** In 100 cycles, Burst Assimilation broke the Rung-0 baseline: **inventory rose 82 → 99 (+20.7%)**, **theories jumped 10 → 16 (+60.0%)**, **experiments & investigations jumped 10 → 18 (+80.0%)**, and **beliefs rose 16 → 19**. | Experimental run on 2026-10-23 (`test_burst.db` vs `Rung 0`) |
| **M4** | **The empirical rule established:** *Organica develops substantially more structure when novelty is introduced with enough local reinforcement to survive the architecture's early-stage filters.* | Facts M1–M3; L1–L9 |
| **M5** | **The effect compounds over longer horizons.** At 300 cycles, Burst Assimilation pushed total inventory to **113** (vs Rung 0 baseline of **91**, a **+24.2%** increase), with **theories rising 10 → 17 (+70%)**, **questions rising 10 → 13**, **beliefs rising 17 → 20**, **experiments rising 12 → 19**, and **new discoveries continuing across epochs (10, 7, 2, 6 vs 6, 6, 0, 2)**. Development did not freeze at 91. | 300-cycle experiment on 2026-10-23 (`test_burst_300.db`, `test_burst_curve.db`) |
| **M6** | **The developmental ceiling is not a fixed architectural constant.** Two prior candidate ceilings were falsified: 74 items (broken by Rung 0 baseline at 91) and 91 items (broken by Burst Assimilation at 113). The ceiling moved when the presentation schedule of novelty changed. | Facts I3, L1, M5 |
| **M7** | **The core conclusion established:** *Organica's developmental capacity is not fixed. It is strongly dependent on the structure and presentation schedule of novelty.* Novelty must first become stable enough through local reinforcement to enter the developmental hierarchy; when it does, the organism assimilates it repeatedly throughout the run rather than experiencing a one-time initialization boost. | Facts M1–M6 |

## M-H. Open Research Questions on Burst Assimilation

1. **Does the attractor keep moving at longer horizons?** The 1,200-cycle extension reached 128, below the preregistered 140+ expansion band, and added 2 items in its last 100 cycles. This is continued but slowing discovery, not a settled attractor. See `docs/scale_horizon_1200.json` and journal §24.
2. **Does earlier assimilated structure serve as developmental substrate for later novelty?**

---

## N. Held-Out Prediction Pilot — MEASURED (2026-10-23)

Protocol: Organica and two tag-transition baselines trained on the same
bootstrap scaffold plus burst curriculum cycles 1–200, then frozen and scored
on cycles 201–300. The 0.5 F1 threshold and 50-cycle half-life were fixed in
the benchmark code before the pilot was run. Results are from one seed and do
not estimate run-to-run uncertainty.

| Model | Known-tag F1 | Known-tag log loss | All-tag F1 | All-tag log loss |
|---|---:|---:|---:|---:|
| Organica G1 predictions | 0.413 | 0.775 | 0.363 | 0.816 |
| First-order tag Markov | **0.504** | **0.182** | **0.417** | 0.335 |
| Recency-decayed temporal association | 0.485 | 0.184 | 0.399 | **0.334** |

**N1.** On this synthetic task, both simple baselines exceed Organica's G1
predictions in F1; Markov also has substantially lower log loss on known tags.
Organica has higher recall but lower precision at the common 0.5 threshold.
The decayed model is a one-step tag-transition graph with a 50-cycle
exponential half-life, not a separate cognitive architecture.

**N2.** The held-out window includes nine test-only tags (402 tag occurrences).
Known-tag scores and scores including those novel labels are reported
separately in `docs/heldout_prediction.json`. Organica's G1 strengths are not
calibrated probabilities, so its Brier and log-loss values are descriptive.
This pilot does not measure recovery of latent causes and is not a multi-seed
comparison.

---

## O. Known-Cause Recovery Pilot — MEASURED (2026-10-23)

The generator emits only feature pairs, not cause or regime labels. The scorer
uses hidden labels to define 12 gold same-cause feature pairs. Two regimes
alternate every 100 cycles, and 10% of events are random pairs from a separate
noise vocabulary. Training used cycles 1–200; cycles 201–300 were not ingested.

| Model | True pairs | False pairs | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| Organica surviving structures | 12 | 10 | 0.545 | 1.000 | 0.706 |
| Same-event co-occurrence | 12 | 6 | **0.667** | 1.000 | **0.800** |
| Temporal transition graph | 12 | 138 | 0.080 | 1.000 | 0.148 |

On this single-seed pilot, same-event co-occurrence is the strongest
structural-recovery model. The generator uses cleanly separated feature
families, and pairwise association recovery does not demonstrate causal
intervention knowledge. Full protocol and limits: `docs/ground_truth_recovery.json`;
implementation: `organica/ground_truth_worlds.py` and
`benchmarks/ground_truth_recovery.py`.

---

## P. Phase H External-Validity Campaign — MEASURED (2026-10-23)

Ten seeds (20261023–20261032) ran with `PYTHONHASHSEED=0`. Prediction uses
the same deterministic curriculum on all seeds, so its ten scores are
identical and its intervals are degenerate; this is a fixed-stream repeat, not
ten sampled input worlds. Recovery varies the world and Organica's seeded sleep
RNG. Intervals are deterministic 10,000-resample percentile bootstrap
intervals over per-seed results.

### Held-out next-event prediction

Train cycles 1–200, freeze, test cycles 201–300; fixed 0.5 F1 threshold.

| Model | Known-tag F1 | 95% bootstrap interval |
|---|---:|---:|
| Organica G1 | 0.4126 | [0.4126, 0.4126] |
| First-order Markov | **0.5040** | [0.5040, 0.5040] |
| Recency-decayed association | 0.4851 | [0.4851, 0.4851] |

The Markov-minus-Organica paired F1 difference is **+0.091**; the
decayed-association difference is **+0.072**. Both intervals are degenerate
because the stream and all resulting scores repeat exactly. These results
confirm the pilot result on this one curriculum; they do not estimate
variation across input worlds.

### Known-cause structure recovery

Organica's surviving structures are compared with same-event co-occurrence and
the temporal transition graph. Results are F1 mean and 95% bootstrap interval:

| World | Organica | Same-event co-occurrence | Temporal graph |
|---|---:|---:|---:|
| Clean (10% noise) | 0.7041 [0.6835, 0.7250] | **0.8000 [0.8000, 0.8000]** | 0.1482 [0.1481, 0.1484] |
| Overlapping (20% noise, 2 shared tags, 10% decoys) | 0.5469 [0.5150, 0.5764] | **0.7642 [0.7632, 0.7662]** | 0.2199 [0.2162, 0.2234] |
| Stress (30% noise, 3 shared tags, 25% decoys) | 0.1091 [0.0991, 0.1226] | **0.7959 [0.7959, 0.7959]** | 0.2803 [0.2792, 0.2812] |

Co-occurrence outperforms Organica in all three conditions. Organica
outperforms the temporal graph in clean and overlapping worlds, but loses to
it in the stress world. Its relative F1 position worsens from clean to
overlap by **0.121** (95% interval [−0.167, −0.077]) and from clean to stress
by **0.591** ([−0.607, −0.576]) versus co-occurrence; the corresponding shifts
versus the temporal graph are **−0.229** ([−0.273, −0.187]) and **−0.727**
([−0.743, −0.712]). This does not support the hypothesis that the current
structural machinery becomes more useful as these worlds get harder.

**Limits.** The prediction seeds do not vary the input stream. The recovery
scenarios are controlled synthetic stress cases, not a sample of natural
worlds. Recovery scores undirected pairwise same-cause association, not
causal intervention knowledge or held-out regime prediction. The campaign
does not identify which cognitive layer contributes to any advantage.
Protocol and full per-seed results: `docs/PHASE-H-PREREGISTRATION.md` and
`docs/phase_h_results.json`; runner: `benchmarks/phase_h_campaign.py`.

---

## Q. Phase I Regime-Shift Detection — MEASURED (2026-10-23)

The frozen campaign ran 20 seed-paired shifted and stationary-control worlds
in each of two generator families, with `PYTHONHASHSEED=0`. Organica, a
first-order Markov model, and recency-decayed transition association were
scored by predictive surprise. Alarm thresholds were set within each world
from cycles 20–59; a detection required two consecutive five-cycle windows
above the mean-plus-three-SD threshold. Lower restricted delay is better;
misses count as 31 cycles. Paired delay intervals are 97.5% percentile
bootstrap intervals, adjusted for the two family opportunities.

| Generator family | Organica delay | Markov delay | Decayed delay | Control false-alarm rates (Organica / Markov / decayed) |
|---|---:|---:|---:|---:|
| Cause-mixture switch | 2.55 | 2.80 | 4.25 | 0% / 5% / 0% |
| Mapping-swap | 2.65 | 1.25 | 1.20 | 0% / 15% / 15% |

In cause-mixture worlds, Organica's paired advantage over Markov was only
0.25 cycles (97.5% interval [−0.25, 0.75]); its 1.70-cycle advantage over
decayed association had interval [−0.05, 5.75]. Neither comparison met the
preregistered effect-size and interval rule. In mapping-swap worlds, the
baselines detected faster on average: baseline-minus-Organica delay was
−1.40 cycles for Markov (97.5% interval [−1.900, −0.949]) and −1.45 for
decayed association ([−1.950, −0.950]). However, both exceeded the 10%
stationary false-alarm limit (3/20 controls each); that family cannot
establish a valid baseline comparison under the frozen rule. The primary
success criterion was not met in either family.

The campaign does not demonstrate a comparative advantage for Organica on
this detector. It also does not establish that the baseline alarms would
remain excessive under a detector calibrated from independent stationary
worlds. Any calibration redesign must be preregistered as a new evaluation;
these thresholds were not tuned after observing this result. Full per-world
records and internal cycle counts: `docs/regime_shift_results.json`; frozen
protocol: `docs/REGIME-SHIFT-PREREGISTRATION.md`; runner:
`benchmarks/regime_shift.py`.

## R. Phase J Gradual Post-Shift Adaptation — MEASURED (2026-10-23)

The frozen campaign ran 20 paired shifted and stationary-control worlds in
each of two generator families (80 worlds total), with PYTHONHASHSEED=0.
The event-level next-tag NLL was measured online during cycles 30–79. The
primary shift-specific measure is each model's mean NLL in the shifted world
minus its paired stationary-control mean; positive baseline-minus-Organica
differences favor Organica. Lower NLL is better.

| Generator family | Model | Shifted NLL | Control NLL | Adaptation cost |
|---|---|---:|---:|---:|
| Cause-mixture ramp | Organica | 6.441 | 3.944 | 2.497 |
|  | First-order Markov | 1.234 | 1.056 | 0.178 |
|  | Decayed association | 1.221 | 1.098 | 0.122 |
| Mapping-mixture ramp | Organica | 7.702 | 4.975 | 2.727 |
|  | First-order Markov | 1.350 | 0.908 | 0.442 |
|  | Decayed association | 1.207 | 0.931 | 0.276 |

Baseline-minus-Organica adaptation-cost differences were **−2.319** nats/event
for Markov (97.5% interval [−2.798, −1.865]) and **−2.375** for decayed
association ([−2.853, −1.920]) in cause-mixture worlds. In mapping-mixture
worlds they were **−2.285** ([−2.700, −1.854]) and **−2.451**
([−2.865, −2.022]), respectively. All four intervals favor the baselines.

The final-stable non-inferiority guard also failed: Organica's NLL exceeded
Markov by **4.478** nats/event ([3.944, 4.989]) and decayed association by
**4.500** ([3.967, 5.011]) in cause-mixture worlds; corresponding mapping
gaps were **3.617** ([3.018, 4.169]) and **3.796** ([3.199, 4.348]). The
preregistered primary rule was not met in either family. The result gives no
evidence that Organica adapts with less predictive error on these tasks.

These are replications within two specified synthetic gradual-transition
families, not a sample of natural environments. The adaptation cost is
paired to a stationary control and the final-stage guard checks absolute
shifted-world performance; neither isolates a particular cognitive layer.
The self-referenced settling-time measure is descriptive only. Full per-world
loss curves: docs/post_shift_adaptation_results.json; protocol:
docs/PHASE-J-ADAPTATION-PREREGISTRATION.md; runner:
benchmarks/post_shift_adaptation.py.

---

## S. Correction to I1 — how flat the structure actually is — MEASURED (2026-10-24)

**Why this exists.** The Tier-1 artifact was regenerated on 2026-10-24 from the
campaign's own per-colony part files so that it carries the per-cycle discovery
series. That meant checking every published claim against the regenerated file
rather than assuming it had survived. I1's phrase *"holds that configuration
for 2,999 cycles"* did not survive. Journal §31 is the record; this is the
measurement.

**The measurement.** Cycle by cycle from `docs/force_matrix.json` → `series`:

| Colony | cycles at 18 beliefs / 7 subjects | of the tail half | last excursion | pool values seen |
|---|---:|---:|---:|---|
| FULL | 2,964 / 2,999 (98.8%) | 100% | cycle 212 | 18, 16 |
| SALIENCE | 2,984 / 2,999 (99.5%) | 100% | cycle 221 | 18, 16 |
| NO_CONTRADICTIONS | 2,957 / 2,999 (98.6%) | 100% | cycle 163 | 18, 16, **20** |
| **NO_QUESTIONS** | **2,277 / 2,999 (75.9%)** | **95.1%** | **cycle 2,738** | 18, 16 |
| NO_DREAMS | 2,984 / 2,999 (99.5%) | 100% | cycle 185 | 18, 16 |
| ANTI_EIG | 2,943 / 2,999 (98.1%) | 100% | cycle 539 | 18, 16 |

**S1** | **The retained belief count is exactly constant.** 15 in every one of the
2,999 cycles of every colony, with no exception. | `docs/force_matrix.json` → `series.beliefs`

**S2** | **The pre-retention pool is modal, not constant.** It dips to 16 beliefs
over 6 competing subjects and returns. The excursions are brief — 1–17 cycles
long in five arms, 15 to 56 of them, all over by cycle 539 — and are real
substrate states, not a recording artifact: `pre_beliefs` is the count of
belief candidates produced before retention. | same

**S3** | **`NO_QUESTIONS` is the exception.** It is at 16/6 for 722 of its 2,999
cycles (24%), with excursions as late as cycle 2,738 — and it is also the arm
that discovers the most (112 items; 95% of them by cycle 977, 99% by cycle
2,167). The five arms whose structure stops moving are the five that stop
discovering; the one arm that kept discovering kept moving. One arm in one run:
a correlation, not a cause. | `docs/discovery.json` → `discovery_curves`

**S4** | **No launch gate is affected.** G-CS, G-P1, G-SUP and G-EXP hold in
**100% of cycles** in all six colonies, and G-SUS is **100%** in every tail
half, re-verified cycle by cycle from the regenerated artifact. G-P1/G-SUP
require the pool to *exceed* 15, and 16 does. The verdicts, the noise floor,
the inventory totals and the +10,776% support growth stand as published. | `docs/force_matrix.json` → `series`

**S5** | **The corrected claim.** "Structure flat, evidence growing" is true of
the *typical* arm and needs qualification for one: five arms settle on cycle 1
and hold 18/7 for 98–99.5% of the run and 100% of the tail half; `NO_QUESTIONS`
does not. | —

Reproduce from the artifact alone: `docs/force_matrix.json` → `series` →
`pre_beliefs`, `pre_subjects_ge2`, `beliefs`.

## T — Phase K: Comparative Advantage Search (2026-10-24)

Three candidate task families, ten seeds each, scored against the **best**
simple baseline configuration from a declared grid of 24 per seed per family.
Decision rule: paired percentile bootstrap, 98.33% interval (Bonferroni across
the three families); SUPPORTED only if the interval lies wholly above zero.

| Fact | Value | Source |
|---|---|---|
| **T1** | **All three families are REVERSED.** K1 (incremental world modeling) Organica **0.5923** vs baseline **0.9360**, difference **−0.3437** [−0.3773, −0.3123]. K2 (belief revision) **0.4111** vs **0.9846**, **−0.5735** [−0.6162, −0.5309]. K3 (longitudinal integration) **0.0000** vs **0.8578**, **−0.8578** [−0.8598, −0.8571]. No family is SUPPORTED; none is INCONCLUSIVE. | `docs/phase_k_results.json` → `summaries` |
| **T2** | **The terminal outcome is H2: the search failed.** It was written into the preregistration before any Phase K outcome existed. Three more task families are ruled out, the negative-results map grows, and **V2 is not designed.** | `docs/PHASE-K-PREREGISTRATION.md` §7 |
| **T3** | **The verdicts are robust.** Re-running the bootstrap with 8 different seeds leaves all three verdicts unchanged. Dropping the single most favorable seed, and separately the single least favorable seed, also leaves every verdict unchanged. | journal §33 |
| **T4** | **The mechanism ablations came back empty — a negative attribution.** `NO_QUESTIONS` (K1) −0.0095 [−0.0328, +0.0140]; `NO_FALSIFICATION` (K2) +0.0241 [−0.0048, +0.0495]; `NO_DREAMS` (K3) +0.0000 [0.0000, 0.0000]. **All three intervals contain zero**, so question generation, falsification and dreams are not load-bearing for the tasks they were built around. Within one implementation, on synthetic worlds. | `docs/phase_k_results.json` → `summaries.*.matched_ablation` |
| **T5** | **The K3 zero is architectural, not a measurement artifact.** Three checks, each able to fail: the late structure appears in **0 of 150 cycles** (not merely the final one); every candidate type except `anomaly` mentions **0 of 12** late tags, so nothing was left unread; and a 2×2 control across 5 seeds shows the late group is incorporated **only when strictly stronger** than the group that arrived first (9–11 of 18 at late weight 3 / early weight 1; 0–1 of 18 otherwise). | `benchmarks/phase_k_diagnose.py`; journal §33 |
| **T6** | **Organica retains the early scaffold and incorporates none of the late structure under the protocol's configuration.** Core-retention F1 ≈ 0.67; late-incorporation F1 = 0.000 on all 10 seeds. The exclusion is a salience/priority competition under a bounded belief pool, which is the risk §6 of the preregistration named before the run. | `docs/phase_k_results.json` → `per_model_detail` |
| **T7** | **Six task families are now negative.** Phase H (next-event prediction), I (regime-shift detection), J (post-shift adaptation), K1, K2, K3. The question *"what class of problems benefits from a developmental architecture?"* stays **open**, with six families excluded rather than one verdict reached. | journal §32, §33 |
| **T8** | **One bookkeeping note.** The live recording `docs/phase_k_results.ndjson` holds **29 of 30** seeds: K1/20261023 was completed by an earlier harness version before the checkpoint existed and was carried in through the results-file resume path. The authoritative results file holds all 30, and the two agree numerically on every overlapping seed. | `docs/phase_k_results.json`, `docs/phase_k_results.ndjson` |

Reproduce from the artifact alone: `docs/phase_k_results.json` → `summaries`,
`per_model_detail`; the root cause with `python benchmarks/phase_k_diagnose.py
--scale 4 --seeds 5`.

## T — Phase K results (2026-10-24)

**T1** | **All three families are REVERSED.** K1 (incremental world modeling) Organica **0.5923** vs baseline **0.9360**, difference **−0.3437** [−0.3773, −0.3123]. K2 (belief revision) **0.4111** vs **0.9846**, **−0.5735** [−0.6162, −0.5309]. K3 (longitudinal integration) **0.0000** vs **0.8578**, **−0.8578** [−0.8598, −0.8571]. No family is SUPPORTED; none is INCONCLUSIVE. | `docs/phase_k_results.json` → `summaries`

**T2** | **The terminal outcome is H2: the search failed.** It was written into the preregistration before any Phase K outcome existed. Three more task families are ruled out, the negative-results map grows, and **V2 is not designed**. | `docs/PHASE-K-PREREGISTRATION.md` §7

**T3** | **The verdicts are robust.** Eight different bootstrap seeds leave all three verdicts unchanged. Dropping the single most favorable seed, and separately the least favorable seed, also leaves every verdict unchanged. | journal §33

**T4** | **The mechanism ablations came back empty — a negative attribution.** `NO_QUESTIONS` (K1) −0.0095 [−0.0328, +0.0140]; `NO_FALSIFICATION` (K2) +0.0241 [−0.0048, +0.0495]; `NO_DREAMS` (K3) +0.0000 [0.0000, 0.0000]. **All three intervals contain zero**, so question generation, falsification and dreams are not load-bearing for the tasks they were built around. Within one implementation, on synthetic worlds. | `docs/phase_k_results.json` → `summaries.*.matched_ablation`

**T5** | **The K3 zero is architectural, not a measurement artifact.** Three checks, each able to fail: the late structure appears in **0 of 150 cycles**; every candidate type except `anomaly` mentions **0 of 12** late tags; and a 2×2 control across 5 seeds shows the late group is incorporated **only when strictly stronger** than the group that arrived first (9–11 of 18 at late weight 3 / early weight 1; 0–1 otherwise). | `benchmarks/phase_k_diagnose.py`; journal §33

**T6** | **Organica retains the early scaffold and incorporates none of the late structure under the protocol's configuration.** Core-retention F1 ≈ 0.67; late-incorporation F1 = 0.000 on all 10 seeds. The exclusion is a salience/priority competition under a bounded belief pool — the risk §6 of the preregistration named before the run. | `docs/phase_k_results.json` → `per_model_detail`

**T7** | **One bookkeeping note.** The live recording `docs/phase_k_results.ndjson` holds **29 of 30** seeds: K1/20261023 was completed by an earlier harness version before the checkpoint existed and was carried in through the results-file resume path. The authoritative results file holds all 30, and the two agree numerically on every overlapping seed. | `docs/phase_k_results.json`, `docs/phase_k_results.ndjson`

## U — The freeze and Phase L (2026-10-25)

**U1** | **Organica 1 is frozen as of the `v0.9.0` tag.** Not abandoned and not "no more commits" — **no more architectural modifications to the engine.** The engine is a fixed reference object: everything afterwards measures it, nothing afterwards quietly changes it. Frozen: `organica/sleep.py`, `memory.py`, `paths.py`, `streams.py`, `branch_streams.py`, `scale_streams.py`, `ground_truth_worlds.py`, and the published result artifacts. `organica/__init__.py` is excluded deliberately — it carries the version. | `docs/V1-FREEZE.md`; journal §35

**U2** | **The freeze is enforced, not declared.** `tests/test_v1_freeze.py` reads the frozen files out of the `v0.9.0` tag and compares them against the working tree, failing and naming the difference if one differs, and skipping honestly when the tag is unreachable. It was **proved to fire** by temporarily modifying a frozen file. The first version compared raw bytes and failed on 13 untouched files because of `core.autocrlf`; it now compares git object IDs, because a check that fires on noise trains the reader to ignore it. | `tests/test_v1_freeze.py`; journal §35

**U3** | **Phase L asks a different question from every previous phase.** Not *"can Organica do X?"* but **"how much pressure is required for new structure to displace old structure?"** It is a measurement phase, not a benchmark hunt, and its success criterion is a **reproducible displacement curve**, not a win. The protocol is frozen and was committed before any outcome existed. | `docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`

**U4** | **The Phase L endpoints are named.** **Displacement Index** = `late_structure_retained / late_structure_available`; **Preservation Index** = `early_structure_retained / early_structure_original`; **Revision Threshold** = the pressure at which DI crosses PI, and the headline quantity. No composite score is computed — a harmonic mean is what destroyed an endpoint in Phase K. | same

**U5** | **The independent variables are varied one at a time.** V1 support ratio (8 points, **primary**), V2 arrival timing, V3 novelty density, V4 belief-cap pressure, V5 contradiction pressure. V5 is included **because it could overturn the framing**: if late structure that *contradicts* displaces while merely *new* structure does not, the operative variable is conflict rather than strength, and the phase's title is wrong. | same §4

**U6** | **The instrument audits are permanent and required.** A **discrimination control** must show first-seen-wins at DI ≈ 0 / PI ≈ 1 and last-seen-wins at DI ≈ 1 / PI ≈ 0, so the metric can tell "never revises" from "always revises"; an **endpoint ceiling check** must show a perfect model at 1.0 on both. Both passed when the harness was built. The campaign does not run if either fails. | `benchmarks/phase_l_campaign.py --self-test`

**U7** | **Launch is not run.** The protocol is written, the harness is built and validated, and the protocol is reviewed **before** the campaign executes. Four terminal outcomes are pre-committed, and **none of them authorises a V2**. | journal §35; preregistration §7

## V — The Phase L pilot defects (2026-10-25)

**V1** | **The Phase L pilot's "result" was an artifact, not a finding.** The reduced-scale execution check returned `DI = 0.000` at **all eight** points of the support-ratio sweep, with `PI = 0.611` at all eight. Read casually that is a clean negative result — *the late structure never displaces the early structure at any pressure*. It is not a result at all: **the support ratio was not varying anything.** | journal §36; preregistration Amendment 1

**V2** | **Cause 1 — the late group arrived after the run ended.** The arrival cycle was an **absolute** number (150), but the pilot ran 150 cycles, so the late group never became active and the late structure was never available to measure. Fixed: arrival is now a **fraction** of the run (`ARRIVAL_FRACTION = 0.25`, i.e. the same 150-of-600 proportion), scaled proportionally in every arm. | `benchmarks/phase_l_campaign.py`; Amendment 1

**V3** | **Cause 2 — an unmeasurable index was reported as `0.0`.** A ratio with a zero denominator was scored as zero, so "the late structure was never available" was recorded as "the organism retained none of the late structure". Fixed: undefined ratios are `None`, excluded from the curve and counted as unmeasurable; an arm with any unmeasurable point returns the verdict `UNMEASURABLE` and **no scientific verdict**. This is the same failure mode as the Phase K collapsed harmonic mean. | `benchmarks/phase_l_campaign.py`; AGENTS.md rule 13

**V4** | **Cause 3 — the contradiction arm (V5) was a no-op.** The code shared a feature of the **late** group with itself, rebuilding `late_0` exactly as it already was. The world was byte-identical with the arm on and off, so V5 measured nothing. Fixed: the shared feature now comes from the **early** group, so the two groups genuinely compete for the same subject. Verified: the gold sets and event streams now differ between `off` and `on`. | `benchmarks/phase_l_campaign.py`; Amendment 1

**V5** | **Cause 4 — the density arm (V3) fed the engine only part of the world.** The event stream was chunked at a fixed 12 events per cycle while the density arm varies that rate (6/12/24/48), so at density 4.0 the engine saw **7,200 of 28,800** events while the harness reported a complete run. Fixed: the world's own `events_per_cycle` is passed to the engine. | `benchmarks/phase_l_campaign.py`; Amendment 1

**V6** | **A fifth defect, found by reading rather than running: the RT bootstrap measured the wrong statistic.** It resampled the **DI−PI gap** and reported its min/max. Criterion 4 of the protocol asks for the **crossing location**: the RT from a paired bootstrap over seeds with a 99% interval excluding both endpoints. Fixed: the resampled statistic is the index of the first label at which DI overtakes PI, the interval is a percentile interval over those locations, seeds are resampled **paired across labels**, and "excludes both endpoints" is tested directly against the sweep bounds. | `benchmarks/phase_l_campaign.py`; Amendment 1

**V7** | **Why the existing audits did not catch any of it.** Both Phase L audits check the **metric** — that it separates the two poles, that a perfect model reaches the ceiling. Both passed on the broken world, because the metric was fine. The **design** was dead. *An audit of the instrument is not an audit of the experiment.* | journal §36

**V8** | **A third audit now exists: the degeneracy audit.** For every cell of every arm it checks that both groups are available for measurement, that the support ratio actually changes the early/late event mix, that the contradiction arm differs from the plain arm, and that the density arm actually changes the event count. Every check is failable by construction and the campaign does not run if it fails. It earned its place immediately: **the first version of the audit itself had a scaling inconsistency with the campaign builder**, and the audit caught it by failing the run before anything executed. | `benchmarks/phase_l_campaign.py --self-test`; Amendment 1

**V9** | **After the fix, the axis is live — and this is still not evidence.** The corrected pilot (reduced scale, **one seed**, disclosed pilot, never evidence) gives DI 0.000 / 0.000 / 0.000 / 0.000 / 0.167 / 0.500 / 0.667 / 0.667 and PI 0.667 / 0.722 / 0.667 / 0.667 / 0.611 / 0.278 / 0.000 / 0.000 across 1:4 → 6:1, with the curves crossing between 2:1 and 3:1. **No Phase L campaign has been run and no Phase L outcome exists.** | journal §36; `.scratch/phase_l_smoke2.json`

**V10** | **The decision interval is settled: 99%.** The protocol stated a **98.33%** interval and glossed it as "Bonferroni across the arms"; across five arms Bonferroni gives 0.05/5 = 0.01, i.e. **99%**, while 98.33% corresponds to 0.05/3 — Phase K's correction factor, carried over by accident. The owner ruled before any outcome existed that **the intent governs and the stray percentage is the accidental constant**: the procedure is preserved and the number corrected. Recorded as **Amendment 2**. Phase K's own 98.33% figures are unaffected — that protocol had three families and 0.05/3 was correct there. | Amendment 2; preregistration §6, §8

**V11** | **The transferable rule, now AGENTS.md rule 13.** *An identical value at every point of a sweep is a measurement defect until proven otherwise.* The protection is not more scrutiny of the result — it is scrutiny of the **design**, before the run, by an instrument built to contradict the code rather than confirm it. | AGENTS.md rule 13; journal §36

## W — Amendment 2: the interval, the diagnostic, and the hidden-degeneracy hunt (2026-10-25)

**All of this was recorded BEFORE any Phase L outcome existed.** The campaign had not been run when these facts were written.

**W1** | **The Phase L decision interval is 99%, not 98.33%.** The protocol stated a 98.33% interval and glossed it as "Bonferroni across the arms". Those disagree: across five arms Bonferroni gives 0.05/5 = 0.01, i.e. **99%**, while 98.33% corresponds to 0.05/3 — Phase K's correction factor over its three families, carried over by accident. The owner ruled that **the intent governs and the stray percentage is the accidental constant**. Phase K's own 98.33% figures are unaffected. | Amendment 2; preregistration §6, §8

**W2** | **Success and failure are now stated plainly** (preregistration §6.1). Success is a stable displacement curve with an interior, reproducible crossing. Failure is a flat DI, a flat PI and no crossing — a characterization of the organism sitting at one pole, and a publishable one. **The campaign must be able to fail**; no gate is relaxed to make it produce a win. | Amendment 2 §6.1
**W3** | **A new diagnostic: the Displacement Score, `DS = DI − PI`.** The owner's review raised the sharpest remaining point: **DI and PI are not opposites**. DI 0.8 with PI 0.8 is *coexistence* — the late structure was learned and the early structure kept — and that is not revision; DI 0.8 with PI 0.1 is genuine displacement. K3 already established that acquisition and displacement are different phenomena. **DS is a diagnostic only**: not a primary metric, not a success criterion, in no verdict, never averaged. A curve where DS stays near zero while DI rises shows *accumulation*, not *revision*. | Amendment 2; `benchmarks/phase_l_campaign.py`
**W4** | **Revision latency is elevated to co-primary reporting.** Two organisms can end at the same DI and PI while crossing at completely different cycles — same endpoint, different developmental behavior. The mean and median revision latency and the count of seeds that reached it are now reported per sweep point. **The four success criteria are unchanged**: latency is a co-primary *report*, not a fifth criterion. | Amendment 2; preregistration §3.4
**W5** | **Hysteresis is deliberately deferred, not forgotten.** Running the axis in reverse (late → early) would show whether the system crosses back — path-dependence, which a genuinely dynamic intelligence might show. It is recorded as the natural successor phase and deliberately **not** added now: a protocol that measures one thing well is worth more than one that measures two things imperfectly. | Amendment 2
**W6** | **Two preregistered secondary outcomes are now implemented.** The protocol declares three secondary outcomes; the harness computed only *absolute late incorporation*. *Revision latency* and the *knowledge-preservation trajectory* are now computed from a per-cycle DI/PI trace. The trace is **per-cycle, not cumulative**, so it answers "when did the organism start asserting the late structure"; the final indices still come from the last report alone, and a consistency check confirms the trace's last point equals the final DI and PI. | Amendment 2; `benchmarks/phase_l_campaign.py`
**W7** | **A fourth instrument audit: the V4 pressure audit.** Phase G measured the belief pool **starved** on the live study stream — mean 5.17 beliefs, max 6, against `MAX_HYPOTHESES = 15`. If the pool never fills, the belief-cap arm cannot change anything and a flat V4 curve would be a statement about the engine, not the organism — the way V5 was inert before Amendment 1. The audit runs the frozen engine at both ends of the V4 sweep and requires the cap to bind. **It does: peak beliefs 11 at cap_pressure 3, 15 at cap_pressure 24.** | Amendment 2; `benchmarks/phase_l_campaign.py --self-test`
**W8** | **The pre-flight hunt for hidden degeneracy — all five checks pass.** (a) The engine is **deterministic** for a given seed (0.5 / 0.277778 twice), so the paired bootstrap over seeds resamples something real. (b) Different seeds give different results (4 distinct of 4), so there is seed variance to resample. (c) Every arm has a **full denominator** — min `late_available` = 18 and min `early_available` = 18, of 18 possible. (d) The V4 belief cap **binds** (W7). (e) The protocol's own factual claims hold: "600 cycles, matching the Phase K K3 family" was checked against Phase K's preregistration, which does say 600 cycles for K3. | Amendment 2
**W9** | **One false record, fixed.** The results file recorded `"python_hash_seed": "0"` unconditionally — asserting the pinned value whether or not it was set. It now records the **actual** value, records whether the pin was met, and warns loudly when it was not. | Amendment 2; `benchmarks/phase_l_campaign.py`
**W10** | **Two performance defects fixed before the long run.** The intermediate checkpoints recomputed the 10,000-replicate bootstrap after **every** cell — it cannot change until an arm is complete, so that was hours of pure arithmetic; it is now computed once at the end. And the audits are computed **once at startup** and carried into the run rather than rebuilt per cell. | Amendment 2

## X — Phase L V1: the primary axis, measured (2026-10-25)

**Verdict: `H3-L — INCONCLUSIVE`.** Protocol remedy: *raise n; conclude nothing*. No outcome here authorises a V2. Full detail: `docs/phase_l_results.md`.

**X1** | **The run completed: 80 of 80 cells, 8,057.8 s, 10 seeds per point, `PYTHONHASHSEED=0` pinned and recorded as the actual value.** Decision interval 99.00% (alpha 0.01), 10,000 bootstrap replicates, 12 workers. Engine = frozen `v0.9.0`, verified unchanged by the freeze test. **Unmeasurable cells: 0** — nothing was excluded and nothing was zeroed. | `docs/phase_l_results.json`
**X2** | **All four instrument audits passed on the live run** — discrimination control, ceiling check, degeneracy audit, V4 pressure audit (peak beliefs 11 → 15, the cap binds). The sweep is non-degenerate and the perturbation lands. | `docs/phase_l_results.json`
**X3** | **The V1 curve has a shape, and the pilot's flat line is gone.** DI 0.000 / PI 0.73–0.79 across 1:4, 1:3, 1:2, 1:1 (preservation plateau) → DI 0.283 / PI 0.600 at 2:1 (coexistence) → DI 0.722–0.750 / PI 0.022–0.000 at 3:1, 4:1, 6:1 (displacement). | `docs/phase_l_results.md`
**X4** | **Three of the four pre-committed criteria are met.** (1) DI monotone increasing, range 0.750 ≥ 0.25. (3) The curves cross at **3:1**, interior to the sweep. (4) The crossing is reproducible: paired bootstrap interval **[5.0, 5.0]**, **10,000/10,000** replicates found a crossing, 8 alternative bootstrap seeds all `INTERIOR`, leave-one-seed-out crossing = **3:1 in 10 of 10**. | `docs/phase_l_results.md`
**X5** | **Criterion 2 (PI monotone decreasing) was NOT met.** Mean PI rises 0.789 → 0.794 between 1:4 and 1:3 (+0.005, against a per-point sd of 0.070) before falling monotonically through the rest of the sweep. The criterion was evaluated once by the committed code and it failed. **It was not re-read, relaxed, or reinterpreted.** | `benchmarks/phase_l_campaign.py`; `docs/phase_l_results.md`
**X6** | **Revision latency (co-primary report): 0/10 seeds reached DI > 0.5 at 1:4 through 2:1; 10/10 at 3:1 (mean 347 cycles, median 342), 4:1 (mean 285), 6:1 (mean 236).** The transition is abrupt rather than gradual — from *never* to *always* between 2:1 and 3:1. Reported separately, never averaged, **not** a criterion. | `docs/phase_l_results.md`
**X7** | **DS (diagnostic only) shows a coexistence band, not a clean handover.** At 2:1 the organism retains 60% of the early structure while holding 28% of the late structure (DS −0.317); the gap only turns positive at 3:1 (DS +0.700). DS entered no verdict. | `docs/phase_l_results.md`
**X8** | **A wording defect in the protocol, recorded rather than exploited.** The `H3-L` bucket is described as *"intervals too wide to place RT"* — but the RT interval is `[5.0, 5.0]`, the narrowest possible, and criterion 4 passed. The verdict is INCONCLUSIVE because **criterion 2 failed**, not because the threshold could not be located. The criterion was not re-read; the verdict stands. A future phase must say what "inconclusive" means when the interval is narrow and a different criterion failed. | `docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md` §7; `docs/phase_l_results.md` §9
**X9** | **What is established:** the instrument works; the pilot's flat line was an artifact and the fix held; the organism sits at the preservation pole under low displacement pressure; on this axis DI and PI cross at 3:1 and that crossing is highly reproducible. **What is not:** a boundary in the H2-L sense, PI's monotone decrease, any claim about capability, anything about V2–V5 (deliberately not run), and the baseline rule was recorded but not exercised in V1. | `docs/phase_l_results.md` §8

## Y — Phase L raise-n (n=30): the verdict stands, and now the reason is visible (2026-10-25)

**Verdict: `H3-L — INCONCLUSIVE`, unchanged — and now with TWO of the four criteria unmet.** The protocol's remedy was *raise n; conclude nothing*; it was taken, on the primary axis, with the same sweep, same criteria, no edits. **No outcome authorises a V2; V2–V5 were not run.**

**Y1** | **The raise-n run: 240 of 240 cells, 30 seeds/point, 12,738.1 s, all four instrument audits pass, 0 unmeasurable cells.** It is a strict **superset** of the n=10 run — the original ten seeds are the first ten of the new list, so the 80 original cells were **reused, not recomputed** — and the reuse was verified: all 80 are present and byte-identical in the merged file. The n=10 record is preserved as `docs/phase_l_results_n10.json` / `.ndjson`. | `docs/phase_l_results.json`; `docs/phase_l_results.md` §1
**Y2** | **The Revision Threshold did not move.** Still **3:1**, interval **[5.0, 5.0]**, **10,000/10,000** replicates finding a crossing, eight alternative bootstrap seeds all `INTERIOR`, leave-one-seed-out at 3:1 in **30 of 30** folds. Tripling n did not move the one quantity the phase set out to locate. | `docs/phase_l_results.md` §4
**Y3** | **Criterion 1 flipped.** *DI monotone increasing* was **met** at n=10 and is **not met** at n=30: the top of the curve dips 4:1 0.722 → 6:1 0.715, a step of −0.007 [−0.037, +0.022]. Criterion 2 still fails (+0.011 [−0.026, +0.044] at 1:4 → 1:3). Criteria 3 (range 0.722, crossing interior at 3:1) and 4 ([5.0, 5.0]) still hold. | `docs/phase_l_results.md` §3
**Y4** | **The curve is a step function, not a ramp.** Three plateaus, two transitions: **DI = 0.000 exactly** at 1:4–1:1 for all 30 seeds; DI ≈ 0.71 at 3:1–6:1 with **PI = 0.000 exactly** (the early structure entirely gone); PI ≈ 0.74 across the low end. Revision latency: **0/30** seeds reach DI > 0.5 at 2:1, **30/30** at 3:1 (mean 356 cycles, median 351) — the transition is abrupt,
not gradual. | `docs/phase_l_results.md` §2
**Y5** | **Both failing criteria fail on steps whose 99% paired interval contains zero.** Every step whose interval excludes zero is a real transition (1:1→2:1 dPI −0.111 [−0.157, −0.065]; 2:1→3:1 dDI +0.502 [+0.443, +0.559], dPI −0.567 [−0.619, −0.522]); every step whose interval contains zero is a plateau edge. The failures are the *signs of two differences indistinguishable from zero*. | `docs/phase_l_results.md` §5
**Y6** | **The criteria are not equally stable, and the data says so.** Resampling the 30 measured seeds: criteria 3 and 3b hold in **100%** of random 10-, 20- and 30-seed subsets; criterion 1 holds in 19.3% / 16.1% / 0%; criterion 2 in 12.0% / 6.6% / 0%; **all four together in 2.9% / 1.2% / 0%**. The n=10 run's criterion-1 pass was itself one of the lucky 19%. **This does not re-score the protocol** — the verdict stands, no boundary is claimed — but it establishes that **strict monotonicity is not a property this organism's displacement curve has**, at any practical n, and that "raise n" is exhausted as a route to satisfying criteria 1 and 2. | `docs/phase_l_results.md` §6
**Y7** | **The added seeds moved the curve more than resampling should allow.** DI at 6:1: original 10 seeds 0.750 vs added 20 seeds 0.697 (p = 0.0022 against random 10-vs-20 splits); DI at 2:1: 0.283 vs 0.164 (p = 0.0103). Every non-zero gap points the same way. The seed enters the world only through `random.Random(seed)` and the entity set does not depend on it, so the seeds *should* be exchangeable — but the campaign's seeds are **consecutive integers**, which is exactly the pattern non-exchangeability produces and also exactly what an unlucky draw produces. A **seed-exchangeability audit** (30 fresh, non-consecutive, pre-declared seeds at the point with the largest gap) was run to tell them apart; it is an instrument audit and produces no experimental claim. **The seeds ARE exchangeable**: the fresh scattered set gave DI 0.7241 at 6:1 against the campaign's own 0.7148 (30 seeds) and 0.7500 (its original ten) — a difference of +0.0093, **p = 0.60** against random 30/30 splits of all 60 measured values — and its own arbitrary half-split gap of **−0.0407** has the *opposite sign* to the campaign's +0.0528 at similar magnitude. **The original ten seeds were an unlucky high draw, not a seed-block artifact**, so the paired bootstrap over seeds is sound and the n=30 curve is the better estimate because there are more seeds, not different ones. | `docs/phase_l_results.md` §7; `docs/phase_l_seed_audit.json`; `benchmarks/phase_l_seed_audit.py`
**Y8** | **Amendment 3 was committed before the raise-n run existed, and it is now history:** n 10 → 30 (same sweep, criteria, interval, engine, terminal outcomes); a **real defect found and fixed** — the "paired" bootstrap paired by *position in the records list*, and since the records arrive in completion order that order differs per label, it was pairing unrelated seeds across labels (the fix changes no n=10 number: still [5.0, 5.0], 10,000/10,000, same verdict); the **adjacent-difference diagnostic** added (a diagnostic only — not a metric, not a criterion, in no verdict); and the analysis promoted from an uncommitted scratch script to committed code, `benchmarks/phase_l_analyze.py`. | `docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md` Amendment 3

## Z — Phase L: the published characterization (2026-10-25)

**The protocol verdict is unchanged: `H3-L — INCONCLUSIVE`. The characterization is a separate artifact and does not re-score it.** Full text: `docs/PHASE-L-SYNTHESIS.md`.

**Z1** | **The one-sentence conclusion:** *"Organica 1 does not appear to exhibit a continuous coherence–plasticity trade-off. It appears to exhibit regime behavior separated by a reproducible transition region."* This is the owner's reading of the pattern that survived raising n — a **characterization**, not the protocol verdict, and **not** a capability claim. | `docs/PHASE-L-SYNTHESIS.md` §1
**Z2** | **What survived increasing n:** the preservation plateau (**DI exactly 0.000 for all 30 seeds** across 1:4–1:1), the transition region, the crossing at **3:1**, the reproducible RT (**[5.0, 5.0]**, 10,000/10,000 replicates, 8/8 alternative bootstrap seeds `INTERIOR`, leave-one-seed-out 3:1 in **30 of 30**), and the abrupt latency shift (**0/30 → 30/30** seeds reaching DI > 0.5 between 2:1 and 3:1). | `docs/PHASE-L-SYNTHESIS.md` §2
**Z3** | **What did not survive:** strict monotonicity — which got *weaker*, exactly as expected if it was never a property of the organism. | `docs/PHASE-L-SYNTHESIS.md` §3.2
**Z4** | **Why raising n again is not the answer.** The reason to raise n was that the +0.005 PI reversal might be **noise around an otherwise monotone curve**, or the curve might be **genuinely step-shaped** — worlds that predict differently. n=30 distinguished them: the low-end steps are each consistent with zero, the plateaus are exact across all 30 seeds, and the monotonicity criteria fail *more* firmly. **The campaign was not failing for want of precision; it was failing because the curve is not the curve the protocol expected.** "Raise n until it says what I want" is the failure mode a pre-registration exists to prevent. | `research-journal/phase_g_findings_20261021.md` §40
**Z5** | **The decision:** publish the characterization — not `H2-L` (not reached), not "boundary established" (not established) — and only then consider the secondary axes, which are no longer tests of *which variable moves a smooth boundary* but of **why the curve is step-shaped**: what sets the width and location of the transition region. **V2–V5 remain unrun**; no Phase L outcome authorises a V2. | `docs/PHASE-L-SYNTHESIS.md` §6; journal §40
**Z6** | **The dangerous question, and its answer:** *"a stable, reproducible threshold at 3:1 — that is a boundary, isn't it?"* **It is not.** A threshold is a boundary only if the trade-off is a continuum the threshold divides; here the curve is flat on both sides of the crossing, and the crossing is stable because the organism **switches regimes** — a real property, but not the property the protocol asked for. Calling it a boundary would be the same category of error as re-scoring the failed criteria, only more flattering. And "regime" describes the shape of a displacement index, a preservation index and a latency on synthetic worlds — **it is not a claim about intelligence**. | `docs/PHASE-L-SYNTHESIS.md` §7

## AA — The development audit trace (2026-10-25)

**Specification only. No build, no outcome, no engine change.** Full text: `docs/AUDIT-TRACE-SPEC.md`.

**AA1** | **The question the spec answers:** *could an investigator reconstruct the reason — what evidence was used, how the claim was formed, what the competing candidates were — without asking the system?* Not natural-language explanation, not counterfactuals inside the trace, and not instrumentation by default. | `docs/AUDIT-TRACE-SPEC.md` §1, §0
**AA2** | **Level 1 (provenance) is available.** `get_ancestry(candidate_id, max_depth=7)` returns a parent tree; every candidate already stores `parent_ids` and every candidate is persisted as a JSON payload. **The limits are explicit and must appear in the record:** depth 7, and the 4,000-event window (`recent(n=4000, event_type='sleep')`) — a parent outside it returns `found: False`, which means *not found in window*, never *no parent*. **Provenance terminates at candidates, not at events:** no parent link points at an event, so Level 1 and Level 2 are different kinds of link. | `organica/sleep.py:841-858`, `organica/sleep.py:876-886`
**AA3** | **Level 2 (evidence) is available, and the counts are not what they look like.** `support_count` = `precedes[subject][expectation]`, a count of **temporal transitions** built with `lookback=3`. `raw_contradiction = max(0, total_flow − support)` where `total_flow` is **all** outgoing flow from the subject — so `contradiction_count` is the subject's **competing flow, not a count of contradicting observations**. `confidence = support / (support + contradiction)`. The proposed record format ("12 supporting observations, 4 contradictory observations") was therefore **corrected** before it was written down. | `organica/sleep.py:1480-1512`
**AA4** | **Level 3 (selection) is available without instrumenting the engine — under the default policy.** The report contains only survivors, but the full contest is reconstructible: pool = ordered component pairs of the cycle's workflow concepts + adjacent pairs of its process candidates + meta-concepts with ≥5 related candidates; the cycle's own Layer-2/3 outputs are **in the report**, and the priors are **in the substrate** (`all_workflows`/`all_processes`/`all_metas` add back stable priors at `STABLE_THRESHOLD` 0.3). Ranking is deterministic — `sorted(by (−salience, subject))`, cap `MAX_HYPOTHESES = 15`, weights `0.25` each over tension/curiosity/novelty/revision — so the retained set is a function of derivable quantities. **Under `stochastic` it is not**: a weighted lottery over salience, reconstructible only as a bound. | `organica/sleep.py:473-509`, `1418-1528`, `1534-1647`
**AA5** | **Two selection stages exist, not one.** A candidate is first culled by the **death rule** (confidence < 0.15 and support+contradiction ≥ 3) *before* the contest, and separately `_natural_selection` reinforces Layer-1 candidates (+0.05) or decays them (×0.8) and prunes those under the death threshold — the report exposes those **counts** but not their **identities**. The trace must carry the identities. `_candidate_key` has no hypothesis branch, so **beliefs are never decayed or pruned by that stage**. | `organica/sleep.py:1499-1500`, `1752-1802`, `1804-1817`
**AA6** | **Two disclosed defects, neither patched — the engine is frozen.** **D1:** `contradiction_count` is a contention measure and is easy to misread; the trace must name it. **D2:** the temporal graph's lookback query has **no `event_type` filter** (`SELECT tags FROM events ORDER BY time DESC LIMIT 3`), while `store()` scopes co-occurrence and tag-frequency edges to world events — so a supporting transition can originate from the organism's **own previous sleep payload**. The trace reports the world/self split of every belief's support. | `organica/memory.py:261-263`, `memory.py:321-343`

**AA7** | **Limb verdicts.** **Predict** — supported (prediction candidates carry source/target/strength/evidence/lineage; `strength` is an internal score, **not** a calibrated probability). **Trace** — supported as a structured record, subject to AA2–AA4. **Revise** — supported as a structural operation (`revision_delta`, `prior_confidence`, support/contradiction, generation counters); this is an operational test of revision, not evidence of rational revision. **Experiment** — **not supported**: proposals exist (`ExperimentCandidate`: payload, expected outcome, cost, priority) but **nothing executes them** (gap G1), so a proposal can be traced and its outcome cannot. | `organica/sleep.py:88-98`, `1505-1512`; facts sheet G1
**AA8** | **The spec's load-bearing claim was tested, not just asserted.** `benchmarks/audit_trace_probe.py` is an **instrument probe, not an experiment about the organism**: it runs the frozen engine on the frozen cause-world generator and, at every cycle, rebuilds the selection contest from the report and the substrate and compares. **Default arm** (belief cap 15, the engine's own): 120 cycles, **1,412 beliefs checked, A1 evidence replay 0 failures, A2 selection reconstruction 120/120 cycles**, 4 candidates died under the confidence rule, 0 lost on rank. **Stress arm** (cap 5, so the cap binds): 60 cycles, **290 beliefs checked, A1 0 failures, A2 60/60 cycles**, 3 died, **403 lost on rank**. The default arm alone was a weak test — its pool peaked at 12 against a cap of 15, so the *lost-on-rank* branch never fired — which is why the stress arm exists, and the table says so. **The checks can fail**: `tests/test_audit_trace_probe.py` breaks the auditor (zeroing curiosity; dropping a tag from the temporal graph) and requires A1 and A2 to go red; they do. **Establishes:** the selection contest needs **no hook inside the engine**. **Does not establish:** generality (one world family, one policy), the `stochastic` policy (reconstruction degrades to a bound), the ancestry/field-honesty/separation criteria (they belong to the build), or anything about learning. | `docs/AUDIT-TRACE-SPEC.md` §10; `docs/audit_trace_probe.json`; `docs/audit_trace_probe_stress.json`

**AA9** | **The trace is pre-committed to adjudicate a live question, or it is a second inventory.** The audit layer is attractive, and attractive things become projects: it could be built, extended and admired without ever settling a question the project wanted answered — which would make it a *second* inventory ("how many events resolve?"). The rule is therefore **pre-committed, not aspirational**: the next protocol's success criteria must contain at least one **trace-derived diagnostic**, and a result that fails it **fails the protocol even if the headline behavior is correct**. **The first instance is the disqualifier: *a predicted-correct result whose supporting evidence is self-sourced is not a transfer result.*** The trace reports the world/self split of every belief's support, because the temporal graph's lookback window has no `event_type` filter and a supporting transition can originate from the organism's own previous sleep payload (D2). **That is D2's first concrete use, and it turns a disclosed defect into a live scientific instrument** — a defect that can defeat a claim is worth more than a defect that is merely recorded. A claimed revision must be visible as a change in a world-supported claim with its prior state resolved; a claimed explanation must resolve to event ids, never to counts and never to the system's own account of itself. **Second guard:** the trace's own metrics — evidence-trace completeness, lineage completeness, selection reproducibility — are **diagnostics of the instrument**, reported and never criteria. | `docs/AUDIT-TRACE-SPEC.md` §11; `AGENTS.md` rule 18; manual §8.14

**AA10** | **The probe's headline was corrected to match what it verified, and the correction produced a measurement.** The first version reconciled the **aggregate** `precedes` table against the engine's reported support counts: that shows the auditor reproduces Organica's *counts* and *selection decisions*, **not** that it can identify the individual experiences behind a count. The specification now says so in those words — **aggregate evidence reconciliation and selection reconstruction passed** — and event-level attribution is its own check (**A7**), measured with a passive store-time observer. **Default arm: A1 1,412 beliefs / 0 failures, A2 120/120 cycles, A7 1,412 beliefs / 0 failures with 244 aggregate edges reconciling exactly.** **A4 behavior invariance passes**: observer on vs off, reports byte-identical apart from `ran_at`. **Three corrections, each verified against the source first:** a cycle returns **14** candidate lists (not 13); the lookback window **includes the event being stored** (`store()` inserts the row before recording edges), so the window is the event itself plus two others and **within-event tag pairs also become temporal edges**; and **a post-hoc replay from the final log cannot reconstruct the window** — the engine's query has no `rowid` tiebreak, and sleep-candidate rows are pruned — so attribution **requires** a store-time observer whose guard mirrors the engine's `event_type != "sleep"` rule. **D2 measured: of 307,857 attributed support transitions, 53,980 (17.5%) were self-sourced** — the prior event was the organism's own sleep payload — so roughly one belief-support transition in six rests on the organism's own output; the stress arm gives 15.3%. **The probe found two defects in itself** (an observer that attributed sleep-event transitions; an invariance check that compared `ran_at`), both caught by the checks rather than by inspection. | `docs/AUDIT-TRACE-SPEC.md` §10; `docs/audit_trace_probe.json`; `docs/audit_trace_probe_stress.json`

**AA11** | **The self-sourced figure needed its denominator fixed — and the fix changed what the number was *about*, not how big it was.** The first version pooled the support of every reported belief across every cycle in which it was reported; because a belief's support count is **cumulative**, a transition that occurred early is counted again in every later cycle where the belief survives. That pooled number counts **support references**, not distinct evidence. The probe now reports **three views**: (i) **distinct evidence behind reported beliefs** — 802 of 4,481 = **17.9%** self-sourced, deduplicated by `(from_tag, to_tag, prior_event_id, to_event_id)` and restricted to the edges that actually back a reported belief — **this is the disqualifier's figure**; (ii) pooled support references — 53,980 of 307,857 = 17.5%; (iii) all distinct transitions recorded, **including edges no reported belief ever rested on** — 5,436 of 12,583 = **43.2%** self-sourced. **Correcting the denominator moved the headline only slightly** (17.5% → 17.9%), and that agreement is worth stating; **but it surfaced a separate and much larger number**: 43.2% of the organism's entire distinct transition surface is its own output, against 17.9% of the evidence actually behind its claims. Those are different surfaces and the trace must report both rather than let one stand in for the other. **The forced-tie arm is now run:** the clock is patched so every four consecutive stores share a timestamp, producing **479 stores with a genuinely tied window**, and the observer reproduces the engine's choice anyway — **A7 stays exact** (2,589 distinct transitions, 241 aggregate edges reconciling, 0 mismatches; tie arm: A1 692 beliefs 0 failures, A2 60/60 cycles). The honest statement: the **implementation** is deterministic for identical queries over identical data, so the observer's re-run selects the same rows; the **schema** still does not determine the window under a tie, and a replayer that did not observe at store time could not rely on it. | `docs/AUDIT-TRACE-SPEC.md` §3.3, §10, §11; `docs/audit_trace_probe.json`; `docs/audit_trace_probe_stress.json`; `docs/audit_trace_probe_tie.json`

**AA12** | **The figure's population is now stated precisely, and the disqualifier became a per-claim rule.** The **17.9%** is a share of the **union of the unique evidence transitions behind beliefs reported during the run** — deduplicated, restricted to the edges those beliefs rested on. It is **not** a per-claim share (a particular claim's own support can be far more or far less self-sourced) and it is **not** evidence that self-sourced support caused an incorrect prediction. A run-level share cannot carry a per-claim claim, so the disqualifier is rewritten as a **per-claim rule fixed in advance**: (1) report the world/self split for the **claim's own** support; (2) a **majority** of it must be world-derived; (3) its self-sourced share must be **no higher than the run's baseline rate** for beliefs; (4) the comparison is against the claim, never the organism in general, and a failed condition **fails the protocol even if the prediction was correct**. **Why the rule is conservative, and why that is stated:** the contamination is now **measured, not shown to be consequential** — nothing yet demonstrates that a self-sourced transition caused a wrong answer — so the disqualifier is a statement about **what counts as evidence of transfer**, not a claim that the organism is damaged by its own output. That is also why it is pre-committed: a criterion that only bites once the harm has been demonstrated would never bite at all. **Whether self-sourced support *hurts* is now a measurable question, and the trace is the first instrument that can ask it — not asked here.** | `docs/AUDIT-TRACE-SPEC.md` §3.3, §10, §11
**AA13** | **The observer's window match is an implementation match, not a schema guarantee.** The engine runs `SELECT tags FROM events ORDER BY time DESC LIMIT 3`; the observer runs the **same ordering clause and limit** with a **wider projection** (`id, time, event_type, tags, rowid`) so the contributing rows can be identified. The two are not byte-identical SQL, and SQLite does not promise a stable order among rows that tie on `time`. The correct statement: **the observer's window matched the engine's in every tested case, as an empirical match on the tested SQLite implementation** — and the evidence for that match is **A7's exactness**, because a window mismatch on any store would have broken the reconciliation. The forced-tie arm pushes on this deliberately: **479 stores with a genuinely tied window, 0 mismatches** (692 beliefs, 241 aggregate edges). The **60-cycle forced-tie artifact is committed** as `docs/audit_trace_probe_tie.json` — 60 cycles, 479 tied windows, A1 692 beliefs / 0 failures, A2 60/60 cycles, A7 692 beliefs / 0 failures. The schema still does not settle tied ordering, and a replayer that did not observe at store time could not rely on it — which is exactly why A7 requires store-time observation. | `docs/AUDIT-TRACE-SPEC.md` §3.3, §10

**AA14** | **The per-claim rule's reference rate is now FROZEN, not recomputed on the run it judges.** The reference rate is **17.9%** — the distinct-evidence self-sourced share measured on the calibration probe (default arm, 120 cycles). Two rules, both fixed now: it is **not recomputed on the evaluated run** (a threshold derived from the same data it judges is a description that moves with the result, and a run with unusually self-sourced beliefs would otherwise relax the criterion meant to constrain it), and it **may only be re-calibrated on data that is not being judged**, with any re-calibration recorded before the next protocol runs. It is also labelled a **provisional calibration value, not a precise universal cutoff**: it rests on **one run, one world, one policy** (`salience`, the default). The honest description of condition 3 is *"no more self-sourced than the reference claim's support was"* — a comparison against a fixed calibration, not a claim about a universal threshold. | `docs/AUDIT-TRACE-SPEC.md` §11
**AA15** | **A3's definition is fixed in advance, and the window span is now measured rather than estimated.** The trace carries two different links: **Level 1 developmental lineage** (candidate → candidate via `parent_ids`, terminating at Layer 1 — **no parent link points at an event**) and **Level 2 evidential linkage** (claim → transitions → events). Level 1 answers *"where did this structure come from?"*; Level 2 answers *"what evidence supports it?"*; **success in one cannot stand in for success in the other**. A3 will report three things separately: **lineage reachability** (share of extant structures resolving back to Layer 1 within depth 7), **evidence linkage** (share of extant claims whose support resolves to event ids with a world/self split), and a **truncation split** — *aged out* (window censoring, **a persistence problem**) / *depth-truncated* (**a representation problem**) / *no parent* / *missing record* (**a data defect**, and the one that would matter most). **And the measurement corrects an earlier estimate by more than an order of magnitude: the engine stores 2,374.68 sleep events per cycle, so the 4,000-event cognition window spans only 1.7 cycles — not the "roughly 40–130 cycles" this project previously asserted from a guess.** The estimate was wrong, and the correction is recorded rather than quietly fixed. Consequence: a lineage still being produced stays inside the window (candidates are re-stored every cycle), while one that stopped being produced is gone within about 1.7 cycles — so the developmental history of anything the organism has moved on from is unrecoverable, not slowly censored. | `docs/AUDIT-TRACE-SPEC.md` §12; `docs/audit_trace_probe.json` → `A7_event_level_attribution.cognition_window`
**AA16** | **Fidelity is not sufficiency.** The probe establishes **fidelity to the implemented rule**: the auditor reproduces what the engine did, including under a binding cap. It does **not** establish that an intact reconstruction is a *uniquely correct account of why a belief arose*. A reconstruction can be exactly faithful to the algorithm and still be a shallow account of development — it explains the arithmetic of selection, not why the structures formed. That is a separate validation question, and A3 is where it begins. The candidate outcomes for the follow-up characterization study — none pre-committed — are **correctness**, **persistence**, **revision resistance**, **confidence inflation** and **false-positive rate**: does self-sourced support *hurt*, and in what way? | `docs/AUDIT-TRACE-SPEC.md` §10, §12
**AA17** | **Seven literal template placeholders had shipped in the committed audit-trace specification** — `{ties}`, `{t_dist:,}`, `{t_edges}`, `{t_cycles}`, `{t_a1:,}`, `{t_a2}` (committed in the second and third review rounds) and `{share:.1f}` (introduced by the fourth round's script and caught before commit). They sat inside sentences that assert results — *"producing **{ties}** stores with a genuinely tied window"* — so in a document read as a measurement record a literal placeholder reads as **a number that was never computed**, when in fact the value was sitting in a committed artifact the whole time. Corrected in place from the artifacts: **479** tied windows, **2,589** distinct transitions, **241** aggregate edges, **60** cycles, **692** A1 beliefs, **60** A2 cycles, **692** A7 beliefs, **17.9%** reference rate. The lesson is narrow: **a placeholder is silent** — it looks like a sentence in a diff, so another careful read will not find it. What found it was a mechanical substitution pass with a leftover-assertion, and the guard is now standing: **`tests/test_doc_placeholders.py`** scans the guarded document set, asserts that no unsubstituted placeholder survives, and carries its own proof-of-firing. **A check that must be run beats a check that must be remembered.** | `docs/AUDIT-TRACE-SPEC.md` §10; journal §46
**AA18** | **A3 is met, and the answer to its key question is that the observer's limit and the architecture's limit are the same limit.** The ancestry auditor walks each cycle's reported structures' parent chains against the engine's own cognition window and classifies every branch that fails to resolve. **Lineage reachability 1.000** (8,061 of 8,061 structures resolve back to Layer 1 within depth 7), **evidence linkage 1.000** (1,412 of 1,412 claims resolve to event ids with a world/self split), **zero honesty errors**, and the structure-level truncation split empty (0 / 0 / 0 / 0) — while the *branch-level* count shows **105 aged-out branches**, because every structure resolves through at least one branch that stayed inside the window. The same holds on the stress arm (3,240 structures, 1.000) and the forced-tie arm (3,988 structures, 1.000). **So an investigator can reconstruct the lineage of everything Organica still holds, exactly — and cannot see further back than Organica remembers, because there is nothing further back to see.** That is good news for the trace and a hard ceiling on the project's distinguishing property: **developmental provenance in Organica 1 has the horizon of the organism's own memory.** | `docs/AUDIT-TRACE-SPEC.md` §13; `docs/audit_trace_probe.json` → `A3_ancestry_honesty`
**AA19** | **The window is NOT the binding constraint on lineage depth, and the measurement corrected section 12's claim that it was.** Section 12 said the window was "the more likely binding constraint", because the window spans only 1.7 cycles of stores. **That was wrong.** **Surviving candidates are re-stored every cycle** — Layer-1 candidates by the natural-selection decay path (`sleep.py:1784-1800`), higher-layer candidates by the report's re-derivation and the stable-prior add-back (`sleep.py:476-509`) — so an ancestor that is still alive stays in the window however old it is. **A lineage's depth is not bounded by the window's recency; what bounds it is the DEATH of an ancestor.** Measured: the window holds 3,998 candidates, the oldest last stored 1 cycle ago, content spanning 2 distinct cycles — so a *dead* structure's history is unrecoverable almost immediately, while a *living* one's is recoverable indefinitely. **Two sweeps prove the branches are reachable rather than inert**: the window sweep falls from 1.000 at the engine's window to 0.971 at 100 candidates (2 aged out) to 0.000 at 25–50 (68 aged out); the depth sweep falls from 1.000 at depth 7 to 0.809 at depth 3 to 0.221 at depth 1 (53 depth-truncated) — so **the engine's depth limit of 7 is not binding; the chains are shorter than it.** | `docs/AUDIT-TRACE-SPEC.md` §12, §13; journal §47; AGENTS.md rule 21
**AA20** | **The lineage is RE-DERIVED, not carried — and the lineage the trace shows is the PRESENT lineage, not the historical one.** A candidate's identity is a content hash (`_make_id` = `sha256("|".join(key_parts))[:8]`, `sleep.py:45-48`) but the identity **does not include the parent set**, and higher-layer structures are re-formed every cycle with parents **recomputed** from current state (`sleep.py:1432`, `1450`, `1467`, `1384`). So the same content identity can carry a **different lineage** later. **Consequence: the trace reconstructs the organism's current descent, not the history of that descent.** "Reconstruction of surviving developmental state" is the correct phrase; "developmental history" is not. Diagnostic: a surviving structure's parent set is identical in **94.5%** of 3,883 structure-cycles, but **87.2% of all 8,416 lineage links point at structures re-derived in that same cycle** (12.8% carried) — so the identical sets are deterministic re-derivation, not copied edges, and **this corrects an earlier reading of mine that called them "carried forward"**. | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §2; journal §48
**AA21** | **The engine's survival rule is ASYMMETRIC across layers, and this is the fact the whole acquisition design rests on.** `_natural_selection` (`sleep.py:1752-1802`) reinforces a structure whose key current experience re-produced, and otherwise decays it ×0.8 and prunes it below `DEATH_THRESHOLD = 0.15`. **But `_candidate_key` returns `""` for every type except concept, phrase, loop and prediction** (`sleep.py:1804-1817`), so **meta-concepts, processes, workflows, hypotheses, theories, questions, dreams, investigations and experiments are NEVER decayed and NEVER pruned by that path.** So: **Layer 1 survives only if current experience keeps producing its content key** (the true "persistent reconstruction"), while **Layers 2–4 persist as rows while they stay in the window and are re-formed with recomputed parents** (closer to row persistence with re-derived edges). Hypotheses die by their own rule: `conf < 0.15` and `support + contradiction ≥ 3` (`sleep.py:1499`). **So "persistent reconstruction" is accurate for Layer 1 and misleading for the rest, and the experiment must not treat "the structure survived" as one thing.** | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §2.3, §7
**AA22** | **The acquisition experiment is pre-registered: six cells, three outcomes, and the control the mechanism claim actually needs.** Parent {{removed, not}} × source experiences {removed, not} × removal applied to the **observer** or the **organism** — because **removing a parent from the auditor's reconstruction tests the trace, and removing it from the organism's state tests the maintenance mechanism**; they are different experiments. **Q1 (internal persistence) and Q2 (external provenance) are scored separately**, and the three outcomes (does the content identity reappear; is the lineage still connected; does the belief still support the preregistered task) are tracked **separately and per cycle**, so a crossover — content that persists and then stops being useful unless it is re-derived — is detectable. **The sharpest prediction is computed from the source, not fitted:** a Layer-1 structure whose key stops being produced is pruned after `⌈log(0.15/c)/log(0.8)⌉` cycles — 4 from c=0.3, 6 from c=0.5. **And the decisive control is a replay learner that stores episodes verbatim and regenerates nothing**: if continuity is reconstruction rather than recall, perfect recall is the *harder* baseline, and beating it is the result — if Organica does not beat it, "persistent reconstruction" is decoration. | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`; journal §48; AGENTS.md rule 22
**AA23** | **The acquisition study's endpoint was the WRONG METRIC, and the review caught it.** Revision 1 scored task support with **DI** — `late_structure_retained / late_structure_available` (`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md` §3.1) — which measures **structural displacement, not whether a belief predicts the world**. Revision 2 uses a **ground-truth prediction score**: for each evaluation event and each tag in a **fixed vocabulary**, predict whether that tag appears in the next event, ground truth = the observed next event, **fixed denominator** so no learner can gain by scoring on a different set. Primary metric **F1 at 0.5**, with balanced accuracy and Brier co-reported (the label set is imbalanced, so F1 alone flatters a selective learner). Organica's readout is the compressed graph from `edges_implied_by_structures` over the surviving candidates — **binary, no partial credit**. **A metric imported from another study can measure a completely different quantity, and nothing about DI looked wrong until someone asked what it measures.** | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §4.2; journal §49
**AA24** | **"Source experiences removed" left derived memory behind, and the condition is now named for what it is: EPISODE REMOVAL WITH LEARNED GRAPH RETAINED.** Ingest accumulates **`cooccurrences`** and **`tag_counts`** on every world event (`memory.py:282`, `306`), and those outlive the event rows. Removed: the acquisition `events` rows and their `precedes` edges. **Retained, deliberately:** `cooccurrences`, `tag_counts`, all `sleep` candidate rows, the cognition window, and every derived structure. So the condition is **not** a blank slate — it asks *can the organism use a representation when the episodes are gone but the compressed graph remains?* **And the same rows are removed from every learner's store**, which is what makes the comparison about *reconstruction versus replay* rather than about *different access to evidence*. Removal is **verified before any outcome is interpreted**: the episodes and their edges must be gone **and** the aggregates must still be present. | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §3.3, §9
**AA25** | **The acquisition study is now one complete, executable table: 10 runs per seed, 30 seeds, 180 engine runs — and the exact number of runs is stated because the previous version never was.** The factors are P ∈ {none, org, obs} × E ∈ {pres, rem} for **Organica only** (6 runs), and E ∈ {pres, rem} for the **replay** and **statistical** learners (2 each), with the fixed-rule ceiling as a computed reference (0 runs) — **10 per seed**. **`P-none × E-pres` IS the untreated baseline**, not an extra cell on top of six. **"Same memory budget", operationally:** identical raw rows and identical removal for every learner, with **derived state deliberately NOT equalised, because derived state IS the mechanism under test**; and in the `E-pres` cells the comparison learners can read the raw episodes Organica's cognition window has dropped, so **they have strictly more usable access and a win for Organica is conservative**. No baseline is handicapped — each is swept over its declared grid and its best score is used, with the comparator selected on the **tuning split**, never on a scoring window. **The decision rule is fixed:** 99 % bootstrap CI of the mean paired difference, 10,000 replicates, paired by seed; and the study verdict is exactly one of *"Reconstruction does work"* / *"The comparator's mechanism wins"* / *"Inconclusive"* — **every branch publishes**. | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §5–§8; journal §49
**AA26** | **Two drifts the review found, and one that is the owner's to decide.** (a) The README claimed that every abstract structure keeps *"100% verified ancestral parent links down to raw experience events"* — **the engine has never done that**: the `parent_ids` chain **terminates at Layer 1** (concepts, phrases, loops, predictions, built from tags), and the structure→event link exists only as *counts*. The README's restatement was corrected; **Law II of `docs/DESIGN_LAWS.md` still says "back to Generation 0 empirical events" and is left as written**, with the discrepancy disclosed in the audit-trace spec as **D3**, because **the frozen engine's constitution is the owner's decision, not a documentation fix.** (b) The audit-trace spec said *"all six"* acceptance criteria where the table lists **seven** — corrected. (c) The manual's status table was dated **2026-10-23** while the file recorded 2026-10-26 work — refreshed, and the missing **dated supersessions** were added to the README, `ROADMAP.md` and the V1 synthesis, so a new reader can tell what the project is doing now. **And the audit build's remaining work was smaller than the roadmap implied: only A5 and A6 were pending**, they have been **closed** (each with a proof-of-firing test), and the instrumentation has been **tagged, frozen, and stopped** at **`audit-trace-v1`** (2026-10-28) — after which **no feature may be added to it**; the instrumentation may be *fixed* if it is found wrong, but not *extended*. The **package version stays untagged**: the tag marks the instrumentation, not a release. | `docs/AUDIT-TRACE-SPEC.md` §6, §7 (D3), §9; manual §2, §8.17; journal §49; AGENTS.md rule 23

## AB — The five claims, narrowed (2026-10-26)

**A review of the project's own summary found five sentences that were wider
than the checks behind them. No measurement changed; five headlines were
narrowed, before the acquisition experiment ran.** These are corrections to
*language*, recorded here rather than quietly applied.

**AB1** | **"Revision exists" was a misnomer: Phase L measured STRUCTURAL DISPLACEMENT.** Phase L's `DI`/`PI` are **structure-retention** indices — `late_structure_retained / late_structure_available` (`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md` §3.1) — so they measure whether later *structure* displaces earlier *structure*. They do **not** measure whether a *belief* was corrected against ground truth. Belief revision is a **separate capability question**, and the one head-to-head measurement of it was a clean loss: Organica **0.4111** vs the best simple baseline **0.9846**, difference **−0.5735**, 98.33% interval **[−0.6162, −0.5309]**, **REVERSED**. So "revision exists" is not a supported summary of Phase L; "structural displacement occurs, and is sharply thresholded" is. | `docs/phase_k_results.md` §K2; `docs/phase_l_results.md` §3.1; manual §8.18; journal §50
**AB2** | **The 3:1 crossing is robust WITHIN a defined experiment, and is not a general threshold for Organica.** The crossing's stability is a property of **this engine, this world family and this support-ratio axis**. The eight alternative bootstrap seeds test **resampling stability, not new worlds** — they re-draw from the same measured seeds — and leave-one-seed-out is the same kind of check on the same data. The correct reading is: *within the axis, world family and engine tested, the transition location is highly reproducible and does not drift with n*. | `docs/phase_l_results.md` §4; `docs/PHASE-L-SYNTHESIS.md` §2.2; manual §8.18; journal §50
**AB3** | **Path dependence is supported; STRICT ORDER DEPENDENCE IS NOT TESTED.** The curriculum, scaffold, burst-assimilation and long-horizon results show that developmental outcomes vary with the experience *schedule*. But those comparisons vary the event **multiset and the order together**, so they cannot separate "order matters" from "content matters". To claim that *the same information in a different order* produces a different state, the comparison must hold the **event multiset fixed** and change **only the order** — and that comparison **has not been run**. | `docs/V1-SYNTHESIS.md` §2.2; `docs/WORLD-SCALE-PREREGISTRATION.md` §9.5; manual §8.18; journal §50
**AB4** | **Transfer: no positive transfer has been demonstrated, and the measured cross-domain result was NEGATIVE.** Cross-domain transfer is **−0.4863** (`cdt`, quoted as **−0.486** in prose) over **12 domain pairs**, with a mean shared vocabulary of **0.17 tags** — the substrate is lexical co-occurrence, so there is no representation above the tag that could cross a vocabulary boundary. **Other forms of transfer remain untested**, so this is a measured negative on one axis, not a general finding that Organica cannot transfer. | `docs/FACTS-SHEET.md` §D2; `docs/EMERGENCE-CRITERIA.md` §4; journal §24; manual §8.2, §8.18
**AB5** | **"Independently auditable" means INDEPENDENTLY RECONSTRUCTED from the engine's state — not independently replicated by another lab.** An outside reader given the report and the substrate can rebuild the developmental decision and check it; no second laboratory has reproduced this work, and nothing here is a replication result. One limit stands alongside it: the trace concerns the organism's **surviving, current** structures and does not reconstruct their full past. **The audit layer is finished** — A1–A7 are all met, the three probe arms are regenerated, and the instrumentation is **tagged and frozen at `audit-trace-v1`** (2026-10-28); from that tag no feature may be added to it. | `docs/AUDIT-TRACE-SPEC.md` §9, §10; manual §8.18; journal §50, §53
**AB6** | **The compressed project state (2026-10-26; updated 2026-10-28 after the acquisition campaign stopped at its gate), now the framing the project leads with.** *"Organica demonstrably changes its internal structure as experience and curriculum change. Under one tested pressure axis, later structures can abruptly displace earlier ones. The project has built a strong instrument for auditing surviving state and implemented decisions. It has not yet shown that these structures yield useful knowledge or positive transfer; the acquisition benchmark's first run did not change that — on a compositional task with a genuine generalization gap, the frozen engine asserted almost none of the world's relations and lost to simple transition counting. The benchmark is sound, the obstacle is one named and measured bound, and the organism is not yet able to use it."* **The 2026-10-28 revision replaces one clause** — *"the acquisition experiment could address that … it is pre-registered and not yet run"* — **which had become false.** The framing's substance is unchanged and slightly strengthened. Journal §50 is a frozen record of the 2026-10-26 wording and was not rewritten; journal §51 records the change. | `README.md` banner; manual §8.18, §8.19; journal §50, §51
**AB7** | **The lesson: a claim must be no wider than the check behind it, and the summary is where the widening happens.** Each of the five was true of some *narrower* thing the project had actually measured, and each had been stated in a broader form — in the README's own "what is established" section, in the Phase L synthesis, in the V1 synthesis and in the manual. The measurements were not the defect; the **headline** was, and the headline is what a reader takes away and repeats. This is the same defect the acquisition-plan review found in a *plan*, where `DI` — an endpoint imported from another study — measured a completely different quantity from the one it was asked about. | `AGENTS.md` rule 24; manual finding 24, §8.18; journal §50
## AC — The endpoint audit, the compositional task, and the campaign that stopped at its gate (2026-10-28)

**The acquisition endpoint was audited, and the campaign it belongs to stopped at
its own gate. Seven defects were confirmed against the code; the benchmark was
rebuilt around a compositional task whose gate passes; the frozen engine then
failed the preregistered acquisition gate on every inspected seed. Transfer was
not measured, and it is not a transfer failure.**

**AC1** | **The endpoint was measuring the wrong thing — seven defects, all confirmed against the code.** (a) The task and the readout described **different relations**: the frozen generator draws each event's cause independently (within-regime P(next = same cause) differs from P(next = that cause) by at most 0.0254), and the gold relation is a **within-event** co-occurrence that does not predict the next event. (b) **F1@0.5 was degenerate** — the Bayes-optimal model scored **0.0000**, exactly like the model that knows nothing. (c) The projection was **directional** where the gold relation was undirected: 10 of 12 gold pairs appeared in exactly one direction. (d) The "fixed-rule ceiling" was a **relation oracle**, not a prediction ceiling. (e) **Retention and transfer were one number with two names** (Brier 0.1583 pre-switch vs 0.1081 post-switch). (f) The engine's taxonomy has **no category for a tight group**: `_classify` requires a concept to have clustering <= 0.4, and a co-occurrence-defined group has clustering **1.000**, so all 12 tags classified `unclassified` and **zero** concepts formed, at 4, 5, 6 and 8 features per cause. (g) The generator's regime switch is **relation-invariant**. | `docs/ACQUISITION-ENDPOINT-AUDIT.md` §1-§2; `docs/acquisition_feature_sweep.json`; journal §51
**AC2** | **The redesigned transition world's law is FIRST-ORDER MARKOV, so it was reclassified CALIBRATION / CONTROL.** Retention window, house shape: ceiling **0.224231**, strongest baseline (cell counter) **0.229878**, tuned bigram and decayed bigram **0.240949**, grouping oracle **0.252139**, first-order Markov on raw rows **0.251693**, base rate **0.329263**, trivial **2.706801**. Headroom over the **base rate** is **0.105032** nats, which passes the probe's own 0.05-nat bar; headroom over the **strongest** baseline is **0.005647** nats, which does not. | `docs/acquisition_endpoint_audit.json`; `docs/acquisition_baseline_capability.json`; manual §8.19
**AC3** | **The compositional task IS discriminative, and the headroom is GENERALIZATION headroom.** Gap between the Bayes ceiling and the strongest simple baseline: **+0.1035** nats, 99 % interval **[+0.0996, +0.1074]** over 30 independent worlds (seeds 20261200-20261229); the binding baseline was the bigram in **23 / 30** worlds and the cell counter in **7**. G7: the gap on the **held cell's** contexts is **+0.1963** [+0.1901, +0.2033] against **+0.0425** [+0.0411, +0.0444] on the other cells — **4.6x**. Sensitivity, reported and not gated: a control with the right structure but the two transition weights swapped is only **+0.0307** worse [+0.0283, +0.0332], so the endpoint resolves the law's **structure** sharply and its **weights** only weakly. | `docs/acquisition_compositional_gate.json`; manual §8.19
**AC4** | **The +0.1035 is the BENCHMARK'S HEADROOM, not an Organica margin.** The compositional probe runs no engine and scores no learner. It answers *"is there room for something better than transition counting?"* — yes. It does not answer whether Organica occupies that room, and reporting it as a capability result inverts the finding. | `docs/acquisition_compositional_gate.json`; `docs/ACQUISITION-ENDPOINT-AUDIT.md` §8.2
**AC5** | **The frozen engine FAILED the preregistered acquisition gate on every inspected seed.** Asserted structure coverage **0.0 %-2.7 %** (0-3 of 112 world edges) against **112 / 112 (100 %)** raw temporal coverage, on seed `20261100` (exploratory) and seeds `20261101`-`20261105` (diagnostic). The world was fully present in memory; the organism did not assert it. | `docs/GATE13-PREFLIGHT-AUDIT.md`; `docs/acquisition_single_seed_pilot.json`; manual §8.19
**AC6** | **The proximate cause is ONE NAMED BOUND: `MAX_PREDICTIONS = 20` — but it is not the deepest cause (see AC12).** `_build_predictions` sorts candidates by raw temporal count and truncates at 20; on this stimulus a cell's two tags co-occur in every one of that cell's events, so within-cell pairs out-count the cross-cell transitions that carry the law and take all 20 slots. Raising **only** the cap to 1,000 — same engine, same observation stream, same five seeds — restores **98.2 %-100 %** coverage and clears Gate 13 on every seed, and the admitted cross-cell predictions survive natural selection and decay across 110 cycles. The failure is **not** a missing signal and **not** a readout defect. | `docs/GATE13-PAIRED-CAPACITY-TEST.md`; `docs/gate13_paired_capacity_test.json`; `docs/GATE13-CAUSAL-ACCOUNT.md`
**AC7** | **Organica's readout LOST, and transfer was not measured.** Pilot 0 seed, identical raw exposure for every learner, retention / transfer / revision: Organica **0.453018 / 0.453886 / 0.463391**; Replay **0.347521 / 0.349592 / 0.351989**; Statistical **0.347273 / 0.350723 / 0.352194**; base rate **0.409581 / 0.409529 / 0.406084**; Bayes ceiling **0.276259 / 0.272383 / 0.275208**. Organica scored worse than the baselines did after their episodes were deleted (the 0.403045 floor). **Transfer was not measured and is NOT a transfer failure** — a seed that fails acquisition is reported `acquisition_failed`, and the 600-cell factorial did not run. | `docs/PILOT-0-INSTRUMENTATION-AUDIT.md`; `docs/acquisition_single_seed_pilot.json`; `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` Amendment 3
**AC8** | **Two gates shared one name and disagreed, and the harness held a gate that COULD NOT FIRE.** The harness measured Gate 13 on the **raw temporal** basis (**100 %**, passed); the runner measured it on the **asserted** basis (**0.0 %**, failed) — same seed, same world, one name. The harness now implements the dual accounting, gates on the asserted figure, exposes the cap-raised treatment so the failure is attributable, and its test asserts that Gate 13 **fails** on the frozen engine and **passes** under the treatment. | `benchmarks/acquisition_harness.py`; `tests/test_acquisition_harness.py`; `docs/ACQUISITION-ENDPOINT-AUDIT.md` §8.5
**AC9** | **The readout was the limiter, not the organism — and the metric's shape shielded the baseline.** The house scoring rule excludes `target == source`: with it the base rate is **0.329263**, without it **0.402159**, while the ceiling moves only **0.224231 -> 0.230751**. The same frozen structures score **1.302721** (house) and **1.655377** (self-cells) under an ad-hoc readout, and **0.277761 / 0.362233** — **0.9784 / 0.9592** of the achievable span — under a backoff-smoothed readout whose alpha is chosen on a **tuning split**. Two earlier readings of that comparison (-0.579, then 0.940) were superseded. | `docs/acquisition_level_audit.json`; `docs/acquisition_readout_design.json`; journal §51
**AC10** | **The confirmatory sample has shrunk from 30 to 25, and that is bookkeeping, not a result.** Amendment 2 defined the confirmatory seeds as `20261101`-`20261130`; Amendment 3 designated `20261101`-`20261105` as diagnostic. Five of the thirty confirmatory seeds are now diagnostic, leaving a usable confirmatory sample of **25** (`20261106`-`20261130`). The frozen amendment text is not rewritten; the consequence is recorded rather than applied silently. | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §10; `docs/ACQUISITION-ENDPOINT-AUDIT.md` §8.6
**AC11** | **The world's relations ARE in memory, and they are a minority of the candidate space.** Raw temporal coverage is **0.97-1.00** on every seed and both stimulus shapes (**1.0000** on all six 2-tag seeds). But the `precedes` table has **366-518 rows** for a 16-tag world, only **232-240** of which are world-tag pairs, and the world's 112 edges are about a third of what any selection must retain: **precision never exceeds 0.3443** at any budget under either allocation rule. The highest-count rows are internal-vocabulary edges (`type -> olive`, `generation -> olive`), not relations of the world. | `docs/GATE13-CAUSAL-ACCOUNT.md` §4, §6; `docs/gate13_allocation_rule.json`
**AC12** | **"MAX_PREDICTIONS = 20 is the bottleneck" names the PROXIMATE bound, not the deepest cause — the deeper constraint is PRECISION, not capacity.** Coverage is a steep monotone dose-response in the global cap: **0.0000-0.0268** at 20, **0.0089-0.0714** at 40, **0.0893-0.1786** at 80, **0.9911-1.0000** uncapped — needing **240-244** asserted edges, about **12x** the budget. A **per-source** allocation rule does **not** help (258-286 edges retained for coverage **0.72-0.77**, where the global rule reaches **0.95-0.97** at 320). A **1-tag** stimulus removes the within-cell pairs by construction and still fails **0 of 6** seeds (asserted coverage **0.1719-0.1953**). In a candidate space where the signal is a third of the rows and is not clustered at the top of any frequency ordering, **no frequency-based selection can find it**. | `docs/GATE13-CAUSAL-ACCOUNT.md` §2-§6; `docs/gate13_capacity_sweep.json`; `docs/gate13_allocation_rule.json`
**AC13** | **The V2 capacity brief's premise was measured and it does not hold.** "Bounded structural allocation" assumes the useful structure does not fit within the budget. The measurements say there is **no budget to preserve more within**: the question is whether the organism can identify **which of its vocabulary items are its own** (a perfect filter buys precision **0.35 -> 0.5333** at **unchanged coverage 1.0000** — but the measured filter selects on the world's tag list and is therefore an **oracle**, not an organism-side fix) and whether it can **rank candidates by something other than raw frequency**. **No V2 build is authorised.** | `docs/V2-CAPACITY-DESIGN-BRIEF.md` addendum; `docs/ORGANICA-V2-DESIGN-BRIEF.md` §9.7; `docs/GATE13-CAUSAL-ACCOUNT.md` §7
**AC14** | **The relation table mixes world relations with the organism's own descriptive vocabulary, the separation is measurable and oracle-free, and it is NOT sufficient.** `memory.py:261` gates the *trigger* of edge recording (`if event_type != "sleep"`) but `memory.py:332` does **not** gate the *lookback window* (`SELECT tags FROM events ORDER BY time DESC LIMIT ?`), so a world event can take its `tag_from` from a sleep row — disclosed as **D2**, now measured. Rebuilding the table offline with a world-only window removes **35.7 %-40.7 %** of its rows, and **100.0 %** of the removed rows have a sleep-sourced `tag_from`. The separation uses `event_type`, which the engine already records, so it is **not an oracle**. **But with every contaminated row removed, coverage at the frozen cap of 20 is still **0.0000-0.0446** and the top 20 is still **75-100 % intra-cell**.** The substrate is **756-772 world events against 152,186-263,533 sleep events** — **201x-341x**. The V2 requirement list is therefore **three**: provenance separation, relation-family separation, and a **ranking that is not raw frequency**. The third is the hard one, and the capacity sweep showed it cannot be bought with budget. **No V2 build is authorised.** | `docs/GATE13-RELATION-SEPARATION.md`; `docs/gate13_relation_separation.json`; `docs/AUDIT-TRACE-SPEC.md` §7 (D2); manual finding 27; journal §54
**AC15** | **The ranking requirement is not "find a better formula" — every criterion the engine already stores was tested, and all of them fail.** A 60-cell grid (2 tables x 2 frequency scopes x 5 criteria x 3 seeds) over the frozen engine's own fields — `temporal_count`, `source_frequency`, `target_frequency`, `ratio` — found a **best cell of coverage 0.0804 at precision 0.4500** against a **0.50** gate: **six times short**. Neither fix works alone (0.0089); together they take coverage from **0.0000 to 0.0804** and precision from **0.0000 to 0.4500**, and flip the intra/inter balance from 20/0 to ~8-15/5-13. **The engine's own normalized criterion is actively harmful here:** on the raw table under the engine's own scope, `ratio`, `cosine` and `pmi` each select **20 engine-vocabulary edges and zero world edges** on every seed. The mechanism is measured, not inferred: `_record_tag_counts` is inside the `if event_type != "sleep":` block, so **`tag_counts` is world-scoped** and the engine's own words have **no frequency entry** — `freqs.get(tag_from, 1)` returns 1, so `ratio = count / 1 = count`, the maximum possible for that count. Adding a self-inclusive frequency scope flips the failure the other way: the engine's sleep output **names the world's tags** (`sable` 2,601 times, `olive` 7,753, `maple` 35,986, `cedar` 52,070), so the world's tags acquire enormous denominators and are penalised, and the engine's *rare* metadata words win (best world edge by the same criterion: `sable -> fern`, ratio **0.0177**, against `mutation -> cedar` at 0.1654). **The world's vocabulary and the engine's own vocabulary are not separable by frequency in either direction**, so the discriminator cannot be a per-tag statistic — it must be a **relation-level** property, and the only one available is *which event the relation came from*. **No V2 build is authorised.** | `docs/GATE13-RANKING-CRITERION.md`; `docs/gate13_ranking_criterion.json`; `benchmarks/probe_ranking_criterion.py`; `benchmarks/probe_ranking_mechanism.py`; manual finding 28; journal §55
**AD1** | **The audit build's closure was recorded in six places, and two documents still said the opposite.** A5 and A6 closed on 2026-10-28, each with a proof-of-firing test; the three probe arms were regenerated; the instrumentation was tagged and frozen at `audit-trace-v1`. The closure was written into six places (spec §9/§10, README banner, manual §2/§8.17, facts AA26/AB5, AGENTS rule 23(c), CHANGELOG). On 2026-10-29 the owner found **Paper 02 contradicting itself** — abstract and §3 said A5/A6 "remain pending" and the instrumentation "not yet frozen" while its own draft-status line and conclusion said they had closed — and the **V2 design brief's §4.3 still reading "nearly, but not fully, closed"**, with five further passages in §7/§10/§11 in the same state. **Eleven passages across four documents** corrected: Paper 02 (abstract, §3, draft-status line), the V2 brief (§4.3 heading and body, build gate 4 now marked EXECUTED, the gate-5 annotation, the §10 corrections table, the §11 table), and the superseded banners in `ROADMAP.md` and `docs/V1-SYNTHESIS.md` (which still named the pre-registration as Revision 2). | **A freeze recorded in six places is not a freeze if two documents still say the opposite.** Six agreeing places do not compensate for two disagreeing ones, and a self-contradicting document is worse than a merely out-of-date one, because it teaches the reader that its own sentences cannot be relied on. The sweep criterion was **one status, stated in every document that states it**. | `papers/02_persistent_structural_provenance.md`; `docs/ORGANICA-V2-DESIGN-BRIEF.md` §4.3, §7, §10, §11; `ROADMAP.md`; `docs/V1-SYNTHESIS.md`; manual finding 29; journal §56
**AD2** | **The papers are the publication surface, and the manuscript index now carries the owner's plan.** The repository is a research program whose codebase is one component. Near-term sequence: **Paper 01** (the honest empirical V1 account), **Paper 02** (the bounded audit-trace result). **Paper 00** separately, as a position paper, only after its broad claims and literature framing are audited. **Papers 03 and 04** held — mechanism proposals, not demonstrated-efficacy results. **Papers 05 and 06** historical until their claims are rechecked, and **no claim in either is currently strengthened by recent work — neither should be described as if it were**: Paper 05 in particular **cannot** be presented as evidence that the system prevents self-contamination, because its strict-firewall claim conflicts with the measured sleep-sourced relations (D2; quantified in `docs/GATE13-RELATION-SEPARATION.md`), and Paper 06's major lifecycle, stability and lineage claims remain unverified against the current evidence. Paper 01's core question is **"can developmental structure emerge in Organica 1?"**, answered with the negative external-task results as the boundaries of the answer. The Phase L characterization, the V1 synthesis and the audit artifacts are **research records, not manuscripts**, and the inventory stays **seven manuscript files, zero published**. Paper 01 renamed to `01_developmental_structure_formation.md` to match its revised title; Paper 02 revised to academic grade (methods, results, populations, controls, limitations, data availability); house style set to **American English**. The corpus is now organized as **two maps kept side by side**: a **research-program map** (theory / proposed mechanisms / empirical findings) and a **publication map** (which manuscript can make a coherent, evidence-backed contribution now), so the layer map orients without pressing every old manuscript or lab artifact into a paper. **Claims carry one of four statuses**: *supported within this scope*, *mixed / context-limited*, *reversed*, and *not established / not measured* — **not established is not refuted**. Paper 01's central question was narrowed accordingly and it no longer covers every probe. Paper 05 might become a paper about the **limits or failure** of cognitive isolation, but that would be a new thesis, not a revision. | **"Drafted" is not "publishable."** The strongest near-term story is the **carefully bounded empirical record, including what failed and what remains unanswered** — not the theoretical corpus, which is a program rather than a set of publishable papers. | `papers/README.md`; `AGENTS.md` rule 26; manual finding 30; journal §56
**AD3** | **Paper 00's first audit found two verified factual defects; Paper 05's core guarantee is contradicted by the measurement.** (a) Paper 00 said *"this hierarchy spans eight generations"* and then listed **nine** rows (G0–G8); `docs/architecture.md` names it correctly — *"The 8 Generational Primitives"*, with **G0 = Experience** as the substrate and G1–G8 as the primitives. (b) Paper 00 stated **Law II** as an inviolable law — *"Every structure carries explicit, verified `parent_ids` traceable to G0 events"* — without the project's own disclosure **D3**: the chain **terminates at Layer 1**, because concepts, phrases, loops and predictions are built from tags and the structure→event link exists only as counts. It is the same sentence that had to be removed from the README. (c) Paper 00's abstract claims the architecture can "spontaneously generate ... epistemic curiosity, counterfactual imagination, and prioritized empirical inquiry"; the **forms** exist (G5–G8) but the **efficacy** does not — Phase K's matched ablations came back empty (`NO_QUESTIONS` −0.0095 [−0.0328, +0.0140]; `NO_FALSIFICATION` +0.0241 [−0.0048, +0.0495]; `NO_DREAMS` +0.0000 [0.0000, +0.0000], **all three intervals containing zero**), and **Law IV is never exercised** — experiments are generated, every consumer only prints them, and **no Question can ever close**. (d) Paper 05's *"strict partition ensures zero synthetic self-contamination across indefinite life cycles"* is contradicted: **17.9%** of the distinct supporting transitions behind reported beliefs (802 of 4,481) are self-sourced, and **43.2%** of all distinct transitions recorded are the organism's own output, entering the temporal substrate through the unfiltered lookback (D2). | **A position paper is audited against the code, not against the prose.** The two documents most likely to be circulated are the two least checked against the engine, because neither is a measurement record and so neither is covered by the harness. Paper 00's remaining broad claims and its literature framing are **still unaudited**; Paper 05 may need a **new thesis** (the limits of cognitive isolation) rather than a revision. | `papers/00_intelligence_through_structural_descent.md`; `papers/05_cognitive_isolation_principle.md`; `docs/architecture.md`; `docs/AUDIT-TRACE-SPEC.md` §7 (D3); manual finding 31; journal §57
**AD4** | **The historical record was normalized to American English, with the change proven to be spelling-only rather than promised to be.** **234 words across 25 files**, including `docs/ABLATION-PREREGISTRATION.md`, `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`, `docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`, `docs/WORLD-SCALE-PREREGISTRATION.md`, `docs/AUDIT-TRACE-SPEC.md`, the measurement records and the frozen journal sections. Three independent proofs were run against `HEAD` for every changed file: **(1) non-target content byte-identical** (every British-or-American target word replaced by the same token, so only non-target bytes and token positions are compared); **(2) the sequence of numeric literals identical** (no number changed, moved, appeared or disappeared); **(3) structure identical** (same count of headings, table rows, list items and lines). All three pass on all 23 changed files. Inline code spans were never rewritten, so no identifier, path, tag, test name or constant was touched. | **A verifier that reuses the writer's parser inherits the writer's bug.** The first pass reported *"remaining: 0"* and was wrong by 88 occurrences, because the sweep and its check shared a document-wide code-span regex that mis-aligns when backticks are unbalanced across a line, so prose was skipped and then not counted. It surfaced only because a **second, differently implemented** check — a raw-text scan with no span logic — disagreed with the first. **A check that cannot disagree with its own writer is not a check.** | `git diff HEAD` (23 files); manual finding 32; journal §58
**AD5** | **Paper 00's audit was completed against the code: two of the six architectural laws are contradicted by the implementation, one is untested on its own terms, one is contradicted in direction.** **Law III (Cognitive Isolation) is violated in exactly the way it was written to prevent** — the design law requires that *"temporal precedes matrices are strictly computed on non-sleep events"*, and `memory.py` gates the **trigger** on `event_type != "sleep"` but not the **lookback window**, so sleep output re-enters `precedes` at **201×–341×** the world's own event count (D2). **Law V (EIG Attention) is wrong twice over**: formally the engine applies `uncertainty * (1.0 + novelty)` to questions and `uncertainty * novelty` to dreams, so the law's single expression is not what it computes for half its cases; empirically the pre-registered prediction that development is EIG-orthogonal came back **REVERSED** — selecting the *lowest*-EIG experiment develops **more** than the highest-EIG one. **Law IV (Grounded Dreaming) is mixed**: the confidence baseline **holds** (dreams are created at **0.04–0.06**, matching the design law), but the operative clause — a dream becomes a belief only if an external experiment generates the confirming events — is **never exercised**, because the engine generates experiments and never executes them, so no question can ever close. **Law VI** holds (thresholds **0.3** / **0.15**); **Law I** was not separately audited. Also corrected: the abstract's *"unbroken lineage to the raw experience"* is false (D3); *"causal predictions"* overstates the engine's own words, since `memory.py` calls the temporal edges *"the organism's first approximation of causality"*; and the reference list's *"Associated pre-prints"* label was false (seven manuscript files, **zero published**) with titles that were the old names. **D4 (new, disclosed defect):** the engine's stored `generation` field agrees with `docs/architecture.md` for **G1** but is **one lower for every primitive from G2 upward** (meta-concepts and processes `generation = 1`, workflows `2`, hypotheses `3`, theories and questions `4`, dreams `5`, investigations `6`, experiments `7`), and no document states the field's mapping — an undocumented offset, not a violated claim. The audit-trace specification is frozen at `audit-trace-v1` and was **not** edited to carry D4. | **A constitution that has never been audited against its implementation is a description of an unimplemented architecture.** Every one of these was found by *writing the auditor*, not by arguing — which is the strongest evidence this program has produced for its own thesis, and would have been invisible to any review that read the laws and the code side by side without measuring the code's behavior. **A law that cannot be violated is not a law; a law that has never been tested is not yet a claim.** | `papers/00_intelligence_through_structural_descent.md` §3.1; `docs/DESIGN_LAWS.md`; `docs/AUDIT-TRACE-SPEC.md` §7; `docs/architecture.md`; `organica/memory.py` `_record_temporal_edges`; `organica/sleep.py` `_rank_investigations`; `docs/verdicts.json`; manual finding 33; journal §59
**AD6** | **A hand-transcribed table had drifted from its artifact in 18 of its 36 values, and the first repair was defective in a way only a mechanical check could catch.** The Pilot-0 score matrix in `docs/PILOT-0-INSTRUMENTATION-AUDIT.md` §2 declared `docs/acquisition_single_seed_pilot.json` as its artifact, but **18 of its 36 values disagreed with it** in the fourth and fifth decimal of log-loss (largest gap **6.7×10⁻⁵**); the artifact was identical in both commits that carried it (`89b0744`, `4ceeab4`), so the drift was in the transcription. Six of the drifted values had been inherited by `papers/01_developmental_structure_formation.md` §4.7, and six more each by the five-row summaries in `docs/ACQUISITION-ENDPOINT-AUDIT.md`, `docs/ORGANICA-V2-DESIGN-BRIEF.md`, `docs/FACTS-SHEET.md` (AC7), `research-journal/phase_g_findings_20261021.md` and `research-journal/_journal_entry_51.md`. **No conclusion changed** — Organica's readout still loses to both baselines, the E-rem floor is still **0.403045**, the acquisition gate still fails and transfer is still *not measurable*. The first repair, written by hand, **replaced the two reference rows with duplicate copies of cells 7 and 8**; it was caught only by running the table against the artifact, and the table is now regenerated from it. | **A table transcribed from an artifact is a new claim and needs a mechanical check against that artifact — and a repair written by hand is another hand transcription.** The check is permanent: `tests/test_readout_tables.py`. | `docs/acquisition_single_seed_pilot.json`; `docs/PILOT-0-INSTRUMENTATION-AUDIT.md` §2.1; `tests/test_readout_tables.py`
**AD7** | **Paper 02's citations were verified against primary sources, one candidate citation was dropped because it could not be read, and the manuscript figures were generated by a program that has to be able to fail.** Paper 02 now carries inline `(Author, year)` markers and a **References** section with **five** sources, each read on 2026-10-29: ACM Publications' *Artifact Review and Badging* v1.1 (the **Results Reproduced** / **Results Replicated** distinction, and the Publications Board's 2020 interchange of the two definitions); Bau, Liu, Wang, Zhu & Torralba, *Rewriting a Deep Generative Model* (ECCV 2020, oral); Elhage, Nanda, Olsson et al., *A Mathematical Framework for Transformer Circuits* (Anthropic, 2021); the W3C *PROV-DM* Recommendation (Moreau & Missier, eds., 2013); and Shumailov, Shumaylov, Zhao, Papernot, Anderson & Gal, *Nature* 631(8022):755–759 (2024) **with its 2025 Author Correction** disclosed — a notation typo, and no change to the cited empirical claim. The Elhage paper's *faithful vs sufficient* distinction was **not cited**: no readable copy could be found, so it is not claimed. Eight figures were generated for Papers 01 and 02 by the stdlib-only `benchmarks/figure_papers.py`, which **asserts every value it draws against the committed artifact**, bounds-checks its canvas, checks for text overflow, and **parses its own XML before writing**. | **Cite only what was read.** **A figure is a program that draws a claim, so it must be able to fail.** | `papers/02_persistent_structural_provenance.md` §2 and References; `benchmarks/figure_papers.py`; `docs/figure_p*.svg`
**AD8** | **The first world edge was reported without the distribution beside it, and the distribution is what the claim needed.** The rank of the first world edge — **31** in the 1-tag stimulus, **30 / 18 / 53** in the 2-tag seeds, **16 / 8 / 8** after the LIMIT-4 separation — was reported on its own, which made the ranking problem look nearly solved. Under the engine's own global count-ranked selection the world's 112 edges are **spread through the table, not clustered at its top**: the top 20 recovers **0–1** of them, the top 40 **0–2**, the top 80 **8–16**, the top 160 **36–55**, and the top **320** — about **16×** the engine's budget — **106–109** (`docs/gate13_allocation_rule.json`, 3 seeds); the five-seed capacity sweep puts cap 40 at **1–8 of 112** and the frozen cap of 20 at **0–3 of 112**. The figure *"cap 40 recovers 4–8 of 112"*, which had been quoted in correspondence, is **not** what the artifact says and has been restated from it. **No measurement changed.** | **A first edge at rank *N* is one edge arriving, not a set arriving.** A threshold, a first case and a headline statistic are all single points, and **the set is the claim**. | `docs/gate13_allocation_rule.json`; `docs/gate13_capacity_sweep.json`; `docs/gate13_relation_separation.json`; `docs/GATE13-RELATION-SEPARATION.md`; journal §62
**AD9** | **Paper 01's citations were verified against primary records, and the project's own rule was kept distinct from the literature.** §4.1's curriculum-sensitivity framing and §5.4's four methodological lessons now carry inline `(Author, year)` markers and a **References** section with **seven** sources, each read on 2026-10-30. Six of them carry a literature-grounded claim; the second lesson — compare against the strongest simple baseline and take the headroom from the ceiling — **carries no external citation by design**, because it is this project's own rule and reports only Organica 1's own numbers. An **erratum** to Button et al. (*Nature Reviews Neuroscience* 14(6):451, 2013) was read: it corrects the definition of *R* on page 366 and does not affect the abstract-level power conclusions cited here. | **"Cite only what was read" applies to the limit as well as to the citation.** Two sources — Bengio et al. (2009) and Davis & Goadrich (2006) — were reachable only as their authors' abstracts, so they are cited only for what those abstracts state, and that limit is written down instead of being left implicit. One candidate source could not be located in any bibliographic record and is therefore not cited. | `papers/01_developmental_structure_formation.md` §4.1, §5.4, References; `papers/README.md`; `research-journal/phase_g_findings_20261021.md` §63
