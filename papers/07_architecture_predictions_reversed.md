# Paper 7: When the Architecture's Own Theory Fails — Three of Five Preregistered Developmental Predictions Reversed in Organica 1

**Author:** Jeremy Beebe (Nuera RDL) — https://orcid.org/0009-0009-2394-9714 — jeremy@nueraresearch.com
**Draft status:** First draft, 2026-11-06. Numbers in the three results tables are checked mechanically against `docs/verdicts.json` and `docs/phase_k_results.json` by `tests/test_reversals_paper_numbers.py`. No external citation is made in this draft; see §9. Not submitted or published.
**Scope:** Organica 1; the five preregistered architecture predictions of Ablation Study 2, and the matched mechanism ablations of Phase K.
**Repository:** [`nueraresearch/project-organica`](https://github.com/nueraresearch/project-organica), branch `master`.

## Abstract

A developmental architecture usually arrives with a theory of what drives development: that contradiction is fuel, that curiosity requires explicit questions, that expected-information-gain attention steers growth. Organica 1 was built on exactly that theory, and it preregistered five directional predictions before the Tier-1 campaign ran. This paper reports what happened to them.

Two predictions held: retention policy affects development, and removing dreams harms it. **Three reversed.** Removing contradiction's weight from the confidence formula *raised* the development measure; removing question generation *raised* it further; and selecting the *lowest*-expected-information-gain experiment developed more than selecting the highest. Each verdict is direction-aware, so a naive "did the metric move?" test would have scored five confirmations where the directional test scores two, and would have hidden the three results that matter.

An independent arm points the same way. On three external task families the organism already loses to the strongest simple baseline, the matched mechanism ablations — question generation, falsification, dreams — changed the score by intervals that all contain zero: −0.0095 [−0.0328, +0.0140], +0.0241 [−0.0048, +0.0495], and 0.0000 [0.0000, 0.0000]. The mechanisms the families were built around are not what separates Organica from a co-occurrence counter.

We offer two readings and the experiments that separate them. Either the mechanisms are mis-specified — contradiction as a weight rather than a count, questions as a capped layer on an already saturated belief pool, EIG's uncertainty-times-novelty ranking favouring noise — or the development measure rewards breadth, and mechanisms that focus attention necessarily narrow the inventory it counts. Both readings are testable, and neither licenses the stronger claim that these mechanisms are useless. The finding is narrower and more useful than a refutation: **a developmental architecture's motivational layer is a hypothesis about load-bearing structure, and this one was never tested as one until now.**

## 1. Introduction

The project's own account of development was explicit and falsifiable. Contradiction between competing expectations was said to be the fuel of development; question generation was said to be a prerequisite for curiosity; expected-information-gain (EIG) attention was said to allocate inquiry to where it buys the most. These were not slogans: they were implemented as layers, and Ablation Study 2 turned each into a directional prediction, committed before the campaign ran.

The predictions were tested by disabling each mechanism in its own colony, running all six colonies on the same engine, the same stimulus and the same seed, and asking whether the development measure moved — **and in which direction**. The direction check is the whole design. A two-sided "did it move?" test cannot distinguish "the mechanism is necessary", "the mechanism is irrelevant", and "the mechanism is actively harmful", and those three have completely different consequences for the architecture. The campaign's verdict code is direction-aware for that reason, and the difference between the two tests is the difference between five confirmations and the result reported here.

This paper is deliberately narrow. It reports the five predictions, the three reversals, the one independent cross-check, and what each reading would require to be wrong. It does not re-analyse Phase L, does not report Gate 13, and does not survey the negative task map; those are separate records. It also does not claim that contradiction, questions or EIG are useless in general — only that in this engine, on this stimulus, at this scale, removing them did not reduce development.

## 2. The theory under test

Organica 1 forms candidate structures from a tagged event stream through repeated consolidation cycles. Six architectural laws govern the process, and the motivational layers are two of them: contradiction between competing expectations, and EIG-ranked attention. The project's design laws and architecture reference state the intended roles.

The five preregistered predictions were:

| # | Prediction | Mechanism disabled in the comparison colony |
|---|---|---|
| P1 | Retention policy affects development | `SALIENCE` (retention policy replaced) |
| P2 | Contradiction is developmental fuel | `NO_CONTRADICTIONS` |
| P3 | Curiosity needs explicit questions | `NO_QUESTIONS` |
| P4 | Dreams contribute to trajectory | `NO_DREAMS` |
| P5 | EIG is orthogonal to development | `ANTI_EIG` (lowest-EIG selection) |

Two naming disclosures matter for reading the results, and both are in the campaign record. **`NO_CONTRADICTIONS` does not remove contradictions.** It removes contradiction's *weight in the confidence formula*; the raw count is unchanged, and the metric built on raw counts is near-invariant for that colony by construction. The honest name is *contradiction not weighted in confidence*. **`NO_DREAMS` does not merely remove eleven dreams** — the dreams that would have been built from its beliefs are absent too, which is why the inventory loss is far larger than the dream count alone.

## 3. Methods

### 3.1 Campaign

Six colonies — `FULL`, `SALIENCE`, `NO_CONTRADICTIONS`, `NO_QUESTIONS`, `NO_DREAMS`, `ANTI_EIG` — each ran 3,000 cycles on the frozen engine, 18,000 colony-cycles in total. The stimulus was `lattice_L1`: three disjoint triangles, 9 distinct events over 7 distinct words, with the experience repeating every 9 cycles. Seed `20261023` for every colony, `PYTHONHASHSEED=0` in all six processes so that hash order is common-mode across arms. G1 code paths were verified distinct before the run, so each colony really executes the mechanism it names.

### 3.2 Metrics and the noise floor

Development is measured as the **inventory** — the count of distinct structures discovered — and by nine metrics M1–M9 computed per cycle. The development-velocity metric M5 is new items per 100 cycles. That definition has a defect the campaign disclosed after the fact: over 300 cycles `FULL` recorded 74 new items; over 3,000 cycles it also recorded 74, so the "rate" fell from 24.667 to 2.467 because the numerator stopped growing while the denominator grew tenfold. **M5 is a finite inventory divided by the run length, not a velocity**, and the paper uses it only as a scale-free way to compare arms on the same stimulus, never as evidence of continuing development.

The noise floor was measured before the run, not assumed. At 3,000 cycles the within-process seed floor is exactly **0.00** for every metric; the process-level floor moves exactly one field, M5, by exactly one new item, which at 3,000 cycles is a rate spread of **0.033**. A delta counts as moved only if it exceeds that floor for its metric.

### 3.3 Sensitivity audit

The campaign audited which metrics can move at all before interpreting any of them. **5 of 9 can**: M2, M3, M4, M5, M7. M1, M6 and M8 are saturated — a theory present in 2,999 of 3,000 cycles in every arm, lineage depth 7 in every arm, identical population stability — and M9 is structurally zero, because a cognitive revolution requires a dominant theory to be demoted and replaced within 50 cycles and no arm does so. A metric that cannot move cannot support a verdict, and reporting the saturated ones as null results would have been an error.

### 3.4 Verdict rule

Each prediction is scored on its **effect metric** — the metric the preregistration declares for it, or, where it declares none (P1), the mover with the largest absolute delta; §4.1 quotes the metric used for each row — against the measured noise floor, and the verdict requires the *predicted direction*. A prediction whose metric moves beyond the floor in the opposite direction is **REVERSED**, not SUPPORTED. This rule was committed with the metrics and was not amended after the run.

### 3.5 The independent arm

Phase K supplies the cross-check: ten seeds per family, a paired percentile bootstrap, a 98.33% decision interval (Bonferroni across three families), and baselines swept over a declared grid of 24 configurations per seed per family with the **best** configuration used. Each family was built around one of the mechanisms above — question generation for K1, falsification for K2, dreams for K3 — so the matched ablations ask whether removing the mechanism changes the score. A control (K0) reran a task where Organica's loss is already known and reproduced it (0.412605 against 0.504039), so the pipeline can report a loss.

## 4. Results

### 4.1 The five predictions

| # | Prediction | Colony | Effect metric | Reference | Colony value | Δ | Noise floor | Verdict |
|---|---|---|---|---|---|---|---|---|
| P1 | Retention policy affects development | SALIENCE | M7 | 212.000 | 2989.667 | +2777.667 | 0.000 | SUPPORTED |
| P2 | Contradiction is developmental fuel | NO_CONTRADICTIONS | M5 | 2.467 | 2.633 | +0.166 | 0.033 | REVERSED |
| P3 | Curiosity needs explicit questions | NO_QUESTIONS | M5 | 2.467 | 3.733 | +1.266 | 0.033 | REVERSED |
| P4 | Dreams contribute to trajectory | NO_DREAMS | M5 | 2.467 | 1.467 | -1.000 | 0.033 | SUPPORTED |
| P5 | EIG is orthogonal to development | ANTI_EIG | M5 | 2.467 | 2.833 | +0.366 | 0.033 | REVERSED |

**SUPPORTED 2 · REVERSED 3 · NOT INTERPRETABLE 0.** Every prediction was decidable on this metric suite. "Not interpretable" being empty is itself a result: the sensitivity audit and the noise-floor measurement, both done before the run, are what made the five predictions answerable at all.

### 4.2 Removing contradiction's weight raised development

`NO_CONTRADICTIONS` develops **0.166 more new structures per 100 cycles** than `FULL` (2.633 against 2.467), against a floor of 0.033. That is the opposite of the prediction: contradiction, on this account, was supposed to be fuel, and de-weighting it should have starved development.

The result is not a null and not a measurement failure. The intervention is visible where it should be: contradiction *survival* falls from 0.9375 to 0.7500, and the raw contradiction density is near-invariant by construction (15,951.86 against 15,938.80) because the engine keeps the raw count whether or not it is weighted. So the colony does what its name describes, and the development measure moves the wrong way for the theory.

### 4.3 Removing question generation raised it further

`NO_QUESTIONS` develops **1.266 more per 100 cycles** (3.733 against 2.467) — the largest positive movement in the campaign, and roughly eight times the floor. Its question duty cycle is exactly 0.0000 by construction, as it must be. Its mean hypothesis lifetime is 2,978.333 cycles against `FULL`'s 212.0.

This is the reversal that is hardest to explain away as a naming defect, because the mechanism is not a weight or a threshold: the layer is simply absent. On this stimulus, an architecture that asks no questions builds more of everything else.

### 4.4 Lowest-EIG selection developed more than highest-EIG

`ANTI_EIG` develops **0.366 more per 100 cycles** than `FULL` (2.833 against 2.467). The preregistered prediction was that EIG is *orthogonal* to development — that selecting on expected information gain neither helps nor hurts. The measured result is that selecting the **lowest**-EIG experiment helps, relative to the default, by eleven structures per 3,000 cycles. That is not orthogonality; it is a sign reversal.

### 4.5 What did move, and one fragile support

The two supported predictions are informative in their own right. Retention policy moves development massively on M7 — mean hypothesis lifetime 2,989.667 under `SALIENCE` against 212.0 under `FULL` — but the support is **fragile and disclosed as such**: `FULL`'s 212-cycle mean is the mean of exactly **one** belief that died. In every arm, 15 or 16 of the beliefs never die at all. The robust statement is that retention changes *which* beliefs persist, not how long they last; there are almost no deaths to time. Removing dreams, by contrast, lowers development by a full 1.000 per 100 cycles (1.467 against 2.467) and removes far more inventory than the dream count alone, because dreams are built from beliefs. P4's support is the least ambiguous result in the campaign.

### 4.6 The independent arm agrees

Phase K's three families were each chosen to match one of these mechanisms, and the matched ablations all return intervals containing zero:

| Family | Matched ablation | Ablation mean | Organica − ablation | 98.33% interval |
|---|---|---|---|---|
| K1 | organica_NO_QUESTIONS | 0.6018 | -0.0095 | [-0.0328, +0.0140] |
| K2 | organica_NO_FALSIFICATION | 0.3870 | +0.0241 | [-0.0048, +0.0495] |
| K3 | organica_NO_DREAMS | 0.0000 | +0.0000 | [0.0000, 0.0000] |

The primary results are separately reported: all three families are **REVERSED** against the best simple baseline.

| Family | Organica | Best simple baseline | Paired difference | 98.33% interval | Verdict |
|---|---|---|---|---|---|
| K1 | 0.5923 | 0.9360 | -0.3437 | [-0.3773, -0.3123] | REVERSED |
| K2 | 0.4111 | 0.9846 | -0.5735 | [-0.6162, -0.5309] | REVERSED |
| K3 | 0.0000 | 0.8578 | -0.8578 | [-0.8598, -0.8571] | REVERSED |

Two limits keep this from being over-read. The ablations were run **within one implementation** and on tasks where Organica already loses by a wide margin, so a mechanism cannot show an effect that is dominated by something else; and K3's ablation is identical to the decimal because the score was already zero. What the arm does establish is narrower and still important: on the tasks these mechanisms were built for, removing them changed nothing measurable, so they are not what separates the organism from a co-occurrence counter.

## 5. Two readings, and the experiments that separate them

**Reading A — the mechanisms are mis-specified.** Contradiction is implemented as a *weight* in a share-based confidence formula (`support / (support + contradiction)`), so a subject with many successors dilutes every minority expectation below the death threshold; de-weighting contradiction may therefore free belief slots rather than starve development. Questions are capped per cycle, and the belief pool already exceeds its cap, so removing question generation may release capacity rather than remove curiosity. EIG attention ranks by `uncertainty × (1 + novelty)`, a quantity that favours rare and uncertain candidates — which on a periodic stimulus may select noise rather than informative probes. On this reading the theory is not wrong about development; the implementations are wrong about what their own formulas do.

**Reading B — the measure and the architecture interact.** The development measure is an inventory count. Mechanisms that focus attention — contradiction, questions, EIG — narrow what the organism explores, and a narrower search discovers fewer distinct structures even when it discovers better ones. On this reading the reversals are real but they are reversals *of the measure*, not of development: an organism that asks questions may be doing something the inventory cannot see.

The two readings make different predictions, and both are cheap to test.

1. **A world where question generation is load-bearing.** If Reading B is right, there exists a stimulus on which removing questions lowers a breadth measure — for example a world with more independent branch points than the belief cap, where the question layer's focusing is what finds the branches. If no such world exists across a declared ladder, Reading B weakens.
2. **An outcome that is not an inventory.** If the mechanisms matter, they should matter on a held-out behavioural measure, not only on structure counts. Phase K's outcome is external but Organica loses there by a wide margin, which masks mechanism effects; a task within reach of the organism is required to test attribution.
3. **A corrected EIG.** If Reading A is right, an EIG variant that ranks by expected reduction in uncertainty *about the world* rather than by novelty-weighted uncertainty should not reverse. That is a versioned engine change, not a tooling change.
4. **The breadth-controlled measure.** Re-score the same runs on distinct-subject coverage rather than raw count. If the reversals disappear, the finding is about the measure; if they persist, it is about the architecture.

## 6. Limits

- **One seed per colony.** The Tier-1 deltas have no confidence interval; the comparator is the measured noise floor, which is exactly 0.00 within process and 0.033 on M5 between processes. A second seed per colony would test whether the signs are stable, and the campaign did not run one.
- **One stimulus, and it repeats every 9 cycles.** The world offers nothing to reorganise toward after the first cycle, so a plateau and a ceiling are indistinguishable here. The campaign states this as H24 and leaves it untested. Any reversal measured on this world is a reversal at this information content.
- **The development measure is an inventory.** It counts distinct structures discovered, not their quality, use or predictive value. Reading B is a live alternative for exactly this reason.
- **M5 is not a velocity.** It is a finite inventory divided by run length; the campaign corrected the name after the run and the paper uses it only for scale-free comparison.
- **The reversals are about this engine at this scale.** "Reversed" means the measured direction is opposite the prediction in the tested conditions. It does not establish that contradiction, questions or EIG are harmful in general, and the rule-8 disclosure (the contradiction colony de-weights rather than removes) is part of the scope.
- **Phase K's ablations are within one implementation and on tasks already lost.** They corroborate the direction; they do not independently establish it.

## 7. What would change the conclusion

- A second seed per colony reversing any of the three signs.
- A stimulus on which `NO_QUESTIONS` develops *less* than `FULL` on a breadth measure.
- An EIG variant, ranked on a non-novelty quantity, that does not reverse.
- A held-out behavioural outcome on which the mechanisms show a non-zero effect.
- A re-scoring of the same runs on a breadth-controlled measure that removes the reversals.

Any one of these would move the finding from "the motivational layer is not load-bearing here" to "the motivational layer is load-bearing under conditions this campaign did not reach". That is the more interesting outcome, and the design above is what would produce it.

## 8. Implications

For this project, the immediate implication is that the next block should not be another admission variant or another task family. The reversals are a claim about the architecture's own theory, and they are the only results in the corpus that bear on *which internal mechanism, if any, produces development* — the question Phase K left open. Two of the five predictions held, so the motivational layer is not uniformly inert; the campaign locates where it is and is not.

For developmental architectures generally, the transferable lesson is methodological. A system that arrives with a theory of its own development should preregister that theory as directional predictions and disable each mechanism in its own colony. The design is cheap, the verdict rule is a few lines, and without it the same data would have been reported as five confirmations. **The direction check is what turns a sensitivity table into a result.**

## 9. Data, provenance, and citations

Every number in §4's three tables is checked against the artifacts by `tests/test_reversals_paper_numbers.py`, which fails if a row disagrees or if the checker itself cannot fail.

- `docs/verdicts.json` — the five verdicts, per-metric reference and colony values, deltas, noise floor, and the direction-aware verdict field.
- `docs/force_matrix.json` — the six-colony campaign, per-cycle series, provenance and the G1 distinctness verification.
- `docs/FORCE-MATRIX-PREREGISTRATION.md` — the frozen predictions, metrics, gates and noise-floor protocol.
- `docs/FORCE-MATRIX-RESULTS.md` — the campaign record, including the disclosures about `NO_CONTRADICTIONS`, `NO_DREAMS`, and M5.
- `docs/phase_k_results.json`, `docs/PHASE-K-PREREGISTRATION.md`, `docs/phase_k_results.md` — the independent arm, its control, and the matched ablations.
- `docs/EMERGENCE-CRITERIA.md` — the project's definition of emergence and the levels the record can evidence.

**Citations.** This draft makes no external citation. Its claims are about one engine, one stimulus and one committed record, and a literature positioning would have to be written from sources actually read rather than inferred; stating that limit is preferable to a reference list assembled from memory. The companion manuscripts (Papers 01 and 02) carry external references that were each read against a primary record, and the same standard applies here before submission.
