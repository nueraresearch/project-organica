# G9 stage-ledger validator

**Date:** 2026-11-14  
**Status:** `CONTRACT BUILT — SYNTHETIC FIXTURES ONLY; NO REAL LEDGER, NO SEED, NO G9 DESIGN`

This page documents the validator and its six-row synthetic fixture. It is not a stage map
and not evidence for activation, self-modeling, transfer or external advantage.

## Ledger schema

| Field | Meaning |
| --- | --- |
| `seed` | Fixed seed |
| `edge` | Directed world edge |
| `formed_cycle` | First cycle a candidate structure exists |
| `admitted_cycle` | First cycle the edge is eligible for service, before the cap |
| `served_cycle` | First cycle the edge enters a served window |
| `asserted_cycle` | First cycle the edge appears in the final structure |
| `carrier_cycle` | First cycle a carrier exists; does not change the class |
| `class` | One of A-F, computed from admitted/served/asserted presence |
| `sources` | Per-stage provenance; every present stage must be `observed` |

A missing stage is `null`, never `0`. A missing cycle is not measurable at that stage,
not an early transition. The validator does not infer a missing stage from a later stock.

## Invariants

1. `(seed, edge)` is unique; every edge in the fixed universe has one row for every seed.
2. Every present cycle is an integer in `1..cycles`; missing is `null`; zero is invalid.
3. `formed_cycle` is present for every row.
4. `served_cycle` implies `admitted_cycle`; a served edge cannot be unadmitted.
5. `served_cycle >= admitted_cycle` and `asserted_cycle >= formed_cycle`; carrier timing is free.
6. Every present stage has source `observed`; an absent stage has no source. A final assertion
   cannot fill in a missing service cycle.

The declared `class` must equal the class derived from stage presence. The validator never
trusts a class label on its own.

## Six classes

| Class | Admitted | Served | Asserted | Reading | Fixture edge |
| --- | --- | --- | --- | --- | --- |
| **A** | yes | yes | yes | admitted, served, asserted | `a>b` |
| **B** | yes | no | yes | admitted, never served, asserted | `b>c` |
| **C** | no | no | yes | not admitted, not served, asserted | `c>d` |
| **D** | no | no | no | formed only | `d>e` |
| **E** | yes | no | no | admitted but latent | `e>f` |
| **F** | yes | yes | no | served but not asserted | `f>g` |

## Synthetic fixture

The committed fixture has one row in every class on one seed and the fixed universe:

| Class | Count |
| --- | ---: |
| **A** | 1 |
| **B** | 1 |
| **C** | 1 |
| **D** | 1 |
| **E** | 1 |
| **F** | 1 |

The fixture is `docs/g9_stage_ledger_fixtures.json`. It validates only as a fixture; it is
not a measured ledger and spends no seed.

## Commands

```bash
python -m benchmarks.g9_stage_ledger --write
python -m benchmarks.g9_stage_ledger --check
python -m benchmarks.g9_stage_ledger --self-test
python -m benchmarks.g9_stage_ledger --check-ledger my_ledger.json
```

## CI

CI runs `--check` and `--self-test` next to the A1 readiness step. `--check` validates
the committed fixture, page freshness and six-class coverage; `--self-test` independently
exercises every class and every invariant.

**Not evidence:** Synthetic fixtures for validator self-testing. No engine, seed, cell or real stage ledger is used, and this is not a G9 result.
