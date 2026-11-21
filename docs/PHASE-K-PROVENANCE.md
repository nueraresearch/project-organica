# Phase K results — provenance record

**Artifact:** [`docs/phase_k_results.json`](phase_k_results.json)  
**Artifact SHA-256:** `cab5891fcc861c0ecf353f4b781e217928f160704932dae53843faf9a05a14ac`  
**Frozen:** yes — included in `tests/test_v1_freeze.py`. This sidecar is separate; the artifact itself was not modified.

## Build

| Field | Value |
|---|---|
| Engine version | `0.9.0` |
| Engine tree | `25d9e50173b108b2d961bf621a6823778f9753cd` |
| Artifact commit | `190233f3c2ff9e5da65bf14d6964f59c123b1182` (2026-10-24) |
| Tag relationship | the `organica/` tree at the artifact commit is identical to the tree at tag `v0.9.0`; the tag was cut later that evening |

The artifact carries no `engine_version`, `engine_commit`, `engine_sha256` or
`runner` field. It predates `engine_stamp`; this record supplies the missing
attribution from the commit that recorded the result rather than retroactively
editing a frozen artifact.

## Harness

| Field | Value |
|---|---|
| Module | `benchmarks/phase_k_campaign.py` |
| Harness blob at artifact commit | `843cc924ca9e09e109bca995b29603fda76fa3df` |
| Recorded invocation | `PYTHONHASHSEED=0 python benchmarks/phase_k_campaign.py --families K1 K2 K3 --seeds 10 --workers 12` |
| Protocol | [`docs/PHASE-K-PREREGISTRATION.md`](PHASE-K-PREREGISTRATION.md) |

The artifact’s protocol block independently records ten seeds, twelve workers,
`PYTHONHASHSEED=0`, 10,000 bootstrap replicates and `complete: true`. The
harness has changed since the run, so the blob above — not the current working
tree — is the historical harness identifier.
