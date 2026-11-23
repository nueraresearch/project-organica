# The confidence-formula amendment — results

**Reading: R3 — void.** Control C2 fired: across all 288 cells the
amendment produced **no measurable change in G5 appearance**. By §8 of the
pre-registration nothing here may be read as support for, or evidence against,
the amendment. The diagnostic below says *why* the control fired, which is a
fact about this harness rather than a result about the formula.

A second defect was found while checking this document against its artifact and
is reported in full below: **the `real_git_history` stream is not pinned**, so
its cells mixed corpus states and the earlier claim that G5 appears there under
the frozen engine cannot be reproduced. That claim is withdrawn as a property of
the stream.

**The engine is unmodified.** `organica/` is byte-identical to `v0.9.0`,
`tests/test_v1_freeze.py` is green, and every posterior arm is an in-process
override in `benchmarks/confidence_posterior.py`.

## What was run

The pre-registered grid: three arms (`share`, `jeffreys`, `laplace`) over six
unchanged cold-start streams, twelve confirmatory seeds `700001001`–`700001012`,
40 cycles per cell — 288 cells once the `share_reimplemented`
control is included. Every cell completed.

| Control | Result |
|---|---|
| C1 — the zero-prior copy reproduces the frozen engine | **passed**, 0 mismatching cells at the resolution it compares (G5 timing, final populations, belief counts) |
| C2 — the independent variable is live | **failed** |
| C3 — the baseline stream is reachable | **passed** |

## G5 by stream and arm

`share` is the frozen engine; `share_reimplemented` is the alpha = beta = 0 copy
that C1 compares against it.

| Stream | Arm | Median final confidence | Median final beliefs | Cells reaching G5 |
|---|---|---|---|---|
| `baseline` | `share` | 0.3187 | 14 | 12/12 |
| `baseline` | `share_reimplemented` | 0.3187 | 14 | 12/12 |
| `baseline` | `jeffreys` | 0.4713 | 13 | 12/12 |
| `baseline` | `laplace` | 0.9999 | 13 | 12/12 |
| `no_branch` | `share` | 0.7222 | 7 | 0/12 |
| `no_branch` | `share_reimplemented` | 0.7222 | 7 | 0/12 |
| `no_branch` | `jeffreys` | 0.7222 | 7 | 0/12 |
| `no_branch` | `laplace` | 0.7222 | 7 | 0/12 |
| `cold_start` | `share` | 0.4259 | 6 | 12/12 |
| `cold_start` | `share_reimplemented` | 0.4259 | 6 | 12/12 |
| `cold_start` | `jeffreys` | 0.4259 | 6 | 12/12 |
| `cold_start` | `laplace` | 0.4259 | 6 | 12/12 |
| `cold_start_unbranched` | `share` | 0.7552 | 6 | 0/12 |
| `cold_start_unbranched` | `share_reimplemented` | 0.7552 | 6 | 0/12 |
| `cold_start_unbranched` | `jeffreys` | 0.7552 | 6 | 0/12 |
| `cold_start_unbranched` | `laplace` | 0.7552 | 6 | 0/12 |
| `real_git_history` | `share` | 0.4827 | 5 | 12/12 |
| `real_git_history` | `share_reimplemented` | 0.4824 | 5 | 12/12 |
| `real_git_history` | `jeffreys` | 0.4827 | 5 | 12/12 |
| `real_git_history` | `laplace` | 0.4818 | 5 | 12/12 |
| `wide_lookback` | `share` | 0.7845 | 8 | 0/12 |
| `wide_lookback` | `share_reimplemented` | 0.7845 | 8 | 0/12 |
| `wide_lookback` | `jeffreys` | 0.7845 | 8 | 0/12 |
| `wide_lookback` | `laplace` | 0.7845 | 8 | 0/12 |

## The diagnostic: the override is live, and these streams do not dilute

On `baseline` the override **is** live: the median final confidence of surviving
beliefs moves from 0.3187 under the share to
0.4713 under Jeffreys and
0.9999 under Laplace, while the median belief count
moves from 14 to 13.
The formula does what it says it does.

On the streams that carry the question the arms barely move: `wide_lookback` and
`cold_start_unbranched` are identical in every arm at
0.7845 and
0.7552, and `real_git_history` shifts by
0.0009
from the share to Laplace, with the G5 count unchanged across arms. All of them
sit far above the death threshold of 0.15. **There is no dilution to correct.**
The share does not drive these beliefs toward death in the first place, so
replacing it cannot change which of them survive.

That is the substantive finding, and it is a diagnostic rather than a result: the
account in which the share dilutes minority expectations below the threshold
describes the **live study** — where settled confidence sits around 0.16–0.17 —
not a 40-cycle cold-start stream, where a subject has few successors and the
share stays high. The amendment was tested where the mechanism is not active.

## The stimulus was not pinned, and one premise went with it

`real_git_history` is built from this repository's own commit messages, read at
run time. Nothing pins that corpus, and the grid was resumed in more than one
invocation, so its cells can mix corpus states. Two measurements say so.

**First, the control's confidence differs on this stream in the stored cells**
and on no other: the median is 0.4824
for the copy against 0.4827 for the engine, with
identical maxima and identical belief counts. The pre-registered C1 compares G5
timing, populations and counts — not confidence — so it did not see this.

**Second, the stream no longer produces what was stored.** Re-running all twelve
`real_git_history` seeds for every arm on one pinned corpus
(328 events, `a8bd3d3afcfa`) gives **G5 in 0/12 cells** for the
frozen engine and 0/12 and 0/12 for
the posterior arms, with a median confidence of
0.4458 and
4 beliefs — against
0.4827 and
5 beliefs in the stored cells. The same
check, with confidence compared as well as counts, finds
**0 confidence-level C1 mismatches**. On a pinned corpus the copy is
exact; the stored discrepancy is a property of the unpinned stream, not of the
copy.

**What this costs.** The stored result that the frozen engine reaches G5 in
12/12 cells on the unengineered stream is true of
the corpus those cells ran on and **is not reproducible afterwards**. The claim
that G5 does not require an engineered branch point therefore **cannot be
supported from this study**, and is withdrawn rather than restated: at the corpus
that can be pinned, the stream reaches G5 0/12. The other
five streams are synthetic and fixed, so nothing else in the grid is affected,
and the void reading does not depend on this stream at all — C2 fired on the
five fixed streams alone.

## What this does not license

- It does not say the amendment is wrong, useless, or right: C2 fired, so the
  study is void by its own rule.
- It does not revise Paper 01. That engine is unchanged and its claims stand as
  measured; this is a separate record about a separate question.
- It does not settle whether G5 is architectural. It shows that the cold-start
  harness cannot see the mechanism the amendment targets.
- It does not license quoting the stored `real_git_history` figure as a
  reproducible fact about the stream.

## What a testable version requires

A stream in which subjects have **many successors**, so the share actually
dilutes — the regime the live study occupied at 0.16–0.17 confidence — and a
belief population large enough that the retention budget is not the binding
constraint. It also requires a **pinned** corpus: the commit list recorded with
its hash, so a cell can be re-derived. That is a new pre-registration with a new
seed block. This one is closed and its grid is not re-run.

## Provenance

- Protocol: `docs/CONFIDENCE-POSTERIOR-PREREGISTRATION.md`, committed unrun.
- Harness: `benchmarks/confidence_posterior.py`.
- Artifact: `docs/confidence_posterior.json`. Every figure above is substituted
  from it, and `tests/test_confidence_posterior_results.py` re-derives each one.
- Pinned re-check: `docs/confidence_posterior_pinned.json`.
