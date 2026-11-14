# A1 successor requirements and refusal checklist

**ID:** `A1-REDESIGN-REQUIREMENTS-1`  
**Date:** 2026-11-14  
**Status:** `REFERENCE — NO FREEZE, NO GRANT, NO RUN`

This is the front door for a second A1 successor candidate. It restates constraints already fixed by the C1/C4 gate, the disposition memo, the N20 rule and the successor preflight. It does **not** choose a design, select targets, reserve seeds, freeze a manifest, issue a grant or run a cell.

## 1. Candidate package

A candidate is a JSON spec with these fields:

| Field | Requirement |
| --- | --- |
| `kind` | `a1_successor_candidate` |
| `id` | A unique candidate ID |
| `seed_block` | At least **six fresh seeds**; not the current six; no duplicate seeds |
| `targets_in_scope` | `true` iff C2/C8 are in scope |
| `per_seed` | Every seed → candidate rows `{edge, A, K}` from a no-arm 120-cycle replay |

The candidate universe must be **one orientation per undirected pair**. Each row is a raw A/K boolean, not a treatment result.

## 2. Machine-readable contract

The schema is [`a1_successor_candidate.schema.json`](a1_successor_candidate.schema.json); the standard-library validator is [`A1-SUCCESSOR-SCHEMA.md`](A1-SUCCESSOR-SCHEMA.md). It checks the candidate package, the seed and universe declarations, the target-selection declaration, and the governance flags, then runs the existing preflight as a separate gate.

```bash
python -m benchmarks.a1_successor_schema --check
python -m benchmarks.a1_successor_schema --validate docs/a1_successor_candidate.json
python -m benchmarks.a1_successor_schema --self-test
```

`--check` verifies the committed schema and page and that the live candidate is structurally valid even when its gate fails. `--validate` is strict: any refusal, including a failing C1 gate, returns non-zero.

## 3. PASS conditions

A candidate passes only if **all** of these hold:

- **Freshness:** the block is not the current six seeds and was not selected, reordered or filtered on the same no-arm A/K that judges it. Any earlier K exposure, including a one-seed timing probe, is disclosed and did not alter the block.
- **Independence:** at least **60 independent edges per seed** after duplicate and reverse-duplicate removal.
- **C1 ceiling:** `min(A available, K available, independent edges) ≥ 60` on **every** seed.
- **Stream integrity:** no duplicate oriented edge, reverse pair or self-loop.
- **Targets, if in scope:** a capacity-respecting **20-row A+K matching** exists on every seed. This proves constructibility only; it does not prove C2 or C8 and does not repair C1.
- **One universe:** the runner, selector and result layer declare and use the same edge universe. The N4/N20 target profile and the 112-row directed cell stream must not silently substitute for the candidate stream.
- **Preflight before freeze:** `A1-SUCCESSOR-PREFLIGHT-1` returns `PASS` **before** any target freeze, seed reservation, grant or run.

## 4. Refusal conditions

Any one of these is a `FAIL`, not a reason to retry:

- `REUSED_CONTROL_SEEDS` — the current six seeds are only the negative control.
- `SEED_SCREENED_ON_K` — the block was chosen or reordered on the no-arm K it is meant to test.
- `UNDISCLOSED_K_EXPOSURE` — a prior probe is omitted from the candidate record.
- `DUPLICATE_EDGE`, `REVERSE_DUPLICATE`, `SELF_LOOP` — the stream is inflated or malformed.
- `INDEPENDENT_BELOW_60` — fewer than 60 independent edges after dedupe.
- `C1_BELOW_60` — the minimum of A, K and independent edges is below 60.
- `TARGET_POOL_BELOW_20` — C2/C8 are in scope but a 20-row matching does not exist.
- `TARGETS_SELECTED_BEFORE_PREFLIGHT` — a candidate spec is not a target freeze.
- `UNIVERSE_INCONSISTENT` — the scorer and the candidate use different edge sets.
- `NO_PREFLIGHT_PASS` — a proposal proceeds without a passing preflight.
- `PASS_TREATED_AS_GRANT` — a PASS is used to freeze, reserve or run.

A candidate that needs a lower floor, a different estimator, a favourable seed subset, or reverse-orientation rows is **not a successor under this checklist**. The 28-tag candidate also shows that a larger universe can fail by **dilution**: more independent edges does not preserve the K rate.

## 5. Current evidence

| Candidate | Independent edges | C1 ceiling by seed | 20-row matching | Result |
| --- | ---: | --- | --- | --- |
| Current six-seed control | 63–64 | 44, 31, 39, 35, 43, 36 | 32, 23, 36, 27, 35, 33 | FAIL 0/6 |
| Fresh block `20650101–20650106` | 63–64 | 40, 37, 46, 42, 31, 38 | 33, 30, 46, 36, 20, 32 | FAIL 0/6 |
| 28-tag larger universe `20660101–20660106` | 158–172 | 23, 40, 42, 55, 47, 37 | 18, 15, 16, 26, 26, 18 | FAIL 0/6 |

The fresh block had **64, 64, 64, 64, 63, 64** independent edges and a 20-row matching on **6/6**; its best seed was still **14 rows short**. The 28-tag candidate cleared the structural **144-edge** target but K collapsed to **23–55** and matching failed on four seeds. The larger-universe route is therefore **tested and failed at this construction**; it does not prove every possible larger world fails, but it removes “just add tags” as a presumed fix.

## 6. Order of operations

```text
candidate spec (no target)
        ↓
successor preflight
        ↓
   PASS ──────► new protocol → freeze → dated grant → run
        │
        └── FAIL ──► park, or a new predeclared candidate
```

A FAIL does **not** license target-selection tricks, a lower floor, a new estimator or a rerun. Those are different studies, not repairs.

## 7. What this is not

This is not a redesign, a target selection, a freeze, a grant or a run. It selects no target, reserves no seed and makes no C2/C8 or treatment claim.

## Reproduce

```bash
python -m benchmarks.a1_successor_preflight --check
python -m benchmarks.a1_successor_candidate --check
```

## References

- [Successor preflight](A1-SUCCESSOR-PREFLIGHT.md)
- [Candidate schema](A1-SUCCESSOR-SCHEMA.md)
- [Fresh-seed candidate](A1-SUCCESSOR-CANDIDATE.md)
- [Disposition memo](A1-DISPOSITION-MEMO.md)
- [Park recommendation](A1-PARK-RECOMMENDATION.md)
- [C1/C4 VOID gate](A1-C1-C4-VOID-GATE.md)
- [N20 competent rule](A1-N20-COMPETENT-SELECTION.md)
- [Pre-freeze checklist](A1-PRE-FREEZE-CHECKLIST.md)
