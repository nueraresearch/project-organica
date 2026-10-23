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
| Selection pressure understood | ❌ | **Measured: currently inert.** Cap binds 0/600 cycles; pool max 8 vs cap 15; policy changes only list *order* (§D1–D3). "Retention redesign required" was the assumption — it is not yet the blocker |
| Belief supply sufficient | ❌ | 6 real beliefs across 5 subjects; **53.8%** of hypothesis slots are inert markers; exactly **one** subject carries ≥2 beliefs, which is why there is exactly one theory (§D5–D6) |
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
| 1 | Is the retention policy a developmental force? | A measured difference between alphabetical and salience retention on M1–M9, with the cap binding in at least one arm | Research | **Belief supply (row 2)** — the experiment is degenerate until the pool can exceed the cap |
| 2 | Is the hypothesis cap the constraint, or is upstream belief supply? | `benchmarks/development_probe.py` cap census + a knob sweep showing which upstream gate limits the pool | Research | — |
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
1. Replace alphabetical retention → *engine change, in progress*
2. Establish belief supply so selection pressure can exist → *measured prerequisite for 3*
3. Freeze M1–M9 in a pre-registration → *must precede any run*
4. Run the Tier-1 matrix: `FULL` · `SALIENCE_RETENTION` · `NO_CONTRADICTIONS` · `NO_QUESTIONS` · `NO_DREAMS` · `ANTI_EIG`, 3,000 cycles each
5. Publish the before/after figure: alphabetical vs salience, cycle vs contradiction density, salience distribution, theory population
6. Build the experiment executor → *unlocks G5, makes EIG testable, lets a Question close*

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
