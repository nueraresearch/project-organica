# Phase K replication on `0.15.0` — result

**Status: `COMPLETE` — all three families `REVERSED` on the shipping build.**

This is the build-labelled replication authorised in
[`PHASE-K-REPLICATION-0.15.0.md`](PHASE-K-REPLICATION-0.15.0.md). The frozen
protocol ([`PHASE-K-PREREGISTRATION.md`](PHASE-K-PREREGISTRATION.md)) is
unchanged — same families, same grid, same 98.33% decision intervals, same
terminal outcomes — and the same ten seeds (`20261023`–`20261032`), so this is
a **build replication with paired seeds**, not a seed generalisation. The
`0.9.0` artifact [`phase_k_results.json`](phase_k_results.json) was not read or
written by the run.

## 1. Verdicts

| Family | Organica | Best simple baseline | Paired diff | 98.33% interval | Matched ablation | Verdict |
|---|---|---|---|---|---|---|
| K1 incremental world modeling | 0.312011 | 0.935972 | −0.623961 | [−0.646675, −0.599907] | 0.312011 | `REVERSED` |
| K2 belief revision | 0.176471 | 0.984615 | −0.808144 | [−0.823529, −0.785068] | 0.176471 | `REVERSED` |
| K3 longitudinal integration | 0.235788 | 0.857808 | −0.622021 | [−0.630928, −0.611828] | 0.237528 | `REVERSED` |

Every decision interval lies wholly below zero, so all three are clean losses
under the pre-registered rule. The matched no-questions ablation is identical
to Organica on K1 and K2 and 0.00174 above it on K3; `mechanism_implicated` is
false for all three, as it was on `0.9.0`.

**The pre-registered terminal outcome repeats:** no family was confirmed, so no
task is carried to a larger-n campaign, **no V2 is designed from these
families**, and the negative-results map grows. This is the second time the
protocol has returned this outcome, on a different build.

## 2. What the build changed, and what it did not

| Family | `0.9.0` Organica | `0.15.0` Organica | `0.9.0` gap | `0.15.0` gap |
|---|---|---|---|---|
| K1 | 0.5923 | 0.312011 | −0.3437 | −0.623961 |
| K2 | 0.4111 | 0.176471 | −0.5735 | −0.808144 |
| K3 | 0.0000 | 0.235788 | −0.8578 | −0.622021 |

The sign of every verdict is unchanged. K1 and K2 widened their gaps; K3
narrowed its gap from a structural zero but remains far behind its baseline.
No family came within 0.62 of its baseline, and no family's interval contains
zero. The `0.9.0` figures are the frozen campaign's; the comparison is a
build reading, not a re-score of that campaign.

**One cross-check worth recording.** The K1 paired gap here is `−0.623961`,
the exact live K1 comparator value the K2 block recorded when its registered
`−0.343658` failed to reproduce. That independently confirms the block's
build-drift finding from a clean, complete campaign. It does **not** make the
K2 block evidence: the block remains `VOID` on `G4`, no criterion was read, and
nothing here rescues it.

## 3. Pins and provenance

| Item | Value |
|---|---|
| Engine | `0.15.0`, commit `fb701f48b9d593256559f30395c5ccfad7f17cae` |
| Engine digest | `d4eeefcfabe6a947db7715d3c50b1053d6a4fa4f0eccfa8ad622dbfe13540711` (the stamped digest over the pinned file map) |
| Engine pin | `docs/engine_pin.json`, SHA-256 `375b7056304b54ac6980d2fed80ba76bd7a715082cc11fa2e2bc66161d553221`; `--check` clean, 14 files at `0.15.0` |
| Harness | `benchmarks/phase_k_campaign.py`, git blob `77a45d002fd55475948e03b47faefb85d4347a2c`, SHA-256 `fa0b0324…aad0637f` — identical before and after the run |
| Protocol | `docs/PHASE-K-PREREGISTRATION.md`, unchanged versus HEAD; SHA-256 pinned in the sidecar |
| Artifact | `docs/phase_k_results_0.15.0.json`, SHA-256 `8fdd532011adce1bc41e768fff2b15d7fd11bc574a673f96d2b83b03a0b58be8` |
| Checkpoint | `docs/phase_k_results_0.15.0.ndjson`, 30 rows |
| Preflight | control `organica 0.401363` vs `markov 0.504039` (`organica_loses: true`); all three endpoint ceilings `1.000000` |
| Run | 30 cells, 8 workers, `PYTHONHASHSEED=0`, cycle scale 1, wall clock 414.1 s |

Full digests and the pin comparison are in
[`phase_k_results_0.15.0.provenance.json`](phase_k_results_0.15.0.provenance.json);
`pins.match` is `true`. A moved engine or harness pin would have made this
result `VOID` for replication purposes; neither moved.

## 4. What this settles, and what it does not

**Settles.** For K1, K2 and K3 on `0.15.0`, the negative map is current-engine
evidence: the engine loses to the best simple baseline by a wide, unambiguous
margin on every family, with the same mechanism-null ablations as before. The
build did not produce a positive external result.

**Does not settle.** It says nothing about seeds outside the frozen ten, about
a seventh task family, or about K2's mechanism question, whose one block is
`VOID` and remains so. It is not an adjudication of the band/allocation
evidence or of `DECISION-ADMISSION-STEP`. It does not authorise V2 or any new
campaign; those remain owner decisions.

**Where it lives.** Artifact
[`docs/phase_k_results_0.15.0.json`](phase_k_results_0.15.0.json), provenance
[`docs/phase_k_results_0.15.0.provenance.json`](phase_k_results_0.15.0.provenance.json),
authorisation [`docs/PHASE-K-REPLICATION-0.15.0.md`](PHASE-K-REPLICATION-0.15.0.md).
The frozen `0.9.0` artifact and its provenance are untouched.
