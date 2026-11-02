# Review package — contents and cover sheet

**Status: assembled. No reviewer appointed. No result from the protocol exists.**

This package exists so that an external researcher can assess the proposed experiment without
reconstructing the project. It is **not** a paper, and receiving it is **not** peer review for publication:
this review asks whether the experiment deserves to be run; publication review asks whether a finished
contribution deserves to be published. The project takes the first before the second.

## 1. The five components

| Component | Where it is | Purpose |
| --- | --- | --- |
| 1. Experimental protocol | `docs/STRUCTURE-BEHAVIOR-DESIGN.md` | defines exactly what will be tested: hypothesis, variables, estimand, model, controls, rejection |
| 2. Prior evidence summary | §2 of this document | what Organica has already established, reversed and left unmeasured, with artifact pointers |
| 3. Relevant artifacts | the package table in `docs/INDEPENDENT-METHODS-REVIEW.md` §4 | the underlying evidence, each file checked to exist |
| 4. Reviewer rubric | `docs/INDEPENDENT-METHODS-REVIEW.md` §3 and §5 | the five questions, the defect conditions, and the three outcomes |
| 5. Review report | `docs/INDEPENDENT-METHODS-REVIEW.md` §7 | the record the reviewer fills: item verdicts, conditions, outcome, signature |

## 2. Prior evidence summary

Read this as the state of the record, not as support for the hypothesis. Each row names the artifact that
carries it.

| Claim | Status | Artifact |
| --- | --- | --- |
| Developmental structure forms and varies with experience | **supported within the tested scope** | `docs/V1-SYNTHESIS.md` §2 |
| A structural property is associated with later **world content** (does the pair occur in a window never shown) | **supported once**: difference 0.214061, 98.33 % interval [0.195886, 0.228119], permutation control including zero, 15 seeds, all gates passed | `docs/formation_provenance_study.json` |
| Structural displacement responds to the strength of competing groups | **measured** (K3: 9–11 of 18 gold pairs at late weight 3 / early weight 1, against 0–1 otherwise) | `docs/phase_k_results.json`, restated in `docs/V1-SYNTHESIS.md` §5 |
| Belief revision against a strong baseline | **reversed**: 0.4111 against 0.9846, difference −0.5735, 98.33 % interval [−0.6162, −0.5309] | `docs/phase_k_results.json` |
| A structural property predicting the organism's **own later behaviour** | **not established for any structural variable** | this protocol is the first test |
| Stability of any such relation across generating configurations | **not established** | — |
| Within-run resolution versus between-world replication | **measured**; the 100-cycle window is the adopted, provisional convention | `docs/SCALING-LADDER.md` §§8–10 |
| Whether this block can resolve the relation it proposes to test | **computed before any seed**: a rank relation of 0.50 needs **48 worlds per configuration** at the 0.90 bar (p = 0.902), and that is a **floor**; at reliability 0.80 it is 79. No engine ran, no seed was spent | `docs/sign_resolution_structure_behavior.json` |
| A causal role for structure | **not attempted** | §1 of the protocol |

## 3. What the package deliberately does not contain

- **No result from this protocol.** None exists; §6 of the review document forbids producing one before the
  outcome is recorded.
- **No draft paper.** A protocol paper is a later decision, and writing one now would invite the reader to
  read a proposal as a finding.
- **No summary that replaces an artifact.** Where a document restates a number, the artifact that owns it is
  in the package.

## 4. Checking the package without trusting it

```bash
python -m pytest tests/test_structure_behavior_design.py tests/test_independent_methods_review.py tests/test_review_package.py -q
```

The tests assert that the protocol contains its nine required elements, that every artifact the package names
exists, that the prior-evidence numbers match `docs/formation_provenance_study.json`, and that the review
record still states the three outcomes and the exclusion of the author.

## 5. What the reviewer should do, in order

0. If you are not in this field, or are short of time, read `docs/REVIEW-PRIMER.md` first —
   five minutes, no jargon, and it names the two hard things rather than hiding them.
1. Read the protocol once without the rest, and mark anything that is not measurable as written.
2. Check the prior-evidence summary against `docs/formation_provenance_study.json` and `docs/phase_k_results.json`.
3. Work through the five questions in the rubric, marking PASS, CONDITIONAL or DEFECT, with a pointer.
4. Write the report into `docs/INDEPENDENT-METHODS-REVIEW.md` §7, including what was not reviewed.

## 6. The feasibility result, and how to read it

The protocol's §6 carries this, and it belongs in the package rather than in the protocol alone, because a
reviewer asked to approve a block of a given size must be able to see where the size came from.

- **What the number is.** `0.902` is the simulated frequency with which this protocol's decision rule
  resolves a rank relation of 0.50 at 48 worlds per configuration — Spearman rho, an interval from
  resampling worlds at 98.33 %, resolved only when that interval excludes zero with the predicted sign. It
  is not a posterior probability, not a p-value, and not a claim about the engine: no engine ran.
- **It is a floor, not a target, and the curve is not a product rule.** Classical error in the predictor
  multiplies the Pearson correlation by `sqrt(reliability)`; the Spearman value follows from
  `(6/pi) asin(rho_g/2)`. That curve is computed and checked by Monte Carlo to within 0.021:

| `DI` reliability | Observed relation (Spearman) | Worlds per configuration |
| --- | --- | --- |
| 1.00 | 0.50 | 48 |
| 0.90 | 0.47 | 54 |
| 0.80 | 0.45 | 62 |
| 0.70 | 0.42 | 72 |
| 0.60 | 0.39 | 85 |
| 0.50 | 0.35 | 104 |
| 0.40 | 0.31 | 131 |
| 0.30 | 0.27 | 177 |

- **The predictor's reliability is unmeasured.** That column is the price of a quantity nobody in this
  project has measured, and measuring it is a prerequisite the reviewer should expect to see discharged
  before a block of this size is bought.
- **Exchangeability is an assumption with a diagnostic, and its direction is measured, not assumed.**
  Per-configuration analysis removes across-configuration clustering and says nothing about dependence within
  one. The artifact simulates a shared component and reports the resolution probability under individual-world
  and contiguous-block resampling; the difference (+0.033, +0.000, -0.013) is inside Monte-Carlo noise, so no direction is
  claimed, and the block must report lag-1 dependence on seed order plus both intervals.
- **No size has been chosen.** The computation constrains the claim; it does not authorise spending.

## 7. Reading the record directly

The repository is public, so nothing here has to be taken on trust and nothing has to be attached:

```bash
git clone https://github.com/nueraresearch/project-organica
cd project-organica && git checkout 1051313
python -m pytest tests/test_structure_behavior_design.py tests/test_sign_resolution_behavior.py \
                  tests/test_independent_methods_review.py tests/test_review_package.py -q
```

`1051313` is the commit at which the numbers in this package were computed. Read the repository at the
commit you are sent, not at whatever `master` happens to be: later commits may correct wording, and the
correction is recorded rather than absorbed, but a reviewer checking a number should know which state they
checked it in.
