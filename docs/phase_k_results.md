# Phase K — Comparative Advantage Search — RESULTS

**Status: RESULTS.** The protocol was frozen in
[`PHASE-K-PREREGISTRATION.md`](PHASE-K-PREREGISTRATION.md) and committed
before any Phase K outcome was generated. This document reports what the
campaign found and what it changes. Nothing here revises a pre-registered
decision rule; the rules were fixed before the run and are applied as
written.

---

## 1. The question

Not *"can Organica do X?"* but **"what is Organica uniquely good at?"**

Phase H tested next-event prediction. Phase I tested regime-shift detection.
Phase J tested gradual post-shift adaptation. All three were negative. Three
negative tasks is not a verdict on the architecture; it is three tasks. So
Phase K was a **search** over three candidate families, each derived from a
mechanism the project has actually measured, each scored against the
strongest simple baseline that could plausibly solve it.

**The question this phase deliberately does not ask:** whether the engine
should be redesigned. No result here authorises a V2. The pre-committed
terminal outcomes were: a confirmed family names the task to take to a
larger-n confirmation campaign; **no confirmed family means the search
failed within these three families, and V2 is not designed**.

---

## 2. What was measured

| Family | Task | Primary endpoint | Matched ablation |
|---|---|---|---|
| **K1 — Incremental world modeling** | a two-entity scaffold observed from cycle 1; a third entity arrives at cycle 150 and the world keeps running | pair F1 over all three entities' gold pairs | `NO_QUESTIONS` |
| **K2 — Belief revision** | one entity holds the world until cycle 200, then a different entity takes over and the first stops appearing | revision F1 — the new regime's pairs are the gold, the retired regime's pairs are false positives | `NO_FALSIFICATION` |
| **K3 — Longitudinal knowledge integration** | three scaffold entities from cycle 1, then one new entity every 100 cycles for 600 | harmonic mean of core-retention F1 and late-incorporation F1 | `NO_DREAMS` |

Ten seeds (20261023–20261032), `PYTHONHASHSEED=0` in every process, the
engine frozen. Decision rule: paired percentile bootstrap over the ten
per-seed differences, **98.33%** interval (Bonferroni across the three
families), SUPPORTED only when the interval for Organica − best simple
baseline lies wholly above zero.

---

## 3. The two instrument audits

Both ran before the campaign and the campaign did not run if either failed.

**K0 — the pipeline can report a loss.** The Phase H held-out next-event
task was rerun through the same code, where Organica's loss is already
known: **0.412605 vs 0.504039** for the first-order Markov baseline. It
reproduced exactly. A control that could only ever confirm itself would be
worthless; this one can fail.

**The endpoint ceiling check — the metric can report a win.** Every
endpoint is checked against a *synthetic perfect model*, which must score
1.0. This is what caught the defect recorded in Amendment 1: the K3 joint
endpoint originally scored each group against the other group's content as
false positives, so a model holding both the scaffold and the late
structure could reach only 0.667. The defect was found before any K3
outcome existed, the whole first run was discarded, and the check is now
permanent.

---

## 4. The results

**All three families are REVERSED.** Not one is SUPPORTED, and not one is
INCONCLUSIVE: every 98.33% decision interval lies wholly below zero, so each
family is a clean loss rather than an ambiguous one.

| Family | Organica (mean) | Best simple baseline (mean) | Paired difference | 98.33% interval | Verdict |
|---|---|---|---|---|---|
| **K1** — incremental world modeling | 0.5923 | 0.9360 | **−0.3437** | [−0.3773, −0.3123] | **REVERSED** |
| **K2** — belief revision | 0.4111 | 0.9846 | **−0.5735** | [−0.6162, −0.5309] | **REVERSED** |
| **K3** — longitudinal integration | 0.0000 | 0.8578 | **−0.8578** | [−0.8598, −0.8571] | **REVERSED** |

Per-seed, Organica against the *best* baseline configuration and the matched
ablation:

| Family | Seed | Organica | Best baseline | Ablation |
|---|---|---|---|---|
| K1 | 20261023 | 0.579 | 0.923 | 0.541 |
| K1 | 20261024 | 0.556 | 0.973 | 0.600 |
| K1 | 20261025 | 0.595 | 0.878 | 0.595 |
| K1 | 20261026 | 0.595 | 0.947 | 0.595 |
| K1 | 20261027 | 0.615 | 0.923 | 0.632 |
| K1 | 20261028 | 0.615 | 0.923 | 0.579 |
| K1 | 20261029 | 0.564 | 0.973 | 0.632 |
| K1 | 20261030 | 0.595 | 0.923 | 0.615 |
| K1 | 20261031 | 0.595 | 0.973 | 0.615 |
| K1 | 20261032 | 0.615 | 0.923 | 0.615 |
| K2 | 20261023 | 0.370 | 1.000 | 0.429 |
| K2 | 20261024 | 0.333 | 1.000 | 0.276 |
| K2 | 20261025 | 0.444 | 1.000 | 0.370 |
| K2 | 20261026 | 0.444 | 1.000 | 0.429 |
| K2 | 20261027 | 0.462 | 1.000 | 0.429 |
| K2 | 20261028 | 0.444 | 0.923 | 0.429 |
| K2 | 20261029 | 0.429 | 1.000 | 0.429 |
| K2 | 20261030 | 0.385 | 1.000 | 0.345 |
| K2 | 20261031 | 0.370 | 1.000 | 0.308 |
| K2 | 20261032 | 0.429 | 0.923 | 0.429 |
| K3 | 20261023 | 0.000 | 0.857 | 0.000 |
| K3 | 20261024 | 0.000 | 0.857 | 0.000 |
| K3 | 20261025 | 0.000 | 0.857 | 0.000 |
| K3 | 20261026 | 0.000 | 0.857 | 0.000 |
| K3 | 20261027 | 0.000 | 0.864 | 0.000 |
| K3 | 20261028 | 0.000 | 0.857 | 0.000 |
| K3 | 20261029 | 0.000 | 0.857 | 0.000 |
| K3 | 20261030 | 0.000 | 0.857 | 0.000 |
| K3 | 20261031 | 0.000 | 0.857 | 0.000 |
| K3 | 20261032 | 0.000 | 0.857 | 0.000 |

**The baselines were handed the tuning advantage on purpose.** Every simple
baseline was swept over its declared grid and its *best* configuration was
used: 15 co-occurrence configurations (5 windows × 3 minimum counts) and 9
temporal-graph configurations (3 lookbacks × 3 minimum counts), 24 per seed
per family, and the maximum taken. The winning configuration is recorded per
seed in `docs/phase_k_results.json`. A strawman cannot manufacture a win out
of this; the only thing it can do is manufacture a loss.

### 4.1 The matched ablations, and what they do and do not say

| Family | Ablation | Ablation mean | Organica − ablation | 98.33% interval |
|---|---|---|---|---|
| K1 | `NO_QUESTIONS` | 0.6018 | −0.0095 | [−0.0328, +0.0140] |
| K2 | `NO_FALSIFICATION` | 0.3870 | +0.0241 | [−0.0048, +0.0495] |
| K3 | `NO_DREAMS` | 0.0000 | +0.0000 | [0.0000, 0.0000] |

**These intervals all contain zero.** In K1 and K2 the hypothesised mechanism
makes no detectable difference at all — removing question generation does not
change the score, and removing falsification does not change the score. That
is a *negative attribution*: the mechanisms these families were built around
are not what separates Organica from a co-occurrence counter.

This is worth stating plainly, because it is the more interesting half of the
result. The three families were chosen *because* each matches a mechanism the
project has measured — question generation for novelty assimilation,
falsification for belief revision, dreams for integration. The campaign's
ablation arm says **none of those three mechanisms is load-bearing for the
corresponding task.** K3 is the extreme case: with dreams removed the score is
identical to the decimal, because the score was already zero.

The attribution is *within one implementation* on synthetic worlds. It says
these mechanisms do not carry these tasks in Organica 1. It does not say the
mechanisms are useless.

### 4.2 Robustness

A verdict this clean still has to survive its own uncertainties, so both were
checked on every family:

| Family | 8 bootstrap seeds | Drop the most favorable seed | Drop the least favorable seed |
|---|---|---|---|
| K1 | REVERSED (all 8) | REVERSED [−0.3832, −0.3211] | REVERSED [−0.3669, −0.3074] |
| K2 | REVERSED (all 8) | REVERSED [−0.6239, −0.5435] | REVERSED [−0.6034, −0.5211] |
| K3 | REVERSED (all 8) | REVERSED [−0.8601, −0.8571] | REVERSED [−0.8571, −0.8571] |

The published interval depends on a bootstrap seed derived from the family
name through Python's string hash, which is deterministic only because the
protocol pins `PYTHONHASHSEED=0`. Re-running the bootstrap with eight
different seeds leaves every verdict unchanged, so no verdict is an artifact
of that choice. Removing the single most favorable seed, and separately the
single least favorable seed, also leaves every verdict unchanged — with ten
seeds, one outlier cannot carry any of these intervals.

### 4.3 Why K3 is exactly zero — measured, not assumed

Organica scored **0.000 on all ten K3 seeds** while the trivial baseline
reached 0.857. A hard zero on a metric that the ceiling check proved can
reach 1.0 deserves a root cause before it is reported, so three checks were
run.

**It is not a reading artifact.** The harness reads the structures from the
final sleep cycle's report. A per-cycle diagnostic ran one K3 world and
inspected **every** cycle's own structures: late-group pairs appear in
**zero cycles out of 150**, not just the last one. The late structure is
never formed at any point, so this is not the organism forming it and then
losing it.

**It is not the harness failing to read a structure type.** The engine emits
several candidate types and the edge extractor handles a specific set. The
final cycle's structures were dumped by type and checked for late-entity tag
mentions: `hypothesis`, `loop_candidate`, `prediction_candidate`,
`process_candidate`, `workflow_concept`, `meta_concept`, `dream`,
`investigation` and `experiment` mention **0 of 12** late tags. Only
`anomaly` mentions them (5 of 12) — the engine *notices* the late structure
as anomalous and does not absorb it. So there is no late structure sitting
unread in a type the extractor ignores.

**It is not simply that late structure cannot be incorporated.** A 2×2 control
varied the two things that could matter — which group arrives first, and
which group carries more weight — and the late group is not uniformly
excluded. When the *early* group is weakened (weight 1) and the late group is
strengthened (weight 3), the late group **is** incorporated, at 9 of 18 gold
pairs, in the very same world shape. The exclusion is therefore a property of
the *configuration the protocol specifies*, not a blanket inability to learn
late structure.

That is the honest characterization: under the frozen K3 protocol — scaffold
entities at weight 3, late entities at weight 1 — Organica retains the early
scaffold (core-retention F1 ≈ 0.67) and incorporates **none** of the late
structure, and a bounded belief pool (`MAX_HYPOTHESES = 15`, with 18
pre-retention beliefs measured in the matrix) is where the competition
happens. The preregistration's §6 flagged exactly this risk before the run:
*"a K3 result measures retention against incorporation under a capacity
limit."* The campaign confirmed the measurement, and the §6 caveat is what
makes the number interpretable.

**The 2×2, in full.** Peak coverage of each group's gold pairs, five seeds:

| early weight | late weight | early group (arrives 1st) | late group (arrives 2nd) |
|---|---|---|---|
| 3 | 1 *(the protocol's K3)* | 14, 16, 15, 15, 17 | **0, 0, 0, 0, 0** |
| 3 | 3 | 13, 16, 15, 15, 17 | 0, 1, 0, 0, 0 |
| 1 | 3 | 12, 14, 14, 15, 16 | **9, 11, 10, 10, 9** |
| 1 | 1 | 13, 16, 15, 15, 17 | 0, 1, 0, 0, 0 |

The late group is incorporated **only when it is strictly stronger** than the
group that arrived first. At equal strength the earlier group wins. Reproduce
with `python benchmarks/phase_k_diagnose.py --scale 4 --seeds 5`.

---

## 5. What this changes

**For V2: nothing, and that is the point.** The pre-committed terminal
outcomes were written before the run. **H2 — the search failed** — is the
outcome that materialised: no family is SUPPORTED, three more task families
are ruled out, **and V2 is not designed.** The preregistration was explicit
that "no family confirmed" is a legitimate, publishable result and that it
does not authorise a V2. That is how this result is being treated.

**Six task families are now negative.** Phase H (next-event prediction), Phase
I (regime-shift detection), Phase J (post-shift adaptation), and now K1, K2
and K3. The question — *what class of problems benefits from a developmental
architecture?* — stays open, with six families excluded rather than one
verdict reached.

**The losses are large and stable, not marginal.** This is a fact worth
stating plainly because it constrains what comes next. K2's baseline scores a
perfect 1.000 on eight of ten seeds. K3's scores 0.857 on nine of ten. The
paired intervals are tight and every robustness check agrees. These are not
near-ties that a bigger sample might flip.

**The ablations came back empty, and that is the most actionable part.** On
the two families where a mechanism was ablated specifically — question
generation for K1, falsification for K2 — the ablation changed nothing
measurable, and on K3 the ablation was identical to the decimal because the
score was already zero. The three families were each chosen *because* they
match a mechanism the project has measured, and the campaign says those
mechanisms are not carrying these tasks.

This does not say the mechanisms are inert in general. It says that on tasks
where the organism was already losing by a wide margin, a mechanism cannot
show an effect — the outcome is dominated by something else.

**So the next question is a mechanism question, not a task question.** Six
negative families is strong evidence that the current engine has no external
advantage on any task tried so far. Continuing to add task families to the
map is a reasonable thing to do and the map is the deliverable. But the
ablation result points at a prior question: **which internal mechanism, if
any, produces an external advantage at all?** Until that is answered, another
task family is being added to a list of losses.

That question is answerable without designing V2, and it is the natural
continuation of Phase K rather than a replacement for it.

---

## 6. Reproducing this

```bash
# the campaign (resumable; safe to stop and restart)
python benchmarks/phase_k_campaign.py --families K1 K2 K3 --seeds 10 \
       --workers 12 --resume --out docs/phase_k_results.json

# the two instrument audits, which run before the campaign
python benchmarks/phase_k_campaign.py --control-only
python benchmarks/phase_k_campaign.py --self-test

# the K3 root-cause diagnostics (per-cycle, under-read, and the 2x2)
python benchmarks/phase_k_diagnose.py --scale 4 --seeds 5
```

The full artifact is `docs/phase_k_results.json`: the protocol block, the
control, the ceiling check, all thirty per-seed records with every model's
score and configuration, and the per-family summaries with their intervals.
The live recording of the run is `docs/phase_k_results.ndjson`.

**One bookkeeping note, recorded rather than hidden.** The live recording
holds **29 of the 30 seeds**: seed K1/20261023 was completed by an earlier
harness version, before the checkpoint existed, and was carried into the final
run through the results-file resume path rather than re-appended to the
recording. The results file — the authoritative artifact — holds all thirty,
and the two files agree numerically on every overlapping seed.

---

## 7. Where the result is recorded

- `research-journal/phase_g_findings_20261021.md` **§33** — the scientific
  record, with the robustness checks and the K3 root cause.
- `docs/FACTS-SHEET.md` **§T** — the one-line-per-fact version.
- `docs/PHASE-K-PREREGISTRATION.md` — the frozen protocol, unchanged since it
  was committed before any outcome existed.
