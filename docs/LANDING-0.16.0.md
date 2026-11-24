# Landing 0.16.0: support-gated co-occurrence admission, one ranked list, partition deleted

**Status: LANDED** on 2026-11-20 (`3e2412f`). The package is `0.16.0`, the Layer-1 cap is still
`112`, `docs/engine_pin.json` names 0.16.0 over fourteen files at
`716da31be3f304715c3ecbd4063dcac44abb54e1`, and the four canaries were re-recorded on those bytes.
**No campaign cell ran.** The granted `COOCCURRENCE-A-T1` block (`20261300`–`20261309`, 20 cells at
floor 35) stays unrun and is not part of this landing.

## The state this landing departed from

Captured from the 0.15.0 records and preserved in `docs/block_canaries_0.15.0.json`:

| Item | Value |
| --- | --- |
| Package version | `0.15.0` |
| Layer-1 cap | `112` |
| Pin version | `0.15.0` |
| Pin: files / head | `14` files / `fb701f48b9d593256559f30395c5ccfad7f17cae` |
| Canary engine sha256 | `d4eeefcfabe6a947db7715d3c50b1053d6a4fa4f0eccfa8ad622dbfe13540711` |

| Block | 0.15.0 digest |
| --- | --- |
| `PRESENCE-CAP-1` | `a32ae3bc3d00dd4fc54a39f3a5629d1f237b900944c9a96e32a2685ad2b70f8d` |
| `PRESENCE-CONSTRUCT-1` | `8ffefa8d1ec7957ebe82124225648a95ab350fcc07e2b93bffd81736d9a06486` |
| `PRESENCE-CONVERSION-1` | `3d8d83ed6f723c81573525778cb44d9d9816ea0aec7c2056937657c170dc965f` |
| `PRESENCE-CONVERSION-2` | `f8ead12b63221c9db5b261b7969f8797b4ceb4ad1b44d67cce415b8036972aca` |

## The state the landing produced

Derived from the same files after the landing:

| Item | Value |
| --- | --- |
| Package version | `0.16.0` |
| Layer-1 cap | `112` |
| Pin version | `0.16.0` |
| Pin: files / head | `14` files / `716da31be3f304715c3ecbd4063dcac44abb54e1` |
| Canary engine version | `0.16.0` |
| Canary engine sha256 | `25843ded68f50e90ad04bd80df4ade86f57d31eb7ed61ef77d6d7f4fedfe4236` |

| Block | 0.16.0 digest | Moved? |
| --- | --- | --- |
| `PRESENCE-CAP-1` | `ec226cc8c0e82f38e7325bf6b64b78996d297c094e6e3fcf9eae9ae800fa94f4` | yes |
| `PRESENCE-CONSTRUCT-1` | `3aad6ce7d6316053e5799eb97d26f0fb8d1b4b13cd247217b429874497871aeb` | yes |
| `PRESENCE-CONVERSION-1` | `edfd3f1eca2803927e555fb2c05ee6f405ac0448ee2cfcf35533c8e852123a7f` | yes |
| `PRESENCE-CONVERSION-2` | `f8ead12b63221c9db5b261b7969f8797b4ceb4ad1b44d67cce415b8036972aca` | no, by design |

`PRESENCE-CONVERSION-2` is the refusal canary: it reads no cap and no prediction list, so the
admission law cannot reach it. Unchanged is the correct reading there.

## 1. The admission law

`_build_predictions` now admits a temporal relation only when its unordered pair co-occurs within an
event at least `PREDICTION_COOCURRENCE_FLOOR = 35` times, serves **one** list ranked by temporal
count with the existing source/target tie-break, and truncates at `MAX_PREDICTIONS = 112`.
`transition_budget`, the co-occurrence quota and the backfill are deleted, because there is no
longer a window to divide, and every admitted candidate carries `is_cooccurrence: true`.

The floor is the owner's, registered as `CONSTRAINT-COOCCURRENCE-A-T1-1` and granted one 20-cell
block on 2026-11-20 (`docs/COOCCURRENCE-A-T1-GRANT.json`). This landing implements the decision; it
does not run the block and does not adjudicate the constraint.

The presence gates keyed to the two populations (`transitions + cooccurrences = 112`,
`transitions >= 56`, `cooccurrences <= 56`) no longer describe a window. They must be re-expressed
before a block reads them; no gate was relaxed or re-derived here.

## 2. Re-pin the engine

```
python -m benchmarks.engine_pin          # records version, head_at_pin, pinned, files
python -m benchmarks.engine_pin --check  # must report 14 files at version 0.16.0
```

The pin reports fourteen files at 0.16.0. The edit added no engine module; `sleep_extraction.py` is
the only file whose bytes the admission law changed.

## 3. Re-record the canaries, and what moved

```
python -m benchmarks.block_canaries --write
python -m benchmarks.block_canaries --check
```

The predecessor digests are quoted above and the 0.15.0 file is archived whole at
`docs/block_canaries_0.15.0.json`. Three digests moved; the refusal canary did not.

**The move is not incremental, and it is recorded as a finding.** Every cell canary now serves an
**empty prediction list**: `S_ever` world edges are `0` (was `86`, `106` and `106`), and
`median_window` at cap 40 is `0.0`. On these 120-cycle Gate-13 worlds no pair reaches the
within-event co-occurrence floor of 35, so `_build_predictions` admits nothing. Assertion still
happens through the non-prediction route, so asserted world edges are `18`/`18`/`20` — and all of
them are bypass (`asserted_without_admission` is `18`, `18` and `20`, against `2`, `0` and `0`).

That is a true statement about the build on those worlds, not a failure of the re-record: the
canary's job is to turn red when behaviour changes, and it did. It also means these three canaries
no longer exercise the prediction path at all, so they cannot detect a change inside it. A future
canary needs a world or window in which the floor is reachable; that is a follow-up, not a repair
made here.

## 4. The change-map row

`docs/engine_change_failure_map.json` gains row `M16`, claiming `3e2412f`, with the mechanism and
both decisions sourced from the 0.16.0 changelog and the `K1S` registration
(`docs/constraint_registrations/CONSTRAINT-COOCCURRENCE-A-T1.json`). The recorded failure is the
K1 same-build gap `-0.623961` in `docs/PHASE-K-REPLICATION-0.15.0-RESULT.md`.

The map now covers **23** commits in **16** rows (12 staying, 4 excluded), and
`docs/ENGINE-CHANGE-AUDIT.md` quotes the derived count. `python -m benchmarks.change_map --check`
recomputes coverage from git and passes; no cell was run to write the row.

## 5. The V2 scorer re-pin

`docs/v2_first_cell_scorer_pin.json` re-pins `organica/sleep_extraction.py` from
`56da7e2930347c323688803a77e26aa94ff4d23b6394ddebd14d33ccc17ac788` to
`b6b06ed13a1cc3d5dc146e27e3597c71f70ad5b2563847ca694a756f3a7efac2`, keeping the departure
digest and naming the 2026-11-19 `REVERSAL`. `docs/v2_first_cell_result.json` is not edited: its
`scorer_pin_ok: true` is a fact about the 0.15.0 build. The re-pin keeps the pin honest; it
authorises no cell, and a cell on 0.16.0 needs its own dated authorisation and a fresh statement of
what the design now measures.

## 6. The frozen records

- The three cap-40 records (`PRESENCE-CONSTRUCT-1`, `PRESENCE-CAP-1`, `PRESENCE-CONVERSION-1`) keep
  `recorded_version 0.14.0`, `recorded_cap 40` and the `1fc7be8f…` digest, and their
  `build_superseded` blocks now name `0.16.0` at cap 112. The `date` is the 0.16.0 landing date,
  with `first_superseded_on: 2026-11-11` and `first_superseded_by: 0.15.0` preserving the earlier
  move. No verdict, threshold, grant or measurement moved.
- `docs/LANDING-0.15.0.md` is marked superseded by this record; its check accepts it as the 0.15.0
  record it is and requires it to name its successor.
- `docs/cap112_admission_plan.json` stays at `build.version 0.15.0` as a historical plan, and its
  `decision` step is closed from `DECISION-ADMISSION-STEP`, not re-targeted to 0.16.0.
- `docs/USER-MANUAL.md` was updated in the same turn with a revision row.

## 7. Verify

```
python -m pytest tests -q
python -m benchmarks.engine_pin --check
python -m benchmarks.block_canaries --check
python -m benchmarks.engine_lineage --check
python -m benchmarks.change_map --check
python -m benchmarks.presence_cap112_prereg --check
python -m benchmarks.test_count
git diff --check
```

## Stop conditions

- the pin fails, or reports a file count other than 14;
- a canary digest that *can* move does not move — `PRESENCE-CONVERSION-2` is the refusal canary and
  is expected unchanged, while a non-move of `PRESENCE-CAP-1` would have been a finding, not
  confirmation;
- the version declarations disagree, or the changelog entry is missing;
- any campaign cell starts: the `COOCCURRENCE-A-T1` block is granted and unrun;
- a verdict, an artifact or a measurement is re-scored to fit the new build.

## Rollback

Revert the engine file, the three version declarations and the changelog section, re-record the pin
and the canaries from the 0.15.0 state quoted above (the archived file restores it exactly), restore
the three `build_superseded` blocks to `0.15.0`, and revert the V2 pin to the departure digest. No
tag exists to move, and no campaign cell ran. Record the abandoned attempt in the manual's revision
log; never restore a digest silently.

## What this does not do

- It does not run any campaign cell, including the granted `COOCCURRENCE-A-T1` block.
- It does not tag, publish or deposit anything.
- It does not claim the new admission law improves K1, or any other quantity. That is the block's
  question, and `M16` names the falsifier.
- It does not re-score any 0.14.0 or 0.15.0 verdict, and it does not claim 35 is the right floor.
- It does not re-express the two-population presence gates; they are recorded as needing
  re-expression before a block reads them.
