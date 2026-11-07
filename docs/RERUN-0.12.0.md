# Rerun of the claim-bearing experiments on Organica 0.12.0

**Status: STOPPED AT THE PRECONDITION — 2026-11-06.** The rerun was started and
halted after the first two colonies. It is **not** a result, and no paper is
updated from it.

## Outcome

On `v0.12.0` the reference arm stops developing at **cycle 112**. Beliefs,
contradictions, support and confidence are non-zero only through that cycle and
are empty for the remaining 2,888 cycles of a 3,000-cycle run; theories are
non-zero only through cycle **37**. On `v0.9.0`, under the same harness, every
one of those series is live through cycle 2,999.

A campaign whose reference arm is empty for 96% of its run cannot rank the five
preregistered predictions, and its zeros are not evidence of a null. The
campaign's own precondition said so in the log — and the script wrote the
artifact and exited 0 anyway.

## What is frozen

| Item | Value |
|---|---|
| Commit | `5804e609e5978bb6437da79827f14002b006457a` |
| Tag | `v0.12.0` (peels to the commit above) |
| Engine version | 0.12.0 |
| Protocols | Unchanged from `docs/FORCE-MATRIX-PREREGISTRATION.md`, `docs/PHASE-K-PREREGISTRATION.md`, `docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`, `docs/AUDIT-TRACE-SPEC.md` |
| `PYTHONHASHSEED` | `0` in every process (common-mode across arms) |

The protocols are **read, not amended**. A rerun that changes a metric or a gate
is a different study, and none is changed here.

## Seeds and configuration

| Experiment | Seeds | Configuration | Status |
|---|---|---|---|
| Tier-1 force matrix | `20261023` | 3,000 cycles, stimulus `lattice_L1`, 6 colonies | **stopped after 2 colonies** |
| Phase K matched ablations | `20261023`–`20261032` (10 per family) | 3 families, 300 cycles per unit, 10,000-replicate paired bootstrap | not started — same engine |
| Phase L plasticity–coherence | `20261023`–`20261052` (30 per point) | 8 support-ratio points, 240 cells | not started — same engine |

## What was run

Two colonies of the Tier-1 matrix, one seed, `PYTHONHASHSEED=0`, 3,000 cycles
each, written to `docs/rerun-0.12.0/parts/`:

```bash
PYTHONHASHSEED=0 python benchmarks/force_matrix.py --cycles 3000 --seed 20261023 \
    --colonies FULL     --out docs/rerun-0.12.0/parts/FULL.json
PYTHONHASHSEED=0 python benchmarks/force_matrix.py --cycles 3000 --seed 20261023 \
    --colonies SALIENCE --out docs/rerun-0.12.0/parts/SALIENCE.json
```

Both exit 0. `FULL` reports `TDC=0.012 QDC=0.012 CD=131.9489 CS=0.0 DV=1.9
gen=8 life=58.278` after 152.5 s.

## The evidence

Series are per cycle, length 3,000, from the two per-colony artifacts.

| Quantity | `v0.9.0` (`docs/force_matrix.json`) | `v0.12.0` (this run) |
|---|---|---|
| Theory duty cycle, whole run | 0.9997 | 0.012 |
| Cycles with any theory | 2,999 / 3,000 | 37 / 3,000 |
| Cycles with any belief | 2,999 / 3,000 | 112 / 3,000 |
| Last cycle with a contradiction | 2,999 | 112 |
| Contradiction density, mean | 15,938.80 | 131.95 |
| Contradiction survival | 15 of 16 | 0 of 18 |

The same run at 300 cycles returns `TDC=0.123`, which is the expected value of a
series that dies at cycle 37; the decay is not specific to the long run.

## Why the campaign did not stop itself

`benchmarks/force_matrix.py:655` appends `FULL produced no theories -- the
reference arm is broken` to its `problems` list and prints it, but the run
writes its artifact and exits 0. G1 **did** detect the failure here — the
warning is printed before the colony's metrics in the log — so the defect is
enforcement, not detection: a non-empty `problems` list is reported, not treated
as a failed precondition, and a campaign whose reference arm was just declared
broken still produces a result file. A campaign must fail closed on its
reference arm.

## Consequence for the papers

- **Paper 07** — not re-measurable on this build: both of its claim-bearing
  experiments (the matrix and the Phase K ablations) sit downstream of the dead
  reference arm.
- **Paper 01** — not re-measurable: Phase L measures the retention of exactly
  the structures that empty at cycle 112.
- **Paper 02** — not re-measurable: the audit trace reconstructs selections that
  stop occurring after cycle 112.

The manuscripts keep their `v0.9.0` measurements, which they already label as
measurements of that build. **No paper is updated from this run**: substituting
a dead-arm zero for a measured effect would be a fabricated null, not a rerun.

## Diagnosis (2026-11-06)

The cause is `MemoryService.decay_temporal_edges(factor=0.95)`, called once
per cycle at `organica/sleep.py:331`. It does not exist at `v0.9.0`.

The chain, measured cycle by cycle on the matrix's own stimulus and seed:

1. Every cycle multiplies every temporal edge count by 0.95. Total edge mass
   falls from 1,729 to ~1,270 and then plateaus, because arrivals and decay
   reach an equilibrium.
2. Prediction strength is a **ratio**: `ratio = count / max(source_freq, 1)`,
   `cand_strength = min(1.0, ratio)` (`organica/sleep_extraction.py:453, 465`).
   The numerator is the decayed temporal count; the denominator is the
   cumulative frequency of the source tag, which keeps growing. A decaying
   numerator over a growing denominator is monotone decay by construction:
   the median prediction strength falls 0.70 -> 0.31 by cycle 30 and 0.18 by
   cycle 79.
3. `stable_prior` keeps candidates with strength >= `STABLE_THRESHOLD = 0.3`
   (`organica/sleep.py:183-185`). Stable predictions fall 21 -> 15 (cycle 30)
   -> 12 (cycle 35).
4. `_compose_processes` finds cycles among the stable predictions; with the
   triangles' edges dropping below the filter, processes fall 13 -> 3,
   workflows 12 -> 3, and pre-retention beliefs 18 -> 6.
5. Layer 5 needs at least two hypotheses per subject; theories reach **0 by
   cycle 40**.
6. The 2026-11-06 supersession amendment makes the loss permanent:
   carried-forward structures stop counting as current evidence, so the last
   six beliefs decay x0.8 and retire by cycle 112 (0 of 18 contradiction-bearing
   structures survive).

### The counterfactual

| Same run, 80 cycles | cycle 30 | cycle 79 |
|---|---|---|
| shipped (`0.95`) | 15 stable predictions, 9 processes, 5 theories | 12, 3, 0 |
| decay disabled in the harness (`1.0`) | 21, 10, 5 | 21, 10, 5 |

With decay disabled the run holds 21 stable predictions, 10 processes, 10
workflows, 22 hypothesis objects (7 of them structural markers) and 5 theories
for all 80 cycles, and edge mass grows 1,819 -> 6,981. Clearing
`carried_forward` alone does not fix it: it only delays the collapse (theories
fall at cycle 65 instead of 40) and still loses them.

So this is neither a crash nor a metric defect. It is a stationary stimulus
producing a monotone sub-threshold equilibrium: decay lowers the numerator
while the denominator grows, so a `stable` set cannot be stable at any
horizon.

### Fix options (engine change, owner decision)

1. **Decay only unreinforced edges.** The pass currently decays every edge in
   the same cycle that extraction reinforces it; excluding the current cycle's
   reinforced edges removes the ratchet with the least change to Law VI.
2. **Make strength a transition probability**, `count / out_counts[source]`,
   which is already computed as `trans_prob`, instead of a count over
   cumulative frequency.
3. **Slow the decay** to a factor whose equilibrium clears the filter for the
   stream's arrival rate - a parameter fix, not a mechanism fix.
4. **Keep decay and lower `STABLE_THRESHOLD`** - not recommended: it hides a
   monotone trend behind a threshold rather than removing it.

All four have since been measured side by side in `docs/DECAY-FIX-OPTIONS.md`
(300 stationary cycles plus a vocabulary shift). Option 2 was the only arm alive
at 300 cycles, but on 2026-11-06 the owner kept it as a lead candidate only:
`docs/DECAY-FIX-CONFIRMATION-PREREGISTRATION.md` fixes a separate-seed threshold
calibration and a degree-stratified held-out run before any engine change. None
is applied. The engine is frozen under rule 12, and a change to the selection
path is the owner's decision (rule 2).

## What must happen before a rerun

1. Choose and implement one of the fixes above, with a test that a stationary
   world's stable set does not decay (`benchmarks/prediction_decay_probe.py` is the pattern).
2. Make the campaign's reference-arm check fail closed.
3. Re-run in the order matrix -> Phase K -> audit probes -> Phase L.

## Artifacts

`docs/rerun-0.12.0/parts/FULL.json`, `docs/rerun-0.12.0/parts/SALIENCE.json` and
their logs; `benchmarks/prediction_decay_probe.py` reproduces the diagnosis. The `v0.9.0` artifacts (`docs/force_matrix.json`,
`docs/verdicts.json`, `docs/phase_k_results.json`, `docs/phase_l_results.json`)
are unchanged.

**Closed 2026-11-07.** Item 2 is implemented: `benchmarks/force_matrix.py`
exits non-zero when G1 finds the reference arm dead, when the arm is missing,
or when the reference colony's own trace holds no theory in its final tenth of
cycles; `benchmarks/run_matrix.py` refuses to launch on a G1 problem and fails
after merging a dead `FULL` row. The artifact is still written so the failure
has a record, but the exit status no longer reports success. On the current
build `--verify-only` exits 1, because the reference arm is still dead at G1 -
the decay rule this document diagnosed has not been fixed, so the campaign
remains blocked. `tests/test_force_matrix_exit.py` covers the dead, missing,
late-dead and live cases.
