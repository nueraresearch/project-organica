# Phase K — Comparative Advantage Search

**Status: PREREGISTRATION. Committed 2026-10-24, before any Phase K outcome
was generated.** Nothing in this document may be edited to match a result. If
the protocol has to change, the change is made here, dated, with the reason
given, and the reason is recorded in the journal — not applied silently in
the code.

**The question.** Not *"can Organica do X?"* but **"what is Organica uniquely
good at?"**

Phase H tested next-event prediction. Phase I tested regime-shift detection.
Phase J tested gradual post-shift adaptation. All three were negative. The
obvious conclusion — *Organica cannot do anything the baselines cannot* —
does not follow from that, and the mistake would be to treat it as if it
did. Three tasks were negative; an infinite number of tasks were not tested.

So Phase K is a **search**, not a test. It looks for the task family where
the architecture's particular machinery pays off, and it is designed so that
finding nothing is a legitimate, pre-committed, publishable outcome.

**What is explicitly not being asked.** Phase K does not ask whether the
engine should be redesigned, and no result here authorises a V2. It asks
where the current architecture has an advantage. V2 design is downstream of
that answer, and only if the answer is positive.

---

## 1. Why these three families, and what "advantage" would have to mean

Each candidate is derived from a mechanism the project has actually measured,
and each is a task that a *strong* simple baseline could plausibly solve.
That last clause is the whole discipline of this phase: Phases H, I and J
each failed against baselines that were given no tuning advantage at all, and
a benchmark that a strong baseline cannot solve is not evidence of anything.

| Family | Mechanism it targets | Why it might be Organica's | The simple baseline that could beat it |
|---|---|---|---|
| **K1 — Incremental world modeling** | question generation drives novelty assimilation (the matrix found `NO_QUESTIONS` discovers *most*: 112 items) | the organism maintains a *persistent* structure and folds new material into it, rather than counting what is currently in front of it | online co-occurrence counting, which won Phase H at 0.8000 vs Organica's 0.7041 |
| **K2 — Belief revision** | falsification and contradiction machinery drive revision (the matrix found `NO_CONTRADICTIONS` and `NO_FALSIFICATION` change development) | revision should be *cheaper* than relearning: keep what is still valid, update only what changed | change-point detection followed by wholesale relearning, with a forgetting window |
| **K3 — Longitudinal knowledge integration** | dreams integrate beliefs into coherent structure (prediction P4, **SUPPORTED**) | the inventory grew 74 → 91 → 113 → 119 → 128 under a scaffold; the organism may accumulate coherent structure where a local predictor cannot | sliding-window co-occurrence counting, which must trade retention against acquisition and cannot do both |

**The selection risk, stated plainly.** These three families were chosen
*because* they match measured mechanisms. That is hypothesis generation from
data and it creates a real risk of manufacturing a false positive. Three
things counter it, and they are the reason this phase can be trusted either
way:

1. **The baselines get the tuning advantage.** Every simple baseline is swept
   over a declared grid and its **best** score is the number used. That makes
   the baseline harder to beat than any fixed configuration would be, and a
   strawman baseline — the single most likely way to fake a win — is
   impossible by construction.
2. **The outcome is pre-committed.** "No family confirmed" is a terminal
   state with its own meaning, written down before the run.
3. **Every win must survive its own mechanism ablation.** A family whose
   advantage disappears when the hypothesised mechanism is removed is not
   evidence for that mechanism.

---

## 2. Frozen protocol

**Seeds.** 20261023 … 20261032 — ten seeds, the same set Phase H used.

**Process control.** `PYTHONHASHSEED=0` in every process, so hash order is
common-mode across arms and cannot contaminate a comparison.

**Engine.** Frozen. No engine changes. The matched ablations are in-process
subclasses, exactly as the campaign runner does them.

**Event structure.** Eight events per cycle. Each event is a pair of tags
drawn from one *entity*; an entity is a four-tag set active over a window of
cycles. With probability 0.10 an event is a pair drawn from a noise-only
vocabulary (`quartz`, `static`, `velvet`, `random`). Noise pairs and
cross-entity pairs are **false positives** in every family below.

### K1 — Incremental world modeling

| | |
|---|---|
| Cycles | 300 |
| Entities | `core_a` (cycles 0–299, weight 3), `core_b` (cycles 0–299, weight 3), `late_c` (cycles **150**–299, weight 3) |
| **Primary endpoint** | pair **F1** against the union of all three entities' gold pairs |
| Supporting | late-entity F1 (*incorporation*), core F1 (*retention*) |
| Matched ablation | `NO_QUESTIONS` — question generation removed |

### K2 — Belief revision

| | |
|---|---|
| Cycles | 300 |
| Entities | `old_a` (cycles **0–199**, weight 1), `new_b` (cycles **200**–299**, weight 1). `old_a` **stops appearing** at the switch. |
| **Primary endpoint** | **revision F1** — the new regime's pairs are the gold; the retired regime's pairs are counted as false positives, so carrying the old belief forward is penalised |
| Supporting | current-regime F1, stale-pair count and stale rate |
| Matched ablation | `NO_FALSIFICATION` — no refutation, no extinction, no revision |

### K3 — Longitudinal knowledge integration

| | |
|---|---|
| Cycles | 600 |
| Entities | `core_0..2` (cycles 0–599, weight 3 — the scaffold), `late_0` (cycle 100), `late_1` (cycle 200), `late_2` (cycle 300), each weight 1 |
| **Primary endpoint** | **harmonic mean of core-retention F1 and late-incorporation F1** — a model that keeps everything and learns nothing scores badly, and so does the reverse |
| Supporting | core-retention F1, late-incorporation F1, each separately |
| Matched ablation | `NO_DREAMS` — dream generation removed |

---

## 3. The baselines, and the grid they get

Two baseline families, both trivial and both independent of Organica's
machinery — they count co-occurrences and temporal transitions over the event
text and nothing else.

| Baseline | Grid swept |
|---|---|
| **Online co-occurrence** (undirected, within a trailing window) | window ∈ {all, 300, 150, 75, 30} cycles × min_count ∈ {3, 5, 10} |
| **Temporal transition graph** (undirected, within a lookback of events) | lookback ∈ {1, 3, 5} events × min_count ∈ {3, 5, 10} |

**The rule:** for each seed, the best configuration *of each baseline family*
on the scored primary endpoint is selected, and the better of the two becomes
**the best simple baseline** for that seed. The comparison is
`Organica − best simple baseline`.

This selects the baseline's configuration using the gold labels. That is
deliberate and it is generous to the baseline: it can only make an Organica
win harder to claim. A win under this rule is a win against the best a simple
method could do on this task, not against a convenient strawman.

---

## 4. Uncertainty and the decision rule

**Paired percentile bootstrap**, 10,000 replicates, over the ten per-seed
paired differences.

**Multiplicity.** Three candidate families. Bonferroni across them:
α = 0.05 / 3 = 0.016667 two-sided, so the decision interval is the **98.33%**
percentile interval. (Phase I used the same construction across two families:
97.5%.)

| Outcome | Condition |
|---|---|
| **SUPPORTED** — an advantage is demonstrated | the 98.33% paired interval for Organica − best simple baseline lies **wholly above zero** |
| **REVERSED** — the baseline is ahead | the interval lies **wholly below zero** |
| **INCONCLUSIVE** | the interval contains zero |

**Attribution** is reported separately and is *not* part of the success
criterion. The matched ablation's paired interval against Organica tells you
whether the hypothesised mechanism is implicated. A family can be SUPPORTED
with the mechanism unresolved; it cannot be SUPPORTED with the mechanism
*refuted* and still be attributed to that mechanism.

**NOT INTERPRETABLE** is kept distinct from REVERSED. A family whose primary
endpoint is degenerate (no gold pairs, or a baseline that predicts nothing)
is reported as not interpretable and is not allowed to be called a loss.

---

## 5. The harness is validated before the campaign runs

**K0 — negative control.** The Phase H held-out next-event task is rerun
through this harness, where Organica's loss to a first-order Markov baseline
is already known: **0.412605 vs 0.504039**.

If the harness reports an Organica *win* on K0, the harness is broken and the
campaign **does not run**. This is an instrument check, run before the
experiment, and it is excluded from the three-family multiplicity adjustment
and from every claim.

A control that could only ever confirm itself would be worthless. This one
can only fail.

**The pilot, disclosed.** Before this document was frozen, the harness was
run once at **one seed and one tenth of every cycle count** (K1 30 cycles,
K2 30, K3 60) to check that it executes and that the numbers move. It did,
and it is a **pilot, not evidence**: one seed, ten per cent of the protocol,
no interval, and it is excluded from every claim below.

What it showed:

| Family | Organica | best simple baseline | (pilot, 1 seed, 1/10 scale) |
|---|---:|---:|---|
| K1 | 0.5714 | 0.9444 | baseline ahead |
| K2 | 0.3846 | 0.6316 | baseline ahead |
| K3 | 0.0000 | 0.5742 | baseline ahead |

Two things came out of it that change nothing about the protocol but are
recorded so that nobody is surprised later:

1. **K3's joint endpoint is sensitive to a hard zero.** In the pilot
   Organica retained core structure (F1 0.60, close to the baseline's 0.63)
   but incorporated **none** of the late entities, so the harmonic mean was
   exactly zero. That is a real measurement at 60 cycles, not an extraction
   failure — the score components are reported separately in every artifact,
   so the joint number can always be taken apart.
2. **The harness extracts the organism's structures correctly.** K1 and K3
   produce non-zero pair sets, and the same code path produces the Phase H
   numbers exactly.

The pilot was run **after** the family definitions, endpoints, grids and
decision rules were fixed, and it did not change any of them. It is recorded
here rather than in the results file so that it cannot be mistaken for
evidence.

---

## 6. A note on representational capacity

Organica's persistent structure is bounded: the matrix measured 18
pre-retention beliefs and 15 retained beliefs in every arm, and
`MAX_HYPOTHESES = 15` binds the belief layer. The K3 world asks whether a
structure of that size can *both* retain three scaffold entities and
incorporate three late ones.

That is a fair question — a bounded structure is a real constraint and the
baselines are unbounded — but it means a K3 result measures **retention
against incorporation under a capacity limit**, not unbounded accumulation.
The scaffold entities carry weight 3 and the late entities weight 1
precisely so that the scaffold stays observable after the novelty arrives.
A redesigned architecture would not inherit the cap, so a K3 result is a
result about *Organica 1*, not about developmental architectures in general.

---

## 7. Pre-committed terminal outcomes

| Outcome | Condition | What it means |
|---|---|---|
| **H1 — a task is found** | at least one family is SUPPORTED | that family names the task to take to a larger-n confirmation campaign. **Still not a V2 design.** A confirmation at greater n is required first. |
| **H2 — the search failed** | no family is SUPPORTED | three more task families are ruled out. The negative-results map grows. **Do not design V2.** The question *what class of problems benefits from a developmental architecture* stays open, with three families now excluded. |
| **H3 — inconclusive** | every family's interval contains zero | raise n rather than conclude anything. |

**H2 is a real outcome and is written down in advance so that it cannot be
quietly reinterpreted as a near-miss.**

---

## 8. Limits

- These are **synthetic worlds** with four-tag entities. A result here is a
  result about this task family, not about natural environments.
- The three families were **selected** because they match measured mechanisms.
  That is a real risk of false positives and is why the baselines get the
  tuning advantage and why the terminal outcome includes H2.
- Ten seeds is a small sample. The bootstrap interval is the honest
  uncertainty statement, but a near-zero mean with a wide interval is
  INCONCLUSIVE, not a loss, and not a win.
- The matched ablations isolate a mechanism **within one implementation**. A
  mechanism that helps here may still be the wrong mechanism for a task that
  matters.
- Phase K measures the current engine. Nothing here is evidence about
  Organica 2, and nothing here is a reason to build it.

---

## 9. Artifacts

Committed with this protocol:

- `benchmarks/phase_k_campaign.py` — the harness (world generator, baselines,
  scoring, bootstrap, control)
- `docs/PHASE-K-PREREGISTRATION.md` — this document

Produced by the campaign and committed with its result:

- `docs/phase_k_results.json` — the campaign result, per model and per seed
- `docs/phase_k_results.md` — the write-up
- journal §33 — the result and what it changes
