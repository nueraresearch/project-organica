# Phase K replication on `0.15.0` — registration and owner authorisation

**Status:** `AUTHORISED 2026-11-19 — BUILD-LABELLED REPLICATION`
**Authorisation:** the owner's instruction of 2026-11-19: *"require the Phase K
re-run to pin both engine and harness. Then authorize and run that replication
on 0.15.0."*
**Protocol:** [`PHASE-K-PREREGISTRATION.md`](PHASE-K-PREREGISTRATION.md),
**unchanged** — K1, K2 and K3; seeds `20261023`–`20261032`; 300 / 300 / 600
cycles at cycle scale 1; the same baselines, grid, 98.33% decision intervals and
terminal outcomes.
**Result:** `docs/phase_k_results_0.15.0.json` — a **new** path.
**Checkpoint:** `docs/phase_k_results_0.15.0.ndjson` — a **new** path.
**Provenance:** `docs/phase_k_results_0.15.0.provenance.json`.

## 1. What this is, and what it is not

This is a **replication of the frozen protocol on a different build**. It is
not an amendment to the preregistration, not a re-score of the `0.9.0`
campaign, and not a replacement for `docs/phase_k_results.json` — that artifact
is frozen and is never read or written by this run. The preregistration's
decision rule is applied as written; the only thing that changes is the build
the rule is applied to, and that change is the reason the run exists.

The question it answers: **do the three `REVERSED` verdicts survive the 22
engine commits since `v0.9.0`?** Either answer is decision-relevant.

## 2. Pins — both are required

**Engine.** Package version `0.15.0`; `docs/engine_pin.json` must be clean
(`python -m benchmarks.engine_pin --check`); the result is written through
`benchmarks.engine_stamp.stamp`, so the artifact carries `engine_version`,
`engine_commit`, `engine_sha256` and `engine_tree_sha256`.

**Harness.** `benchmarks/phase_k_campaign.py` is pinned by git blob and
SHA-256 in the provenance sidecar, recorded **before the first cell and again
after the last**, and the two must agree. A run whose harness moved is not a
replication; it is a mixed-build artifact and may not be reported.

If either pin moves, the result is `VOID` for replication purposes and the
record says which pin failed. The K0 control and the endpoint ceiling check
also run before any cell; either failing stops the run, as the protocol
requires.

## 3. Fixed invocation

```
PYTHONHASHSEED=0 python -m benchmarks.phase_k_campaign \
    --families K1 K2 K3 --seeds 10 --workers 8 --scale 1 \
    --out docs/phase_k_results_0.15.0.json
```

`--resume` may continue an interrupted run on the same output path; it may not
change the family set, seed block, cycle scale or engine build. The K2 block's
harness, treatment and registration are untouched by this record.

## 4. What this authorises

One replication block: 30 cells (3 families × 10 seeds) and their K0/ceiling
preflight. No engine change, no new version, no new seed, no new threshold,
no change to the K2 block or its spent grant, and no V2 work.
