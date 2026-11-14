# A1 successor candidate schema

**ID:** `A1-SUCCESSOR-SCHEMA-1`  
**Status:** `REFERENCE — MACHINE-READABLE CONTRACT; NO FREEZE, NO GRANT, NO RUN`

The JSON Schema is the external contract for a candidate. The validator adds the cross-row and governance rules that JSON Schema cannot express, then runs the existing no-arm preflight as a separate gate.

**Schema:** [`a1_successor_candidate.schema.json`](a1_successor_candidate.schema.json)

## Commands

```bash
python -m benchmarks.a1_successor_schema --check
python -m benchmarks.a1_successor_schema --validate docs/a1_successor_candidate.json
python -m benchmarks.a1_successor_schema --self-test
```

`--check` verifies the schema artifact and page, and verifies the live candidate is structurally valid. `--validate` returns a non-zero status for any refusal, including a failing gate. Schema validity and gate success are reported separately.

## Refusal codes

| Code | Meaning |
| --- | --- |
| `REUSED_CONTROL_SEEDS` | uses one of the current six control seeds |
| `SEED_SCREENED_ON_K` | declares a K-screened block |
| `UNDISCLOSED_K_EXPOSURE` | omits the prior K exposure declaration |
| `DUPLICATE_EDGE` | repeats an oriented edge |
| `REVERSE_DUPLICATE` | contains both orientations of one pair |
| `SELF_LOOP` | contains a self-edge |
| `INDEPENDENT_BELOW_60` | fewer than 60 independent edges on a seed |
| `C1_BELOW_60` | C1 ceiling below 60 on a seed |
| `TARGET_POOL_BELOW_20` | no 20-row A+K matching while targets are in scope |
| `TARGETS_SELECTED_BEFORE_PREFLIGHT` | the candidate already selects targets |
| `UNIVERSE_INCONSISTENT` | selector, runner and scorer do not agree |
| `NO_PREFLIGHT_PASS` | preflight is not declared as required |
| `PASS_TREATED_AS_GRANT` | the spec claims a freeze, grant or run |
| `SCHEMA_NOT_OBJECT` | the candidate is not a JSON object |
| `SCHEMA_KIND` | the candidate kind is wrong |
| `SCHEMA_ID` | the candidate has no ID |
| `SCHEMA_TARGETS_IN_SCOPE` | targets_in_scope is not boolean |
| `SCHEMA_SEED_BLOCK` | the seed block is malformed |
| `DUPLICATE_SEED` | the seed block repeats a seed |
| `TOO_FEW_SEEDS` | fewer than six seeds |
| `SEED_BLOCK_MISMATCH` | per_seed does not match the seed block |
| `SCHEMA_PER_SEED` | per_seed is not an object |
| `SCHEMA_ROWS` | a seed has no row list |
| `SCHEMA_ROW` | a row has the wrong fields or non-boolean A/K |
| `INVALID_EDGE` | an edge does not match tag>tag |
| `SCHEMA_SELECTION` | the selection declaration is missing or malformed |
| `SCHEMA_GOVERNANCE` | the governance declaration is missing or malformed |
| `SCHEMA_BASELINE` | the baseline is missing or is not a no-arm replay |
| `SCHEMA_STATUS` | the status is not a candidate specification |
| `SCHEMA_DATE` | the date is not YYYY-MM-DD |
| `GATE_UNREADABLE` | the preflight could not read the candidate |

A schema-valid candidate may still fail the gate; the current fresh block does, at C1 **40, 37, 46, 42, 31, 38**. A gate PASS would still not freeze, grant or run anything.

**Not evidence:** a schema and validator. They select no target, reserve no seed, freeze no target, issue no grant and run no cell.

