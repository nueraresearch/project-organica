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
| **I1** | **The structure is decided on cycle 1.** Every colony reaches 18 pre-retention beliefs, 7 competing subjects and 15 retained beliefs on the first cycle and holds that configuration for 2,999 cycles. All six arms converge to the **same** attractor despite six different interventions. | `docs/force_matrix.json` → `series` |
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
