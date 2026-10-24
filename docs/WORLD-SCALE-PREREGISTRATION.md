# The H24 World-Scale Ladder — Pre-registration

**Status: PILOT RAN — DESIGN REVISED. 2026-10-23.**

The 300-cycle pilot completed for Rungs 0, 1, and 2 (Rung 3 was stopped;
see §7 for the full account). The pilot produced a clean, measured result
that **invalidates the original ladder design** and replaces it with a
mechanism-derived one. The decision rule in §2 does not change. The new
design is in §8.

The original pre-registration (§1–§6) is preserved unchanged below. §7
is the pilot result. §8 is the revised ladder. Nothing in §1–§6 has been
edited to match the result.

The hypothesis itself is stated in
[`FORCE-MATRIX-RESULTS.md`](FORCE-MATRIX-RESULTS.md) §11 and
[`FACTS-SHEET.md`](FACTS-SHEET.md) §J, with the evidence on both sides.

---

## 1. H24

> **Organica's apparent developmental plateau is primarily constrained by
> environmental information content rather than by architectural inability to
> reorganise.**

The Tier-1 matrix measured a nine-event world in which every arm reached its
complete structural configuration on cycle 1 and then accumulated evidence for
2,999 cycles. H24 says that is what you would expect from a *finite*
environment, and that the organism's apparent ceiling is the world's ceiling,
not the architecture's.

**What would falsify it:** a larger, non-repeating world still produces ~74
distinct structures, the same plateau, and the same attractor.

---

## 2. The decision rule, fixed in advance

The measurement that matters is the **inventory** — the number of distinct
items (beliefs, questions, dreams, experiments) the organism has ever
discovered. It is scale-invariant; the M5 *rate* is not, and M5 has already
been shown to measure a finite inventory divided by the run length.

| Inventory across the ladder | Reading |
|---|---|
| **grows** with the world's information content | H24 **supported**: the plateau was an environmental artefact, and what this project found is a developmental system inside a toy universe |
| **flat** across the ladder | H24 **falsified**: the ceiling is architectural, and the honest conclusion becomes *the organism cannot reorganise beyond what a nine-event world teaches it, no matter how much novelty it is given* |
| grows then saturates | **partial**: the environment was binding at small scale, and an architectural ceiling binds at large scale. The rung at which it saturates is then the finding, and the layer census at that rung says which layer is the ceiling |

The third row is the most likely, and it is why the layer census is measured
at every rung and not only the inventory.

---

## 3. Structural constraints measured BEFORE the design was fixed

These are recorded because they changed the design, and because a design
that ignores them measures the caps rather than the environment.

### 3.1 The Layer-1 survival threshold caps hub degree

`benchmarks/hub_degree_probe.py` → `docs/hub_degree_probe.json`. One hub
shared across N triangles, 200 cycles each, threshold 0.3:

| Hub degree | hub's best edge ratio | beliefs | pre-retention beliefs | competing subjects |
|---:|---:|---:|---:|---:|
| 1 | 1.000 | 6 | 6 | 3 |
| 2 | 1.000 | 12 | 12 | 5 |
| **3** | **0.751** | **15** | **17** | **6** |
| 4 | 0.561 | 13 | 13 | 5 |
| 5 | 0.440 | 9 | 9 | 3 |
| 6 | 0.354 | 2 | 2 | 0 |
| 8 | 0.310 | 8 | 8 | 2 |
| 12 | **0.185** | 0 | 0 | 0 |

Structure is **best at degree 3** and the usable range is narrow. By degree
12 the hub's best edge ratio (0.185) falls below `STABLE_THRESHOLD` (0.3)
and the structure collapses to **nothing** — no beliefs, no competing
subjects, no theories.

**Consequence for the ladder:** a rung must not scale by the *degree* of one
hub. It scales by the number of hubs, each of degree 3.

### 3.2 The prediction window caps how much structure is visible at once

`MAX_PREDICTIONS = 20`. Layer 1 ranks temporal edges by count and keeps the
top 20; the Layer-2 process builder finds 3-cycles *among those 20*.

The ranking is by **count**, so when many triangles are equally frequent the
top 20 is an arbitrary subset of them. A 3-cycle needs three specific edges
(`h→a`, `a→b`, `b→h`), so an arbitrary subset usually contains no complete
triangle — and with no complete triangle there is no process, no workflow,
and no belief.

Measured on the ladder's first draft (4 hubs × 3 triangles = 48 edges, of
which 20 survive, ≈5 edges per hub): **competing subjects fell from 5.98 to
1.50.** More structure in the world produced *less* structure in the
organism.

**Consequence for the ladder:** the world must not present many equally
frequent triangles at once. The rungs below are built so that a small number
of structures are *frequent* and the world then *adds* new ones — never many
equally-weighted ones competing for 20 slots.

### 3.3 A tag must be at least four letters

The engine extracts tags with `re.findall(r"\b[a-zA-Z]{4,}\b", ...)`. The
first version of `organica/scale_streams.py` numbered its leaves (`ta0`),
every one of them was silently invisible, and the ladder measured nothing
and looked like a null result. Caught by checking that the perturbation
happened before reading the result. Tags are now spelled in letters, and
the rule is in `AGENTS.md`.

---

## 4. The ladder

The rungs below are **hypotheses about the world**, not the final design.
A **pilot at 300 cycles** must run first and must show that the gates still
pass at every rung before the full run is committed. The pilot's result
decides whether the rungs are the ones that get run; the decision rule in §2
does not change.

| Rung | World | Distinct structure offered | Predicted inventory if H24 holds |
|---|---|---|---|
| 0 *(measured)* | `lattice_L1` — 3 triangles on one hub, repeating | 3 triangles, 9 distinct events | **74** |
| 1 | **medium**: 3 frequent triangles on one hub, plus 1 new triangle introduced per 100 cycles | grows linearly with the run | ≫ 74, no plateau |
| 2 | **large**: 3 frequent triangles on one hub, plus 1 new triangle per 20 cycles | grows faster | ≫ rung 1 |
| 3 | **open-ended**: a new triangle every cycle, never repeated | unbounded | unbounded growth, no plateau |

The "frequent core" in rungs 1–3 is what keeps the top-20 window populated
with *complete* triangles (§3.2) while new structure keeps arriving. The
frequent core is what the organism can actually see; the arriving
structure is what the world offers that it has never seen.

**What is measured at every rung**, on the reference arm, with the same
protocol, the same seed and the same `PYTHONHASHSEED=0` pinning the campaign
used:

1. **The inventory**, and its per-category breakdown — the primary quantity.
2. **The cumulative discovery curve**, and the cycle at which 95% and 99% of
   the inventory was reached.
3. **The competing-subject count** (MBSD) and the belief supply.
4. **Theories, questions, dreams, experiments** (means and populations).
5. **Cognitive revolutions** (M9) — currently structurally zero, and a
   non-zero value would itself be a result.
6. **The layer census** — which layer's cap binds at each rung, so that a
   saturating inventory is attributed to a cause rather than observed
   without one.

**A pilot first.** 300 cycles per rung, all four, before anything is
committed. The pilot's job is to establish that the perturbation happened
(beliefs form at all, the inventory is non-zero, the discovery curve rises
and does not immediately flatten) — not to decide H24.

---

## 5. Why this is a stimulus experiment and not an architecture change

The standing rule is unchanged: **finish learning what V1 can teach before
changing the architecture.** Nothing in `organica/sleep.py` or
`organica/memory.py` changes for this experiment. The caps are not raised.
If the ladder saturates because a cap binds, that is the *finding*, and the
right response to a cap-limited result is a recorded decision about the
cap — taken afterwards, on the evidence, and disclosed.

**This experiment cannot settle H24 if it saturates at every rung.** It can
only report that the environment is not the binding constraint, and name the
layer that is. That is a real result, and it is the result that would move
the project toward an architectural review.

---

## 6. What is NOT being claimed

- Not that Organica is developmental in the strong sense. It is not
  established, and this experiment does not establish it.
- Not that the Tier-1 plateau was an artefact. It might have been a genuine
  architectural ceiling in a world that happened to be small. The ladder
  exists to find out which.
- Not that the ladder's own rungs are the right ones. The pilot decides
  that.

---

## 7. The pilot result — MEASURED 2026-10-23

### 7.1 The finding

Protocol: 300 cycles per rung, `colony=FULL`, `seed=20261023`, same engine
and same protocol as the Tier-1 matrix. Rung 3 (`mode=open`) was stopped
early due to a bootstrapping defect (§7.3); Rungs 0–2 are complete.

| Rung | World | Distinct triangles | Total inventory | Beliefs | Questions | Theories | Dreams | New in last 100 cycles |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **0** | `lattice_L1`, repeating | **3** | **91** | 17 | 10 | 10 | 52 | 3 |
| **1** | 4 hubs × 3 triangles, repeating | **12** | **66** | 12 | 4 | 4 | 28 | 0 |
| **2** | 16 hubs × 3 triangles, repeating | **48** | **56** | 10 | 4 | 4 | 24 | 0 |

**The finding, stated without interpretation:**

> Increasing environmental variety (3 → 12 → 48 distinct triangles) while
> holding Layer-1 capacity fixed (`MAX_PREDICTIONS = 20`) **decreased**
> total inventory (91 → 66 → 56), theories (10 → 4 → 4), questions
> (10 → 4 → 4), and dreams (52 → 28 → 24). Discovery ceased entirely in the
> final 100 cycles for Rungs 1 and 2 (`new_in_last_100_cycles = 0`).

This is a measured fact. The simple version of H24 — *more world → more
development* — is **not supported** by this data.

**What this does not say:**

- It does not say H24 is false. H24 says the plateau is constrained by
  environmental information content. That hypothesis is *compatible* with
  the world having a structure requirement as well as an information
  requirement. The pilot tested one kind of world scaling (uniform variety);
  H24 could still hold for a different kind (structured scaffolding with
  incremental novelty).
- It does not say the architecture has no ceiling. The pilot cannot
  separate "wrong stimulus shape" from "architectural ceiling" because it
  did not test a stimulus with the right shape.

### 7.2 The mechanism hypothesis — proposed, not yet tested

The finding is consistent with the following mechanism, which is stated as
a hypothesis to be tested, not as a conclusion:

> **Frequency dilution through `MAX_PREDICTIONS = 20`.** When many
> triangles are presented with uniform frequency, their 3 × N directed
> edges compete equally for the top-20 prediction slots. A complete 3-cycle
> requires all three of its specific edges to survive simultaneously; an
> arbitrary top-20 subset of N equally-weighted triangles will usually
> contain no complete triangle. Without complete 3-cycles no process forms,
> without processes no workflow forms, without workflows no belief forms,
> without beliefs no competing subjects exist, and without competing
> subjects no theories or questions form.

The chain:

```
uniform high-variety world
  ↓ MAX_PREDICTIONS = 20 (top edges by count)
  ↓ frequency dilution: many triangles equally frequent
  ↓ no complete 3-cycle survives into the top-20 window
  ↓ no process, no workflow, no belief
  ↓ fewer competing subjects
  ↓ fewer theories, questions, dreams
  → inventory decreases
```

**What supports it:**

- K2 (pre-registered structural constraint, measured before the pilot):
  with 4 hubs × 12 triangles, competing subjects fell from 5.98 to 1.50
  under exactly this mechanism.
- The pattern of the pilot: beliefs fell fastest, and beliefs are the
  earliest layer that the 3-cycle requirement gates. If the collapse were
  architectural rather than stimulus-structural, later layers would
  degrade differently than earlier ones.
- Rung 2 has 16× more triangles than Rung 0 and produces 41% fewer
  beliefs. Rung 1 has 4× more and produces 29% fewer. The degradation is
  monotone with world size in the uniform-frequency regime.

**What would directly test it:**

A world where the *same three triangles repeat frequently* (so complete
3-cycles always dominate the top 20) while *additional triangles arrive
infrequently* (so the world's information content grows). If beliefs and
theories track the rare arrivals, frequency dilution was the mechanism.
If they do not, something else is the ceiling. This is the design of the
revised ladder (§8).

**What has not been tested:**

- Whether raising `MAX_PREDICTIONS` allows a uniform high-variety world to
  be learned. If the dilution mechanism is correct, doubling the window to
  40 should allow Rung 1 to approach Rung 0's inventory.
- Whether the deficit is in *discovery* or in *retention*. It is possible
  that many 3-cycles are briefly completed but do not survive the
  strength threshold, producing the same surface result from a different
  internal cause.

The mechanism hypothesis is recorded here because it drove the revised
design. It is not confirmed.

### 7.3 The Rung 3 bootstrapping defect — disclosed

`scale_ladder.py` builds the complete event stream for a rung and then
dumps the entire list to `memory.db` under `seed:bootstrap` before any
sleep cycle runs. For Rungs 0–2 (`mode=block`) this is 36–576 events — a
normal bootstrap. For Rung 3 (`mode=open`, 300 cycles × 8 events = 2,400
events needed) the script pre-generated 8,100 triangles = 24,300 events
and dumped all of them before cycle 1.

**Why this is wrong.** An open-ended world is supposed to deliver fresh
structure cycle by cycle, so the organism encounters novelty progressively.
Dumping 24,300 events into bootstrap:

1. Flooded the engine's candidate generation: by cycle 35 the database held
   283,437 phrase-candidate events (~8,000 per sleep cycle) and latency
   had risen from ~200 ms to >25 seconds per cycle, making 300 cycles
   impractical.
2. Violated the definition of the rung: the world was not open-ended in
   experience; it was a batch dump that the organism processed as an
   arbitrarily ordered past.

The defect is in the runner, not in the engine or the stream generator.
The revised runner (§8) delivers events to `seed:bootstrap` only for the
first repeating block of each world, then feeds the rest cycle by cycle.

---

## 8. The revised ladder — mechanism-derived

The pre-registered ladder (§4) assumed that uniform variety was the right
axis of scaling. The pilot (§7) measured that it is not: uniform variety
dilutes the prediction window and *decreases* development. The revised
ladder tests the mechanism's own prediction: a **stable scaffold** plus
**incremental novelty** should allow the organism to keep discovering as
the world grows, because the scaffold keeps complete 3-cycles in the top-20
window while the arriving structure is genuinely novel.

This is no longer an arbitrary design choice. It is a mechanism-derived
experiment with a pre-stated direction and falsification criteria.

**The decision rule (§2) does not change.** The primary quantity is still
the inventory. What changes is the world shape.

### 8.1 The experiment

> **Can Organica preserve recurring structure while continuing to discover
> new structure?**

Two world shapes, run head-to-head on the same organism and engine:

| Arm | World | What it tests |
|---|---|---|
| **Uniform** | N triangles, all equally frequent (the pilot's design) | Baseline: frequency dilution hypothesis predicts inventory ≤ 91 and declining with N |
| **Scaffold + novelty** | 3 frequent triangles (one hub, repeating) + 1 new triangle introduced every K cycles | Mechanism test: if the scaffold holds the window and novelty drives discovery, inventory should grow beyond 91 |

The scaffold is `lattice_L1` (the Rung 0 world, which is already
characterised). The novelty triangles are introduced one at a time, each
with a fresh hub at degree 3, so they do not compete with the scaffold for
the top-20 slots in the first cycle they appear.

**What would confirm the mechanism hypothesis:** inventory grows beyond 91
(Rung 0) and continues growing as novelty accumulates. Theories and
questions track the arrival of new triangles rather than saturating
immediately.

**What would falsify it (and support an architectural ceiling):** inventory
stays flat regardless of how the world is structured. If adding 10 fresh
triangles one at a time (each fully visible when it arrives) does not
raise the inventory above 91, the mechanism explanation fails and the
ceiling is architectural.

### 8.2 The runner fix

`benchmarks/scale_ladder.py` will be updated before the revised ladder
runs. The fix:

- For `mode=block` worlds: bootstrap with one block (current behaviour).
- For `mode=scaffold` worlds: bootstrap with the scaffold block only; deliver
  novelty triangles cycle by cycle, one triangle's 3 events per K cycles.
- For `mode=open` worlds (if re-run): bootstrap with one hub's events (9
  events), then deliver one new hub's events per cycle.

The engine does not change. The scaffold world is a stimulus change only.

---

## 9. The Burst Assimilation Finding — MEASURED 2026-10-23

### 9.1 Scaffold Experiment Results (300 Cycles)
Running the 300-cycle scaffolded ladder (`docs/scale_ladder_scaffold.json`)
tested passive single-exposure novelty alongside the core scaffold:
* **Theories did not collapse**: 10 (Rung 0) → 13 (1s) → 13 (2s) → 14 (3s).
* **Questions did not collapse**: 10 (Rung 0) → 11 (1s) → 11 (2s) → 13 (3s).
* **Beliefs remained stable**: 18 across all scaffold arms (vs 10 in uniform variety).
* **However, inventory grew only modestly**: 91 → 94 → 93 → 95.

**The cause:** Single-exposure novelty (appearing 1× every K cycles) had raw count 1,
which failed to clear `PREDICTION_MIN_COUNT = 5` and `STABLE_THRESHOLD = 0.3`.
Passive novelty was being filtered out before it could form a process.

### 9.2 The Burst Assimilation Experiment (100 Cycles Head-to-Head)
To test whether novelty requires local reinforcement to become developmental
substrate, a 100-cycle controlled trial was run:
* **Baseline (Rung 0)**: 3-triangle core repeating.
* **Burst Assimilation**: Core scaffold + 1 new triangle every 30 cycles with an
  8-cycle concentrated burst, sustained alongside the core.

| Metric | Rung 0 Baseline (100c) | Burst Assimilation (100c) | Delta |
|---|---:|---:|:---:|
| **Total Inventory (M5)** | **82** | **99** | **+17 (+20.7%)** |
| — Theories | 10 | **16** | **+60.0%** |
| — Experiments | 10 | **18** | **+80.0%** |
| — Investigations | 10 | **18** | **+80.0%** |
| — Beliefs | 16 | **19** | **+3** |
| — Questions | 10 | **12** | **+2** |
| — Dreams | 46 | **50** | **+4** |

### 9.3 The Principle
> **Development requires novelty to become established before it can become developmental substrate.**

Organica develops substantially more structure when novelty is introduced with
enough local reinforcement to survive the architecture's early-stage filters.

### 9.4 Next Test: Cumulative Compounding (300 Cycles)
The remaining open question is whether this effect compounds over longer horizons:
* Does the burst arm pull away continuously (e.g. 91 → 130+ at 300 cycles), or
  does it encounter a higher-order architectural saturation?

### 9.5 The 300-Cycle Compounding Result — MEASURED 2026-10-23
Running 300 cycles of Burst Assimilation head-to-head against the 300-cycle
Rung 0 baseline:

| Metric | Rung 0 Baseline (300c) | Burst Assimilation (300c) | Delta |
|---|---:|---:|:---:|
| **Total Inventory (M5)** | **91** | **113** | **+22 (+24.2%)** |
| — Theories | 10 | **17** | **+70.0%** |
| — Experiments | 12 | **19** | **+58.3%** |
| — Investigations | 12 | **19** | **+58.3%** |
| — Questions | 10 | **13** | **+30.0%** |
| — Beliefs | 17 | **20** | **+3** |
| — Dreams | 52 | **60** | **+8** |

#### Trajectory: 50-Cycle Epoch Discovery Profile

| Epoch | Baseline Cumulative | **Baseline New** | Burst Cumulative | **Burst New** |
|---|---:|---:|---:|---:|
| Cycles 001–050 | 76 | **76** | 88 | **88** |
| Cycles 051–100 | 82 | **6** | 98 | **10** |
| Cycles 101–150 | 88 | **6** | 105 | **7** |
| Cycles 151–200 | 88 | **0** | 107 | **2** |
| Cycles 201–250 | 90 | **2** | 113 | **6** |
| Cycles 251–300 | 91 | **1** | 113 | **0** |

### 9.6 Core Conclusion Frozen
> **Organica's developmental capacity is not fixed. It is strongly dependent on the structure and presentation schedule of novelty.**

Two earlier candidate ceilings were falsified: 74 items (broken by baseline at 91)
and 91 items (broken by burst assimilation at 113). Repeatedly reinforced novelty
increased developmental inventory by +24.2% and continued producing new structure
across epochs 2 through 5. Novelty must first become stable enough through local
reinforcement to enter the developmental hierarchy.


