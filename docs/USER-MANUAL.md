# Project Organica — Owner's Manual

> **Audience:** Jeremy (project owner). This is the single document that tells you what the project is, what state it is in, how to run it, how to read its output, and what you personally need to decide and do.
>
> **Currency:** This manual is maintained live. Every change to the project's state, commands, findings, or your action list must be reflected here **in the same turn it happens** — see [§18 Keeping this manual current](#18-keeping-this-manual-current).

---

## Table of contents

1. [Five-minute quickstart](#1-five-minute-quickstart)
2. [Where things stand right now](#2-where-things-stand-right-now)
3. [What Organica actually is](#3-what-organica-actually-is)
4. [Running everything](#4-running-everything)
5. [Reading the output](#5-reading-the-output)
6. [What the study is measuring](#6-what-the-study-is-measuring)
7. [What you need to do](#7-what-you-need-to-do)
8. [The findings, and what each means for you](#8-the-findings-and-what-each-means-for-you)
9. [Troubleshooting](#9-troubleshooting)
10. [File map](#10-file-map)
11. [Vocabulary](#11-vocabulary)
12. [Abbreviations and acronyms](#12-abbreviations-and-acronyms)
13. [Data dictionary](#13-data-dictionary)
14. [The eight layers, in detail](#14-the-eight-layers-in-detail)
15. [The formulas, with worked examples](#15-the-formulas-with-worked-examples)
16. [Metric cheat sheet](#16-metric-cheat-sheet)
17. [Common misreadings](#17-common-misreadings)
18. [Keeping this manual current](#18-keeping-this-manual-current)

---

## 1. Five-minute quickstart

```bash
cd C:\Users\monte\anti\project-organica

# Read the latest recorded study health (read-only; daemon is paused)
python benchmarks/study_health.py

# Do not restart until a stable V1.0.0 is ready and reviewed.

# Watch it work
Get-Content organica.log -Wait -Tail 20      # PowerShell
tail -f organica.log                          # bash / git-bash
```

The one-line summary you want to see:

```
daemon              : ALIVE - PID <n> since <time>
sleep_cycle 1..N    : non-monotonic steps: 0   OK
G5 duty cycle       : 100.0%
failed cycles       : 0
```

**Full picture in 3 commands:**

| Goal | Command |
|---|---|
| Health / status | `python benchmarks/study_health.py` |
| Watch it grow from nothing | `python build.py` |
| The full Phase G findings | `research-journal/phase_g_findings_20261021.md` |
| The research write-ups | `papers/` and `research-journal/` |
| Brand new to this project? | `GETTING-STARTED.md` |

---

## 2. Where things stand right now

**As of 2026-10-26 17:40 MDT** (this section is refreshed on every manual update):

| | |
|---|---|
| Study status | **PAUSED** by owner request after continuous-run cycle 1032 / global sleep cycle 5396 at 2026-10-23 20:26 MDT. No `run_continuous.py` process is active. Do not resume until a stable V1.0.0 is ready and reviewed. Pause marker is appended to `organica.log`. |
| Build in effect | `retention=salience caps(hyp=15,pred=20,proc=10,meta=15,wf=10) contradiction_scale=1.0 markers=15 freq_scope=world` — written to the log at every startup, so the log says which configuration produced which cycles. |
| Cycles completed | **5,396** sleep cycles; the last daemon session completed 1,032 continuous-run cycles. |
| Sleep-cycle counter | 1 → 5,396, **0 non-monotonic steps**, 0 failed cycles. The counter survived the restart and substrate correction because it lives in the database, not in the process. |
| Cycle latency | median 309 ms and max 631 ms over the last 50 recorded cycles; last-200 median 297 ms |
| Substrate | Bounded by retention; mean **109 rows pruned/cycle** over the last 200 recorded cycles. |
| Tag vocabulary | **29 tags, 0 schema tags.** Before the fix it was 63 tags, 60.6% of them the organism's own JSON field names. |
| Mean population (last 200 cycles) | 13.0 hypotheses, 8.0 dreams, 1.0 theories, 1.0 questions — **exactly constant**, stdev 0.000 |
| Lineage (Law II) | 100% grounded, 0 unverifiable, 0 ungrounded |
| Archived run | `logs/organica_prefix_20261022.log` (7.97 MB) + per-cycle series in `docs/prefix_run_series.json` (3,725 cycles) |
| **Tier-1 matrix** | **COMPLETE** — 6 colonies × 3,000 cycles = 18,000 colony-cycles. Results in [`docs/FORCE-MATRIX-RESULTS.md`](FORCE-MATRIX-RESULTS.md); journal §23. |
| **V1 before/after** | **COMPLETE** — 21 reversals, and three interpretations **retracted**. `docs/v1_impact.json`; journal §22. |
| **Phase H external-validity campaign** | **COMPLETE** — ten seeds, fixed held-out curriculum, three latent-cause difficulty levels; simple baselines lead overall. Full intervals in `docs/phase_h_results.json`; journal §28. |
| **Phase I regime-shift benchmark** | **COMPLETE** — 20 shifted and 20 stationary worlds per family. Primary success rule not met: cause-mixture comparisons inconclusive; Markov and decayed controls exceeded the 10% false-alarm gate in mapping-swap (15%). Results: `docs/regime_shift_results.json`; journal §29. |
| **Phase J gradual-adaptation benchmark** | **COMPLETE** — 20 paired shifted/control seeds in each of two gradual-transition families (80 worlds total). Organica's preregistered adaptation-cost advantage and final-stable non-inferiority gates both failed in both families; Markov and decayed association had much lower NLL. Results: `docs/post_shift_adaptation_results.json`; journal §30. |
| **Phase K comparative-advantage search** | **COMPLETE — all three families REVERSED; the search failed.** Ten seeds per family, scored against the *best* simple baseline configuration out of a declared grid of 24 per seed per family. K1 (incremental world modeling) Organica 0.5923 vs baseline 0.9360; K2 (belief revision) 0.4111 vs 0.9846; K3 (longitudinal integration) 0.0000 vs 0.8578. Every 98.33% decision interval lies wholly below zero, so all three are clean losses, not ambiguous ones, and every verdict survives 8 bootstrap seeds and both leave-one-out checks. **The pre-committed terminal outcome H2 fired: three more task families are ruled out, the negative-results map grows, and no V2 is designed.** Results: [`docs/phase_k_results.md`](phase_k_results.md); journal §33; facts sheet §T. Protocol: [`docs/PHASE-K-PREREGISTRATION.md`](PHASE-K-PREREGISTRATION.md). |
| Git | The working tree is **clean**. Package version **0.11.0**, **unreleased** — the changelog heading says so, and rule 10 allows an unreleased version to have no tag. `v0.10.0` is **cut, dated, tagged and pushed** (annotated tag at the candidate-membership-audit commit); it has **no GitHub release page**, so `v0.9.0` is still the latest *published* release, and the README and `CITATION.cff` now say which kind of release they mean. `v0.9.0` remains the **archival reference for the frozen Organica 1 engine** and is never moved. **402 tests pass.** **Organica 1 is frozen** — see [§8.7](#87-organica-1-is-frozen-the-v090-tag-is-the-archival-reference). |
| Cold-start study | **complete** — see [§8.1](#81-the-cold-start-study) |
| Ablation study (V1) | **complete** — see [§8.2](#82-the-ablation-study-which-mechanisms-are-actually-doing-the-work) |
| Instrumentation audit (V1.5) | **complete** — see [§8.3](#83-the-instrumentation-audit-where-the-pressure-really-is) |
| Mechanism closure (M0.5) | **complete** — see [§8.4](#84-the-counter-that-was-measuring-the-wrong-population). The gate is validated, the launch gates are closed, and the substrate defect that caused the collapse is fixed. |
| **Audit trace (Phase M)** | **COMPLETE — A1–A7 all met, TAGGED and FROZEN at `audit-trace-v1` (2026-10-28).** A5 (field honesty) and A6 (trace/counterfactual separation) each have a proof-of-firing test that passes; the three probe arms (default, stress, forced-tie) are regenerated. **No feature may be added to the instrumentation from that tag**; it may be *fixed* if found wrong, but not *extended*. The **package version stays untagged** — the tag marks the instrumentation, not a release. Spec [`docs/AUDIT-TRACE-SPEC.md`](AUDIT-TRACE-SPEC.md); journal §41–§48, §53. |
| **Acquisition experiment** | **PRE-REGISTERED (Revision 3). THE CAMPAIGN STOPPED AT THE ACQUISITION GATE (2026-10-28).** The endpoint was audited — seven defects, all confirmed against the code — the benchmark was rebuilt as a **compositional task** whose gate passes, and the frozen engine then **failed the preregistered Gate 13 on every inspected seed**: asserted structure coverage **0.0 %–2.7 %** (0–3 of 112 edges) against **112 / 112 (100 %)** raw temporal coverage. **Transfer was not measured, and it is not a transfer failure**; the 600-cell factorial did not run. Cause: `MAX_PREDICTIONS = 20` crowding — raising only the cap to 1,000 restores **98.2 %–100 %**; and the *deepest* cause is **precision**, not capacity (finding 26). The center of the project: *can a controlled experience leave behind a structure that helps on later events, after the raw episodes are unavailable?* [`docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`](ACQUISITION-EXPERIMENT-PREREGISTRATION.md). **10 runs per seed × 30 seeds.** See [§8.19](#819-the-endpoint-audit-and-the-campaign-that-stopped-at-its-own-gate-2026-10-28) and finding 25. |
| **Reusable knowledge** | **PROTOCOL DRAFT — not committed, nothing run (2026-11-01).** Two days after the formation-vs-utilization campaign reported that both formed arms lose transfer, the next question is whether formed structure is usable on held-out events. The draft ([`docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md`](REUSABLE-KNOWLEDGE-PREREGISTRATION.md)) fixes a formation gate that can fail, forbids calling a latent-structure-granted counter "data-only", and makes capacity and ordering changes named variants. It stops at an owner decision: the `V1.1-cap` variant, or V1 frozen with the capacity limit as a finding. **No cell has run.** **Owner authorised Option A (2026-11-01); Revision 1 closes the review points; no cell has run.** **Feasibility checked generator-only (2026-11-01): the every-fourth rule disconnects the law, so the rule is now the first feasible of 28 enumerated subsets under criteria fixed beforehand — withhold `(0,0)` flip_p and `(0,1)` flip_q. No cell has run.** **Now a committed PREREGISTRATION (Revision 2, 2026-11-01)** after a seed leak and a schedule mismatch were corrected: seed `20261206` is burned as diagnostic and confirmatory seeds are `20261207–20261226` (n = 20); the check now covers warmup + acquisition as formation and tests the floor in the real 50-cycle transfer window. No cell has run. **Amendment 1 (2026-11-01): Gate F counts the 96 relations available during formation; the ceiling is the full latent-rule holder and the oracle-admitted arm is only a mechanism arm. No cell has run.** **Amendment 2 (2026-11-01): the variant is fixed at `MAX_PREDICTIONS = 1,000`; Gate F governs the calibration pass on V1.1 only and all five calibration seeds must pass; the oracle-admitted arm is deferred until its candidate-level rule is specified.** **Harness built and calibration cleared (2026-11-01): `benchmarks/reusable_knowledge.py` implements the five §10 items — the conditioned sampler (the withheld transitions are never generated, so nothing is skipped), Gate F over the 96 available relations with its precision companion, the retention and withheld-only transfer limbs, the closed-form ceiling, and the swept comparators with the cell counter kept privileged. Gate F passed on all five calibration seeds (minimum coverage 0.9792); the oracle arm is not implemented. No confirmatory seed has been run, so there is no transfer verdict of any kind.** **Guards and the attribution share fixed (2026-11-01): the calibration artifact now records its capacity, label and `PYTHONHASHSEED`, and the confirmatory guard refuses unless the cap is 1,000, the label is `V1.1-cap(1000)`, the seed set is the five calibration seeds, and Gate F, the audit and the attribution share all passed on all five; a calibration at another capacity is refused outright. The attribution share (Layer-1 edge weight over total, minimum 0.50) cleared on all five calibration seeds at 0.9848–0.9866. **Revision and provenance (2026-11-01): the revision limb and its withheld-only co-primary are implemented and scored, and a store-time support-provenance diagnostic now measures how much of the readout's evidence is the organism's own sleep payload. It fails its declared 0.25 maximum at 0.4092–0.4155 on every calibration seed, so the artifact records `authorises_confirmatory: false` and the confirmatory set stays closed: the transfer margin is **not attributable** under the protocol's own stop rule 3. **Per-claim reconciliation (2026-11-01):** the provenance measure now applies the audit-trace specification's own per-claim rule — each claim's distinct support against the frozen 17.9 % reference — instead of a run-level average. It fails on 254–576 of 604–1277 measurable claims per seed (maximum share 1.0000; an earlier count on a collapsed transition unit is withdrawn — journal §98), so `authorises_confirmatory` stays false and the confirmatory set remains closed; the run-level share is reported as a diagnostic only.** **Provenance diagnostic (2026-11-02):** the tracer was pointed at the five already-used calibration seeds only, under a plan frozen at commit `c5b4d49e` before the run ([`docs/PROVENANCE-ANALYSIS-PLAN.md`](PROVENANCE-ANALYSIS-PLAN.md); results [`docs/PROVENANCE-DIAGNOSTIC.md`](PROVENANCE-DIAGNOSTIC.md)). The claim type the study scores is stored without parent links — all 1581 formation and 1596 revision `prediction_candidate` structures resolve zero ancestors — while the 63 formation and 57 revision `hypothesis` structures carry seven-ancestor chains, 14 / 13 of them complete `world_rooted` (39 / 41 with a cyclic branch, 23 / 9 with a pruned parent, none cut by the depth cap). No `self_only`, no `mixed`, no threshold and no verdict; vocabulary overlap is not observation-level provenance, and the study stays closed. **Correction (same day):** those are **unique structure ids**, while the study's per-claim rule counts **raw snapshot rows** — a survivor is re-stored every cycle — so 1313 formation claim rows for seed 20261201 are not 329 structures. The tracer now reports raw rows, unique ids and unique asserted edges, reconciles its raw-row count against `_claim_edges`, and the claim that the traced population *is* the study's claim population is withdrawn. |
| **Formation vs. utilization** | **COMPLETE (2026-10-30) — the pre-committed verdict is "utilization fails with correct structure" on both tasks; summary claim NOT SUPPORTED.** 30 seeds × 2 tasks, 60/60 units `campaign_ready`, four arms, all eight audits pass or are not applicable. **C — cap 1,000 with the generator's support admitted at Layer 1, reading arm B's per-cycle temporal graph (Amendment 1) — loses transfer on both tasks** (d = bar − arm: T1 **−0.0262** [−0.0275, −0.0249]; T2 **−0.0227** [−0.0242, −0.0211]) and **loses retention** (T1 −0.0267; T2 −0.0230). It **wins revision on T1** (d = **+0.1002** [+0.0956, +0.1047]) and **ties it on T2** (d = +0.0007 [−0.0012, +0.0026]). C closes **65.2 %** of arm A's transfer gap on T1 and **79.9 %** on T2, so the label means *does not clear the bar*, not *no use*. **B also loses transfer on both tasks** (T1 −0.0296; T2 −0.0795), so §7's "both lose" cell fires: **V2 targets the use path (retrieval / activation / readout)**, and the report names transfer and retention. **The T2 bar is the cell-level latent-state counter, which is granted the latent cell structure — it is not a data-only learner**, and C still loses to Replay by 0.0208 and the bigram by 0.0187 on T2, so the verdict does not depend on that oracle. **No V2 build is authorised.** [`docs/formation_utilization_results.md`](formation_utilization_results.md); protocol §7 and §12; [§8.21](#821-the-formation-vs-utilization-campaign-the-verdict-and-what-it-does-and-does-not-mean-2026-10-30). **The diagnostic ran on 2026-10-30 and returned AUDIT REQUIRED** — D0 failed on 18 of 180 seed-limbs (largest 0.004386) while every other control passed, so no room, no variant effect and no component are reported. **The reproduction audit ran on 2026-10-30 and did not support the tie-order hypothesis** — both read orders are repeatable 8/8 and identical 8/8, and neither reproduces the campaign's per-type table — so D0 remains fired and no V2 build follows. **The next test is a hash-seed sensitivity sweep ([§8.22](#822-the-use-path-diagnostic-the-step-to-v2-authorization-2026-10-30)), not a V2 design.** |
| **Owner's standing decisions (2026-10-26)** | V2 **not cut**; live study **not restarted**; **V2–V5 not run**; no further open-ended audit work. Sequence: finish the audit build → freeze it → run the acquisition experiment → compare against the replay learner → publish whatever happens → only then discuss V2. **Added 2026-10-30:** Law II stays disclosed and its amendment is deferred, pending whether the law is a design requirement or a description of V1's actual behavior. |
| **Five claims narrowed (2026-10-26)** | The project's own summary was reviewed and five headlines were wider than the checks behind them: *"revision exists"* → **structural displacement**; the **3:1** transition → robust **within this engine, world family and support-ratio axis**; *"path-dependent"* → **schedule dependence**, strict order dependence untested; *transfer* → **no positive transfer demonstrated, measured cross-domain result negative**; *"independently auditable"* → **independently reconstructed, not replicated by another lab**. No measurement, verdict or criterion changed. See [§8.18](#818-the-five-claims-narrowed-2026-10-26) and finding 24. |
| Facts sheet | `docs/FACTS-SHEET.md` — every claim with its provenance |
| Gate board | `docs/GATE-BOARD.md` — what is demonstrated, what is assumed, what is blocked |

**The third headline, and it changed the plan again on 2026-10-23: the matrix ran, and what it measured was not what it was named.** Six colonies, 3,000 cycles each, and **every arm reaches its complete structural configuration on cycle 1** — 18 pre-retention beliefs, 7 competing subjects, 15 retained beliefs — and essentially holds it for 2,999 cycles while mean support grows **+10,776%**. Structure flat, evidence growing by three orders of magnitude. *(Corrected 2026-10-24, journal §31: the retained belief count is exactly 15 in every cycle of every colony, but the pre-retention pool is the *modal* configuration rather than a constant one — 98.1–99.5% of cycles for five arms, 75.9% for `NO_QUESTIONS`, whose excursions run as late as cycle 2,738. No launch gate is affected.)*

**And the reason is environmental, not architectural: the stimulus repeats every 9 cycles.** `lattice_L1` is 9 distinct events over 7 distinct words; the organism sees the same world 333 times. Every colony discovered **zero** new items in its final 100 cycles, and the whole inventory is 74 items. **M5 ("development velocity") was not a velocity** — it was a finite inventory divided by the run length, which is why it read 24.667 over 300 cycles and 2.467 over 3,000 while the underlying count stayed at 74.

The five pre-registered predictions came back **2 SUPPORTED and 3 REVERSED** — removing contradiction or question creation *raises* development velocity, and selecting the lowest-EIG experiment develops *more* than selecting the highest-EIG one. The verdicts are direction-aware; a naive "did it move?" test would have reported five confirmations.

**H24 has been tested with the world-scale ladder and burst curriculum.** Uniform variety reduced inventory, while scaffolded and reinforced novelty raised it from 91 to 113 at 300 cycles and 119 at 600. The exploratory 1,200-cycle extension reached 128 (against a 91-item core baseline), with 2 new items in its final 100 cycles. This supports curriculum-dependent structure formation, but does not establish ongoing expansion. Phase H then tested external usefulness: Markov beat Organica on the single fixed prediction stream, and same-event co-occurrence beat it on latent pair recovery in all three conditions. Details and uncertainty intervals are in `docs/phase_h_results.json` and journal §28.

**Phase H's ten-seed usefulness campaign favors simple baselines on the tested tasks.** Markov F1 was 0.504 vs Organica 0.413, but all ten prediction runs used the same deterministic stream and produced identical scores; those intervals do not measure input-world uncertainty. In structure recovery, same-event co-occurrence led Organica across clean, overlapping, and stress worlds (F1 0.800, 0.764, 0.796 vs 0.704, 0.547, 0.109). Organica beat the temporal graph only in clean and overlapping conditions; its relative recovery position declined as difficulty increased. See [facts §P](FACTS-SHEET.md), [Phase H protocol](PHASE-H-PREREGISTRATION.md), result artifact, and journal §§26–28.

**The headline, and it changed the plan:** the 90-day run **plateaued at cycle 261 — 7% of the way in.** Every population series has standard deviation **0.000000** and slope **0.0 per 1,000 cycles** over the last 931 cycles. The organism reached a fixed point and then sat still for 3,464 cycles. A single arm with a flat line describes nothing and identifies nothing; **only contrasts can.** The comparative matrix replaces the 90-day single arm as the primary experiment, and the daemon becomes a *monitor*, not a gate.

**The second headline, and it changed again on 2026-10-23:** the Tier-1 experiment as originally specified — *Full vs Salience retention* — **would have measured nothing**, because the Layer-4 belief pool reached a maximum of **8** against a cap of **15** and the cap bound in **0 of 600** cold cycles. Two things have changed since that was written:

1. **The belief pool was being starved by a measurement defect**, not by the world. The tag-frequency counter was scoped to *all* events while the graph it normalises was scoped to *world* events. Fixed. See [§8.4](#84-the-counter-that-was-measuring-the-wrong-population).
2. **On the study stream the pool is still short** — 5.17 beliefs mean, 6 max, against a cap of 15 — so the retention policy is still inert *there*. **On the branch-structured stimulus it is not**: the pool reaches **18**, the cap binds, and alphabetical and salience retention produce **different** populations (5 theories / 5 questions vs 4 / 4). The comparison is finally measurable.

**Where the pressure actually is:** at Layer 1, not Layer 4. The organism generates **936 loops, 621 predictions and 309 anomalies** and keeps 15, 20 and 10 of them — retention pressure of **61×, 30× and 29×** — while Layer 4 received **5–8 beliefs for 15 slots** (pressure **0.35**) on the study stream. **The organism was starved, not selective** — and it was starved by its own instrumentation. Read [§8.3](#83-the-instrumentation-audit-where-the-pressure-really-is) and [§8.4](#84-the-counter-that-was-measuring-the-wrong-population) before you run anything else.

**The long-horizon answer has been re-measured, and part of it changed.** The cold-start ablation is done. On the frozen engine the organism bootstraps G1, G4, G6, G7 and G8 from an unengineered stream with no assistance, and G2 processes and G3 workflows follow at cycle 14 — but **G5 never appears on that stimulus**. It *does* appear, unseeded, at cycle 10 in `cold_start`, which uses the engineered stream; the 2026-10-21 table said it never did there, and that row no longer reproduces. The correction is stated in [§8.1](#81-the-cold-start-study).

**The unflattering answer is unchanged:** the ablation study says most of the architecture's layers are not load-bearing. Sleep and the substrate graph are foundational. **Lineage changes nothing at all except auditability.** The attention economy changes what it selects without changing what the organism achieves. Read [§8.2](#82-the-ablation-study-which-mechanisms-are-actually-doing-the-work).

> **Read the status table this way:** `sleep_cycle` monotonic and `failed cycles` at 0 mean the *machinery* is sound. A population that is *exactly* constant means the *experiment* has converged — a run can be perfectly healthy and still be measuring nothing (see [§17](#17-common-misreadings)).

---

## 3. What Organica actually is

**One paragraph:** Organica is a program that tries to grow a mind instead of loading one. It ingests a raw event stream (timestamps and text, no schema), builds a graph of which tags co-occur and which tend to follow which, and then repeatedly "sleeps" — a cycle that reads the graph, proposes higher-order structures, tests them against the evidence, and lets the ones that don't hold up decay and die.

The important claim is not that it works well. It's that **every structure it holds must trace back to raw experience through unbroken parent links** (Law II), and that it **never hard-codes a cognitive concept** (Law I) — concepts, loops, workflows, hypotheses, theories, questions, dreams, investigations and experiments are all supposed to emerge from the layer below.

**The developmental ladder** (from `CHALLENGE.md` and `docs/developmental-ladder.md`):

```
[Gen 0] Events (Experience Stream)
  ↓
[Gen 1] Concepts, Predictions & Loops
  ↓
[Gen 2] Process Candidates & Meta-Concepts
  ↓
[Gen 3] Workflow Concepts
  ↓
[Gen 4] Hypothesis Candidates          (falsifiable A → B)
  ↓
[Gen 5] Theory & Question Candidates   ← epistemic tension, Shannon entropy
  ↓
[Gen 6] Categorized Dreams             (completion, analogy, mutation, conditional)
  ↓
[Gen 7] Investigation Candidates        (ranked by Expected Information Gain)
  ↓
[Gen 8] Experiments                    (concrete, executable interventions)
  ↓
[Gen 9] Self-Modeling                  ← LOCKED until the study concludes
```

**The six design laws** (`docs/DESIGN_LAWS.md`) are the constitution. The three that matter most for reading the data:

- **Law I — Strict upward layer induction.** Layer N+1 only ever operates on Layer N's output.
- **Law II — 100% verified structural provenance.** Everything traces to Generation 0. *Verified — see [§8, finding 8](#8-the-findings-and-what-each-means-for-you).*
- **Law V — Epistemic attention (EIG over confidence).** The organism spends effort where *uncertainty* is, not where it's already certain. `EIG = Uncertainty × (1 + Novelty)`.

**Generation 9 is deliberately locked.** The study is paused; V1.0.0 stability and review are prerequisites before deciding whether to resume it or reopen the architecture.

---

## 4. Running everything

Everything lives in `C:\Users\monte\anti\project-organica`. Open a PowerShell there.

### 4.1 The study daemon

```bat
start_organica.bat
```

Launches `run_continuous.py` in the background. It writes one JSON summary line per cycle to `organica.log` and never truncates it. The cycle interval is 30 seconds (override with a file named `INTERVAL` containing a number of seconds).

**Current state: paused.** The daemon stopped after cycle 1032 (global sleep
cycle 5396) on 2026-10-23, pending a stable V1.0.0. The temporary `INTERVAL`
override was removed. Do not launch `start_organica.bat` or
`run_continuous.py` until the V1.0.0 build and resumption decision are
reviewed. The database and append-only log are preserved.

| Behavior | Detail |
|---|---|
| Log | `organica.log` — **appended**, never truncated |
| Console mirror | `console.log` |
| Database | `memory.db` (SQLite) |
| Working memory | newest 4,000 sleep events |
| Candidate retention | newest 20,000 (bounded; older ones evicted) |
| Stop | Stop only after the latest cycle is logged, then record the pause; see [§9](#9-troubleshooting). |

### 4.2 Making it survive 90 days ⚠️

**This section is deferred while the study is paused.** Do not configure an
auto-restarting supervisor until the V1.0.0 build is reviewed and the owner
decides to resume collection. Otherwise a scheduled task could undo the pause.

A Windows Scheduled Task fixes it: it survives console close and logoff, and restarts the daemon if it exits.

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

Stop and remove it later:

```powershell
Stop-ScheduledTask -TaskName 'OrganicaStudy'
Unregister-ScheduledTask -TaskName 'OrganicaStudy'
```

### 4.3 Observation snapshots

```bat
run_daily_observer.bat      :: daily snapshot + appends new events to the journal
run_weekly_monthly.bat      :: weekly aggregate + monthly genome + velocity
```

Outputs land in `snapshots/`:

| File | Contents |
|---|---|
| `snapshots/daily/daily_YYYYMMDD.json` | populations, births/deaths over the trailing 24 h, latest cycle |
| `snapshots/weekly/weekly_YYYYMMDD.json` | aggregate over the trailing 7 days, largest births/deaths |
| `snapshots/monthly/monthly_YYYYMMDD.json` | belief population + hypothesis lifecycle + dream distribution |
| `snapshots/velocity/velocity_YYYYMMDD.json` | new theories/questions/dreams/experiments per day over 7 days |
| `snapshots/event_journal.log` | append-only structural event log (theory births/deaths, hypothesis births/deaths, generation milestones) |

These are **time-window based**, not cycle based: "today" means the trailing 24 hours, "this week" means the trailing 7 days. The writers refuse to write an empty artifact — if there is no data, they write nothing and say so.

**Set these on a schedule too.** The same Scheduled Task pattern works; run them hourly or daily and the study will accumulate a real longitudinal record without you remembering.

### 4.4 Dashboards and API

```bat
run_dashboard_and_api.bat
```

- **Inception API** — `inception_api.py`, exposes health metrics and accepts injected payloads at `/inception`. The Streamlit UI uses it to inject seed events (Auth Failure, Contradictory Belief, Dream Trigger, or a custom JSON payload).
- **Streamlit UI** — `dashboard_ui.py`, the live health dashboard.
- `dashboard.py` is the older CLI dashboard; `study_health.py` is the current command-line health tool and is what to trust.

### 4.5 Audits and analyses

| Tool | What it answers |
|---|---|
| `python benchmarks/study_health.py` | Is it alive? Is the counter monotonic? Latency? G5 duty cycle? |
| `python benchmarks/g5_gap_diagnostic.py --cycles 10` | Can this stream reach Generation 5, and what is the ceiling on theories? |
| `python benchmarks/lineage_audit.py` | Does every candidate actually resolve to a Generation 0 experience event? (Law II) |
| `python benchmarks/substrate_probe.py` | What does the substrate cost per cycle, and is the database bounded? |
| `python benchmarks/stream_sweep.py` | Scores candidate event streams on G5 sustainment and EIG |
| `$env:PYTHONHASHSEED='0'; python benchmarks/heldout_prediction.py` | Freezes after 200 cycles and compares Organica G1, a tag-level Markov baseline and a recency-decayed temporal baseline on cycles 201–300; writes `docs/heldout_prediction.json`. Pilot only; one seed. |
| `python benchmarks/cold_start.py --cycles 40` | **Would the organism bootstrap later generations with no help?** Ablates pre-seeding, the engineered branch point, the lookback window and the hypothesis cap. |
| PowerShell: `$env:PYTHONHASHSEED='0'; python benchmarks/ground_truth_recovery.py` | Recovers known same-cause feature pairs from 200 training cycles and scores Organica and graph baselines; writes `docs/ground_truth_recovery.json`. Pilot only; one seed. |
| PowerShell: `$env:PYTHONHASHSEED='0'; python benchmarks/phase_h_campaign.py --seeds 10` | Runs the preregistered ten-seed prediction and clean/overlap/stress structure-recovery league; writes `docs/phase_h_results.json` with per-seed scores and bootstrap intervals. Default three workers. |
| PowerShell: `$env:PYTHONHASHSEED='0'; python benchmarks/regime_shift.py --workers 3` | Runs Phase I: 20 shifted and 20 stationary-control worlds per family; writes per-world alarms, delays, and paired summaries to `docs/regime_shift_results.json`. |
| PowerShell: `$env:PYTHONHASHSEED='0'; python benchmarks/post_shift_adaptation.py --workers 3` | Runs Phase J: 20 paired shifted/control seeds per gradual-transition family; writes per-world NLL, adaptation costs, final-stable comparisons, and settling summaries to `docs/post_shift_adaptation_results.json`. |
| PowerShell: `$env:PYTHONHASHSEED='0'; python benchmarks/phase_k_campaign.py --families K1 K2 K3 --seeds 10 --workers 3` | Runs Phase K: the comparative-advantage search over three candidate task families, each with a matched within-architecture ablation and each scored against the strongest simple baseline. **The K0 harness control and the endpoint ceiling check run first and the campaign does not run if either fails.** Writes `docs/phase_k_results.json`. Use `--control-only` for the control alone, `--self-test` for both instrument audits, and `--smoke` for a one-seed, one-tenth-scale harness check (a pilot, never a result). |
| PowerShell: `$env:PYTHONHASHSEED='0'; python benchmarks/phase_k_campaign.py --families K1 K2 K3 --seeds 10 --workers 12 --resume` | Continues a Phase K campaign that was stopped. The campaign is long enough to need more than one sitting on some machines, so it checkpoints as it goes: the results file is written **atomically** after every seed, and an append-only live recording goes to `docs/phase_k_results.ndjson`. `--resume` skips the seeds already present and rebuilds from the recording if the results file is missing. Nothing that has been computed is ever lost to a stop. |
| `python benchmarks/formation_utilization.py --timing` | **The formation-vs-utilization harness's timing pass.** Runs the pre-registered arms — cap 20, cap 1,000, and cap 1,000 with oracle admission — plus a shuffled-oracle no-leakage arm. Under **Amendment 1**, arms C and S read arm B's per-cycle temporal graph, and **A8** gates that each admission arm actually read it and built B's eligible candidate stream. All eight audits are evaluated. Writes `docs/formation_utilization_timing.json` / `.md`. **Not a result:** one exploratory seed, no win/tie/loss, no verdict. |
| `python benchmarks/formation_utilization.py --campaign --seeds 30 --workers 8` | The pre-registered campaign: 30 seeds × 2 tasks × 3 arms, plus the shuffled-oracle audit arm and the frozen comparators. Writes `docs/formation_utilization.json` / `.md`, or a **not measurable** stop that names the audit. **Run complete on 2026-10-30; the verdict is in §8.21 and the results document.** This run used a resumable wrapper over the same units. |
| PowerShell: `python benchmarks/phase_k_diagnose.py --scale 4 --seeds 5` | **Why did Organica score exactly zero on K3?** Three checks, each able to fail: a **per-cycle** check (the late structure appears in no cycle, so the zero is not an artifact of reading only the final cycle), an **under-read** check (every candidate type except `anomaly` mentions zero late tags, so no late structure was sitting unread in a type the edge extractor ignores), and a **2×2** crossing which group arrives first against which group is stronger. The 2×2 shows the late group is incorporated only when it is strictly stronger than the group that arrived first. Use `--scale 1` for the protocol's own scale (slower). |
| `python benchmarks/ablation_study.py --cycles 300` | **Which parts of the architecture are actually load-bearing?** Ten ablations plus a full-system reference, scored forward-looking. |
| `python benchmarks/ablation_verify.py --cycles 300` | **Did each ablation actually change the organism?** Perturbation census, Random-Curiosity overlap and score distribution, contradiction provenance. Run this *before* reading any outcome. |
| `python benchmarks/clone_check.py` | Clones the public repo into a temp directory and checks a stranger can run it: import, tests, `build.py`, all 9 examples, and that the live study is untouched. |
| `python benchmarks/development_probe.py --cycles 600` | **Is the machinery sound, and is the run still moving?** Cap-binding census, budget-insensitivity check, plateau analysis of the archived run, vocabulary audit. Writes `docs/development_probe.json`. |
| `python benchmarks/instrumentation_audit.py --cycles 400` | **Is the observation channel saturated?** Pre-truncation candidate pools and retention pressure per layer, a 14-parameter influence map, and effective world size. Writes `docs/instrumentation_audit.json`. |
| `python benchmarks/archive_run.py --log organica.log` | Snapshots the daemon log into a per-cycle series (`docs/prefix_run_series.json`), re-deriving contradiction totals from the hypothesis snapshot. |
| `python benchmarks/benchmark_suite.py` | BM1–BM5 growth benchmarks |
| `python benchmarks/cross_domain_validation.py` | Phase F: the four reproduction domains, writes `docs/validation_report.json` |
| `python -m pytest tests -q` | The test suite (250 tests) |

### 4.6 The four reproduction domains

```bash
python examples/domains/01_developer_workflow.py
python examples/domains/02_bug_tracking.py
python examples/domains/03_synthetic_ecology.py
python examples/domains/04_robot_simulation.py
```

Each runs a short, self-contained emergence demo in its own world, in about a second.

### 4.7 Building an organism from nothing

```bash
python build.py
```

**This is the one command you give a stranger.** It creates an empty substrate, feeds it the study stream, runs the sleep cycles, and prints the full developmental ladder, the Law II integrity check, and whether Law V's attention economy ever engaged. It writes only to `.scratch/` — your live `memory.db` is never touched.

```
python build.py --all              # every domain, not just the study stream
python build.py --domain robot_simulation
python build.py --cycles 25        # longer run (default 12)
python build.py --keep             # keep the scratch DB for inspection
```

Verified output on the current build: 48 events in, ladder reaching **G8**, **100% lineage**, **G5 reached**, uncertainty **1.000**, top priority **1.500**.

`GETTING-STARTED.md` is the stranger-facing version of the same thing, and `README.md` links to it.

---

## 5. Reading the output

### 5.1 The log line

Every cycle appends one line to `organica.log`:

```
2026-10-21 11:31:00,123 INFO Cycle 42: {"cycle": 42, "sleep_cycle": 285, "timestamp": "2026-10-21T17:31:00Z", "status": "success", ...}
```

**Every daemon start also writes a build marker** immediately before the
first cycle:

```
2026-10-23 06:28:26,882 INFO BUILD retention=salience caps(hyp=15,pred=20,proc=10,meta=15,wf=10) contradiction_scale=1.0 markers=15
```

The log is append-only and can span several builds, so without this marker
there is no way to tell which configuration produced which cycles. It was
added on 2026-10-23, when the run was stopped for the retention change and
a reader would otherwise have had no way to see where the old build ended.

| Field | Meaning | Watch for |
|---|---|---|
| `cycle` | counter **since the last daemon start** | resets to 0 on restart — *not* the global counter |
| `sleep_cycle` | **global** counter, survives restarts | must increase by 1 every line; a reset means the counter bug is back |
| `timestamp` | UTC wall clock of the cycle | the anchor for every time-window metric |
| `status` | `success` or `failed` | anything other than `success` is an error |
| `duration_ms` | wall time of the sleep cycle | should be ~150–300 ms; drift upward = substrate degrading |
| `consecutive_errors` | error streak | should stay 0 |
| `concepts` `predictions` `loops` | Gen 1 populations | |
| `hypotheses` | Gen 4 population | 13–15 in a healthy run |
| `hypothesis_snapshot` | per-hypothesis `id`, `subject`, `confidence`, `support_count`, `contradiction_count` | the raw material for every belief-revision metric |
| `theories` `questions` | Gen 5 populations | **0 here means the study is invalid** — see finding 1 |
| `dreams` `dream_categories` | Gen 6 | `conditional` dreams only appear when there are uncertain Questions — a good sign |
| `investigations` `experiments` | Gen 7 / Gen 8 | |
| `composites_created` `total_composites` | cumulative structure count | |
| `candidates_strengthened` `candidates_pruned` | Law VI selection pressure | `pruned` ≫ `strengthened` is normal |
| `substrate_rows_pruned` | rows evicted by retention | should be a steady non-zero number, not zero |

### 5.2 The headline metric: G5 duty cycle

**Do not read "theories > 0" as a per-cycle yes/no.** The organism oscillates between a G4 fixed point and a G5 state, so the right metric is a **duty cycle over a rolling window**:

```
G5 duty cycle = fraction of the last 200 cycles that carried at least one Theory
```

`study_health.py` prints it. Current value: **100.0%**.

> **Why this matters:** in the first (invalid) run the same metric read ~0%. A number that reads 0% and a number that reads 100% look similar in a snapshot — one is a dead study, the other is a healthy one. Always report the window, not a single cycle.

### 5.3 The snapshots

`snapshots/daily/*.json` is the artifact to look at when you want "how is the organism doing today":

```json
{
  "cycle": 285, "timestamp": "2026-10-21T17:31:00Z",
  "active_concepts": 2, "active_hypotheses": 13, "active_theories": 1, ...
  "births_today": 963, "deaths_today": 919,
  "window_hours": 24.0, "cycles_in_window": 200
}
```

`snapshots/event_journal.log` is the narrative record — one JSON object per structural event:

```json
{"event": "theory_birth", "cycle": 285, "timestamp": "...", "subject": "developer"}
{"event": "hypothesis_death", "cycle": 284, "timestamp": "...", "id": "hyp_..."}
{"event": "generation_milestone", "cycle": 12, "generation": "questions"}
```

It is idempotent — running the observer twice appends nothing the second time.

### 5.4 The lineage audit

```bash
python benchmarks/lineage_audit.py
```

Reports how many candidates resolve to an actual Generation 0 experience event, and separates the two ways a chain can fail:

- **GROUNDED** — the chain resolves to a Layer 1 anchor whose tags appear in a real experience event. This is the only good outcome.
- **UNVERIFIABLE** — the chain was broken because an intermediate candidate was *evicted* by bounded retention. Not a lineage failure, but not provable either.
- **UNGROUNDED** — the chain resolves, but the Layer 1 anchor's tags appear in no experience event. This is a genuine violation.

Current: **100% grounded, 0 unverifiable, 0 ungrounded.**

---

## 6. What the study is measuring

### 6.1 The nine emergence targets

`CHALLENGE.md` defines success as all nine emerging **without hand-coded domain knowledge**:

| | Target | How you see it in the data |
|---|---|---|
| G0 | Pure experience | raw events in the DB, no schema assumed |
| G1 | Signal extraction | `concepts`, `predictions`, `loops` > 0 |
| G2 | Composites | meta-concepts and 2–3 cycle processes |
| G3 | Workflows | multi-anchor sequences |
| G4 | Falsifiable hypotheses | `hypotheses` > 0, with support/contradiction counters |
| G5 | Epistemic tension | `theories` > 0 **and** `questions` > 0, with non-zero uncertainty |
| G6 | Grounded dreams | `dreams` > 0, including `conditional` dreams |
| G7 | Attention economy | `investigations` > 0, ranked by EIG |
| G8 | Active experiments | `experiments` > 0 with a real priority spread |

Plus the **integrity constraint**: 100% of candidate nodes resolve their parental ancestry back to Generation 0.

### 6.2 What G5 means, precisely

G5 is the pivot of the whole architecture. Layer 5 coalesces **two hypotheses about the same subject with competing expectations** into a Theory, and scores the Shannon entropy of that split as the Question's uncertainty.

That means G5 requires the organism to hold *two contradictory beliefs about one thing*. Concretely, in the current study stream, "developer executed test suite" is followed sometimes by a failures report and sometimes by a passed report — so "developer" carries two expectations, and the organism must notice.

**G5 is where the EIG economy gets its fuel.** Zero contradictions → zero entropy → zero EIG → the attention economy is dead even though the counters all look "fine". This is the single most important thing to understand about the telemetry: *a run can look healthy and be epistematically inert.*

### 6.3 What the study deliberately does not yet do

- **It does not execute experiments.** G8 produces *candidates*; nothing runs a probe against the world and measures whether a belief moved. So a Question can never actually close — the study measures **epistemic tension**, not **epistemic resolution**. (Finding 9.)
- **It does not use Generation 9.** Self-modeling is locked until the study concludes.
- **It does not yet touch a real external world.** The stream is synthetic and fixed, so it measures development, not usefulness.

### 6.4 Rules for a clean run

**A "run" is one constant engine plus one constant stimulus.** That is the whole definition, and it decides every question about whether a change ruins the experiment.

| Change | Ruins the run? | Why |
|---|---|---|
| `organica/sleep.py` — any change to the cognitive pipeline | **YES** | The organism's behavior changes mid-history. Archive and start fresh. |
| `organica/memory.py` — a change to substrate *semantics* | **YES** | Same: the substrate is part of the organism. |
| `organica/memory.py` — a **performance-only** change proven behavior-preserving | **No** | If a test proves the result is identical, the organism cannot tell. (This is why `tests/test_substrate_equivalence.py` exists.) |
| The event stream in `organica/streams.py` | **YES** | A different stimulus is a different experiment. |
| `run_continuous.py` log fields, `metrics.py`, `observation/`, `dashboard*`, `inception_api.py` | **No** | Measurement and presentation only. The daemon does not import them. |
| `benchmarks/`, `examples/`, `docs/`, `papers/`, this manual, LICENSE, CI | **No** | No effect on the running organism. |
| **Pausing** the daemon (stop it, leave the DB and log, start it later) | **No** | The counter is monotonic and the log appends, so a pause is a gap in wall-clock time, not a corruption. *Record the gap* — the organism did not experience the missing time. |
| **Restarting** the daemon after a crash or reboot | **No** | The counter and log survive restarts. This is exactly what the Scheduled Task's restart-on-failure relies on. |
| Running an **example script** | **No** — and now impossible | Examples write to `.scratch/`. They used to open `Path("memory.db")` in the working directory, which would have deleted the live study's substrate. |

**The three questions, answered directly:**

1. *"Do we need a fresh start every time?"* — **No.** You run for 90 days without restarting. A fresh start is needed only when the engine or the stream changes, and then the old run is archived, not erased.
2. *"Can we pause and change the programs?"* — **Yes, with one line.** Tooling, docs, dashboards, analysis, and the UI can change freely. The engine and the stream are frozen for the duration of the run.
3. *"Does a pause ruin it?"* — **No.** It leaves a gap in the time series. Note the gap in the report; that is all.

**Auditability.** To prove a run was clean, check the engine's modification time against the daemon's start time, and check that `sleep_cycle` is contiguous. Both are cheap:

```powershell
Get-Item organica\memory.py, organica\sleep.py | Select-Object Name, LastWriteTime
Get-CimInstance Win32_Process -Filter "Name like '%python%'" |
  Where-Object { $_.CommandLine -match 'run_continuous' } |
  Select-Object ProcessId, CreationDate
python benchmarks/study_health.py
```

**Current run's audit record (2026-10-21):**

| Check | Result |
|---|---|
| `organica/memory.py` last modified | 10-20 10:00:45 — before the run started |
| `organica/sleep.py` last modified | 10-20 10:01:10 — before the run started |
| Stream the daemon is running | byte-identical to `organica/streams.py` (verified against the live DB) |
| Writers to `memory.db` | only the daemon (`seed:bootstrap`, `cycle:N`) — no analysis tool, example, or API call ever wrote to it |
| `sleep_cycles` table | 921 rows, contiguous 1–921, no gaps |
| Log | 921 records, `sleep_cycle` strictly increasing, 0 gaps, 0 failures |

**Two caveats, stated plainly.**

**Caveat 1 — the first ~264 cycles ran on the pre-optimization build**, before transaction batching and candidate retention were added. Neither changes cognition — batching writes the same rows in the same order, and retention keeps a window 5× larger than the organism's 4,000-event working memory, so the working set is identical either way (proven by `test_prune_keeps_working_memory_intact`). But a paper should not have to argue that, so the recommendation is a **clean restart on the final build**. It costs about an hour of data and removes the argument entirely. **This is decision #4 in [§7.2](#72-decide-this-week) and it is still yours to make.**

**Caveat 2 — the cognitive freeze has now been tested, not just asserted.** The cold-start ablation ([§8.1](#81-the-cold-start-study)) ran the *unchanged* engine against eight different assistance levels and confirmed that the engine is still the engine. That matters for provenance: the cognitive code has not been touched since the run began, and the substrate changes were proven behavior-preserving by test, so the run is a legitimate experiment against the current engine — you are not comparing two engines, you are comparing one engine against two substrates with identical behavior.

---

## 7. What you need to do

Ordered by how much they cost you if you skip them.

### 7.1 Do today

| # | Action | Why | Effort |
|---|---|---|---|
| 1 | **After V1.0.0 review: decide whether to resume the study** | Owner decision recorded 2026-10-23: pause collection until a stable V1.0.0 exists; preserve the current database and log. | Deferred |
| 2 | **If resuming: install the Scheduled Task supervisor** ([§4.2](#42-making-it-survive-90-days-)) | Configure restart behavior only after the owner authorizes collection again. | Deferred |
| 3 | **If resuming: schedule the snapshot jobs and decide on a clean restart** | Resolve whether the preserved 5,396-cycle database is compatible with the V1.0.0 engine before choosing continuation or a new run. | Deferred |
| 4 | **Write the designer-surprise predictions** | One metric answers your actual question — *"did it produce anything I did not anticipate?"* — and it cannot be automated, because only you can say what you expected. The scorer is built; it needs your predictions recorded **before** a run. | 20 min |
| 5 | **Do not recalibrate the completed Phase I detector** | The 3-SD detector met the false-alarm gate for cause-mixture worlds, but Markov and decayed association each alarmed in 3/20 mapping-swap controls. Threshold tuning would change the completed protocol; Phase J tests a distinct adaptation question. | Resolved 2026-10-23 |
| 6 | **Use structure-recovery results to choose the next benchmark** | Completed: co-occurrence beat Organica in clean, overlapping, and stress worlds; the result motivated an external task focused on adapting after gradual environmental change. | Complete |
| 7 | **Use the Phase J result to guide V1.0.0 review** | The frozen benchmark found substantially higher Organica NLL and no adaptation-cost advantage over either baseline in either gradual-transition family. Do not infer usefulness from internal structure counts. | Results complete; see journal §30 |
| 8 | **Only after a stable advantage, run targeted layer ablations** | Identify which mechanisms explain any task-specific advantage over the strongest simple baseline. | Later |
| 9 | **Structural-contribution study — closed at the design gate; nothing to do** | Owner decision recorded 2026-11-02: keep the preregistration unchanged and run no confirmatory seed. The density finding (329–333 edges over 17 target tags is 86–87 % of the possible pairs) **is** the result; the 20 % overlap limit stays, because moving it after the control failed would turn a failed control into a different experiment; and the weight-level shuffle is **not** substituted — it keeps every pair and so tests edge *strengths*, not the learned pairings, which needs its own preregistration. | Resolved 2026-11-02 |
| 10 | **Upload both papers' packages to Zenodo** | Built and checked 2026-11-02. Paper 01: **25-page** PDF (revised 2026-11-02), 0 LaTeX errors, 0 overfull boxes, five vector figures. Paper 02: 14-page PDF, 0 errors, 0 overfull boxes (its seven-column tables are set in portrait, not on landscape pages), three vector figures. Both: 38 of 38 cited artifacts inside the archived tree, checksums under `.scratch/deposit/`, and a reproduction bundle naming the archived commit and the commands that rebuild the papers. The upload is the only step left, and it mints public DOIs — so it is yours. **Before the upload:** open both PDFs and look at the pages — figure placement, caption collisions, and Paper 02's two wide tables (portrait since 2026-11-02) — because nothing in the pipeline renders a page to an image; the checks prove there are no overfull boxes, not that the result reads well. Title, author, subject and keywords are now inside the files and asserted by the build. **Reconciled 2026-11-02:** both Zenodo records now carry the document's own title (the longer descriptive variants appeared in neither PDF) and Paper 01's description now covers §4.10; `tests/test_pdf_titles.py` fails if a record and its document disagree. **Also 2026-11-02:** all 40 pages of both PDFs have been rendered to images and inspected — Paper 01's 23 pages are clean, Paper 02's three layout defects found in that review are now fixed (Journal §128) — so your page check is now a confirmation of renders you can see rather than a first look. | 15 min |
| 11 | **Decide whether to spend the strength-assignment confirmatory block.** `docs/STRENGTH-ASSIGNMENT-PREREGISTRATION.md` is committed with its harness, and the design block (`20270401`–`20270405`) now passes every gate end to end: coverage of realised cells by a formed edge **77.1 %–81.4 %**, median largest probability change **0.0926–0.1125**, zero draws that moved nothing, and eleven layer fixtures including a negative plant with **nonconstant** weights that reaches exactly zero and fails when exchangeability is broken. The first run of that block **failed** gate S2, and the diagnosis is in the record: the original primary window left only **1.6 %** of realised cells carrying a weight the intervention could move, so Amendment A1 moved the primary window to the full held-out window and gave S2 a coverage floor — disclosed as a pre-outcome design amendment, with the bar, the direction and the labels unchanged. **The confirmatory block `20270406`–`20270420` is unspent and has not been read.** Spending it is one run, after which the study reports §6's label with no re-run. Run: `PYTHONHASHSEED=0 python -m benchmarks.strength_assignment_harness --design` (audit, ~2.5 min) and, only if it passes, `--confirmatory` (~8 min). | 15 min |
| 12 | **Decide the scaling rule before authorising any larger run.** `docs/SCALING-LADDER.md` measured it on 2026-11-02: five fresh methodology worlds, exposure fixed at 110 cycles, scored window 1x-16x. The frozen 50-cycle window is too short for one run to resolve itself (within-run SE 0.008830 against its own delta 0.007468, and no number of runs reaches half the between-world SD); from 100 cycles up the spread between worlds is flat, so worlds are the horizon. **Re-analysed after the owner's challenge - same five worlds, no new seed: the criterion is now the probability that a run reports its own world's sign, not the SE/delta ratio.** That ratio is a t-statistic, not a bar: 1.18 reads 0.80 and 1.57 reads 0.74 through the normal CDF, and it moves with the pooled delta rather than with the window (0.003536 -> 0.002085 between 100 and 200 cycles is what made the 200-cycle ratio worse). The sign probability is **0.855 at 50 cycles (min world 0.780, one world of five at 0.90) and 0.977 at 100 cycles (min 0.917, all five at target)**, first reached at `2x`. Agreement with the *block's* sign never exceeds 0.780 at any window and falls again at 16x: a run in a world whose effect is negative can be perfectly resolved and still disagree with the average, so only more worlds move that number. **Adopted on 2026-11-02 as the scoring convention for future methodology blocks** (`docs/SCALING-LADDER.md` §10): score at least 2x (100 cycles) - the smallest window where every world's own sign is resolved (0.917-0.997; at 50 cycles only one world of five reaches 0.90) - then spend on worlds; do not lengthen the window as a substitute for seeds, and do not read 4x/8x/16x as improvement (0.961, 0.974, 0.944 against 0.977 - inside what five worlds separate). The window is provisional, not a validated minimum (§9's audit: the target is a convention, and a fixed 4x reference would give 0.898). **Known limitation, logged for the next methodological review rather than fixed:** the per-world quantifier is a conjunction, so it gets harder as worlds are added (0.648 at five worlds, 0.177 at twenty, under the weakest measured value); the rule stands and may not be relaxed on those grounds. The adoption re-scores nothing, changes no frozen window, spends no seed and authorises no confirmatory run. | ~1 h, done |
| 13 | **Settle the central scientific claim before spending the next block, and hold the measurement framework fixed until it is settled.** Owner's direction, 2026-11-02: the apparatus grew faster than the question it serves - candidate-membership auditing, strength-assignment controls, sign-resolution estimation, scaling analysis, reference-sensitivity auditing, record safeguards - and each addition must now earn its place by serving a named claim. **Frozen until further notice:** no change to the measurement framework without a justification tied to a scientific question. **Chosen 2026-11-02, as a working hypothesis and not as an established claim:** option (3), changes in internal structure produce identifiable changes in behavior - recorded in [`docs/STRUCTURE-BEHAVIOR-DESIGN.md`](STRUCTURE-BEHAVIOR-DESIGN.md) at **Level 2 (prediction on held-out events)**, with Level 3 (causal influence) explicitly excluded because nothing in the design manipulates the structural variable. The record fixes the predictor (`DI`), the outcome (`revision_held_out`), the disjointness guard between their pair sets, three generating configurations plus the gate that drops one rather than approximating it, the null and both falsifiers, and the pre-committed outcomes - including that a relation which weakens across conditions is reported as the finding. **Not a first association test:** the formation-provenance confirmatory block already found a structural property associated with later *occurrence* of its content (0.214061, [0.195886, 0.228119]) - but occurrence is a property of the stream, not of the organism's response, and that study's own record says it does not establish that the knowledge is useful. What remains open, and what this design tests, is structure predicting the organism's own later behavior and the stability of that relation across configurations (design record §2a). **No seed is named and nothing is authorised:** the independent review in §8 comes first. Once chosen, the owner's order: independent review of definitions, estimators, comparator selection, controls and interpretation; then design the conditions experiment; then preregister and execute once. | minutes to record; the choice is the owner's |

| `docs/REVIEW-PRIMER.md` | the protocol in plain language, five minutes, for a reviewer outside the field |
| 14 | **Obtain the independent methods review before any confirmatory seed.** `docs/INDEPENDENT-METHODS-REVIEW.md` is the brief and the rubric: five questions mapped to the parts of the design that answer them, five eligibility criteria, the artifact package (nine files, each checked to exist), a PASS/CONDITIONAL/DEFECT rubric, and the three outcomes - approved, approved with conditions, rejected. **The safeguard is the point:** the reviewer sees no data from this design, because none may be produced until the outcome is recorded; if an item needs data the reviewer gets design-block data only, declared as such. Conditions must be specific enough to re-review, and a rejection is recorded verbatim. The reviewer cannot be the author of the design record, and cannot be me. The package the reviewer receives is `docs/REVIEW-PACKAGE.md`: the protocol (now carrying its nine required elements, its statistical model and its rejection table), the prior-evidence summary, the artifact list, the rubric and the report form. | one external reviewer; weeks |
| `docs/AI-REVIEW-PROMPT.md` | the paste-in prompt for a machine pre-pass, and the four reasons its output cannot fill §7 |
| `docs/REVIEW-REQUEST.md` | the one-page letter a reviewer receives, and the checklist for sending it; written, not sent |
**Completed on 2026-10-21 — recorded, not just done** (per rule 3 of [§18](#18-keeping-this-manual-current)):

| Action | Outcome |
|---|---|
| Commit and push the whole working set | `master` is in sync with `origin/master`. Commit `dacf170` — 59 files, +20,853 / −4,065. Nothing uncommitted except the live `organica.log` and `memory.db`, both gitignored, both alive. |
| Repair the observation pipeline | Snapshots contain real numbers instead of `{}`; the event journal is idempotent and time-windowed. |
| Make the repo usable by a stranger | `GETTING-STARTED.md`, `build.py`, `LICENSE`, `CITATION.cff`, `requirements*.txt`, `conftest.py`, and 9 examples that can no longer delete the live substrate. |
| Answer the long-horizon question | The cold-start ablation is complete and reported — [§8.1](#81-the-cold-start-study). |
| Answer the harder question: which parts are load-bearing? | The ablation study is complete: 11 conditions, pre-registered before the run, with a mechanism-verification stage run before any interpretation. [§8.2](#82-the-ablation-study-which-mechanisms-are-actually-doing-the-work) |
| Make the claims checkable by anyone | `docs/EMERGENCE-CRITERIA.md` defines what emergence means here, level by level, and states plainly which levels the project can currently evidence and which it cannot. |

### 7.2 Decide this week

| # | Decision | Why it matters | Detail |
|---|---|---|---|
| 4 | **The confidence-formula amendment** — *now the top-ranked decision* | Confidence is a **share**: `support / (support + contradiction)`. A hypothesis is scored against the *total flow of its siblings*, so a subject with many successors dilutes every minority expectation below the death threshold of 0.15. This is **supported causally, not guessed**: the `wide_lookback` ablation (lookback 3 → 30, nothing else changed) destroyed G5 outright, while `no_truncation` was byte-identical to baseline and `no_dev_stopwords` kept G5 at cycle 2 with a smaller population (1 theory / 1 question against 2 / 2). The proposed fix is a Laplace/Beta-smoothed posterior, which keeps a genuinely split belief alive, makes the lookback width irrelevant, and is *simpler* than what it replaces. | [§8.1](#81-the-cold-start-study), journal [§14](../research-journal/phase_g_findings_20261021.md) |
| 5 | **Clean restart on the final build** | The current run is valid, but the first ~264 cycles ran pre-batching and pre-retention. A fresh start costs about an hour of data and removes an argument from the paper. **Do this after the architecture decision above, not before** — otherwise you restart twice. | [§6.4](#64-rules-for-a-clean-run) |
| 6 | ~~**The hypothesis-cap amendment**~~ — **superseded 2026-10-23** | The reasoning was wrong. The cap was believed to bind constantly; measured, it binds in **0 of 600** cycles and `MAX_HYPOTHESES` is **INERT**. The *sort* was still wrong and has been fixed (see decision 11), but the sort is a correctness fix, not a behavioral one. The cap is **not** the constraint. | Journal [§17](../research-journal/phase_g_findings_20261021.md), [§19](../research-journal/phase_g_findings_20261021.md) |
| 7 | **Scope the experiment executor** | The largest remaining design gap, and it now blocks two things at once: the emergence claim at Level 5, and the ability to tell whether the attention economy actually buys anything (the metric that would separate EIG from random is exactly the one that needs an executor). Needs a probe format, a probe→event mapping, and a belief-delta measurement. | Journal [§13](../research-journal/phase_g_findings_20261021.md) |
| 8 | **Should `cross_domain_validation.py` use the real lineage audit?** | The shipped check measures a proxy (parent ids present among candidates) and would report 100% even if nothing touched raw experience. The real audit is `benchmarks/lineage_audit.py`. Aligning them means the published report and the shipped verification agree. | Journal [§12](../research-journal/phase_g_findings_20261021.md) |
| 9 | **Decide whether the architecture should be simplified** | The ablation study found that several layers contribute nothing measurable. The stated goal was "the simplest possible architecture that emulates living human learning and memory perfectly" — and simplification only happens if you are willing to *remove* what the measurement says is ornament. That decision is yours, and it needs a recorded rationale either way. | [§8.2](#82-the-ablation-study-which-mechanisms-are-actually-doing-the-work) |
| 10 | **The valuation layer — a proposal, not a change** | *"Feeling comes before thinking."* Organica already computes value signals (confidence, uncertainty, EIG, novelty) and already computes them upstream of the beliefs they gate — that is Law V, and it is a salience rule. What it lacks is **valence** (no aversive signal: nothing is costly), **persistence** (attention is re-derived every cycle rather than integrated — which is why the G5 duty cycle oscillates instead of trending), and an **appetite for disconfirmation** (contradiction is *derived from* the graph, so it is recorded, never sought). The proposal is to make the valuation layer explicit and give it those three properties — but **after** the experiment executor, because a drive cannot be measured without behavior to measure, and because the executor is where valence naturally comes from. | Journal [§18](../research-journal/phase_g_findings_20261021.md) |
| **11** | **The stimulus must carry more independent branch points** — *new, 2026-10-23, and now the top blocker* | The Tier-1 matrix is **gated**: gate G-P1 requires retention pressure > 1.0, and the belief pool reaches only 5.3–7.7 against a cap of 15 (pressure 0.35–0.51) at every setting tested. The belief pool is bounded by the number of distinct *reciprocal* structures reaching Layer 4, and a process only forms from a reciprocal prediction pair. Measured: widening the world makes things **worse** (belief pool 5.47 → 1.41, theories → 0), and widening the budget does nothing. What is needed is a stimulus with **more independent branch points** — subjects with competing successors — so the belief pool can exceed 15 and a retention policy can have something to choose between. This is a stimulus-design decision, not an architecture one. | [§8.3](#83-the-instrumentation-audit-where-the-pressure-really-is), journal [§19](../research-journal/phase_g_findings_20261021.md) |
| **13** | **Phase K leaves a sharper question than it answered** — *new, 2026-10-24, and now the top-ranked decision* | Phase K searched three candidate task families against the strongest simple baseline and **all three came back REVERSED**, and the pre-committed terminal outcome **H2** fired: three more families ruled out, **no V2 designed**. The ablation arm is the part that redirects the work: on K1 and K2, where a mechanism was ablated specifically (question generation, falsification), the ablation changed **nothing measurable** — all intervals contain zero. So the next question is not *which task?* but **which internal mechanism, if any, produces an external advantage at all?** Another task family would be the seventh entry in a list of losses; the mechanism question is answerable without designing V2 and it is what would make a seventh family worth running. | [§8.5](#85-phase-k-the-search-failed-and-what-that-changes), journal [§33](../research-journal/phase_g_findings_20261021.md) |
| **14** | **Formation vs. utilization — the campaign is complete; the pre-committed mapping names the use path, and a V2 build is still not authorised** — *updated 2026-10-30* | The 30-seed campaign ran to completion (60/60 units, all audits pass or N/A). **C loses transfer on both tasks** (T1 d = −0.0262, T2 d = −0.0227) and **B loses it too** (T1 −0.0296, T2 −0.0795), so §7's "both lose" row fires: **V2 targets the use path (retrieval / activation / readout)**, with transfer and retention named as the failing limbs. C wins revision on T1 (+0.1002) and ties it on T2 (+0.0007). **That decision is made: the diagnostic was commissioned, frozen and run (2026-10-30), and it returned AUDIT REQUIRED** — no component was selected, so the use path remains the target, not a design. The result selects a target and does not authorise a build; the next decision is the reproduction audit (action 16). | [Results](formation_utilization_results.md); protocol §7; [§8.21](#821-the-formation-vs-utilization-campaign-the-verdict-and-what-it-does-and-does-not-mean-2026-10-30) |
| **15** | **The use-path diagnostic ran and returned AUDIT REQUIRED — D0 did not reproduce the campaign's C scores on 18 of 180 seed-limbs** — *run 2026-10-30* | The pre-committed validity gate fired: 162/180 seed-limbs agreed within 1e-4, 18 did not, largest **0.004386** (T1 seed `20261128`, revision). Every other control passed. No room estimate, no variant effect and no component are reported; the mechanism condition of gate 5 remains unmet. The recorded candidate cause was the engine's `recent()` tie order against `structure_edges` keeping the first snapshot per id; the audit of 2026-10-30 tested it and **did not support it** (the tiebreak changed nothing; both orders were repeatable) — the cause is upstream of `recent()` and is not identified. | [Results](USE-PATH-DIAGNOSTIC-RESULTS.md); [Protocol](USE-PATH-DIAGNOSTIC-PREREGISTRATION.md); [§8.22](#822-the-use-path-diagnostic-the-step-to-v2-authorization-2026-10-30) |
| **16** | **Run the reproduction audit — done 2026-10-30; the tie-order hypothesis is not supported** | 48 runs (8 failing seeds × 2 configurations × 3 repeats). Both configurations stable 8/8 and identical 8/8; neither reproduced the campaign's per-type table (0/8 and 0/8), so score reproduction was not entered. The divergence is upstream of `recent()`; the audit does not name it. The next test is a hash-seed sensitivity sweep on one failing seed; if that does not move the table, the campaign-time code is the remaining candidate and needs a campaign-time copy. D0 remains fired and no V2 follows. | [Audit](USE-PATH-AUDIT.md); [Artifact](use_path_audit.json); [§8.22](#822-the-use-path-diagnostic-the-step-to-v2-authorization-2026-10-30); journal §69 |
| **12** | **The 90-day horizon** — *new, 2026-10-23* | The run plateaued at cycle 261 with **zero** variance for 3,464 cycles. The 90-day single arm is replaced by the comparative matrix as the primary experiment, and the daemon becomes a **monitor** rather than a gate. A clean restart (decision 5) is still worth doing, but it is no longer urgent: the matrix is what produces the next evidence, and it runs cold by design. | [§2](#2-where-things-stand-right-now), journal [§19](../research-journal/phase_g_findings_20261021.md) |

> **Phase A freeze reminder.** Decisions 4 and 6 are *cognitive* changes — the confidence formula and the layer-selection logic. Under the Phase A freeze they remain **proposals only**; nothing in this turn applied them. What shipped this turn was substrate and measurement only. Any change to decision 4 ends the current run and requires a fresh start ([§6.4](#64-rules-for-a-clean-run)).

### 7.3 Keep doing

| # | Cadence | Action |
|---|---|---|
| 7 | Daily (30 sec) | `python benchmarks/study_health.py` — glance at the duty cycle and the failure count. |
| 8 | Daily | `run_daily_observer.bat` (or let the scheduled task do it). |
| 9 | Weekly | `run_weekly_monthly.bat`; skim `snapshots/event_journal.log` for the narrative. |
| 10 | At day 7, 30, 90 | Write a real Phase G report: G5 duty cycle over the whole window, belief-revision events, memory bound, and a Generation 9 recommendation. |
| 11 | After **any** engine change | Re-run `python benchmarks/cold_start.py --cycles 40`. It is the regression test for "did we accidentally make the organism depend on us?" — if a condition that used to bootstrap now fails, that change was cognitive, not cosmetic. |

### 7.4 When to worry

- `theories` = 0 across a **rolling window** (not one cycle) → the stream or the substrate is broken. Re-run `benchmarks/g5_gap_diagnostic.py`.
- `duration_ms` median drifting above ~1 s → substrate growth. Run `benchmarks/substrate_probe.py`.
- `sleep_cycle` going backwards → the counter bug regressed. Everything time-derived is suspect until fixed.
- `status: failed` appearing → check `console.log` for the traceback.
- G5 duty cycle dropping below ~95% → *something changed*. Check the engine's modification time against the daemon's start time ([§6.4](#64-rules-for-a-clean-run)), then re-run `benchmarks/cold_start.py`.

---

## 8. The findings, and what each means for you

Full detail and evidence: **`research-journal/phase_g_findings_20261021.md`**.

| # | Finding | What it means for you |
|---|---|---|
| 1 | **The original study stream could never reach G5.** No subject ever had two competing expectations, so Layer 5 had nothing to coalesce. 0 theories, 0 questions, and **zero contradictions** across 670 cycles. | The first 90-day attempt would have recorded a flat G4 line with confident-looking telemetry. Law V's EIG economy never ran. *Fixed* by a branch-structured stream chosen by sweep. |
| 2 | **The substrate could not have survived 90 days.** A full-table scan every cycle (4,826 ms at 1.65M rows) projected to ~370M rows / **~210 GB** and ~12 min/cycle. | The study was infeasible as designed. *Fixed* with an incremental counter table (result proven identical) and bounded retention. |
| 3 | **The cycle counter reset mid-run.** It was read from a 500-row window of the table it writes to; once candidates/cycle exceeded 500 the marker vanished and the counter fell from 319 to 4. | Every longitudinal time series was suspect. The health report's "670 cycles" was a count of *log lines*, not cycles. *Fixed* with a monotonic table; 426 cycles now show 0 resets. |
| 4 | **The log was truncated on every restart.** The launcher used `>` against a file the daemon's own append-mode FileHandler owns. | The longitudinal record was being destroyed. *Fixed*; the log now appends and survives restarts. |
| 5 | **The observation pipeline had never actually run.** The weekly snapshot contained literally `{}`; the event journal parsed a dead log format; "births today" was a 30-second delta; "per day" velocity used 7 cycles. | There was no data pipeline behind the study. *Fixed*: time-window based, idempotent, refuses to write empty artifacts. |
| 6 | **G5 is an oscillation, not a state.** It fires, collapses, and returns. Minority expectations sit at confidence 0.15–0.20 against a `DEATH_THRESHOLD` of 0.15 — a competitor can be extinguished by the success of its sibling. | Report Generation 5 as a **duty cycle**, never a per-cycle boolean. Also sharpens the case for the architecture amendment. |
| 7 | **One fsync per candidate dominated the cycle.** 1,023 commits = 3.0 s of a 4.5 s cycle. | *Fixed* by transaction batching: 4,500 ms → **263 ms**. The cycle is now cognition-bound, not disk-bound. |
| 8 | **Law II holds — but nothing was measuring it.** `get_ancestry()` cannot reach G0, and the shipped validation only checked that parent ids were present among other candidates. | The invariant is **true** (100% grounded, both stores). The gap was in the *verification*, not the architecture. `benchmarks/lineage_audit.py` now tests the real thing. |
| 9 | **Experiments are generated but never executed.** Every consumer only prints them. | Law IV is never exercised and **no Question can ever close**. The study measures epistemic *tension*, not *resolution*. Largest remaining design gap. |
| 10 | **The organism bootstraps most of itself, but not Generation 5 on an unengineered stream.** Measured across eight assistance levels: G1–G4, G6, G7 and G8 appear from an unengineered stream with no seeding, and G2 processes and G3 workflows at cycle 14. G5 never does there — but it does appear, unseeded, at cycle 10 in `cold_start`, which uses the engineered stream. The 2026-10-21 table said it never did in that condition; that row was re-measured on 2026-10-30 and no longer reproduces. | The project's central claim holds for every generation below G5, and G5 is bounded by the stimulus rather than by seeding alone. The confidence-formula evidence is now narrower: `wide_lookback` destroys G5, `no_truncation` is identical to baseline, `no_dev_stopwords` is close but not identical. See [§8.1](#81-the-cold-start-study). |
| 11 | **Six task families are now negative, and the mechanism ablations came back empty.** Phase K searched three candidate task families against the strongest simple baseline; all three came back REVERSED, and on the two families where a mechanism was ablated specifically, the ablation changed nothing measurable. | The question *“what class of problems benefits from a developmental architecture?”* is still **open**, with six families excluded rather than one verdict reached. The next useful step is a **mechanism** question, not another task family. See [§8.5](#85-phase-k-the-search-failed-and-what-that-changes). |
| 12 | **The internal developmental machinery is not what drives development.** Removing contradiction, removing question creation, and selecting the lowest-EIG candidate each *raise* development (P2, P3, P5 — all REVERSED), and the Phase K ablations agree independently: `NO_QUESTIONS`, `NO_FALSIFICATION` and `NO_DREAMS` all have intervals containing zero. | What moved development was the **curriculum and the structure of the stimulus** — not the curiosity, contradiction and attention machinery designed to be the active ingredient. This is the finding that most redirects the work. See [§8.6](#86-the-v1-synthesis-what-v1-established-and-what-it-did-not). |
| 13 | **Organica 1 is frozen, and the freeze is enforced by a test.** The `v0.9.0` tag is the archival reference for the engine; `tests/test_v1_freeze.py` compares every frozen file against that tag and fails if one differs. | The engine is a fixed reference object now: everything afterwards measures it and nothing changes it quietly. Benchmarks, harnesses and documentation stay free, so the research continues — it just runs against a stable thing. See [§8.7](#87-organica-1-is-frozen-the-v090-tag-is-the-archival-reference). |
| 14 | **An identical value at every point of a sweep is a measurement defect until proven otherwise.** The Phase L pilot returned `DI = 0.000` at all eight points of the support-ratio sweep — a clean-looking negative result that was entirely an artifact: the late group arrived after the run had ended, so the late structure was never available, and a ratio with no denominator was being reported as zero. Four harness defects in total, plus a bootstrap that was resampling the wrong statistic. | Two audits were in place and **both passed** on the broken world, because they checked the *metric* and the metric was perfect — the *design* was dead. A **third audit** now checks the design itself (the degeneracy audit), and an unmeasurable quantity is reported as not measurable and **excluded, never zeroed**. See [§8.8](#88-phase-l-the-pilot-that-looked-like-a-negative-result-and-was-not). |
| 15 | **Phase L's primary axis found a reproducible crossing and still did not clear its bar.** On the V1 sweep the Displacement Index rises from 0.000 to 0.750 and the Preservation Index falls from ~0.79 to 0.000; the curves cross at **3:1**, and that crossing survives everything: a 10,000-replicate paired bootstrap puts it at **[5.0, 5.0]** with 10,000 of 10,000 replicates finding it, eight alternative bootstrap seeds all return `INTERIOR`, and leave-one-seed-out leaves it at 3:1 in **10 of 10** folds. But one of the four pre-committed criteria — *PI is monotone decreasing* — was **not met**: mean PI rises 0.789 → 0.794 between 1:4 and 1:3 before falling through the rest of the sweep. The pre-committed verdict is therefore **`H3-L — INCONCLUSIVE`** (*raise n; conclude nothing*), and no V2 is authorised. | **Three passing criteria are not a partial success.** The protocol asked four questions and the phase is judged on all four; the number satisfied is not a score. The criterion was evaluated once by the committed code and it failed — it was **not** re-read, relaxed, or reinterpreted afterwards, and the stable RT was not allowed to stand in for the criterion that failed. Note also that the protocol describes `H3-L` as *"intervals too wide to place RT"*, which is **not** what happened here; that wording gap is recorded, not exploited. See [§8.10](#810-phase-l-the-primary-axis-result). |
| 16 | **The raise-n run did not clear the bar either — and it showed that the bar was testing the wrong shape.** At **n=30** (240 cells, the original 80 reused not recomputed) the verdict is still `H3-L — INCONCLUSIVE`, and now **two** criteria fail: *DI monotone increasing* was met at n=10 and is **not met** at n=30. The RT did not move (3:1, [5.0, 5.0], 10,000/10,000, leave-one-seed-out 3:1 in **30 of 30**). The reason is now visible: the curve is a **step function** — DI = 0.000 exactly across 1:4–1:1, DI ≈ 0.71 across 3:1–6:1, two sharp transitions between — so **both failing criteria are sign tests on steps whose 99% paired interval contains zero**. | **A criterion that flips when n changes is measuring the draw, not the organism.** Resampling the 30 measured seeds: the two stable criteria (DI range, interior crossing) hold in **100%** of random subsets; the two monotone ones hold in 7–19%; **all four together in 0–2.9%**. Strict monotonicity is not a property this curve has, and no n will make a plateau into a ramp. The verdict still stands and no boundary is claimed — but the phase can now say *what* the verdict means. See [§8.11](#811-phase-l-the-raise-n-result-30-seeds-per-point). |
| 17 | **Phase L published a characterization, and kept the verdict.** The raise-n result is now read as **regime behavior separated by a reproducible transition region**, not as a continuous coherence–plasticity trade-off — and the two artifacts are kept deliberately separate: the measurement record says `H3-L — INCONCLUSIVE`, the synthesis says what the shape is, and neither re-scores the other. | **A protocol verdict and a scientific characterization are different claims and belong in different documents.** The temptation is to let a good story quietly replace a failed protocol — *"a stable threshold at 3:1, that's a boundary, isn't it?"* It is not: a threshold is a boundary only if the trade-off is a continuum the threshold divides, and here the curve is flat on both sides of the crossing. Calling it a boundary would be the same category of error as re-scoring the failed criteria, only more flattering. See [§8.12](#812-phase-l-the-published-characterization). |
| 18 | **The next question is not "can it develop?" but "does what it develops become usable?" — and answering it needs a record an investigator can check.** The specification for that record is written against the frozen engine's actual report fields and persistence limits, and it corrects one thing in the record format as first proposed: the engine's `support_count` counts **temporal transitions**, and `contradiction_count` is the subject's **competing flow** — *not* a count of observations that contradicted the claim. | **A count must be named as what it counts, and a trace must not contain counterfactuals.** Calling 12 transitions "12 observations" and 4 competing transitions "4 contradictions" would put a false claim at the center of the audit record — and the audit record exists precisely so that claims can be checked. Separately: *"candidate B would have survived without A"* is a **replay**, not a trace; it needs a separate run and its own label, and can never be a field of the trace. See [§8.13](#813-phase-m-groundwork-the-development-audit-trace-specification). |
| 19 | **The trace must adjudicate a pre-committed question, or it is a second inventory.** The audit layer is attractive, and attractive things become projects: it could be built, extended and admired without ever settling a question the project wanted answered — which would make it a *second* inventory ("how many events resolve?") and swap one measurement habit for another. So the rule is pre-committed rather than aspirational: **the next protocol's success criteria must contain at least one trace-derived diagnostic, and a result that fails it fails the protocol even if the headline behavior is correct.** | **An instrument that cannot fail a claim is decoration, and a diagnostic that is never a criterion is just a number to report.** The first pre-committed instance is the disqualifier: *a predicted-correct result whose supporting evidence is self-sourced is not a transfer result* — the temporal graph's lookback window has no `event_type` filter, so a belief's support can come from the organism's own previous sleep payload (D2). That is the first concrete use of D2, and it is what turns a disclosed defect into a live instrument. And the trace's own metrics — evidence completeness, lineage completeness, selection reproducibility — stay **diagnostics of the instrument**: reported, never criteria. See [§8.14](#814-keeping-the-trace-honest). |
| 20 | **A pre-committed threshold must not be computed from the run it judges — and the window that bounds the trace was an order of magnitude smaller than asserted.** The per-claim transfer rule's third condition read *"no higher than the run's baseline rate"* — circular, because a baseline computed on the same run relaxes the criterion whenever that run's beliefs happen to be unusually self-sourced. **The reference rate is now FROZEN at 17.9%** (the distinct-evidence self-sourced share on the calibration probe), is **not recomputed on the evaluated run**, may be **re-calibrated only on data that is not being judged**, and is labelled a **provisional calibration value, not a precise universal cutoff** — one run, one world, one policy. **And the cognition window is now MEASURED rather than estimated: the engine stores 2,374.68 sleep events per cycle, so the 4,000-event window spans only 1.7 cycles — not the "roughly 40–130 cycles" this project had asserted from a guess.** The estimate was wrong by more than an order of magnitude and the correction is recorded rather than quietly fixed. Consequence: a lineage still being produced stays inside the window, but one that stopped being produced is gone within about 1.7 cycles — so the developmental history of anything the organism has moved on from is **unrecoverable**, not slowly censored. **A3's definition is now fixed in advance** (lineage reachability, evidence linkage, and a four-way truncation split reported separately), and **fidelity is not sufficiency**: reproducing the implemented rule does not establish that the reconstruction is a uniquely correct account of *why* a belief arose. |
| 21 | **A3 is met, and it says something uncomfortable: an investigator cannot see more developmental history than Organica itself remembers.** The ancestry auditor walks each cycle's structures' parent chains against the engine's own window. **Lineage reachability 1.000** (8,061 of 8,061 structures resolve back to Layer 1 within depth 7), **evidence linkage 1.000** (1,412 of 1,412 claims resolve to event ids with a world/self split), **zero honesty errors**, and an empty structure-level truncation split — while the branch-level count shows **105 aged-out branches**, because every structure resolves through at least one branch that stayed in the window. **The window is not the binding constraint on lineage depth, and this corrects section 12's claim that it was:** surviving candidates are re-stored every cycle, so a live ancestor stays in the window however old it is; what bounds a lineage is the **death** of an ancestor. Measured: the window holds 3,998 candidates, the oldest last stored 1 cycle ago, content spanning 2 cycles. **So the trace reconstructs everything the organism still holds, exactly — and the developmental history of anything it has moved on from is unrecoverable, because the organism does not hold it either.** That is a hard ceiling on the project's distinguishing property, and it is a property of Organica 1 as frozen, not of the auditor. |
| 22 | **The organism's memory and the laboratory's record are different objects, and the acquisition experiment must score them separately.** Q1 — *did the organism retain the knowledge?* — is answered by the organism's own state. Q2 — *can the laboratory prove how it developed?* — is answered by the per-cycle snapshots the laboratory kept. Conflating them is how an audit system slides into claiming historical reconstruction it never earned. **And two diagnostic probes changed what the design has to ask.** First, the lineage is **re-derived, not carried**: a structure's parent set is identical in ~94.5% of structure-cycles, but **87.2% of all 8,416 lineage links point at structures re-derived in that same cycle** — so the identical sets are deterministic re-derivation, not copied edges. Second, the engine's survival rule is **asymmetric across layers**: `_natural_selection` decays and prunes **Layer 1 only** (`sleep.py:1752-1802`, `_candidate_key` returns `""` for everything else), so **Layer 1 survives only if current experience keeps producing its content key, while Layers 2–4 are never decayed and persist as rows with re-derived edges.** The pre-registration therefore tests six cells (parent removed or not × source experiences removed or not × removal applied to the **observer** or to the **organism**), and the sharpest prediction is computed from the source rather than fitted: a Layer-1 structure whose key stops being produced is pruned after `⌈log(0.15/c)/log(0.8)⌉` cycles — 4 cycles from 0.3, 6 from 0.5. |
| 23 | **The acquisition study was reviewed, and five defects in its plan were found — including one that would have made the headline meaningless.** The endpoint had been **DI**, which measures *structural displacement* (`late_structure_retained / late_structure_available`), **not** whether a belief predicts the world; it is now a **ground-truth prediction score** on a fixed label set, with the exact predictions named. **"Source experiences removed" did not say what derived memory survives** — ingest also accumulates `cooccurrences` and `tag_counts` (`memory.py:282`, `306`), which outlive the event rows — so the condition is now named **"episode removal with learned graph retained"**, and **the same rows are removed from every learner's store**, which is what makes the comparison about *reconstruction versus replay* rather than about *different access to evidence*. The cell matrix was not specified (a "2 × 2 × 3" heading, a baseline added on top of six cells, and a prediction table with five rows): it is now **one complete table with the exact number of runs — 10 per seed, 30 seeds — and a prediction for every cell**. And **"same memory budget" needed an operational definition**: identical raw rows and identical removal for every learner, with derived state deliberately *not* equalised, because derived state **is the mechanism under test**. The review also found the audit build's remaining work is smaller than the roadmap implied: **only A5 and A6 are pending**, so they are closed and then the instrumentation is **tagged, frozen, and stopped** — no feature may be added to it. And the review caught **presentation drift**: the README still claimed parent links ran *down to raw experience events*, which the engine has never done — the `parent_ids` chain terminates at Layer 1 — and the manual's status table was dated October 23 while the file recorded October 26 work. |
| 24 | **Five claims in the project's own summary were wider than the checks behind them, and they are now narrowed.** (a) *"Revision exists"* was a misnomer: Phase L measured **structural displacement** (a structure-retention index), not belief correction against ground truth — and on Phase K's belief-revision task Organica scored **0.4111** against the best simple baseline's **0.9846** (difference **−0.5735**, 98.33% interval **[−0.6162, −0.5309]**, **REVERSED**), so belief revision remains a **separate capability question**. (b) The **3:1** crossing is robust **within this defined experiment** — this engine, this world family, this support-ratio axis; the eight alternative bootstrap seeds test **resampling stability, not new worlds**, so 3:1 is **not a general threshold for Organica**. (c) **Path dependence** is supported; **strict order dependence is not tested** — the curriculum comparisons vary the event multiset and order together, and isolating order needs the multiset held fixed, which has not been run. (d) On transfer, **no positive transfer has been demonstrated and the measured cross-domain result was negative** (**−0.486** across 12 domain pairs, mean shared vocabulary **0.17 tags**); other forms of transfer remain untested. (e) **"Independently auditable" means independently *reconstructed from the engine's state*, not independently *replicated by another lab*** — and the trace concerns the organism's **surviving, current** structures, not their full past. | **A claim must be no wider than the check behind it, and the summary is where the widening happens.** Each of the five was true of some *narrower* thing the project had actually measured, and each had been stated in a broader form — in the README's own "what is established" section, in the Phase L synthesis, in the V1 synthesis, and in the manual. The error was not in the measurements; it was in the *headline*, which is the one thing a reader takes away. The same discipline that caught the **DI endpoint defect** in the acquisition plan — *a metric imported from another study can measure a completely different quantity* — applies to a summary sentence the same way. **Apply when:** any sentence summarising what the project has established. Ask what the check actually measured, name the population and the axis it was measured on, and cut the claim to fit. See [§8.18](#818-the-five-claims-narrowed-2026-10-26). |
| 25 | **The acquisition endpoint was measuring the wrong thing; the benchmark was rebuilt; and the campaign then stopped at its own gate.** Seven defects were confirmed against the code (the task and the readout described different relations; F1@0.5 was degenerate — the Bayes-optimal model scored **0.0000**, exactly like the trivial model; the projection was directional where the gold relation was not; the "ceiling" was a relation oracle, not a prediction ceiling; retention and transfer were one number with two names; the engine's taxonomy has no category for a tight group; the regime switch is relation-invariant). The benchmark was rebuilt as a **compositional task** and its gate passes: gap **+0.1035 nats**, 99 % interval **[+0.0996, +0.1074]**, with the held cell's gap **4.6×** the rest. Then the frozen engine **failed the preregistered Gate 13 on every inspected seed** — asserted structure coverage **0.0 %–2.7 %** (0–3 of 112 edges) against **112 / 112 (100 %)** raw — and the campaign stopped there. Organica's readout scored **0.453018** against Replay **0.347521** and Statistical **0.347273**. **Transfer was not measured, and it is not a transfer failure.** | **A benchmark must be able to fail, and so must the question it asks — and a benchmark's headroom is not a learner's margin.** The **+0.1035** is the room between the Bayes ceiling and the best simple model; it is **not** what any learner achieved, and reading it as a capability result inverts the finding. The engine's failure has **one named proximate cause** (`MAX_PREDICTIONS = 20` crowding): raising only that cap restores **98.2 %–100 %** coverage, so the failure is attributable rather than mysterious — though **finding 26** shows the *deepest* cause is **precision**, not capacity. **Apply when:** reporting anything from this task — say which of the three questions was answered (*is the benchmark discriminative / does the engine hold the structure / does the organism beat the baselines*) and never merge them. See §8.19 and journal §51. |

| 26 | **The acquisition failure is a PRECISION limit, not a capacity limit — and the two are different claims.** The Gate 13 write-up named `MAX_PREDICTIONS = 20` as the cause, because raising the cap to 1,000 restored coverage to 98.2 %–100 %. Four further diagnostic probes (all on **diagnostic** seeds) show that was the **proximate** bound only. The world's relations **are** in memory (raw temporal coverage **0.97–1.00**, **1.0000** on all six 2-tag seeds), but they are about a **third** of the candidate space and are **not** the high-count rows: precision **never exceeds 0.3438** at any budget under either allocation rule. A 1-tag stimulus removes the within-cell pairs by construction and still fails **0 of 6** seeds. Coverage is a steep dose-response in the cap needing **240–244** asserted edges (~12× the budget), and a **per-source** allocation rule does **not** help (258–286 edges for coverage 0.72–0.77, where global reaches 0.95–0.97 at 320). | **A bounded selection is not a selection rule.** Before enlarging a budget, check that the ranking can find the signal *at all*: measure the coverage ceiling with the budget removed, the precision at each budget, and the same curves under a different allocation rule. If precision is flat and low across budgets and rules, the defect is the **candidate space**, and the question is "can this be ranked by something other than frequency?" — not "how much budget?". The V2 capacity brief's premise ("bounded structural allocation") was measured and does **not** hold, and two of its design objectives are refuted. The specific pollution is **internal vocabulary**: **27–34** distinct sources for a 16-tag world. **No V2 build is authorised.** See §8.19 and `docs/GATE13-CAUSAL-ACCOUNT.md`. |

| 27 | **The relation table mixes world relations with the organism's own descriptive vocabulary — the separation is real, oracle-free, and NOT sufficient.** `memory.py:261` gates the *trigger* of edge recording (`if event_type != "sleep"`) but `memory.py:332` does **not** gate the *lookback window*, so a world event can take its `tag_from` from a sleep row. That is **D2**, disclosed but never measured. Rebuilding the table offline with a world-only window removes **35.7 %–40.7 %** of its rows, and **100.0 %** of the removed rows have a sleep-sourced `tag_from`. The separation uses `event_type`, which the engine already records, so it is **not an oracle**. **But with every contaminated row removed, coverage at the frozen cap of 20 is still 0.0000–0.0446** and the top 20 is still **75–100 % intra-cell**. The substrate is **756–772 world events against 152,186–263,533 sleep events** — **201×–341×**. | **A disclosed mechanism is not a measured one**, and **removing a contaminant can reveal the next one.** Two distinct crowding mechanisms were in play: in the 1-tag stimulus the crowding is the **engine's own vocabulary** (first world edge at rank 31; the top 30 rows all `internal→world`) — a first case, not a distribution: the world's 112 edges are **spread through the table rather than clustered at its top**, so the global count-ranked selection recovers **0–1 of them** at the engine's own budget of 20, **0–2** at 40, **8–16** at 80, **36–55** at 160, and **106–109** only at 320 (`docs/gate13_allocation_rule.json`; the five-seed capacity sweep puts cap 40 at **1–8 of 112** and the frozen cap of 20 at **0–3 of 112**). And in the 2-tag stimulus, once that is removed, the crowding is the **world's own co-occurrence** (intra-cell pairs out-count the law's transitions by ~an order of magnitude). Separate the mechanisms before designing for them — a fix aimed at one looks like a partial success in the other and invites a second, contradictory diagnosis. The V2 requirement list is now **three**: provenance separation, relation-family separation, and a **ranking that is not raw frequency** — the third being the hard one, and the one the capacity sweep showed cannot be bought with budget. **No V2 build is authorised.** See `docs/GATE13-RELATION-SEPARATION.md` and journal §54. |

| 28 | **The third V2 requirement — a ranking that is not raw frequency — was measured, and every criterion the engine already stores fails.** It had been called the hard one, with no precedent in the engine. It has a precedent: `sleep.py:1139-1160` computes `ratio = count / max(source_freq, 1)`, stores it in every candidate's evidence, uses it for **survival**, and then sorts by **raw count** for **admission**. A 60-cell grid over fields the engine already stores (`temporal_count`, `source_frequency`, `target_frequency`, `ratio`) x 2 tables x 2 frequency scopes x 3 seeds reached a **best cell of coverage 0.0804 at precision 0.4500 against a 0.50 gate — six times short.** Neither fix works alone (0.0089); together they take coverage from **0.0000 to 0.0804** and flip the intra/inter balance from 20/0 to roughly 8-15/5-13. Worse, **the engine's own normalized criterion is actively harmful here**: on the raw table under the engine's own scope, `ratio`, `cosine` and `pmi` each select **20 engine-vocabulary edges and 0 world edges** on every seed. The mechanism is measured, not inferred: `_record_tag_counts` sits inside the `if event_type != "sleep":` block, so **`tag_counts` is world-scoped** and the engine's own words have **no frequency entry** — `freqs.get(tag_from, 1)` returns 1, so `ratio = count / 1 = count`, the maximum possible for that count. Adding a self-inclusive scope flips the failure the other way: the engine's sleep output **names the world's tags** (`sable` 2,601 times, `olive` 7,753, `maple` 35,986, `cedar` 52,070), so world tags acquire enormous denominators and are penalised, and the engine's *rare* metadata words win (best world edge `sable` -> `fern`, ratio **0.0177**, against `mutation` -> `cedar` at **0.1654**). | **A normalization can be undefined exactly where it is needed, and the symptom is a ranking that prefers the contamination.** `max(source_freq, 1)` looks defensive and the default of 1 looks safe — it is safe for the tags the counter knows and **catastrophic** for the tags it does not, and the tags it does not know are the ones the criterion must discriminate. **A denominator with a silent default is a hole with a plausible shape.** Two further consequences: **"the engine has no precedent for this" is a statement about the code, not about the space of solutions** (the engine *did* compute a normalized criterion, and using it would have been worse than the thing it replaces), and **when a criterion cannot be computed, the honest report is "cannot be computed", not "does not work"** — the quantity the criterion needs is not in the substrate, so the discriminator has to be **relation-level** (*which event did this relation come from*), not a per-tag statistic. **No V2 build is authorised.** See `docs/GATE13-RANKING-CRITERION.md`. |

| 29 | **The audit build's closure was recorded in six places, and two documents still said the opposite.** On 2026-10-28 A5 and A6 closed, the three probe arms were regenerated, and the instrumentation was tagged and frozen at `audit-trace-v1`; the closure was written into six places (spec §9/§10, README banner, manual §2/§8.17, facts AA26/AB5, AGENTS rule 23(c), CHANGELOG). On 2026-10-29 the owner found that **Paper 02 contradicted itself** — its abstract and §3 said A5 and A6 "remain pending" and the instrumentation "not yet frozen", while its own draft-status line and its conclusion said they had closed — and that the **V2 design brief's §4.3 still read "nearly, but not fully, closed"**, with five further passages in §7, §10 and §11 carrying the same stale state. **Eleven passages across four documents** were corrected: Paper 02's abstract, §3 and draft-status line; the V2 brief's §4.3 heading and body, build gate 4, the gate-5 annotation that called gate 4 open, the §10 corrections table and the §11 table; and the superseded banners in `ROADMAP.md` and `docs/V1-SYNTHESIS.md`, which still described the audit build as unfinished and the pre-registration as Revision 2. | **A freeze recorded in six places is not a freeze if two documents still say the opposite — and a self-contradicting document is worse than a merely out-of-date one.** An out-of-date document misleads the reader who follows it; a self-contradicting document makes the reader distrust the *correct* statement too, because the document has taught them that its own sentences cannot be relied on. The sweep also needs a **named criterion**, not suspicion: the criterion here was **one status, stated in every document that states it** — the audit build's closure is a single boolean, and every sentence that asserts it must agree. Six agreeing places do not compensate for two disagreeing ones. |
| 30 | **The papers are the publication surface, and the manuscript index now carries the plan.** The repository is a research program whose codebase is one component, and the owner set the near-term publication sequence explicitly: **Paper 01** as the honest empirical V1 account (developmental structure forms; external advantage has not been demonstrated; Task 2 stopped at acquisition and transfer was not measured), and **Paper 02** as the bounded audit-trace result (reconstruction of tested surviving state from the engine's stored state). **Paper 00** may be developed separately as a position paper, but only after its broad claims and literature framing are audited; **Papers 03 and 04** are mechanism *proposals*, not demonstrated-efficacy results, and are held; **Papers 05 and 06** stay historical until their claims are rechecked, and **no claim in either is currently strengthened by recent work — neither should be described as if it were**: Paper 05 must **not** be presented as evidence that the system prevents self-contamination, because its strict firewall claim conflicts with the measured sleep-sourced relations (disclosed as D2, quantified in `docs/GATE13-RELATION-SEPARATION.md`), and Paper 06's major lifecycle, stability and lineage claims remain unverified against the current evidence. Paper 01's core question is **"can developmental structure emerge in Organica 1?"**, answered with the negative external-task results as the boundaries of the answer, and it does not attempt to cover every probe. The Phase L characterization, the V1 synthesis and the audit artifacts are **research records, not manuscripts**; they are not additional papers in `papers/`. Paper 01 was renamed to match its revised title (`01_developmental_structure_formation.md`), and Paper 02 was revised to academic grade. The corpus is now organized as **two maps kept side by side** — a **research-program map** (theory / proposed mechanisms / empirical findings) and a **publication map** (which manuscript can make a coherent, evidence-backed contribution now) — so the layer map orients a reader without pressing every old manuscript or lab artifact into a paper. **Claims now carry one of four statuses**: *supported within this scope*, *mixed / context-limited*, *reversed*, and *not established / not measured* — a claim that was not established is **not** a claim that was refuted. Paper 01's central question was narrowed to match, and it no longer covers every probe. Paper 05 might instead become a paper about the **limits or failure** of cognitive isolation, but that would be a new thesis rather than a revision. | **"Drafted" is not "publishable", and an index that says so is part of the contribution.** The inventory is **seven manuscript files, zero published**, and the strongest near-term story is **the carefully bounded empirical record, including what failed and what remains unanswered** — not the theoretical corpus, which is a program rather than a set of publishable papers. Recording the plan in `papers/README.md` keeps the program from being mistaken for a codebase with some papers around it, and keeps a future session from re-deriving a sequence the owner has already decided. The accurate next milestone is **making the first two submission-ready**, not publishing them as they stand. |
| 31 | **The first audit of Paper 00 found two verified factual defects, and the first audit of Paper 05 found its core guarantee contradicted by the measurement.** Paper 00 said "this hierarchy spans **eight generations**" and then listed **nine** rows (G0–G8); the project's own architecture specification names it correctly — *"The 8 Generational Primitives"*, with **G0 = Experience** as the substrate and G1–G8 as the primitives. Paper 01 made the same error in its first draft and was corrected in the same pass. And Paper 00 stated **Law II** as an inviolable law — *"Every structure carries explicit, verified `parent_ids` traceable to G0 events"* — without the project's own disclosure (**D3**): the chain **terminates at Layer 1**, because concepts, phrases, loops and predictions are built from tags and the structure→event link exists only as counts. That is the same sentence that had to be removed from the README. Paper 00's abstract further claims the architecture can "spontaneously generate ... epistemic curiosity, counterfactual imagination, and prioritized empirical inquiry"; the **forms** exist (G5–G8), the **efficacy** does not — Phase K's matched mechanism ablations came back empty (`NO_QUESTIONS` −0.0095 [−0.0328, +0.0140]; `NO_FALSIFICATION` +0.0241 [−0.0048, +0.0495]; `NO_DREAMS` +0.0000 [0.0000, +0.0000], **all three intervals containing zero**), and **Law IV is never exercised** — experiments are generated, every consumer only prints them, and **no Question can ever close**. Paper 05's claim that its strict partition "ensures zero synthetic self-contamination across indefinite life cycles" is contradicted by the measured record: **17.9%** of the distinct supporting transitions behind reported beliefs (802 of 4,481) are self-sourced, and **43.2%** of all distinct transitions the observer recorded are the organism's own output, entering the temporal substrate through the unfiltered lookback (D2). | **A position paper is audited against the code, not against the prose.** The two documents most likely to be circulated are the two least checked against the engine, because neither is a measurement record and so neither is covered by the harness — and the first audit finding is usually a count or a law the record already contradicts, because those are the claims a reader cannot check for themselves. Paper 00's remaining broad claims and its literature framing are **still unaudited**, and Paper 05 may need a **new thesis** (the limits of cognitive isolation) rather than a revision. |
| 32 | **The historical record was normalized to American English, and the change was proven to be spelling-only rather than promised to be.** **234 words across 25 files**, including the preregistrations, the measurement records and the frozen journal sections. Three independent proofs were run against `HEAD` for every changed file: **(1) non-target content byte-identical** — every British-or-American target word replaced by the same token, so only the non-target bytes and the token positions are compared; **(2) the sequence of numeric literals identical** — no number changed, moved, appeared or disappeared; **(3) structure identical** — same count of headings, table rows, list items and lines. All three pass on all 23 changed files. Inline code spans were never rewritten, so no identifier, path, tag, test name or constant was touched. | **A verifier that reuses the writer's parser inherits the writer's bug.** The first pass reported *"remaining: 0"* — and it was wrong by 88 occurrences, because the sweep and its check shared a document-wide code-span regex that mis-aligns when backticks are unbalanced across a line, so prose was skipped and then not counted. The bug was found only because a **second, differently implemented** check — a raw-text scan with no span logic at all — disagreed with the first. **A check that cannot disagree with its own writer is not a check.** The fix was per-line backtick pairing (correct for balanced lines) plus the raw scan as an independent witness, and the final state is 0 remaining under a raw scan. |
| 33 | **Paper 00's audit was completed against the code, and the result is that **two of the six architectural laws are contradicted by the implementation**, one is untested on its own terms, and one is contradicted in direction. **Law III (Cognitive Isolation) is violated in exactly the way it was written to prevent**: the design law requires that *"temporal precedes matrices are strictly computed on non-sleep events"*, and the engine's edge recorder gates the **trigger** on `event_type != "sleep"` but not the **lookback window**, so sleep output re-enters `precedes` at **201×–341×** the world's own event count (D2). **Law V (EIG Attention) is wrong twice over**: formally, the engine applies `uncertainty * (1.0 + novelty)` to questions and `uncertainty * novelty` to dreams, so the single formula the law states is not what it computes for half its cases; empirically, the pre-registered prediction that development proceeds independently of EIG came back **REVERSED** — selecting the *lowest*-EIG experiment develops **more** than selecting the highest-EIG one. **Law IV (Grounded Dreaming)** is *mixed*: the confidence baseline **holds** (dreams are created at **0.04–0.06**, matching the design law), but the law's operative clause — a dream becomes a belief only if an external experiment generates the confirming events — is **never exercised**, because the engine generates experiments and never executes them, so no question can ever close. **Law VI** holds (thresholds **0.3** / **0.15**); **Law I** was not separately audited. The abstract's *"unbroken lineage to the raw experience"* is false (D3), and its claim of spontaneously generating *causal predictions* overstates the engine's own words — `memory.py` calls the temporal edges *"the organism's first approximation of causality"*. Two further items were corrected: **D4**, a new disclosed defect — the engine's stored `generation` field agrees with the specification for **G1** but is **one lower for every primitive from G2 upward**, and no document states the field's mapping; and the reference list, whose titles were the *old* names and whose *"Associated pre-prints"* label was false (the inventory is seven manuscript files and **zero published**). | **A constitution that has never been audited against its implementation is a description of an unimplemented architecture.** Two laws broken, one unexercised, one reversed — and every one of them was found by *writing the auditor*, not by arguing. That is the strongest evidence this program has produced for its own thesis, and it would have been invisible to any review that read the laws and the code side by side without measuring the code's behavior. **A law that cannot be violated is not a law; a law that has never been tested is not yet a claim.** |
| 34 | **A hand-transcribed table had drifted from its artifact in 18 of its 36 values, and the first repair made it worse before a mechanical check caught both.** The Pilot-0 score matrix in `docs/PILOT-0-INSTRUMENTATION-AUDIT.md` §2 declares its artifact as `docs/acquisition_single_seed_pilot.json`, but **18 of its 36 values disagreed with that artifact** in the fourth and fifth decimal of log-loss (the largest gap **6.7×10⁻⁵**). The artifact never changed — the same values are present in both commits that carried it (`89b0744` 2026-10-28, `4ceeab4` 2026-10-29), verified by extracting them at each revision — so the drift was in the **transcription**, not in the run. Six of the drifted values had been inherited by `papers/01_developmental_structure_formation.md` §4.7, and six more each by the five-row summaries in `docs/ACQUISITION-ENDPOINT-AUDIT.md`, `docs/ORGANICA-V2-DESIGN-BRIEF.md`, `docs/FACTS-SHEET.md` (AC7), `research-journal/phase_g_findings_20261021.md` and `research-journal/_journal_entry_51.md`. **No conclusion changed**: Organica's readout still loses to both baselines, the E-rem floor is still **0.403045**, the acquisition gate still fails and transfer is still *not measurable*. The correction was then applied *by hand* — and the hand-written repair **replaced the two reference rows (Bayes ceiling, base rate) with duplicate copies of cells 7 and 8**, so the table went from *18 wrong values* to *12 rows in which 2 were duplicates and 2 references were missing*. That defect was invisible to review: the table still had the right shape, the right headers and the right-looking numbers. It was caught only by running the table against the artifact mechanically. The table is now **regenerated from the artifact** rather than patched, and the check is permanent: the new `tests/test_readout_tables.py` asserts every document that restates this readout against the artifact, and includes four assertions that the checker itself can fail. | **A table transcribed from an artifact is a new claim and needs a mechanical check against that artifact** — the artifact is the machine-written record, a hand-copied table is a second claim that looks checked, and the prior verification script reported "0 failures" precisely because it never covered these cells. **A repair written by hand is another hand transcription, and it fails the same way.** |
| 35 | **The two active manuscripts were brought to academic grade, every citation in Paper 02 was verified against a primary source — and one candidate citation was dropped because it could not be read.** Paper 02's §2 now carries inline `(Author, year)` markers and a **References** section with **five** sources, each read on 2026-10-29: ACM Publications' *Artifact Review and Badging* v1.1 (for the **Results Reproduced** vs **Results Replicated** distinction, with the Publications Board's 2020 interchange of the two definitions recorded); Bau, Liu, Wang, Zhu & Torralba's *Rewriting a Deep Generative Model* (ECCV 2020, oral); Elhage, Nanda, Olsson et al.'s *A Mathematical Framework for Transformer Circuits* (Anthropic, 2021); the W3C **PROV-DM** Recommendation (Moreau & Missier, eds., 2013); and Shumailov, Shumaylov, Zhao, Papernot, Anderson & Gal's model-collapse paper (*Nature* 631(8022):755–759, 2024), **with its 2025 Author Correction disclosed** — which corrects a notation typo and does not touch the empirical claim Paper 02 cites. The Elhage paper's *faithful vs sufficient* distinction was **not cited**, because no readable copy of it could be found. Eight figures were then generated for Papers 01 and 02 by the new stdlib-only `benchmarks/figure_papers.py`, which **asserts every value it draws against the committed artifact**, bounds-checks its canvas, checks for text overflow, and **parses its own XML before writing**. | **Cite only what was read.** A reference list is a set of claims about what other people wrote; verified against the source it is evidence, verified against memory it is a guess with a citation attached. **A figure is a program that draws a claim, so it must be able to fail** — a figure that silently draws nothing, or that a renderer truncates at the first malformed attribute, is worse than no figure, because a missing figure is noticed. |
| 36 | **The first world edge was reported without the distribution beside it, and the distribution is what the claim needed.** The **rank** of the first world edge — **31** in the 1-tag stimulus, **30 / 18 / 53** in the 2-tag seeds, **16 / 8 / 8** after the LIMIT-4 separation — was reported on its own in the relation-separation record, the journal, the manual and the changelog. The ranks are correct. What was missing is what sits behind them: under the engine's own global count-ranked selection the world's 112 edges are **spread through the table, not clustered at its top**. The top 20 recovers **0–1** of them, the top 40 **0–2**, the top 80 **8–16**, the top 160 **36–55**, and the top **320** — about **16×** the engine's budget — **106–109** (`docs/gate13_allocation_rule.json`, 3 seeds); the five-seed capacity sweep puts cap 40 at **1–8 of 112** and the frozen cap of 20 at **0–3 of 112**. The figure *"cap 40 recovers 4–8 of 112"*, which had been quoted in correspondence, is **not** what the artifact says, and has been restated from it. **No measurement changed**, and the conclusion is unchanged — now stated with its distribution: **no frequency-based selection can find the world's relations**, because they are a third of the rows and are not clustered at the top of any frequency ordering. | **A first edge at rank *N* is one edge arriving, not a set arriving.** The same discipline as *a benchmark's headroom is not a learner's margin* and *the proximate bound and the deepest cause are different claims*: a threshold, a first case and a headline statistic are all single points, and **the set is the claim**. Reporting the first edge alone made the ranking problem sound nearly solved, when it needs roughly **16×** the engine's budget and a ranking rule the engine does not have. **A number that cannot be traced to an artifact is not a weaker claim — it is not a claim.** |
| 37 | **Paper 01's citations were verified against primary records, and one of its four methodological lessons is stated as the project's own rule with no external citation.** §4.1's curriculum-sensitivity framing and §5.4's four methodological lessons now carry inline `(Author, year)` markers, and the manuscript carries a **References** section with **seven** sources, each read on 2026-10-30: Bengio et al. (2009) for the definition of curriculum learning, Wang, Chen & Zhu (2021) for curriculum as a measured training strategy, Button et al. (2013) for the power result behind "a criterion that flips when n changes is measuring the draw", Simmons et al. (2011) for analytic flexibility inflating the actual false-positive rate, Jacobs & Wallach (2021) for the construct-versus-operationalization mismatch behind "an endpoint must measure the claim it is used for", Davis & Goadrich (2006) for the ROC–PR relationship on skewed data, and Saito & Rehmsmeier (2015) for the demonstration that a ROC curve's visual interpretability is deceptive on imbalanced data. The second lesson — compare against the strongest simple baseline and take the headroom from the ceiling — carries **no external citation by design**: it is this project's own rule and reports only Organica 1's own numbers. An **erratum** to Button et al. (*Nature Reviews Neuroscience* 14(6):451) was read and disclosed: it corrects the definition of *R* on page 366 and touches nothing cited here. | **"Cite only what was read" is a rule about the limit as well as about the citation.** Two of the seven sources were reachable only as their authors' abstracts, because the ACM Digital Library's full text is not retrievable in this environment; they are cited only for what those abstracts state, and that limit is written into the source notes instead of being left implicit. One candidate source could not be located in any bibliographic record and is therefore not cited. The project's own rule and the literature are kept distinct: a lesson that is the project's own is labeled as such rather than given a borrowed reference. |
| 38 | **A Layer-1 admission filter is not a filter on this engine: the temporal lookback includes the organism's own sleep rows, so changing what is admitted changes what will be admitted next.** The formation-utilization timing pass measured the four arms' temporal graphs on one seed. On T2, **32** edges differ (**374** vs **380**), the permitted candidate streams differ on **59 of 131** cycles, first at cycle 6, with **248** permitted candidates missing and **172** extra over the run. On T1, **21** edges differ (**362** vs **351**), **107 of 160** cycles differ, first at cycle 40, with **274** missing and **120** extra. The mechanism is `_record_temporal_edges`: it reads the last three **events** (`SELECT tags FROM events ORDER BY time DESC LIMIT 3`), and sleep payloads are events. Their extracted tags enter `precedes`, so arm C's own admitted predictions become evidence for the next cycle's admission. The protocol's arm table says *"all other layers and all counts are untouched"*; that is false, B versus C is not the same evidence with different admission, and a C advantage could be **self-sourced support** rather than utilization. The campaign was therefore not authorised by the timing pass. | **Before comparing two arms that differ inside a layer, check that the layer's input is not derived from its output.** This is the same defect as the audit trace's D2 (a lookback with no event-type filter) appearing where it does real damage: not in a trace, but in the experiment's independent variable. **A perturbation of a layer's input is not a perturbation of its output**, and the difference is invisible in the arm table because both arms are described by what they admit, not by what they read. **A ten-minute timing pass that finds this is worth more than a five-hour campaign that reports a confounded number** — which is why the protocol required the timing pass before the campaign, and why the pass reports a diagnostic it was not asked for. **Amended 2026-10-30 (protocol §12).** Arms C and S now read arm B's per-cycle temporal graph, captured at the start of each sleep cycle; A and B are unchanged and `organica/` is untouched. Audit **A8** gates that the graph each admission arm actually read and its eligible pair stream equal B's at every cycle; the amended timing pass passes A8 on T2 (**131** cycles, **75,488** pair checks) and T1 (**160**, **80,200**). What the amendment fixes is the feedback into Layer 1; what it does not fix is B's own self-sourced evidence, and C is now a counterfactual trajectory on B's evidence — so a C result is admission filtering at fixed evidence, not "the engine with this filter installed". |
| 39 | **Correct structure is necessary but not sufficient: with the generator's support admitted at Layer 1, the organism still loses retention and transfer to the best simple baseline — and the protocol's "data-only" label does not describe the T2 bar.** The 30-seed campaign (60/60 units ready, all eight audits pass or N/A) measured C at **0.2365 / 0.2355 / 0.3892** on T1 and **0.3643 / 0.3632 / 0.3502** on T2 (retention / transfer / revision). The pre-committed decision rule, d = bar − arm over 30 paired seeds with a 98.33 % interval, returns a **loss** on retention and transfer on both tasks: T1 **−0.0267 / −0.0262**, T2 **−0.0230 / −0.0227**. It returns a **win** on T1 revision (**+0.1002**) and a **tie** on T2 (+0.0007). B also loses transfer on both tasks (−0.0296 / −0.0795), so §7's "both lose" cell fires on both: **"utilization fails even with correct structure" → V2 targets the use path (retrieval / activation / readout)**; the summary claim is **not supported**, and the failing limbs are transfer and retention. The label is not the magnitude: C closes **65.2 %** of A's transfer gap on T1 and **79.9 %** on T2 (retention 65.2 % / 79.6 %), and improves over B by 0.0034 / 0.0568 nats. The T2 bar is the **cell-level latent-state counter**, which is **granted the latent cell structure** (`fit_cell_counter` takes `tag_to_cell` from the generator), so it is **not** the "strongest data-only learner" the protocol names. That is a naming defect, not a deviation — the counter is a declared member of the statistical-learner family — and the verdict survives without it: post hoc, C still loses T2 transfer to Replay by **0.0208** [−0.0224, −0.0192] and to the bigram by **0.0187** [−0.0205, −0.0168], while on T1 the bar is Replay and C loses by 0.0262. | **A pre-committed label and its magnitude are different claims, and the label must not stand in for the effect size.** "Utilization fails with correct structure" is the protocol's verdict; the same run shows C closing two-thirds to four-fifths of A's gap and winning revision on T1. A reader who takes the label alone over-reads it; a reader who takes the closure alone under-reads the loss. Report both, in that order. **And a comparator's name is part of its definition:** calling the T2 bar "data-only" widens the claim, because the cell counter is handed the latent cell map. The check that makes the label safe is the sensitivity against the genuinely data-only comparators, and it is post hoc — say so. **No V2 build is authorised.** See `docs/formation_utilization_results.md`, protocol §7, journal §65. |
| 40 | **The Gate 13 precision ceiling was 0.3438, not 0.3443, and the repair a string replace would have made would have corrupted eight real measurements.** The maximum of the **36** precision measurements in `docs/gate13_allocation_rule.json` is **0.3438** (seed `20261101`, global rule, `k=160`, coverage **0.4911**); the ceiling had been quoted as **0.3443** in the campaign artifact's own A3 blocks, in the harness constant that gates them, in the figure generator, in a test and in fourteen documents. The correction changed **no verdict** — the highest arm-B Layer-1 precision on T2 is **0.3394**, below both band edges — but `0.3343` is both the derived lower band edge and four units' *measured* precision, and six more measurements merely begin with `0.3443` or `0.3543`. | **A hand-transcribed ceiling becomes a ceiling everywhere it is quoted, including inside the figures, and a number that merely begins with the same digits is not that number.** Write a number from its artifact once, mechanically; when correcting a published artifact, edit **by field path**, keep the original beside it, and compare every measurement before and after. `AGENTS.md` rule 29. |
| 41 | **The eight failing seeds are a hash-order artifact, and the campaign's candidate population is now named.** The campaign artifact carries no candidate ID at all — only a per-type table of `unique_count` and `edge_weight` — so the campaign side had to be regenerated: the harness is re-run under each hash seed and the run whose fingerprint equals the campaign's IS the campaign's population. The engine is byte-identical to the state the campaign ran against (`git diff a95305d HEAD -- organica/` is empty), and under the committed code the campaign's own table is reproduced **exactly** on **8 of 8** failing seeds by varying only `PYTHONHASHSEED`. Across them **252** candidate IDs are the campaign's and not ours and **288** are ours and not the campaign's, and the two populations part company at cycle **2** (T1/20261129); cycle **3** (T1/20261128); cycle **5** (T2/20261118, T2/20261120, T2/20261121, T2/20261123, T2/20261130); cycle **11** (T1/20261125). | **The reconstruction environment, not the code, was responsible** — the campaign ran with ten worker processes and therefore ten hash seeds, and the audit pinned one. A candidate population is not reproducible without its hash seed, and an artifact that records no identity cannot be reconciled with a reconstruction except by regenerating the side that lacks it. A cached run that disagrees with an independently recorded reconstruction is not a measurement and must be recomputed, not read. `AGENTS.md` rule 29. |
| 42 | **The candidate pool at the divergence cycle is now named, the capture is addressed by the engine's own cycle markers, and at that cycle the two sides no longer hold the same set of candidates.** The membership audit found *where* the two populations part company and the 4,000-row window it captured could not say *what was in the pool* there, because that window is a snapshot of the read-back near the arm's snapshot point while the divergences are at cycles 2–11. The new instrument captures the window at the cycle **before** the divergence, and the capture is not addressed by assumption (**corrected 2026-11-01:** it was described as the divergence cycle itself, but the audit's `first_cycle` is a zero-based index and window index *i* is engine cycle *i*, so the pools are one cycle early; the re-measurement at the divergence cycle and the cycle before it is in the 2026-11-01 revision row and in `docs/divergence_cycle_capture.json`): the engine stores one `sleep:meta` event per cycle, so the newest marker in the i-th window must carry cycle *i*, and a window that cannot show that is refused rather than reported. Across the 16 arm-pairs, the two sides hold the **same set** of candidate IDs at the divergence cycle in **0** of them and the **same order** in **0**: at the cycle where the admitted streams part company, every arm-pair differs in membership. **Corrected 2026-11-01:** the figures this finding shipped with — the same set in **11** of 16, and on **3** seeds the same set *and* order while the admitted stream still differed — were measured one cycle **before** the divergence, because the audit stores `first_cycle` as a zero-based index and the capture read window index *k* as cycle *k*. The measurement was real; the cycle it was attributed to was wrong. | **A window is only evidence of the cycle it can prove it is in — and a set is not a sequence.** The engine's candidate list is assembled from sets of strings (`organica/sleep.py:1201`, `:1223`) and its window is ordered by timestamp with no rowid tiebreak (`organica/memory.py:390`), so the order is part of what the organism receives. The membership audit was right that the count held and the identities changed; the 2026-10-31 capture read one cycle early and so reported that the identities *usually hold* and only the order changes, which is false at the divergence cycle. `AGENTS.md` rule 29. |
| 43 | **The next instrument is planned and its hypothesis is pre-registered: the divergence may enter through order-sensitive candidate construction, at a site the instrument has to locate.** §72 appeared to end with a negative result about the pool — on 3 seeds the two sides' pools at the divergence cycle were identical in set **and** order while the admitted stream still differed — so the difference seemed to arise inside the cycle, in a step nobody had looked at. **That premise was an artifact of the cycle base (corrected 2026-11-01):** those pools were read one cycle before the divergence, where being identical is possible; at the divergence cycle itself no arm-pair holds the same set. The instrument this finding planned was still worth building and was run, but it was planned to explain a difference in the wrong place. Reading the frozen source found four order-dependent sites: `_score_tags` iterates a set of strings and stable-sorts on a tying integer; the temporal graph is read with `ORDER BY count DESC` and no tiebreak over a table with no index on `count`; `_build_predictions` stable-sorts on `temporal_count` alone; and `_build_anomalies` picks the anomaly's expected tag among equal counts by graph order, so that one changes a candidate's **content**. The predictions truncation does **not** bind — the harness overrides that cap — and identity is not at risk, because `_make_id` is a SHA-256. | **A stable sort on a key that is not a total order inherits whatever order its inputs arrived in, and an input order nobody specified is an order nobody chose.** The hypothesis, two forms of it, three predictions, three falsification criteria and four controls are committed in the brief and in journal §73 **before** any run, so that they can be checked against what the instrument found. A refutation is a result, not a failure, and the brief says so. `AGENTS.md` rule 29. |
| 44 | **The construction-order experiment ran, and its own control stopped it before it could speak: H2 is untested in an admissible form.** Arm A observed every builder on the eight failing seeds at their two hash seeds, and found that the first builder whose assembled sequence differs is `_score_tags` at **cycle 1** on **8 of 8** seeds — and on the **control** seed too. That is a property of the code (`_score_tags` iterates a set of strings and stable-sorts on a frequency that ties constantly), not the site where the two sides part company. **Corrected 2026-11-01:** the admitted prediction streams first differ at the membership audit's divergence cycle **itself** on 8 of 8 seeds. The earlier text reported a **+1 offset** and explained it as a difference of cycle numbering between the two instruments; that was wrong. The audit stores `first_cycle` as a **zero-based index** and both instruments number cycles from one, so the offset was the index base, not a property of the organism. The metric that appeared to show the delay (`admitted_same_at_divergence`) read the stream one cycle *before* the audit's divergence, where the audit's own definition makes the streams identical — a field that could not be false. It is replaced by `audit_cycle_reproduced`, which can. The surviving statement is **reproduction of the audit's cycle on fresh captures**, and it is analytical reproduction, not an independent replication. Arm B canonicalised the temporal graph and the composites in the harness only: **0 of 8** seeds became hash-seed invariant (P3 not met, **F1 fired**) and the control seed's builder sequences changed at a fixed hash seed (**F2 fired**), so by the pre-registration no conclusion may be drawn from Arm B. The reason is now identified: the first order channel is `_score_tags`, upstream of both sites the intervention touched. **C1 as pre-registered FAILED** (corrected 2026-11-01): it required the control seed's *assembled lists* to be identical at every hash seed, which is P2, and P2 is **not met** — the control's builders differ too, from cycle 1. This finding first reported C1 as held, and as the sharpest positive result, by substituting a different quantity: the control's *admitted stream*, which is identical at every cycle across hash seeds 0 and 2 while its builders differ. That observation is real and stands, but it is a post-hoc reading of a quantity the control did not specify, on one seed at one hash-seed pair, and it is not a passed control. No engine file changed; Organica 1 stays frozen at `v0.9.0`. |
| 45 | **The next instrument is planned and pre-registered: the question is now *when* the candidate populations first differ, not why identical pools admit differently.** The 2026-11-01 correction removed the observation the construction-order experiment was pre-registered to explain — at the divergence cycle the two sides hold the same set in **0 of 16** arm-pairs — so the surviving question is where the membership difference first appears. The capture already brackets it: **11 of 16** arm-pairs hold the same set at *k−1* and a different set at *k*, so onset lies in **(k−1, k]**; **5** already differ at *k−1* (T1/20261125 both arms, T2/20261120 both arms, T2/20261121 arm B), so onset there is at or before *k−1* and nothing measured bounds it. The instrument walks back from *k* to cycle 1 per arm, inherits the marker-witnessed addressing rule, reports a refused window as **not measured**, and records what entered and left at the onset cycle. Two predictions, four falsification criteria and four controls are committed in the brief and in journal §75 **before** any run — a third prediction was withdrawn before the run because it could not fail (the bracket plus integer cycles already fix onset at *k* for the eleven bracketed arm-pairs), which is the same defect the correction pass removed from the mechanism instrument. | **A change of question is a result, and it must be pre-registered like any other.** The bracket is what makes the new question cheap: eleven arm-pairs need one cycle checked, five need a walk-back. F1 — reproduce the corrected capture's cycles *k* and *k−1* before reading any onset — exists because an instrument that cannot reproduce the measurement it generalises is measuring itself. `AGENTS.md` rules 11 and 29. |
| 46 | **The membership onset was measured and its own control fired against it: the pools first differ by insertion, never by replacement, but the attribution to the divergence does not hold.** 18 runs, 0 cached. **F1 passed on 16 of 16 arm-pairs** — cycles *k* and *k−1* reproduce the corrected capture's values and IDs. Of the **five** search arm-pairs, **four** reached onset strictly before *k−1* (T1/20261125 both arms at cycle **3** against *k* = 12; T2/20261120 both arms at cycle **4** against *k* = 6), and the fifth (T2/20261121 arm B) at cycle 5 = *k−1*. **P3 met**: every onset is at cycles 3–6, none at cycle 1. Across all 16 arm-pairs **zero candidates left** a pool at its onset — each divergence is the pool gaining candidates. **C1 was void and has now been run properly:** the audit's pair is seed 0 twice, so the control was re-run at **seeds 0 and 1** (2 runs), and the control seed's own pools **differ** — 3 of 24 measured cycles, arm B, cycles 10–12. **F2 therefore fires: the instrument is inadmissible by its own pre-registration**, and the onset numbers and the insertion observation may not be attributed to the divergence. The only residue is a difference in *pattern* (control at 10–12 on one arm, failing seeds at 3–6 on both), which is a hypothesis for a new pre-registration, not a finding from this run. | **A check that cannot fail is not a control, and this one was found by running it.** The onset numbers are real; the missing gauge is the reason they are reported as a characterisation and not as a divergence-specific result. **Divergence is insertion, not displacement** — which is a different claim from the withdrawn order-only reading and does not restore it. `AGENTS.md` rules 13, 25 and 29. |
| 47 | **Decide the block's size, now that the sign resolution is computed** | The computation (`docs/sign_resolution_structure_behavior.json`) says a rank relation of 0.50 needs **48 worlds per configuration** to clear the 0.90 bar - **144 runs** across the three configurations. 0.70 needs 21, 0.60 needs 32, 0.40 needs 79, 0.30 needs 144. The protocol may not name a smaller n without either shrinking the claim to a larger relation or lowering the bar, both of which are protocol changes made before the block opens. Authorize the size or change the claim; no seed is allocated until one of those happens. | the owner | days |
### 8.1 The cold-start study

**The question:** *would G1 have eventually built out the generations above it, with no assistance and no code changes on our end?*

**The answer, measured:** **mostly yes — and one crucial no.**

**Method.** `benchmarks/cold_start.py` runs the *unchanged* engine under eight levels of assistance. Ablations are applied in-process (subclassing and rebinding), so the engine's source is never edited and the running study is unaffected. 40 cycles per condition. The most unassisted condition, `real_git_history`, feeds the organism this repository's own commit messages — nobody designed those to cooperate.

**Results** — sleep cycles until each generation first appears (`—` = never):

| Condition | G1 | G2 proc | G3 | G4 | **G5** | G6 | G7 | G8 |
|---|---|---|---|---|---|---|---|---|
| `baseline` (seeded, engineered) | 1 | 2 | 2 | 2 | **2** | 2 | 2 | 2 |
| `no_branch` (the original stream) | 1–5 | 6 | 6 | 4 | **never** | 2 | 2 | 2 |
| `cold_start` (no seed, 1 event/cycle) | 5–8 | 9 | 9 | 8 | **10** | 7 | 7 | 7 |
| `cold_start_unbranched` | 6–37 | never | never | 18 | **never** | 10 | 10 | 10 |
| `real_git_history` (real commits) | 4–13 | 14 | 14 | 6 | **never** | 5 | 5 | 5 |
| `no_truncation` (cap 15→200) | 1 | 2 | 2 | 2 | **2** | 2 | 2 | 2 |
| `no_dev_stopwords` | 1 | 2 | 2 | 2 | **2** | 2 | 2 | 2 |
| `wide_lookback` (3→30) | 1 | 2 | 2 | 2 | **never** | 2 | 2 | 2 |

**What bootstraps on its own:** G1 (concepts, predictions, loops) within 4–13 cycles on the real-commit stream and 5–8 on `cold_start`; G2 processes and G3 workflows at cycle 14 on the real-commit stream and cycle 9 on `cold_start`; G4 (hypotheses) by cycle 6; G6/G7/G8 (dreams, investigations, experiments) by cycle 5. These are genuine emergences — no seed, no engineered structure, no code change.

**What never emerges on an unengineered stimulus:** **G5** — and only G5. G2 processes and G3 workflows do appear there, at cycle 14, and G4 at cycle 6. The earlier claim that G2, G3 and G5 all never appear was measured on 2026-10-21 and no longer reproduces; see the disclosure below.

**The mechanism, supported causally.** Confidence is a *share*, not a probability:

```python
confidence = support / (support + contradiction)   # organica/sleep.py:1402
```

`contradiction` is the subject's *total outgoing flow minus this hypothesis's support*, so a hypothesis is measured against its **siblings**. The more successors a subject has, the more every minority expectation is diluted — and below `DEATH_THRESHOLD = 0.15` with ≥3 observations, it is pruned permanently.

The `wide_lookback` row is the evidence: widening the temporal lookback from 3 events to 30 — **changing nothing else** — destroys G5 completely, while `no_truncation` is *identical* to baseline and `no_dev_stopwords` keeps G5 at cycle 2 with a smaller population (1 theory / 1 question against 2 / 2). More context → the organism is *less* able to hold two beliefs at once. That is the opposite of how human memory behaves, and it is a property of the formula, not of the data.

*(This also corrected an earlier hypothesis of ours: the alphabetical truncation of hypotheses was **not** what blocked G5. `no_truncation` falsified that, and the journal entry was corrected in place.)*

**Three things this means for you:**

1. **The organism is not a stub.** G1–G4, G6, G7 and G8 bootstrap themselves from real, uncooperative input, with G2 processes and G3 workflows arriving at cycle 14 on the real-commit stream. The core claim of the project holds for every generation below G5.
2. **G5 currently requires a stream that contains a branch point.** It appears in the study because the study stream was *engineered* to hold two competing expectations about one subject, and it appears unseeded at cycle 10 in `cold_start` on the same engineered stream. On the one unengineered stimulus it never appears — and widening the lookback on an engineered stream destroys it, so the confidence formula is a live constraint on holding it.
3. **The fix is small, and it is the direction you asked for.** A Laplace/Beta-smoothed posterior instead of a share: `confidence = (support + α) / (support + contradiction + α + β)`. It is *simpler* than the formula it replaces, it keeps a genuinely split belief alive regardless of how many siblings the subject has, and it makes the lookback width irrelevant — the human-like behavior the project is aiming at. **It is a proposal, not a change**: it is a cognitive change, and Phase A freezes those ([§7.2](#72-decide-this-week), decision #4).

**The caveat, stated plainly.** `real_git_history` used only **11 commit messages**. It is under-powered: it shows the result is not a one-line artifact, but it is not a general proof about arbitrary real-world streams. Before this goes in a paper, that condition should be re-run on a much larger real corpus.

**The other half of the answer — the self-build loop.** G8 experiments are *generated but never executed* (finding 9). Until something runs the probe and feeds the result back, the organism cannot create its own branch points, and the only source of branch points is the stream you designed. An **experiment executor** closes that loop and is the other half of "would it have built the next generations itself" — decision #7 in [§7.2](#72-decide-this-week).

**Disclosure — the table was re-measured on 2026-10-30.** The `cold_start` row previously read `never`, and the whole table came from `python benchmarks/cold_start.py --cycles 40` run on 2026-10-21. That artifact is no longer reproducible: on every engine retrievable from this repository — `v0.6.0` (tagged 2026-10-23), `v0.9.0`, and `HEAD` — `cold_start` reaches G5 at cycle 10, on Python 3.13.15 and 3.14.7, under repeated runs and varied hash seeds. Parameters, seededness, the event stream, the benchmark schema and the interpreter were each checked and ruled out as causes. The commits between 2026-10-21 and 2026-10-23 were never published — `master` history was rewritten on 2026-10-29 — so the transition cannot be bisected, and whether the 2026-10-21 measurement was correct for a then-current engine or was itself anomalous cannot be decided from the surviving evidence. The artifact and this table were therefore re-measured on the frozen engine, and the change is disclosed here rather than applied silently.

**Where the evidence lives:** `benchmarks/cold_start.py`, `docs/cold_start.json`, journal [§14](../research-journal/phase_g_findings_20261021.md).

### 8.2 The ablation study: which mechanisms are actually doing the work?

The cold-start study asks *"how much help does it need?"*. The ablation study asks the complementary and less flattering question: *"which parts are load-bearing, and which are ornament?"*

Eleven conditions — a full-system reference (`O_FULL`) plus ten ablations, each removing or replacing exactly one mechanism, all applied **in-process** so the engine source is never touched. Metrics: predictive accuracy (PA), information preservation (IP), structural compression (SCR), survival selectivity (SS), lineage completeness (LC), contradiction density (CD), cross-domain transfer (CDT) and novel structure rate (NSR).

Two of the specified metrics — `CY` (questions resolved ÷ generated) and `EIG*` (entropy removed by an experiment) — are **structurally unmeasurable** here: nothing resolves a Question and nothing executes an experiment, so both are identically zero for every condition including the full system. They are excluded from the aggregate rather than zeroed, because zeroing them would look like a measurement and is not one. The Designer Surprise metrics need your protocol before a run and are pending.

**Verification comes before interpretation.** `benchmarks/ablation_verify.py` runs first and asks, for every condition, *"did the ablation actually change the organism?"* — the perturbation census (which populations changed), the Random Curiosity overlap and score-distribution check, and a contradiction-provenance analysis that re-runs the same conditions with the Layer-4 hypothesis cap removed. A condition that changed nothing was not an ablation, and saying so before reading the outcomes is the difference between a result and a coincidence.

**The pre-registration is amended, not rewritten.** `docs/ABLATION-PREREGISTRATION.md` records the predictions written before the run *and* six measurement defects found afterwards — including one that had inverted a prediction. All six are disclosed in place; §4's predictions were never revised.

**What the study found.** Nine findings, in plain words. Full evidence and reasoning: journal [§17](../research-journal/phase_g_findings_20261021.md).

| # | Finding | What it means for you |
|---|---|---|
| 1 | **Sleep and the graph are the architecture.** Removing either one produces **zero** structures of any kind. | The two foundations are real and load-bearing. |
| 2 | **Nothing leaks in.** With the graph edges removed, not one concept, loop or hypothesis emerges. | The contamination check passes cleanly. This is the most reassuring result in the study. |
| 3 | **Lineage is governance, not cognition.** Stripping every parent link changes *nothing* measurable except Lineage Completeness (1.000 → 0.000). | Law II is what makes the other claims checkable. It is not a cognitive mechanism, and the design documents should stop implying otherwise. |
| 4 | **Curiosity does not drive belief formation — it drives action on belief.** Removing it *raises* hypotheses (13→15), theories (1→3) and contradictions (12.2→17.7); only investigations and experiments vanish. | The belief layer never consults the curiosity layer. Curiosity is an output channel. |
| 5 | **Removing falsification does not cause runaway belief growth — it freezes the organism.** Hypotheses fall 13→7, theories to zero, contradictions collapse from 61% of cycles to 5%. | Our pre-registered prediction was wrong, and the real result is better: forgetting is load-bearing for holding a *current* view. Stale beliefs crowd out live ones. |
| 6 | **Dreams are structurally load-bearing for everything above Layer 5** — yet score "cosmetic". Removing them leaves 6 hypotheses, no theories, no questions, no investigations, no experiments. | The aggregate score is blind to population size. This is why the population table is part of the result. |
| 7 | **Removing the hypothesis layer produces MORE theories and LESS provenance** — 6 theories instead of 1, with lineage dropping to 0.641. | A system without lineage can produce more and prove less. |
| 8 | **Questions are not the gateway to inquiry. Dreams are.** Remove Questions and investigations and experiments carry on unchanged, because Layer 7 draws on dreams as well. | **Our pre-registered prediction was falsified.** Questions are not load-bearing for inquiry. |
| 9 | **Random curiosity performs identically to EIG curiosity** on every metric that can currently be measured — identical predictive accuracy, slightly higher aggregate, smaller organism. | **But the metric that would separate them cannot be computed without an experiment executor.** This is a blind spot with a known cause, not a null result. |
| 10 | **Which beliefs are allowed to disagree is decided by alphabetical order.** Layer 4's 15-hypothesis cap is applied *after* sorting by subject name, so `high_structural_significance` markers (subjects like `developer`, `engineer`, `report`) fill the budget and crowd out the genuine belief pairs that carry contradiction. | **Corrected 2026-10-23 — the rule is wrong but currently inert, and it was not the cause of Finding D.** See [§8.3](#83-the-instrumentation-audit-where-the-pressure-really-is). The sort is still a defect worth fixing: deciding what to keep by sorting strings is not deciding by merit. |

**The verification stage confirms these are real perturbations, not vacuous comparisons.** Every condition changed the organism. For Random Curiosity specifically: the two policies overlapped on only **1 of 9** final selections (Jaccard 0.111), and EIG's *top-k precision* was **1.000** — it picked the five highest-curiosity candidates **every single time**, against random's 0.584, with a top-decile hit rate of 48% against 27%.

That matters for how finding #9 should be read. **The EIG implementation is not broken — it is a perfect ranker.** It selects demonstrably better candidates than random and the organism's predictive accuracy does not move, because the layers above curiosity produce candidates that nothing consumes. "The attention economy works perfectly and buys nothing measurable" is a sharper claim than "it doesn't work", and it says exactly where to look next.

The same verification also answered the question finding #5 raised about contradictions, and it produced finding #10: the full system generates contradiction counts in the **thousands** (up to 6,391 on a single hypothesis), so contradiction *generation* has nothing to do with falsification. What the No-Falsification condition suppresses is contradiction *survival*.

> **Correction to the paragraph above (2026-10-23).** It previously ended "…and the cause is Layer 4's alphabetical truncation, not the removal of extinction." **That was wrong.** The verification census shows `D` had `G2 processes` = 0 **and** `G3 workflows` = 0. Hypotheses are built only from workflows, processes and meta-concepts, so `D`'s all-marker population is fully explained by the destroyed Layer-2/3 layers — no truncation was involved. The alphabetical rule is a real defect, but the cap binds in **0 of 600** cold cycles, so the rule currently changes nothing at all. See [§8.3](#83-the-instrumentation-audit-where-the-pressure-really-is).

**Two of our predictions were falsified by the run** — #5 and #8. Both are recorded as such in the pre-registration rather than quietly restated. That is the point of writing predictions down first.

**A blind spot worth knowing about:** the aggregate `ES` score does not count structures. Condition #6 removed most of the organism and still scored −3.0 ("cosmetic"). Read the per-metric deltas and the population table together; treat `ES` as a convenience index over six of the eight computable metrics.

**One number to carry away:** cross-domain transfer is **−0.486** across 12 domain pairs, with a mean shared vocabulary of **0.17 tags**. Organica cannot carry knowledge from one domain to another, because its substrate is lexical co-occurrence and there is no representation above the tag that could cross a vocabulary boundary. That is the sharpest evidence that the current architecture is a knowledge-compression engine rather than a general learner — and it is exactly where the next architectural work belongs.

**The careful summary of the transfer evidence (2026-10-26): no positive transfer has been demonstrated, and the measured cross-domain result was negative.** That is a measured negative on **one** axis. **Other forms of transfer remain untested** — so this is not a general finding that Organica cannot transfer, and it should not be quoted as one.

**The single highest-value next step** is the **experiment executor**. It unblocks four things at once: it makes EIG testable against random curiosity (#9), it makes `CY` and `EIG*` measurable so the aggregate stops being blind, it lets a Question actually close, and it is the missing half of the self-build loop. Everything else in the remedy list is downstream of it.

Full protocol, predictions and disclosure: **`docs/ABLATION-PREREGISTRATION.md`**. Results: **`docs/ablation_study.json`** and **`docs/ablation_verification.json`**, re-run on the fixed substrate as **`docs/ablation_study_postfix.json`**, and compared before/after in **`docs/v1_impact.json`** (the audit that classifies each V1 conclusion as survived / changed magnitude / reversed, and each *interpretation* as survived or **retracted**). What emergence means and which levels Organica can evidence: **`docs/EMERGENCE-CRITERIA.md`**.

### 8.3 The instrumentation audit: where the pressure really is

The ablation campaign produced **byte-identical results for five very
different upstream threshold settings.** That has two possible causes and
they demand opposite responses:

* (a) the parameter genuinely does not matter, or
* (b) **the observation channel is saturated** — the parameter changes the
  candidate pool, but the layer's output cap discards the change before it
  can be seen.

(b) is far more likely, and it would have made a whole matrix of
experiments measure bottlenecks instead of cognition. So before running
the Tier-1 matrix, the machinery itself was measured.
`benchmarks/instrumentation_audit.py`, 400 cycles per arm, observation only
— the engine is subclassed, never edited.

#### Retention pressure: `pool_size / cap`

`< 1.0` no pressure · `1–2` weak · `2–5` useful · `> 5` strong.

| Layer | cap | pool mean | p95 | pressure mean | pressure p95 | |
|---|---:|---:|---:|---:|---:|---|
| loops | 15 | 936 | 936 | **61.1** | **62.4** | hard over-truncation |
| predictions | 20 | 598 | 621 | **29.9** | **31.1** | hard over-truncation |
| anomalies | 10 | 292 | 309 | **29.2** | **30.9** | hard over-truncation |
| investigations | 5 | 8.8 | 11 | 1.77 | 2.20 | useful |
| processes | 10 | 11.8 | 13 | 1.18 | 1.30 | weak |
| dreams | 8 | 8.3 | 12 | 1.04 | 1.50 | borderline |
| experiments | 5 | 4.9 | 5 | 0.98 | 1.00 | none |
| workflows | 10 | 9.1 | 10 | 0.91 | 1.00 | none |
| meta_concepts | 15 | 9.0 | 9 | 0.60 | 0.60 | none |
| **hypotheses** | 15 | **5.3** | 8 | **0.35** | 0.53 | **none** |
| questions | 6 | 1.2 | 3 | 0.19 | 0.50 | none |
| theories | 8 | 1.2 | 3 | 0.14 | 0.38 | none |

**The organism is starved, not selective.** Layer 1 throws away ~99% of its
own candidates; Layer 4 has 5–8 beliefs for 15 slots. The caps are
mismatched.

#### The funnel, measured end to end

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

Every arrow is a cap, and **every cap retains by a popularity rule** — raw
temporal count for predictions, strength for loops, dominance ratio for
anomalies. The alphabetical hypothesis rule is the same family of defect,
three layers downstream, and it is invisible only because there is nothing
left to choose between.

#### The parameter influence map — 8 of 14 knobs do nothing

| Verdict | Parameters |
|---|---|
| **DECISIVE** (changed final outputs) | `DEATH_THRESHOLD` · `STABLE_THRESHOLD` · `MAX_PROCESSES` · `MAX_PREDICTIONS` |
| **POOL_ONLY** (changed the pool; the cap hid it) | `PREDICTION_MIN_COUNT` · `LOOP_MIN_STRENGTH` |
| **INERT** (changed nothing at any level) | `MAX_HYPOTHESES` · `MAX_WORKFLOWS` · `MAX_META_CONCEPTS` · `WORKFLOW_MIN_MATCHED_METAS` · `META_CONCEPT_MIN_REFS` · `CONCEPT_MIN_DEGREE` · `CONCEPT_MIN_REACH` · `PHRASE_MIN_CLUSTERING` |

`MAX_HYPOTHESES` — **the parameter the whole P1 experiment was built
around — is INERT.** Raising it 15 → 40 changes nothing at any level. A
parameter that never changes an output should not have a row in an
experiment plan.

#### The effective world

The temporal world is **42 tags** (mean 41.8, median 42), with a top-10
tag share of 0.44 — but only **~9 tags reach the composition layers**, and
that is a *consequence* of the Layer-1 caps: meta-concepts are composed
only from candidates that survived them. The narrow world is downstream of
the over-truncation, not an independent fact about the stimulus.

#### The G1–G4 perturbation ladder

```
G1  the ablation perturbed the code path
G2  the ablation perturbed the candidate pools
G3  the ablation perturbed the final outputs
G4  the ablation perturbed the developmental metrics
```

| Cond | Intervention | G1 | G2 | G3 | G4 | Reading |
|---|---|:--:|:--:|:--:|:--:|---|
| A | No Sleep | ✅ | ✅ | ✅ | ✅ | foundational — everything to zero |
| **B** | **No Lineage** | ✅ | ✅ | **❌** | ❌ | **the control.** Populations *identical*; the only metric that moved is the one measuring the thing that was removed. Every cognitive delta is exactly 0.000 |
| C | No Curiosity | ✅ | ✅ | ✅ | ✅ | passes G4, but **in the wrong direction** — removing EIG raises theories 1→3 and kills both output layers |
| D | No Falsification | ✅ | ✅ | ✅ | ✅ | freezes rather than bloats |
| E | No Dreams | ✅ | ✅ | ✅ | ✅ | collapses processes and workflows to zero |
| F | No Hypothesis Layer | ✅ | ✅ | ✅ | ✅ | 6 theories instead of 1 |
| G | No Questions | ✅ | ✅ | ✅ | ✅ | the gateway is dreams, not questions |
| H | Random Curiosity | ✅ | ✅ | ✅ | ✅ | Jaccard 0.111 vs EIG — different selection, no developmental gain |
| I | Random Sleep | ✅ | ✅ | ✅ | ✅ | random *structure* recovers most of the aggregate |
| J | Memory Without Structure | ✅ | ✅ | ✅ | ✅ | foundational — everything to zero |

**Read the EIG row carefully.** EIG passes all four rungs, so "no
measurable gain" is **not** a measurement artifact — it is a real finding.
EIG is a perfect ranker (top-k precision 1.000 vs random 0.584) that buys
nothing, and removing it makes the organism look *better* on every
structural metric. A perfect selector over a **starved** candidate pool
cannot matter: there is nothing for selection to choose between.

#### What changed because of this

The owner had proposed Tier-1 Priority #1 as *Full vs Salience retention*.
**That experiment is degenerate on the current build** — retention pressure
on the hypothesis layer is 0.35, so both colonies would be identical. The
audit replaced it with a gate: **G-P1 — retention pressure must exceed 1.0
on the object being retained before a retention experiment means
anything.**

Tool: `benchmarks/instrumentation_audit.py`. Results:
**`docs/instrumentation_audit.json`**. Gate board: **`docs/GATE-BOARD.md`**.
Facts with provenance: **`docs/FACTS-SHEET.md`**.

---

### 8.4 The counter that was measuring the wrong population

This is the finding that changed the plan twice, so it is worth reading in
full if you only read one section.

**What the audit found.** Retention pressure on the belief layer was 0.35:
the belief pool held 5–8 beliefs against a cap of 15, so the cap never
bound and the `FULL` / `SALIENCE` arms would have been identical colonies.
A branch-structured stimulus was designed to supply enough competing beliefs
to make the cap bind.

**What the stimulus run found.** The branch stimulus passed every gate *on
peaks* — 7 competing subjects, a belief pool of 17, pressure 1.13 — but its
*mean* belief count was 2.97 and **55% of tail cycles produced no beliefs at
all**. A repeat count of 4 worked; 6 and 10 collapsed. That looked like a
phase transition, and the instinct was to treat it as a boundary condition.

**What the mechanism probe found.** The collapse was a **measurement defect**,
not a property of the stimulus.

`MemoryService.store()` builds the co-occurrence and temporal graphs from
world events only:

```python
if event_type != "sleep":
    self._record_cooccurrences(event.tags)
    self._record_temporal_edges(event.tags)
```

But the tag-frequency counter was maintained for **every** stored event,
including the organism's own sleep payloads — and that counter is the
**denominator** of the Layer-1 edge strength:

```
ratio    = count / max(source_freq, 1)      # count     = world edge count
strength = min(1.0, ratio)                   # source_freq = ALL events
```

So the numerator and the denominator measured **different populations**. A
prediction candidate only survives into `stable_prior` when its strength
clears `STABLE_THRESHOLD = 0.3`, so the filter was silently discarding the
world's own structure in favor of whatever the organism happened to say
about itself.

Measured, on one tag in the branch stimulus:

```
count   src        tgt       source_freq  ratio  survived
   930       alpha       bravo    21516  0.043  no
   306       delta       alpha     1901  0.161  YES
   115     experiment       alpha     2378  0.049  YES
```

With only **4 distinct surviving edges** — two of them the organism's own
schema tags — there was no reciprocal pair, so **0 processes, 0 workflows,
0 beliefs**.

**The fix.** The counter is now scoped to world events, like the graph it
normalises. A `meta` table records the scope the counters were built with,
so a database written by an older build rebuilds its counter exactly once
instead of mixing two populations in one table.

**What it changed.**

| | before | after |
|---|---:|---:|
| branch stimulus — belief pool (mean) | 5.43, intermittent | **18.00, constant** |
| branch stimulus — competing subjects (mean) | 1.72, intermittent | **7.00, constant** |
| branch stimulus — tail cycles passing every gate | 27% | **100%** |
| study stream — belief pool (mean) | 6.83 | 5.17 |
| study stream — competing subjects (mean) | 1.83 | 0.97 |

**The study stream got slightly worse, and that is the important part.** The
pollution had been suppressing edges *selectively*, leaving a concentrated
set — and a concentrated set is exactly what produces a high-share subject
and therefore a theory. The study stream's "exactly one competing subject"
was partly an artifact of the defect.

**Two disclosures follow.**

1. **The V1 ablation results were produced on the broken scope.** Every
   condition ran on the same substrate, so the *comparisons* stand, but the
   absolute densities are not comparable to post-fix numbers. No V1
   conclusion is retracted, because every one of them is a comparison.
2. **The live run has a discontinuity** where it was restarted on the fixed
   build. The build marker in `organica.log` records which configuration
   produced which cycles, and the sleep cycle at the restart is in the
   revision log below.

**The generalisable lesson.** A stimulus parameter that flips a result
between "works" and "collapses" is a statement about the *instrument*, not
a boundary condition of the system under study. The parameter was
interacting with a mis-scoped denominator, and the interaction looked
exactly like a phase transition because the denominator's pollution grows
with the organism's output, which grows with the stimulus.

Tools: `benchmarks/freq_scope_probe.py` → **`docs/freq_scope_probe.json`**;
`benchmarks/gate_check.py` → **`docs/gate_check.json`**;
`benchmarks/branch_diag2.py` for the layer-by-layer edge trace.
Journal: §21.

---

### 8.5 Phase K: the search failed, and what that changes

**What was run.** Three candidate task families, ten seeds each, each scored
against the **best** simple baseline configuration out of a declared grid of 24
per seed per family. The baselines were given the tuning advantage on purpose:
a strawman is the most likely way to manufacture a false positive.

| Family | Organica | Best simple baseline | Difference | 98.33% interval | Verdict |
|---|---|---|---|---|---|
| K1 — incremental world modeling | 0.5923 | 0.9360 | −0.3437 | [−0.3773, −0.3123] | **REVERSED** |
| K2 — belief revision | 0.4111 | 0.9846 | −0.5735 | [−0.6162, −0.5309] | **REVERSED** |
| K3 — longitudinal integration | 0.0000 | 0.8578 | −0.8578 | [−0.8598, −0.8571] | **REVERSED** |

**What it means for you.** The pre-committed outcome **H2** fired exactly as
written down before the run: three more families ruled out, **no V2
designed**. That was the point of writing it down first — so a negative
result could not later be quietly reinterpreted as a near-miss.

Two things this does *not* say:

- It does **not** say developmental architectures do not work. It says six
  kinds of task have been tried and none of them favoured Organica 1.
- It does **not** say the three mechanisms are inert. It says that on tasks
  where the organism was already losing by a wide margin, a mechanism cannot
  show an effect.

**The zero, and why it was worth checking.** Organica scored exactly 0.000 on
K3's late incorporation on all ten seeds, which looks like a bug until you
check it. Three artifacts could have faked it, and each was tested with a
check that could fail: the late structure appears in **zero of 150 cycles**,
so it is not a snapshot artifact; every candidate type except `anomaly`
mentions **zero of 12** late tags, so nothing was left unread; and a 2×2
control across five seeds shows the late group is incorporated **only when it
is strictly stronger** than the group that arrived first. So the exclusion is
a salience/priority competition under a bounded belief pool — the risk the
preregistration's §6 named before the run.

**The one thing worth acting on.** The ablations came back empty on the two
families that had a mechanism hypothesis. That points at a prior question:
**which internal mechanism, if any, produces an external advantage at all?**
Adding a seventh task family to the map is reasonable and the map is the
deliverable — but until that mechanism question is answered, another family
is being added to a list of losses.

Tools: `benchmarks/phase_k_campaign.py` → **`docs/phase_k_results.json`**;
`benchmarks/phase_k_diagnose.py` for the K3 root cause. Write-up:
**`docs/phase_k_results.md`**. Journal: **§33**. Facts sheet: **§T**.

---

### 8.6 The V1 synthesis: what V1 established, and what it did not

**Why this exists.** Six task families are now negative. The project's risk
has changed shape — it is no longer a shortage of data, it is **the risk of
drawing the wrong conclusion from data that is already there.** Six negatives
are either a map of a development-first architecture's natural properties, or
a verdict on it, and the difference between those readings decides everything
after this.

**The synthesis is a separate document** because it is a different kind of
statement from a finding: it adds **no new evidence**, it is a reading of the
record, and every claim in it cites a committed artifact.
**[`docs/V1-SYNTHESIS.md`](V1-SYNTHESIS.md).** Journal: **§34**.

**The one-sentence conclusion.**

> Organica demonstrates that a development-first architecture can generate
> history-dependent cognitive structure through experience, but it has not yet
> demonstrated that those structures confer a measurable advantage on external
> tasks.

The first half is supported by direct measurement. The second is a negative
result with a specific shape — six families, several of them large losses
rather than near-misses. Read together they are usually taken as a verdict.
They should not be: the first half is a claim about **development**, the second
about **tasks**, and the benchmarks were never chosen to measure development.

**The two goals, and why the distinction decides the next step.**

| Goal | The evidence |
|---|---|
| **A dynamic intelligence whose internal organization changes through experience** | **Supported.** Development occurs, outcomes vary with the experience schedule (path dependence — strict order dependence is **not** isolated, because the curriculum comparisons vary the event multiset and order together), curriculum matters, trajectories diverge, and internal epistemic structure emerges with no pretrained domain knowledge. |
| **A replacement for modern language models** | **Not supported.** Nothing here addresses language, generation, or scale — and the one relevant measurement is negative. |

The dangerous move is letting the urgency of the second goal drive the method
of the first, which is how a project ends up running benchmark after benchmark
looking for a win the architecture was never designed to produce.

**The question this leaves open** — not *can we make Organica smarter*, and
not *what benchmark next*:

> **What properties must a developmental intelligence have to remain adaptable
> without losing coherence?**

All six campaigns so far asked *"can Organica beat a baseline?"*. The next one
should ask *"can we find and move the property that makes plasticity and
coherence trade against each other?"* The discipline does not change:
pre-register it, make every harness able to fail, do not relax a gate to make
a campaign runnable, record a null as a null.

**No V2 is designed and no Phase L is launched by this.** The preregistered
terminal outcome for Phase K stands as written, and Path B (engineering) becomes
available when Path A (developmental science) identifies the mechanism —
not before, because the mechanisms one would most naturally reach for are
exactly the ones measurement has shown are **not** load-bearing.

---

### 8.7 Organica 1 is frozen: the v0.9.0 tag is the archival reference

**What frozen means here, precisely.** It does **not** mean no more commits.
It means **no more architectural modifications to Organica 1**. The engine
becomes a fixed reference object: everything afterwards *measures* it, and
nothing afterwards *quietly changes* it.

**What is frozen:** `organica/sleep.py`, `organica/memory.py`,
`organica/paths.py`, `organica/streams.py`, `organica/branch_streams.py`,
`organica/scale_streams.py` and `organica/ground_truth_worlds.py`, plus the
published result artifacts.

**What is still free:** benchmarks and harnesses, all documentation, the
manual, the action list, and tests for new instrumentation. Phase L lives
entirely in `benchmarks/`. The one rule covering the boundary: nothing may
change the **behavior** of the frozen engine.

**It is enforced, not just declared.** `tests/test_v1_freeze.py` reads the
frozen files out of the `v0.9.0` tag and compares them byte for byte with the
working tree. A changed file fails the test and names the difference. This
repository's history is a history of promises drifting — the version
declaring a release master was not, the changelog linking a 404, the
"structure flat" claim being an overstatement — and every one of those was
caught by an instrument rather than by reading carefully. So the freeze is an
instrument too. It skips honestly (and says so) when the tag is not reachable,
which is what a shallow clone looks like.

The freeze record is **[`docs/V1-FREEZE.md`](V1-FREEZE.md)**.

---

### 8.8 Phase L: the pilot that looked like a negative result and was not

**What happened.** The reduced-scale execution check of the Phase L harness
printed eight identical points:

```
V1 1:4 seed 20261023: DI=0.000 PI=0.611
V1 1:3 seed 20261023: DI=0.000 PI=0.611
... (all eight points identical)
```

Read casually, that is a publishable-looking negative result — *the late
structure never displaces the early structure, at any pressure*. It is
exactly the shape of the Phase K K3 result, and it would have slotted neatly
into the existing story. **A result that confirms what you already believe
is the result you are least likely to check.**

**What it actually was.** The support ratio was not varying anything. The
late group's arrival cycle was an absolute number (150) while the pilot ran
150 cycles, so the late group never became active, the late structure was
never available to measure, and a ratio with no denominator was being
reported as `0.0`. The sweep ran through eight points in which **nothing
could be displaced**, and reported "nothing was displaced" eight times.

**Why the existing audits missed it.** Phase L had two instrument audits and
both passed on that broken world: the discrimination control checked that the
metric separates the two poles, and the ceiling check checked that a perfect
model can reach 1.0. Both check the **metric**. Neither checked the
**design**. The metric was working perfectly on a world where the thing being
measured was not present.

**The four defects, all fixed** (details in
[`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`](PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md),
Amendment 1):

1. The late group's arrival was absolute rather than a fraction of the run.
2. An unmeasurable index was reported as `0.0` instead of excluded.
3. The contradiction arm shared a feature of the late group with itself, so
   the world was byte-identical with the arm on and off — V5 measured
   nothing.
4. The density arm fed the engine only part of the world (7,200 of 28,800
   events at density 4.0).

A fifth, found by reading rather than running: the Revision Threshold
bootstrap was resampling the **DI–PI gap** instead of the **crossing
location** that the protocol's criterion 4 is about.

**What was added.** A **third instrument audit — the degeneracy audit** — that
checks the design rather than the metric: that every cell has a denominator
to measure against, that the support ratio actually changes the early/late
event mix, that the contradiction arm differs from the plain arm, and that
the density arm actually changes the event count. The campaign does not run
if it fails. It earned its place immediately: the first version of the audit
itself had a scaling inconsistency with the campaign builder, and the audit
caught it by failing the run before anything executed.

**After the fix**, the corrected pilot (reduced scale, one seed — a disclosed
pilot, never evidence) gives DI rising 0.000 → 0.667 and PI falling
0.722 → 0.000 across the sweep, with the curves crossing between 2:1 and
3:1. The axis is alive. **No Phase L campaign has been run and no Phase L
outcome exists.**

**The rule this earns, now AGENTS.md rule 13:**

> *An identical value at every point of a sweep is a measurement defect until
> proven otherwise.*

The protection is not more scrutiny of the result. It is scrutiny of the
**design**, before the run, by an instrument built to contradict the code
rather than confirm it.

---

### 8.9 Phase L: the protocol review, and the hunt for hidden degeneracy

**What this section records.** The owner's protocol review of Phase L, the
changes it produced, and the pre-flight audit that ran *before* the campaign
to look for the degeneracies the pilot had **not** exposed. Written before
any Phase L outcome existed.

### What the review changed

**The decision interval: 98.33% → 99%.** The protocol stated a 98.33%
interval and glossed it as "Bonferroni across the arms". Those disagree:
across five arms Bonferroni gives 0.05/5 = 0.01, i.e. a **99%** interval,
while 98.33% corresponds to 0.05/3 — Phase K's correction factor, carried
over by accident. The ruling was that **the intent governs and the stray
percentage is the accidental constant**. Phase K's own figures are untouched.

**Success and failure, stated plainly.** New §6.1 of the protocol. Success is
a stable displacement curve with an interior, reproducible crossing. Failure
is a flat DI, a flat PI and no crossing — a characterization of the organism
sitting at one pole, and a publishable one. **The campaign must be able to
fail.**

**A new diagnostic: the Displacement Score, `DS = DI − PI`.** The sharpest
point in the review: **DI and PI are not opposites.** DI 0.8 with PI 0.8 is
*coexistence* — the late structure was learned and the early structure kept —
and that is not revision. DI 0.8 with PI 0.1 is genuine displacement. K3
already established that acquisition and displacement are different
phenomena, so the gap between the two indices is now reported on its own.
**DS is a diagnostic only**: not a primary metric, not a success criterion, in
no verdict, never averaged.

**Revision latency elevated to co-primary reporting.** Two organisms can end
at the same DI and PI while crossing at completely different cycles — same
endpoint, different developmental behavior. Latency is now reported beside
the RT. **The four success criteria are unchanged**: a phase that quietly
added a fifth criterion after the fact would be the same error in a
different coat.

**Hysteresis deferred, not forgotten.** The reverse sweep (late → early) would
show whether the system crosses back — path-dependence. It is the natural
successor phase and is deliberately *not* added now.

### The pre-flight hunt for hidden degeneracy

The pilot proved the class of bug is live in this project, so before spending
hours of compute the harness was audited for the degeneracies the pilot had
**not** exposed. All five checks pass:

| Check | Result |
|---|---|
| The engine is **deterministic** for a given seed | DI 0.5 / PI 0.277778, twice — the paired bootstrap over seeds resamples something real |
| Different seeds give **different** results | 4 distinct results from 4 seeds — there is seed variance to resample |
| Every arm has a **full denominator** | min `late_available` = 18, min `early_available` = 18, of 18 possible |
| The **V4 belief cap binds** | peak beliefs 11 at cap_pressure 3 → **15** (the cap) at cap_pressure 24 |
| The protocol's **factual claims hold** | "600 cycles, matching the Phase K K3 family" — checked against Phase K's preregistration, which says 600 cycles for K3 |

The V4 check deserves a note. Phase G measured the belief pool *starved* on
the live study stream — mean 5.17 beliefs, max 6, against a cap of 15. If the
pool never fills, the belief-cap arm cannot change anything, and a flat V4
curve would be a statement about the engine rather than about the organism —
the way V5 was inert before Amendment 1. It binds, so V4 is live. There is now
a **fourth instrument audit** that keeps this honest permanently.

### Two things that were quietly wrong

- The results file recorded `"python_hash_seed": "0"` unconditionally —
  asserting the pinned value whether or not it was set. It now records the
  **actual** value and warns loudly when the pin was not met.
- The intermediate checkpoints recomputed the 10,000-replicate bootstrap after
  **every** cell, and rebuilt the audits per cell. Both are now computed once.
  The first would have added hours of pure arithmetic to the run.

---

### 8.10 Phase L: the primary axis result

**What this section records.** The completed Phase L V1 run — 80 of 80 cells,
8,057.8 s wall clock, 10 seeds per sweep point, decision interval 99.00% — and
the verdict the frozen protocol produced from it. Full detail and evidence:
**`docs/phase_l_results.md`**; artifacts `docs/phase_l_results.json` and
`docs/phase_l_results.ndjson`.

**The verdict: `H3-L — INCONCLUSIVE`.** The protocol's remedy for that verdict
is *raise n; conclude nothing*, and no Phase L outcome authorises a V2.

### The curve

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

All four instrument audits passed on the live run, and **no cell was
unmeasurable** — nothing was excluded and nothing was zeroed.

### The four criteria, as evaluated

| # | Criterion | Result |
|---|---|---|
| 1 | DI monotone increasing, range ≥ 0.25 | **MET** (range 0.750) |
| 2 | PI monotone decreasing | **NOT MET** — mean PI rises 0.789 → 0.794 at 1:3, then falls monotonically |
| 3 | The curves cross, interior to the sweep | **MET** — at **3:1** |
| 4 | The crossing is reproducible (99% bootstrap interval excludes both endpoints) | **MET** — **[5.0, 5.0]**, 10,000/10,000 replicates |

Criterion 2 is the only failure, and it failed by **+0.005** at a point whose
standard deviation is 0.070. The criterion has no noise clause: it is evaluated
on the mean curve, and the mean curve rises. It was evaluated once by the
committed code, and it was **not** re-read, relaxed, or reinterpreted
afterwards — the stable RT was not allowed to stand in for the criterion that
failed.

### The crossing, for what it is worth

The RT at 3:1 is as reproducible as a crossing over eight positions can be: a
paired bootstrap over seeds puts it at [5.0, 5.0], eight alternative bootstrap
seeds all return `INTERIOR`, and leave-one-seed-out leaves it at 3:1 in **10 of
10** folds. Revision latency (co-primary report, not a criterion) goes from
**0/10** seeds reaching DI > 0.5 at 2:1 to **10/10** at 3:1, with a median of
347 cycles — the transition is abrupt, not gradual.

### One wording gap in the protocol, recorded rather than exploited

The protocol describes the `H3-L` bucket as *"intervals too wide to place RT."*
That is **not** what happened: the RT interval is the narrowest possible and
criterion 4 passed. The verdict is INCONCLUSIVE because **criterion 2 failed**,
not because the threshold could not be located. Nothing was reinterpreted, but
the next phase must say what "inconclusive" means when the interval is narrow
and a different criterion failed — otherwise a stable RT becomes a quiet license
to round INCONCLUSIVE down to "close enough".

### What this does and does not establish

**Established:** the instrument works and the pilot's flat line was an artifact;
the organism sits at the preservation pole (DI exactly 0.000, PI ≈ 0.79) under
low displacement pressure; on this axis DI and PI cross at 3:1 and the crossing
is highly reproducible.

**Not established:** a boundary in the `H2-L` sense (criterion 2 was not met);
PI's monotone decrease; anything about capability; anything about the support
ratio being *the* operative variable beyond this axis on this engine. **V2–V5
were not run** — no Phase L outcome authorises a V2. The baseline rule was
recorded and not exercised in V1.

### The raise-n campaign is running (Amendment 3)

The protocol's own remedy for `H3-L` is *"raise n; conclude nothing"*, and the
owner elected to take it on the primary axis: **same sweep, same protocol,
same criteria, no edits.** Amendment 3 in the preregistration records the
commitment, and it was committed **before the raise-n run existed**.

| | |
|---|---|
| Seeds per point | 10 → **30** (the original 10 plus 20 new) |
| Cells | 240 total — the 80 original cells are **reused**, 160 new ones added |
| Sweep, metrics, criteria, interval, engine, terminal outcomes | **unchanged** |
| Secondary arms V2–V5 | still not run |

**Where to watch it:**

```powershell
Get-Content C:\Users\monte\anti\project-organica\.scratch\phase_l_raisen.log -Tail 20
```

Results land in `docs/phase_l_results.json` (the canonical file, now a
superset of the n=10 run) and `docs/phase_l_results.ndjson`. The n=10 record
is preserved unmodified as `docs/phase_l_results_n10.json` / `.ndjson`.

**The analysis is committed code now:** `benchmarks/phase_l_analyze.py`
produces the curves, the four criteria, the RT interval, the eight
alternative bootstrap seeds and the leave-one-seed-out check — all from
committed code rather than a scratch script.

**One thing to expect, stated before the run:** the low-end PI steps are each
individually consistent with zero at n=10, so the raise-n run should *tighten*
the low-end intervals and establish that end of the curve as a plateau. It
should **not** be expected to resolve the sign of the 1:4 → 1:3 step. If
criterion 2 passes at n=30, that must be read as *"the signs happened to come
out non-increasing at n=30"*, not as *"PI decreases at the low end"* — the
adjacent-difference diagnostic is reported alongside it either way.

### 8.11 Phase L: the raise-n result, 30 seeds per point

**What this section records.** The raise-n campaign — the protocol's own
remedy for `H3-L`, taken on the primary axis with the same sweep, the same
criteria and no edits — and what it produced. Full detail:
**`docs/phase_l_results.md`**; artifacts `docs/phase_l_results.json` (n=30),
`docs/phase_l_results_n10.json` (the n=10 record, preserved).

**Verdict: `H3-L — INCONCLUSIVE`, unchanged — and now with two of the four
criteria unmet.**

| Criterion | n = 10 | n = 30 |
|---|---|---|
| 1. DI monotone increasing | **met** | **not met** |
| 2. PI monotone decreasing | not met | not met |
| 3. DI range ≥ 0.25, crossing interior | met | met |
| 4. RT interval excludes both endpoints | met | met |

### The curve is a step function, not a ramp

| Label | DI (sd) | PI (sd) | DS | Latency | Seeds DI > 0.5 |
|---|---|---|---|---|---|
| 1:4 | 0.000 (0.000) | 0.743 (0.101) | −0.743 | — | 0/30 |
| 1:3 | 0.000 (0.000) | 0.754 (0.079) | −0.754 | — | 0/30 |
| 1:2 | 0.000 (0.000) | 0.748 (0.091) | −0.748 | — | 0/30 |
| 1:1 | 0.000 (0.000) | 0.717 (0.064) | −0.717 | — | 0/30 |
| 2:1 | 0.204 (0.119) | 0.606 (0.090) | −0.402 | — | 0/30 |
| 3:1 | 0.706 (0.059) | 0.039 (0.044) | +0.667 | 356 | 30/30 |
| 4:1 | 0.722 (0.076) | 0.000 (0.000) | +0.722 | 291 | 30/30 |
| 6:1 | 0.715 (0.048) | 0.000 (0.000) | +0.715 | 244 | 30/30 |

Three plateaus and two transitions. **DI is exactly 0.000** at the four low
ratios for all 30 seeds, and **PI is exactly 0.000** at 4:1 and 6:1 — the
early structure is entirely gone at the top of the sweep.

### What did not move, and what did

**The Revision Threshold did not move:** still 3:1, interval [5.0, 5.0],
10,000/10,000 replicates, eight alternative bootstrap seeds `INTERIOR`,
leave-one-seed-out at 3:1 in **30 of 30** folds. Tripling n did not move the
one quantity the phase set out to locate.

> **What that robustness means (2026-10-26).** Robust **within this defined
> experiment** — this engine, this world family, this support-ratio axis. The
> eight alternative bootstrap seeds test **resampling stability, not new
> worlds**: they re-draw from the same measured seeds. **3:1 is not a general
> threshold for Organica**, and the number should not be quoted as one.

**Criterion 1 flipped.** The top of the DI curve dips by −0.007
(4:1 0.722 → 6:1 0.715).

### Why both criteria fail: they are signs of zero

| Step | dPI (99% paired interval) |
|---|---|
| 1:4 → 1:3 (**criterion 2 fails here**) | **+0.011 [−0.026, +0.044]** |
| 1:2 → 1:1 | −0.031 [−0.078, +0.015] |
| 1:1 → 2:1 | −0.111 [−0.157, −0.065] |
| 2:1 → 3:1 | −0.567 [−0.619, −0.522] |
| 4:1 → 6:1 (**criterion 1 fails here**) | +0.000 [+0.000, +0.000] |

Every step whose interval excludes zero is a real transition; every step
whose interval contains zero is a plateau edge. **Both failing criteria are
sign tests on differences indistinguishable from zero.**

### The uncomfortable part, and it is the useful part

*Run after the n=30 outcome was known. It changes no criterion, no verdict
and no prediction — the verdict stands as INCONCLUSIVE and no boundary is
claimed.*

Resampling the 30 measured seeds and recomputing the four criteria:

| Criterion | random 10-seed subsets | random 20-seed subsets | n = 30 |
|---|---|---|---|
| 1. DI monotone increasing | 19.3% | 16.1% | 0% |
| 2. PI monotone decreasing | 12.0% | 6.6% | 0% |
| 3. DI range ≥ 0.25 | **100.0%** | **100.0%** | met |
| 3b. Crossing interior | **100.0%** | **100.0%** | met |
| **All four together** | **2.9%** | **1.2%** | 0% |

**The two stable criteria are the two robust ones.** The two
strict-monotonicity criteria hold in 7–19% of random draws — the n=10 run's
criterion-1 pass was itself one of the lucky 19%. Strict monotonicity is not
a property this organism's displacement curve has: the low end is DI = 0.000
exactly and the high end saturates at DI ≈ 0.71. **More seeds cannot turn a
plateau into a ramp, so "raise n" is exhausted as a route to satisfying
criteria 1 and 2.**

### And the added seeds moved the curve

DI at 6:1 was 0.750 for the original ten seeds and 0.697 for the added
twenty (p = 0.0022 against random 10-vs-20 splits); DI at 2:1 was 0.283 vs
0.164 (p = 0.0103). The seeds *should* be exchangeable — the seed enters only
through `random.Random(seed)` — but the campaign's seeds are consecutive
integers, which is what non-exchangeability looks like and also what an
unlucky draw looks like. A **seed-exchangeability audit** with 30 fresh,
non-consecutive, pre-declared seeds was run to tell them apart; it is an
instrument audit and produces no experimental claim.

**The audit's answer: the seeds ARE exchangeable.** The fresh scattered set
gave DI **0.7241** at 6:1, against 0.7148 for the campaign's own 30 and
0.7500 for its original ten — a difference of +0.0093 from the campaign's
30-seed mean, **p = 0.60** against random 30/30 splits of all 60 measured
values. And the fresh set's own arbitrary half-split gap of **−0.0407** has
the *opposite sign* to the campaign's **+0.0528**, at similar magnitude —
which is what an exchangeable axis looks like when the partition is
arbitrary. **So the original ten seeds were an unlucky high draw, not a
seed-block artifact, the paired bootstrap over seeds is sound, and the n=30
curve is the better estimate because there are more seeds, not different
ones.**

### 8.12 Phase L: the published characterization

**What this section records.** The synthesis published after the raise-n run:
what Phase L established, what it did not, and the owner's reading of the
pattern that survived increasing n. Full text:
**[`docs/PHASE-L-SYNTHESIS.md`](PHASE-L-SYNTHESIS.md)**, following the
`docs/V1-SYNTHESIS.md` pattern — a formal read that adds no new evidence and
cites a committed artifact for every claim.

**The protocol verdict is unchanged and stands: `H3-L — INCONCLUSIVE`.** The
characterization is a separate artifact and does not re-score it.

**The one-sentence conclusion:**

> *Organica 1 does not appear to exhibit a continuous coherence–plasticity
> trade-off. It appears to exhibit regime behavior separated by a
> reproducible transition region.*

**What survived increasing n:** the preservation plateau (**DI exactly 0.000
for all 30 seeds** across 1:4–1:1), the transition region, the crossing at
**3:1**, the reproducible RT (**[5.0, 5.0]**, 10,000/10,000 replicates,
leave-one-seed-out 3:1 in **30 of 30**), and the abrupt latency shift
(**0/30 → 30/30** seeds reaching DI > 0.5 between 2:1 and 3:1).

**What did not survive:** strict monotonicity — which got *weaker*, exactly as
expected if it was never a property of the organism.

**Why raising n again is not the answer.** The reason to raise n was that the
+0.005 PI reversal might be *noise around an otherwise monotone curve*, or the
curve might be *genuinely step-shaped* — worlds that predict differently. n=30
distinguished them: the low-end steps are each consistent with zero, the
plateaus are exact across all 30 seeds, and the monotonicity criteria fail
*more* firmly. **The campaign was not failing for want of precision; it was
failing because the curve is not the curve the protocol expected.** "Raise n
until it says what I want" is the failure mode a pre-registration exists to
prevent.

**What comes next:** the secondary axes are no longer tests of *which variable
moves a smooth boundary* — they are tests of **why the curve is step-shaped**:
what sets the width and location of the transition region. **V2–V5 remain
unrun**; no Phase L outcome authorises a V2.

**The dangerous question, and its answer:** *"a stable, reproducible threshold
at 3:1 — that is a boundary, isn't it?"* **It is not.** A threshold is a
boundary only if the trade-off is a continuum the threshold divides; here the
curve is flat on both sides of the crossing, and the crossing is stable
because the organism **switches regimes**. That is a real property, and it is
not the property the protocol asked for. And "regime" describes the shape of a
displacement index, a preservation index and a latency on synthetic worlds —
**it is not a claim about intelligence.**

### 8.13 Phase M groundwork: the development audit trace specification

**What this section records.** The specification written after the Phase L
characterization, on the owner's direction that the next decisive move is a
**developmental auditability** layer: the record that would let an investigator
reconstruct *why* a structure survived, without asking the organism.

**Full text:** **[`docs/AUDIT-TRACE-SPEC.md`](AUDIT-TRACE-SPEC.md)**.

**The question it answers:**

> **Could an investigator reconstruct the reason — what evidence was used, how
> the claim was formed, what the competing candidates were — without asking the
> system?**

**The three levels, and where each one lands against the real engine:**

| Level | Question | Verdict |
|---|---|---|
| 1. Provenance | Can every structure be traced to what it was built from? | **Available** — `get_ancestry()` exists, with parent links already stored. Bounded by depth 7 and a 4,000-event window. |
| 2. Evidence | Can a belief's support be resolved to the experiences behind it? | **Available, with one correction** — see below. |
| 3. Selection | Can it be established *why this survived and that disappeared*? | **Available under the default policy** — the contest set is invisible in the report but reconstructible from the report's own Layer-2/3 outputs plus the persisted priors. |

**Level 3 is the valuable one.** Level 1 shows what a structure was made of;
Level 2 shows what it rests on; Level 3 shows **the choice** — and after Phase L
the choice is the interesting thing, because the organism is selecting, and its
selection has a reproducible transition region.

**The correction that matters.** The record format first proposed would have
written *"12 supporting observations, 4 contradictory observations"*. The engine
does not hold either of those. `support_count` is a count of **temporal
transitions**; `contradiction_count` is the subject's **total outgoing flow
minus the flow that supports this expectation** — that is, its *competing*
flow, not evidence that anything contradicted it. `confidence` is
`support / (support + competing_flow)`. A record that mislabels these puts a
false claim at the center of the audit.

**The counterfactual wall.** *"Candidate B would have survived without A"* is a
**replay**, not a trace. It requires a separate run with A removed, a separate
artifact, and its own label. It can never be a field of the trace.

**No instrument by default.** The whole selection contest turns out to be
externally reconstructible under the default `salience` policy, because every
input to the ranking is derivable from what the engine already exposes and
the substrate already persists. So the plan is **assembly, not
instrumentation**; a labeled observer build is the fallback, and it must
demonstrate that recording the trace leaves the engine's outputs unchanged.

**Two disclosed defects found while writing the spec** (both recorded, neither
patched — the engine is frozen): `contradiction_count` is easy to misread (D1),
and the temporal graph's lookback window has **no `event_type` filter**, so a
supporting transition can originate from the organism's own previous sleep
payload while co-occurrence and tag-frequency edges are world-scoped (D2). The
trace reports the world/self split of every belief's support.

**Six acceptance criteria** for the eventual build, each able to fail: evidence
replay exactness, selection reconstruction exactness, ancestry honesty,
behavior invariance, field-honesty, and trace/counterfactual separation.

**The load-bearing claim has since been tested.** `benchmarks/audit_trace_probe.py`
is an **instrument probe, not an experiment about the organism**: it runs the
frozen engine on the frozen cause-world generator and, at every cycle,
rebuilds the selection contest from the report and the substrate and
compares. Default arm (the engine's own cap of 15): **120 cycles, 1,412
beliefs checked, A1 aggregate evidence 0 failures, A2 selection reconstruction
120/120 cycles, A7 event-level attribution 1,412 beliefs 0 failures with 244
aggregate edges reconciling exactly.** Stress arm (cap 5, so the cap binds):
**60 cycles, 290 beliefs, A1 0 failures, A2 60/60, A7 290 beliefs 0 failures,
and 403 candidates lost on rank** — the default arm alone never exercised that
branch, because its pool peaked at 12 against a cap of 15, and the write-up says
so rather than letting the weaker test stand.

**What the first version of the probe actually verified was narrower than it
claimed, and the specification was corrected to match.** The first pass
reconciled the **aggregate** `precedes` table against the engine's reported
counts. That shows the auditor reproduces Organica's *counts* and its
*selection decisions*; it does **not** show it can identify the individual
experiences behind a count. Event-level attribution is therefore now its own
check (A7), and the earlier result is named for what it is: **aggregate
evidence reconciliation and selection reconstruction passed.**

**Three corrections to the specification, each verified against the source
before being written down.** (i) A cycle returns **14** candidate lists, not
13. (ii) The engine's lookback window **includes the event being stored** —
`store()` inserts the row before recording edges — so the window is the event
itself plus two others, and **within-event tag pairs also become temporal
edges**. The specification's first replay rule was wrong about this. (iii)
**A post-hoc replay from the final log cannot reconstruct the window** — the
engine's query has no `rowid` tiebreak, and sleep-candidate rows are pruned —
so event-level attribution requires a **passive store-time observer**, and
the observer must mirror the engine's own `event_type != "sleep"` guard.

**D2 is now a measured quantity, and the denominator had to be fixed first.**
The first version pooled the support of every reported belief across every
cycle in which it was reported; because a belief's support count is
**cumulative**, a transition that occurred early is counted again in every later
cycle where the belief survives. That pooled number counts **support
references**, not distinct evidence. The probe now reports three views:
**distinct evidence behind reported beliefs** (802 of 4,481 = **17.9%** self-sourced — the
disqualifier's figure); **pooled support references** (53,980 of 307,857 = 17.5%); and **all distinct
transitions recorded** (5,436 of 12,583 = **43.2%**), including edges no reported belief
ever rested on. **Correcting the denominator moved the headline only slightly**
(17.5% → 17.9%) and that agreement is worth stating; **but it surfaced a separate and much
larger number**: **43.2% of the organism's entire distinct transition surface is its own
sleep output**, against 17.9% of the evidence actually behind its claims. Different
surfaces; the trace must report both.

**The forced-tie arm is now run.** The clock is patched so that every four
consecutive stores share a timestamp, producing **479 stores with a genuinely tied
window**; the observer reproduces the engine's choice anyway and **A7 stays
exact** (2,589 distinct transitions, 241 aggregate edges reconciling, 0 mismatches). The honest
statement: the **implementation** is deterministic for identical queries over
identical data, so the observer's re-run selects the same rows; the **schema**
still does not determine the window under a tie, and a replayer that did not
observe at store time could not rely on it.

**The probe found two defects in itself, which is the point of checks that can
fail.** Its first observer attributed transitions for sleep events as well as
world events — the engine deliberately skips those — so the attributed totals
ran an order of magnitude above the aggregate counts and A7 caught it. And its
first invariance check compared whole reports including `ran_at`, a wall-clock
timestamp, so two identical runs differed for a reason that had nothing to do
with behavior. Both were the auditor's errors, both were found by the checks
rather than by inspection. **The checks can fail**: the probe's own
tests break the auditor on purpose (zeroing the curiosity term; dropping a
tag from the temporal graph) and require A1 and A2 to go red, and they do.
**So the selection contest needs no hook inside the engine** — the plan is
assembly, not instrumentation. What is *not* established: generality (one
world family, one policy), the `stochastic` policy, the four remaining
acceptance criteria, and anything whatsoever about learning.

**What comes next:** build the auditor (read-only, no engine change), meet the
six criteria, run it against a world with known ground truth — and only then
design the blank-slate acquisition experiment, so that "it revised" is a claim
with a record behind it.

### 8.14 Keeping the trace honest

**The risk, named.** The audit trace is attractive, and attractive things become
projects. It could become the new displacement curve — infrastructure that is
built, extended and admired without ever adjudicating a question the project
wanted answered. Then it is a *second* inventory, and the project has swapped
one measurement habit for another.

**The rule, pre-committed rather than aspirational:** the next protocol's
success criteria must contain at least one **trace-derived diagnostic**, and a
result that fails it **fails the protocol even if the headline behavior is
correct**.

**The first instance — the disqualifier.** The blank-slate acquisition test
asks whether experience can produce knowledge that transfers, predicts and
revises. The standing criticism of any such success is *"it predicted
correctly — but what did it actually learn?"* The trace answers that, and the
pre-commitment stops it being decoration:

> **A transfer claim must rest on world-derived evidence, and it must be shown
> to do so.**

The disqualifier is now a **per-claim rule**, fixed in advance, because a
run-level share cannot carry a per-claim claim. Four conditions:

1. **Report the split for the claim's own support** — the trace's world/self
   split over that claim's *distinct* evidence. A run-level average is not
   acceptable evidence for a particular claim.
2. **A majority of that support must be world-derived.** A claim resting mainly
   on the organism's own output is not a transfer claim.
3. **Its self-sourced share must be no higher than the reference rate fixed
   below** — a claim that leans on self-generated evidence *more* than an
   ordinary belief does has not been carried by the world.
4. **The comparison is against the claim, never against the organism in
   general** — and a failed condition **fails the protocol even if the
   prediction was correct**.

**The reference rate is FROZEN, not recomputed on the run being judged.**
**17.9%** — the distinct-evidence self-sourced share measured on the
calibration probe (default arm, 120 cycles). It is **not recomputed on the
evaluated run**: a threshold derived from the same data it judges is not a
threshold, and a run whose beliefs happen to be unusually self-sourced would
otherwise relax the criterion meant to constrain it. It may only be
**re-calibrated on data that is not being judged**, with any re-calibration
recorded before the next protocol runs. And it is a **provisional calibration
value, not a precise universal cutoff** — one run, one world, one policy.
The honest description is *"no more self-sourced than the reference claim's
support was"*.

The trace reports the world/self split of every belief's support (§3.3 of the
spec, defect D2): the temporal graph's lookback window has no `event_type`
filter, so a supporting transition can originate from the organism's own
previous sleep payload. **That is what turns a disclosed defect into a live
scientific instrument** — a defect that can defeat a claim is worth more than
a defect that is merely recorded.

**Why the rule is conservative, and why that is stated rather than hidden.**
The contamination is now **measured, not shown to be consequential**: nothing
yet demonstrates that a self-sourced transition caused a wrong answer. The
disqualifier is therefore a statement about **what counts as evidence of
transfer**, not a claim that the organism is damaged by its own output. That is
also why it is pre-committed: a criterion that only bites once the harm has
already been demonstrated would never bite at all. **Whether self-sourced
support *hurts* is now a measurable question, and the trace is the first
instrument that can ask it — not asked here.**

A claimed **revision** must be visible in the trace as a change in a claim
whose support is world-derived, with the prior state resolved
(`revision_delta`, `prior_confidence`). A claimed **explanation** must resolve
to event ids — not to counts, and never to the system's own account of itself.

**The second guard.** The trace's own metrics — evidence-trace completeness,
lineage completeness, selection reproducibility — are **diagnostics of the
instrument**, not measurements of the organism. Reported; never criteria.

**A3's definition is fixed in advance, and the window that bounds it was
MEASURED rather than estimated.** A criterion whose definition is written after
the measurement is not a criterion, so spec §12 now says what A3 counts before
anything is run. The trace carries **two different links**, and conflating them
makes A3 silently impossible:

- **Level 1 — developmental lineage**: candidate → candidate, via `parent_ids`.
  It **terminates at Layer 1** (concepts, phrases, loops, predictions), and **no
  parent link points at an event**.
- **Level 2 — evidential linkage**: claim → supporting transitions → events.

Level 1 answers *"where did this structure came from?"*; Level 2 answers *"what
evidence supports it?"*. **Success in one cannot stand in for success in the
other** — asking ancestry to reach events would be asking Level 1 to prove
something it was never designed to represent.

A3 therefore reports **three quantities separately**: **lineage reachability**
(share of extant structures resolving back to Layer 1 within depth 7),
**evidence linkage** (share of extant claims whose support resolves to event
ids with a world/self split), and a **truncation split** — *aged out* (the
ancestor fell outside the cognition window — **a persistence problem**) /
*depth-truncated* (the chain was longer than depth 7 — **a representation
problem**) / *no parent* / *missing record* (**a data defect**, and the one that
would matter most).

**The window is the more likely binding constraint, and it is now measured, not
guessed: the engine stores 2,374.68 sleep events per cycle, so the 4,000-event cognition window spans
only 1.7 cycles — not the "roughly 40–130 cycles" this manual previously
asserted.** That estimate was wrong by more than an order of magnitude, and the
correction is recorded rather than quietly fixed. Two consequences point in
opposite directions, and both matter: a lineage that **keeps being produced**
stays inside the window (candidates are re-stored every cycle), so active
lineages may resolve far better than 1.7 cycles of history suggests — while a lineage that
**stops being produced** is gone within about 1.7 cycles. The developmental
history of anything the organism has moved on from is therefore
**unrecoverable**, not slowly censored.

**The key outcome is not the percentage.** It is this:

> **Does the incompleteness reflect the architecture's actual developmental
> history, or the observer's retention limit?**

**And the boundary A3 cannot cross: fidelity is not sufficiency.** The probe
establishes **fidelity to the implemented rule** — the auditor reproduces what
the engine did, including under a binding cap. It does **not** establish that
an intact reconstruction is a *uniquely correct account of why a belief arose*.
A reconstruction can be exactly faithful to the algorithm and still be a shallow
account of development: it explains the arithmetic of selection, not why the
structures formed in the first place. That is a separate validation question,
and A3 is where it begins.

**Whether self-sourced support *hurts* — and in what way — is now a measurable
question.** The candidate outcomes, none of them pre-committed: **correctness**
(does a self-sourced-heavy claim predict more errors?), **persistence** (does
it last longer?), **revision resistance** (does it survive contradicting
evidence?), **confidence inflation** (does its confidence overstate what its
support warrants?), and **false-positive rate**. The trace is the first
instrument that can ask these questions. They are a **characterization study,
not a protocol**, and they are not asked here.

**The roadmap this sits in:** V1 established developmental properties → Phase L
established regime behavior with a stable transition region → the development
audit trace makes the developmental *decision* reconstructible → next, can
experience produce knowledge that **transfers, predicts and revises**, judged
with trace-derived diagnostics committed in advance.

### 8.15 A3: the lineage measurement, and what it says about how much history Organica keeps

**What was measured.** An ancestry auditor, added to the probe, that walks each
cycle's reported structures' parent chains against the engine's own cognition
window and classifies every branch that fails to resolve.

| Quantity | Result |
|---|---|
| Lineage reachability | **1.000** — 8,061 of 8,061 structures resolve back to Layer 1 within depth 7 |
| Evidence linkage | **1.000** — 1,412 of 1,412 claims resolve to event ids with a world/self split |
| Truncation split (structures) | aged out 0 / depth-truncated 0 / no parent 0 / missing record 0 |
| Branch-level counts | layer-1 resolved 25,168 / aged out 105 / depth-truncated 0 / no parent 0 |
| Honesty errors | **0** |

The stress arm (3,240 structures) and the forced-tie arm (3,988 structures) both
return 1.000.

**Read the two counts together.** The structure-level split is empty, but
**105 branches were aged out**. Every structure still resolves, because each has at least one
parent branch inside the window. The empty split is not "nothing aged out" — it
is "nothing failed to resolve". Both numbers are reported for that reason.

**What it means, and it cuts both ways.** The auditor reconstructs the lineage
of **everything Organica still holds**, exactly, with no honesty errors. And it
cannot see further back than Organica remembers — because the organism does not
remember it either. **The engine's cognition window *is* its memory.** That is
good news for the trace and a hard ceiling on the project's distinguishing
property: **developmental provenance in Organica 1 has the horizon of the
organism's own memory.**

**How much history does it keep?** **Measured: the window's content age is at
most 1 cycle, spanning 2 distinct cycles.** The window holds 3,998 candidates and the
oldest was last stored one cycle ago. A *dead* structure's history is therefore
unrecoverable almost immediately; a *living* one's is recoverable indefinitely.

**And this corrected section 12.** The specification said the window was "the
more likely binding constraint", on the reasoning that it spans only 1.7
cycles. **That was wrong.** Surviving candidates are re-stored every cycle, so
a live ancestor stays in the window however old it is — **a lineage's depth is
not bounded by the window's recency; what bounds it is the death of an
ancestor.** The correction is recorded rather than quietly fixed.

**Two sweeps show the branches are reachable, not inert.** The window sweep
falls from 1.000 at the engine's window to 0.971 at 100 candidates (2 aged
out) to 0.000 at 25–50 (68 aged out). The depth sweep falls from 1.000 at
depth 7 to 0.809 at depth 3 to 0.221 at depth 1 (53 depth-truncated) — so
**the engine's depth limit of 7 is not binding; the chains are shorter than it.**
Both are diagnostics of the instrument, never criteria.


### 8.16 The acquisition experiment: pre-registered, not yet run

**The question, as it now stands.** Not *can a structure emerge?* but **can
experience create a structure that remains useful after the originating
experience is gone?** — and then, **does the organism carry structure forward,
reconstruct it from evidence, or do both under different conditions?**

**The design is pre-registered** in
[`docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`](ACQUISITION-EXPERIMENT-PREREGISTRATION.md),
committed before any cell is run.

### Two questions, kept apart

| | Question | Answered by |
|---|---|---|
| **Q1** | Did the organism retain the knowledge? | the organism's own state — current beliefs, current lineage, current support |
| **Q2** | Can the laboratory prove how it developed? | the laboratory's record — per-cycle snapshots, the store log, the trace |

A result on Q1 is not a result on Q2. The trace reconstructs what the organism
holds; it is evidence about Q2 only where the laboratory's record independently
covers the period in which the structure formed.

### Two diagnostics that shaped the design (design inputs, not predictions)

| Diagnostic | Result |
|---|---|
| A surviving structure's parent set is identical across consecutive cycles | **94.5%** of 3,883 structure-cycles |
| …but what do those links point at? | **87.2% active** (parent re-derived that same cycle) / **12.8% carried** (alive, not re-derived) — of 8,416 links |

**Read together: the lineage is re-derived, not carried.** The identical parent
sets are deterministic re-derivation, not copied edges. *(This corrected an
earlier reading of mine, which called the ~95 % identical sets "carried
forward"; the link-state measurement is the discriminating evidence.)*

### The engine's survival rule is asymmetric across layers

This is the single most important fact for the design:

- **Layer 1** (concept, phrase, loop, prediction) — `_natural_selection`
  (`sleep.py:1752-1802`) **reinforces** a structure whose key current
  experience re-produced, and otherwise **decays it ×0.8** and **prunes** it
  below `DEATH_THRESHOLD = 0.15`. `_candidate_key` returns `""` for every
  other type, so **nothing above Layer 1 is ever decayed or pruned this way**.
- **Layers 2–4** (meta, process, workflow, hypothesis, theory, question) —
  never decayed; they persist as rows while they stay in the window, and are
  **re-formed with recomputed parents** when the composition rules re-form
  them. Hypotheses die by their own rule: `conf < 0.15` and
  `support + contradiction ≥ 3` (`sleep.py:1499`).

**So "persistent reconstruction" is accurate for Layer 1 and misleading for
Layers 2–4**, where continuity is closer to row persistence with re-derived
edges. The experiment must not treat "the structure survived" as one thing.

### The design

**Six cells**: parent {removed, not} × source experiences {removed, not} ×
removal applied to the {observer, organism}.

**Removing a parent from the observer's reconstruction tests the trace.
Removing it from the organism's state tests the maintenance mechanism.** They
are different experiments, and the observer-side arm cannot corrupt the
organism — it can only expose whether the trace stays honest.

**Three outcomes, tracked separately and per cycle:** does the content
identity reappear; is the lineage still connected; does the belief still
support the preregistered task. The third is a **time course**, so a
crossover — content that persists and then stops being useful unless it is
re-derived — is detectable rather than invisible.

**The sharpest prediction is computed from the source, not fitted:** a Layer-1
structure whose key stops being produced is pruned after
`⌈log(0.15 / c) / log(0.8)⌉` cycles — 4 cycles from `c = 0.3`, 6 from `c = 0.5`.

### The control that matters

If continuity is persistent reconstruction rather than archival recall, then
**a perfect-recall system with no re-derivation is the harder baseline**, not
the easier one. The design therefore includes a **replay learner** — it
stores the episodes verbatim and regenerates nothing — scored on the same
three outcomes. If Organica beats it on *"structure that remains useful after
the experience is gone"*, that is a result worth the project. If it does not,
"persistent reconstruction" is decoration and must be reported as such.

### What it will not establish

Not that Organica learns. Not that the trace reconstructs *developmental
history* — it reconstructs the **present** lineage of surviving structures.
Not that the results generalize. And **not anything biological**: the
resemblance to how some biological systems are described is a motivation for
the experiment, never a claim about its result.


### 8.17 The acquisition study: the plan, the stop condition, and the road ahead

**The pre-registration is Revision 2**
([`docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`](ACQUISITION-EXPERIMENT-PREREGISTRATION.md)),
committed before any cell is run. **Nothing here has been measured against a
factorial cell.**

### What was wrong with Revision 1, and what fixed it

| Defect | Correction |
|---|---|
| The endpoint was **DI** — a *structural displacement* ratio, not a prediction score | a **ground-truth prediction score** on a fixed label set, with the exact predictions named |
| "Source experiences removed" did not say what derived memory survives | named **"episode removal with learned graph retained"**; `cooccurrences` and `tag_counts` survive and are said to; **the same rows are removed from every learner's store** |
| The cell matrix was not specified | **one table, the exact number of runs, a prediction for every cell** |
| Not an executable plan | target relation, warm-up/follow-up lengths, seeds, sample size, decision rule, and both baselines' algorithms, grids, memory accounting and test-time procedures all pinned |
| The audit build had no stop condition | **close A5 and A6, then tag, freeze and stop** — no feature may be added to the instrumentation |

### The plan in brief

**World.** `generate_cause_world`, 220 cycles × 8 events, `regime_cycles=110`,
`noise_rate=0.10`, no overlap, no decoys. The target relation is the generator's
own gold same-cause pair set.

**Phases.** Warm-up 0–19; **acquisition 20–109**; **follow-up 110–219** — and the
regime switches at cycle 110, exactly on the follow-up boundary, so the
acquisition phase saw the follow-up's dominant cause only at its 15 % minority
rate. That is what makes the follow-up a **transfer** test rather than a repeat.

**Endpoint.** For each evaluation event and each tag in a fixed vocabulary,
predict whether that tag appears in the next event. Ground truth is the
observed next event. Fixed denominator, so no learner can gain by scoring on a
different set. **Primary metric: F1 at 0.5**, with balanced accuracy and Brier
co-reported.

**Three scores, not one.** **Retention** — does the acquired structure still
predict after the source episodes are removed? **Transfer** — does it apply to a
regime it barely experienced? **Revision** — does the score improve with
continued learning? **Scored per seed, not per cycle**, paired by seed.

**The cell matrix — 10 runs per seed, 30 seeds, 180 engine runs.**

| Learner | Cells | Runs |
|---|---|---|
| Organica | P ∈ {none, org, obs} × E ∈ {pres, rem} | 6 |
| Replay learner | E ∈ {pres, rem} | 2 |
| Statistical learner | E ∈ {pres, rem} | 2 |
| Fixed-rule ceiling | — | 0 (a reference, not a run) |

**`P-none × E-pres` IS the untreated baseline** — it is not an extra cell on
top of six.

**Where the mechanism question lives.** In the `E-pres` cells the comparison
learners can read the raw episodes that Organica's cognition window has
already dropped, so **they have strictly more usable access than Organica** —
**a win for Organica is conservative.** In the `E-rem` cells they have nothing,
so those cells measure **Organica's retention**, not the head-to-head. **The
head-to-head is the `E-pres` comparison.** And the predicted dissociation is
cell 4: the organism retains everything while the laboratory's provenance is
broken — **Q1 and Q2 separated in the auditor's own hands.**

**"Same memory budget", operationally.** Identical raw rows and identical
removal for every learner. **Derived state is deliberately not equalised**,
because derived state *is* the mechanism under test. No baseline is handicapped:
each is swept over its declared grid and its best score is used, and the
comparator is the single best configuration across both baseline families,
selected on the **tuning split**, never on a scoring window.

**The decision rule, fixed.** 99 % bootstrap CI of the mean paired difference,
10,000 replicates, paired by seed. **Win** if the CI excludes 0 upward; **tie**
if it contains 0; **loss** if it excludes 0 downward. The study verdict is
exactly one of **"Reconstruction does work"** (wins transfer, loses neither
other), **"The comparator's mechanism wins"** (the comparator wins transfer),
or **"Inconclusive"**. **Every branch publishes** — a loss publishes as a loss.

**The audit build's stop condition — EXECUTED (2026-10-28).** Close **A5**
(field honesty) and **A6** (trace / counterfactual separation) — the only two
that were pending — regenerate the three probe arms, then **tag, freeze and
stop**. **All four steps are done**: A5 and A6 are closed with proof-of-firing
tests, the three arms are regenerated, and the instrumentation is **tagged
`audit-trace-v1`**. After that **no feature may be added to the
instrumentation**; a new requirement goes to the study's wish-list. The
instrumentation may be *fixed* if it is found wrong, but not *extended*. **A1,
A2, A3, A4 and A7 were closed and are not reopened.** The **package version
stays untagged** — the tag marks the instrumentation, not a release, which
keeps the three version namespaces separate.

### The owner's standing decisions (2026-10-26)
- **Decided (2026-11-01) — reusable knowledge: Option A.** A formally separate `V1.1-cap` diagnostic is authorised, because V1's cap-20 formation failure is already established and the capacity test put coverage at 98.2–100 % at cap 1,000, so a variant is the direct way to ask whether formed structure is usable without touching the V1 finding or the frozen engine. Revision 1 of the draft closes the four conditions you set — precision now carries its denominator (engine top-k max 0.3438 over 36 cells; the 0.4500 is a 9-of-20 filtered set at coverage 0.0804, below its own 0.50 gate), replay/bigram/decayed-bigram are the primary same-experience bar with the cell counter demoted to a separately reported privileged reference, transfer now requires a declared 25 % of the law's edges withheld from formation, and the seeds, 98.33 % paired bootstrap and calibration/confirmatory split are fixed. **Promotion to a preregistration is still an owner step, and no cell has run.**

> **Added 2026-11-01 — freeze point on the divergence line.** The owner called the freeze after the fourth correction in this line (identical pools, the one-cycle lag, the divergence-specific onset reading, and C1). *Rationale:* each correction removed a claim rather than confirming one, and the next question — which upstream write admits candidates at cycles 3–6 — needs a new observer rather than another reading of the existing artifacts. Nothing is read further out of those artifacts; the record stands as narrowed.

**V2 is not cut. The live study is not restarted. V2–V5 are not run. No further
open-ended audit work.** The sequence is: **finish the audit build → freeze it →
run the acquisition experiment → compare against the replay learner → publish
whatever happens → only then discuss V2.**

### Two things the review caught that were not about the plan

**The endpoint question is the one that matters.** A metric imported from
another study can measure a completely different quantity. DI was the right
metric for a *displacement* claim and the wrong one for a *prediction* claim,
and nothing about it looked wrong until someone asked what it actually
measures.

**The charter drifted from the engine.** `docs/DESIGN_LAWS.md` Law II still
says every primitive traces its `parent_ids` DAG *"back to Generation 0
empirical events"*. **The engine has never done that** — the chain terminates
at Layer 1, and the structure→event link is a *count*, not a pointer. The
README's restatement was corrected; the law itself is left as written with the
disclosure attached, because **the frozen engine's constitution is the owner's
decision, not a documentation fix.**

**Owner ruling, 2026-10-30: keep the discrepancy disclosed, and do not amend the law
yet.** The amendment waits on a question the owner has framed explicitly: *is Law II a
design requirement, or a description of V1's actual behavior?* Those two readings imply
different amendments, and rewriting the law to match the frozen engine would erase the
distinction that makes the discrepancy meaningful. `docs/DESIGN_LAWS.md` is therefore
**not** edited; the disclosure stays where the audit put it — facts sheet AD5, finding 33,
and `papers/00_intelligence_through_structural_descent.md` §Law II.


---

### 8.18 The five claims, narrowed (2026-10-26)

**What this section records.** A review of the project's own *summary* found
five sentences that were wider than the checks behind them. None of the
measurements changed; all five headlines were narrowed, and the corrections
were made **before** the acquisition experiment ran, so the next study is not
the one that has to carry the overstatement.

Each narrowing is written into the document that made the claim: the README,
`docs/PHASE-L-SYNTHESIS.md`, `docs/V1-SYNTHESIS.md`,
`docs/AUDIT-TRACE-SPEC.md`, `docs/EMERGENCE-CRITERIA.md` and this manual.

| # | The claim as it stood | What it actually measured | Now says |
|---|---|---|---|
| 1 | "Revision exists" | Phase L's DI/PI are **structure-retention** indices | **Structural displacement.** Belief revision is a separate capability question — and K2 was a clean loss (0.4111 vs 0.9846) |
| 2 | "The 3:1 transition is remarkably stable" | Resampling the *same* measured seeds | Robust **within this engine, world family and support-ratio axis**; alternative bootstrap seeds test **resampling stability, not new worlds** |
| 3 | "Development is path-dependent" | Schedule changes (multiset **and** order together) | **Path dependence** supported; **strict order dependence not tested** — needs the multiset held fixed |
| 4 | "Transfer is open" | One measured axis: cross-domain, **−0.486** | **No positive transfer has been demonstrated, and the measured cross-domain result was negative**; other forms remain untested |
| 5 | "An independently auditable developmental record" | Reconstruction from the engine's state | **Independently reconstructed**, not **replicated by another lab**; the trace covers surviving, current structures |

**Why this is finding 24 and not a footnote.** The project's discipline has
always been about the *measurement*: measure, don't infer; pre-register;
never revise a prediction to fit a result. The same discipline has to reach
the **summary**, because the summary is what a reader takes away and repeats.
A review of the acquisition plan found that **DI** — an endpoint imported from
another study — measured a completely different quantity from the one it was
asked about. That defect was in a *plan*. These five were in the *headline*,
and they had already shipped into the README and three synthesis documents.

**The compressed project state (2026-10-26).** The framing the project now
leads with:

> *Organica demonstrably changes its internal structure as experience and
> curriculum change. Under one tested pressure axis, later structures can
> abruptly displace earlier ones. The project has built a strong instrument for
> auditing surviving state and implemented decisions. It has not yet shown that
> these structures yield useful knowledge or positive transfer; the acquisition
> benchmark's first run did not change that — on a compositional task with a
> genuine generalization gap, the frozen engine asserted almost none of the
> world's relations and lost to simple transition counting. The benchmark is
> sound, the obstacle is one named and measured bound, and the organism is not
> yet able to use it.*

**What this does not change.** The protocol verdict `H3-L — INCONCLUSIVE`
stands. The Phase L characterization stands. The six negative task families
stand. No number changed, no artifact was re-read, and no criterion was
reinterpreted — this was a correction to *language*, made against the
existing record, and recorded rather than quietly applied.

### 8.19 The endpoint audit, and the campaign that stopped at its own gate (2026-10-28)

**The short version.** The acquisition experiment's **endpoint** was audited
and found to be measuring the wrong thing. Seven defects were confirmed
against the code. The benchmark was rebuilt around a **compositional task**
whose gate passes. A separate, parallel run then measured the **frozen engine**
on that task and found it **fails the preregistered acquisition gate on every
inspected seed**. The campaign stopped there. **Transfer was not measured, and
it is not a transfer failure.**

**Three different questions, three different answers.** These are easy to
conflate and they were run by different pieces of work:

| Question | Answer | Where |
|---|---|---|
| Is the benchmark discriminative — is there room for something better than transition counting? | **YES.** Gap **+0.1035 nats**, 99 % interval **[+0.0996, +0.1074]**, lower bound clears the 0.05-nat bar across 30 independent worlds | `docs/acquisition_compositional_gate.json` |
| Does the frozen engine's own state contain the world's relations? | **NO.** Asserted coverage **0.0 % – 2.7 %** (0–3 of 112 edges) while raw temporal memory holds **112 / 112 (100 %)** | `docs/GATE13-PREFLIGHT-AUDIT.md` |
| Did Organica beat the baselines on the task? | **NO.** Organica **0.453018** against Replay **0.347521**, Statistical **0.347273**, base rate **0.409581** | `docs/PILOT-0-INSTRUMENTATION-AUDIT.md` |

> **The +0.1035 is the benchmark's headroom, not an Organica margin.** The
> compositional probe runs **no engine** and scores no learner. It answers
> *"is there room for something better than counting?"* — yes. It does not
> answer whether Organica occupies that room. Reading one as the other turns a
> task-validity result into a capability result.

**The cause of the failure, measured rather than inferred.** `_build_predictions`
sorts prediction candidates by raw temporal count and truncates at
`MAX_PREDICTIONS = 20`. On the compositional stimulus the two tags of a cell
co-occur in *every* event of that cell, so within-cell pairs accumulate far
higher counts than the cross-cell transitions that carry the law — the top 20
slots fill with within-cell pairs and the cross-cell edges are discarded.
Raising **only** the cap to 1,000, same engine, same stream, same five seeds:

| Seed | Cap 20 | Cap 1,000 |
|---|---|---|
| `20261101` | 0 / 112 (FAIL) | 110 / 112 = **98.2 %** (PASS) |
| `20261102` | 1 / 112 (FAIL) | 112 / 112 = **100 %** (PASS) |
| `20261103` | 1 / 112 (FAIL) | 112 / 112 = **100 %** (PASS) |
| `20261104` | 0 / 112 (FAIL) | 112 / 112 = **100 %** (PASS) |
| `20261105` | 3 / 112 (FAIL) | 112 / 112 = **100 %** (PASS) |

So it is a **capacity limit**, not a missing signal, not a readout defect, and
not a property of the world. Organica's readout then lost because the asserted
structure is mostly within-cell co-occurrence — so it answers *which cell the
context is in* when the task asks *which cell comes next*.

> **Refined on 2026-10-28 — "bottleneck" is not "deepest cause".** Four
> further diagnostic probes (`docs/GATE13-CAUSAL-ACCOUNT.md`) measured this
> bound and found it is **not the deepest cause**. Coverage is a steep monotone
> dose-response in the cap — **0.00 → 0.04–0.07 → 0.09–0.18 → 0.99–1.00** — and
> needs **240–244** asserted edges, about **12×** the budget. Switching from a
> global to a **per-source** allocation rule does **not** help (per-source K=10
> retains 258–286 edges for coverage 0.72–0.77, where the global rule reaches
> 0.95–0.97 at 320), and **precision never exceeds 0.3438** at any budget under
> either rule. A 1-tag stimulus removes the within-cell pairs *by construction*
> and still fails on **0 of 6** seeds (asserted coverage 0.1719–0.1953).
> **The deeper constraint is precision**: in a candidate space where the
> world's edges are about a third of the rows and are not clustered at the top
> of any frequency ordering, **no frequency-based selection can find them**.
> The V2 question is therefore narrower and sharper than "keep more under a
> bound": can the organism tell which of its vocabulary items are its own, and
> can it rank candidates by something other than raw frequency? **No V2 build
> is authorised by this.**

**An instrument defect found while reconciling the two results.** Two functions
implemented "Gate 13" under one name. The runner used the **asserted** basis,
as Amendment 1 of the pre-registration requires, and failed correctly. The
harness used the **raw temporal** basis, returned **100 %**, and passed — on
the same seed, on the same world — and its test asserted `passed is True`. A
gate that cannot fire on the condition the study exists to detect is
decoration. **Fixed:** the harness now computes both figures, gates on the
asserted one, records `coverage_basis = "asserted_structure"`, and exposes the
cap-raised treatment so the failure can be *attributed*. The test now asserts
that Gate 13 **fails** on the frozen engine, that the treatment arm **passes**,
and that the aggregate prerequisite check reports the failure at the
preregistered threshold.

**Seed bookkeeping.** Amendment 2 defined the confirmatory sample as thirty
seeds, `20261101`–`20261130`. Amendment 3 designated `20261101`–`20261105` as
diagnostic. **Five of the thirty confirmatory seeds are now diagnostic**;
a usable confirmatory sample is **25** (`20261106`–`20261130`). The frozen
amendment text is not rewritten — the consequence is recorded in
`docs/ACQUISITION-ENDPOINT-AUDIT.md` §8.6. Any future campaign must
re-specify its seed set rather than inherit a partly-spent one.

**Where the study stands.** Pre-registration **Revision 3**, with
**Amendment 3** recording the stop. The 600-cell factorial did not run.
Seeds `20261100`–`20261105` are permanently diagnostic. **No verdict on
transfer or revision exists.** The compositional task remains a valid,
pre-registered instrument — it is the thing a future V2 would be measured on,
not a result about V1.

**Commands.**

```bash
# the task gate — no engine run
python benchmarks/acquisition_compositional_probe.py

# the acquisition gate on the frozen engine
python benchmarks/acquisition_harness.py --gate 13

# the whole harness gate set
python benchmarks/acquisition_harness.py --gate all

# proof-of-firing tests (the Gate 13 arm is slow: two 120-cycle runs)
python -m pytest tests/test_acquisition_harness.py -q -k Gate13
```

**Do not say** that Organica generalized, transferred, or revised on this
task. It did not get that far. **Do say** that the benchmark is valid, the
frozen engine cannot currently reach the state the benchmark asks about, and
the reason is one named bound.

**See also:** `docs/ACQUISITION-ENDPOINT-AUDIT.md` (the audit record),
`docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` (Revision 3 + Amendment 3),
`docs/ORGANICA-V2-DESIGN-BRIEF.md` §9.6–§9.7,
`docs/V2-CAPACITY-DESIGN-BRIEF.md`, journal §51, and finding 25.

---

### 8.20 Formation versus utilization: the harness, the timing pass that found a confound, and the amendment that closed it (2026-10-30)

**What was built.** `benchmarks/formation_utilization.py` implements the
protocol committed at `8536d9a`: three paired arms — **A** (cap 20, the
published failure), **B** (cap 1,000, formation at the measured precision
ceiling) and **C** (cap 1,000 with the generator's support admitted at Layer 1,
utilization *given* correct structure) — plus a size-matched shuffled-oracle arm
for the no-leakage audit. The oracle is materialized from the generator's own
parameters before any arm runs: **128** permitted pairs on T2 (**112** of them
the training-stream edges) and **272** on T1 (**167**). The filter lives in the
harness, rewrites `temporal` before the engine's cap, and leaves `freqs`
untouched. `tests/test_formation_utilization.py` adds **44 tests**; the suite is **237** with the diagnostic's 20 checks:
every audit has a proof-of-firing case, the fixed temporal basis has an
equivalence test and a load-bearing test, the shuffled filter's shape is
asserted, `analyse()` refuses a one-seed verdict, and the recording subclass is
proven behavior-neutral — two stock runs and one recording run produce identical
stores and candidate dumps.

**The timing pass found a confound (D1).** The first one-seed pass, on
`20261100`, measured **72.8 s** per engine run and passed every applicable
audit — but the arms did not share a temporal graph. At the end of acquisition,
on T2, **32** edges differ (374 vs 380), the permitted candidate streams differ
on **59 of 131** cycles,
first at cycle 6, with **248** missing and **172** extra; on T1, **21** edges
differ (362 vs 351), **107 of 160** cycles differ, first at cycle 40, with
**274** missing and **120** extra. `_record_temporal_edges` is called only for
world events, but its window is the last three **rows** of `events`, and sleep
rows are rows: the last sleep rows of cycle k occupy window slots for the first
world events of cycle k+1, and their tags become `tag_from` values. An admission
filter therefore changed the next cycle's temporal input. The arm table's
*"all other layers and all counts are untouched"* was false, and a C advantage
could have been self-sourced support. The pre-amendment artifact is preserved as
`docs/formation_utilization_timing_pre_amendment.json`; its C and S cells are
**not** a result of the amended design.

**Amendment 1 (2026-10-30, protocol §12).** Arms C and S read **arm B's
per-cycle temporal graph** instead of their own. B is run first, unmodified, and
the graph `_load_temporal()` returns is recorded at the start of each sleep
cycle; C and S are given that graph for the same cycle index, and each run
asserts it consumed exactly one graph per cycle. A and B are unchanged, and
`organica/` is untouched — the engine still writes each arm's own `precedes`
table, which Layer 1 no longer reads for C and S. The filter itself is
unchanged. **Why not make every arm sleep-blind:** that would change B, and with
it A1's 98–100 % premise and A3's 0.3438 band, both measured on B as shipped;
re-measuring either on the campaign's own data is forbidden by rule 19.

**What it fixes, and what it does not.** The feedback path is closed at the
layer that reads it: **A8** checks, every cycle, the graph each admission arm
**actually read**, the eligible pair stream it built, the evidence on shared
pairs, and that the two arms' logs cover the same cycles; the run separately
asserts the graph list is consumed exactly once per cycle. A8 is a gate
with proof-of-firing tests (differing graph, differing stream, cycle-count
mismatch, differing evidence) and a load-bearing test (a perturbed graph changes
the store; with the filter off the fixed-basis run reproduces B's store and
candidate dump, with wall-clock fields normalized). It
does **not** make B sleep-blind — B's graph still contains B's own sleep-row
tags, and C inherits them — so the study still says nothing about self-sourcing.
C's own payload and prior still differ; that is the treatment. And C is a
counterfactual trajectory on B's evidence, not an independent organism: a C
result is **admission filtering at fixed temporal evidence**, never "the engine
with this filter installed".

**The amended timing pass.** Eight runs on `20261100`: **72.2 s per run**
(265 s T2, 316 s T1), projecting to **3.6 h** for the 180 arm runs, **1.2 h** for
the 60 shuffled-audit runs and under a minute for the comparators — **4.8 h
sequential**. Every applicable audit passes on both tasks. T2: A1
(0.0000 / 1.0000 / 1.0000); A2 (**14,455** permitted candidates over **131**
cycles, admitted exactly); A3 (B precision **0.3373**, inside the band; C's
admission precision 1.0); A4; A5; A6 (shuffled Layer-1 coverage and precision
**0.0000**, transfer **0.5007** against C's 0.3661); A7 (**95.0 %** of readout
weight from Layer 1); A8 (**131 cycles**, **75,488** eligible-pair checks, the
graph and stream identical; the engine's own tables still differ by **28**
edges, unread). T1: A1 (0.1497 / 0.9222 / 0.9222); A2 (**21,057** / **160**);
A4; A5; A7 (**97.3 %**); A8 (**160** cycles, **80,200** checks, **15** unread
edges). A3 and A6 are **not applicable** on T1 with their reasons recorded: the
band was measured on T2, and the shuffled filter retains **144 of 272** permitted
pairs, so no size-matched wrong filter exists there.

**B reproduces to the reported precision; C is a new cell.** B is unchanged by
the amendment, and its cells agree with the pre-amendment pass at the artifact's
four decimals — T2 retention/transfer/revision **0.4244 / 0.4254 / 0.4212**, T1
**0.2370 / 0.2359 / 0.4014**, Layer-1 precision **0.3373 / 0.5404**. At full
precision the untouched A arm also moves in the fifth decimal (up to **1.4 × 10⁻⁵**),
so the check is reproducibility to about **10⁻⁵**, not bit-identity; that is a
property of the engine and the readout, not of the amendment. C changes by
design: readout coverage is now **1.0000** on T2 and **0.9222** on T1 (the same
as B), and its scores are T2 **0.3656 / 0.3661 / 0.3490**, T1
**0.2350 / 0.2346 / 0.3890**. It clears the bar on **2 of 6** task-limbs (both
revision) and is worse on transfer by **0.0154** nats (T2) and **0.0229** (T1).
One seed is not a verdict and these numbers may not be quoted as a win or a
loss; they are recorded because an oracle-admitted arm that does not clear a
counting baseline on its own timing seed is a warning the campaign should carry.
The pre-amendment C and S cells are **not** comparable with the amended ones and
must not be presented as an improvement: they were a different design, measured
under the confound.

**What the campaign now means.** Every applicable audit passes, so the
instrument was ready; the campaign was subsequently run on 2026-10-30 and is
reported in [§8.21](#821-the-formation-vs-utilization-campaign-the-verdict-and-what-it-does-and-does-not-mean-2026-10-30).
A summary claim from C must carry *given B's temporal evidence* in the same
sentence, and a C result cannot be used to argue that self-sourcing was or was
not the cause of anything. The protocol's question — does holding the relation
predict better than the strongest simple baseline — is answered by B (unchanged)
and C (the conditional ceiling), with the §7 mapping in §8.21. The T2 bar is a
cell-level counter that is granted the latent cell structure, so "data-only"
is too wide a name for it; the results document says so.

**Commands.**

```bash
# the timing pass (~10 minutes; writes the two timing artifacts)
python benchmarks/formation_utilization.py --timing

# the campaign (the built-in path; the 2026-10-30 run used a resumable wrapper)
python benchmarks/formation_utilization.py --campaign --seeds 30 --workers 8

# the command the 2026-10-30 run actually used (wrapper, 60 checkpointed units)
python .scratch/run_campaign_resumable.py --seeds 30 --workers 10
```

**Do not say** the oracle arm "failed to transfer": that was one timing seed
and no verdict. The campaign has now run, and C loses the bar rather than
failing to transfer; **do say** the harness is built, the confound was measured
and closed by a recorded amendment, the campaign is complete, and the verdict
is in §8.21.

**See also:** [`docs/FORMATION-UTILIZATION-PREREGISTRATION.md`](FORMATION-UTILIZATION-PREREGISTRATION.md) §12,
`docs/formation_utilization_timing.json` (the amended artifact) and `.md`,
`docs/formation_utilization_timing_pre_amendment.json` (the diagnosis),
AGENTS rule 18, and finding 38.

---

### 8.21 The formation-vs-utilization campaign: the verdict, and what it does and does not mean (2026-10-30)

**What ran.** The amended protocol's 30 confirmatory seeds (`20261101`–`20261130`),
both tasks, four arms per unit (A, B, C, S) and three comparator fits: **60
units, 240 arm runs**. The engine is **0.10.0** and no engine file changed. The
campaign was executed through `python .scratch/run_campaign_resumable.py --seeds
30 --workers 10`, a resumable wrapper over the harness's own `run_task_seed`;
each unit was checkpointed, no unit failed or was re-run, and the artifact was
assembled with the harness's own `analyse()` and renderer. The artifact's
per-unit timings sum to **12.72 worker-hours**; the run used 10 workers.
All **60/60** units are `campaign_ready`.

**The pre-committed verdict.** Both formed arms lose transfer on both tasks, so
§7's "both lose" cell fires on both tasks: **"utilization fails even with correct
structure" → V2 targets the use path (retrieval / activation / readout)**. The
summary claim is **not supported**. The failing limbs are **transfer and
retention**; revision is not a failing limb.

| Task | Arm | Retention | Transfer | Revision |
|---|---|---|---|---|
| T1 | B | −0.0302 | −0.0296 | +0.0877 |
| T1 | C | −0.0267 | −0.0262 | +0.1002 |
| T2 | B | −0.0797 | −0.0795 | −0.0676 |
| T2 | C | −0.0230 | −0.0227 | +0.0007 (tie) |

`d = bar − arm`; positive favours the arm. Intervals are 98.33 % percentile
bootstraps over 10,000 replicates, paired by seed (n = 30). The full eighteen-cell
table is in the results document.
The protocol's §7 writes the subtraction in the opposite order and then states
the win rule for this orientation; the artifact and this table use `bar − arm`,
which is the orientation the rule requires. The discrepancy is notation, not
analysis; no verdict changes.

**The label is not the magnitude.** C closes **65.2 %** of A's transfer gap on T1
and **79.9 %** on T2 (retention 65.2 % / 79.6 %), leaving **0.0262** and
**0.0227** nats. It improves over B by **0.0034** (T1) and **0.0568** (T2). So
"fails" means *does not clear the bar*, not *no use*; the result is not "the
engine cannot use structure". C wins T1 revision by **0.1002** — against Replay,
which is the bar there and cannot revise — and ties T2 revision.

**The bar's name.** The protocol calls the comparator "the strongest data-only
learner". On T2 the bar is the **cell-level latent-state counter**, which is
granted the latent cell structure (`fit_cell_counter` takes `tag_to_cell` from
the generator; the docstring says "here granted"). It is not data-only. That is
a naming defect, not a deviation: the counter is a declared member of the
statistical-learner family (acquisition protocol §6.3). The verdict does not
depend on it: post hoc, C still loses T2 transfer to Replay by **0.0208**
[−0.0224, −0.0192] and to the bigram by **0.0187** [−0.0205, −0.0168]; on T1
the bar is already Replay and C loses by **0.0262**. C's oracle (the full
transition support) is stronger than the counter's (the four-cell map), so the
loss is not explained by a better baseline oracle.

**What it does not mean.** It is not discovery: C is given the support, B is the
discovery arm, and B also loses transfer on both tasks. It is not a
self-sourcing result: B's graph still contains B's sleep rows and C inherits it.
It is not "the engine with this filter installed": Amendment 1 holds the
evidence fixed, so C is a counterfactual trajectory. It does not localize the
defect inside the use path. It does not generalize beyond T1/T2, and it does not
authorise a V2 build.

**Audits.** 60/60 units ready. A1 coverage: T2 A **0.0000–0.0625** vs B/C
**0.9643–1.0000**; T1 A **0.1553–0.2549** vs **0.8812–0.9935**. A2:
**473,351** (T2) and **612,005** (T1) permitted candidates, **0** mismatches, the
cap never bound. A3: B precision **0.3182–0.3394** on T2 (band 0.3543), C
admission 1.0. A6: shuffled transfer **0.4957–0.5052** vs C **0.3569–0.3726**,
Layer-1 coverage 0.0. A7: **94.0–96.2 %** (T2) and **96.2–97.7 %** (T1) of
readout weight from Layer 1. A8: **2,539,326** (T2) and **2,408,224** (T1)
eligible-pair checks, **0** mismatches, own-table symmetric difference
**17–93** / **0–19** edges (unread). A3 and A6 are not applicable on T1, with
the reasons recorded before the campaign. **Reproducibility:** the campaign artifact reproduces
exactly only under `PYTHONHASHSEED=0`; its command did not record the seed. The diagnostic's
self-test measured a **4.7e-4** drift without the pin, then reproduced exactly with it. This is a
provenance gap, not a change to any verdict.

**Do not say** "utilization fails" without the magnitude: C closes most of A's
gap and wins revision on T1. **Do say** the pre-committed mapping returns
"utilization fails with correct structure" on both tasks, C loses transfer by
0.0262 / 0.0227 nats, B loses it too, and the V2 target is the use path — with
the bar named as the cell-level counter, not a data-only learner. **No V2 build
is authorised.**

**See also:** [`docs/formation_utilization_results.md`](formation_utilization_results.md)
(generated from the artifact), `docs/formation_utilization.json` / `.md`,
protocol §7 and §12, finding 39, journal §65.

### 8.22 The use-path diagnostic: the step to V2 authorization (2026-10-30)

**The record is corrected, and the correction is visible.** The campaign's ceiling condition is now recorded as **observed**: with the generator's support admitted at Layer 1 and arm B's temporal graph fixed, arm C lost transfer on both tasks (T1 −0.0262, T2 −0.0227) while holding correct internal structure. The V2 brief's §9.8 carries the record claim; gate 5 now says the *specific-failure* condition is met and the *mechanism* condition is not; and the old §11 "NOT OBSERVED" entry is preserved and marked **SUPERSEDED**, not erased.

**The question, in order.** The diagnostic does not begin by asking which component binds. It asks first whether there is **measurable room** in the use path at the evidence the campaign had, using the generator's true conditional as the ceiling. Only if the room exists does it ask which component — retrieval/provenance (D1), activation/aggregation (D2), or the readout form (D3/D4) — accounts for part of it.

**The gate that can invalidate the whole run.** D0 must reproduce the campaign's arm-C scores for all 30 seeds and all three limbs within **1e-4**, under **`PYTHONHASHSEED=0`**. The self-test reproduced exactly with the pin and drifted by **4.7e-4** without it, which is a provenance gap in the campaign, not a change to its verdict. If the gate fails, the outcome is **AUDIT REQUIRED** — no room estimate, no mechanism mapping. The decomposition would be of a different object than the one that produced the ceiling result. The result document's first section is the gate, and the generator refuses to emit a mechanism section if it failed.

**Result (2026-10-30): AUDIT REQUIRED.** All 60 units ran (30 seeds × 2 tasks; 180 seed-limbs over the three scored limbs). D0 reproduced **162 of 180** seed-limbs within **1e-4** and failed **18**; the largest absolute difference was **0.004386** (T1 seed `20261128`, revision). Every other control passed — the D2 constants are unchanged and provably independent of the campaign seeds, and every admitted unit had an attribution and a denominator. The pre-committed outcome fired: **no room estimate, no variant effect and no component are reported**. The candidate cause recorded at the time was the engine's `recent()` ordering — sleep rows stamped in the same `time.time()` tick come back by `time DESC` with no `rowid` tiebreak, while `structure_edges` keeps the first snapshot per candidate id. The audit of 2026-10-30 tested that hypothesis with a harness-side `rowid` tiebreak and **did not support it**: the tiebreak changed neither the per-type table nor any score, and both read orders were repeatable. The cause is upstream of `recent()` and is not identified. The mechanism condition of gate 5 remains unmet, and the next test is a hash-seed sensitivity sweep.

**Audit observation (2026-10-30).** A post-hoc check compares the C arm's frozen-candidate table in the campaign artifact with the diagnostic's, unit by unit. It is an audit instrument, not a finding, not a gate and not a protocol amendment. **Cross-tab (source: `docs/use_path_diagnostic_structure.json`):** 51 identical/pass, 0 identical/fail, 8 different/fail, 1 different/pass. Every failing unit has a different table; no unit with an identical table fails; T2 `20261122` differs structurally while all three scores stay inside the D0 tolerance, which is the negative control that makes the indicator credible. The divergence is localised to the frozen candidate set, before scoring; the cause is not established. The campaign ran from an uncommitted working tree, so a stable code-revision difference must be excluded before tie order is blamed. The audit is now three layers: repeatability (paired no-tiebreak and `rowid`-tiebreak runs), structural reproduction (the per-type table), then score reproduction. D0 remains score-based and unchanged. See journal §68.

**Audit result (2026-10-30).** The three-layer audit ran on the eight failing seeds: 48 runs (8 seeds × 2 configurations × 3 repeats), each against a fresh database, with `PYTHONHASHSEED=0` asserted and the `rowid DESC` tiebreak applied in-process. **The tie-order hypothesis is not supported.** Both configurations reproduced their own per-type table 3/3 on 8/8 seeds, and the two configurations produced identical tables and identical scores on 8/8 — the tiebreak changed nothing. Neither configuration reproduced the campaign's per-type table on any seed (0/8 and 0/8), so layer 3 was not entered. The no-tiebreak runs reproduce the diagnostic exactly on 8/8, which proves the audit is a re-run of the D0 object rather than a different measurement. The divergence is therefore upstream of `recent()`'s tie order; the audit does not name it. Two candidates remain, both unrecorded: a campaign-time harness revision (the harness was uncommitted when the campaign ran) and the campaign's execution environment (the artifact records neither the hash seed nor the tie order). The structure check constrains the first — 51/60 units reproduce under the current pinned code — but does not exclude a difference confined to ordering-sensitive units. D0 remains score-based and fired; the diagnostic remains **AUDIT REQUIRED**, and no room, mechanism, component or V2 brief follows. See [the audit](USE-PATH-AUDIT.md) and journal §69.

**The outcomes, pre-committed.** The diagnostic can return **EVIDENCE-LIMITED** (room below 0.01 nats on both tasks and no arm helps: the use path has no measurable room at this evidence, so the target moves upstream to formation/estimation), a **MECHANISM CANDIDATE** (a named component), **UNKNOWN USE-PATH MECHANISM** (room exists but the tested family cannot reach it), **TASK-DEPENDENT**, or **AUDIT REQUIRED**. Evidence-limited is a successful result: it can disprove a class of use-path V2 concepts before implementation.

**D2 is constants-only.** The type weights are declared in the protocol — Layer 1 `= 1.0`, every other type `= 0.5` — not fitted, not calibrated, and not influenced by the campaign's seeds. If they were chosen after seeing a score, D2 would be a tuned retrospective analysis, not a diagnostic.

**What it can and cannot do.** It was designed to select a component for a V2 **brief**; it did not, because D0 failed. It cannot authorise a V2 build, and it does not turn C into a deployable learner: C is given the support and reads B's evidence. The owner's build decision remains separate.

**Where it lives.** [`docs/USE-PATH-DIAGNOSTIC-PREREGISTRATION.md`](USE-PATH-DIAGNOSTIC-PREREGISTRATION.md) (frozen by SHA-256 in `docs/use_path_diagnostic_freeze.json`), `benchmarks/use_path_diagnostic.py`, `tests/test_use_path_diagnostic.py`; the artifact is `docs/use_path_diagnostic.json`, the post-hoc per-type check is `docs/use_path_diagnostic_structure.json`, and the generated document is `docs/USE-PATH-DIAGNOSTIC-RESULTS.md`. **The result did not select a component. No V2 build is authorised.**

---

## 9. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `study_health.py` says "NO CYCLES PARSED" | the daemon has not written a cycle yet, or `organica.log` is missing | `start_organica.bat`, then wait ~40 s |
| daemon not running | it was killed, or the console it was started from closed | `start_organica.bat`; for durability install the Scheduled Task ([§4.2](#42-making-it-survive-90-days-)) |
| `theories` stuck at 0 | the stream cannot produce competing expectations | run `python benchmarks/g5_gap_diagnostic.py --cycles 10` — if `g5_eligible_subjects` is 0, the stream is the problem |
| `duration_ms` climbing | substrate growth | `python benchmarks/substrate_probe.py`; check that `substrate_rows_pruned` is non-zero in the log |
| `sleep_cycle` went backwards | the counter regression | stop the daemon, restore `organica/memory.py`'s `sleep_cycles` handling, restart |
| `status: failed` | an exception in the sleep cycle | read `console.log` for the traceback |
| `snapshots/` empty or `{}` | the observer ran against an empty/partial log | the writers now refuse to write empty artifacts; re-run after the daemon has logged cycles |
| "no such table: events" | you ran a script from the wrong directory | `cd C:\Users\monte\anti\project-organica` first, or pass absolute paths |
| disk filling up | a stray `.db` copy, or retention disabled | check `memory.db.run1_20261020` (898 MB, archived run-1 evidence — keep or delete deliberately) |

**Stopping the daemon cleanly:**

```powershell
Get-CimInstance Win32_Process -Filter "Name like '%python%'" |
  Where-Object { $_.CommandLine -match 'run_continuous' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

The log and the database are both safe to stop and restart — the counter is monotonic and the log appends.

---

## 10. File map

```
project-organica/
├── organica/
│   ├── memory.py              # SQLite substrate: events, co-occurrence, temporal
│   │                          #   graphs, tag counts, cycle counter, retention
│   ├── sleep.py               # the 8-layer sleep pipeline (68 KB — the core)
│   ├── streams.py             # the study event stream + the four reproduction domains
│   ├── branch_streams.py      # branch-structured stimuli (triangle lattices) for the V2 gates
│   └── scale_streams.py       # worlds of increasing information content (the H24 ladder)
│   ├── ground_truth_worlds.py  # synthetic causes, regime switches, and hidden labels
│
├── run_continuous.py           # the study daemon
├── start_organica.bat          # daemon launcher (appends, never truncates)
├── run_daily_observer.bat      # daily snapshot + event journal
├── run_weekly_monthly.bat      # weekly + monthly + velocity snapshots
├── run_dashboard_and_api.bat   # Inception API + Streamlit dashboard
│
├── metrics.py                  # log parsing + metric aggregation
├── observation/
│   └── metrics_observer.py     # time-window snapshot writers + event journal
│
├── dashboard.py / dashboard_ui.py / inception_api.py
│
├── benchmarks/
│   ├── benchmark_suite.py         # BM1–BM5 growth benchmarks
│   ├── cross_domain_validation.py # Phase F: 4 domains -> docs/validation_report.json
│   ├── endurance_soak.py          # Phase G endurance harness
│   ├── g5_gap_diagnostic.py       # WHY G5 does or does not happen
│   ├── stream_sweep.py            # choosing the study event stream
│   ├── cold_start.py              # how much assistance does it need? (unassisted bootstrap)
│   ├── ablation_study.py          # ten ablations: which mechanisms are load-bearing?
│   ├── ablation_metrics.py        # the metric contract (PA, IP, SCR, SS, LC, CD, CDT, NSR, ES)
│   ├── ablation_verify.py         # perturbation census: did each ablation actually change anything?
│   ├── development_probe.py       # is the machinery sound? cap census, plateau, vocabulary
│   ├── instrumentation_audit.py   # is the observation channel saturated? pre-cap pools, pressure
│   ├── archive_run.py             # snapshot the daemon log into a per-cycle series
│   ├── gate_validation.py         # does the proposed gate predict theory formation? (V1 data)
│   ├── mbsd_census.py             # exact gate density, with its denominator, over all 11 conditions
│   ├── branch_sweep.py            # first branch-stimulus sweep (superseded by branch_sweep2)
│   ├── branch_sweep2.py           # lattice sweep: gates + sustainment + the prediction window
│   ├── branch_diag2.py            # why does a stimulus die? edge survival, one layer at a time
│   ├── freq_scope_probe.py        # is the tag-frequency scope the collapse mechanism?
│   ├── gate_check.py              # the official launch-gate re-run
│   ├── force_matrix.py            # the six-colony Tier-1 campaign + G1 verification
│   ├── run_matrix.py              # launches the six colonies in parallel, hash seed pinned
│   ├── metric_sensitivity.py      # can each metric actually move across colonies?
│   ├── seed_noise.py              # the within-process seed floor
│   ├── process_noise.py           # the process-level floor a delta must actually beat
│   ├── v1_impact.py               # V1 before vs after the scope fix, incl. interpretations
│   ├── verdicts.py                # every pre-registered prediction, forced into a bucket
│   ├── discovery_report.py        # the inventory breakdown + the cumulative discovery curves
│   ├── scale_ladder.py            # the H24 ladder: worlds of increasing information content
│   ├── scaling_ladder.py          # resolution or replication? within-run SE vs between-world SD
│   ├── heldout_prediction.py      # Organica vs Markov and decayed association on held-out events
│   ├── ground_truth_recovery.py   # score recovered structure against hidden-cause pair ground truth
│   ├── phase_h_campaign.py        # ten-seed prediction/recovery league with bootstrap intervals
│   ├── regime_shift.py            # Phase I online surprise-based regime-shift detector and paired campaign
│   ├── post_shift_adaptation.py   # Phase J gradual-transition adaptation benchmark and paired campaign
│   ├── phase_k_campaign.py         # Phase K: the comparative-advantage search -- world generator, baseline grid, scoring, bootstrap, and the K0 harness control
│   ├── phase_k_diagnose.py         # the K3 root cause: per-cycle check, under-read check, and the arrival-order x strength 2x2 control
│   ├── formation_utilization.py    # the three-arm formation-vs-utilization harness: generator support, oracle admission, eight audits (Amendment 1: A8 input invariance), paired bootstrap
│   ├── store_time_observer.py   # the store-time write observer: records every admitting call, reconciles per cycle
│   ├── store_time_observer_trace.jsonl.gz # every admitting call of one control run, gzip JSONL (read with `load_trace()`)
│   ├── use_path_diagnostic.py      # the frozen use-path diagnostic (ran 2026-10-30; AUDIT REQUIRED): D0 reproduction gate, D1–D5, room-before-mechanism, generated results
│   ├── use_path_audit.py          # the three-layer reproduction audit: paired no-tiebreak/rowid-tiebreak runs, per-type table before scores
│   ├── hub_degree_probe.py        # the Layer-1 survival threshold against hub degree
│   ├── run_horizon_600.py         # the burst curriculum carried to a 600-cycle horizon
│   ├── figure_campaign.py         # the before/after figure, as dependency-free SVG
│   ├── figure_papers.py           # the manuscript figures, as dependency-free SVG; asserts every drawn value against its artifact
│   ├── lineage_audit.py           # Law II: real resolution to Generation 0
│   ├── substrate_probe.py         # live substrate cost + page accounting
│   ├── substrate_scaling_analysis.py  # latency vs cycle, from the real log
│   └── study_health.py            # standing health check  ← use this daily
│
├── build.py                     # one command: build an organism from nothing
├── GETTING-STARTED.md           # stranger-facing guide
├── LICENSE  CITATION.cff        # Apache 2.0; how to cite this work
├── requirements.txt             # core dependencies (deliberately empty)
├── requirements-ui.txt / requirements-api.txt
├── conftest.py                  # makes `pytest` work from any directory
│
├── examples/domains/            # the four reproduction worlds
├── tests/                       # 250 tests (incl. substrate equivalence, retention policy, versioning, audit-trace probe, ancestry auditor, doc-placeholder guard, readout-table drift, ranking-distribution drift, manual-table drift, formation-utilization audits, use-path diagnostic, reproduction audit)
├── papers/                      # research manuscripts
├── research-journal/            # development history + Phase G findings
├── docs/                        # architecture, design laws, failures, reports
│   ├── USER-MANUAL.md           # ← this document
│   ├── ABLATION-PREREGISTRATION.md  # predictions written before the run
│   ├── EMERGENCE-CRITERIA.md    # what counts as emergence, and what we can evidence
│   ├── FORCE-MATRIX-PREREGISTRATION.md  # Ablation Study 2: frozen M1–M9 + the launch gates
│   ├── FORCE-MATRIX-RESULTS.md   # the Tier-1 matrix results and what they can/cannot answer
│   ├── PHASE-H-PREREGISTRATION.md # frozen external-validity protocol, seeds, conditions, and decision rules
│   ├── REGIME-SHIFT-PREREGISTRATION.md # frozen Phase I generator, detector, baselines, and decision rules
│   ├── PHASE-J-ADAPTATION-PREREGISTRATION.md # frozen Phase J gradual-world schedules, metrics, and decision rules
│   ├── post_shift_adaptation_results.json # Phase J 80-world NLL, adaptation-cost, and settling results
│   ├── phase_h_results.json       # ten-seed external-validity campaign and paired difficulty trends
│   ├── regime_shift_results.json  # Phase I 80-world detection-delay campaign and control false alarms
│   ├── GATE-BOARD.md            # what is demonstrated vs assumed, and what is still open
│   ├── FACTS-SHEET.md           # facts with provenance, separated from assumptions
│   ├── ORGANICA-V2-DESIGN-NOTES.md  # planning only: what survived, what failed, what is inert
│   ├── USE-PATH-DIAGNOSTIC-PREREGISTRATION.md # the frozen diagnostic protocol: D0 gate, room, component mapping
│   ├── use_path_diagnostic_freeze.json # the protocol's SHA-256 and freeze commit
│   ├── use_path_diagnostic.json       # the diagnostic artifact
│   ├── use_path_diagnostic_structure.json # the post-hoc per-type check: identical/different × D0 pass/fail
│   ├── use_path_audit.json        # the three-layer audit artifact (runs, per-seed outcomes, scores)
│   ├── USE-PATH-AUDIT.md          # generated from that artifact: layers, per-seed tables, verdict
│   ├── candidate_membership_audit.json # the per-seed candidate membership and the first divergent cycle
│   ├── CANDIDATE-MEMBERSHIP-AUDIT.md # generated from that artifact: membership, first divergent cycle, limits
│   ├── divergence_cycle_capture.json # the candidate pool at the divergence cycle, in set and in order
│   ├── DIVERGENCE-CYCLE-CAPTURE.md # generated from that artifact: the pool, its order, and what it cannot show
│   ├── DIVERGENCE-MECHANISM-BRIEF.md # the next instrument's plan, with its hypothesis and falsification criteria pre-registered
│   ├── STORE-TIME-OBSERVER-BRIEF.md # the next instrument's plan: which write admits the extra candidate, with its result space pre-registered
│   ├── USE-PATH-DIAGNOSTIC-RESULTS.md # generated from the artifact; the D0 gate is the first section
│   ├── ablation_study.json      # the ablation results
│   ├── ablation_study_postfix.json  # ...re-run on the fixed substrate
│   ├── v1_impact.json           # V1 before vs after, incl. the RETRACTED interpretations
│   ├── verdicts.json             # the five pre-registered predictions, bucketed
│   ├── gate_validation.json     # is the gate a predictor or a definition?
│   ├── mbsd_census.json         # exact gate density across all 11 V1 conditions
│   ├── mbsd_census_postfix.json # ...and the same census on the fixed substrate
│   ├── gate_check.json          # the launch-gate re-run that closed the gates
│   ├── freq_scope_probe.json    # the scope defect, isolated
│   ├── metric_sensitivity.json  # the audit on the full 3,000-cycle matrix
│   ├── metric_sensitivity_pilot.json  # ...and on the 300-cycle pilot
│   ├── seed_noise.json          # the within-process seed floor (measured: 0)
│   ├── process_noise.json       # the process-level floor at 300 cycles
│   ├── process_noise_3000.json  # ...and at 3,000 cycles, the scale that binds
│   ├── discovery.json           # the inventory breakdown and the discovery curves
│   ├── force_matrix.json        # the Tier-1 campaign results (3,000 cycles x 6 colonies)
│   ├── force_matrix_pilot.json  # the Tier-1 pilot campaign results (300 cycles)
│   ├── WORLD-SCALE-PREREGISTRATION.md # H24: the world-complexity ladder and the burst curriculum
│   ├── scale_ladder.json         # the H24 ladder rungs and their gate/sustainment readings
│   ├── scale_ladder_scaffold.json # the 300-cycle scaffold ladder (91 baseline vs 94/93/95)
│   ├── scale_horizon_600.json    # the burst curriculum at 600 cycles (91 baseline vs 119 burst)
│   ├── scale_horizon_1200.json   # ...and at 1,200 cycles (91 baseline vs 128 burst)
│   ├── heldout_prediction.json   # the held-out prediction pilot vs Markov and decayed baselines
│   ├── ground_truth_recovery.json # structure recovery against hidden-cause pair ground truth
│   ├── hub_degree_probe.json     # survival ratio against hub degree (3 optimal, 12 collapses)
│   ├── PHASE-H-PREREGISTRATION.md   # the external-validity protocol, frozen before the run
│   ├── REGIME-SHIFT-PREREGISTRATION.md # Phase I, frozen before the run
│   ├── PHASE-J-ADAPTATION-PREREGISTRATION.md # Phase J, frozen before the run
│   ├── PHASE-K-PREREGISTRATION.md   # the comparative-advantage search: three candidate task families, frozen before any outcome
│   ├── phase_k_results.json         # the Phase K campaign result (produced by the phase)
│   ├── phase_k_results.ndjson       # the Phase K live recording: one line per completed seed, appended and flushed
│   ├── phase_k_results.md           # the Phase K write-up: results, robustness, the K3 root cause, and what it changes
│   ├── V1-SYNTHESIS.md              # the formal synthesis of V1: what was established, what was not, and the question it leaves open
│   ├── V1-FREEZE.md                # the Organica 1 freeze: what is frozen, what is not, and why it is enforced
│   ├── clone_check.json          # the last fresh-clone check, check by check
│   ├── figure_tier1_matrix.svg  # the campaign figure
│   ├── figure_discovery.svg     # the cumulative-discovery figure
│   ├── figure_p01_*.svg         # the five Paper 01 figures (displacement curve, adjacent differences, Phase K families, acquisition, capacity sweep)
│   └── figure_p02_*.svg         # the three Paper 02 figures (reconstruction arms, self-sourcing, cognition window)
├── snapshots/                   # the longitudinal data  ← the study's output
├── organica.log                 # one JSON line per cycle (appended, gitignored)
└── memory.db                    # the substrate (gitignored)
```

---

## 11. Vocabulary

Every term the project uses, what it means, and where you will meet it. Grouped by area.

### 11.1 The substrate

| Term | Definition | Where you see it |
|---|---|---|
| **Event** | A single observation: a timestamp, a source, a type, some text. The only thing the organism ever ingests. | `events` table; `event_type` is `event` (experience) or `sleep` (internal). |
| **Experience event** | An event from the outside world. These are the only source of grounding. | `event_type != 'sleep'`. **2,344 in the current study.** |
| **Sleep event** | An event the system wrote about itself. Never used to build graphs. | `event_type == 'sleep'`; `source` begins `sleep:`. |
| **Tag** | A word of ≥4 characters extracted from an event's text, minus a stopword list. The atom of the graph. | `events.tags`; ~29 distinct in the current study. |
| **Co-occurrence edge** | "These two tags appeared in the same event." | `cooccurrences` table. |
| **Temporal edge (precedes)** | "This tag was seen within the previous 3 events of that tag." The organism's first guess at causality. | `precedes` table. |
| **Working memory** | The newest **4,000** sleep events. The population the organism reasons over. | `SleepService._load_prior_candidates()`. |
| **Candidate store** | Where persisted candidates live, bounded to the newest **20,000** rows by retention. | `events` where `source LIKE 'sleep:%'`. |
| **Retention** | Periodic eviction of old candidate rows so the database cannot grow without bound. It evicts, it does not delete history of experience events. | `MemoryService.prune_sleep_candidates()`. |
| **Backfill** | One-time reconstruction of the accounting tables (`tag_counts`, `sleep_cycles`) when opening a database created before they existed. | `MemoryService._backfill_accounting()`. |
| **Batch** | Grouping many writes into one transaction. Cuts 1,023 disk syncs per cycle to 2. | `MemoryService.batch()`. |

### 11.2 The structures (one per layer)

| Term | Definition | recognized by |
|---|---|---|
| **Concept** | A cluster of tags that co-occur densely but spread widely — a hub of meaning. | `concepts`, `concept_candidate` |
| **Phrase** | Tags that cluster tightly but lead nowhere — a recurring idiom, not a concept. | `phrases`, `phrase_candidate` |
| **Loop** | A repeated temporal cycle of tags, e.g. `failure → modified → passed → failure`. | `loops`, `loop_candidate` |
| **Prediction** | A directed temporal edge strong enough to be worth expecting. | `predictions`, `prediction_candidate` |
| **Anomaly** | An observed value where something else was expected. | `anomalies`, `anomaly` |
| **Meta-concept** | A tag that anchors many other structures — a structural hub. | `meta_concept`, `anchor_tag` |
| **Process** | A 2–3 tag cycle in the temporal graph, a recurring behavior. | `processes`, `process_candidate` |
| **Workflow** | A multi-step sequence joining a process and its meta-concept anchors. | `workflow_concepts`, `workflow_concept` |
| **Hypothesis** | A falsifiable claim: "subject *A* tends to be followed by *B*", with support and contradiction counters. | `hypotheses`, `hypothesis` |
| **Theory** | Two or more hypotheses about the **same subject** with **competing expectations**, coalesced. | `theories`, `theory` |
| **Question** | The entropy of that competition, scaled by how much evidence backs it. | `questions`, `question` |
| **Dream** | A proposed counterfactual path, with near-zero confidence and zero belief authority. | `dreams`, `dream` |
| **Investigation** | A ranked proposal for where to look next, scored by EIG. | `investigations`, `investigation` |
| **Experiment** | A concrete probe derived from an investigation, scored by EIG ÷ cost. | `experiments`, `experiment` |

### 11.3 The quantities

| Term | Definition |
|---|---|
| **Support** | How many times the experience stream backed a hypothesis. |
| **Contradiction** | How many times the stream produced a *different* outcome for that subject. |
| **Confidence** | `support / (support + contradiction)` — a hypothesis's **share** of its subject's outgoing flow, not a probability of being true. |
| **Death threshold** | 0.15. Below this confidence with ≥3 observations, a hypothesis is permanently pruned. |
| **Uncertainty** | Normalized Shannon entropy of a Question's two competing expectations, scaled by evidence maturity. |
| **Novelty** | How far a dream is from established reality. 0.65 completion, 0.75 analogy, 0.85 mutation, 0.90 conditional. |
| **EIG** | Expected Information Gain — `uncertainty × (1 + novelty)` for questions, `uncertainty × novelty` for dreams. The attention currency. |
| **Priority** | `EIG / cost`. Costs: discriminating probe 1.0, dream probe 0.8, mutation/conditional probe 1.2. |
| **Clustering coefficient** | How tightly a tag's neighbours interlink, 0–1. High = phrase, low = concept. |
| **Predictive reach** | How many tags a tag leads to that its neighbours do not. High = concept. |
| **Lineage** | The chain of `parent_ids` from a candidate up to the layer below. |
| **Grounded** | A candidate whose lineage provably reaches a Generation 0 experience event. |
| **Unverifiable** | Lineage broken by eviction from the candidate store. Unprovable, but not disproven. |
| **Ungrounded** | Lineage resolves, but its Layer 1 anchor appears in no experience event. A genuine violation. |
| **Duty cycle** | The fraction of a rolling window of cycles in which a generation is present. The correct way to report intermittent emergence. |
| **Cognitive revolution** | A shift in which structure dominates the population. Logged as an event-journal entry. |

### 11.4 The process

| Term | Definition |
|---|---|
| **Sleep** | One consolidation cycle. Reads the graph, proposes structures, tests them against evidence, lets the failures decay and die. Not a summariser, not a prompt. |
| **Sleep cycle / `sleep_cycle`** | The global, restart-surviving counter of sleep cycles. The x-axis of every time series. |
| **Run / process cycle** | The `cycle` field — resets to 0 on every daemon start. Not a time axis. |
| **Consolidation** | The part of a sleep cycle that merges the graph into higher-order candidates. |
| **Natural selection** | Law VI: candidates that are not reinforced decay by ×0.80 per cycle; below 0.15 they are pruned. |
| **Reinforcement** | A candidate reappearing in the current population; its confidence is boosted by +0.05. |
| **Decay** | A prior candidate absent from the current population, kept alive but weakened. |
| **Pruning** | A prior candidate whose confidence fell below threshold. Counted, and excluded from the next cycle's population. |
| **Ground truth** | Generation 0 experience events. The only thing that can confirm a belief. |

### 11.5 The experiment vocabulary

Terms from the cold-start and ablation studies.

| Term | Definition |
|---|---|
| **Cold start** | Running the organism with no pre-seeding, so the world arrives one observation at a time. Tests what bootstraps unaided. |
| **Ablation** | Removing or replacing one mechanism and measuring what changes. All ablations here are applied **in-process**, so the engine source is never edited. |
| **O_FULL** | The full-system reference condition. Every ablation is compared against it. |
| **Forward-looking scoring** | Snapshotting the organism's graph and predictions *before* a cycle's events arrive, then scoring them against what happened. The organism is always predicting unseen events. |
| **PA** | Predictive accuracy — the F1 of the organism's own Layer-1 predictions against what actually happened. |
| **PA_substrate** | The same F1 computed on the substrate's temporal graph. Separates "the substrate learned it" from "the organism represents it". |
| **IP** | Information Preservation — how much predictive power survives when the raw event stream is replaced by the organism's own abstractions. |
| **SCR** | Structural Compression Ratio — experience events represented per surviving structure. Undefined when nothing survived. |
| **SS** | Survival Selectivity — the fraction of created candidates that died. `CSR = 1 − SS`. |
| **LC** | Lineage Completeness — the fraction of structures whose ancestry resolves to a Generation 0 event. Target 1.0. |
| **CD** | Contradiction Density — unresolved contradictions per 1000 active nodes. Undefined when there are no nodes. |
| **CDT** | Cross-Domain Transfer — accuracy with transfer minus accuracy without. Negative means the donor domain hurt. |
| **NSR** | Novel Structure Rate — the fraction of new nodes whose exact topology never existed before. |
| **ES** | Emergence Score — a weighted convenience index over the computable metrics. **A summary, not a measurement**; the per-metric deltas are the result. |
| **Impact(S)** | `ES_full − ES_without_S`. Bands: cosmetic / supportive / important / foundational / existential. |
| **Not measurable** | A metric that is structurally impossible to compute here (e.g. experiment information gain, with no experiment executor). Excluded from the aggregate rather than zeroed. |
| **Emergence level** | The seven-step ladder in `docs/EMERGENCE-CRITERIA.md`, from compression emergence to ontological emergence. |

### 11.6 The three version namespaces

This project uses "v1" and "v2" in three different senses. They are
deliberately distinct, and mixing them up is a documentation bug, not a
matter of taste.

| Namespace | Form | What it means | Where it lives |
|---|---|---|---|
| **Package version** | `0.x.y` | the released, installable, citable artifact. **Semantic Versioning 2.0.0.** The project is **pre-1.0**, so the public API is *not* declared stable and the MINOR/PATCH numbers carry the meaning instead. | `organica.__version__` (the single source of truth), `pyproject.toml`, `CITATION.cff` |
| **Architecture generation** | *Organica 1*, *Organica 2* | a generation of the eight-layer engine. **Organica 1** is the frozen engine that runs today. **Organica 2** is the planned successor — planning only, in [`docs/ORGANICA-V2-DESIGN-NOTES.md`](docs/ORGANICA-V2-DESIGN-NOTES.md). | `docs/ORGANICA-V2-DESIGN-NOTES.md` |
| **Research campaign** | *Ablation Study 1*, *Ablation Study 2* | the experimental series. **Ablation Study 1** is the eleven-condition ablation study (`docs/ablation_study.json`). **Ablation Study 2** is the six-colony Tier-1 matrix (`docs/FORCE-MATRIX-PREREGISTRATION.md`). | `docs/FORCE-MATRIX-PREREGISTRATION.md` |

**So: no, the project is not at "v1" or "v2" as a release.** It is
**0.9.0**, pre-1.0, with the architecture at *Organica 1* and the second
research campaign in flight.

`tests/test_versioning.py` asserts that the three version declarations
never drift apart, that the version is valid SemVer 2, that it is
pre-1.0, that it has a changelog entry, and that **the version describes
this commit**. The three declarations disagreed once already —
`pyproject.toml` said 0.1.0 while `CITATION.cff` said 0.5.0 — and a
reader who cited one and installed the other had no way to tell.

Releases are tagged `v<version>` and recorded in [`CHANGELOG.md`](../CHANGELOG.md).

**Bumping the version is not optional after a release.** Master drifted
past the `v0.7.0` tag while still declaring `0.7.0`, so the version named
a release that master was not, and anyone installing from master got a
different artifact under the same number. The rule is now enforced: *if
a tag `v<version>` exists, it must point at the current commit*. A
version whose changelog heading is marked **`(unreleased)`** is allowed to
have no tag yet, because there is nothing to check out yet — that is the
normal state of `master` between releases. See AGENTS.md rule 10.

---

## 12. Abbreviations and acronyms

| Short | Full | Meaning |
|---|---|---|
| **EIG** | Expected Information Gain | The attention currency of Law V. |
| **G0–G9** | Generation 0 – Generation 9 | The developmental ladder, bottom to top. |
| **BM1–BM5** | Benchmark 1 – 5 | The growth-benchmark suite in `benchmarks/benchmark_suite.py`. |
| **CFA** | Cross-Domain Validation | Phase F. The four reproduction domains. |
| **Phase G** | Endurance / External Soak | The current phase. 24h / 7d / 30d endurance. |
| **Law I–VI** | Design Laws I–VI | The architectural constitution, `docs/DESIGN_LAWS.md`. |
| **LLM** | Large Language Model | Not used by the core — the whole point is to avoid one. |
| **G5 duty cycle** | — | Fraction of recent cycles carrying ≥1 Theory. |
| **ETL** | Extract-Transform-Load | Not used; the observer is a direct log reader. |

---

## 13. Data dictionary

### 13.1 The log line (`organica.log`)

One JSON object per cycle, appended. Fields:

| Field | Type | Meaning | Typical healthy value |
|---|---|---|---|
| `cycle` | int | Cycles since the last daemon start | 0, 1, 2, … (resets on restart) |
| `sleep_cycle` | int | **Global** sleep-cycle counter | increases by exactly 1 per line |
| `timestamp` | string | UTC ISO-8601 | `2026-10-21T18:41:17Z` |
| `status` | string | `success` or `failed` | `success` |
| `duration_ms` | int | Wall time of the sleep cycle | 150–300 ms |
| `consecutive_errors` | int | Error streak | 0 |
| `concepts` `predictions` `loops` | int | Gen 1 populations | 2 / 20 / 15 |
| `hypotheses` | int | Gen 4 population | 13–15 |
| `hypothesis_snapshot` | array | Per-hypothesis detail | see below |
| `theories` `questions` | int | Gen 5 populations | 1 / 1 |
| `dreams` | int | Gen 6 population | 8 |
| `dream_categories` | object | Dreams by category | `{"conditional": 6, "mutation": 2}` |
| `investigations` `experiments` | int | Gen 7 / Gen 8 | 5 / 5 |
| `composites_created` | int | New structures this cycle | 60–70 |
| `total_composites` | int | Cumulative | grows monotonically |
| `candidates_strengthened` | int | Law VI reinforcement count | 30–90 |
| `candidates_pruned` | int | Law VI pruning count | 0–3000 |
| `substrate_rows_pruned` | int | Rows evicted by retention | ~109, steady |

Each `hypothesis_snapshot` entry:

```json
{"id": "hyp_e7423150", "subject": "developer", "confidence": 0.19,
 "support_count": 61, "contradiction_count": 260, "generation": 3}
```

> **Reading it:** `subject` is the tag the claim is about. `confidence` is its *share* of that subject's outgoing flow. A subject appearing **twice** in the snapshot is the organism holding two competing beliefs about it — that is exactly what G5 needs. `support_count` and `contradiction_count` are the raw evidence.

### 13.2 The database (`memory.db`)

| Table | Contents |
|---|---|
| `events` | Every experience event and every persisted candidate. `event_type` separates them. |
| `cooccurrences` | `(tag_a, tag_b, count)` — which tags appear together. |
| `precedes` | `(tag_from, tag_to, count)` — which tags follow which. |
| `tag_counts` | `(tag, count)` — incremental tag frequencies. Replaces a full-table scan. |
| `sleep_cycles` | `(cycle, ran_at)` — the authoritative monotonic counter. |

### 13.3 The snapshot artifacts (`snapshots/`)

| File | Key fields |
|---|---|
| `daily/daily_YYYYMMDD.json` | `active_*` populations, `births_today`, `deaths_today`, `window_hours`, `cycles_in_window` |
| `weekly/weekly_YYYYMMDD.json` | `window_cycles`, `aggregated`, `largest_births`, `largest_deaths` |
| `monthly/monthly_YYYYMMDD.json` | `belief_population`, `hypothesis_lifecycle`, `dream_distribution` |
| `velocity/velocity_YYYYMMDD.json` | `new_theories_per_day`, `new_questions_per_day`, `new_dreams_per_day`, `new_experiments_per_day` |
| `event_journal.log` | Append-only structural events |

---

## 14. The eight layers, in detail

| Layer | Produces | recognized by | Typical value |
|---|---|---|---|
| **G1** | Concepts, phrases, loops, predictions, anomalies | graph topology separates signal from noise | 2 concepts, 20 predictions, 15 loops |
| **G2** | Meta-concepts, processes | high-degree anchors; 2–3 tag cycles | ~5–8 processes |
| **G3** | Workflows | process + matching meta-concept anchors | ~4–8 workflows |
| **G4** | Hypotheses | workflow component pairs and process cycles, each with evidence | 13–15 |
| **G5** | Theories, Questions | ≥2 hypotheses sharing a subject with competing expectations | 1–3 |
| **G6** | Dreams | four categories, confidence 0.04–0.08, no belief authority | up to 8 |
| **G7** | Investigations | ranked by EIG | up to 5 |
| **G8** | Experiments | ranked by EIG ÷ cost | up to 5 |

### 14.1 The four dream categories

| Category | What it proposes | Confidence | Novelty |
|---|---|---|---|
| **Completion** | A transitive shortcut: if A→B and B→C, dream A→C. | 0.08 | 0.65 |
| **Analogy** | A transfer through a co-occurrence neighbour: if A~B and A→C, dream B→C. | 0.05 | 0.75 |
| **Mutation** | A structural path extension. | 0.04 | 0.85 |
| **Conditional** | The hidden context tag that might separate a Question's two outcomes. | 0.06 | 0.90 |

> **Conditional dreams only exist when there are uncertain Questions.** If you see `conditional` in `dream_categories`, G5 is live. If you only ever see `analogy`, the stream has no competing expectations and the study is invalid.

---

## 15. The formulas, with worked examples

**Confidence** — a hypothesis's share of its subject's outgoing flow:

```
confidence = support / (support + contradiction)
```

*Example:* `developer → failures` has support 61, contradiction 260.
`61 / 321 = 0.19`. That is above the 0.15 death threshold, so it survives — barely. A sibling hypothesis `developer → passed` with support 37 and contradiction 0 gets `37/37 = 1.00`, so `developer` holds one certainty and one doubt. That pair is what Layer 5 needs.

**Question uncertainty** — Shannon entropy of the two competing expectations, scaled by evidence:

```
p1 = s1 / (s1 + s2)         p2 = 1 - p1
entropy     = -(p1·log2(p1) + p2·log2(p2))
maturity    = min(1.0, (s1 + s2) / 10)
uncertainty = entropy × maturity
```

*Example:* supports 12 and 8 → p1 = 0.6, p2 = 0.4.
`entropy = 0.6·0.737 + 0.4·1.322 = 0.971`. `maturity = min(1, 20/10) = 1.0`.
`uncertainty = 0.971`. Evenly split expectations give near-maximum uncertainty — exactly the state Law V wants the organism to investigate.

**EIG** — the attention currency:

```
question target:  EIG = uncertainty × (1.0 + novelty),   novelty = 0.50
dream target:     EIG = uncertainty × novelty,             uncertainty = 1 - dream confidence
```

*Example:* a Question with uncertainty 0.97 → `EIG = 0.97 × 1.5 = 1.46`.

**Experiment priority** — value per unit cost:

```
priority = EIG / cost
cost: discriminating probe 1.0 | dream probe 0.8 | mutation/conditional probe 1.2
```

*Example:* `1.46 / 1.0 = 1.46`, which matches the ~1.49 peaks seen in the study.

**Concept vs phrase** — the two classification rules, which pull in opposite directions:

```
clustering = (edges among neighbours) / (possible edges)     high = phrase
reach      = targets the tag leads to that its neighbours do not   high = concept
```

A tag with degree ≥ 4, clustering ≤ 0.4 and reach ≥ 4 is a **concept**. A tag with clustering ≥ 0.7 and reach ≤ 2 is a **phrase**.

---

## 16. Metric cheat sheet

What a healthy run looks like, and when to worry.

| Metric | Healthy | Investigate if |
|---|---|---|
| `sleep_cycle` | +1 every line | it ever goes backwards |
| `status` | always `success` | any `failed` |
| `duration_ms` | 150–300 ms | median drifts above ~1,000 ms |
| `theories` (windowed) | 1–3, duty cycle 90–100% | duty cycle 0% over 200 cycles |
| `questions` | 1–3 | 0 across a window |
| `hypotheses` | 13–15 | drops below ~8 |
| `dreams` | 6–8 | 0 |
| `dream_categories` | contains `conditional` | only `analogy` → stream is inert |
| `contradiction_total` | 1,000–30,000 | exactly 0 → no competing expectations |
| `candidates_strengthened` | 30–90 | 0 |
| `substrate_rows_pruned` | ~109, steady | 0 → retention not running |
| `candidates_pruned` | 0–3,000 | 0 → selection pressure gone |
| DB size | ~15 MB, flat | growing without bound |
| Law II (lineage audit) | 100% grounded | any `ungrounded` |

**The two most important sanity checks:**

1. **`theories` > 0 over a window.** If this reads 0 across 200 cycles, the study is invalid regardless of how healthy everything else looks.
2. **Contradictions > 0.** Zero contradictions means zero entropy means zero EIG — a run can look perfectly healthy and be epistemantically inert.

---

## 17. Common misreadings

Things that look like findings but are not, and things that look fine but are not.

| Misreading | The truth |
|---|---|
| "The health report said 670 cycles." | That was a count of **log lines** across 4 process restarts, not cycles. The database's own count was 504, and the `sleep_cycle` counter was itself resetting mid-run. |
| "`theories` is 0, so Generation 5 failed." | Check the **window**. G5 oscillates; a single cycle reading 0 is normal. Read the duty cycle over 200 cycles. |
| "The report says `lineage_integrity_pct: 100.0`." | That check verified parent ids were present among *other candidates in a 4,000-event window*. It never reached Generation 0. The real audit (`benchmarks/lineage_audit.py`) also reports 100% — but that one actually resolves to experience events. |
| "Contradiction count is 0, so the organism is stable." | Zero contradictions means no competing expectations, so no entropy, so no EIG. That is a dead study, not a stable one. |
| "The run is dead because the daemon crashed." | It was terminated by a person (`Stop-Process` in the shell history). 504 cycles, **zero** errors. |
| "The database is 942 MB, so memory is unbounded." | That was the *unbounded* store. The current build retains a bounded window and sits flat at ~15 MB. The 942 MB file is archived run-1 evidence. |
| "Adding more domains makes the organism smarter." | Measured: adding the ecology and robot domains **reduced** G5 sustainment from 0.70 to 0.57, because more workflow structures crowd the 15-slot hypothesis budget. |
| "The organism actively experiments." | It *generates* experiment candidates. Nothing executes a probe or measures a belief delta. The study measures epistemic **tension**, not **resolution**. |
| "`sleep_cycle` and `cycle` are the same thing." | `cycle` resets per process; `sleep_cycle` is global. Only `sleep_cycle` is a time axis. |
| "The dashboard shows the same numbers as the study." | `dashboard.py` is the older CLI tool. `study_health.py` is current and is what the manual quotes. |
| "The organism will eventually work out the higher generations on its own." | Measured, and no: G1, G4 and G6–G8 bootstrap unassisted, but **G5 never appears from any unengineered stream** — and it will not appear later either, because the confidence formula destroys a minority belief as the subject accumulates successors. [§8.1](#81-the-cold-start-study) |
| "The ablation study showed the architecture works." | It did not. It showed *which parts* matter, and the answer is uncomfortable: sleep and the graph are foundational, and lineage is pure governance with **zero** behavioral effect. |
| "Lineage is one of the six design laws, so it must be doing something." | It is load-bearing for **auditability** — removing it drops Lineage Completeness from 1.0 to 0.0 — while changing no other measured behavior. Governance, not cognition. |
| "Random curiosity performed the same, so curiosity is fake." | Not yet proven. Random and EIG curiosity score the same on the metrics that count *populations*, but the metrics that would separate them (experiment value, experiment information gain) are exactly the ones that cannot be computed without an experiment executor. |
| "The 90-day run proves the organism is emergent." | It proves the organism runs, is reproducible, and maintains lineage. Emergence is a separate claim with its own instruments: the ablation study and the designer-surprise protocol. |
| "The study measured 1,665 cycles, so the data is richer than 60 cycles." | More cycles is more of the same world. The study stream is a 48-event rotation; the cross-world measurement is CDT, and it is negative. |
| "The 3,725-cycle run is rich longitudinal data." | It is 3,725 cycles of the *same* number. Every population series has **stdev 0.000000** over the last 931 cycles. The organism converged at cycle 261 and did not move again. More cycles is not more data when the line is flat. [§8.3](#83-the-instrumentation-audit-where-the-pressure-really-is) |
| "The hypothesis cap decides which beliefs survive, so it must matter." | It **does not bind**. The belief pool maxes at 8 against a cap of 15, in 0 of 600 cold cycles; raising it to 60 changes nothing. `MAX_HYPOTHESES` is INERT. |
| "The retention rule sorts by name, so it must be distorting the results." | It is a real defect and currently **inert** — nothing is truncated, so alphabetical and salience choose the same beliefs. It also was **not** the cause of the No-Falsification collapse; that had zero processes *and* zero workflows. [§8.3](#83-the-instrumentation-audit-where-the-pressure-really-is) |
| "The organism is complexity-limited by its environment — give it a richer world." | **Measured false.** Going from 42 to 97 world tags *lowered* the belief pool from 5.47 to 1.41 and took theories to **zero**. A richer world makes it worse. What it needs is more *branch structure*, not more words. |
| "Raising the budget will give the organism room to develop." | Raising `MAX_HYPOTHESES` changes nothing at all. Raising `MAX_PREDICTIONS` widens the belief pool to 7.71 at best, and **destroys** the organism past 160 (theories to zero). The budget is not the constraint. |
| "The branch stimulus worked at r=4 and collapsed at r=6, so r=4 is the right setting." | **There was no boundary.** The apparent phase transition was the tag-frequency counter measuring a different population from the graph it normalises. With the counter corrected, r=4, r=6 and r=10 all give the *same* result: 18 beliefs, 7 competing subjects, 100% of tail cycles passing every gate. [§8.4](#84-the-counter-that-was-measuring-the-wrong-population) |
| "The organism's own output doesn't reach the cognition layers, so its schema tags are harmless." | The *graph* was world-only, but the *frequency counter* was not — and that counter is the denominator of the Layer-1 survival filter. The effect was to discard the world's own edges. [§8.4](#84-the-counter-that-was-measuring-the-wrong-population) |
| "If an ablation changed no metric, it did nothing." | Use the G1-G4 ladder. **No Lineage** passes G1 and G2 and fails G3: the populations are identical and only the lineage metric moved. That is what "governance, not cognition" looks like. |
| "The seed-noise floor is 0, so every delta is a finding." | The **within-process** seed floor is 0.00, but that is not the floor that binds: the campaign runs each colony in its own process, and CPython randomises string hashing per process. The **process-level** floor moves exactly one field — M5, by 0.333 new-per-100-cycles (1.34%). The campaign pins `PYTHONHASHSEED=0` in all six colony processes so the hash order is common-mode and cannot contaminate the between-colony comparison. |
| "M1, M6 and M8 did not move, so the interventions did nothing." | Those three are **saturated**: a theory is present in 299 of 300 cycles in every arm, the lineage reaches generation 7 in every arm, and the belief population is equally stable in every arm. Insensitivity there is itself a result — the interventions do not destabilise the organism. The signal that *did* move is in the **population means** (`theories_mean` 5.10 → 4.91), which are reported alongside the duty cycles. |
| "M9 is 0, so the metric failed." | M9 is **structurally zero** at 300 cycles: a cognitive revolution needs a dominant theory demoted by more than 50% and replaced within 50 cycles, and no arm demotes a dominant theory. Zero across all arms is a finding in its own right, and the pre-registration says so. |
| "The plateau proves the architecture can't develop." | Tier-1 shows exhaustion of a repeating 9-event stimulus, not an architectural ceiling. Later curricula moved inventory from 74 to 91, 113, 119 and 128. The 1,200-cycle extension ended below the preregistered 140+ expansion band, with 2 discoveries in its final 100 cycles. This supports curriculum dependence, while the long-run ceiling remains unresolved. [World-scale record §11](WORLD-SCALE-PREREGISTRATION.md) |
| "Development velocity is 2.467, so development is slow." | M5 is `new items ÷ run length`, not a velocity. The reference arm found **74** items over 300 cycles and **74** over 3,000; the rate fell from 24.667 to 2.467 because the numerator stopped growing. The rate divides a finite inventory by the run length, so it falls with the run even when nothing changes. The inventory is the number. |
| "Retention matters because M7 is 212 against 2,990." | Directionally yes, but the reference arm's 212-cycle mean is the mean of **exactly one** observed belief death (15 of 16 censored). The robust finding underneath is that 15–16 of the beliefs **never die** in any arm. Reported with the sample size attached, because a mean over one observation is not a mean. |
| "Phase L proved that Organica revises its beliefs." | Phase L measured **structural displacement** — later *structure* displacing earlier *structure*. It says nothing about correcting a belief against ground truth. On the belief-revision task (Phase K), Organica scored **0.4111** against the best simple baseline's **0.9846** — a clean loss. [§8.18](#818-the-five-claims-narrowed-2026-10-26) |
| "The 3:1 crossing is a threshold for Organica." | It is a threshold **within this engine, world family and support-ratio axis**. The eight alternative bootstrap seeds re-draw from the same measured seeds, so they test **resampling stability, not new worlds**. [§8.18](#818-the-five-claims-narrowed-2026-10-26) |
| "Path dependence proves the order of events matters." | The curriculum and history results change the schedule's **multiset and order together**, so they establish schedule dependence. **Strict order dependence** needs the multiset held fixed with only the order changed — that comparison has not been run. [§8.18](#818-the-five-claims-narrowed-2026-10-26) |
| "Transfer is still completely open." | It is not fully open and not positive: the one measured axis, cross-domain transfer, is **negative** (**−0.486** across 12 domain pairs, mean shared vocabulary **0.17 tags**). **No positive transfer has been demonstrated**; other forms remain untested. [§8.2](#82-the-ablation-study-which-mechanisms-are-actually-doing-the-work) |
| "An independently auditable record means another lab has replicated this." | It means the developmental decision can be **independently reconstructed from the engine's state**. No second laboratory has reproduced the work, and the trace covers the organism's **surviving, current** structures rather than their full past. |

---

## 18. Keeping this manual current

**This manual is a living document. It must be updated in the same turn as any change it describes.** Concretely:

**Update this file when any of these change:**

- The daemon's running state, cycle counts, or any metric in [§2](#2-where-things-stand-right-now)
- A command, launcher, or path in [§4](#4-running-everything)
- A log field's meaning in [§5](#5-reading-the-output)
- The study protocol or the nine targets in [§6](#6-what-the-study-is-measuring)
- **Your** action list in [§7](#7-what-you-need-to-do) — completed, deferred, or newly identified
- A finding in [§8](#8-the-findings-and-what-each-means-for-you)
- A symptom or fix in [§9](#9-troubleshooting)
- A file's role in [§10](#10-file-map)

**The rules:**

1. **Same turn, not deferred.** If you changed the code, the manual is updated before the turn ends.
2. **No stale numbers.** A status block with old numbers is worse than no status block.
3. **Decisions get recorded, not just made.** When you decide something in [§7](#7-what-you-need-to-do), move it with a date and a one-line rationale — that trail is part of the project's contribution.
4. **Findings link to evidence.** Every claim in [§8](#8-the-findings-and-what-each-means-for-you) points at a section of `research-journal/phase_g_findings_20261021.md` or a JSON report in `docs/`.
5. **The manual is for you, the journal is for the field.** The manual explains *what to do*; the journal is the scientific record. Write for the former in plain language; keep the latter rigorous.
6. **This rule is also recorded in `AGENTS.md`** at the repository root, so any agent working on this project picks it up automatically.

**Revision log:**

| Date | Change |
|---|---|
| 2026-10-21 | Created. Documented the Phase G audit, the corrected study daemon, the nine findings, the action list, and the scheduled-task recipe. |
| 2026-10-21 | Added the reference block: full vocabulary (§11), abbreviations (§12), data dictionary (§13), layer-by-layer reference (§14), formulas with worked examples (§15), metric cheat sheet with alert thresholds (§16), and common misreadings (§17). |
| 2026-10-22 | Added the cold-start study (§8.1): eight assistance levels, what bootstraps unaided, and the proof that share-based confidence is what blocks G5. Added finding 10. Added §4.7 (build an organism from nothing), the new file map entries, §11.5 (experiment vocabulary), and the new files to §4.5. |
| 2026-10-22 | Added §8.2: the ablation study — ten ablations, the metric suite, the two structurally unmeasurable metrics, and the pending designer-surprise protocol. Recorded `docs/ABLATION-PREREGISTRATION.md` (predictions written before the run) and `docs/EMERGENCE-CRITERIA.md` (the measurable emergence ladder). |
| 2026-10-22 | Added the mechanism-verification stage (`benchmarks/ablation_verify.py`): perturbation census, Random-Curiosity overlap and score distribution, contradiction provenance. Recorded findings #10 (the alphabetical truncation decides which beliefs survive) and #5's corrected mechanism. Added `benchmarks/clone_check.py` and its 8/8 fresh-clone result. Added §7.2 decision #10, the valuation-layer proposal, and journal §18. |
| 2026-10-23 | **Phase V1.5 — the instrumentation audit.** Stopped the daemon at 3,725 sleep cycles and archived the run (`logs/organica_prefix_20261022.log` + `docs/prefix_run_series.json`). Added `benchmarks/development_probe.py`, `benchmarks/instrumentation_audit.py` and `benchmarks/archive_run.py`; added `docs/FACTS-SHEET.md` and `docs/GATE-BOARD.md`; added `tests/test_retention_policy.py` (18 tests). Added **§8.3**. Added §7.2 decisions #11 and #12. **Corrected finding #10** and superseded decision #6: the hypothesis cap does not bind, `MAX_HYPOTHESES` is INERT, and the alphabetical rule was not the cause of the No-Falsification collapse. Refreshed §2. Journal §19 added. |
| 2026-10-23 | **Engine change (owner-authorised, 2026-10-22).** The hypothesis retention rule changed from an inline alphabetical sort to a named, unit-free **salience** policy with a separate allowance for inert structural markers, plus a `CONTRADICTION_SCALE` hook. Also extracted six hard-coded layer caps to named constants. Verified behavior-preserving: 35/35 tests pass and the cap census is unchanged (pool max 8, mean 5.31, cap binds 0/600). **Measured effect on behavior today: none** — the cap does not bind, so this is a correctness fix, not a behavioral one. |
| 2026-10-23 | **Daemon relaunched** on the new build (PID 32328, 06:28 MDT) and `run_continuous.py` now writes a **build marker** at every startup, so an append-only log spanning several builds says which configuration produced which cycles. Counter continued 3,725 → 3,730 with 0 non-monotonic steps and 0 failures across the restart. |
| 2026-10-23 | **Milestone M0.5 — mechanism closure, and a substrate correction.** The proposed gate was **validated** against the 11 V1 conditions and came back *structural*, not predictive: `theories == min(competing_subjects, MAX_THEORIES)` holds in 100% of cycles in 9 of 11 conditions, so the gate is restated as a count and a fifth gate (**G-SUS**, sustained rather than peaked) was added. The exact density census over all 11 conditions is in `docs/mbsd_census.json` — **no existing condition sustains more than 1.95 competing subjects on average, and only 4 of 9 ever reach 3.** The branch stimulus then cleared every gate *on peaks only*, and a repeat-count boundary appeared (4 worked, 6 and 10 collapsed). **The boundary was an artifact**: `tag_counts` was maintained over *all* events while the graphs it normalises are world-only, so the Layer-1 survival filter compared a world edge count against a polluted denominator. Fixed in `organica/memory.py` (counter now world-scoped, with a `meta` scope marker so an old database rebuilds exactly once). After the fix the branch stimulus holds **18 beliefs and 7 competing subjects with 100% of tail cycles passing every gate**, and the apparent phase transition disappears — r=4, 6 and 10 now behave identically. Added `benchmarks/gate_check.py`, `benchmarks/freq_scope_probe.py`, `benchmarks/branch_sweep2.py`, `benchmarks/branch_diag2.py`, `benchmarks/mbsd_census.py`, `benchmarks/gate_validation.py`, `organica/branch_streams.py`; added `tests/test_substrate_equivalence.py` scope-consistency regression test (36/36 tests pass). **Added §8.4.** **Corrected facts sheet D8b in place** — the claim that the pollution was "not the cause of anything" was wrong. Gate definitions frozen in `docs/FORCE-MATRIX-PREREGISTRATION.md` §1 (measured on the pre-retention pool, so they do not depend on the arm under test). Journal §21. |
| 2026-10-23 | **Versioning, and the campaign tooling.** The package version is now **0.6.0** under **Semantic Versioning 2.0.0**, declared once in `organica/__init__.py` and asserted against `pyproject.toml` and `CITATION.cff` by the new `tests/test_versioning.py` (the three previously disagreed: 0.1.0 vs 0.5.0). The project is **not** at "v1" or "v2" as a release — it is pre-1.0, with the **architecture generation** at *Organica 1* and the **research campaign** at *Ablation Study 2*. Added **§11.6** (the three version namespaces) and `CHANGELOG.md`; 0.6.0 is the first release to carry a git tag. Added `benchmarks/force_matrix.py` (six-colony campaign runner with G1 code-path verification and per-colony parallelism), `benchmarks/metric_sensitivity.py` (which of M1–M9 can actually move), `benchmarks/seed_noise.py` and `benchmarks/process_noise.py` (the two noise floors), `benchmarks/v1_impact.py` (V1 before/after, with a RETRACTED category for interpretations), and `benchmarks/figure_campaign.py` (dependency-free SVG). The six-colony **pilot** ran at 300 cycles: 6/6 colonies, G1 verified distinct, and the **sensitivity audit** reports **5 of 9 metrics able to move** (M1, M6, M8 insensitive; M9 structurally zero). `benchmarks/seed_noise.py` measured the **within-process** seed floor as exactly **0.00**; because the campaign runs each colony in its own process, the binding floor is the **process-level** one, measured by `benchmarks/process_noise.py --sweep`. **42/42 tests pass.** |
| 2026-10-23 | **Ablation Study 2 — the Tier-1 matrix ran, and it changed the plan again.** Six colonies × 3,000 cycles = **18,000 colony-cycles** (`docs/force_matrix.json`), launched by the new `benchmarks/run_matrix.py`, which runs the G1 verification once and pins **`PYTHONHASHSEED=0` in all six colony processes** so the hash order is common-mode across arms. **The structure is decided on cycle 1**: every arm reaches 18 pre-retention beliefs, 7 competing subjects and 15 retained beliefs and holds them for 2,999 cycles while mean support grows **+10,776%**. **M5 was not a velocity** — it is a finite inventory ÷ run length (74 items over both 300 and 3,000 cycles; the rate fell 24.667 → 2.467 because the numerator stopped growing), and every arm discovered **zero** new items in its final 100 cycles. **The confound: the stimulus repeats every 9 cycles** (9 distinct events, 7 words, 333 repetitions), so the plateau is consistent with *the organism exhausted the environment*, not with an inability to develop. **The five pre-registered predictions: 2 SUPPORTED, 3 REVERSED, 0 UNSUPPORTED, 0 NOT INTERPRETABLE** — the verdicts are direction-aware, so removing contradiction or questions reads as REVERSED rather than as a confirmation. The **noise floor is one new item**, measured at the 3,000-cycle scale (`docs/process_noise_3000.json`). Two colony names are corrected in place: `NO_CONTRADICTIONS` removes contradiction's *weight in confidence*, not contradictions. Added `benchmarks/verdicts.py`, `benchmarks/discovery_report.py`, `benchmarks/run_matrix.py`; added **`docs/FORCE-MATRIX-RESULTS.md`**, `docs/discovery.json`, `docs/figure_discovery.svg`, `docs/figure_tier1_matrix.svg`, `docs/verdicts.json`; added facts sheet §I (matrix results) and **§J (H24)**; updated `docs/ORGANICA-V2-DESIGN-NOTES.md` §7–§10 with the matrix's answers and the new stimulus requirement. Journal §23. |
| 2026-10-23 | **Release 0.7.0 — the Tier-1 matrix, and H24.** Six colonies × 3,000 cycles = **18,000 colony-cycles**. **The structure is decided on cycle 1**: every arm reaches 18 pre-retention beliefs, 7 competing subjects and 15 retained beliefs and holds them for 2,999 cycles while mean support grows **+10,776%**. **M5 was not a velocity** — it is a finite inventory ÷ run length (74 items over both 300 and 3,000 cycles; the rate fell 24.667 → 2.467 because the numerator stopped growing), and every arm discovered **zero** new items in its final 100 cycles. **The confound: the stimulus repeats every 9 cycles** (9 distinct events, 7 words, 333 repetitions), so the plateau is consistent with *the organism exhausted the environment*, not with an inability to develop. **The five pre-registered predictions: 2 SUPPORTED, 3 REVERSED, 0 UNSUPPORTED, 0 NOT INTERPRETABLE** — the verdicts are direction-aware, so removing contradiction or questions reads as REVERSED rather than as a confirmation. The **noise floor is one new item**, measured at the 3,000-cycle scale (`docs/process_noise_3000.json`). Two colony names are corrected in place: `NO_CONTRADICTIONS` removes contradiction's *weight in confidence*, not contradictions. Added `benchmarks/verdicts.py`, `benchmarks/discovery_report.py`, `benchmarks/run_matrix.py`, `benchmarks/scale_ladder.py`, `benchmarks/hub_degree_probe.py`, `organica/scale_streams.py`; added **`docs/FORCE-MATRIX-RESULTS.md`**, `docs/discovery.json`, `docs/figure_discovery.svg`, `docs/figure_tier1_matrix.svg`, `docs/verdicts.json`; added facts sheet §I (matrix results) and **§J (H24)**; updated `docs/ORGANICA-V2-DESIGN-NOTES.md` §7–§10 with the matrix's answers and the new stimulus requirement; **rewrote the README** to carry the findings, the verdicts and H24. Journal §23. |
| 2026-10-23 | Recorded the exploratory 1,200-cycle horizon (91 baseline, 128 burst, 2 new in the final 100), corrected novelty metadata (39/19 actual bursts at 1,200/600 cycles), and documented the held-out pilot (Markov F1 0.504 vs Organica 0.413 on known tags). Added its run command, file-map entry, and review action. Journal §24; world-scale record §11. |
| 2026-10-23 | Added the known-cause generator and structural-recovery pilot. The one-seed result: Organica F1 0.706, same-event co-occurrence 0.800, temporal graph 0.148. Added hidden-cause results and limits to the fact sheet and journal §25, and recorded seed/noise/overlap follow-up in the action list. |
| 2026-10-23 | Preregistered Phase H before its multi-seed run: ten seeds, fixed hash seed, prediction and structure-recovery leagues, and three controlled noise/overlap/decoy levels. Added `benchmarks/phase_h_campaign.py`; the campaign leaves the cognitive engine unchanged. Journal §26. |
| 2026-10-23 | **Paused live study collection at owner direction** after continuous-run cycle 1032 (global cycle 5396), preserving the database and log until a stable V1.0.0 is ready and reviewed. Updated the status dashboard, restart guidance, and deferred study actions. Journal §27. |
| 2026-10-23 | **Completed Phase H external-validity campaign** across ten seeds. Recorded fixed-stream prediction scores, recovery intervals, and paired difficulty trends; clarified that H1 seeds did not resample the input stream. Updated next actions toward seed-varied prediction and regime-shift evaluation. Journal §28. |
| 2026-10-23 | **Preregistered Phase I regime-shift detection** before implementation or outcome generation: two synthetic generator families, one Markov and one decayed-association baseline, per-world surprise thresholds, shifted/control seed pairs, and a paired restricted-delay success rule. The live study remains paused. |
| 2026-10-23 | Before any Phase I outcome generation, amended the preregistration to use 97.5% paired intervals with a Bonferroni adjustment across the two generator-family opportunities for a primary claim, score all next-tag transitions so cause-mixture prevalence changes are observable, and pin `PYTHONHASHSEED=0`. |
| 2026-10-23 | Completed Phase I without engine changes: 20 shifted and 20 stationary-control worlds in each of two generator families. The primary success rule was not met; cause-mixture comparisons were inconclusive and mapping-swap baselines exceeded the control false-alarm gate. Recorded results in `docs/regime_shift_results.json` and journal §29. |
| 2026-10-23 | **Preregistered Phase J gradual post-shift adaptation before implementation or outcome generation.** Defined two gradual-transition world families, 20 paired seed-varied shifted/control worlds, shift-specific predictive-loss and final-performance gates, and descriptive settling time. The live study remains paused; the cognitive engine is frozen. |
| 2026-10-23 | **Completed Phase J** on 80 paired shifted/control worlds without engine changes. Organica failed both primary gates in both families; the two simple baselines had much lower predictive NLL. Recorded all per-world curves and paired intervals in `docs/post_shift_adaptation_results.json`; journal §30. |
| 2026-10-24 | **The fresh-clone check was failing, and the repository was fine.** `benchmarks/clone_check.py` clones with `--depth 1`, which fetches only the tags pointing at the commit it fetched — so a release tag on an ancestor commit is absent locally — and `test_a_git_tag_exists_for_the_version` asserted against that empty tag list. The test was wrong, not the repo: the witness for "can a stranger check this version out" is the **remote**, not the local tag list. The check now consults `git ls-remote` when the checkout is shallow, and a full checkout with no tag still fails exactly as before. Reproduced the failure in a shallow clone before fixing it. |
| 2026-10-24 | **Release 0.7.0 published, and the package version moved to 0.8.0.** The `v0.7.0` tag existed but had no release page, so the link in `CHANGELOG.md` was a 404; the page now exists and the tag it points at (the complete 0.7.0 changelog) is unchanged. Separately, master had drifted **13 commits past the `v0.7.0` tag while still declaring 0.7.0**, so the version number named a release that master was not and anyone installing from master got a different artifact under the same number. The version is now **0.8.0** in all three declarations (`organica/__init__.py`, `pyproject.toml`, `CITATION.cff`) with a changelog entry marked `(unreleased)`. `tests/test_versioning.py` now enforces the invariant: **if a tag `v<version>` exists, it must point at the current commit**; an `(unreleased)` version is allowed to have no tag, because there is nothing to check out yet. The guard was proved to fire by reconstructing the lying-version state in a throwaway clone. New rule 10 in AGENTS.md. |
| 2026-10-24 | **The Tier-1 campaign artifact was regenerated, and the two missing artifacts now exist.** `docs/discovery.json` and `docs/figure_discovery.svg` were referenced by `CHANGELOG.md` and the facts sheet but had never been produced, because the published `docs/force_matrix.json` was assembled *before* the discovery instrumentation was added and so carried no `series.discovery` for `benchmarks/discovery_report.py` to read. The campaign was re-run on the current build and the artifact reassembled from the run's own per-colony part files. **Every shared metric and every other series is bit-identical to the published artifact**, so this is a re-issue of the same result with the discovery history attached, not a new result. The six colonies ran in two batches (five in parallel, then the slowest alone, because the first batch was interrupted); the batching is recorded in the artifact's provenance and is a wall-clock fact, not a scientific one. |
| 2026-10-24 | **A correction to the campaign's headline claim.** Regenerating the Tier-1 artifact (see the row above) meant checking every published claim against the regenerated file rather than assuming it had survived, and one did not. Journal §23.3 said every colony "does not change it again for 2,999 cycles". Measured cycle by cycle: the **retained** belief count is exactly **15 in every cycle of every colony**, but the **pre-retention pool is modal, not constant** — it dips to 16 beliefs over 6 competing subjects and returns, in 2,964/2,999 cycles (98.8%) for FULL, 99.5% for SALIENCE and NO_DREAMS, 98.6% for NO_CONTRADICTIONS, 98.1% for ANTI_EIG, and only **2,277/2,999 (75.9%) for `NO_QUESTIONS`**, whose excursions run as late as cycle 2,738. The excursions are 1–17 cycles long in the other five arms and all end by cycle 539. **No launch gate is affected** — G-CS, G-P1, G-SUP and G-EXP hold in 100% of cycles in all six colonies and G-SUS is 100% in every tail half, re-verified from the regenerated artifact; G-P1/G-SUP need the pool to exceed 15 and 16 does. The verdicts, the noise floor, the inventory totals and the +10,776% support growth are unchanged. The exception is the interesting part: `NO_QUESTIONS` is also the arm that discovers the most (112 items, 95% by cycle 977) and the only one still finding new items deep into the run — the arms that stopped discovering are the arms that stopped moving, which points the same way as H24. Corrected in place in `docs/FORCE-MATRIX-RESULTS.md` §2, `docs/FACTS-SHEET.md` §I1 with the measurement in a new **§S**, `README.md`, `CHANGELOG.md` (0.8.0, with a pointer at the 0.7.0 entry), `docs/ORGANICA-V2-DESIGN-NOTES.md` and `docs/WORLD-SCALE-PREREGISTRATION.md`. Journal §31. |
| 2026-10-24 | **Repository hygiene.** The local `master` branch had never actually been advanced past the overnight merges — a fast-forward had landed on a since-deleted PR branch instead, leaving `master` 13 commits behind its remote while the working tree looked current, which is what made `git rev-list --left-right --count origin/master...master` report a divergence that `git rev-parse` contradicted. `master` is now level with `origin/master`, and the three orphaned feature branches are deleted. `AGENTS.md` updated: the research journal is at **§1–§30**, not §1–§23; the Phase H/I/J preregistrations are listed as frozen-before-the-run documents; and the new benchmark commands are listed. The pre-G9 master plan's Phase A deliverables list `docs/generations/GEN_0.md`…`GEN_8.md`, which were never produced as separate files — the generation specifications live in `docs/architecture.md` and the manual's layer tables, and an amendment in the plan records this rather than leaving a dangling reference. A sweep of every repo-relative path referenced across the markdown files now resolves, apart from the per-generation specification files the pre-G9 plan lists and never produced. |
| 2026-10-24 | **Phase K is runnable, resumable, and watched.** The campaign is long — the Phase K worlds carry 16 to 28 distinct tags against the Tier-1 lattice's 7, so a cycle costs roughly three and a half times what it did there, and the full thirty-seed matrix runs for a couple of hours of wall time. Three changes make that safe. **Results are collected with `as_completed` rather than `pool.map`**, because `pool.map` yields in submission order: one slow seed blocked every checkpoint until it finished, and when the first run was stopped, only the single seed that had landed survived. **The results file is written atomically** — to a temporary file and then renamed — so a kill during the write cannot truncate it, and **an append-only live recording** is flushed after every seed to `docs/phase_k_results.ndjson`, which a resume can rebuild from if the results file is ever lost. `--resume` skips the seeds already done. `temp_db` creates a directory per call and the harness was leaving them behind — 775 leaked directories, now cleaned up, and the directory is removed after each run from now on. |
| 2026-10-24 | **Published 0.9.0, and froze Organica 1.** 0.9.0 is published as the **archival reference** for the V1 record: the Phase K result (all three families REVERSED), the V1 synthesis, the six-family negative-results map, the corrected claims, and the README refresh. **Organica 1 is frozen** — not abandoned, and not "no more commits": **no more architectural modifications to the engine.** The frozen files are `organica/sleep.py`, `memory.py`, `paths.py`, `streams.py`, `branch_streams.py`, `scale_streams.py` and `ground_truth_worlds.py`, plus the published result artifacts. Benchmarks, harnesses, documentation and the action list stay free, and Phase L lives entirely in `benchmarks/` — so the research continues against a stable reference object. **The freeze is enforced, not just declared:** the new `tests/test_v1_freeze.py` reads the frozen files out of the `v0.9.0` tag and compares them byte for byte with the working tree, failing and naming the difference if one differs, and skipping honestly when the tag is not reachable (a shallow clone). This repository's history is a history of promises drifting — the version naming a release master was not, the changelog linking a 404, the "structure flat" claim being an overstatement — and each of those was caught by an instrument rather than by reading carefully, so the freeze is an instrument too. Added `docs/V1-FREEZE.md`; added §8.7 and finding 13. |
| 2026-10-24 | **The V1 synthesis, and a README that had fallen behind.** The README still declared package version 0.8.0, still called 0.7.0 the latest release, and had no mention of Phase K at all — it was written before the campaign and had drifted. It now carries the Phase K result, the six-family negative table, a **"What is established"** section (which it was missing entirely, so it was showing only the negative half of the picture), and a pointer to the synthesis. **Added `docs/V1-SYNTHESIS.md`**, the formal read of what V1 established and what it did not. It adds no new evidence — it is a reading of the record, and every claim in it cites a committed artifact. Its content: development, history-dependence, curriculum-sensitivity and trajectory-divergence are **supported**; external advantage is **not**, across six task families; and the finding that most redirects the work is that **the internal developmental machinery is not what drives development** (P2/P3/P5 all REVERSED, and all three Phase K ablation intervals contain zero) — what moved development was the curriculum and the structure of the stimulus. It states the two goals the project could serve (dynamic intelligence — supported; LLM replacement — not), and the danger of letting the second goal's urgency drive the first goal's method. It closes with the question the evidence leaves open: **what properties must a developmental intelligence have to remain adaptable without losing coherence?** — and with the note that K3's 2×2 makes this precise: Organica is not incapable of revision, it is **priority-ordered**, so the deficit is in displacement, not acquisition and not capacity. **No V2 is designed and no Phase L is launched.** Added manual §8.6 and finding 12; journal §34; README refresh. |
| 2026-10-24 | **Phase K ran to completion, and the search failed.** All thirty seeds (ten per family, three families) came back **REVERSED**: K1 Organica 0.5923 vs baseline 0.9360 (difference −0.3437, 98.33% interval [−0.3773, −0.3123]); K2 0.4111 vs 0.9846 (−0.5735, [−0.6162, −0.5309]); K3 0.0000 vs 0.8578 (−0.8578, [−0.8598, −0.8571]). No family is SUPPORTED and none is INCONCLUSIVE, so these are clean losses rather than ambiguous ones, and every verdict survives eight different bootstrap seeds and both leave-one-out checks. **The pre-committed terminal outcome H2 fired exactly as written down before the run**: three more task families are ruled out, the negative-results map grows, and **no V2 is designed**. The ablations came back empty — `NO_QUESTIONS` −0.0095 [−0.0328, +0.0140], `NO_FALSIFICATION` +0.0241 [−0.0048, +0.0495], `NO_DREAMS` +0.0000 — so question generation, falsification and dreams are **not load-bearing** for the tasks they were built around (within one implementation, on synthetic worlds; a mechanism cannot show an effect on a task the organism was already losing by a wide margin). The **K3 zero was root-caused rather than reported as a number**: the late structure appears in **0 of 150 cycles** (not a final-cycle artifact), every candidate type except `anomaly` mentions **0 of 12** late tags (nothing left unread by the edge extractor), and a 2×2 control across five seeds shows the late group is incorporated **only when it is strictly stronger** than the group that arrived first — so the exclusion is a salience/priority competition under a bounded belief pool, which is the risk §6 of the preregistration named before the run. Added `benchmarks/phase_k_diagnose.py` (per-cycle, under-read and 2×2 checks), `docs/phase_k_results.md`, `docs/phase_k_results.json` and the live recording `docs/phase_k_results.ndjson`; added **§8.5** and finding 11; added decision **13**; facts sheet **§T**; journal **§33**. The campaign ran across two background chunks because it exceeded a single command's time limit, and the resumable harness meant no seed was lost or re-run; one bookkeeping note is recorded rather than hidden — the live recording holds **29 of 30** seeds, because K1/20261023 was completed by an earlier harness version before the checkpoint existed and was carried in through the results-file resume path. |
| 2026-10-24 | **Released 0.8.0, and opened Phase K.** 0.8.0 is published as a **research-integrity release** — corrected clone verification, corrected version/tag semantics, the two missing campaign artifacts regenerated, the cycle-1 fixation claim corrected, the negative external-validity results recorded, and the documentation synchronised with the measurements. Its release page now exists, so the link in `CHANGELOG.md` resolves. The project question changed: from *can we make a developmental architecture?* to *what class of problems benefits from one?* Phases H, I and J were three negative attempts, not a verdict on V1 — three tasks were negative, and an infinite number were not tested — so **no V2 is designed**. Instead **Phase K: Comparative Advantage Search** opens, with three candidate task families (K1 incremental world modeling, K2 belief revision, K3 longitudinal knowledge integration), each derived from a mechanism the project has actually measured, each scored against the strongest simple baseline that could plausibly solve it, and each with a matched within-architecture ablation so that a win can be attributed rather than merely seen. The protocol is frozen in `docs/PHASE-K-PREREGISTRATION.md` and was committed **before any Phase K outcome was generated**. Three safeguards are built into it: the simple baselines are swept over a declared grid and their **best** score is used, so a strawman cannot manufacture a win; the harness is validated against the Phase H task, where Organica's loss is already known, and the campaign does not run if that control fails; and **"no family confirmed" is a pre-committed terminal outcome** that does not authorise a V2. The harness was run once at one seed and one tenth scale before the freeze; that pilot is disclosed in the preregistration and is **not evidence**. The package version is **0.9.0** for the phase. Journal §32. |
| 2026-10-25 | **The Phase L pilot exposed four harness defects, and the apparent negative result it produced was an artifact.** The reduced-scale pilot printed `DI = 0.000` and `PI = 0.611` at **all eight** points of the support-ratio sweep — a clean-looking negative result of exactly the Phase K K3 shape. It was not a result: the support ratio was not varying anything. The late group's arrival was an **absolute** cycle number while the pilot ran fewer cycles than that, so the late group never became active and the late structure was never available to measure; a ratio with a zero denominator was reported as `0.0`, so the harness reported "nothing was displaced" eight times in a sweep where nothing could be displaced. Two further defects: the **contradiction arm (V5) shared a feature of the late group with itself**, so the world was byte-identical with the arm on and off and V5 measured nothing; and the **density arm (V3)** chunked the event stream at a fixed rate while the arm varies it, so at density 4.0 the engine saw 7,200 of 28,800 events while the harness reported a complete run. A fifth defect was found by reading: the **RT bootstrap was resampling the DI–PI gap** rather than the **crossing location** that criterion 4 is about, and reporting a min/max rather than the preregistered percentile interval. **Why the two existing audits did not catch any of it: both check the METRIC, and the metric was fine — the DESIGN was dead.** An audit of the instrument is not an audit of the experiment. A third audit now exists — the **degeneracy audit** — checking that every cell has a denominator, that the support ratio changes the early/late event mix, that the contradiction arm differs from the plain arm, and that the density arm changes the event count. It earned its place at once: the first version of the audit had a scaling inconsistency with the campaign builder and the audit caught it by failing the run before anything executed. Unmeasurable quantities are now reported as not measurable and **excluded, never zeroed**. Recorded as **Amendment 1** in the preregistration, made before any Phase L outcome existed: no hypothesis, variable, metric, baseline, success criterion or terminal outcome was changed, and no gate was relaxed — one audit was added. After the fix the axis is live (DI 0.000 → 0.667 across the sweep, one seed, reduced scale — a disclosed pilot, never evidence). **No Phase L campaign has been run and no Phase L outcome exists; the protocol awaits your review.** Added **§8.8** and finding 14; journal **§36**; facts sheet **§V**; AGENTS.md rule 13; CHANGELOG 0.10.0. |
| 2026-10-25 | **The Phase L protocol review, and the hunt for hidden degeneracy.** The owner reviewed the preregistration and authorised the campaign, with four changes. **The decision interval is corrected from 98.33% to 99%**: the protocol glossed 98.33% as "Bonferroni across the arms", but across five arms Bonferroni gives 0.05/5 = 0.01 (a 99% interval) while 98.33% is 0.05/3 — Phase K's factor, carried over by accident. The intent governs; the stray percentage is the accidental constant. Phase K's own figures are unaffected. **Success and failure are now stated plainly** (protocol §6.1): success is a reproducible displacement curve with an interior crossing; failure is a flat DI, a flat PI and no crossing — a characterization of the organism at one pole, and a publishable one. The campaign must be able to fail. **A new diagnostic, the Displacement Score `DS = DI − PI`**, because DI and PI are not opposites: DI 0.8 / PI 0.8 is *coexistence*, not revision, and K3 already established that acquisition and displacement differ. DS is a diagnostic only — not a metric, not a criterion, in no verdict. **Revision latency is elevated to co-primary reporting** (same endpoint, different developmental behavior), with the four success criteria unchanged. **Hysteresis is deferred, not forgotten** — the reverse sweep is the natural successor phase. Before running, a **pre-flight audit for the degeneracies the pilot did NOT expose** was added, and all five checks pass: the engine is **deterministic** for a given seed (so the paired bootstrap resamples something real), different seeds give different results (4 distinct of 4), every arm has a **full denominator** (18/18), the **V4 belief cap binds** (peak beliefs 11 → 15 against a cap of 15 — so V4 is not inert, unlike V5 was), and the protocol's own claims hold. A **fourth instrument audit** now keeps the V4 check honest permanently. Two quietly-wrong things were fixed: the results file recorded `PYTHONHASHSEED=0` whether or not it was set (it now records the actual value and warns), and the checkpoints recomputed the 10,000-replicate bootstrap and the audits after every cell (now computed once). Recorded as **Amendment 2**, made before any Phase L outcome existed. |
| 2026-10-25 | **The Phase L primary axis ran to completion: 80 of 80 cells, and the verdict is `H3-L — INCONCLUSIVE`.** 8,057.8 s wall clock, 10 seeds per sweep point, `PYTHONHASHSEED=0` pinned and recorded as the *actual* value, 99.00% decision interval, 10,000 bootstrap replicates, engine = the frozen `v0.9.0` (verified unchanged by the freeze test). **All four instrument audits passed on the live run** and **no cell was unmeasurable** — nothing excluded, nothing zeroed. The V1 curve: DI 0.000 / PI 0.73–0.79 across 1:4–1:1 (preservation plateau) → DI 0.283 / PI 0.600 at 2:1 (coexistence) → DI 0.722–0.750 / PI 0.022–0.000 at 3:1, 4:1, 6:1 (displacement). **Three of the four pre-committed criteria are met:** DI monotone increasing with range 0.750; the curves cross at **3:1**, interior to the sweep; and the crossing is reproducible under a paired bootstrap with interval **[5.0, 5.0]** and **10,000/10,000** replicates finding it, eight alternative bootstrap seeds all `INTERIOR`, leave-one-seed-out 3:1 in **10 of 10**. **Criterion 2 — PI monotone decreasing — was not met:** mean PI rises 0.789 → 0.794 between 1:4 and 1:3 (+0.005 against a per-point sd of 0.070) before falling monotonically through the rest of the sweep. The criterion has no noise clause, it was evaluated once by the committed code, and it was **not** re-read, relaxed, or reinterpreted afterwards — the stable RT was not allowed to stand in for the criterion that failed. The pre-committed verdict is therefore INCONCLUSIVE: *raise n; conclude nothing*, and **no V2 is authorised** — V2–V5 were deliberately not run. Revision latency (co-primary report, not a criterion): 0/10 seeds reach DI > 0.5 at 1:4–2:1, 10/10 at 3:1 (mean 347 cycles, median 342), 285 at 4:1, 236 at 6:1 — the transition is abrupt rather than gradual. DS (diagnostic only) shows the transition passes through a coexistence band at 2:1 rather than a clean handover. **A wording defect in the protocol is recorded rather than exploited:** the `H3-L` bucket is described as *"intervals too wide to place RT"*, which is **not** what happened — the RT interval is the narrowest possible and criterion 4 passed; the verdict is INCONCLUSIVE because criterion 2 failed. Added `docs/phase_l_results.md` and the artifacts `docs/phase_l_results.json` + `docs/phase_l_results.ndjson`; added **§8.10** and **finding 15**; facts sheet **§X**; journal **§38**. Also in this commit: the harness now keeps the preregistered promise that `--resume` rebuilds from the NDJSON recording when the results file is missing or truncated (six new tests in `tests/test_phase_l_resume.py`, proved able to fail by three separate mutations). |
| 2026-10-25 | **Amendment 3 — the raise-n campaign on the primary axis, and a real defect in the bootstrap's pairing.** The n=10 run produced `H3-L — INCONCLUSIVE`, whose protocol-specified remedy is *"raise n; conclude nothing"*; the owner took that remedy literally and on the primary axis — **same sweep, same protocol, same criteria, no edits**. Seeds per point go **10 → 30** (the original 10 plus 20 new), so the campaign is a strict **superset**: the 80 original cells are **reused, not recomputed**, and 160 new cells are added. Sweep points, independent variable, metrics, decision interval, the four success criteria, the four terminal outcomes and the frozen engine are **all unchanged**, and the secondary arms V2–V5 remain unrun. **A defect was found while preparing the run:** the preregistration says criterion 4 is a *paired* bootstrap over seeds, but the implementation paired by **position in the records list** — and the records arrive in completion order, which differs from label to label (within 1:4 the seed order was `[32,27,31,29,24,25,23,30,26,28]`; within 1:3 it was `[24,23,26,32,29,30,27,31,25,28]`). Position-pairing therefore paired **unrelated seeds** across labels: an unpaired resample wearing the word "paired" on it — the same class as the four the pilot exposed. Each label now contributes a `{seed: value}` map and every label is evaluated on the same drawn set of seeds. **The fix does not change the n=10 result:** RT 3:1, interval `[5.0, 5.0]`, 10,000/10,000 replicates, eight alternative bootstrap seeds `INTERIOR`, leave-one-seed-out 3:1 in 10/10, same four criteria, same verdict — so the n=10 record is retained unmodified as `docs/phase_l_results_n10.json` / `.ndjson`. **The test that proves the fix** (`tests/test_phase_l_analysis.py`) asserts the bootstrap interval, crossing label, criteria and adjacent differences are **invariant under a shuffle of the record order**; the position-pairing implementation fails it, proved by reverting the fix and watching it go red, with the file restored byte-for-byte. **A new diagnostic — the adjacent paired differences** (99% paired-bootstrap intervals for each adjacent pair of sweep points) was added, because the monotone criteria are evaluated on the **mean** curve and therefore test the **sign** of an adjacent difference: *if the underlying curve is flat at one end of the sweep, the sign of a noisy mean difference is a coin flip at any n* — more seeds settle the **effect size**, not the sign. Recorded before the run: the three low-end PI steps are each individually consistent with zero at n=10 (+0.006 [−0.028, +0.044], −0.011 [−0.072, +0.078], −0.056 [−0.128, +0.022]) while the two transition steps are not (−0.128 [−0.206, −0.039], −0.578 [−0.689, −0.494]), and dDI is exactly 0.000 at every low-end step for every seed. So the run is expected to establish the low end as a **plateau** and is **not** expected to resolve the sign of the 1:4 → 1:3 step. **The analysis is now committed code** — `benchmarks/phase_l_analyze.py` replaces the scratch script that produced the reported numbers, with the same seed-paired bootstrap. Amendment 3 was committed **before the raise-n run existed**; 69 tests pass and the four instrument audits pass. |
| 2026-10-25 | **The raise-n campaign finished: 240 of 240 cells, and the verdict is still `H3-L — INCONCLUSIVE` — now with TWO of the four criteria unmet.** 30 seeds per point, 12,738.1 s, `PYTHONHASHSEED=0` pinned and recorded as the actual value, 99.00% decision interval, 10,000 bootstrap replicates, the frozen `v0.9.0` engine. All four instrument audits passed on the live run and **no cell was unmeasurable**. The campaign is a strict **superset** of the n=10 run — the original ten seeds are the first ten of the new list, so the 80 original cells were **reused, not recomputed** — and the reuse was verified: all 80 are present and byte-identical in the merged file, each point has exactly 30 cells with 30 distinct seeds, and the n=10 record is preserved as `docs/phase_l_results_n10.json` / `.ndjson`. **The Revision Threshold did not move:** still 3:1, interval **[5.0, 5.0]**, **10,000/10,000** replicates finding a crossing, eight alternative bootstrap seeds `INTERIOR`, leave-one-seed-out at 3:1 in **30 of 30** folds. **Criterion 1 flipped**: *DI monotone increasing* was met at n=10 and is **not met** at n=30, because the top of the curve dips 4:1 0.722 → 6:1 0.715. **The curve is a step function, not a ramp** — **DI = 0.000 exactly** at 1:4–1:1 for all 30 seeds, **PI = 0.000 exactly** at 4:1 and 6:1, DI ≈ 0.71 across the top, and two sharp transitions in between; revision latency goes from **0/30** seeds reaching DI > 0.5 at 2:1 to **30/30** at 3:1 (mean 356 cycles, median 351). **Both failing criteria fail on steps whose 99% paired interval contains zero**: +0.011 [−0.026, +0.044] at 1:4 → 1:3 and −0.007 [−0.037, +0.022] at 4:1 → 6:1, while every step whose interval excludes zero is a real transition (−0.111 [−0.157, −0.065]; dDI +0.502 [+0.443, +0.559], dPI −0.567 [−0.619, −0.522]). **The uncomfortable part, which is the useful part** (run after the outcome was known; it changes no criterion, no verdict and no prediction): resampling the 30 measured seeds shows criteria 3 and 3b hold in **100%** of random 10-, 20- and 30-seed subsets, criterion 1 holds in 19.3% / 16.1% / 0%, criterion 2 in 12.0% / 6.6% / 0%, and **all four together in 2.9% / 1.2% / 0%** — so the n=10 run's criterion-1 pass was itself one of the lucky 19%, and **strict monotonicity is not a property this organism's displacement curve has at any practical n**. That is not a re-scoring: the verdict stands, no boundary is claimed, and the criteria stand as written; it is a statement of *what the verdict means*. **The added seeds also moved the curve more than resampling should allow** — DI at 6:1 0.750 → 0.697 (p = 0.0022) and DI at 2:1 0.283 → 0.164 (p = 0.0103) against random 10-vs-20 splits — so a **seed-exchangeability audit** with 30 fresh, non-consecutive, pre-declared seeds was run to tell non-exchangeability from an unlucky draw; it is an instrument audit and produces no experimental claim. Added `docs/phase_l_results.md` (rewritten for the raise-n result) and `benchmarks/phase_l_seed_audit.py`; added **§8.11** and **finding 16**; facts sheet **§Y**; journal **§39**. |
| 2026-10-25 | **Phase L published its characterization — and the protocol verdict is unchanged.** The raise-n result is now read as **regime behavior separated by a reproducible transition region**, not as a continuous coherence–plasticity trade-off, and the two are deliberately kept as separate artifacts: the measurement record (`docs/phase_l_results.md`) says `H3-L — INCONCLUSIVE`, the synthesis (`docs/PHASE-L-SYNTHESIS.md`) says what the shape is, and neither re-scores the other. **Raising n is not the answer and will not be done again on this axis:** the reason to raise n was that the +0.005 PI reversal might be noise around an otherwise monotone curve *or* the curve might be genuinely step-shaped, and n=30 distinguished those worlds — the low-end steps are each consistent with zero, the plateaus are exact across all 30 seeds, and the monotonicity criteria fail *more* firmly. The campaign was not failing for want of precision; it was failing because the curve is not the curve the protocol expected. **V2–V5 remain unrun** (no Phase L outcome authorises a V2), and the secondary axes are now a more specific question than the one Phase L was written to ask: not *which variable moves a smooth boundary* but *why is the curve step-shaped* — what sets the width and location of the transition region. The synthesis also names the dangerous question and answers it: a stable, reproducible threshold at 3:1 is **not** a boundary, because the trade-off is not a continuum the threshold divides — the curve is flat on both sides of the crossing. Added `docs/PHASE-L-SYNTHESIS.md`; added **§8.12** and **finding 17**; facts sheet **§Z**; journal **§40**; README and CHANGELOG refreshed. |
| 2026-10-25 | **Phase M groundwork: the development audit trace specification.** On the owner's direction — the next decisive move is a **developmental auditability** layer, and the next question is no longer *can it develop?* (answered) but *does what it develops become usable in a new situation?* — the specification for the record that would let an investigator reconstruct **why** a structure survived, without asking the organism, was written against the frozen engine's **actual** report fields and persistence limits. **Level 1 (provenance) is available** (`get_ancestry()`, parent links already stored; bounded by depth 7 and the 4,000-event window). **Level 2 (evidence) is available with one correction**: `support_count` counts **temporal transitions** and `contradiction_count` is the subject's **competing flow**, *not* contradicting observations — so the record format as first proposed ("12 supporting observations, 4 contradictory observations") would have put a false claim at the center of the audit and is corrected in the spec. **Level 3 (selection) is available under the default `salience` policy without instrumenting the engine at all**: the report exposes only survivors, but the full contest — including candidates that died under the confidence rule and candidates that lost on rank — is reconstructible from the report's own Layer-2/3 outputs plus the persisted prior candidates. The spec fixes the record's fields, their exact semantics, the acceptance criteria (**six**, each able to fail: evidence-replay exactness, selection-reconstruction exactness, ancestry honesty, behavior invariance, field-honesty, trace/counterfactual separation), and the wall that counterfactuals live behind (*"candidate B would have survived without A"* is a **replay**, not a trace). **Two defects disclosed, neither patched** (the engine is frozen): `contradiction_count` is easy to misread (D1), and the temporal graph's lookback window has **no `event_type` filter**, so a supporting transition can originate from the organism's own previous sleep payload while co-occurrence and tag-frequency edges are world-scoped (D2). Added `docs/AUDIT-TRACE-SPEC.md`; manual §8.13 and finding 18; facts sheet §AA; journal §41; AGENTS.md rule 17. |
| 2026-10-25 | **The audit-trace specification's load-bearing claim was tested, and it held.** `benchmarks/audit_trace_probe.py` is an **instrument probe, not an experiment about the organism**: it runs the frozen engine on the frozen cause-world generator and, at every cycle, rebuilds the selection contest from the report and the substrate and compares. **Default arm** (the engine's own belief cap of 15): **120 cycles, 1,412 beliefs checked, A1 evidence replay 0 failures, A2 selection reconstruction 120/120 cycles**, 4 candidates died under the confidence rule, 0 lost on rank. **Stress arm** (cap 5, so the cap binds): **60 cycles, 290 beliefs checked, A1 0 failures, A2 60/60 cycles**, 3 died, **403 lost on rank**. The default arm alone was a weak test — its pool peaked at 12 against a cap of 15, so the *lost-on-rank* branch never fired — which is why the stress arm exists, and why the write-up says so rather than letting the weaker test stand. **The checks can fail**: `tests/test_audit_trace_probe.py` breaks the auditor on purpose (zeroing the curiosity term; dropping a tag from the temporal graph) and requires A1 and A2 to go red; they do. **What this establishes:** the rules transcribed into the specification are a faithful transcription, and **the selection contest does not require a hook inside the engine** — assembly, not instrumentation. **What it does not establish:** generality (one world family, one policy, one configuration), the `stochastic` policy (where the reconstruction degrades to a bound), the four remaining acceptance criteria (ancestry completeness, behavior invariance, field-honesty, trace/counterfactual separation), or anything whatsoever about learning, transfer or capability. Added `benchmarks/audit_trace_probe.py`, `tests/test_audit_trace_probe.py`, and the artifacts `docs/audit_trace_probe.json` and `docs/audit_trace_probe_stress.json`; spec §10; facts sheet §AA8. |
| 2026-10-26 | **The rule that keeps the trace from becoming a second inventory.** The audit layer is attractive, and attractive things become projects: it could be built, extended and admired without ever adjudicating a question the project wanted answered — which would make it a *second* inventory ("how many events resolve?"), swapping one measurement habit for another. The rule is therefore **pre-committed, not aspirational**: the next protocol's success criteria must contain at least one **trace-derived diagnostic**, and a result that fails it **fails the protocol even if the headline behavior is correct**. **The first instance is the disqualifier: *a predicted-correct result whose supporting evidence is self-sourced is not a transfer result.*** The trace reports the world/self split of every belief's support, because the temporal graph's lookback window has no `event_type` filter and a supporting transition can originate from the organism's own previous sleep payload (D2). That is the first concrete use of D2, and it is what turns a disclosed defect into a **live scientific instrument** — a defect that can defeat a claim is worth more than a defect that is merely recorded. A claimed revision must be visible as a change in a world-supported claim with its prior state resolved; a claimed explanation must resolve to event ids, never to counts and never to the system's own account of itself. **Second guard:** the trace's own metrics — evidence-trace completeness, lineage completeness, selection reproducibility — are **diagnostics of the instrument**, reported and never criteria. Recorded as spec §11, AGENTS.md rule 18, manual §8.14 and finding 19, facts sheet §AA9, journal §42. |
| 2026-10-26 | **The audit-trace probe was reviewed, and its headline was ahead of what it actually verified.** The first version reconciled the **aggregate** `precedes` table against the engine's reported support counts. That shows the auditor reproduces Organica's *counts* and its *selection decisions*; it does **not** show it can identify the individual experiences behind a count. The specification was corrected to say exactly that — **aggregate evidence reconciliation and selection reconstruction passed** — and event-level attribution was made its own check (**A7**), measured with a passive store-time observer. **Results: A1 1,412 beliefs / 0 failures, A2 120/120 cycles, A7 1,412 beliefs / 0 failures with 244 aggregate edges reconciling exactly** (default arm); A4 behavior invariance — observer on vs off, byte-identical reports — **passes**. **Three corrections, each verified against the source before being written down:** a cycle returns **14** candidate lists, not 13; the engine's lookback window **includes the event being stored** (so the window is the event plus two others, and within-event tag pairs also become temporal edges) — the specification's first replay rule was wrong; and **a post-hoc replay from the final log cannot reconstruct the window** (the engine's query has no `rowid` tiebreak, and sleep-candidate rows are pruned), so event-level attribution **requires** a store-time observer whose guard mirrors the engine's own `event_type != "sleep"` rule. **D2 is now measured, not feared: of 307,857 attributed support transitions, 53,980 (17.5%) were self-sourced** — roughly one belief-support transition in six rests on the organism's own sleep payload. That is the baseline the pre-committed disqualifier is read against. **The probe found two defects in itself** — an observer that attributed sleep-event transitions, and an invariance check that compared `ran_at` — both caught by the checks rather than by inspection. Five tests now cover the four axes, each with a deliberately-broken variant that must go red. |
| 2026-10-26 | **The self-sourced figure needed its denominator fixed.** The first version pooled the support of every reported belief across every cycle in which it was reported; because a belief's support count is **cumulative**, a transition that occurred early is counted again in every later cycle where the belief survives. That pooled number counts **support references**, not distinct evidence. The probe now reports three views: **distinct evidence behind reported beliefs** (802 of 4,481 = **17.9%** self-sourced — the disqualifier's figure); **pooled support references** (53,980 of 307,857 = 17.5%); and **all distinct transitions recorded** (5,436 of 12,583 = **43.2%**), including edges no reported belief ever rested on. **Correcting the denominator moved the headline only slightly** (17.5% → 17.9%) and that agreement is worth stating; **but it surfaced a separate and much larger number**: **43.2% of the organism's entire distinct transition surface is its own sleep output**, against 17.9% of the evidence actually behind its claims. Different surfaces, and the trace must report both rather than let one stand in for the other. **The forced-tie arm is now run:** the clock is patched so every four consecutive stores share a timestamp, producing **479 stores with a genuinely tied window**, and the observer reproduces the engine's choice anyway — **A7 stays exact** (2,589 distinct transitions, 241 aggregate edges reconciling, 0 mismatches; tie arm A1 692 beliefs 0 failures, A2 60/60 cycles). The honest statement: the **implementation** is deterministic for identical queries over identical data, so the observer's re-run selects the same rows; the **schema** still does not determine the window under a tie, and a replayer that did not observe at store time could not rely on it. Seven tests now cover the four axes, including one that requires the distinct view to be genuinely deduplicated. Recorded in spec §3.3, §6, §10, §11; facts sheet §AA11; journal §44. |
| 2026-10-26 | **The figure's population is now stated precisely, and the disqualifier became a per-claim rule.** The **17.9%** is a share of the **union of the unique evidence transitions behind beliefs reported during the run** — deduplicated, restricted to the edges those beliefs rested on. It is **not** a per-claim share, and it is **not** evidence that self-sourced support caused an incorrect prediction. A run-level share cannot carry a per-claim claim, so the disqualifier is rewritten as a **per-claim rule fixed in advance**: (1) report the world/self split for the **claim's own** support; (2) a **majority** of it must be world-derived; (3) its self-sourced share must be **no higher than the run's baseline rate** for beliefs; (4) the comparison is against the claim, never the organism in general, and a failed condition **fails the protocol even if the prediction was correct**. **Why the rule is conservative, and why that is stated rather than hidden:** the contamination is now **measured, not shown to be consequential** — nothing yet demonstrates that a self-sourced transition caused a wrong answer — so the disqualifier is a statement about **what counts as evidence of transfer**, not a claim that the organism is damaged by its own output. That is also why it is pre-committed: a criterion that only bites once the harm has already been demonstrated would never bite at all. **Whether self-sourced support *hurts* is now a measurable question, and the trace is the first instrument that can ask it — not asked here.** **Also: the observer's window match is an implementation match, not a schema guarantee** — the engine runs `SELECT tags FROM events ORDER BY time DESC LIMIT 3` and the observer runs the **same ordering clause** with a **wider projection**, so the two are not byte-identical SQL; the match is empirical on the tested SQLite implementation, and the evidence for it is **A7's exactness** (a window mismatch on any store would have broken the reconciliation). The **60-cycle forced-tie artifact is committed** as `docs/audit_trace_probe_tie.json` — 60 cycles, 479 tied windows, A1 692 beliefs / 0 failures, A2 60/60 cycles, A7 692 beliefs / 0 failures. Recorded in spec §3.3, §10, §11; facts sheet §AA12, §AA13; journal §45. |
| 2026-10-26 | **A pre-committed threshold must not be computed from the run it judges, and the window span was wrong by an order of magnitude.** **The reference rate is now FROZEN at 17.9%** — the distinct-evidence self-sourced share measured on the calibration probe — and is **not recomputed on the evaluated run**. A threshold derived from the same data it judges is not a threshold: a run whose beliefs happened to be unusually self-sourced would otherwise relax the criterion meant to constrain it. It may only be **re-calibrated on data that is not being judged**, recorded before the next protocol runs, and it is labeled a **provisional calibration value, not a precise universal cutoff** (one run, one world, one policy). **A3's definition is fixed in advance**, and it reports three things separately: **lineage reachability** (share of extant structures resolving back to Layer 1 within depth 7), **evidence linkage** (share of extant claims whose support resolves to event ids with a world/self split), and a **truncation split** — *aged out* (**a persistence problem**) / *depth-truncated* (**a representation problem**) / *no parent* / *missing record* (**a data defect**, and the one that would matter most). The two graphs are kept separate: Level 1 is candidate → candidate and **terminates at Layer 1 — no parent link points at an event**; Level 2 is claim → transitions → events. **And the measurement corrects an earlier estimate by more than an order of magnitude: the engine stores 2,374.68 sleep events per cycle, so the 4,000-event cognition window spans only 1.7 cycles — not the "roughly 40–130 cycles" this project previously asserted from a guess.** The estimate was wrong, and the correction is recorded rather than quietly fixed. Consequence: a lineage still being produced stays inside the window (candidates are re-stored every cycle), while one that stopped being produced is gone within about 1.7 cycles — so the developmental history of anything the organism has moved on from is unrecoverable, not slowly censored. **And the boundary A3 cannot cross: fidelity is not sufficiency.** The probe establishes that the auditor reproduces the implemented rule; it does **not** establish that an intact reconstruction is a uniquely correct account of why a belief arose. Recorded in spec §10, §11, §12; facts sheet §AA14, §AA15, §AA16; journal §46; AGENTS.md rule 19. |
| 2026-10-26 | **Seven literal template placeholders had shipped in the committed audit-trace specification**, inside sentences that assert results — so a reader would have seen a number that was never computed, when the value was sitting in a committed artifact the whole time. Six came from the second and third review rounds (`{ties}`, `{t_dist:,}`, `{t_edges}`, `{t_cycles}`, `{t_a1:,}`, `{t_a2}`) and one from this round's own script (`{share:.1f}`, caught before it was committed). Corrected in place from the artifacts: 479 tied windows, 2,589 distinct transitions, 241 aggregate edges, 60 cycles, 692 A1 beliefs, 60 A2 cycles, 692 A7 beliefs, 17.9% reference rate. The lesson is narrow: **a placeholder is silent** — it looks like a sentence in a diff, so another careful read will not find it. A mechanical substitution pass with a leftover-assertion did, and the guard is now standing as `tests/test_doc_placeholders.py`. **A check that must be run beats a check that must be remembered.** Facts sheet §AA17; journal §46; AGENTS.md rule 20. |
| 2026-10-26 | **A3 was measured, and it corrected the specification's own reasoning.** The ancestry auditor walks each cycle's structures' parent chains against the engine's window. **Lineage reachability 1.000** (8,061 of 8,061 structures resolve back to Layer 1 within depth 7), **evidence linkage 1.000** (1,412 of 1,412 claims resolve to event ids with a world/self split), **zero honesty errors**, and an empty structure-level truncation split — while the branch-level count shows **105 aged-out branches**, because every structure resolves through at least one branch still inside the window. **The window is NOT the binding constraint on lineage depth, and spec §12's claim that it was is corrected in place:** surviving candidates are re-stored every cycle (Layer-1 by the natural-selection decay path, higher-layer by the report's re-derivation and the stable-prior add-back), so a live ancestor stays in the window however old it is — what bounds a lineage is the **death of an ancestor**. **Measured: the window holds 3,998 candidates, the oldest last stored 1 cycle ago, content spanning 2 cycles.** **So the trace reconstructs everything the organism still holds, exactly — and the developmental history of anything it has moved on from is unrecoverable, because the organism does not hold it either. The engine's cognition window IS its memory.** That is a hard ceiling on the project's distinguishing property, and it is a property of Organica 1 as frozen, not of the auditor. Two sweeps prove the branches are reachable rather than inert: the window sweep falls from 1.000 to 0.000 at 25–50 candidates, the depth sweep from 1.000 at depth 7 to 0.221 at depth 1 (53 depth-truncated) — so **the engine's depth limit of 7 is not binding**. Added §8.15 and finding 21; facts sheet §AA18, §AA19; journal §47; AGENTS.md rule 21; spec §13 and the §12 correction; the probe now reports `A3_ancestry_honesty`. |
| 2026-10-26 | **The acquisition experiment was pre-registered — and two diagnostic probes changed what it asks.** The blank-slate question is now **can experience create a structure that remains useful after the originating experience is gone?** — and **does the organism carry structure forward, reconstruct it from evidence, or do both under different conditions?** The design is six cells (parent removed or not × source experiences removed or not × removal applied to the **observer** or to the **organism**, because removing a parent from the auditor's reconstruction tests the trace and removing it from the organism's state tests the maintenance mechanism). **Two diagnostics, quarantined as design inputs rather than predictions:** a surviving structure's parent set is identical in **94.5%** of structure-cycles, but **87.2% of all 8,416 lineage links point at structures re-derived in that same cycle** — so the lineage is **re-derived, not carried**, and this corrects an earlier reading of mine. And the engine's survival rule is **asymmetric across layers**: `_natural_selection` decays and prunes **Layer 1 only**, so Layer 1 survives only if current experience keeps producing its content key, while Layers 2–4 are never decayed and persist as rows with **re-derived edges** — meaning "persistent reconstruction" is accurate for Layer 1 and misleading for the rest. **The sharpest prediction is computed from the source, not fitted:** a Layer-1 structure whose key stops being produced is pruned after `⌈log(0.15/c)/log(0.8)⌉` cycles — 4 from 0.3, 6 from 0.5. **Q1 (internal persistence) and Q2 (external provenance) are scored separately**, and the decisive control is a **replay learner** that stores episodes verbatim and regenerates nothing: if continuity is reconstruction rather than recall, perfect recall is the harder baseline, and beating it is the result. Added `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`; §8.16 and finding 22; facts sheet §AA20–§AA22; journal §48; AGENTS.md rule 22. |
| 2026-10-26 | **The acquisition pre-registration was reviewed and rewritten as Revision 2, after five defects were found in its plan.** The endpoint was **DI** — a *structural displacement* ratio, not a prediction score — and it is now a **ground-truth prediction score** on a fixed vocabulary, with F1 at 0.5 primary and balanced accuracy and Brier co-reported. *"Source experiences removed"* did not say what derived memory survived, so the condition is now named **"episode removal with learned graph retained"** and the **same rows are removed from every learner's store** — which is what makes the comparison about reconstruction versus replay rather than about unequal access to evidence. The cell matrix was not specified; it is now **one complete table, 10 runs per seed, 30 seeds, 180 engine runs, a prediction for every cell**, with `P-none × E-pres` as the untreated baseline. The plan was not executable; the generator, target relation, phase boundaries, seeds, sample size, decision rule and both baselines' algorithms and tuning grids are now pinned. And the audit build had **no stop condition**; it is now explicit: **close A5 and A6 only, then tag, freeze and stop** — no feature may be added afterwards, though the instrumentation may be *fixed* if found wrong. The owner's standing decisions are recorded: **V2 not cut, live study not restarted, V2–V5 not run, no further open-ended audit work.** Added `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` (Revision 2); §8.17 and finding 23; facts sheet §AA23–§AA26; journal §49; AGENTS.md rule 23. |
| 2026-10-26 | **Five claims in the project's own summary were wider than the checks behind them, and all five were narrowed.** (a) *"Revision exists"* → **structural displacement**: Phase L's `DI`/`PI` are structure-retention indices, and belief revision — measured separately in Phase K — was a clean loss (**0.4111** vs **0.9846**, difference **−0.5735**, 98.33% interval **[−0.6162, −0.5309]**, **REVERSED**). (b) The **3:1** crossing is robust **within this engine, world family and support-ratio axis**; the eight alternative bootstrap seeds test **resampling stability, not new worlds**, so 3:1 is **not a general threshold for Organica**. (c) **Path dependence** is supported, **strict order dependence is not tested** — the curriculum comparisons vary the event multiset and order together, and isolating order needs the multiset held fixed. (d) On transfer, **no positive transfer has been demonstrated and the measured cross-domain result was negative** (**−0.4863** across 12 domain pairs, mean shared vocabulary **0.17 tags**); other forms remain untested. (e) **"Independently auditable" means independently *reconstructed from the engine's state*, not independently *replicated by another lab*** — and the trace covers surviving, current structures rather than their full past. **No measurement, verdict or criterion changed**; the protocol verdict `H3-L — INCONCLUSIVE` and the six negative task families stand. This was a correction to *language*, made against the existing record before the acquisition experiment ran, and recorded rather than quietly applied. Added §8.18 and finding 24, six common misreadings, and the §2 status row; README banner and findings; `docs/PHASE-L-SYNTHESIS.md` §2.2, §2.3a, §3.3, §8; `docs/V1-SYNTHESIS.md` §2.2, §3, §5, §9; `docs/AUDIT-TRACE-SPEC.md` §10, §11; `docs/EMERGENCE-CRITERIA.md` §4; facts sheet §AB1–§AB7; journal §50; AGENTS.md rule 24; CHANGELOG. |
| 2026-10-28 | **The acquisition endpoint was audited, the benchmark was rebuilt, and the campaign stopped at its own gate.** Seven defects in the endpoint were confirmed against the code: the task and the readout described different relations; F1@0.5 was degenerate (the Bayes-optimal model scored **0.0000**, exactly like the trivial model); the projection was directional where the gold relation was not; the "fixed-rule ceiling" was a relation oracle, not a prediction ceiling; retention and transfer were one number with two names; the engine's taxonomy has no category for a tight group (a co-occurrence-defined group has clustering 1.000, and `_classify` requires <= 0.4 for a concept); and the generator's regime switch is relation-invariant. The world was then measured against its **strongest** baseline rather than its base rate, which showed the redesigned law is **first-order Markov** (a bigram sits **0.027462** nats from the ceiling; the headroom over the strongest baseline is **0.005647** nats, against **0.105032** over the base rate) — so that world was reclassified **CALIBRATION / CONTROL**. A **compositional task** was built to measure what it could not: withheld *combination* of familiar elements, tag-to-cell mapping randomised per world. Its gate passes on 30 independent worlds — gap **+0.1035** nats, 99 % interval **[+0.0996, +0.1074]**, lower bound clearing the 0.05-nat bar, with the held cell's gap **4.6x** the rest so the headroom is *generalization* headroom. A separate parallel run then measured the **frozen engine** on that task and **failed Gate 13 on every inspected seed**: asserted structure coverage **0.0 %-2.7 %** (0-3 of 112 edges) against **112 / 112 (100 %)** raw temporal coverage. The cause is **one named bound** — `MAX_PREDICTIONS = 20` sorted by raw temporal count, which the within-cell pairs monopolise because a cell's two tags co-occur in every one of its events; raising **only** the cap to 1,000 restores **98.2 %-100 %** coverage and clears the gate on all five paired seeds. Organica's readout scored **0.453018** against Replay **0.347521**, Statistical **0.347273** and base rate **0.409581**. **Transfer was not measured, and it is not a transfer failure**; the 600-cell factorial did not run. **An instrument defect was found while reconciling the two results:** the harness and the runner each implemented "Gate 13", the harness on the *raw temporal* basis (it returned **100 %** and passed) and the runner on the *asserted* basis (it returned **0.0 %** and failed) — on the same seed, on the same world — so the harness held a gate that **could not fire**. It now implements Amendment 1's dual accounting, gates on the asserted figure, exposes the cap-raised treatment so the failure is attributable, and its test asserts that Gate 13 **fails**. The lessons are: **run the perfect model *and the strongest simple model*, and require the lower uncertainty bound across independent worlds** (a base rate is the weakest possible comparator); **the metric choice and the readout choice are not separable** (an ad-hoc readout scores 1.655377 on structures a tuned backoff readout scores 0.362233); **a grading-only control is not a control set** (the grouping oracle reaches 0.8679 of the span); and **a benchmark's headroom is not a learner's margin** — the +0.1035 is the room between the ceiling and the best simple model, not what any learner achieved. Added §8.19 and finding 25 and the §2 status row; `docs/ACQUISITION-ENDPOINT-AUDIT.md` (new); `docs/ORGANICA-V2-DESIGN-BRIEF.md` §9.6-§9.7; `docs/V2-CAPACITY-DESIGN-BRIEF.md`; facts sheet §AC; journal §51; AGENTS.md rule 25; CHANGELOG. |
| 2026-10-28 | **The Gate 13 causal account: "bottleneck" is not "deepest cause."** The parallel session's write-up named `MAX_PREDICTIONS = 20` as the cause of the acquisition failure, on the evidence that raising the cap to 1,000 restored coverage to 98.2 %-100 %. That was sound on its own evidence, but it left three probes written and uncommitted that ask whether there is a *better* fix than a bigger budget. Running them, and adding a fourth, changes the answer. **All seeds used are diagnostic (`20261100`-`20261105`); the confirmatory sample (`20261106`-`20261130`, 25 seeds) is untouched.** The world's relations **are** in memory (raw temporal coverage **0.97-1.00**, **1.0000** on all six 2-tag seeds), but they are about a **third** of the candidate space and are **not** the high-count rows: **precision never exceeds 0.3438** at any budget under either allocation rule. A **1-tag** stimulus removes the within-cell pairs by construction, quintuples coverage to **0.1719-0.1953**, and still fails **0 of 6** seeds. Coverage is a steep monotone dose-response in the cap -- **0.0000-0.0268** at 20, **0.0089-0.0714** at 40, **0.0893-0.1786** at 80, **0.9911-1.0000** uncapped -- needing **240-244** asserted edges, about **12x** the budget; and at the frozen cap the law-bearing **inter-cell** edges are **0-3** while intra-cell edges are **28-39**. A **per-source** allocation rule is **not** the fix (258-286 edges for coverage 0.72-0.77, where the global rule reaches 0.95-0.97 at 320). **So the deepest cause is PRECISION, not capacity**: in a candidate space where the signal is a third of the rows and is not clustered at the top of any frequency ordering, no frequency-based selection can find it. The specific pollution is **internal vocabulary** -- **27-34** distinct sources for a 16-tag world. Also found: **three different things are called "Gate 13"** and they disagree (the protocol's, on the asserted structure, FAIL; the capacity sweep's, a dose-response; the observation probe's, on the `precedes` table under a *per-source* rule, PASS) -- the third is a different selection rule over the same table, and the filter it uses selects on the world's own tag list and is therefore an **oracle**, not an organism-side fix. The V2 capacity brief's premise ("bounded structural allocation") was measured and does **not** hold, and two of its design objectives are refuted; it has been retitled as a **sub-brief** and given an addendum. Added `docs/GATE13-CAUSAL-ACCOUNT.md`, `benchmarks/probe_allocation_rule.py`, `docs/gate13_capacity_sweep.json`, `docs/gate13_allocation_rule.json`; updated §8.19, finding 26, `docs/ACQUISITION-ENDPOINT-AUDIT.md` §8.3, `docs/ORGANICA-V2-DESIGN-BRIEF.md` §9.7, `docs/FACTS-SHEET.md` AC11-AC13, `AGENTS.md` rule 25(d), journal §52, CHANGELOG. **No V2 build is authorised.** |
| 2026-10-29 | **The relation-separation probe: the separation is real, oracle-free, and not sufficient.** The owner's reading of the Gate 13 evidence proposed the next question -- *can world relations be separated from engine-generated relations without modifying the frozen engine?* -- and it has now been measured. The mechanism was located first: `memory.py:261` gates the **trigger** of edge recording (`if event_type != "sleep"`) but `memory.py:332` does **not** gate the **lookback window** (`SELECT tags FROM events ORDER BY time DESC LIMIT ?`), so a world event can take its `tag_from` from a sleep row. That is **D2** in the audit-trace spec -- disclosed but never quantified. Rebuilding the table offline with a world-only window removes **35.7 %-40.7 %** of its rows, and **100.0 %** of the removed rows have a sleep-sourced `tag_from`; the separation uses `event_type`, which the engine already records, so it is **not an oracle** (unlike yesterday's world-vocabulary filter, which is). **But with every contaminated row removed, coverage at the frozen cap of 20 is still 0.0000-0.0446** and the top 20 is still **75-100 % intra-cell**. The substrate is **756-772 world events against 152,186-263,533 sleep events** -- **201x-341x**. Two distinct crowding mechanisms were in play: in the **1-tag** stimulus the crowding is the engine's own vocabulary (first world edge at rank **31**; the top 30 rows all `internal->world`, verified), and in the **2-tag** stimulus, once that is removed, the crowding is the world's own co-occurrence (intra-cell pairs out-count the law's transitions by ~an order of magnitude). The V2 requirement list is now **three** -- provenance separation, relation-family separation, and a **ranking that is not raw frequency** -- and the third is the hard one, and the one the capacity sweep showed cannot be bought with budget. Added `docs/GATE13-RELATION-SEPARATION.md`, `benchmarks/probe_relation_separation.py`, `docs/gate13_relation_separation.json`; updated finding 27, `docs/GATE13-CAUSAL-ACCOUNT.md`, `docs/V2-CAPACITY-DESIGN-BRIEF.md` (second addendum), `docs/FACTS-SHEET.md` AC14, journal §54, CHANGELOG. **No V2 build is authorised.** |
| 2026-10-29 | **The ranking requirement, measured: every criterion the engine already stores was tested, and all of them fail.** The third V2 requirement -- a ranking that is not raw frequency -- had been called the hard one with no precedent in the engine. It has a precedent, and the precedent is the finding: `sleep.py:1139-1160` computes `ratio = count / max(source_freq, 1)`, stores it in every candidate's evidence, uses it for **survival**, and then sorts by **raw count** for **admission**. So a 60-cell grid was run over fields the engine already stores (`temporal_count`, `source_frequency`, `target_frequency`, `ratio`) x 2 tables x 2 frequency scopes x 3 seeds. **The best cell reaches coverage 0.0804 at precision 0.4500 against a 0.50 gate -- six times short.** Neither fix works alone (0.0089); together they take coverage from 0.0000 to 0.0804 and precision from 0.0000 to 0.4500. **The engine's own normalized criterion is actively harmful here:** on the raw table under the engine's own scope, `ratio`, `cosine` and `pmi` each select **20 engine-vocabulary edges and zero world edges** on every seed. The mechanism is measured, not inferred: `_record_tag_counts` is inside the `if event_type != "sleep":"` block, so **`tag_counts` is world-scoped** and the engine's own words have **no frequency entry** -- `freqs.get(tag_from, 1)` returns 1, so `ratio = count / 1 = count`, the maximum possible for that count. Adding a self-inclusive frequency scope flips the failure the other way: the engine's sleep output **names the world's tags** (`sable` 2,601 times, `olive` 7,753, `maple` 35,986, `cedar` 52,070), so the world's tags acquire enormous denominators and are penalised, and the engine's *rare* metadata words win (best world edge by the same criterion: `sable -> fern`, ratio **0.0177**, against `mutation -> cedar` at 0.1654). **The world's vocabulary and the engine's own vocabulary are not separable by frequency in either direction**, so the discriminator cannot be a per-tag statistic -- it must be a **relation-level** property, and the only one available is *which event the relation came from*. Added `docs/GATE13-RANKING-CRITERION.md`, `benchmarks/probe_ranking_criterion.py`, `benchmarks/probe_ranking_mechanism.py`, `docs/gate13_ranking_criterion.json`; updated finding 28, `docs/FACTS-SHEET.md` AC15, journal §55, CHANGELOG, `docs/V2-CAPACITY-DESIGN-BRIEF.md`. **No V2 build is authorised.** |
| 2026-10-29 | **The audit build's closure was recorded in six places, and two documents still said the opposite — so eleven passages across four documents were corrected.** The owner found that **Paper 02 contradicted itself**: its abstract and §3 said A5 and A6 "remain pending" and the instrumentation "not yet frozen", while its own draft-status line and its conclusion said they had closed. The **V2 design brief's §4.3 still read "nearly, but not fully, closed"**, and five further passages in §7, §10 and §11 carried the same stale state; the superseded banners in `ROADMAP.md` and `docs/V1-SYNTHESIS.md` still described the audit build as unfinished and the pre-registration as Revision 2. Corrected: Paper 02's abstract, §3 and draft-status line; the V2 brief's §4.3 heading and body, build gate 4 (now marked **EXECUTED**), the gate-5 annotation that called gate 4 open, the §10 corrections table and the §11 table; and both banners. **A freeze recorded in six places is not a freeze if two documents still say the opposite** — and a self-contradicting document is worse than an out-of-date one, because it teaches the reader that its own sentences cannot be relied on. The sweep criterion was **one status, stated in every document that states it**. Added findings 29 and 30; `docs/FACTS-SHEET.md` AD1–AD2; journal §56. |
| 2026-10-29 | **The publication framing moved into the repository's own rule file, and the living guidance documents were set to American English.** **AGENTS.md rule 26** now states the two disciplines the owner settled on: **research-program structure is not publication structure** (the corpus is organized as a research-program map and a publication map kept side by side, so the layer map orients a reader without pressing every old manuscript or lab artifact into a paper), and **a claim's status names its scope** (four statuses — *supported within the tested scope*, *mixed / context-limited*, *reversed*, *not established / not measured* — with **not established is not refuted**, and a compound status required where the evidence splits). The current publication map, the claim-status vocabulary and the milestone (**making the first two manuscripts submission-ready**, not publishing them as they stand) live in `papers/README.md`. `AGENTS.md`, `README.md` and `ROADMAP.md` were set to American English; the **historical research record was not rewritten** — preregistrations, measurement records and the frozen journal sections are committed records, and normalizing them is the owner's call, not a cleanup. | **A rule that only lives in a document is a preference; a rule in the rule file is a constraint.** The publication framing was the most consequential decision of this cycle and it was the kind that is lost between sessions unless it is written where the rules live. |
| 2026-10-29 | **The first audit of Paper 00 and Paper 05 found two verified factual defects and one contradicted guarantee.** Paper 00 said *"this hierarchy spans **eight generations"*" and then listed **nine** rows (G0–G8); `docs/architecture.md` names it correctly — *"The 8 Generational Primitives"*, with **G0 = Experience** as the substrate and G1–G8 as the primitives. Paper 01's first draft made the same error and was corrected in the same pass. Paper 00 also stated **Law II** as an inviolable law (*"...`parent_ids` traceable to G0 events"*) without the project's own disclosure **D3**: the chain **terminates at Layer 1**. Corrected in place, with the disclosure inline. Paper 00's abstract also claims efficacy the record does not support — the *forms* of curiosity, dreaming and inquiry exist (G5–G8), the *efficacy* does not: Phase K's matched mechanism ablations all came back empty (`NO_QUESTIONS` −0.0095 [−0.0328, +0.0140]; `NO_FALSIFICATION` +0.0241 [−0.0048, +0.0495]; `NO_DREAMS` +0.0000 [0.0000, +0.0000], **all three intervals containing zero**), and **Law IV is never exercised** — experiments are generated, every consumer only prints them, and no Question can ever close. Paper 05's "zero synthetic self-contamination" guarantee is contradicted by the measurement (**17.9%** of distinct supporting transitions behind reported beliefs are self-sourced; **43.2%** of all distinct transitions recorded), which is why it needs a **new thesis** rather than a revision. Added finding 31; `docs/FACTS-SHEET.md` AD3; journal §57. **Paper 00's remaining broad claims and literature framing are still unaudited, and neither 00 nor 05 is ready to circulate.** |
| 2026-10-29 | **The historical record was normalized to American English, with the change proven to be spelling-only.** **234 words across 25 files**, including the preregistrations, the measurement records and the frozen journal sections. Three proofs run against `HEAD` for every changed file: **non-target content byte-identical**, **numeric-literal sequence identical**, and **structure identical** (headings, table rows, list items, lines) — all three pass on all 23 changed files. Inline code spans were never rewritten, so no identifier, path, tag, test name or constant changed. **A verifier that reuses the writer's parser inherits the writer's bug:** the first pass reported *"remaining: 0"* and was wrong by 88 occurrences, because the sweep and its check shared a document-wide code-span regex that mis-aligns on unbalanced backticks. The bug surfaced only because a second, differently implemented check — a raw-text scan with no span logic — disagreed with the first. Added finding 32; `docs/FACTS-SHEET.md` AD4; journal §58. **Every number, claim, verdict, date, method, seed and decision rule in the repository is unchanged.** |
| 2026-10-29 | **Paper 00's audit was completed against the code, and the six laws were measured.** **Two of six laws are contradicted by the implementation.** **Law III** is violated in exactly the way it was written to prevent: the design law requires that *"temporal precedes matrices are strictly computed on non-sleep events"*, and the engine's edge recorder gates the trigger but not the lookback window, so sleep output re-enters `precedes` at **201×–341×** the world's own event count (D2). **Law V** is wrong twice: the engine applies `uncertainty * (1.0 + novelty)` to questions and `uncertainty * novelty` to dreams, and the pre-registered prediction that development is EIG-orthogonal came back **REVERSED** — the lowest-EIG experiment develops **more**. **Law IV** is *mixed*: the **0.04–0.06** dream confidence baseline holds, but the law's validating path is **never exercised**, because the engine generates experiments and never executes them. **Law VI** holds (thresholds **0.3** / **0.15**). The abstract's *"unbroken lineage"* is false (D3), and *"causal predictions"* overstates the engine's own words — `memory.py` calls the temporal edges *"the organism's first approximation of causality"*. Corrected in place, and **D4** registered: the stored `generation` field agrees with the specification for **G1** but is **one lower for every primitive from G2 upward**, with no document stating the mapping. The reference list's stale titles and false *"pre-prints"* label were corrected. Added finding 33; `docs/FACTS-SHEET.md` AD5; journal §59. **Paper 00 is now accurate, and still not ready to circulate: it is not yet the recast position paper, and its literature engagement is absent.** |
| 2026-10-30 | **The publication pass on Papers 01 and 02, and a hand-transcribed table that had drifted from its artifact.** Added findings 34 and 35. Paper 02's §2 now carries inline citations and a five-source **References** section, every source read against a primary source on 2026-10-29 (one candidate citation dropped because it could not be read). Eight dependency-free SVG figures were generated for Papers 01 and 02 by the new `benchmarks/figure_papers.py`, which asserts every drawn value against the committed artifact, checks its canvas bounds and text overflow, and parses its own XML before writing. Separately, the Pilot-0 readout matrix in `docs/PILOT-0-INSTRUMENTATION-AUDIT.md` §2 was found to have drifted from `docs/acquisition_single_seed_pilot.json` in **18 of its 36 values** (largest gap **6.7×10⁻⁵**); the correction was applied, the **first repair was itself defective** (it replaced the two reference rows with duplicate cell rows), the table was then **regenerated from the artifact**, and the check is now permanent in the new `tests/test_readout_tables.py`. The same pass found a **pre-existing** defect: journal §59's Law V formula had its LaTeX escapes written in as **literal tab characters**, so the expression rendered as broken text and read as unsubstituted template placeholders — the committed record was red on `master` at `67a7565`, and `tests/test_doc_placeholders.py` is what caught it. The escapes are restored and the repair is noted in place. No measurement, verdict or conclusion changed. |
| 2026-10-30 | **The publication index was brought back in line with the manuscripts, the first world edge was given the distribution it needed, and the owner ruled on Law II.** `papers/README.md` no longer lists figures as outstanding for either paper and no longer lists Paper 02's citations as outstanding; **Paper 01's citations remain open** and now name what they are (§4.1's curriculum-sensitivity framing and §5.4's four methodological lessons). The **first world edge** — rank **31** (1-tag), **30 / 18 / 53** (2-tag), **16 / 8 / 8** (after LIMIT-4) — was reported without the distribution beside it; under the engine's own global count-ranked selection the world's 112 edges are **spread, not clustered**, with the top 20 recovering **0–1** of them and the top 320 **106–109**. The distribution is now beside the claim in `docs/GATE13-RELATION-SEPARATION.md`, journal §54, finding 27 and the changelog, and **the figure "cap 40 recovers 4–8 of 112" was corrected to 1–8** against the artifact. **Law II: the owner's ruling is to keep the discrepancy disclosed and defer the amendment** until it is settled whether the law is a design requirement or a description of V1's actual behavior; `docs/DESIGN_LAWS.md` is not edited. Added finding 36, facts sheet AD8, journal §62. No measurement changed. |
| 2026-10-30 | **The cold-start table was re-measured on the frozen engine, because the 2026-10-21 artifact no longer reproduces.** `cold_start` (no seed, engineered stream) reaches G5 at cycle 10 on `v0.6.0`, `v0.9.0` and `HEAD`, on Python 3.13.15 and 3.14.7, across repeated runs and hash seeds; the old table said `never`. `real_git_history` never reaches G5 but does reach G2 processes and G3 workflows at cycle 14, and its stimulus is 11 commit messages rather than 8. Parameters, seededness, event stream, schema and interpreter were each checked and ruled out; the 10-21→10-23 commits were never published, so the transition cannot be bisected. `docs/cold_start.json` and `docs/g5_gap_diagnostic.json` were regenerated, §8.1, decision 4 and finding 10 were corrected, and the claim that `no_dev_stopwords` is byte-identical to baseline was narrowed. No engine change. |
| 2026-10-30 | Added the **formation-vs-utilization preregistration** (`docs/FORMATION-UTILIZATION-PREREGISTRATION.md`): three paired arms (cap 20, cap 1,000, cap 1,000 + oracle admission), the retention/transfer/revision limbs, a pre-committed mapping from outcome to a V2 target, and seven audits that must fire before a score is read. **Not run; no engine change.** Corrected the Git status row, which still described 0.9.0 as the package version and `master` as level with origin. |
| 2026-10-30 | **Paper 01's citations were supplied and verified, and the publication index was brought in line with both manuscripts.** Paper 01's §4.1 and §5.4 now carry inline citations and a seven-source **References** section, every source read against a primary record on 2026-10-30, with Button et al.'s 2013 erratum read and disclosed. The second methodological lesson is stated as the project's own rule and carries no external citation by design. `papers/README.md` now lists Paper 01's citations as supplied rather than open. Added finding 37. |
| 2026-10-30 | **The formation-vs-utilization harness was built and its one-seed timing pass run — and the pass found a confound, so the campaign is not authorised.** `benchmarks/formation_utilization.py` implements the protocol committed at `8536d9a`: arms A (cap 20), B (cap 1,000) and C (cap 1,000 + generator-support admission), plus a size-matched shuffled-oracle arm; the oracle is materialized from the generator (128 permitted pairs on T2, 272 on T1) and applied before the cap. `tests/test_formation_utilization.py` adds **39 tests** (203 total), one proof-of-firing per audit plus a substrate-equivalence check and the campaign stop path. **Cost:** 8 engine runs at **72.8 s** each; the campaign projects to **4.9 h sequential** (3.6 h arms, 1.2 h audit arm, comparators under a minute). **Audits:** every applicable one passed on both tasks — T2 A1 0.0000/1.0000/1.0000, A2 14,379 permitted candidates over 131 cycles admitted exactly, A3 B precision 0.3373 inside the 0.3438 + 0.01 band, A6 shuffled transfer 0.5002 vs C 0.3670, A7 94.6 % of readout weight from Layer 1; T1 A1 0.1497/0.9222/0.9102, A7 97.1 %, with A3 and A6 marked not applicable and the reasons recorded. **The finding (D1, finding 38):** the arms do not share a temporal graph — T2 32 edges differ (374 vs 380) and 59 of 131 permitted streams differ from cycle 6; T1 21 edges differ and 107 of 160 streams differ from cycle 40. `_record_temporal_edges` reads the last three **events**, sleep rows included, so an admission filter changes Layer 1's own input; the arm table's *"all other layers and all counts are untouched"* is false and a C advantage could be self-sourced support. **Descriptive only:** C is the best Organica arm but clears the bar on only 2 of 6 task-limbs and is worse on transfer by 0.0163 nats (T2) and 0.0229 (T1); one seed, no verdict. Two audit-scope corrections are disclosed: A2 is the committed self-stream audit (the stricter C-vs-B comparison became D1, not A2), and A3's band is applied on T2 only because that is where it was measured. Added §8.20, finding 38, the two command rows and the file-map entry; artifacts `docs/formation_utilization_timing.json` / `.md`. |
| 2026-10-30 | **Amendment 1 to the formation-vs-utilization protocol: the admission arms read arm B's temporal graph, and audit A8 gates it.** The timing pass's D1 confound — the engine's lookback window is the last three rows of `events`, sleep rows included, so the oracle filter changed Layer 1's own input — is closed by fixing the temporal basis at arm B's: B is run first and its `_load_temporal()` graph is recorded at the start of each sleep cycle; C and S read it instead of their own; A and B are unchanged and `organica/` is untouched. **A8** checks, every cycle, the graph actually read, the eligible pair stream and the evidence on shared pairs, and that the two arms' logs cover the same cycles (the run asserts exact consumption); it is a gate with proof-of-firing and load-bearing tests. The amended timing pass (eight runs, **72.2 s** each, **4.8 h** sequential) passes every applicable audit on both tasks: T2 A8 **131** cycles and **75,488** pair checks, T1 **160** and **80,200**; the engine's own `precedes` tables still differ by **28** and **15** edges but Layer 1 no longer reads them. B agrees with the pre-amendment pass at four decimals (full-precision drift is at most **1.4 × 10⁻⁵**, including the untouched A arm, so reproducibility is about **10⁻⁵**, not bit-identity). C's new cells are descriptive only: readout coverage **1.0000** / **0.9222**, transfer **0.3661** / **0.2346**, clearing the bar on 2 of 6 task-limbs. **The claim is narrowed:** a C result is admission filtering at fixed temporal evidence, not "the engine with this filter installed", and it says nothing about self-sourcing. The pre-amendment artifact is preserved; its C and S cells are not a result of the amended design. No engine change; no campaign run. |
| 2026-10-30 | **The formation-vs-utilization campaign ran to completion, and the pre-committed verdict is "utilization fails with correct structure" on both tasks — C loses transfer by 0.0262 nats (T1) and 0.0227 (T2), B loses it too, so V2's target is the use path and the summary claim is not supported.** 30 seeds × 2 tasks, 60/60 units `campaign_ready`, all eight audits pass or are N/A (A3/A6 N/A on T1), 12.72 worker-hours. C wins revision on T1 (+0.1002) and ties it on T2 (+0.0007), and closes 65.2 % / 79.9 % of A's transfer gap — the label means *does not clear the bar*, not *no use*. The T2 bar is the cell-level latent-state counter, **granted the latent cell structure**; the protocol's "data-only" wording is corrected, and a post-hoc check shows C still loses to Replay (0.0208) and the bigram (0.0187) on T2. Added `docs/formation_utilization_results.md` (generated from the artifact), its drift test, §8.21, finding 39, and journal §65; corrected the artifact's `command` provenance. **No V2 build is authorised.** |
| 2026-10-30 | **The V2 record was corrected and the use-path diagnostic pre-registered.** The campaign's ceiling condition is now recorded as **observed** (V2 brief §9.8; gate 5's specific-failure condition met, mechanism condition not); the old §11 "NOT OBSERVED" entry is preserved and marked **SUPERSEDED**, not erased. The diagnostic freezes D0 reproduction (1e-4) as a validity gate, estimates the room (D5 − D0) before naming a component, and pre-commits five outcomes including **evidence-limited** and **audit required**. D2's weights are constants (1.0/0.5), not fitted. Added `docs/USE-PATH-DIAGNOSTIC-PREREGISTRATION.md`, `benchmarks/use_path_diagnostic.py`, `tests/test_use_path_diagnostic.py`; added action 15 and §8.22. **No V2 build is authorised.** |
| 2026-10-30 | **The use-path diagnostic ran and returned AUDIT REQUIRED: its D0 validity gate failed on 18 of 180 seed-limbs, so no room, no variant effect and no component are reported.** 162/180 seed-limbs reproduced the campaign's arm-C scores within 1e-4; the largest difference was **0.004386** (T1 seed `20261128`, revision). All other controls passed. The likely cause is `MemoryService.recent()` ordering by `time DESC` with no `rowid` tiebreak, against `structure_edges` keeping the first snapshot per candidate id; the campaign artifact did not record the tie order, so this is a **code-path hypothesis, not an established cause**. The mechanism condition of gate 5 remains unmet; **no V2 brief follows**. Added the result document and its artifact, §8.22's result, action 16 (the reproduction audit), and the generated result's gate-first section. **No engine change; no V2 build.** |
| 2026-10-30 | **Recorded the campaign-validity vs diagnostic-reconstructability status, and mechanically reproduced the per-type observation.** The new journal §68 states that the campaign's conclusion (V2 targets the use path) stands, localization is blocked by D0, and the room question is unreached. The structure check (`--structure-check`) reproduces the cross-tab in §68 from `docs/use_path_diagnostic_structure.json`; every quoted count is checked against that artifact by `tests/test_use_path_diagnostic.py`. The observation is a post-hoc audit instrument, not a finding and not a change to D0. Action 16 is refined to the three-layer audit. **No protocol change; no engine change.** |
| 2026-10-30 | **The reproduction audit ran and the tie-order hypothesis is not supported.** 48 runs (8 failing seeds × 2 configurations × 3 repeats). Both configurations stable 8/8 and identical 8/8; the `rowid` tiebreak changed neither the per-type table nor any score. Neither reproduced the campaign's per-type table (0/8 and 0/8), so score reproduction was not entered. The audit reproduces the diagnostic exactly 8/8, so it is a re-run of the D0 object. The divergence is upstream of `recent()`; the audit names the candidates (a campaign-time harness revision or the unrecorded environment) and does not choose between them. D0 remains fired; the diagnostic remains AUDIT REQUIRED; no room, mechanism or V2 brief follows. Added `benchmarks/use_path_audit.py`, `docs/use_path_audit.json`, `docs/USE-PATH-AUDIT.md`, `tests/test_use_path_audit.py`, journal §69, and the manual corrections. **No engine change; no protocol change.** |
| 2026-10-31 | **The Gate 13 precision ceiling was corrected from 0.3443 to 0.3438, in fourteen documents, in four code files, and in the campaign artifact's A3 blocks.** The artifact's maximum is 0.3438 and the string 0.3443 occurs in no Gate 13 artifact. The correction changed no audit verdict: the highest arm-B Layer-1 precision on T2 is 0.3394, below both band edges. The result artifacts were corrected **by field path** so that four measured `0.3343` precisions and six longer values beginning `0.3443`/`0.3543` were not corrupted; the originals are preserved as `docs/formation_utilization_pre_correction.json` and `docs/formation_utilization_timing_pre_correction.json` with a `correction_note`, and every measurement was compared before and after. `docs/formation_utilization_timing_pre_amendment.json` and its rendered document were left as the historical record they are. **Also corrected:** Paper 01's three stale Phase L adjacent-difference intervals. Added finding 40, facts sheet AD10, journal §70, AGENTS rule 29; `docs/formation_utilization_results.md` and `docs/formation_utilization_timing.md` corrected to match their artifacts. |
| 2026-10-31 | **The candidate-membership audit ran and the eight failing seeds are a hash-order artifact.** The campaign artifact carries no candidate ID, so the campaign side was regenerated by re-running the harness under each `PYTHONHASHSEED` and keeping the run whose per-type table equals the campaign's; that reproduces the campaign exactly on **8 of 8** failing seeds. The engine is byte-identical to the state the campaign ran against, so the code is excluded and the environment is responsible. Per-seed membership, the missing and added candidate IDs, and the first differing cycle are in `docs/candidate_membership_audit.json` and `docs/CANDIDATE-MEMBERSHIP-AUDIT.md`. One cached run from an earlier sweep was found to carry the campaign's table rather than a measurement and was recomputed; the rebuilt artifact supersedes the earlier one. Added `benchmarks/candidate_membership_audit.py`, finding 41, facts sheet AD11, journal §71, and the CHANGELOG entry. |
| 2026-10-31 | **The divergence-cycle capture ran: the candidate pool at the cycle where the populations part company is now named, and it shows the divergence is mostly a difference in order.** **(Corrected 2026-11-01: the capture read the cycle *before* the divergence and labelled it with the divergence cycle's number, so the pools below are one cycle early; see the 2026-11-01 row for the re-measurement at the divergence cycle itself.)** The membership audit established where the campaign's candidate population and the current reconstruction's part company — sleep cycles 2 to 11, depending on the seed — but the 4,000-row sleep window it captured covers only the arm's snapshot point, so it could not say what was in the pool at the divergence. The new instrument captures the window one cycle before the divergence (see the correction in this row), and the capture is addressed by the engine's own cycle markers rather than by assumption: the newest `sleep:meta` marker in the i-th window must carry cycle *i*, and an unwitnessed window is refused. Across the 16 arm-pairs the two sides hold the same set of candidate IDs in **11** and the same order in only **3**; on **3** seeds the pool is identical in set and order altogether and the admitted stream still differs. The capture's own parts were written twice by two independent processes at the same hash seeds and compared field by field: 16 of 16 identical. Added `benchmarks/divergence_cycle_capture.py`, `docs/divergence_cycle_capture.json`, `docs/DIVERGENCE-CYCLE-CAPTURE.md`, `tests/test_divergence_cycle_capture.py`, finding 42, facts sheet AD12, journal §72. |
| 2026-10-31 | **The objective is now written down, a release statement was corrected, and the next instrument is planned with its hypothesis pre-registered.** The README carries a **What this project is for** section above the architecture: **explainable AI, in three layers — decisions, knowledge, cognition** — with the architecture named as **the bet, not the claim**, and an explicit statement that the repository makes no general-intelligence claim. The README and `CITATION.cff` also now say which kind of release they mean: **0.10.0 is the latest cut version** (dated, tagged, pushed) while **v0.9.0 is the latest published release**, because v0.10.0 has no GitHub release page — `gh release list` shows releases only for v0.6.0 to v0.9.0. `CITATION.cff` loses the `artificial general intelligence` keyword, which asserted a claim this repository does not make. The next instrument's brief (`docs/DIVERGENCE-MECHANISM-BRIEF.md`) plans the observation of the candidate construction where the two admitted streams first differ — which type, which builder, and whether the difference is in the order, in the membership or in a candidate's content — with the hypothesis, two forms of it, three predictions, three falsification criteria and four controls committed in advance; journal §73 carries the pre-registration. **No engine change; no D0 re-scoring; no V2; no acquisition cells.** |
| 2026-10-31 | **The Zenodo deposit package is decided, bundled and verified — and not deposited.** On the owner's direction (*"do not deposit yet; use your best judgement on the rest"*) the remaining decisions are made: the papers carry **CC-BY-4.0** (Zenodo's default for a textual work; the engine stays Apache-2.0), the route is a **manual deposit** through the web form, and the **papers go first** so their DOIs exist before the software record links to them. Two states were verified live: the repository has **zero webhooks**, so Zenodo's GitHub app is **not authorised**, and there is **no v0.10.0 GitHub release** — `gh release list` shows releases only for v0.6.0 to v0.9.0. No release is cut and no app is stood up. `benchmarks/deposit_bundle.py` builds the three bundles with their checksums and manifests, and checks the deposit's file list against the manuscripts: **36 artifacts cited, 36 present** in the `v0.10.0` tree. Added `benchmarks/deposit_bundle.py`, `tests/test_deposit_bundle.py`, and the decisions in `docs/ZENODO-DEPOSIT.md`. **Nothing is deposited, tagged or published.** |
| 2026-11-01 | **The release guard was comparing a tag object to a commit, and it is repaired.** `test_a_released_version_is_checkable` asked the remote for a tag with `git ls-remote --tags origin v0.10.0`, and against an **annotated** tag that query returns **one** line — the tag object — and omits the peeled `^{}` line, so the shallow-clone path compared `843247b` (the tag object) against master's commit. The query now uses a `*` pattern so git emits both lines, and `_parse_tag_refs` prefers the peeled commit, matching names exactly so a prefix neighbour (`v0.10.01`) cannot be admitted: `_remote_ref("v0.10.0")` now returns `f3a42a7`, the commit, not `843247b`, the tag object. Five tests pin it, including a proof-of-firing that the comparison still fails when the tag is behind master. `.venv/` is now ignored, so `git add -A` cannot stage a virtualenv. **Separately verified at this commit:** `tests/test_divergence_cycle_capture.py` parses and its **23** tests pass, and the suite's **402** collected tests are **393** passing plus **9** that need the `papers/build/` PDFs — that directory is gitignored, so those nine fail by `RuntimeError` until `benchmarks/render_papers.py` has been run. |
| 2026-11-01 | **The construction-order experiment ran (Arm A and Arm B) and its own control stopped it.** The pre-registered instrument was built (`benchmarks/divergence_mechanism.py`), run on the eight failing seeds and the control seed at their campaign and baseline hash seeds — 36 parts, each with a sha256 — and written up in `docs/DIVERGENCE-MECHANISM-RESULTS.md` and journal §74. Arm A located the first order-sensitive builder as `_score_tags` at cycle 1 on every seed *including the control*, which is a property of set iteration rather than the divergence site; the admitted streams part company one cycle after the audit's divergence cycle on 8 of 8 seeds. Arm B did not make the tables invariant (P3 not met, F1 fired) and changed the control at a fixed hash seed (F2 fired), so by the pre-registration it is inadmissible and H2 remains untested. **No engine file changed.** |
| 2026-11-01 | **Both divergence instruments read the audit's cycle base one cycle early, and the correction removes a timing claim instead of adding one.** The membership audit stores `first_cycle = index` over a **zero-based** digest list; `benchmarks/divergence_cycle_capture.py` and `benchmarks/divergence_mechanism.py` both read that index as a one-based cycle. The capture therefore captured the cycle **before** the divergence and labelled it with the divergence cycle's number, and the mechanism instrument's `admitted_same_at_divergence` read `admitted[cycle - 1]` — identical by the audit's own definition, so a field that could not be false. Corrected: both instruments read `index + 1`; that field is deleted and replaced by `audit_cycle_reproduced`; the capture is re-measured at the divergence cycle and the cycle before it (`OBSERVER_VERSION` 3, parts regenerated) and now guards a refused window as **not measured** rather than as an empty pool, which would have compared equal and reported "identical". Mechanism re-analysis: **0 new runs, 36 cached parts**. Manual finding 44 is narrowed to "the earliest hash-sensitive operation **observed by the instrument**" — the observer wraps seven builder call sites, not query order or dict construction upstream of them. **One status did change when the re-measurement landed:** at the divergence cycle the two sides hold the same set in **0 of 16** arm-pairs, so §72's order-only reading and §73's premise that the difference arose *inside* the cycle are withdrawn. C1 remains supported within scope, H2 remains untested, Arm B remains inadmissible, and the engine remains frozen at `v0.9.0` with no delay between construction order and admission. Added `tests/test_divergence_instrument_bases.py` (7 tests, each written to fail on the old base). |
| 2026-11-01 | **The corrected capture was re-run and it removes a phenomenon rather than relabelling one: at the divergence cycle the two sides share no candidate set.** The re-run cost **16 runs, 0 cached** (`OBSERVER_VERSION` 3) and reports the **same set** in **0 of 16** arm-pairs and the **same order** in **0 of 16**. The 2026-10-31 figures (11 of 16 the same set; 3 seeds identical in set *and* order while the admitted stream differed) are measurements at the **preceding** cycle, so finding 42's order-only conclusion, finding 43's premise, journal §72's reading, facts-sheet AD12 and the README paragraph are corrected here. The capture renderer was repaired with them: its branch for zero identical pools printed an empty seed list while still attributing the divergence to identical pools, its narrow-claim sentence read "on 0 seeds the pool is identical and the divergence is still there", and its provenance line printed the parent process's counters as the work done. **What remains:** the pools diverge, and *when and by what step they first do* is the open question — not why identical pools admit differently. Engine untouched. |
| 2026-11-01 | **The onset question was pre-registered before any run, and no measurement has been made.** Journal §75 and `docs/ONSET-INSTRUMENT-BRIEF.md` fix the question (the earliest cycle at which the two candidate pools differ, and what entered or left there), three predictions, four falsification criteria and four controls. The bracket is computed from `docs/divergence_cycle_capture.json`: **11** arm-pairs bracketed at `(k−1, k]`, **5** already divergent at *k−1*, **0** still identical at *k*. Nothing is built and nothing is run; the existing capture's `capture_cycles()` still returns only the fixed pair, which is the work this plan authorises. Engine untouched. |
| 2026-11-01 | **The onset pre-registration was amended before any run, because its first prediction could not fail.** P1 — that the 11 bracketed arm-pairs reach onset at exactly *k* — is arithmetic once the bracket holds (pools identical at *k−1*, different at *k*, integer cycles), so it was reclassified as a consistency check folded into F1 and retained in the record as written. The predictions are now **P2** and **P3**. This is the same defect the mechanism instrument's `admitted_same_at_divergence` had, caught this time before the run rather than after. Nothing is built or run. |
| 2026-11-01 | **The onset experiment ran and its control was void.** 18 runs, 0 cached; F1 reproduced cycles *k* and *k−1* on 16 of 16 arm-pairs; four of the five search arm-pairs reached onset strictly before *k−1* (cycle 3 for T1/20261125 against *k* = 12, cycle 4 for T2/20261120 against *k* = 6) and the fifth at *k−1* itself; P3 met, with every onset at cycles 3–6. No candidate left any pool at its onset — all 16 divergences are insertions. **The control seed's two hash seeds are both 0**, so C1 compared a run with itself and could not fire; F2 is unadjudicated and a re-run of the control at two distinct seeds is the outstanding check. Added finding 46, facts sheet AD14, journal §76, `benchmarks/divergence_onset.py`, its tests and its report. Engine untouched. |
| 2026-11-01 | **The distinct-seed control ran and F2 fired: the onset result is inadmissible.** The control seed T1/20261101 was re-run at hash seeds **0 and 1** (2 runs, 0 cached) because the audit's own pair is seed 0 twice and could not fail. Its pools **differ**: 3 of 24 measured cycles, arm B, cycles 10–12. By the pre-registration F2 fires and the instrument is inadmissible — the onsets (cycles 3–6) and the insertion observation stand as measured facts about pools under two hash seeds, but neither may be attributed to the D0 divergence. The residual pattern difference — control at 10–12 on one arm versus failing seeds at 3–6 on both — is recorded as a hypothesis for a new pre-registration and was not used to rescue the result. Added journal §77; finding 46 and facts sheet AD14 amended. Engine untouched. |
| 2026-11-01 | **Finding 46's headline now leads with the verdict.** It read *“…and the control that should have checked it was void”*, which went stale the moment the control was re-run: it exists, it was run at two distinct hash seeds, and it fired. The headline is what a reader repeats, so it now states the whole result in one breath — insertion is measured, the attribution is not — and the body below it is unchanged. |
| 2026-11-01 | **Finding 44 reported a control that had already failed.** C1 as pre-registered required the control seed's assembled lists to be identical at every hash seed; P2 is not met, so C1 failed. The finding kept the label and substituted a different quantity (the admitted stream, which does hold) and called that the sharpest positive result. The observation is retained as a post-hoc statement about one seed at hash seeds 0 and 2, and the control is corrected to failed here, in `docs/DIVERGENCE-MECHANISM-RESULTS.md` §6 and in journal §74. No measurement changed and no run was made. |
| 2026-11-01 | **Freeze point called on the divergence line, and the record now says so.** Four corrections in this line each removed a claim instead of confirming one: identical pools at divergence, the one-cycle lag, the divergence-specific onset reading (F2), and C1 as a passed control (P2 not met). The owner called the freeze because the next question — which upstream write admits candidates at cycles 3–6 — requires a new observer, not another reinterpretation. Journal §78 records what stands, at its scope, and what the record no longer says; `_score_tags` survives as the earliest hash-sensitive builder the current instrumentation can see, with whether it is causal or merely earliest-visible left open. No run was made. |
| 2026-11-01 | **The next instrument's brief is committed before any run: the store-time observer.** It asks which write admits the candidate one pool holds and the other does not, and fixes a four-way result space in advance — upstream ingest write, construction write, no explaining write *only* if the observed and reconciled write counts agree, and **indeterminate** otherwise. The known-positive control is the control seed's own cycles 10–12, so an observer that cannot explain a difference the record already contains is inadmissible rather than merely disappointing. Nothing is built and no run was made. |
| 2026-11-01 | **The store-time observer's core is built, and its neutrality control passes.** `benchmarks/store_time_observer.py` wraps the substrate's admitting call in-process (no engine file touched), attributes every write to a cycle **off the engine's own `sleep:meta` marker** rather than a read index or a counter offset, and reconciles observed calls against accepted rows per cycle. The self-test reports neutrality **identical** on the admitted stream and the temporal reads, the comparator proved to fire on an injected difference, **349,502 writes with net delta equal to accepted rows**, and **zero unattributed writes** across cycles 1–160. The verdict pass and the known-positive control are **not built**; no divergence verdict has been read. `tests/test_store_time_observer.py` covers the reconciliation arithmetic cheaply. |
| 2026-11-01 | **The observer's per-call trace is kept, not discarded after summarising.** `--trace` writes every admitting call of a run to `docs/store_time_observer_trace.jsonl.gz`: **349,502 calls, 48,672 distinct digests, 1.12 MB** gzipped, five fields per row. `load_trace()` resolves the digest table. Kept because a run's database is disposable and a summary cannot answer a question nobody had yet. |
| 2026-11-01 | **The known-positive control passes, so the observer is admissible.** C1 / F4 ran the control seed at hash seeds 0 and 1 (2 runs, 93.3 s) and captured cycles 10–12 with witnessed markers on both sides. Every one of the **12** candidate differences was traced to a write: the candidate is offered on one side only, at the **construction** stage — outcome (B) in the brief's result space. This validates the observer on a difference the record already contains; it says nothing about D0, the verdict pass is not built, and no divergence verdict has been read. The first attempt returned `not_measured` because the window index was incremented before the read — caught by the control, not by a result. |
| 2026-11-01 | **F4 is gated on reconciliation, re-run, and frozen as `docs/F4-RESULTS.md`.** The first decision rested on attribution alone; a cycle that does not reconcile cannot distinguish *no write explains it* from *the observer missed the write*, so `f4_decision()` now requires every affected cycle to reconcile **and** at least one difference to be attributed, in that order. Under the stricter rule the control still passes on all three cycles with all twelve differences attributed, outcome (B) **as the label read at the time**. |
| 2026-11-01 | **Correction: the control's outcome is (B) *unlocalized*, not (B).** The brief's (B) means the `_score_tags` write was identified; the observer's stage split only separates ingest from construction, so it shows the candidate is written by the cycle's own construction and does not isolate the scoring step. That suffices for the control and not for a (B) verdict on a failing seed; reaching inside construction is a build change to be pre-registered, not a reading of this result. F4's PASS is unchanged. See `docs/F4-RESULTS.md` §7. |
| 2026-11-01 | **Bucket (B) named a write that does not exist, and is restated before use.** `_score_tags` makes no store call — it builds and sorts `_TagScore` records — so no instrument could report "the `_score_tags` write". Brief §9 restates (B) as a write from one of the two builders that consume this cycle's tag scores, and pre-registers the split: phase (pool write vs survivor re-store, read from the call stack) by type (the engine's own source stamp). |
| 2026-11-01 | **F5 passes: the observer names the builder, and on the control seed it is not tag-scored.** Neutrality was re-proved with the frame walk installed (349,502 accepted calls, 0 unreconciled, 136.5 s), 17 distinct labels were observed, and all 12 attributed candidates carry `pool:dream` — the pre-registered prediction, so (B-restated) is not reached on the control seed. F4 still passes. This says nothing about D0: one seed, one hash-seed pair, one differing type. The verdict pass is still not built. |
| 2026-11-01 | **The verdict pass ran: the write behind the divergence is construction, and it is not tag-scored.** Five cells over T1/20261125, T2/20261120 and T2/20261121 at the hash-seed pairs the membership audit recorded. Every resolving cell attributed **all** its differences (27/27, 27/27, 6/6) to construction writers — predictions, anomalies, loops, hypotheses, dreams, investigations, experiments, questions, theories — and **no** cell attributed one to a tag-scored builder, so (B-restated) is not reached on these seeds. T2/20261120 resolved only partially (8 of 14) and is **`indeterminate`**, and it is the first cell to show a survivor re-store (`restore:loop_candidate`) offered on one side only. A first pass at hash seeds 0/1 found no difference at all; that is kept on the record as an input error about which pair diverges. H2 is still untested and D0 is not re-scored. See `docs/STORE-TIME-OBSERVER-VERDICTS-PAIRS.md` and journal §83. |
| 2026-11-01 | **The six unattributed differences were written one cycle before the search window opened** (two cycles before the divergence), each written exactly once — corrected same day against the lineage artifact, which also shows one attributed candidate, not two, first appearing at the window's outer edge, and four, not six, re-stored every cycle. A post-hoc lineage check (`--lineage`) over the whole run shows all six were written once, at cycle 4, on the side whose pool holds them and never on the other side — while the pre-registered window is the divergence cycle and the one before. The cell stays `indeterminate`; what changed is the diagnosis: not an observer that could not see the write, but a window narrower than the lead time. A wide-window rule would need its own pre-registration and would have to apply to every cell. See journal §84. |
| 2026-11-01 | **Arm B-prime passes its first gate — F2 does not fire, contrary to my own advance prediction.** Arm A re-ran entirely from cache (0 runs, 18 cached): `_score_tags` is still the earliest order-sensitive builder on every seed including the control, which is a property of construction, not of the divergence. Arm B-prime — canonicalising that site, pre-registered in brief §11 — was then gated on F2, the control's table at a fixed hash seed: **0 differences in 168 comparisons**, so the gate passes. Section 11 had predicted F2 would fire; it did not, and the wrong prediction is kept on the record. This licenses the next gates, not any claim about H2: one control seed, one hash seed, and an intervention that was a no-op there. The T2/20261120 cell stays indeterminate and the window is not widened. **C2 and C3 also pass**: a quiet run and an observing run agree on both arms' admitted streams, and a repeat run at the same hash seed is identical, with no part refused. All three pre-gates clear, so gate 4 — the eight failing seeds at their recorded pairs under the intervention — is the next run. **Corrected the same day: this was measured with `canonical_score` unimplemented — the mode behaved as `observe` — so the number is void; see `docs/divergence_arm_b_prime_AUDIT.md` and journal §87.** |
| 2026-11-01 | **Arm B-prime across the eight seeds: F1 fires.** 0 of 8 seeds record identical tables across their own hash-seed pairs under the intervention, over cycles 1-12 and both arms. The order channel as canonicalised does not remove the variation, so H2 is refuted in its strong form. Scope: sufficiency under intervention on these seeds; the canonical order is not thereby the correct one, D0 is not re-scored, and Organica 1 stays frozen. See journal §86.  **But F1 is provisional**: every seed's first difference is at cycle 1 in `score_tags` with identical membership — Arm A's signature, not a total order's — and one seed's two sides differ by ordering `fern`/`cedar`, which under `(-frequency, tag)` requires the *frequencies* to differ. So the next check is one comparison of the two sides' frequency values, and until it is run F1 is fired by the code and not read as closing the order channel. **Corrected the same day: this was measured with `canonical_score` unimplemented — the mode behaved as `observe` — so the number is void; see `docs/divergence_arm_b_prime_AUDIT.md` and journal §87.** |

| 2026-11-01 | **Arm B-prime: the mode was a label, and the arm is now inadmissible by its own control.** An implementation-to-artifact audit found `canonical_score` was an argparse choice with no code behind it — no `CANONICAL_MODES`, no canonical graph, no score total order — so it ran as `observe` and every earlier B-prime number was void. With the intervention actually implemented and telemetry proving it (`total_order_applied`, `adjacent_ties`), F2 fires 125 of 168 on the control, C2 and C3 pass, and gate 4 returns 8 of 8 seeds invariant. §11 pre-registered that if F2 fires no conclusion may be drawn from the arm, and F2 fired: **the decision is yours — restate F2 in membership terms, or abandon Arm B-prime.** `T2/20261120` stays `indeterminate`, D0 unscored, window unwidened. See `docs/divergence_arm_b_prime_AUDIT.md`, journal §87. |

| 2026-11-01 | **Arm B-prime closed by decision, not resolved.** F2 fires on the control (125 of 168 comparisons), so §11's pre-registered stop rule bars any conclusion from the arm: it is closed, F2 is *not* restated, and no further runs happen. The 8-of-8 hash-invariant result is kept as a **diagnostic observation** — hash-invariant is not correct, and it is neither evidence for nor against H2. Returning to hash order later requires a new protocol measuring invariance *and* membership effects on fresh seeds. See `docs/divergence_arm_b_prime_AUDIT.md` §7, journal §88. |
| 2026-11-01 | **A protocol draft for reusable knowledge is written, and nothing is run.** `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` targets the question the acquisition study never reached, and stops at an owner decision: authorise a formally named `V1.1-cap` diagnostic variant, or leave V1 frozen and record the capacity limit as a finding. It fixes a formation gate that can fail, forbids the "data-only" label for a comparator granted the latent cell map, and treats capacity and ordering changes as named variants only. No cell has run and no harness was extended. Journal §89. |

| 2026-11-01 | **Reusable knowledge: Option A authorised, and the draft's three review points closed (Revision 1).** The precision claim was too wide and is now two quantities with their denominators — the engine's own top-k over 36 cells (max 0.3438, best cell 55 of 160 retained) and a 9-of-20 filtered set at coverage 0.0804 that was below its own 0.50 gate (precision 0.4500). Replay, bigram and decayed bigram are now the primary same-experience comparators; the latent-map cell counter is demoted to a privileged reference that no verdict may be computed against. Transfer now requires a declared 25 % of the law's edges withheld from the formation stream, with a 20-transition denominator floor, and a limb that cannot do that is called held-out generalization instead. Seeds fixed: calibration `20261201–20261205`, confirmatory `20261206–20261225` (n = 20), paired percentile bootstrap 10,000 replicates at 98.33 %. Promotion to a preregistration is still an owner step and nothing has run. |

| 2026-11-01 | **The transfer manipulation was checked generator-only, and the draft's rule did not survive it.** Paths corrected to `benchmarks/acquisition_compositional.py` (four cells, **eight** directed cell transitions, 128 tag pairs) rather than the group world or `organica/ground_truth_worlds.py`; the **112** is the group world's tag-level count and is no longer used for this world. The existing `trainable` mask is rejected because it generates the withheld event, advances the hidden state and only skips storage, creating artificial adjacency. Every-fourth withholding **fails** (not strongly connected; two permitted transitions at 0–1 instances in 720 events); all 28 two-transition subsets were evaluated against six criteria fixed before the enumeration, **16 are feasible**, and the adopted rule is the first feasible one — `(0,0)` flip_p with `(0,1)` flip_q — with every check passing and 130/66 withheld instances against a floor of 20. No engine, no cell, no harness. Journal §90. |

| 2026-11-01 | **Two feasibility defects corrected, and the reusable-knowledge protocol promoted to a preregistration.** (1) Seed `20261206` had been used to select the withholding rule while being designated confirmatory, so it is now **burned/diagnostic** and the confirmatory set is `20261207–20261226`, keeping n = 20. (2) The check used 90 formation cycles and a 100-cycle window instead of the module's own schedule — warmup + acquisition = 110 cycles of exposure, transfer on cycles 150–199 (50 cycles) — so formation now conditions both phases and the 20-instance floor is verified in the real generated transfer window. Under the corrected conditions, 16 of 28 subsets remain feasible and the adopted pair (`(0,0)` flip_p with `(0,1)` flip_q) is unchanged, with at least 30 instances in the transfer window on every calibration seed. Protocol is now **Revision 2, committed**; next steps are the harness build and the calibration pass, in that order, and no cell has run. Journal §91. |

| 2026-11-01 | **Amendment 1 to the reusable-knowledge preregistration: Gate F's denominator is 96 and the ceiling is the latent-rule holder.** Counting the law's 128 tag-pair relations would cap coverage at 0.75 because 32 are withheld by the transfer manipulation, so Gate F now counts only the 96 relations available during formation, with the withheld 32 scored solely by the transfer limb. The ceiling is the full latent-rule holder — 0.325 for a flip_p successor, 0.175 for flip_q, closed form — and the oracle-admitted arm is demoted to a mechanism arm that may never be reported as the ceiling. Numbers are generated into `docs/reusable_knowledge_gate_definitions.json`; no cell has run. Journal §92. |
| 2026-11-01 | **Amendment 2 to the reusable-knowledge preregistration: the variant is fixed at 1,000 predictions, calibration is gated on all five calibration seeds for V1.1 only, and the oracle-admitted arm is deferred.** The capacity is fixed at 1,000 because formation has been demonstrated there (asserted coverage 98.2–100 %) and not at 20 (0.0–2.7 %), so it is the value with a precedent behind Gate F's operating point, and fixing it before the build means it cannot be re-chosen after a result — a different capacity is a different variant. Calibration is a go/no-go at n = 5, where one seed is a fifth of the evidence, so a single failure stops the study before any confirmatory seed is touched; confirmatory keeps the 15-of-20 rate already fixed in §2, and the asymmetry is stated in §15 so neither rule can be swapped afterwards. The oracle-admitted arm is excluded from both passes and no verdict may cite it: its candidate-level rule was never specified to a reproducible standard, and an arm whose mechanism is a label is how the B-prime generation was lost (§87). The existing generator's one-transition mask (1 of 8) is explicitly not reusable, so the conditioned sampler is new work; the five build items are enumerated in §10 and the parameters are in `docs/reusable_knowledge_variant.json`. Guards 35 passed, `git diff -- organica/` empty. No cell has run. Journal §93. |
| 2026-11-01 | **The reusable-knowledge harness is built and the Gate F calibration passes on all five calibration seeds.** `benchmarks/reusable_knowledge.py` implements the five items §10 enumerated, with the conditioned sampler replacing the retired one-transition mask: the two declared cell transitions are never generated during warmup or acquisition, so no event is skipped and no adjacency is manufactured. Gate F counts asserted relations in the available set over 96 and passed on `20261201–20261205` (minimum coverage 0.9792; four seeds 0.9896–1.0000), which is the §15.2 go/no-go and clears the study to proceed. The harness audit — endpoint separates the law from a one-transition learner, Gate F fires on a degraded readout, no withheld transition appears in formation, no limb has an empty denominator — passes on every seed. On the withheld-only transfer limb Organica is below the best primary comparator on all five seeds (worst margin +0.1752 nats) and above the ceiling on all five (-0.2294–-0.2231 nats), so the margin is partial: **this is a calibration characterization at n = 5, not a transfer result**. No confirmatory seed has been run. `organica/` untouched; journal §94. |
| 2026-11-01 | **The calibration now names its variant, the attribution share is a pre-registered criterion, and calibration requires a reproducible hash seed.** Three defects were closed before any confirmatory run. (1) `--cap` could override the capacity while every artifact was labelled `V1.1-cap(1000)`, and the confirmatory guard read only the pass flag; the label is now derived from the cap, calibration refuses any capacity but 1,000, and the guard checks cap, label, seed set, Gate F, audit and attribution. (2) The readout aggregates all structure types, so the margin had no attribution rule: §17 adds the attribution share — Layer-1 edge weight over total, minimum 0.50, the formation-utilization A7 operating point, adopted before any confirmatory seed — and it cleared on all five calibration seeds at 0.9848–0.9866. Its first control could not fire (a tenth of Layer-1 is still 0.88 of the weight) and was replaced by the no-Layer-1 counterfactual, now audit E5. (3) Re-running calibration moved seed 20261204 from 0.6006 to 0.6025: the engine's candidate ordering is hash-sensitive, so calibration now requires a fixed `PYTHONHASHSEED` and records it. **No confirmatory seed has been run.** |
| 2026-11-01 | **The revision limb is implemented and the trace-derived provenance diagnostic stops the study.** §5's third limb exists: the revision-learning window is fed under the rotated law with the same two transitions withheld, the readout is frozen again, and the revision-test window is scored — `revision` over the whole window and `revision_held_out` (82–110 pairs per seed) as the co-primary. A store-time observer that repeats the engine's own lookback query labels every support transition world- or self-sourced; **0.4092–0.4155 of the asserted readout's support is self-sourced**, against a 0.25 maximum declared before it was measured, so `authorises_confirmatory` is false and no confirmatory seed may run. Gate F still passes 5 of 5 and the audit passes every check; the stop is the diagnostic, and no threshold was relaxed. Also fixed: the formation readout's base rate had been smoothed over events it was later scored on. Journal §96. |
| 2026-11-01 | **The provenance measure was reconciled with the per-claim rule, and the rule still stops the study.** The run-level share §96 reported was a population average counted by support reference; the audit-trace specification writes its disqualifier per claim and reads **distinct** evidence. The observer now keeps distinct prior event ids per edge, and every Layer-1 prediction and hypothesis is judged individually against the frozen 17.9 % reference: 264–592 of 604–1277 measurable claims fail per seed, with a maximum share of 1.0000. The run-level diagnostic is 0.4209–0.4287 on distinct evidence. Gate F 5 of 5 and the audit 8 of 8 (including the new per-claim check) still pass, so the block is the criterion, not the instrument; `authorises_confirmatory` stays false and no confirmatory seed has run. Journal §97. |
| 2026-11-01 | **The per-claim measure was corrected on three counts, and the stop still holds.** Distinct support is now identified by the transition — (prior event, target event), as the audit-trace specification defines it — not by the source event, so the comparison to the frozen 17.9 % reference is on the reference's own unit: 12,076–12,157 distinct transitions per seed, run-level share 0.4092–0.4155. The all-self control now runs the same evaluator as the real claims (1,313 claims on seed 20261201, every one failing, maximum share 1.0) and `E8` checks that arithmetic instead of a flag. The rule governs every asserted prediction and hypothesis, because a scored pair's prediction comes from the asserted structure through smoothing; the withheld relations' own claims are reported separately (0–20 claims, 0–20 measurable, none at all on 2 of 5 seeds) and cannot be the criterion. Unmeasurable claims are excluded and reported under a declared 50% measurable floor, which bounds exclusion rather than forbidding a pass — the criterion records the share of claims a pass would cover; the measured fraction is 0.9711–0.9765. The corrected result is 254–576 of 604–1277 measurable claims failing per seed (42.1–52.1 %), so `authorises_confirmatory` stays false, the confirmatory set stays closed, and the audit passes 8 of 8 checks including the rebuilt `E8`. The §19 counts are withdrawn. Journal §98. |
| 2026-11-02 | **The per-claim observer was reading its target event off a tie-unordered window; the counts survive the repair.** The support observer took each transition's target from `rows[0]` of `ORDER BY time DESC LIMIT 3` — a query with no `rowid` tiebreak and no index on `time`, so under equal timestamps its first row need not be the event just stored, and a store's whole transition set would be filed under the wrong event. `store()` returns the event, so the target now comes from a keyed lookup on the primary key and the window identifies sources only; the stored row stays a source, as it is for the engine. Two tests: a forced-tie arm (5 tied windows in 6 stores on SQLite 3.45.1, every target the stored row — and on this build `rows[0]` happened to agree, so the defect was latent, not misfiring) and a contrary-order test that returns the tied window with the stored row last, asserts on those rows that their timestamps tie, that `rows[0]` really is a different event, and requires the recorded target to be the stored one anyway. Calibration was rerun and reproduced `docs/reusable_knowledge_calibration.json` **byte for byte**: 254–576 of 604–1277 measurable claims still fail per seed, `authorises_confirmatory` stays false, audit 8 of 8, and no confirmatory seed has run. Journal §99. |
| 2026-11-02 | **The study is closed at calibration, and the failures are relayed world content rather than circular support.** The per-claim rule failed on all five calibration seeds, so no confirmatory seed runs under this protocol, no threshold changes, and the §20.5 verdict stands; the closure is now recorded in protocol §20.7 rather than left to be read off `authorises_confirmatory`. A postmortem (`--postmortem`, `docs/reusable_knowledge_postmortem.json`) re-reads the same five cells and classifies each self-sourced transition by what the sleep row carries: the payload is candidate JSON, so the engine's extractor makes tags of its field names too. Circular self-restatement is negligible (8 formation / 7 revision transitions); excluding the encoding's own field-name transitions rescues **0 of 1,834** failing formation and **0 of 1,792** failing revision claims; what dominates is `content_relayed` (44,897 of 60,525 formation self transitions) — world vocabulary carried in the organism's own stored structures. The rule therefore measures whether the *immediately preceding event* was the world's, not whether the evidence originated in the world. Nothing about the verdict moves: the postmortem asserts `rule_unchanged: true` and `authorises_confirmatory: false` before writing, and a test checks it. The next step is a separately named variant with its own preregistration and fresh seeds. Journal §100. **Superseded by the next row of this log: `content_relayed` was mislabelled, its origin is not traced, and the class is now `content_unresolved`.** |
| 2026-11-02 | **The postmortem's first labels were corrected before they informed anything.** The classifier called any transition with *one* field-name endpoint `schema` (which reads as "between two field names") and called the remaining content `relayed` (which asserts a world origin). It now reports `field_name_both`, `field_name_one` and `content_unresolved` separately, and the artifact records that the origin of non-schema content is **unresolved**: the payloads carry 2340 parent ids and 0 event references across five seeds, so nothing traces content back to a world event. With the corrected labels, excluding transitions between two field names rescues 0 of 1,834 failing formation claims and 0 of 1,792 revision claims, excluding every transition that touches a field name rescues the same 0 and 0, because `field_name_both` is 0 / 0 by construction: the observer records only after world stores, so a field name can only ever be the prior tag and the encoding's whole footprint is `field_name_one` (15,576 / 20,876). Circular restatement remains negligible (8 / 7 transitions). The verdict does not move: the study stays closed at calibration, the rule is unchanged, and no confirmatory seed has run. Journal §100, protocol §20.7. |
| 2026-11-02 | **A provenance tracer exists, and it is proven on controls before it sees data.** `benchmarks/provenance_trace.py` follows a claim's `parent_ids` to its terminal structures (breadth-first, cycle-safe, depth-capped at the engine's own 7) and classifies the chain `world_rooted` / `mixed` / `self_only`, or `unresolved_*` with a reason when a terminal cannot be reached. Resolution stated: structures name **structure** ids, not events, so `world_rooted` means *every ancestor carries tags the world also uses*, not *descends from observation X*. Run `python -m benchmarks.provenance_trace --controls`; the controls (world-derived, self-only, mixed, missing parent, cycle, depth-capped, and a vocabulary-removal mutation) all pass, and writing them caught two design bugs before any real data: the index must include the claim itself, and grounding must exclude the claim's own words or every claim naming a world tag is `world_rooted` by definition. A claim with no parents is `unresolved_no_ancestry`, not `self_only`. This is an instrument, not a study: no threshold, no verdict, no seeds; the closed study and its failure are untouched. Journal §101. |
| 2026-11-02 | **A resolved branch no longer hides an unresolved one in the provenance tracer.** The first controls covered isolated defects only: with one world-tagged parent and one missing parent, `trace()` reached a terminal and returned `world_rooted`, reporting the missing record in a field that is not a status. The same masking applied to a cycle or a truncation on a second branch. Any defect now appends `_incomplete` to the verdict (`world_rooted_incomplete`, `mixed_incomplete`, `self_only_incomplete`) and the result carries `defects` and `complete`, while `nodes`/`terminals` still summarise what resolved; only a complete lineage may be read as `world_rooted`. Three mixed-lineage controls were added (missing parent beside a world-tagged branch, cycle beside a self-only branch, truncation beside a world-tagged branch) and 7 existing ones still pass. Still an instrument: no threshold, no verdict, no seeds, and no real data traced. Journal §101. |
| 2026-11-02 | **Convergence is no longer mistaken for a cycle in the provenance tracer.** The traversal flagged any repeated node, so a diamond lineage (two parents sharing one ancestor) was reported `_incomplete` even though it is complete — which would have under-counted `world_rooted` on the multi-parent graphs the engine produces most. Cycle detection is now a colour DFS over the collected edges: only an edge into a node still on the current path is a loop, and a revisit after full exploration is convergence. A `diamond_shared_ancestor` control must stay `world_rooted` with `complete: true` and the shared ancestor counted once, and a second control places a real loop beside a diamond and requires the loop still to be reported. 11 controls now, all passing. `world_rooted` still means vocabulary overlap along a complete ancestor chain, not proof of descent from a particular observation; no real data has been traced. Journal §101. |
| 2026-11-02 | **The reading of the provenance tracer is frozen before it sees real data.** [`docs/PROVENANCE-ANALYSIS-PLAN.md`](PROVENANCE-ANALYSIS-PLAN.md) fixes the interpretation in advance: `world_rooted` means vocabulary overlap across a complete ancestor chain and never observation-level provenance; incomplete and unresolved lineages are reported separately and are never folded into rooted or self-only; counts are reported by claim type and by lineage depth; and there is no threshold, no pass mark and no verdict. A plan written after the counts would be a description of them. The diagnostic it governs runs only on the five already-used calibration seeds, cannot validate transfer or reopen the closed study, and commits the reading of either outcome in advance: mostly unresolved points at missing lineage in the recorded structures, and mostly vocabulary-overlap says useful chains exist without showing that the links track world evidence. Journal §102. |
| 2026-11-02 | **The provenance diagnostic ran on the five already-used calibration seeds, and the finding is structural: the claims the study scores have no ancestry.** `python -m benchmarks.provenance_trace --diagnostic` (results [`docs/PROVENANCE-DIAGNOSTIC.md`](PROVENANCE-DIAGNOSTIC.md), artifact [`docs/provenance_diagnostic.json`](provenance_diagnostic.json)) traced every claim-typed structure in the formation and revision snapshots. All 1581 formation and 1596 revision `prediction_candidate` structures resolve **zero** ancestors — `unresolved_no_ancestry`, with no dangling-parent claims — so the population the per-claim rule and the transfer limb are about cannot be entered by the walk at all. The 63 / 57 `hypothesis` structures do carry seven-ancestor chains that resolve inside the cap: 14 / 13 complete `world_rooted`, the rest incomplete because a branch is cyclic (39 / 41) or its parent was pruned (23 / 9), and none because of the depth cap. This is the plan's pre-committed mostly-unresolved branch: the missing lineage is in what the engine records, not in the walk. Read it as vocabulary overlap across a complete chain and nothing more — a hypothesis is composed from its members, so world tags on its chain are near-tautological for that type; it is not observation-level provenance. No threshold, no verdict, no confirmatory seed; the closed study stands. The harness gained `run_engine(collect_structures=...)`, off by default, and a re-run of seed 20261201 without it reproduced the committed pair counts (asserted 327, revision-asserted 328, temporal 393). Journal §102. |
| 2026-11-02 | **The provenance diagnostic was counting a different unit from the study, and now reports three.** The tracer deduplicates a structure's per-cycle snapshots by id; the study's per-claim rule passes the raw candidate list to `_claim_edges`, which drops ids and counts one row per cycle. For seed 20261201 that is 1313 formation / 656 revision claim rows against 329 / 328 unique claim structures, and the sentence calling them the same population is withdrawn (journal §102 amendment, plan Amendment 1). The diagnostic now reports raw stored claim rows, unique structure ids and unique asserted edges with their mapping, states lineage statuses at the id level (the level that has an id to walk) and the edges whose claim is complete `world_rooted` beside it, and **aborts** unless `_claim_edges` on the same raw payloads equals its own raw-row count. The structural finding is unchanged and now scoped: unique prediction structures carry no parent links, so no raw prediction row can either. No new cell was run — the same five calibration cells were re-read — and the study stays closed. | **Parent links counted per snapshot (same day):** the tracer deduplicates to the highest-generation snapshot, so "the structure has no parents" described that snapshot only, and every raw snapshot of the same cells has now been counted: 7307 prediction rows, 0 with parent links, 0 ids ever carrying links. The claim that no raw prediction row ever had parents is therefore true — and now measured instead of inferred from a deduplicated walk.
| 2026-11-02 | **Parent links were being read off one snapshot per structure; they are now counted across all of them.** Deduplication keeps the highest-generation snapshot of each id, so a statement about "the structure's parents" described that snapshot and could not support a statement about every raw row. All raw `prediction_candidate` and `hypothesis` snapshots from the same five calibration cells are now counted with the two questions separate — ids that **ever** carried parent links, and ids whose **latest** snapshot does — and reported with the mapping between them. Prediction rows: 7307 raw, 0 with parent links, 0 ids ever carrying links, 0 ids whose links appear only in earlier snapshots; hypothesis rows: 275 raw, 275 with links. The lineage statuses still describe the latest snapshot, and that is now stated wherever they are quoted. No new cell was run and the study stays closed. Journal §102, Amendment 2. |
| 2026-11-02 | **A prospective formation-provenance instrument exists, proven on synthetic controls and not yet pointed at any study cell.** `benchmarks/formation_provenance.py` records, at the moment a prediction is formed, which stored events supplied the tag pair it asserts — the question the ancestry tracer could not answer, because prediction candidates carry no parent ids. The hook calls the engine's own `_build_predictions` and returns its list unchanged; an observer that changes behaviour is not an observer. Origins are classified `pair_world_attributed` / `pair_mixed` / `pair_self_sourced` / `pair_unattributed`, the last being *not zero support* but a recorder that did not see the events, and the vocabulary is deliberately disjoint from the tracer's so the two questions cannot be conflated. 8 synthetic controls pass, including three that can fail: deleting the world transitions must flip `pair_mixed` to `pair_self_sourced`, a mutating subclass must be caught by the neutrality comparison, and reinforcing an edge must strictly increase its recorded world transitions (6 to 9). The unit is a transition (prior event row, stored event row), never a count of "observations". It establishes no usefulness: provenance is not held-out generalization, and the prospective study that would ask that needs its own preregistration on fresh seeds with the closed confirmatory set untouched. Specification: [`docs/FORMATION-PROVENANCE-SPEC.md`](FORMATION-PROVENANCE-SPEC.md). No threshold, no verdict, no seed; no study cell was run. Journal §103. |
| 2026-11-02 | **A prospective provenance study is preregistered on fresh seeds, before any cell runs under it.** [`docs/FORMATION-PROVENANCE-PREREGISTRATION.md`](FORMATION-PROVENANCE-PREREGISTRATION.md) fixes the question — *can a candidate's recorded origins be traced, and does that trace predict successful held-out generalization?* — with the endpoint (the difference in held-out success between `pair_world_attributed` candidates and candidates whose origin includes a self-sourced row, 98.33 % interval, lower bound strictly above zero), a permutation control that must fail, and four gates that stop the study rather than let it shrink: liveness, denominators of at least 30 per arm, the permutation control, and instrument neutrality. Seeds are fresh and disjoint from everything used: design `20270101`–`20270105` for liveness and sample size only, confirmatory `20270106`–`20270120`. The world and withholding rule are reused unchanged from the closed protocol so the worlds stay comparable; the cells are not — no closed seed is read or re-scored, and the closed verdict stands. A positive result would mean an association between recorded provenance and held-out occurrence, and would **not** mean that the knowledge is useful or reusable, that the closed study's transfer failed, or that the content originated in the world. Journal §104. |
| 2026-11-02 | **G13-D ran once, as authorized, and every paired cell came out better under the combined condition.** Plan committed at `c1c46dd` before execution ([`docs/G13-D-DIAGNOSTIC-PLAN.md`](G13-D-DIAGNOSTIC-PLAN.md)); seeds `20261101`–`20261105` only; capacity `MAX_PREDICTIONS = 1,000` plus a lookback restricted to `event_type != 'sleep'`; `alpha = 256.0` fixed in both arms as a constant, not an intervention; both overrides in process, `git diff --stat -- organica/` empty. The interventions were verified before any score was read: the world-only lookback removed every `precedes` source tag absent from the world (11–18 present in baseline, zero under the condition). **Correction, same day, before any interpretation:** the capacity check counted candidates of all types (3,998 in both arms) and so did not test the prediction cap; it is recorded as *not measured*, capacity is verified structurally only (`MAX_PREDICTIONS` 20 vs 1,000), scores were not recomputed, and the result therefore describes the combined condition without decomposing it. Paired log-loss (g13d minus baseline) was negative in **15 of 15** unique seed × window comparisons (30 of 30 counting the metric shape, which coincides exactly), with pooled means retention **-0.0296**, transfer-diagnostic **-0.0305** and revision **-0.0432**; the two metric shapes coincide exactly on this readout, so there is one result here, not two. The per-seed artifact entries and the per-seed caches now record the capacity check as *not measured* throughout, and regenerating the artifact from cache reproduces identical scores. **Read it as a diagnostic only:** no threshold, no acquisition or transfer result, no V2 authorization, and the closed protocol, its Gate 13 threshold, the Task 2 verdict and every confirmatory seed are unchanged. Results [`docs/G13D-DIAGNOSTIC.md`](G13D-DIAGNOSTIC.md), artifact [`docs/g13d_diagnostic.json`](g13d_diagnostic.json). This thread now stops; broader work needs a new recorded owner decision. Journal §105. |
| 2026-11-02 | **The preregistered provenance study ran: design block first, then one confirmatory run, and it found an association.** Design seeds `20270101`–`20270105` were used only for the three gates — liveness on every seed, a projected **4422 / 8874** candidates per arm against the 30 floor, and instrument neutrality over **3998** candidates compared exactly — with no endpoint evaluated. The confirmatory seeds `20270106`–`20270120` then ran once: world-attributed pairs occurred in the held-out window **0.4528** of the time (1938/4280) against **0.2387** (2036/8528) for pairs whose origin includes a self-sourced row, difference **+0.2141**, 98.33 % interval **[+0.1959, +0.2281]** (cluster bootstrap over seeds, recorded in the artifact). The permutation control included zero (**-0.016244**, **+0.016023**), and `pair_unattributed` never occurred, so no candidate was excluded. **This is an association between recorded provenance and held-out occurrence, nothing wider:** it does not show the knowledge is useful or reusable, does not establish where the content originated, does not reopen the closed study, and is not the functional test of whether developed structure helps — that still needs held-out predictive performance against equally exposed baselines. Results [`docs/FORMATION-PROVENANCE-STUDY.md`](FORMATION-PROVENANCE-STUDY.md), artifacts [`docs/formation_provenance_study.json`](formation_provenance_study.json) and [`docs/formation_provenance_study_design.json`](formation_provenance_study_design.json). Journal §106. |
| 2026-11-02 | **Descriptive robustness checks on the provenance association; the registered verdict is unchanged.** Using only the cached per-candidate records (no cell re-run), all **15 of 15** confirmatory seeds show a positive difference (+0.1461 to +0.2435), every leave-one-seed-out fold stays positive (+0.2117 to +0.2187), and comparing candidates at the same recorded `temporal_count` keeps the direction: positive in **17 of 17** strata holding both arms, stratum-weighted difference **+0.2384**. The registered permutation preserved seed and cycle but not evidence count, so this closes that gap descriptively — **not** causally, and not as evidence of usefulness. These checks create no success rule and change no threshold; the registered result stands. Artifact [`docs/formation_provenance_robustness.json`](formation_provenance_robustness.json), report [`docs/FORMATION-PROVENANCE-ROBUSTNESS.md`](FORMATION-PROVENANCE-ROBUSTNESS.md). Journal §107. |
| 2026-11-02 | **A functional preregistration now fixes the project's open question before any cell runs.** [`docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md`](FUNCTIONAL-STRUCTURE-PREREGISTRATION.md) asks whether formed structure improves **held-out prediction** under proper probability scoring — mean log-loss per held-out tag pair — against simple baselines given identical exposure and tuned on a split excluded from their fits. Organica runs at capacity 1,000 with `alpha = 256.0` carried over unchanged; the primary window is cycles 150–200, the co-primary is the withheld-transition subset, and the bar is the **upper** bound of a 98.33 % cluster-bootstrap interval on the difference falling below zero. Seeds are fresh: design `20270201`–`20270205` for harness audit, liveness and denominators only, confirmatory `20270206`–`20270220` run once. The provenance record is a **compulsory diagnostic**, with a pre-committed disqualifier: a margin carried mainly by self-sourced support is reported as not a transfer result even if the score clears the bar. No endpoint is evaluated on design seeds, no threshold moves, and a failure does not reopen the closed study or the provenance study. **The harness is not built.** Journal §108. |
| 2026-11-02 | **Amendment 1 makes the functional protocol executable before any build.** Three clauses were undefined: exposure versus tuning, the probability score, and the self-sourced disqualifier. The amendment fixes them without moving a seed, gate, capacity, alpha or bar. All 110 formation cycles are exposure for every arm; the last 15 are excluded from **hyperparameter selection only**, and the winning baseline is refit on all 110 rows, as the closed comparator already does. The score is the closed protocol's `score(exclude_self=True)` adopted verbatim: one cell per (source tag, vocabulary target), the `b = a` cell kept with label zero, denominator equal to event pairs × source tags × vocabulary. The disqualifier is a share of the positive per-cell improvement on realised held-out transitions: pairs are world-majority only when `world > self`, and a self-majority share of **0.50 or more** withholds the transfer claim, as does an unattributed share of 0.50 or more. It can withhold a claim, never create one. Journal §109. |
| 2026-11-02 | **Gate G6 closes the last pre-build gap: the provenance disqualifier must be proved able to fire.** G3 could fail and G4 is neutral, but nothing showed the §11.3 rule withholding a claim. G6 requires synthetic fixtures, with no engine run, returning all four outcomes: world-majority **passes**, self-majority **withholds** as *not a transfer result*, unattributed **withholds** as *not attributable*, and an empty positive margin is *not evaluable*. It also requires the boundary to fire at exactly 0.50 and not at 0.4999, `world == self` to count as self-majority, and a relaxed 0.90 threshold to stop the self-majority fixture withholding — proof the fixture carries the signal rather than the rule being unable to fail. Amendment §11.5 names the baseline (the same strongest comparator that supplies the §4 bar, refit on all 110 rows) and the window rule: primary and co-primary computed separately, never pooled, claim withheld if either reaches the threshold. No cell has run. Journal §110. |
| 2026-11-02 | **§9's pass wording is corrected to match §4: the bar is the upper bound below zero, not the lower bound above it.** The endpoint is `Organica − baseline`, negative meaning Organica scored better, so §9's "lower uncertainty bound cleared zero" described the opposite result — evidence of the wrong direction. §9 now states the upper bound, notes why the direction is not incidental, and defines "moved" for the co-primary window three ways: **moved** (upper bound below zero), **did not move** (interval contains zero, so a primary pass is held-out generalization only), and **moved the wrong way** (lower bound above zero, reported as reversed on that window). Neither window gates or re-scores the other. No cell has run. Journal §111. |
| 2026-11-02 | **The functional study's scoring layer exists, with its G6 gate firing.** `benchmarks/functional_structure.py` implements §11.2 and §11.3 as pure functions — cells, per-cell loss, the four attribution outcomes — and imports no engine module, so its gates run before any cell exists. `python -m benchmarks.functional_structure --gates` runs synthetic fixtures that must return each outcome and raise on any mismatch: world-majority **passes**, self-majority at 0.60 **withholds**, unattributed at 0.75 **withholds**, an empty positive margin is **not evaluable**, the boundary **fires at exactly 0.50** and not at 0.4999, a tie is self-majority, and a relaxed 0.90 threshold **stops** the 0.60 case from withholding. `tests/test_functional_structure.py` also proves the layer reproduces `acquisition_baselines.score` to 1e-6 in both shapes, and that the gate raises when the rule is replaced by one that never withholds. The engine binding — running a design seed through the frozen engine and scoring it — is **not written yet**, so the harness is not complete and no cell has run. Journal §112. |
| 2026-11-02 | **The functional protocol's run order is now a sequence, not a loop.** §10 previously said no cell of any block may run until the harness is committed *and the design block has passed* — but the design block cannot pass without running its five seeds, so the clause forbade the only run that could satisfy it. §10 now states three steps: **(1)** build, commit and pass the gates; **(2)** run the design block `20270201`–`20270205` only, for liveness, denominators and gate checks; **(3)** run the confirmatory block `20270206`–`20270220` only if the design block passes, one run, no seed added or dropped. The endpoint is **locked until step 3**: `delta` against the best baseline is not formed on a design seed, and a design number may appear only inside a gate diagnostic labelled as one. A guard (`test_run_order_is_explicit_and_not_circular`) now fails if the circular sentence returns or the steps lose their order. Journal §113. |
| 2026-11-02 | **The functional harness is built and the design block has passed — and the design audit found a defect in the protocol's own disqualifier.** `benchmarks/functional_harness.py` develops one arm per seed over the 110-cycle formation stream, freezes the readout at capacity 1,000 and smoothing 256.0, scores the primary (cycles 150–200) and co-primary (withheld-relation) windows, and runs gates G1–G5. `PYTHONHASHSEED=0 python -m benchmarks.functional_harness --design` ran `20270201`–`20270205` only, in about 164 seconds, and **all gates passed**: live readout, one 12768-cell denominator per arm in both windows, a harness that separates the law from a one-transition learner and rejects a degraded readout, a recording hook that leaves the engine's candidates identical, and pinned constants. **The finding:** §11.3's disqualifier withholds whenever the unattributed share reaches 0.50, but the 32 relations the co-primary window scores are the ones formation never carried, so they have no world count by construction (13 of 32 appear in the record at all, and those carry sleep rows only). The rule therefore withholds the transfer claim on every world, whatever the score; the primary window's margin sits on the same cells (7 world-majority of 411 positive-margin cells on the first seed). The endpoint was **not** formed and no confirmatory seed was touched. **Owner decision needed** before step 3: amend §11.3, or accept that the study can report held-out generalization but never transfer. Journal §114. |
| 2026-11-02 | **The transfer limb is recorded as *not attributable under the current provenance measure*, and the endpoint lock is restated accurately.** That status is about the measure, not the engine: the withheld relations were withheld from formation, so they cannot carry world-source support (12–16 of 32 appear in the record; **none** is world-majority on any of the five design seeds), and §11.3 withholds on both the self-majority and unattributed routes. The limb can be scored; it cannot establish transfer; that is not evidence of failed transfer. The threshold is unchanged. Second correction: §10 said the endpoint was "not formed" on design seeds, which was too strong — §11.3's share is defined on per-cell paired losses, so the wiring computes both arms' losses on every realised cell and subtracts them. Those per-cell differences are the endpoint's building block. What stays locked is the statistic and the verdict: the pooled `delta` is not formed, no margin is compared with §4's bar, and the artifact lists both under `endpoint_boundary`, labelling what it computes an **endpoint-derived diagnostic**. **Owner decision pending:** whether to spend the one confirmatory run on the primary held-out question alone. Journal §115. |
| 2026-11-02 | **The record now says plainly what the design run computed, and two contradictions are gone.** §10 step 2 had said the disqualifier "cannot make or withhold a claim on a design seed", while §10.1 reported that it withheld; §10.2 had said the co-primary share was "above 0.50 before any score is read", while the share was computed from per-cell paired losses that had been read. Both are rewritten. The consistent statement: the design run **computed** per-cell paired losses for both arms on both windows (the spread §11.3 is defined on), and **withheld** the pooled `delta`, any comparison with §4's bar, any direction, and every confirmatory statistic. Those losses were inspected — by the attribution to produce the share, by G3, and in the document — and the transfer measure was classified un-attributable from them. That classification is about the instrument and is also derivable from the coverage counts alone. New §10.3 states computed / withheld / inspected / concluded in four lines. Thresholds and scores unchanged. Journal §116. |
| 2026-11-02 | **The functional study has run its one confirmatory block, and the primary bar was not met.** Seeds `20270206`–`20270220` (n = 15), 432 s, artifact `docs/functional_structure_confirmatory.json`. **Primary window:** pooled `delta` -0.003818 nats, 98.33 % interval [-0.010802, 0.002863] — contains zero, so **no improvement detected**; per-seed deltas run -0.027099 to 0.015468, sign flips across seeds. **Co-primary window:** pooled `delta` -0.359327 nats, interval [-0.369382, -0.345823] — a clear score improvement on the withheld relations, but the disqualifier returns `not_attributable` (unattributed 0.700807 of the positive margin), so **the transfer claim is withheld** and the limb stays un-attributable under the current measure. The primary window's margin is also mostly unattributed (0.698500). §8 allows one run; there is no re-run, and the co-primary does not rescue a failed primary. Journal §117. |
| 2026-11-02 | **Result frozen; the record's last stale pre-run statements corrected.** The functional study's outcome is final for this protocol — no re-run, no seed added or dropped, no threshold, constant or gate adjusted in its light (§8) — and §10.4 now says so in one sentence. Two statements were still written from before the run: §11.4 said "no cell has run", and the `functional_harness.py` docstring said design-seed losses were "not computed, not printed and not stored". §11.4 is now past tense with a pointer to §10.1/§10.4; the docstring now states the §10.3 distinction (per-cell paired losses computed and labelled endpoint-derived diagnostics, the pooled statistic not formed). The header status line and the "refuses any seed outside the design block" paragraph were stale for the same reason and are fixed in the same pass. No number moves. Journal §118. |
| 2026-11-02 | **The benchmark is closed, the finding is frozen in three statements, and the paper now carries it.** The freeze in §10.4 states: **primary** — no improvement detected over the tuned baseline, the interval crossing zero with per-seed signs both ways; **withheld relations** — a better score and **not attributable** under the preregistered provenance measure, so no transfer claim in either direction; **no further runs and no threshold changes**. Paper 01 gains §4.10 (design, the audited design block, the one confirmatory run, the provenance result and its two surviving readings), §4.9 gains two claim-status rows, and §3.1, §5.2, §6 and §7 carry the result and its limits; `papers/README.md` updates Paper 01's row and its claim-status table. V2 design is deferred until the manuscript states what V1.1 did and did not demonstrate. Journal §119. |
| 2026-11-02 | **The structural-contribution question is now fixed in advance, as a draft.** [`docs/STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md`](STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md) asks whether the **content** of Organica's formed edge structure improves log-loss on the withheld relations, and answers it by ablation rather than by provenance: four arms on one formation stream — the full readout, the same readout with an empty edge table (the base-rate backoff, checked to equal `m(b)` rather than assumed), a **degree-preserving rewiring** of the same table (Maslov–Sneppen double-edge swaps, 25 draws per seed, mean used, best draw never), and the tuned bigram. The primary criterion is beating **both** the edge-removed and rewired controls; beating the bigram is reported beside it and is explicitly not part of it. The rewiring preserves node set, edge count, per-source out-degree, per-target in-degree and the weight multiset, and does not preserve the pairing — so a row's total weight legitimately differs, which is disclosed rather than engineered away. The control is gated: if more than 20% of `(source, target)` pairs survive rewiring, the study stops. All five outcomes of the three bounds are named in a table before a number exists, including the one that would mean the current interpretation needs rethinking. Seeds are fresh — design `20270301`–`20270305`, confirmatory `20270306`–`20270320` — constants are the frozen study's, and **no harness exists yet**. It is labelled a **structural-contribution test, not a transfer test**, because the provenance measure cannot certify transfer on intentionally withheld relations. **Owner decision:** review the draft before any harness is built. Journal §120. |
| 2026-11-02 | **The structural-contribution harness is built, its design block ran, and it stopped the study at the first gate that matters.** Two new modules: `benchmarks/structural_contribution.py` (the Maslov–Sneppen rewiring rule, its invariants, the 20 % control gate and the §6 outcome table) and `benchmarks/structural_contribution_harness.py (closed), strength_assignment.py and strength_assignment_harness.py (the replacement study, design block passed 2026-11-02)` (`--design`, `--only`, and a `--confirmatory` path that refuses to run unless the design block passed). `PYTHONHASHSEED=0 python -m benchmarks.structural_contribution_harness --design` ran `20270301`–`20270305` in 176 s. **Result: the block failed gate S3b on all five seeds.** The engine's readout is dense — **329–333 edges over 23–24 source tags and 17 target tags, 86–87 % of the possible pairs** — so degree-preserving swaps are refused as duplicates almost every time (1,631 of 2,000 attempts on the first seed; 9 swaps landed). The rewired arm stayed **95–96 %** identical to the full readout against a **20 %** limit; and even a perfectly mixed sample would retain about 82 %, so the rule and the gate cannot both hold at this density. Everything else passed: S1 liveness, S2 denominators, S3a (`max abs gap 0.0` — the edge-removed arm really is the base-rate backoff), S4 invariants on all 125 graphs, S5 constants, S6 reproducibility — and **S3c's oracle plant separated the arms** (0.378707 vs 0.487589 removed and 0.443569 rewired), so the harness does detect a contribution when one is present. **No contrast was formed and no confirmatory seed was read**; the arm losses in `docs/structural_contribution_design_audit.json` are labelled gate diagnostics, not a result. **Owner decision needed:** either amend §4 to a weight-level null (keep the pairs, permute which pair carries which weight) or close the study at the identifiability limit. §11 now records that any result here is a result about one world family. Journal §121. |
| 2026-11-02 | **The structural-contribution study is closed at its design gate, with the density finding as its result.** The owner's decision, recorded in [`docs/STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md`](STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md) §12.6: §1–§10 stay exactly as committed, no confirmatory seed is run, and no weight-level shuffle is substituted into this study — that control keeps every formed pair, so it tests whether edge *strengths* matter rather than whether the learned *pairings* matter, which is a different question needing its own preregistration and its own success criterion (if pursued: weights shuffled within each source row, so `W(a)` survives with the topology). The 20 % overlap limit is **not** relaxed after the fact — a limit moved because the control it guards failed is not a limit. Clean record: stopped at **S3b**; topology-level contribution **not identifiable with this readout and null**; no confirmatory result. Action-list row 9 is resolved. Journal §122. |
| 2026-11-02 | **Paper 01's submission package is rendered, checked and bundled; the upload is the only step left.** The manuscript now compiles to a **23-page PDF** with **0** LaTeX errors and **0** overfull boxes, after eight build-copy rewrites recorded in `docs/PDF-PIPELINE.md` §4 — the duplicate title, double heading numbering, ten unbreakable `\texttt` paths (widest 140 pt into the margin), the fatal microtype-without-scalable-fonts error, and a missing Unicode map that made the deposited text read "con rmed" and drop **all 34** section signs. `\input{glyphtounicode}` fixes it: 34 of 34 now extract. The evidence check found a real gap and it is fixed: the software record was archived at `v0.10.0`, which predates the two artifacts §4.10 cites, so `deposit_bundle.py --check` reported 38 cited, **2 missing**; the record is now archived from the commit at version **0.11.0** (no tag cut — that is your act) and checks **38 of 38**. Bundles: software archive, Paper 01 (8 files), Paper 02 (6 files), each with `SHA256SUMS` and a manifest, under `.scratch/deposit/`. Paper 02 also renders (14 pages, 0 errors) but its wide audit tables still overrun the margin. Action-list row 10 is the upload. Journal §123. |
| 2026-11-02 | **Paper 02 is typeset clean, and both papers travel with a reproduction bundle.** Its 21 overfull boxes traced to one line of the render escape: a `\texttt` span of 24 characters or fewer was made breakable only if it contained a `/`, so the acceptance-criteria table's 40-character test names had nowhere to break and ran **209 pt** into the margin — the rule is now by length, not shape. The nine-column ancestry table cannot hold \"Reachability\" in a 41 pt portrait column at any readable size, so tables of seven columns or more are set on a **landscape page** (`pdflscape`); seven, not six, because Paper 01's six-column tables set fine in portrait and rotating them cost three pages. A 103-character comment line in a script block is set at `footnotesize` rather than wrapped, since a wrap in a block a reader may copy is a break that is not in the command. **Paper 02 now renders to 17 pages, 0 errors, 0 overfull boxes; Paper 01 is unchanged at 23 pages, 0 and 0.** `benchmarks/deposit_bundle.py` also builds a fourth, non-Zenodo bundle — `reproduction/` — naming the archived commit, the build environment, the four commands that regenerate figures and PDFs, and the expected page counts and hashes. Journal §124. |
| 2026-11-02 | **Both deposited PDFs now carry their own document properties, and the build checks them.** Opened as files rather than as sources, both had `/Title`, `/Author`, `/Subject` and `/Keywords` **all empty**: hyperref fills none of them unless asked, and `pdfusetitle` is not an option here because the template's title is a `\parbox`, so a viewer's title bar was blank and a reference manager would import an untitled, unattributed document. `benchmarks/render_papers.py` now holds a `PDF_INFO` entry per paper — the paper's own title, not the "Paper 1/2" label — passes the four values to the template as metadata, and `verify_pdf_info` reads them **back out of the built PDF** and fails the build if one is missing or wrong; a deliberately wrong value was run before the check was trusted, and it fired. Page counts and box counts are unchanged: **23** and **17** pages, 0 errors, 0 overfull boxes. **The pages themselves are still unverified visually** — no rasteriser exists on this machine — so action-list row 10 now carries the human check. Journal §125. |
| 2026-11-02 | **A PDF's title can no longer drift from its paper.** The title lives in two places — the manuscript's level-one heading and `PDF_INFO` in the renderer — and neither half looks wrong, so a retitle could leave the deposited file claiming a title the paper no longer has. `verify_title_matches` now derives the expected title from the heading with the project's "Paper N:" label removed and fails the build on a mismatch, before anything is typeset; `tests/test_pdf_titles.py` asserts both papers currently agree and that the guard fires on a stale value. Both PDFs rebuilt unchanged (385,296 and 302,835 bytes, same as before). Journal §126. |
| 2026-11-02 | **The deposit records now name the papers by their own titles, and Paper 01's record describes §4.10.** Both records had drifted in the one field a citation prints: Paper 01's said *…: a preregistered account of what the engine grows, and what it does not* and Paper 02's said *Persistent structural provenance in Organica 1: …*, neither of which appears in the PDF it describes. The titles are now the documents' titles, exactly as `PDF_INFO` declares them, and the descriptive phrase lives in `description`; Paper 01's description predated §4.10 and now reports the capacity-1,000 result with its numbers, including the withheld-relation margin the provenance measure returns as *not attributable*. `tests/test_pdf_titles.py` asserts a record's title equals its document's, and `docs/ZENODO-DEPOSIT.md` states the rule. Separately, all 40 pages were rasterised and inspected: **Paper 01 is visually clean**; **Paper 02 has three layout defects** — a code block split across pages 7–8 leaving two orphaned lines, a heading-only page 12, and two captionless landscape table pages (9 and 13) that are ~70 % blank — all downstream of `landscape_wide_tables()`, and none of them fixed yet. Journal §127. |
| 2026-11-02 | **Paper 02's three layout defects are fixed, and the fix removed the mechanism that caused them.** All three traced to one function: the landscape environment breaks the page at both ends, so the section heading was left at the foot of the page before its table, and each three-row table sat at the top of an otherwise blank rotated sheet. The wide tables are now set in portrait a size or two down — 9pt at nine columns, where the widest header word is 38 pt in a 43 pt column — with a narrower gutter; the renderer breaks the page before a heading whose table cannot fit; and code blocks are unbreakable, so none splits. **Paper 02 is 14 pages, 0 errors, 0 overfull boxes** — three pages fewer than the landscape setting — and Paper 01 is unchanged at 23 pages, 0 and 0. Two defects found while looking are not fixed and are recorded in Journal §128: every figure carries two captions, and Figure 3's annotation text is clipped inside the figure. |
| 2026-11-02 | **A reviewer's revised report on Paper 01 was checked against the record; three findings were real and one was already answered, and the figures needed re-rendering.** The tuning-split sentence contradicted the implementation — the preregistration's §3 says "excluded from every fit" while its §11.1 says the two cannot both hold and adopts the refit on all 110 cycles, which is what `comparator_sweep` does; the manuscript now describes the two-stage procedure and records §3 as superseded (§11.1, journal §129). §4.4 now says the 3:1 crossing is a **grid-level** location — 3:1 is the first sampled point above parity and the crossing lies between 2:1 and 3:1 — rather than implying an interpolated threshold. §3.5 records Phase L's pre-outcome Amendment 2 (98.33 % → 99 %) and the seed-exchangeability audit as the post-outcome instrument check it is. §4.1 gained the one quantitative curriculum contrast the record holds (91 vs 128 at 1,200 cycles, one seed, exploratory) and states that no pooled effect size exists; §4.6 gained the Phase H–J table; §1.1 separates structure **formation** from the project's stronger emergence criterion. **Figure 1 in the deposit carried six of its eight sweep points** because the PDF beside the generator's SVG was stale, and three figures had text past the page edge; the overflow guard now measures Helvetica widths instead of assuming an average, and all eight figures were re-rendered at their committed page sizes. **Every figure also carried two captions** (pandoc's, from the image's alt text, plus the manuscript's own bold one) and a float could abandon its caption, which it did on the 25-page build; `pin_figures` now pins each figure with float's `[H]` and drops the duplicate caption. Paper 01 is now **25 pages** (was 23), 0 errors, 0 overfull; Paper 02 unchanged at 14. |
| 2026-11-02 | **The strength-assignment harness exists and passes its end-to-end design audit; it failed that audit once first, and the failure found the design's real limit.** `docs/STRENGTH-ASSIGNMENT-PREREGISTRATION.md` fixes the question (does the *assignment* of strengths to existing source–target pairs carry predictive information?), the intervention (permute each source row's weights among its own targets — topology, degrees, row multisets and row totals held exactly), the bar (lower bound of the 98.33 % interval on full − shuffled above zero) and four outcome labels, before any cell ran. The first design block **failed gate S2 on all five seeds**: only **6 of 372** realised cells on the withheld-relation window carried a formed edge, so a permutation had almost nothing to move. Amendment A1 (pre-outcome) made the **full** held-out window primary and gave S2 a **coverage floor of 0.50**; the re-run passes every gate with coverage **77.1 %–81.4 %**, and the layer's negative plant now proves a null with **nonconstant** weights. **No confirmatory seed has been read**; spending `20270406`–`20270420` is owner's action 11. Journal §130. |
| 2026-11-02 | **The owner's deposit review found a title page that printed its own line breaks; the other two defects it reported were already fixed in the 25-page build.** The author block is one hbox, so it was split with a backslash pair in the metadata — and pandoc parses metadata as markdown and escaped the pair, so the PDF showed a literal `\\` between name, ORCID and address. The separator is now a sentinel that survives pandoc and is replaced with a real break on the build copy; the build fails if it survives (`tests/test_author_line.py`). The doubled captions were removed when figures were pinned (Journal §129) and Figure 4's clipping was the stale, width-overflowing figure PDF — both gone from the current build. Rebuilt and repackaged: Paper 01 **25 pages**, Paper 02 **14**, 0 errors, 0 overfull each; deposit bundle regenerated, `sha256sum -c` clean, archive rebuilt. Journal §131. |
| 2026-11-02 | **The scaling ladder ran, and it separates resolution from replication.** `docs/SCALING-LADDER.md` (protocol §1-§6 fixed before the run) scores the frozen endpoint on five fresh methodology worlds at windows of 50-800 cycles with exposure held at 110. Within-run error falls 0.008830 -> 0.001450 (exponent -0.577, r2 0.928, inside the committed -0.5 +/- 0.15 band) while the between-world spread stays at 0.012157 -> 0.010247. At the frozen 50-cycle window `rho` = 0.726 and a run's own error is 1.18x its own delta, so **one run cannot resolve what it measured** and no number of runs reaches half the between-world SD; from 100 cycles `rho` <= 0.30 and about 6 worlds suffice. Action row 12 records the recommendation: score >= 100 cycles, then spend on worlds. Journal §132. |
| 2026-11-02 | **The sign criterion replaces the SE/delta ratio, and the 100-cycle threshold survives on a different argument.** The owner challenged the threshold on the grounds that the ratio is above 1 at 100 and 200 cycles and first falls below at 400. The challenge is right that the ratio is not a criterion and wrong that 100 cycles fails: `SE/delta` is a t-statistic, so 1.18 is 0.80 and 1.57 is 0.74, and the 200-cycle row is worse only because the *pooled* delta fell there (0.003536 -> 0.002085), which is a between-world movement in the numerator. [`docs/SCALING-LADDER.md`](SCALING-LADDER.md) §8 adds the criterion that does answer the question - the probability that one run reports its **own world's** sign, with the world's effect itself drawn from the widest scale other than the one judged, so no cell is graded against its own estimate. It is 0.855 at 50 cycles (0.780-0.917; one world of five at 0.90) and 0.977 at 100 (0.917-0.997; five of five), then 0.961, 0.974, 0.944 - not monotone, and inside what five worlds separate. Agreement with the **block's** sign is 0.694-0.780 and never improves, because one world's effect is negative: a fully resolved run there still disagrees with the average. Two ceilings, not two efficiencies. No seed spent, no world run, §7's verdict unchanged, and the recommendation's number is unchanged while its justification is replaced. Journal §133. |
| 2026-11-02 | **The sign-resolution estimator was audited against known truths, and the 100-cycle target is now labelled provisional.** The owner asked whether the estimator measures what it claims, given that the scored windows are nested and the 0.90 target was chosen after the run. [`docs/SCALING-LADDER.md`](SCALING-LADDER.md) §9 answers with five checks on the stored cells (artifact `docs/sign_audit.json`; no engine, no seed): the nesting is real (6.2 %-50.0 % overlap, correlation 0.164-0.562 under independent pairs) but does not enter the reported probability, because conditional on a world's effect the run's own error is independent of the reference; it does make the five rows dependent comparisons. **The reference rule does move the decision** - at 2x the probability is 0.976 with the leave-one-out reference and 0.898 with a fixed 4x one, clearing 0.90 for 5 and 3 worlds respectively - and at 0.95 only 4 of 5 clear. Against known truths the worst calibration error is 0.068 and it runs conservative; zero-effect cells are excluded as unmeasurable rather than scored. The audit also caught two defects in its own first version: an impossible correlation of 1.78 where the judged window is the longer one, and a degenerate zero-effect cell reported as a large error. Journal §134. |
| 2026-11-02 | **The 100-cycle scoring window is adopted as a convention, and the two ceilings are now reported separately.** `docs/SCALING-LADDER.md` §10 binds new methodology blocks to `2x` unless the block's own design record predicts the sign-resolution probability of a different window before it opens. Per-world sign resolution (`p` >= 0.90 for every world) is the criterion; `rho` is demoted to a description of the two uncertainties. Every block reports both per-world resolution and agreement with the pooled sign, because they differ in ceiling - 0.977 against 0.780 at `2x` - and a claim about an average effect must therefore carry the pooled estimate over worlds rather than the outcome of one run. Nothing was re-scored, V1's frozen window and its labels are untouched, no confirmatory seed was allocated, and the conditions axis is still untested. Journal §135. |
| 2026-11-02 | **The decision and the estimator audit collided in numbering, and the record now names both.** The audit landed as `docs/SCALING-LADDER.md` §9 and journal §134 while the adoption of the window was being written, so the adoption moved to §10 and its journal entry to §135. No content changed beyond the numbering and one sentence in §10 recording that the window is provisional: §9 shows the 0.90 target is a convention and that a fixed `4x` reference would place `2x` at 0.898 with three of five worlds. `tests/test_scaling_ladder.py` now asserts the document's section numbers are unique - a duplicate `## 9.` heading had silently sent the decision-section test to the audit block, where its phrases happened to be present. |
| 2026-11-02 | **The per-world criterion's conjunction is recorded as a known limitation, and the rule is left alone.** `every world >= 0.90` tightens as a study grows even when per-world resolution does not: under the weakest value measured at `2x` (0.917) applied to every world, the chance that a block clears is 0.648 at five worlds, 0.420 at ten and 0.177 at twenty. That is planning arithmetic and is labelled so. The owner's instruction was to keep the adopted rule and revisit the quantifier at the next methodological review rather than change a convention mid-study, so `docs/SCALING-LADDER.md` §10 records the limitation and states that the rule stands and may not be relaxed on those grounds; the options for the review (mean, median or a lower quantile) are named and not adopted. `tests/test_scaling_ladder.py` asserts the note and its three probabilities against the artifact. Journal §136. |
| 2026-11-02 | **The measurement framework is frozen and the next experiment waits on a claim choice.** The owner's review accepted the methodological work and named its risk: the apparatus now outgrew the question it serves, and another tool is likelier to refine than to test. Recorded as given: no framework change without a justification tied to a scientific question; define the next claim before designing anything; obtain independent review of definitions, estimators, comparators, controls and interpretation; then design the conditions experiment; then preregister and execute once. The four candidate ambitions are logged as pending - behavioral advantage, traceable decisions, structure-to-behavior links, and the combined framing - with the record's support for each stated and no preference executed on the owner's behalf. No seed allocated, V1 untouched, conditions axis still untested, and the 100-cycle convention still provisional. Journal §137. |
| 2026-11-02 | **The structure-to-behavior claim is adopted as a working hypothesis at Level 2, and its design record is written before any seed exists.** The owner confirmed option (3) - changes in internal structure produce identifiable changes in behavior - with the requirement that prediction not be confused with causation. [`docs/STRUCTURE-BEHAVIOR-DESIGN.md`](STRUCTURE-BEHAVIOR-DESIGN.md) therefore fixes the level (Level 2, held-out prediction; Level 3 excluded and stated as a later objective), the predictor (Phase L's `DI`, with a zero denominator reported not measurable and the cell excluded), the outcome (`revision_held_out` on transitions withheld from both exposure windows), the temporal order and the measured-disjointness guard between the two pair sets, three generating configurations with a gate that drops one rather than reusing another's withheld set, the null and both falsifiers, and the four pre-committed outcomes. The 100-cycle convention is a declared deviation for this endpoint and the design requires its predicted resolution under a named reference rule before seeds. No seed allocated, V1 untouched, and the independent review in §8 is required before anything runs. Journal §138. |
| 2026-11-02 | **The premise was checked against the record, and it needed one noun corrected.** `docs/formation_provenance_study.json` already reports a structural property - the recorded provenance of a formed candidate - associated with the pair *occurring* in a window the organism was never shown: 0.214061, 98.33 % interval [0.195886, 0.228119], permutation control including zero, 15 confirmatory seeds run once. That is structure tracking the world's later **content**, and its own record lists "that the knowledge is useful or reusable" as not established. Structure predicting the organism's own later **behavior**, and the stability of that relation across generating configurations, remain untested; [`docs/STRUCTURE-BEHAVIOR-DESIGN.md`](STRUCTURE-BEHAVIOR-DESIGN.md) §2a now carries the distinction and the numbers, so the design cannot be read as either a first association test or a repetition of one. No seed allocated. Journal §139. |
| 2026-11-02 | **The design record gains the two guards it was missing, and a way to check itself.** `DI` and the behavioural outcome are produced by the same readout, so disjoint pair sets are not independence: §4 now requires a mechanical baseline (the outcome regressed on structural size and the base rate, which must not already explain the relation) and says that a relation surviving the pair guard but not the size baseline must be reported as a size effect. §6 adds a permutation control that must return an interval containing zero, reusing the formation-provenance study's G3 design. §9 lists the commands that verify the record's numbers against `docs/formation_provenance_study.json` and run its own tests, so a reviewer can check what reading cannot settle. Still no seed, no run, review gate stands. Journal §140. |
| 2026-11-02 | **The independent review is now a document with a rubric rather than an intention.** `docs/INDEPENDENT-METHODS-REVIEW.md` states the five questions and where each is answered, the five eligibility criteria with the author exclusions spelled out, the nine-file package, the PASS/CONDITIONAL/DEFECT rubric with three overall outcomes, and the safeguard that the reviewer sees no data from this design because none may be produced until the outcome is recorded. Conditions must be specific enough to re-review; a rejection stays as written. A test asserts every path in the package exists, so the brief cannot cite an artifact that is not there. No reviewer appointed, no seed allocated. Journal §141. |
| 2026-11-02 | **The design became a protocol, and the review became a package.** `docs/STRUCTURE-BEHAVIOR-DESIGN.md` now opens with its nine required elements and their locations, carries the statistical model a reviewer would otherwise mark missing (rank correlation primary, standardized slope as effect size, 10,000-replicate world bootstrap at 98.33 %, per configuration, never pooled), the decision rule, the size baseline as a competing predictor, the sign-resolution clause that blocks seeds until the quantity is computed under a named reference rule, and a rejection table naming the sentence each outcome licenses - including that a positive result licenses "predicts" and the causal verbs are reserved for a Level 3 design. `docs/REVIEW-PACKAGE.md` is the cover sheet: five components, the prior-evidence summary with artifact pointers, what the package deliberately omits, how to check it, and the reviewer's reading order. No paper is drafted; a protocol paper would invite a proposal to be read as a finding. Journal §142. |
| 2026-11-02 | **The sign resolution is computed, and it changes the block's size.** `docs/sign_resolution_structure_behavior.json` (`python -m benchmarks.sign_resolution_behavior`, no seed) simulates the protocol's own decision rule over synthetic blocks: Spearman rho, interval by resampling worlds at 98.33 %, resolved only when the interval excludes zero with the predicted sign, checked against Fisher's z to within 0.052. Under the named reference rule (smallest relation of interest, 0.50) the block needs 48 worlds per configuration (p = 0.902); the ladder is 21 worlds at 0.70, 32 at 0.60, 48 at 0.50, 79 at 0.40, 144 at 0.30. Three configurations therefore need 144 runs. The protocol carries the result, the forced size, the three reasons it is an upper bound, and the statement that no seed is allocated and that choosing a smaller n after seeing the table would let the design pick its own effect size. Journal §143. |
| 2026-11-02 | **The sign resolution's bound direction was corrected, and attenuation is now priced.** The owner objected that "48 worlds" had been presented as an upper bound when attenuation implies the opposite: measurement error in `DI` weakens the observed relation, so more worlds are needed. The artifact now separates the two quantities (probability = upper bound; minimum n = floor) and states what 0.902 is not (not a posterior, not a p-value, not a property of the engine). An attenuation table prices classical error in one variable: reliability 1.00 needs 48, 0.90 needs 61, 0.80 needs 79, 0.70 needs 105, 0.60 needs 144 worlds per configuration. Exchangeability is now an explicit assumption with a required diagnostic (lag-1 dependence on seed order; block resampling if non-negligible). `DI`'s reliability is unmeasured and is named as a prerequisite the record owes the reviewer. The block's size stays undecided and no seed is allocated; status is provisional pending review, which is to see the floor and the table together. Journal §144. |
| 2026-11-02 | **The review package is finished and the request letter is written, unsent.** `docs/REVIEW-PACKAGE.md` now carries the feasibility result as a package component: the 48-world floor, the attenuation table (reliability 1.00 needs 48, 0.90 61, 0.80 79, 0.70 105, 0.60 144), the unmeasured reliability column and the exchangeability diagnostic, plus the pinned-commit command a reviewer runs instead of trusting the package. The brief lists the sign-resolution artifact and records that gate as discharged; the withheld-set enumeration is the one gate still outside the review. `docs/REVIEW-REQUEST.md` is the letter: all five bracketed fields are the sender's, nothing has been sent and no reviewer has been approached. The repository is public (HTTP 200, master at the commit this row names), so the letter points at the record rather than attaching it. Journal §145. |
| 2026-11-02 | **A machine pre-pass is available and cannot close the gate.** The owner asked why an independent human review is needed at all when another AI could do it. The answer is accountability, not capability: a model approves at no risk, cannot be cited as the reviewer, cannot refuse, and filling §7's affiliation, conflicts and signature fields from one would be a fabricated provenance. `docs/AI-REVIEW-PROMPT.md` is the prompt anyway - a cold model is a genuinely unanchored reader, it is free, and running it before the letter costs nothing. Its output is recorded as `docs/AI-REVIEW-<date>.md` and labelled machine review; a blocking finding is fixed and logged, a clean pass is recorded as a fact about one failure mode and not as a certificate. The brief gains §9 stating the four reasons. The review gate is unchanged and §7 remains empty. Journal §146. |
| 2026-11-02 | **A primer was written, and a partner cannot review.** The owner offered to sign the review himself, then proposed that his partner do it. Neither can: §2's exclusion of the owner is unchanged, and a partner has a stake in the result, which is the fifth eligibility rule - the conflict is the relationship, not a missing declaration, and recording it would make the review look independent while being the least independent reading available. The useful half of the request was "make it metabolisable": `docs/REVIEW-PRIMER.md` now explains the claim, both measurements, both hard parts and the 48-run floor in plain language, and it is the first thing the package, the brief and the request letter point at. Writing it cost nothing and lowers the price of a yes for every candidate. The gate is unchanged and §7 is empty. Journal §147. |
| 2026-11-02 | **The attenuation rule was wrong and is corrected; the dependence direction is withdrawn.** The owner's review found that the table multiplied the rank correlation by reliability, which is not the classical rule: under error in one variable the Pearson correlation is multiplied by sqrt(reliability), and the Spearman value then follows from the (6/pi) asin mapping. The corrected curve (computed by `observed_spearman`, checked by Monte Carlo to within 0.021) gives 1.00 -> 48, 0.90 -> 54, 0.80 -> 62, 0.70 -> 72, 0.60 -> 85, 0.50 -> 104, 0.40 -> 131, 0.30 -> 177 worlds per configuration; the old table overstated the loss (0.80 was 79, now 62). The floor claim is unaffected. Separately, the claim that dependence narrows the interval was untested and is withdrawn: the new simulation finds differences inside Monte-Carlo noise and not consistently signed, so the block measures the direction instead of assuming it. No engine ran and no seed was spent. Journal §148. |
| 2026-11-02 | **`DI` is a state at a designated time, and the protocol's 110–150 window is contested by the data it would be scored on.** The owner paused the sample-size discussion until the construct was settled, so [`docs/DI-CONSTRUCT-AUDIT.md`](DI-CONSTRUCT-AUDIT.md) answers his five questions from the 240 stored Phase L records, with `benchmarks/di_construct_audit.py` writing every quoted number to `docs/di_construct_audit.json` — no engine, no seed, no coefficient. `DI` is `late_retained / late_available` from one cycle's report (**per-cycle, not cumulative**: 1,598 single-cycle decreases across the 240 trajectories and only 122/240 non-decreasing), quantised in steps of 1/18 = 0.0556 because the denominator is 18 pairs. It is zero before arrival, still moving at the last cycle (mean 0.293 at cycle 599; per-arm median first-reach 424.5–586), and configuration-dominated only once settled (ICC 0.890 on cycles 400–600, arm label 98.5 % of between-run variance, four of eight arms at 0.000). **Applied to those records the protocol's window returns 240 identical zeros** — it is pre-arrival — and the matched 40-cycle post-arrival window returns 234/240 all-zero records with ICC 0.068, so the window measures the floor. Design §2 now records the window as **unresolved** rather than rewriting it. Five structural reasons make measurement error inseparable from developmental change in these records, and the estimator that would match a state at a time (parallel forms) has no second form in the data. No reliability coefficient computed; no seed allocated; review gate unchanged. Journal §149. |
| 2026-11-02 | **Stage A of the `DI` measurement window shows the endpoint's dynamic range, not only the window, is the obstacle.** The owner separated selecting a window from validating it, so [`docs/DI-MEASUREMENT-WINDOW.md`](DI-MEASUREMENT-WINDOW.md) answers his five Stage A questions from the 240 stored records, with `benchmarks/di_window_design.py` writing every number to `docs/di_window_design.json` — no engine, no seed, no coefficient, **no window adopted**. Emergence is arm-dependent (median first sustained non-zero 329 `6:1`, 362 `4:1`, 404 `3:1`, 539 `2:1`); the four late-disadvantaged arms produce one non-zero reading in 30 runs at the arrival boundary and none sustained, so **117 of 240 runs never leave zero** and those arms are out of scope for this endpoint. **The record contains no asymptote**: among the 119 runs that move, median settle is **586 of 600**, max 599, and 25–27 of 30 per arm are still changing in the last 50 cycles — so no cycle number is proposed, because any would encode where the run stopped. The larger finding is range: within-configuration SD never exceeds 2.02 pairs and is **0.44 pairs** at the settled window against a one-pair floor, with **at least 97 %** of predictor variance between configurations — the ICC of 0.890 is **not** a repeatability coefficient, and a within-configuration test would rest on about one pair of spread. A settled measurement plus the protocol's 50+50 cycles needs **686** cycles against a 150-cycle run. Stage A proposes a measurement *design* (longer runs, window after a demonstrated asymptote, two disjoint late-pair sets, spread reported beside every relation) and names the trajectory-summary alternative as a different construct needing its own audit. **Stage B is specified and not authorised**: no seed allocated, V1 and the 240 records untouched, window still unresolved, sample size still paused, review gate unchanged. Full suite green at this commit. Journal §150. |
| 2026-11-02 | **The primary candidate predictor becomes the *onset* of `DI`, and "settle" is separated into three criteria.** The owner made a transition summary primary and kept the settled state as a separate, unresolved construct, so [`docs/DI-TRANSITION-CONSTRUCT.md`](DI-TRANSITION-CONSTRUCT.md) audits the three candidates on measurement grounds only — **no behavioural endpoint is read**, so the choice cannot be outcome selection. Slope is not estimable from a record that may still be running (rank stability **-0.315** when the run is cut at cycle 450: the ordering reverses); exposure is defined for all 240 records but its value is defined relative to an integration interval whose length is exactly what is unresolved; **onset** is defined on a one-cycle grid, varies within `6:1` by 12.4 cycles (SD) over a range of 65, and cannot change because the run stopped early. Onset and exposure rank-correlate at -0.932, so choosing onset keeps the ordering and drops the interval dependence. **Correction to the row above:** its "0.44 pairs against a one-pair floor" compared a 40-cycle mean to a single-cycle quantum — 0.44 pairs is real spread (about eight quanta), so the dynamic-range conclusion is withdrawn and the decisive defect is that no settled state exists to measure. The three settling criteria are now separate: median persistence in a one-pair band is **13 cycles**, 17 of 119 runs reach 50 cycles and 4 reach 100, while **96 of 119** moved by at least two pairs over the final 100 cycles — so no asymptote is claimed, and Stage B must declare persistence **and** trend in advance. Stage B still not authorised; no seed, no world, V1 and the 240 records untouched. Journal §151. |
| 2026-11-02 | **The onset construct's operational definitions are closed, and the `1:x` arms are classified rather than dropped.** The owner endorsed onset and asked for three closures before authorisation, all now in [`docs/DI-TRANSITION-CONSTRUCT.md`](DI-TRANSITION-CONSTRUCT.md) §3. The event is the **first cycle of the qualifying sustained run**, not the first non-zero reading: 99 of 119 onsets coincide with it and **20 are later** (one by 279 cycles), the latest confirmation is cycle **598** of 600, **2353** interrupted attempts across 24 records do not move the anchor, a missing reading breaks the run (0 records contain one), and a run cut off before ten readings is censored rather than placed at the boundary. The sustention rule is swept: 5 gives 119 onsets with 3 moving by at most 25 cycles, 20 gives 117 with 1 moving by 13, so the rule does not manufacture the ordering. Eligibility is reported for **all eight** configurations — **240 records, 120 with sustained emergence, 120 without, 0 dropped** — and the claim is stated as *evaluated among configurations in which sustained structure emerges*. The 3-cycle SD criterion is evaluated **per configuration** with IQR, range and distinct values beside it; all four pass (smallest SD 12.4 against a 3-cycle floor, tightest defined share 0.967), and only 17-27 % of onsets sit within ±3 cycles of their configuration's median, so no clump is hiding behind the SD. **Stage B is still not authorised**: no seed, no world, no run. Journal §152. |
| 2026-11-02 | **The sustention sweep is checked on the ordering, and the behavioural clock is fixed before any Stage B run.** The owner accepted commit `20700aa` as a defensible completion of the Stage A construct work and asked for two last design items. (1) The sweep is now checked at the level of the predictor, not the median: within each claimed configuration the onset ordering is correlated across the 5-, 10- and 20-cycle rules — `6:1` and `4:1` are identical at ρ 1.000 with no inversions, `3:1` holds at ρ 0.979 with 10 of 435 orderings reversing and a worst rank shift of 9, `2:1` at ρ ≥ 0.972 with 5–10 inversions and a shift of 6. **No configuration's verdict changes** under either alternative rule, but **2 runs** defined at 10 are undefined at 20 (both `2:1`), so under a doubled rule that configuration sits at exactly **0.900** of the defined-share criterion — a marginal pass — which is the second reason the rule is frozen rather than swept at analysis time. (2) The behavioural clock is declared in §6.2: a **one-cycle** margin (the earliest legal cycle, since confirmation is the last reading the onset rule reads), the protocol's 50-cycle learning and 50-cycle test, so **100** cycles of follow-up identical in every world, with every observation reporting both its absolute cycle and its cycles since confirmation. The two clocks are deliberately separated: behavioural *opportunity* is equal, developmental *age* is not, and the record shows the span — first behavioural cycle **299–599** across the 119 moving runs. The cost is measured, not assumed: each run must extend through confirmation + 101, the slowest world in hand needs **699** cycles, and only **91 of 119** runs would fit the follow-up inside a 600-cycle run (`2:1`: **1 of 29**), so a Stage B horizon must be set per world from its own confirmation cycle — a fixed 600-cycle horizon would shorten the follow-up exactly for the worlds that emerged latest. Disjointness is verified rather than asserted: **0** behavioural cycles fall at or before a world's confirmation. **Stage B remains unauthorised** — no seed, no world, no run. Journal §153. |
