# Arm B-prime: implementation-to-artifact audit

**Status: generation 1 withdrawn as void, generation 2 run, and the arm is
inadmissible by its own pre-registered gate. No conclusion about H2 may be drawn
from it.**

## 1. What the record claimed, and what the code did

At `e2206e5` the record stated that Arm B-prime had been built: `canonical_score`
added to the mode choices, and generation-1 artifacts showing F2 at 0 differences in
168 comparisons, C2 and C3 passing, and F1 firing on every one of the eight seeds.

The mode was never implemented. In `benchmarks/divergence_mechanism.py` at that
commit:

- `CANONICAL_MODES` did not exist anywhere in the file; `--mode` accepted
  `canonical_score` only as an argparse choice.
- `_load_temporal` gated graph canonicalisation on `self.MODE == "canonical"`, so
  `canonical_score` fell through to `graph = super()._load_temporal()`.
- `_compose_meta_concepts` gated on `self.MODE != "canonical"`, so
  `canonical_score` ran the engine's own body unchanged.
- `_score_tags` applied **no intervention at all**: it recorded
  `[s.tag for s in out]` from `super()` and returned `out` untouched. There was no
  sort by `(-frequency, tag)` anywhere on that path.

`canonical_score` was therefore behaviourally **identical to `observe`**, and every
generation-1 number is an artifact of that:

- **F2 = 0 of 168** compared `observe` against `observe`.
- **C2 and C3 passed for free** — the build under test was the observe build.
- **Gate 4's "F1 fires"** reproduced Arm A exactly: first difference at cycle 1 in
  `score_tags`, membership identical. That is what an observe-against-observe
  comparison must produce on these pairs.

The check that exposed it: both sides score `cedar = 1` and `fern = 1`, and applying
the documented `(-frequency, tag)` order collapses the lists into agreement. The
differences were hash order among tied scores, not different frequency inputs.

## 2. The fault belongs to the record, not to the engine

`git diff -- organica/` was empty throughout; the freeze held and Organica 1 is
untouched at `v0.9.0`. The failure is the partial-application mode this repository
already warns about: the docstring described an intervention, argparse accepted its
name, and no code applied it — so artifacts downstream inherited a **label with no
mechanism behind it**, and a reader of those artifacts could not tell.

## 3. The fix

- `CANONICAL_MODES = ("canonical", "canonical_score")`, and both canonical branches
  now test membership rather than string equality with `canonical`.
- `_score_tags` sorts the value the frozen engine returned by `(-frequency, tag)`
  **before recording it**, so the record and the downstream builders both receive the
  intervened order.
- Every score record carries `score_intervention`: the mode, `total_order_applied`,
  `graph_canonical`, and `adjacent_ties` — how many adjacent equal-frequency pairs the
  order had to break. A record can no longer claim an order that was not applied, and a
  world with no ties would show the intervention had nothing to do.
- `ORGANICA_NO_RECORD=1` disables recording, so C2 compares the same build and the
  same intervention with the trace on against the trace off, rather than reusing the
  observe-only neutrality check.

## 4. Generation 2, measured with the intervention in place

| Step | Result |
|---|---|
| F2 — control seed, fixed hash seed | **125 of 168 comparisons differ: F2 fires** |
| C2 — recording off vs on, same build | identical admitted streams, both arms |
| C3 — repeat at one hash seed | identical parts |
| Telemetry | `total_order_applied` true in every score record; 153 adjacent ties broken on the control, 203 on the sweep seeds |
| Gate 4 — eight seeds at their recorded pairs | **8 of 8 invariant, 0 differences: P3 holds, F1 does not fire** |

**Composition of the 125 differences, recorded as a fact and not as a re-reading of
the gate.** 79 are order-only (membership identical, position differs) and
46 change membership. By type — order-only / membership-changing:
anomalies 14/2, loops 0/22, meta 0/22, predictions 19/0, score_tags 22/0, temporal_read 24/0.
`concepts` never differs. **Restating F2 in membership terms would therefore change
what the gate returns**, which is precisely why that restatement is the owner's
decision and not mine.

## 5. What §11 requires now

Brief §11 wrote the rule before the gate ran: *"If canonicalisation changes the
control's per-type table at a fixed hash seed, F2 fires and no conclusion may be drawn
from Arm B-prime."* It also named the conflict in advance: F2 requires the control's
table to be unchanged at a fixed hash seed, the control's order is itself hash-seed
dependent (P2 failed as pre-registered), so any real canonicalisation must move it, and
F2 and P2 cannot both hold.

That is exactly what happened. **The arm is inadmissible by its own control, and the
decision is the protocol's:** F2 restated in membership terms, or Arm B-prime abandoned.
Choosing between them after seeing that P3 holds would be the same defect as choosing
a criterion after seeing the data.

## 6. What is settled, and what is not

**Settled.** The generation-1 artifacts are void and are named as such in journal §85
and §86. The intervention now runs and is visible in telemetry. F2 fires. Under the
pre-registered gate the arm is inadmissible. Under the intervention, the eight seeds'
tables are hash-seed invariant as measured.

**Not settled.** Whether H2 is true. The table `T2/20261120` stays `indeterminate`, the
window is not widened, D0 is not re-scored, and the invocation is unrefuted — an
inadmissible arm is not evidence against a claim either.

## Artifacts

`divergence_arm_b_prime_f2_v2.json`, `divergence_arm_b_prime_gates_v2.json`,
`divergence_arm_b_prime_sweep_v2.json` (generation 2); the `_v2`-less files are
generation 1 and are void. `.scratch/run_bprime_v2.py` is the runner.

## 7. Closed by decision — 2026-11-01

**The owner closed Arm B-prime as inadmissible under its pre-registered stop rule.
F2 is not restated, and the arm is not run again.**

- **The stop rule fired and stands.** Canonicalisation changed the control's output at
  a fixed hash seed (125 of 168 comparisons, including
  membership changes), so under §11 no conclusion may be drawn from the arm. Rewriting
  F2 afterwards would be re-scoring a gate after seeing its result; it is not done.
- **The eight-seed result is kept as a diagnostic observation, not evidence.** All
  8 of 8 seeds became hash-seed invariant under the
  intervention, and that is recorded as what it is: a statement about this
  intervention on these seeds. **Hash-invariant does not mean correct**, and the
  protocol does not license reading stability as an explanation of the divergence,
  in either direction.
- **The line is stopped.** No further runs on this arm. The question of hash-order
  effects is not abandoned, but it may only return under a **new protocol** that
  measures both hash-seed invariance *and* the intervention's effect on candidate
  membership, on **fresh seeds**, with acceptance criteria written before the run.
- **What this leaves in place.** `T2/20261120` stays `indeterminate`, the search window
  stays unwidened, D0 stays unscored, the onset/mechanism/V2 work stays closed, and
  Organica 1 stays frozen at `v0.9.0`.

