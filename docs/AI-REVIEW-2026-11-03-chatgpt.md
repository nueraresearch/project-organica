# Machine methodological pre-pass — Stage B, second model family

**Model:** ChatGPT. Reported by the owner; the exact backend version is not recorded in this repository.
**Date:** 2026-11-03
**Commit reviewed:** `39adb24`, on the pass's own evidence — it reproduces the eight ladder counts, reports the
endpoint resolution computed as a proportion, and says the prompt still requires two model families. All three
describe the state before `e6334dc` and before the block decision.
**Transcript:** outside this repository, at the path the owner supplied. It is **not committed**, nothing below
quotes it verbatim, and the findings are the owner's summary of it — each checked against this tree before any
change was made.
**Record status:** machine pass. Not the independent methods review; §7 of the review brief stays empty.

## Findings and dispositions

### 1. The endpoint-resolution calculation treats the scorer as a proportion — already fixed, at `e6334dc`

A blocking finding against `39adb24`, and correct there: the resolution section claimed a `1/count` quantum while
`benchmarks/acquisition_compositional.py`'s `score()` returns an averaged pairwise binary log loss. It was fixed
before this pass ran — §3.1 withdraws the quantum and the 5.3-quantum margin in place, `stage_b_protocol.py` no
longer emits the claim, the test asserts its absence, and `benchmarks/stage_b_endpoint_precision.py` measures the
per-world standard error by a cluster bootstrap over withheld transitions instead of dividing by `sqrt(N)`.
Disposition: **no action; the pass read a pre-fix pin.**

### 2. The eight ladder counts reproduce the published table — confirmed

Recomputed here from the artifact: 48, 54, 62, 72, 85, 104, 131, 177 at reliabilities 1.00 to 0.30. Agreement is a
check on the arithmetic, not on the bootstrap resolution.

### 3. The 104-world block does not establish the all-four-configuration result — valid, blocking, and live at HEAD

The finding is right and it was not right only against the old pin. The ladder prints a **per-configuration** share,
but §7's outcome table requires the predicted sign with an interval excluding zero **in every claimed configuration**.
The probability that the study can report its own required result is therefore the conjunction across the four, and a
per-configuration share of `p` gives roughly `p^4`:

| worlds per configuration | resolves per configuration | conjunction `p^4` | lower 1.96-sigma bound | clears 0.90 |
| --- | --- | --- | --- | --- |
| 104 | 0.895 | 0.639 | 0.579 | no |
| 120 | 0.931 | 0.752 | 0.696 | no |
| 150 | 0.975 | 0.904 | 0.847 | no |
| 160 | 0.978 | 0.913 | 0.859 | no |
| **180** | **0.998** | **0.990** | **0.971** | **yes** |
| 200 | 0.995 | 0.980 | 0.953 | yes |

The block was therefore reset from 120 to **180 worlds per configuration** — 720 worlds, 373,320 cycles — by the
same lower-bound rule, restated on the conjunction and re-applied in `stage_b_protocol.py`, which now records every
tested size with both quantities (`block_floor_rule.by_size`). The ladder and its 48-world floor are unchanged.
Limits recorded: only the six sizes in the table were simulated, so 180 is the smallest **tested** size; and the
multiplication assumes the configurations resolve independently, which follows from each being its own worlds under
its own seeds.

### 4. Sustention-rule agreement, seed discipline, empty §7 — confirmed

The 0.972 agreement is correctly excluded from the reliability arithmetic, the pre-assigned/allocated/reserved
distinction holds with substitution prohibited, and §7 is empty with the machine status labelled. No action.

## Disposition

| finding | disposition |
| --- | --- |
| 1 proportion-versus-log-loss | already fixed at `e6334dc`; pass read a pre-fix pin |
| 2 ladder arithmetic | confirmed; no change |
| 3 block does not resolve the all-four claim | confirmed at HEAD; rule restated on the conjunction; block reset to 180 |
| 4 construct, seeds, §7 | confirmed; no change |

## What this pass does not establish

It is a machine pass, not a human reviewer, and its own transcript says it reviewed a single-family package. It does
not approve anything, §7 stays empty, no seed is allocated, no world is generated and no relation is computed.
Stage B remains unauthorised, and step 2 of `docs/DECISION-STAGE-B-SEQUENCE.md` remains the owner's.
