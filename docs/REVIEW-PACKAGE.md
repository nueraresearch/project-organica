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

1. Read the protocol once without the rest, and mark anything that is not measurable as written.
2. Check the prior-evidence summary against `docs/formation_provenance_study.json` and `docs/phase_k_results.json`.
3. Work through the five questions in the rubric, marking PASS, CONDITIONAL or DEFECT, with a pointer.
4. Write the report into `docs/INDEPENDENT-METHODS-REVIEW.md` §7, including what was not reviewed.
