# Comparing Organica 0.9.0 and 0.12.0 — pre-registration

**Status: PREREGISTRATION. 2026-11-06. Committed before any comparison cell runs.**
Nothing here may be edited to fit a result. If a protocol has to change it is
amended here, dated, with the reason given — never applied silently in a script.

## 1. The question

Does 0.12.0 acquire and use transferable knowledge better than 0.9.0?

"Better" is not more structure. It is a pre-declared improvement on a held-out
endpoint that the strongest simple baseline does not already win, with the old
build's result kept beside it and labelled. Each experiment returns one of:
**0.12.0 better**, **no difference**, **0.12.0 worse** — and a fourth,
**NOT COMPARABLE**, when the build cannot sustain the protocol at all.

## 2. The builds

| build | tag | commit | identity |
|---|---|---|---|
| 0.9.0 | `v0.9.0` | `af3285423b29780989886f25cf31fad58ab208e4` | frozen blob comparison, `tests/test_v1_freeze.py` |
| 0.12.0 | `v0.12.0` | `5804e609e5978bb6437da79827f14002b006457a` | `docs/engine-identity/0.12.0.json`, `tests/test_engine_identity.py` |

The identity record stores every `organica/**/*.py` blob and sha256 at the tag,
so each build is checkable rather than declared. The live study stays **paused
at 5,396 sleep cycles**; neither build may be run against `memory.db`.

## 3. Protocols selected

| # | question | protocol | harness |
|---|---|---|---|
| A | acquisition | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` Rev 3; T2 compositional is primary, T1 transition is the control | `benchmarks/acquisition_runner.py` |
| B | cross-context reuse | `docs/DECISION-EARNED-SCHEMA-PRIMING.md` (earned evidence) | `benchmarks/cross_context_reuse_benchmark.py` |
| C | held-out prediction | this document freezes the instrument's definitions | `benchmarks/heldout_prediction.py` |
| D | revision | `docs/PHASE-K-PREREGISTRATION.md`, family K2 | `benchmarks/phase_k_campaign.py --families K2` |

These are the four the roadmap names, and each measures a different claim:
asserting relations (A), using prior structure in a new context (B), predicting
held-out events (C), and changing a belief when evidence changes (D).

## 4. Endpoints and decision rules, fixed now

### A — acquisition

* **Primary metric:** log-loss, house shape; the self-cell shape is co-primary.
* **Claim carrier:** T2 (compositional) only. T1 is calibration/control and may
  not support an abstraction claim.
* **Comparator:** the single best configuration across all baseline families,
  selected by independent calibration on seed `20261099`. No parameter is ever
  selected on a scoring window or a confirmatory seed.
* **Statistic:** `d = score(Organica) - score(comparator)`, paired by seed.
  **99% bootstrap interval, 10,000 replicates.**
* **Per-metric verdict:** **Win** if the lower bound is above 0; **Tie** if the
  interval contains 0; **Loss** if the upper bound is below 0.
* **Study verdict:** "reconstruction does work" only if Organica wins on
  transfer and does not lose on retention or revision; "the comparator's
  mechanism wins" if the comparator wins transfer; otherwise "inconclusive".
* **T2 headroom gate:** the lower 99% bound of ceiling minus strongest baseline
  must clear **0.05 nats**. It measured 0.1035 when the task was built.
* **No hidden labels** may enter candidate selection; labels are for scoring.

### B — cross-context reuse

* **Endpoint:** cycles to acquire, persistence, and primed-prediction counts.
* **Primary statistic:** `TR = acquisition(naive) / acquisition(treatment)`;
  `TR > 1` means the treatment acquired faster.
* **Pre-committed bar:** `TR > 1.25` at `p < 0.01` over **10 seeds** — the bar
  the protocol already declared; it was not met at n = 5, and n = 5 is not
  enough to claim it either way.
* **Windows:** phase A 40 cycles, phase B 40 cycles (80 total), as in the
  published run; the harness's 60/60 defaults are not used.
* **Seeds:** `20261101`–`20261110`, the same set for both builds. The first
  five are the published run; the extension to ten is fixed here and is
  disclosed, not chosen after seeing results.
* **Verdict labels:** `REUSE_DEMONSTRATED`,
  `STRUCTURAL_PRIOR_PRESENT_NO_ACQUISITION_ADVANTAGE`, or `NOT_COMPARABLE`.

### C — held-out prediction

* **Protocol, frozen now:** train on cycles 1–200, score cycles 201–300 with no
  model updates; primary metric log-loss over known training tags; Brier and F1
  are diagnostics.
* **Comparator:** the best of the Markov and decayed-count baselines per seed.
* **Statistic:** paired `d` per seed, **99% bootstrap interval, 10,000
  replicates**; Win/Tie/Loss as in A.
* The harness says it is "an evaluation instrument, not a preregistered
  result". This section is what makes it one; the definitions above are frozen
  before its first scored comparison.

### D — revision

* **Endpoint:** Phase K family K2, its own primary endpoint and its own
  strongest-baseline sweep.
* **Decision rule:** `d = Organica - best baseline`, **98.33% paired bootstrap
  interval** (alpha = 0.05/3 across the three families), direction-aware
  **SUPPORTED / REVERSED / UNSUPPORTED / NOT INTERPRETABLE**, exactly as
  `docs/phase_k_results.json` defines them. No new rule is invented here.

## 5. The liveness gate — new, and non-negotiable

The 2026-11-06 diagnosis (`docs/RERUN-0.12.0.md`) showed that 0.12.0's temporal
decay starves the upper layers: beliefs empty by cycle 112 and theories by cycle
40 on the matrix's own stimulus. A comparison scored on a build that is dead for
most of its run is not a null result; it is an unrun experiment.

**Before any cell is scored,** the build is run on that protocol's stimulus for
the full horizon and must satisfy both:

1. at least one theory in the final 10% of cycles, and
2. mean beliefs over the final 10% of cycles of at least 2.

If either fails, the cell is **NOT COMPARABLE**, is excluded, and is never
reported as zero. No partial scoring is allowed.

| protocol | horizon (cycles) | 0.12.0, as tagged |
|---|---|---|
| B cross-context | 80 (40 + 40) | expected to pass (theories persist through cycle 79) |
| A acquisition | the protocol's frozen windows | must be measured; expected to fail above ~112 |
| C held-out | 300 | expected to fail (theory population is 0 after cycle 40) |
| D revision (K2) | 300 | expected to fail |

The last three are therefore **blocked on the decay fix**, not on the comparison
design. The gate is what converts that into a stated limit instead of a fake
loss.

## 6. Same analysis, disclosed confound

Each build runs its **own committed harness**, because the harness is part of the
build and the sleep API changed between the tags. The **scoring and analysis
code is one script**, written before either run and applied unchanged to both
artifacts; its sha256 is recorded in both result files. Harness differences are
a confound and are disclosed in every result. An improvement is attributed to
the engine only if it clears the liveness gate and survives the shared analysis;
otherwise the result says the two moved together and does not attribute a cause.

## 7. Seeds, configuration, and naming

* The same seed set is used for both builds in every experiment.
* `PYTHONHASHSEED=0` in every process; worker count and wall time recorded.
* Identical stimulus and cycle counts per arm; no tuning on scoring data.
* Artifacts are named by build (`*.v090.json`, `*.v0120.json`) and are never
  merged into one verdict file.

## 8. Reporting rules

* All four experiments are reported, including the ones that could not run.
* No composite score, no cherry-picking, no re-scoring of the published
  `v0.9.0` artifacts.
* "0.12.0 is better" requires at least one primary **win** with its lower bound
  above its bar **and** no primary **loss** anywhere else.
* A failure of the liveness gate is `NOT COMPARABLE`; a genuine tie is a tie.

## 9. Stop condition

No engine change during the comparison. Afterwards, one mechanism at a time —
starting with candidate selection, as the roadmap directs — each with its own
pre-registration; exploratory variants stay exploratory until a confirmatory
test is specified.

## 10. Status at registration

* `0.12.0` identity: recorded and checked; the freeze gap is closed per version.
* Liveness: 0.12.0 holds through 80 cycles and dies by 112. Three of the four
  protocols sit above that horizon.
* **No cell has been run.** Cross-context (80 cycles) is the only eligible cell,
  and it is deliberately not run yet: the decay fix would change its result, so
  the comparison waits for a stable 0.12.x build.
