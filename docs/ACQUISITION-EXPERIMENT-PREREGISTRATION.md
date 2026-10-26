# The acquisition experiment — pre-registration

**Status: committed BEFORE any factorial run.** Nothing in this document has
been measured against a factorial cell. Where a number appears, it is either
read from the frozen engine's source or already measured by a *diagnostic*
probe that is named as such.

**The honesty boundary of this document.** Two probes have already been run,
and their results informed this design. They are therefore **design inputs,
not predictions**, and they are quarantined in §2. Every prediction in §7 is
about the factorial cells, which have not been run.

**Owner direction.** R1 and R2 become one small factorial. R3 becomes a
measurement of content identity rather than row identity. The trace's limits
are the same limits the organism's are.

---

## 1. The question

The blank-slate question, as it now stands:

> **Can experience create a structure that remains useful after the
> originating experience is gone?**

And the sharper form that replaced it:

> **Does the organism carry structure forward, reconstruct it from evidence, or
> do both under different conditions?**

The distinction that organises this experiment is between:

- **memory preservation** — the experience is kept, so the structure that
  depended on it is kept too; and
- **developmental continuity** — the *structure* is kept, by whatever means,
  whether or not the experience is.

They look alike from the outside. They are not the same, and the trace is the
instrument that tells them apart.

---

## 2. What is already known (design inputs, not predictions)

### 2.1 The trace sees the present lineage, not the historical one

The audit trace reconstructs the parent chain of every structure the organism
currently holds. It does not reconstruct what that chain *was*.

**Why, from the source.** A candidate's identity is a content hash —
`_make_id` is `sha256("|".join(key_parts))[:8]` (`sleep.py:45-48`) — but the
identity **does not include the parent set**. Higher-layer structures are
re-formed every cycle by the composition rules, and their parents are
**recomputed** from current state (`sleep.py:1432`, `1450`, `1467` for
hypotheses; `1384` for workflows). So the same content identity can carry a
**different lineage** in a later cycle.

**Consequence, and it is a hard limit on what the trace can claim:** the
lineage the trace shows is the organism's **current** lineage. It is not
evidence of the lineage that existed when the structure was first formed.
"Reconstruction of surviving developmental state" is the correct phrase, and
"developmental history" is not — the trace reconstructs the present state of a
structure's descent, not the history of that descent.

### 2.2 A measured diagnostic: links are overwhelmingly *active*, not carried

A diagnostic probe (40 cycles, read-only, scratch database) classified every
parent link of every reported structure by the state of its parent at the
moment of the link:

| State of the parent | Share of 8,416 lineage links |
|---|---|
| **Active** — re-derived from current experience in that same cycle | **87.2 %** |
| **Carried** — alive in the window but not re-derived that cycle | **12.8 %** |
| Dangling — record aged out of the window | 0 % at 40 cycles (105 aged-out branches at 120) |

And a second diagnostic: a surviving structure's **parent set is identical in
~95 %** of structure-cycles.

**Read together, these say something specific, and it is not "carried
forward".** The parent set is identical because re-derivation is deterministic
given the same content key — not because the edge set is being copied. The
links point overwhelmingly at structures that were **freshly re-derived in the
same cycle**. So the lineage is **re-derived**, and continuity comes from the
composition rules finding the same content again.

**This corrects a reading I gave earlier**, when I saw the ~95 % identical
parent sets and called it "carried forward". Measurement 2.2 is the
discriminating evidence: carried would have shown a high share of links
pointing at structures that were *not* re-derived. It does not.

### 2.3 The maintenance rule is asymmetric across layers — and this is the key fact

`SleepService._natural_selection` (`sleep.py:1752-1802`) is the engine's
survival mechanism, and it is **Layer-1 only**:

- `current_keys` is built from the concepts, phrases, loops and predictions
  produced **this cycle** (`1759-1767`).
- A prior candidate whose key is in `current_keys` is **reinforced**
  (`1778-1783`).
- Otherwise it is **decayed ×0.8** (`1785`) and, if it falls below
  `DEATH_THRESHOLD = 0.15` (`334`), **pruned** — never stored again (`1786-1787`).
- The decayed copy is written back with `generation + 1` and
  `evidence.decay_cycle = True` (`1790-1800`).

**And `_candidate_key` returns `""` for anything that is not a concept, phrase,
loop or prediction** (`1804-1817`). So **meta-concepts, processes, workflows,
hypotheses, theories, questions, dreams, investigations and experiments are
never decayed and never pruned by this path.** They are re-formed by the
composition rules and re-stored; their rows age out of the 4,000-event window
or are removed by the 20,000-row candidate retention (`memory.py:31`).

So the answer to *"what determines whether a structure continues to be
regenerated?"* splits in two:

| Layer | What determines survival |
|---|---|
| **Layer 1** (concept, phrase, loop, prediction) | **Whether current experience keeps producing that content key.** Reinforced if yes; decayed ×0.8 per cycle and pruned below 0.15 if not. |
| **Layers 2–4** (meta, process, workflow, hypothesis, theory, question) | **Not decayed at all.** Persist as rows while they remain in the window; re-formed with **recomputed parents** when the composition rules re-form them. Hypotheses have their own death rule: `conf < 0.15` and `support + contradiction ≥ 3` (`sleep.py:1499`). |

**This is the single most important thing in this document.** "Persistent
reconstruction" is an accurate description of **Layer 1** and a misleading one
for Layers 2–4, where continuity is closer to **row persistence with
re-derived edges**. The experiment must therefore not treat "the structure
survived" as one thing.

---

## 3. Definitions, fixed in advance

### 3.1 Content identity

**A structure's content identity is its candidate id.** The id is a content
hash (`_make_id`), so two rows with the same id are the same content, however
and whenever they were written.

**A row is not an identity.** The observer records every store, so for each id
the laboratory knows whether it was *re-instantiated* (a new row written) or
*left alone* (no new row). Both are reported.

### 3.2 Lineage connection

A structure's lineage is **connected** when its parent chain resolves back to
a Layer-1 terminal within depth 7, under the A3 auditor
(`benchmarks/audit_trace_probe.py` → `audit_ancestry`). A3's own honesty
criterion applies unchanged: an unresolvable parent is reported as **aged
out** or **missing record**, never as "no parent", with the window bound
stated.

### 3.3 Task support

A structure **supports the task** when the belief it carries remains
**accurate on subsequent world events** — scored by the frozen DI metric on
the preregistered event set (§6), measured **per cycle after the
intervention**, not once.

### 3.4 The two questions, kept separate

| | What it asks | Who answers |
|---|---|---|
| **Q1 — internal persistence** | Does the organism still hold the knowledge? | the organism's own state: current beliefs, current lineage, current support |
| **Q2 — external provenance** | Can the laboratory prove how it developed? | the laboratory's record: per-cycle snapshots, the store log, the trace |

A result on Q1 is not a result on Q2. A trace that reconstructs what the
organism holds is evidence about Q2 only when the laboratory's record
independently covers the period in which the structure was formed.

---

## 4. The interventions

Three axes, not two. Jeremy's R1/R2 factorial is **P × E**, and the
observer/organism distinction is a third axis because removing a parent from
the auditor's reconstruction and removing it from the organism are different
experiments.

### 4.1 Axis P — the parent structure

| Level | Intervention | What it tests |
|---|---|---|
| **P-obs** | the auditor **withholds** P from its reconstruction; the organism is untouched | **the trace.** Does the auditor stay honest when a parent is unavailable? |
| **P-org** | P's rows are removed **and** P's key is prevented from being re-derived | **the maintenance mechanism.** Does the descendant survive without its ancestor? |
| **P-none** | no intervention | baseline |

### 4.2 Axis E — the source experiences

| Level | Intervention | What it tests |
|---|---|---|
| **E-pres** | the world events that produced P's key are retained | baseline |
| **E-rem** | the source experience rows and the temporal edges they contributed are removed | **reconstruction from evidence.** Can P be rebuilt from what is left? |

### 4.3 The 2 × 2 × 3 design

`P ∈ {P-obs, P-org, P-none}` × `E ∈ {E-pres, E-rem}` = **6 cells**, plus the
untreated baseline carried from the same seed.

### 4.4 Constraints on every intervention

- **The engine is frozen.** Organism-side interventions are implemented in a
  **subclass** of `SleepService` inside the probe — the same pattern as the
  existing `--max-hypotheses` stress arm, which overrides an instance
  attribute rather than changing the frozen files. No file under `organica/`
  is modified.
- **The live study is untouched.** Every run uses a **scratch database**
  (`organica.paths.scratch_db()` / `temp_db()`). The live `memory.db` at
  5,396 sleep cycles is never opened for writing.
- **The intervention is applied after a preregistered warm-up**, so that the
  structure being intervened on exists, has a lineage, and has been observed
  by the laboratory for long enough for Q2 to be answerable.

---

## 5. What is measured, per cycle, after the intervention

Three outcomes, tracked **separately** and **per cycle**:

1. **Content reappearance** — does the content identity reappear in the
   report? (and separately: was it re-instantiated, or was its row left
   alone?)
2. **Lineage connection** — is the chain still resolvable to Layer 1, and is
   the parent set the same as before the intervention?
3. **Task support** — is the belief still accurate on the preregistered event
   set?

**Outcome 3 is a time course, not a point measurement.** The analysis must be
able to detect a **crossover** — content that persists for a while and then
stops being useful unless it is re-derived — and not merely a level
difference at one time point.

---

## 6. The preregistered task and event set

- **Task**: the belief's prediction accuracy on world events **after** the
  intervention cycle, scored with the frozen DI metric.
- **Event set**: the world events generated for the cycles following the
  intervention, from the same generator and seed as the probe's arms.
- **Baseline arms scored on the same three outcomes**:
  - **the fixed-rule ceiling** — what a non-learning system could achieve;
  - **a same-memory statistical learner** — learns the same events with the
    same memory budget, so Q1 is comparable;
  - **a replay learner** — stores the episodes verbatim and re-derives
    nothing. This is the control the mechanism claim actually needs.

**Why the replay learner is the decisive control.** If continuity is
persistent reconstruction rather than archival recall, then **a perfect-recall
system with no re-derivation is the harder baseline**, not the easier one.
It has every experience, and it cannot regenerate anything. If Organica beats
it on *"structure that remains useful after the experience is gone"*, that is
a result worth the project. If Organica does not beat it, "persistent
reconstruction" is decoration and must be reported as such.

---

## 7. Pre-registered predictions

Each prediction is falsifiable and states the observation that would refute it.
None of these cells has been run.

**P1 (Layer-1 pruning is computable from the source).** A Layer-1 structure
whose key is no longer produced is pruned after
`N = ⌈log(0.15 / c) / log(0.8)⌉` cycles, where `c` is its confidence at the
last reinforcement. For `c = 0.3` that is 4 cycles; for `c = 0.5`, 6 cycles.
*Refuted if* the measured pruning cycle differs from the formula, or if the
structure survives indefinitely.
*This is the sharpest test in the design, because the prediction is derived
from the source rather than from a fit.*

**P2 (removing a parent's key removes the descendant's regeneration).** In
`P-org × E-pres`, a descendant whose parent can no longer be re-derived is
**re-formed for at most one further cycle** — because hypothesis formation
requires a workflow, process or meta parent, and the composition rules are
deterministic given the report.
*Refuted if* the descendant persists for many cycles, which would mean the
descendant's content is carried rather than re-derived.

**P3 (removing the source experience does not prevent re-derivation of the
parent).** In `P-none × E-rem`, a Layer-1 parent whose key is still produced
by the remaining world events is **reinforced and survives** — the decay
mechanism keys on the *content key*, not on the provenance of the events.
*Refuted if* the parent decays and dies despite the key still being produced.

**P4 (the lineage is re-derived, so it can change without the structure
changing).** In cells with no intervention, a structure's content identity is
stable while its parent set can change. Specifically: a `meta_concept`'s
parent set differs between consecutive cycles in a substantial fraction of
structure-cycles (the diagnostic measured 57 of 220 at 40 cycles), while the
structure's own identity is unchanged.
*Refuted if* the parent set never changes for any structure.

**P5 (the observer-side intervention cannot corrupt the trace).** In every
`P-obs` cell, the auditor's honesty check **passes**: a withheld parent is
reported as aged out or missing record, never as "no parent", and every
unresolved node carries the window bound.
*Refuted if* any honesty error appears. This arm cannot fail by producing a
wrong answer; it can only fail by producing an untruthful one.

**P6 (the mechanisms coexist).** The predicted pattern across the six cells:

| Cell | Content reappears? | Lineage connected? | Still supports the task? |
|---|---|---|---|
| `P-none × E-pres` (baseline) | yes | yes | yes |
| `P-org × E-pres` | no (after ≤1 cycle) | no | no |
| `P-none × E-rem` | yes, if the key is still produced | yes, re-derived | degraded only if support is lost |
| `P-org × E-rem` | no | no | no |
| `P-obs × E-pres` | yes (organism untouched) | **no — the trace is incomplete** | yes |

**The predicted dissociation is the interesting one:** in `P-obs × E-pres` the
organism retains everything while the laboratory's provenance is broken.
**That cell separates Q1 from Q2 directly, in the trace's own hands.**

*Refuted if* `P-org × E-pres` shows the descendant persisting and remaining
useful (which would mean inherited content is carried and is sufficient), or
if `P-none × E-rem` shows the parent dying despite its key still being
produced.

---

## 8. Instrument requirements, checked before any cell is run

Each of these is a check that must be **proved able to fire**:

1. **Content-identity detector** — the laboratory can tell a re-instantiated
   structure from a retained one, by id, from the store log alone.
2. **Intervention verification** — after an intervention, the laboratory
   confirms the intervention happened (the parent is absent from the window;
   the source events are absent from the `events` table) *before* any outcome
   is interpreted. **A perturbation that did not happen is not a null
   result.**
3. **Observer invariance** — the observer is on/off byte-identical, as A4
   already requires.
4. **Honesty check** — A3's criterion, in every cell.
5. **Scratch-only guarantee** — the live `memory.db` is never opened for
   writing by the probe.

**If any of these cannot be proved to fire, the experiment does not run.**

---

## 9. What this experiment will not establish

- **Not** that Organica learns, or that it learns like a human.
- **Not** that the trace reconstructs *developmental history*. It reconstructs
  the **present** lineage of surviving structures (§2.1).
- **Not** that the results generalise beyond one world family, one policy
  and one configuration.
- **Not** anything biological. "Persistent reconstruction" is a description of
  a mechanism in this code. The resemblance to how some biological systems
  are described is a **motivation for the experiment**, never a claim about
  its result.
- **Not** that the survival rule is forgetting. `×0.8` and `0.15` are
  hand-written thresholds; they resemble forgetting but they are a threshold.

---

## 10. Documents

- `docs/AUDIT-TRACE-SPEC.md` — the trace's specification and limits (§6, §13).
- `docs/USER-MANUAL.md` — §8.16, the manual's account of this design.
- `docs/FACTS-SHEET.md` — §AA20–§AA22.
- `research-journal/phase_g_findings_20261021.md` — §48.
- `AGENTS.md` — rule 22.
