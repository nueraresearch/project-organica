# Organica — Gate Board

**Purpose.** One page that separates *demonstrated* from *assumed*, and names
the evidence each open gate still needs. A gate closes on a measurement, not
on an intention.

**Read with** `docs/FACTS-SHEET.md` — every status below cites a fact sheet
entry (`§C2`) or a committed artifact.

> **Guardrail.** The commercial rows below are **status only**. This file
> lives in a public repository. Do not add counsel advice, customer
> identities, pricing, or IP strategy here — keep those in private working
> notes and cite only the decision that is pending.

**Status key:** ✅ demonstrated · 🟡 partially demonstrated / in flight ·
❌ not demonstrated · ⛔ blocked

---

## Gate board

| Gate | Status | Evidence |
|------|--------|----------|
| Architecture exists | ✅ | 3,725 sleep cycles, counter monotonic 1…3725, 0 non-monotonic (`memory.db` → `sleep_cycles`) |
| Usable by a stranger | ✅ | Fresh clone passes 8/8 checks, 17 pytest, 9/9 examples (`docs/clone_check.json`) |
| Lineage integrity | ✅ | 138/138 candidates grounded, 100%, 0 unverifiable (`docs/lineage_audit.json`) |
| Substrate endurance | ✅ | 3,725 cycles without leak or regression; log archived 8.36 MB (`logs/organica_prefix_20261022.log`) |
| Ablation campaign complete | 🟡 | **V1 complete** — 11 conditions, mechanism-verified, 6 disclosed measurement defects. V2 (Tier-1 forces) pending |
| Development observed | 🟡 | G1/G4/G6/G7/G8 bootstrap unassisted; G5 never does. But the population is **degenerate**: 1 theory, 1 question, and **flat from cycle 261** (§B2) |
| Contradiction is developmental fuel | ❌ | Never isolated. Raw contradiction grew 0 → 400,550 with **no** population change (§B4). The causal question is untested |
| Selection pressure understood | 🟡 | **Was ❌ "measured inert."** The cap did not bind because the belief pool was starved by a **mis-scoped counter** — see the G-P1 update below. Corrected: the branch stimulus now holds **18 beliefs against a cap of 15**, pressure **1.20**, sustained |
| Belief supply sufficient | ✅ *(on the branch stimulus)* | **Was ❌ "6 real beliefs across 5 subjects; exactly one subject carries ≥2 beliefs."** That was partly an artifact of the same defect. Measured now: **18 beliefs, 7 competing subjects, 5 theories, 100% of tail cycles** (`docs/gate_check.json`) |
| Evidence flow measured | ❌ | Every developmental metric is a count, so the flat-population / growing-evidence divergence is invisible to the metric suite (§G3) |
| Experiment executor exists | ❌ | No executor → no Question ever closes, EIG can never pay off, `cy`/`eig_star` structurally unmeasurable (§G1) |
| Cross-domain transfer | ❌ | Level 1 measured-negative; uncertainty 0.0 in 3 of 4 validation domains (§B6) |
| **Commercial** rights understood | ❌ | Counsel required. Pending: entity · IP ownership · open-source licence position · authorization memo |
| **Commercial** customer problem validated | ❌ | Interviews pending. No customer conversation has been run |

---

## Gate G-P1 — retention pressure (precondition for any retention experiment)

**Question.** Can the retention layer be forced to make a choice? A policy
that ranks a list it never truncates cannot matter, no matter how good the
ranking is.

**Measure.** For each retained object type,
`retention_pressure = pre_cap_pool_size / cap`, over ≥ several hundred cycles.

| Layer | cap | pool mean | p95 | pressure mean | pressure p95 | G-P1 |
|---|---:|---:|---:|---:|---:|---|
| loops | 15 | 936 | 936 | 61.1 | 62.4 | ✅ strong |
| predictions | 20 | 598 | 621 | 29.9 | 31.1 | ✅ strong |
| anomalies | 10 | 292 | 309 | 29.2 | 30.9 | ✅ strong |
| processes | 10 | 11.8 | 13 | 1.18 | 1.30 | ⚠️ weak |
| dreams | 8 | 8.3 | 12 | 1.04 | 1.50 | ⚠️ borderline |
| investigations | 5 | 8.8 | 11 | 1.77 | 2.20 | ✅ useful |
| experiments | 5 | 4.9 | 5 | 0.98 | 1.00 | ❌ none |
| workflows | 10 | 9.1 | 10 | 0.91 | 1.00 | ❌ none |
| meta_concepts | 15 | 9.0 | 9 | 0.60 | 0.60 | ❌ none |
| **hypotheses** | 15 | **5.3** | 8 | **0.35** | 0.53 | ❌ **FAILS** |
| questions | 6 | 1.2 | 3 | 0.19 | 0.50 | ❌ none |
| theories | 8 | 1.2 | 3 | 0.14 | 0.38 | ❌ none |

**Pass condition for the P1 retention experiment:** pressure > 1.0 on the
object being retained.

**Current status: ❌ FAILS for hypotheses.** `MAX_HYPOTHESES` is **INERT**
in the parameter influence map — raising it 15 → 40 changes nothing at all.
"Full vs salience" would compare two identical colonies.

> ### ✅ UPDATE 2026-10-23 — the failure was a *measurement* defect, and it is fixed
>
> The pressure was 0.35 because the belief pool genuinely held 5–8 beliefs
> against a cap of 15 — **and** because the belief pool was being
> **starved by a mis-scoped denominator**.
>
> `MemoryService.store()` builds the co-occurrence and temporal graphs from
> **world events only** (`if event_type != "sleep"`). But the tag-frequency
> counter was maintained for **every** stored event, including the
> organism's own sleep payloads — and that counter is the denominator of
> the Layer-1 edge strength:
>
> ```
> ratio    = count / max(source_freq, 1)      # count  = world edge count
> strength = min(1.0, ratio)                   # source_freq = ALL events
> ```
>
> So the numerator and the denominator measured different populations, and
> a prediction candidate only survives into `stable_prior` when its
> strength clears `STABLE_THRESHOLD = 0.3`. The world's own edges were
> being discarded in favour of whatever the organism happened to say about
> itself.
>
> **Measured, on a branch stimulus:** before the fix, 4 surviving edges
> (2 of them schema tags), 0 processes, 0 workflows, 0 beliefs. After the
> fix, a full 20-edge window, **18 beliefs**, **7 competing subjects**, and
> **100% of tail cycles passing every gate.**
>
> Fix: the counter is now scoped to world events, like the graph it
> normalises. `docs/freq_scope_probe.json` · journal §21.

### ✅ The gate re-run — G-P1 is now PASS

`benchmarks/gate_check.py` → `docs/gate_check.json`. 300 cycles per
stimulus, real substrate, gates evaluated on the **pre-retention** pool so
they do not depend on the arm under test.

| stimulus | belief pool mean/max | subjects ≥2 mean/max | theories mean/max | tail cycles passing every gate | result |
|---|---|---|---|---:|---|
| study stream *(control)* | 5.17 / 6 | 1.00 / 1 | 1.06 / 3 | 0% | ❌ fails, as expected |
| `branch_r4` | **18.00 / 18** | **7.00 / 7** | 5.41 / 6 | **100%** | ✅ **all gates pass** |
| `lattice_L1` *(3 disjoint triangles)* | **17.99 / 18** | **6.99 / 7** | 4.91 / 5 | **100%** | ✅ **all gates pass** |
| `lattice_L3` *(3 triangles, one shared petal)* | 16.00 / 16 | 6.00 / 6 | 4.98 / 5 | **100%** | ✅ **all gates pass** |

G-CS ✅ · G-P1 ✅ · G-SUP ✅ · G-EXP ✅ · G-SUS ✅ on all three branch
stimuli. **The launch gates are closed.** The matrix is unblocked.

**One result in that table matters for the campaign, and it is a
prediction confirmed.** The pre-retention competing-subject count is 7, but
the **post-retention** count is 5–6. The retention policy therefore
*does* change how many subjects compete — on a substrate where the cap
binds. That is the P1 arm's hypothesis, and it is now measurable. Under
the old, defective substrate the policy provably could not matter.

---

## Gate G-CS — competing-subject supply *(primary gate; validated 2026-10-23)*

> **At least 3 subjects hold ≥2 active beliefs**, reaching **5–7** at some
> point in the run.

This gate was **proposed** as *Multi-Belief Subject Density* and then
**validated against the 11 existing V1 conditions** before any stimulus
code was written (`benchmarks/gate_validation.py`,
`benchmarks/mbsd_census.py`, journal §20).

**The validation came back stronger than proposed, and the form changed.**

> **Layer 5 forms exactly one theory per subject holding ≥2 beliefs,
> capped at `MAX_THEORIES`.**
> The identity `theories == min(competing_subjects, 8)` holds in **100% of
> cycles in 9 of the 11 conditions** — 99.7% in Random Sleep, and 18.0%
> in No-Hypothesis-Layer, the one condition that bypasses Layer 4 by
> design and builds **6 theories with zero competing subjects**.

So the numerator of the proposed gate is not a *predictor* of theory
formation — it **is** the mechanism. Two consequences:

1. **The density ratio adds nothing beyond the absolute count.** The gate
   is stated as a count; density is kept only as a reported statistic.
2. **A second cap was found, in the same family as the first.**
   `MAX_THEORIES = 8` caps theory capacity. A stimulus producing more
   than 8 competing subjects would push the surplus *invisible* to M1, M8
   and M9 — the same blind spot as the hypothesis cap, one layer up. That
   is why **G-EXP** exists below.

**Current status: ❌ FAILS on the study stream** — 1 competing subject
(mean 1.37, max 4); only "session" ever competes.

### The MBSD census — every V1 condition, exact density with its denominator

`benchmarks/mbsd_census.py` → `docs/mbsd_census.json`. Every V1 condition
class was re-run **verbatim** (300 cycles) with an instrument that records
the belief pool *before* retention, so the density has a real denominator.

| Cond | Intervention | subjects mean/max | subjects ≥2 mean/max | MBSD | belief pool mean/max | pressure mean | ≥3 abs | ≥0.50 dens | G-P1 |
|------|--------------|---|---|---:|---|---|:--:|:--:|:--:|
| **O_FULL** | reference | 3.53 / 5 | 1.39 / **3** | 0.392 | 4.92 / 8 | 0.33 | ✅ | ❌ | ❌ |
| A | No Sleep | — | — | — | — | — | — | — | — |
| B | No Lineage | 3.53 / 5 | 1.39 / **3** | 0.392 | 4.92 / 8 | 0.33 | ✅ | ❌ | ❌ |
| C | No Curiosity | 3.47 / 5 | 1.91 / **3** | **0.550** | 5.37 / 8 | 0.36 | ✅ | ✅ | ❌ |
| D | No Falsification | 0 / 0 | 0 / 0 | 0.000 | 0 / 0 | 0.00 | ❌ | ❌ | ❌ |
| E | No Dreams | 4.27 / 5 | 0.07 / 1 | 0.016 | 4.33 / 6 | 0.29 | ❌ | ❌ | ❌ |
| F | No Hypothesis Layer | — | — | — | — | — | — | — | — |
| G | No Questions | 5.00 / 5 | 1.49 / **3** | 0.299 | 6.49 / 8 | 0.43 | ✅ | ❌ | ❌ |
| H | Random Curiosity | 5.00 / 5 | 1.95 / 2 | 0.389 | 6.95 / 7 | 0.46 | ❌ | ❌ | ❌ |
| I | Random Sleep | 0 / 0 | 0 / 0 | 0.000 | 0 / 0 | 0.00 | ❌ | ❌ | ❌ |
| J | Memory Without Structure | 0 / 0 | 0 / 0 | 0.000 | 0 / 0 | 0.00 | ❌ | ❌ | ❌ |

*A and F bypass Layer 4 by design, so there is no belief pool and MBSD is
undefined; F's 6 theories come from a different route entirely.*

**What the census adds to the validation:**

1. **The gate has never been met, even as a peak, in a way that would
   make a campaign meaningful.** The ≥3-subject form is touched by 4 of
   the 9 measurable conditions (O_FULL, B, C, G); the **≥5** form is met
   by **none**. Mean competing subjects never exceeds **1.95**.
2. **C (No Curiosity) is the only condition that reaches density ≥ 0.50.**
   Removing curiosity *raises* belief density — the same direction as
   V1's C row, now visible at the density level.
3. **B (No Lineage) reproduces O_FULL exactly** on every belief metric
   (3.53 subjects, 1.39 ge-2, 0.392 density, pool 4.92). The V1 control
   holds at the density level too.
4. **E (No Dreams) has the most subjects and almost no competition**
   (4.27 subjects, 0.07 with ≥2). Dreams are load-bearing for
   *competition*, not for subject count.
5. **H (Random Curiosity) has the highest mean (1.95) but never reaches
   3.** A better mean does not mean the gate is close.
6. **D, I and J produce no beliefs at all** in 300 cycles.

**Conclusion.** No existing condition supplies the competing expectations
the theory layer needs. The stimulus must be built; it cannot be found.

### The derived design target

Not more tags. Not more volume. **5–7 subjects, each with 2–3 competing
successors**, spread so the belief pool crosses 15:

| Target | Value | Why |
|---|---|---|
| competing subjects | **5–7** | ≥3 is the proposed bar; ≤7 keeps the theory layer below `MAX_THEORIES = 8` so M8/M9 can see it move |
| beliefs per subject | 2–3 | 2 gives a theory, 3 gives a real question (entropy over a 3-way split) |
| belief pool | **12–24** | must cross 15 for G-P1 to pass |

### Gate G-EXP — theory layer unsaturated

> `max(cycles with theories) < MAX_THEORIES` — so the theory population is
> never clipped, and M8/M9 can see it move.

Added because the validation surfaced `MAX_THEORIES = 8` as a second cap
with the same failure mode as the hypothesis cap. A campaign that cleared
G-CS and G-P1 but saturated the theory layer would be **silently blind in
exactly the way G-P1 exists to prevent**.

### The finding that reframes the whole hierarchy

**The organism is supply-limited, not selection-limited.** The scarce
resource is not vocabulary — it is **competing expectations about the same
subject**. 42 world tags → 1 theory; 97 world tags → 0 theories. More
diversity *reduced* theory production.

**The finding that reorders the plan:** the organism is **starved, not
selective**. Layer 1 discards ~99% of its own candidates (pressure 29–61×)
while Layer 4 has 5–8 beliefs for 15 slots (pressure 0.35). The caps are
mismatched, and every over-truncated layer retains by a *popularity* rule —
raw temporal count for predictions, strength for loops, dominance ratio for
anomalies. The alphabetical hypothesis rule is the same defect three layers
downstream, and it is invisible only because there is nothing left to
choose between.

Source: `benchmarks/instrumentation_audit.py` → `docs/instrumentation_audit.json`.

---

## Gate ladder G1–G4 — did each ablation actually perturb anything?

```
G1  the ablation perturbed the code path
G2  the ablation perturbed the candidate pools
G3  the ablation perturbed the final outputs
G4  the ablation perturbed the developmental metrics
```

An ablation that changes no output cannot change a metric for any reason
about cognition. Scored from `docs/ablation_study.json` +
`docs/ablation_verification.json`.

| Cond | Intervention | G1 | G2 | G3 | G4 | Reading |
|------|--------------|:--:|:--:|:--:|:--:|---------|
| A | No Sleep | ✅ | ✅ | ✅ | ✅ | foundational — everything to zero |
| **B** | **No Lineage** | ✅ | ✅ | **❌** | ❌ | **the control.** Populations *identical*; the only metric that moved is `lc`, the metric that measures the thing that was removed. Every cognitive delta is exactly 0.000. The ladder working as intended |
| C | No Curiosity | ✅ | ✅ | ✅ | ✅ | EIG is the *only* producer of investigations and experiments — and removing it **raises** theories 1→3, hypotheses 13→15, questions 1→3 while the two output layers go to zero. It passes G4, but **in the wrong direction** |
| D | No Falsification | ✅ | ✅ | ✅ | ✅ | freezes rather than bloats; contradiction duty 61%→5% |
| E | No Dreams | ✅ | ✅ | ✅ | ✅ | dreams carry the upper ladder; removing them collapses processes and workflows to zero |
| F | No Hypothesis Layer | ✅ | ✅ | ✅ | ✅ | bypassing G4 gives **6** theories vs 1 — the layer was suppressing theory formation |
| G | No Questions | ✅ | ✅ | ✅ | ✅ | questions → 0; investigations and experiments survive. The gateway is dreams, not questions |
| H | Random Curiosity | ✅ | ✅ | ✅ | ✅ | Jaccard 0.111 vs EIG — genuinely different selection, yet no developmental gain |
| I | Random Sleep | ✅ | ✅ | ✅ | ✅ | random *structure* recovers most of the aggregate; shape beats content |
| J | Memory Without Structure | ✅ | ✅ | ✅ | ✅ | foundational — everything to zero |

**Read the EIG row carefully.** EIG passes all four rungs, so the
"no measurable gain" result is **not** a measurement artifact — it is a
real finding. EIG is a perfect ranker (top-k precision 1.000 vs random
0.584) that buys nothing measurable, and removing it makes the organism
look *better* on every structural metric. A perfect selector over a
starved candidate pool cannot matter: there is nothing for selection to
choose between.

---

## Parameter influence map — 8 of 14 knobs do nothing

`benchmarks/instrumentation_audit.py`, 400-cycle baseline, one variant each.

| Verdict | Parameters |
|---|---|
| **DECISIVE** (changed final outputs) | `DEATH_THRESHOLD` · `STABLE_THRESHOLD` · `MAX_PROCESSES` · `MAX_PREDICTIONS` |
| **POOL_ONLY** (changed the pool; the cap hid it) | `PREDICTION_MIN_COUNT` · `LOOP_MIN_STRENGTH` |
| **INERT** (changed nothing at any level) | `MAX_HYPOTHESES` · `MAX_WORKFLOWS` · `MAX_META_CONCEPTS` · `WORKFLOW_MIN_MATCHED_METAS` · `META_CONCEPT_MIN_REFS` · `CONCEPT_MIN_DEGREE` · `CONCEPT_MIN_REACH` · `PHRASE_MIN_CLUSTERING` |

A parameter that never changes an output should not have a row in an
experiment plan. **The two the P1 campaign was built around —
`MAX_HYPOTHESES` and the hypothesis retention rule — are both inert.**

---

## Decision backlog

Each row is a decision we are carrying without evidence. Closing a row means
producing the named artifact — not writing a plan.

| # | Decision we are carrying | Evidence that closes it | Owner | Blocked by |
|---|--------------------------|--------------------------|-------|------------|
| 1 | Is the retention policy a developmental force? | A measured difference between alphabetical and salience retention on M1–M9, with the cap binding in at least one arm | Research | **Gates G-CS + G-P1 + G-EXP.** The gate is now *validated* (journal §20) and the design target derived: 5–7 competing subjects, 2–3 beliefs each, belief pool > 15. |
| 2 | Is the hypothesis cap the constraint, or is upstream belief supply? | **CLOSED.** `benchmarks/development_probe.py` cap census + a knob sweep. Answer: neither the cap nor any single threshold — the constraint is the number of *distinct reciprocal structures* the stimulus contains. | Research | — |
| 3 | Is contradiction developmental fuel or bookkeeping? | `NO_CONTRADICTIONS` colony vs `FULL`, scored on M1–M9 with the same frozen definitions | Research | Row 4 |
| 4 | Does curiosity require explicit unresolved questions? | `NO_QUESTIONS` colony vs `FULL` | Research | Metrics frozen (row 6) |
| 5 | Is EIG orthogonal to current development? | `ANTI_EIG` colony vs `FULL` — select the *lowest*-scoring candidates | Research | Metrics frozen (row 6) |
| 6 | Which metrics count development? | M1–M9 frozen in a pre-registration **before** the run, with the stoplight interpretation | Research | — |
| 7 | Does the 90-day horizon buy anything? | Closed: **no.** The run plateaued at cycle 261 with zero variance for 3,464 cycles | Research | — |
| 8 | Is the organism's own output polluting its input? | 60.6% of tag occurrences are its own JSON field names (§D8). Decide: exclude stored candidates from tag extraction, or accept and document | Research | — |
| 9 | Entity and IP ownership | Counsel memo covering entity · IP ownership · OSS licence · authorization memo | Commercial | — |
| 10 | Is there a customer problem worth removing? | 5 conversations measuring pain intensity · current workaround · budget ownership · urgency | Commercial | — |

---

## Priority queue

### Track A — Research
1. ~~Replace alphabetical retention~~ → **done** (engine change, 2026-10-23; measured effect on current behaviour: none, because the cap does not bind)
2. **Validate the gate against existing data** → **done** (journal §20: the theory count *is* the competing-subject count, 100% of cycles in 9/11 conditions; the gate is reformulated as a count and a fourth gate, G-EXP, added for `MAX_THEORIES = 8`)
3. **Freeze M1–M9 + the gates** → `docs/FORCE-MATRIX-PREREGISTRATION.md`, committed before the run. Five gates now: G-CS, G-P1, G-SUP, G-EXP, **G-SUS** (sustained, not peaked)
4. ~~**Design the branch-structured stimulus**~~ → **done** (journal §21.7: the unit of competing expectation is a *triangle* — a 3-cycle — because that is the only thing a workflow is built from. Three disjoint triangles give 7 subjects × 2 beliefs and 18 beliefs total, which is exactly the derived target)
5. ~~**Re-run the gates** on the chosen stimulus~~ → **done** (journal §21.8 + `docs/gate_check.json`). The re-run found the *cause* of the earlier failure: a mis-scoped denominator in the substrate, not the stimulus
6. **Run the Tier-1 matrix**: `FULL` · `SALIENCE_RETENTION` · `NO_CONTRADICTIONS` · `NO_QUESTIONS` · `NO_DREAMS` · `ANTI_EIG`, 3,000 cycles each
7. Publish the before/after figure: alphabetical vs salience, cycle vs contradiction density, salience distribution, theory population
8. Build the experiment executor → *unlocks G5, makes EIG testable, lets a Question close*

### Track B — Commercial
1. Facts sheet → **`docs/FACTS-SHEET.md`**
2. Gate board → **this file**
3. Counsel engagement → closes row 9
4. OpenAI agreement review → *status only here*
5. AWS request → *status only here*
6. Five customer conversations → closes row 10

### Explicitly absent from both queues
New features · new dream types · new models · new agents. Both tracks have
reached the stage where **understanding the system is worth more than
expanding it** — ignorance, not capability, is the binding constraint.

---

## Adjacent open risk (other project)

Not tracked here, but live and time-sensitive: a preprint in a **different**
project is staged for prior-art deposit while claiming a measured
performance figure that does not exist in that project's source documents.
Deposit should wait until that claim is corrected to the *specified*
threshold. Flagged, not tracked, in this repository.

---

## Revision log

| Date | Change |
|------|--------|
| 2026-10-22 | Board created. Statuses set from `docs/FACTS-SHEET.md` §A–§G. "Selection pressure understood" downgraded from "retention redesign required" to **measured inert** (§D1–D3). "Development observed" downgraded from ✅ to 🟡 on the degeneracy of the G5 population (§B2, §D5–D6). |
