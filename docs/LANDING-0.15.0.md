# Landing 0.15.0: cap 112, re-pin, canary re-record and attribution

**Status: LANDED** on 2026-11-11. The package is `0.15.0`, `SleepService.MAX_PREDICTIONS` is
`112`, `docs/engine_pin.json` names 0.15.0 over fourteen files, and the canaries were re-recorded
on those bytes. `DECISION-CAP-LEVEL` stays PENDING: landing a level is not promoting a decision,
and this landing adds no lineage link.

## Preconditions

- The tree was clean and the suite green before the landing; the pre-landing run recorded 2020
  passed, 6 skipped, 0 failed.
- No cap-112 cell was running or started: the three records stay `FROZEN, NOT RUN`.
- `DECISION-CAP-LEVEL` records choice C, and the 2026-11-11 cap-112 grant names the comparator, Q1
  and Q2. Both are true; neither substitutes for the other.
- The three cap-112 records are `FROZEN, NOT RUN`, granted, with their runners built and gated.

## The state this landing departed from

Captured on 2026-11-11, derived from `docs/engine_pin.json` and `docs/block_canaries.json`:

| Item | Value |
| --- | --- |
| Package version | `0.14.0` |
| Layer-1 cap | `40` |
| Pin version | `0.14.0` |
| Pin: files / head | `14` files / `fb701f48b9d593256559f30395c5ccfad7f17cae` |
| Canary engine sha256 | `1fc7be8fae436fa154ce8a142412ffaeb8f54768f3b3ceaacd18d457b13f33f2` |

Canary digests before the landing, preserved here because `docs/block_canaries.json` now holds the
0.15.0 rows:

| Block | 0.14.0 digest |
| --- | --- |
| `PRESENCE-CAP-1` | `a32ae3bc3d00dd4fc54a39f3a5629d1f237b900944c9a96e32a2685ad2b70f8d` |
| `PRESENCE-CONSTRUCT-1` | `c2388cfe9e784bc24fbc851acd62b6301fb1c1a2af2ec3c593a8d6b251ba73ad` |
| `PRESENCE-CONVERSION-1` | `87c6af27aec428c60587894667d16bad9a3e8d910d9f11189149b85bc9f95739` |
| `PRESENCE-CONVERSION-2` | `f8ead12b63221c9db5b261b7969f8797b4ceb4ad1b44d67cce415b8036972aca` |

## The state the landing produced

Derived from the same files after the landing:

| Item | Value |
| --- | --- |
| Package version | `0.15.0` |
| Layer-1 cap | `112` |
| Pin version | `0.15.0` |
| Pin: files | `14` |
| Canary engine sha256 | `d4eeefcfabe6a947db7715d3c50b1053d6a4fa4f0eccfa8ad622dbfe13540711` |

| Block | 0.15.0 digest | Moved? |
| --- | --- | --- |
| `PRESENCE-CAP-1` | `a32ae3bc3d00dd4fc54a39f3a5629d1f237b900944c9a96e32a2685ad2b70f8d` | no, by design |
| `PRESENCE-CONSTRUCT-1` | `8ffefa8d1ec7957ebe82124225648a95ab350fcc07e2b93bffd81736d9a06486` | yes |
| `PRESENCE-CONVERSION-1` | `3d8d83ed6f723c81573525778cb44d9d9816ea0aec7c2056937657c170dc965f` | yes |
| `PRESENCE-CONVERSION-2` | `f8ead12b63221c9db5b261b7969f8797b4ceb4ad1b44d67cce415b8036972aca` | no, by design |

The two unchanged digests are a correction to this checklist's own stop condition, disclosed
rather than smoothed over: `PRESENCE-CAP-1` passes an explicit `cap: 40` arm, so the shipped
constant cannot reach that cell, and `PRESENCE-CONVERSION-2` is a refusal canary that reads no cap.
For both, unchanged is the correct reading. A cap that is inside a cell always moves that cell; it
cannot move a cell that pins the level or returns before measuring.

## 1. Bump the version

Edited all three declarations and the changelog together, because `tests/test_versioning.py` fails
unless they agree:

- `organica/__init__.py` -- `__version__ = "0.15.0"`
- `pyproject.toml` -- `version = "0.15.0"`
- `CITATION.cff` -- `version: 0.15.0`
- `CHANGELOG.md` -- `## [0.15.0] — (unreleased)` with the cap change, its decision reference and
  its canary attribution.

No tag was cut, and the changelog heading still says `(unreleased)`.

## 2. Change the cap

`SleepService.MAX_PREDICTIONS` is `112` in `organica/sleep.py`. This is a cognition change under
AGENTS.md rule 2 and is authorised by `DECISION-CAP-LEVEL`; the changelog entry cites it. No other
engine constant, method or ordering was changed.

## 3. Re-pin the engine

```
python -m benchmarks.engine_pin          # records version, head_at_pin, pinned, files
python -m benchmarks.engine_pin --check  # must report 14 files at version 0.15.0
```

The pin reports fourteen files at 0.15.0: the split `sleep_*` modules and `candidates.py` were
already covered, and the edit added no engine module.

## 4. Re-record the canaries

```
python -m benchmarks.block_canaries --write
python -m benchmarks.block_canaries --check
```

Two digests moved and two did not, for the reasons stated above. The `--check` re-runs all four
cells on the installed bytes and passes.

## 5. Attribute the move

- The move is the level, **not** E1. E1's proof is the preserved record
  `docs/block_canaries_0.14.0_e1.json`; the changelog says the digests moved because the cap
  changed.
- The predecessor digests are quoted above, so the 0.14.0 state remains readable after
  `docs/block_canaries.json` was overwritten.
- **No lineage link was added for the level.** A link requires an ADOPTED decision, and
  `DECISION-CAP-LEVEL` is PENDING. The 0.14.0 E1 link cannot carry this build either, because the
  cap is a behaviour change: it is retired to `docs/engine_lineage_0.14.0.json`, and
  `docs/engine_lineage.json` carries no links.

## 6. Bring the frozen records with the landing

- The comparator, Q1 and Q2 records at cap 112 were amended with a dated `cap-landed` row: the
  level is landed, the preflight is met, and the runners are runnable. Their status stays
  `FROZEN, NOT RUN`, their grant stands, and no cell was started.
- The cap-40 records (`PRESENCE-CONSTRUCT-1`, `PRESENCE-CAP-1`, `PRESENCE-CONVERSION-1`) were
  amended, never edited or re-scored: each carries a dated `build_superseded` block naming the
  0.14.0 cap-40 build, and its checks accept that build explicitly instead of the shipped one.
  `benchmarks/build_supersession.py` is that one acceptance point.
- `docs/USER-MANUAL.md` was updated in the same turn: status line, file map and revision log.

## 7. Verify

```
python -m pytest tests -q
python -m benchmarks.engine_pin --check
python -m benchmarks.block_canaries --check
python -m benchmarks.engine_lineage --check
python -m benchmarks.presence_cap112_prereg --check
python -m benchmarks.test_count
git diff --check
```

The suite, the pin, the canaries, the lineage and the cap-112 records must all pass before the
landing is reported. `tests/test_versioning.py` is the version check; it was not weakened.

## Stop conditions

This is the list the landing was held to, with the one correction the landing forced:

- the pin fails, or reports a file count other than 14;
- a canary digest that *can* move does not move -- but a cell that pins the cap (`PRESENCE-CAP-1`)
  or refuses before measuring (`PRESENCE-CONVERSION-2`) is expected unchanged, and this checklist
  originally stated the rule too broadly;
- the version declarations disagree, or the changelog entry is missing;
- any cap-112 cell starts running: the runners are runnable after the landing but no cell was run;
- a verdict, an artifact or a measurement is re-scored to fit the new build.

## Rollback

Revert the engine file, the three version declarations and the changelog section, re-record the pin
and the canaries from the pre-landing state quoted above, restore `docs/block_canaries.json` and
the 0.14.0 lineage link, and remove the `build_superseded` blocks. No tag exists to move, and no
cap-112 cell ran. Record the abandoned attempt in the manual's revision log; never restore a
digest silently.

## What this does not do

- It does not run any cap-112 cell; the runners became runnable, and no cell was started.
- It does not tag, publish or deposit anything.
- It does not promote `DECISION-CAP-LEVEL` from PENDING or add a lineage link.
- It does not re-score any cap-40 verdict, and it does not claim 112 is necessary or optimal.
