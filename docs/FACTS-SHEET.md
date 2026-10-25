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
| **D8c** | **The pollution was not confined to scoring — it was the denominator of a survival filter, and it was the cause of the supply limitation.** `tag_counts` is the source of `source_freq`, and `source_freq` is the denominator of the Layer-1 edge strength `ratio = count / source_freq`. The **numerator** was world-only and the **denominator** was not, so the two sides of the ratio measured different populations, and the survival filter discarded the world's own structure in favour of whatever the organism happened to say about itself. Measured consequence: a branch stimulus collapsed to **4 surviving edges** (2 of them schema tags), **0 processes, 0 workflows, 0 beliefs**. Corrected 2026-10-23 — the counter is now scoped to world events, like the graph it normalises. | `docs/freq_scope_probe.json`; journal §21 |
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
| G4 | **One organism, one run, flat.** No longitudinal data beyond 3,725 cycles, and that run stopped moving at cycle 261. | No claim about behaviour at 10⁵+ cycles is supported — and the plateau argues the current build would not differ there. |
| G5 | **Retention has never been tested under pressure** — the belief pool has never exceeded the cap in the reference configuration. | Gate **G-P1** fails: hypothesis retention pressure is 0.35, and `MAX_HYPOTHESES` is INERT (§D3). The Tier-1 "FULL vs SALIENCE" experiment as specified would measure two identical colonies. |
| G6 | **Commercial track: unresolved.** Entity, IP ownership, open-source licence position and the authorization memo all require counsel. Customer problem unvalidated (no interviews). | Tracked in `docs/GATE-BOARD.md`. |

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
| **T3** | **The verdicts are robust.** Re-running the bootstrap with 8 different seeds leaves all three verdicts unchanged. Dropping the single most favourable seed, and separately the single least favourable seed, also leaves every verdict unchanged. | journal §33 |
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

**T3** | **The verdicts are robust.** Eight different bootstrap seeds leave all three verdicts unchanged. Dropping the single most favourable seed, and separately the least favourable seed, also leaves every verdict unchanged. | journal §33

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

**V1** | **The Phase L pilot's "result" was an artefact, not a finding.** The reduced-scale execution check returned `DI = 0.000` at **all eight** points of the support-ratio sweep, with `PI = 0.611` at all eight. Read casually that is a clean negative result — *the late structure never displaces the early structure at any pressure*. It is not a result at all: **the support ratio was not varying anything.** | journal §36; preregistration Amendment 1

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
