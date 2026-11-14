# C6 assertion-timing instrumentation

**Status: OBSERVER BUILT AND SIX-SEED BLOCK RUN — `C6 ORDER VARIATION CONFIRMED`; N1–N7 PASS.**

This document specifies the measurement needed to clear `C6_temporal_resolution`. The observer and
its neutrality/mutation harness are implemented in `benchmarks/c6_timing_observer.py`. A one-seed
preflight and a fresh six-seed block have been run; the block is recorded in
[`C6-TIMING-BLOCK.md`](C6-TIMING-BLOCK.md). No engine file has changed.

## 1. What C6 needs

`C6` requires that `K` and `Y` be ordered at the same cycle resolution. The existing records do not
carry an assertion cycle: `docs/assertion_carrier_trace.json` records carrier formation
(`formation_cycle`) but not when the edge was asserted. The preflight therefore classified `C6` as
`REQUIRES INSTRUMENTATION`; the observer now exists, and the six-seed block below clears that
timing requirement.

A timestamp alone is not enough. The readout must avoid a circular definition of `Y`.

## 2. The circularity problem

The engine's full assertion readout is `structure_edges(candidates)`. A loop or dream carrier
contributes its own edges to that readout. If `Y_full(c, e)` means "edge `e` appears anywhere in the
cycle-`c` structure readout", and `K(c, e)` means "a loop/dream carrier for `e` exists at cycle `c`",
then for a carrier-borne edge:

```text
K(c, e) = 1  ->  Y_full(c, e) = 1
```

in the same cycle. The two are not merely correlated; one is part of the definition of the other.
C6 cannot be read from `Y_full` for those edges.

The 26 Q4 rows make this concrete: A0 records **26/26** with a loop carrier and **0** prediction
sources. They are the worst possible C6 sample because their assertion is carrier-borne. C6 must not
be run on that slice alone.

## 3. Three readouts

The observer records three separate quantities per edge per cycle.

| Readout | Definition | Use |
| --- | --- | --- |
| `Y_full(c, e)` | `e` appears in `structure_edges` over all candidates at cycle `c` | Parity with the engine's full assertion; never used to order `K` |
| `Y_ind(c, e)` | `e` appears in `structure_edges` over **non-carrier** candidates only | The C6 ordering readout |
| `K(c, e)` | `e` appears in `structure_edges` over **loop and dream** candidates only | Carrier availability |

`Y_ind` is the assertion supported by concepts, phrases, predictions, hypotheses, processes and
workflow structures — anything that is not the carrier under test. It is a diagnostic readout, not a
replacement for the engine's output.

An edge with `Y_full = 1` but `Y_ind = 0` is **carrier-only**. It cannot contribute to C6. This is a
substantive category, not a missing value.

## 4. Observer implementation

The observer is a benchmark-only subclass of `SleepService`. It does not edit a frozen engine file,
does not monkeypatch a frozen function, and is not used by the live study.

```python
class TimingObservedSleepService(SleepService):
    def __init__(self, memory, observer, *, mutate_report=False):
        super().__init__(memory)
        self.observer = observer
        self.mutate_report = mutate_report

    def run_sleep_cycle(self):
        report = super().run_sleep_cycle()
        if self.mutate_report:
            self.mutation_applied = _mutate_report(report)
        self.observer.record(report.cycle, self._load_prior_candidates())
        return report
```

The implementation is `benchmarks/c6_timing_observer.py`. Its self-test is:

```bash
python -m benchmarks.c6_timing_observer --self-test
```

It runs the stock and observed services on the same deterministic synthetic stream. `N1`, `N2` and
`N3` pass. The synthetic stream has no order variation, so the harness reports
`C6 NOT SEPARATED`; that is a property of the harness scenario, not a C6 result.

The observer snapshots `_load_prior_candidates()` after the parent cycle. That is the same live set
the final readout uses. It does not populate `_prior_cache`, and the parent call is made exactly
once with its return value passed through unchanged.

The report alone is insufficient. In the real one-seed preflight, the last `SleepReport` contained
**101** readout edges while the live set contained **196**; the missing **95** were carried
survivors that were not re-emitted in the final cycle. `N3` caught this. A report-only observer is
not a faithful reconstruction of the final assertion and must not be used for C6.
The methods note is [`C6-N3-LIVE-SET-NOTE.md`](C6-N3-LIVE-SET-NOTE.md).

A separate parity check compares the live-set `Y_full` with
`structure_edges(_load_prior_candidates())` at the final cycle. If they differ, the observer is not
a faithful reconstruction and C6 is void.

The sink writes JSONL to `.scratch/` or a dedicated artifact path. It never writes `memory.db` and
never appends to `organica.log`.

## 5. Per-cycle record

One record per edge per cycle is too large to read, so the sink writes two layers.

**Cycle layer** — one row per cycle:

```json
{"seed": 20611601, "cycle": 62, "y_full": 39, "y_ind": 0, "k": 1}
```

**Edge layer** — one row per edge that ever appears in `Y_full`, `Y_ind` or `K`:

```json
{
  "seed": 20611601,
  "edge": "olive>umber",
  "first_y_full": 62,
  "first_y_ind": null,
  "first_k": 62,
  "last_y_full": 119,
  "last_y_ind": null,
  "last_k": 119,
  "y_full_cycles": 58,
  "y_ind_cycles": 0,
  "k_cycles": 58,
  "class": "CARRIER_ONLY"
}
```

The record must preserve the first cycle, not only a boolean. A later disappearance does not erase
the ordering evidence, and a later reappearance must not be mistaken for first appearance.

## 6. Ordering classes

For each edge with both `Y_ind` and `K` observed:

| Class | Condition |
| --- | --- |
| `K_BEFORE_Y_IND` | `first_k < first_y_ind` |
| `Y_IND_BEFORE_K` | `first_y_ind < first_k` |
| `SAME_CYCLE` | `first_k == first_y_ind` |
| `NO_Y_IND` | `Y_ind` never observed; carrier-only |
| `NO_K` | `K` never observed |

`SAME_CYCLE` is **not** a direction. At cycle resolution the engine cannot order two events inside
the same sleep cycle; calling it "carrier first" would be an imputation.

## 7. Gates

| Gate | Test | Failure |
| --- | --- | --- |
| `N1_neutrality` | Same seed, observer off vs on: canonicalized-identical `SleepReport` sequence (all fields except `ran_at`) and final `Y_full` fingerprint | `OBSERVER NOT NEUTRAL`; no C6 data |
| `N2_mutation` | A test-only arm deliberately alters one reported candidate; `N1` must then fail | `GATE CANNOT FIRE`; build rejected |
| `N3_parity` | Live-set `Y_full` equals `structure_edges(_load_prior_candidates())` at the final cycle | `RECONSTRUCTION MISMATCH` |
| `N4_coverage` | Every analysed edge has at least one `K` cycle and one `Y_ind` cycle | Edge excluded as `NOT MEASURABLE`; not read as zero |
| `N5_engine` | `python -m benchmarks.engine_pin --check` and `tests/test_v1_freeze.py` pass | `ENGINE CHANGED`; stop |
| `N6_order_variation` | Both `K_BEFORE_Y_IND` and `Y_IND_BEFORE_K` occur in the analysed set | `NO ORDER VARIATION`; C6 not separated |
| `N7_determinism` | Same seed twice gives identical edge records | `NON-DETERMINISTIC`; stop |

`N3` is the gate that makes the live-set readout acceptable. The report-only implementation failed
it on seed 20611601; do not revert to report-only snapshots. `N2` is the gate that proves `N1` can
fail. `N6` is the gate that prevents a one-sided timing distribution from being reported as
identification. `N1` must not compare `ran_at`: that field is a wall-clock timestamp and differs
between otherwise identical runs. The canonical comparison excludes it and retains every candidate
payload, cycle number and count.

## 8. What would clear C6

C6 is cleared only when:

1. `N1`–`N7` pass;
2. at least one edge has `K_BEFORE_Y_IND` and at least one has `Y_IND_BEFORE_K`;
3. the preregistration has fixed a minimum number of edges per order before the run;
4. the analysis reports `SAME_CYCLE`, `NO_Y_IND` and `NO_K` separately rather than folding them into
   a direction.

If condition 2 fails, the result is **`NO ORDER VARIATION — C6 NOT SEPARATED`**, not evidence for a
carrier-causal or readout graph. If no edge has `Y_ind`, the result is **`CARRIER-ONLY SAMPLE — C6 NOT
MEASURABLE`**.

## 9. Sample definition

The primary sample is **every world edge that enters `Y_full` at any cycle in the run**, fixed
before the outcome is read. The final live-set intersection is reported separately and is not the
timing denominator. The 26 Q4 never-served edges are a prespecified diagnostic subset, not the
primary sample. Selecting the sample on never-served status would condition on the anomaly and make
the timing question circular.

The block is **20621101–20621106**, frozen in `docs/c6_timing_prereg.json` and granted in
`docs/AUTHORISATION-C6-TIMING.md`. The preflight seed **20611601** is excluded. The block is six
fresh seeds, two arms, 120 cycles and cap 40.

## 9.1 One-seed preflight (2026-11-13)

The off/on preflight on seed **20611601**, **120** cycles and cap **40** found:

| Quantity | Value |
| --- | ---: |
| World edges | 112 |
| Asserted world edges at the final cycle | 70 |
| World edges that ever entered `Y_full` | 106 |
| World edges with `Y_ind` | 92 |
| World edges with `K` | 94 |
| `K_BEFORE_Y_IND` | 36 |
| `Y_IND_BEFORE_K` | 32 |
| `SAME_CYCLE` | 12 |
| `NO_K` | 12 |
| `NO_Y_IND` | 14 |

`Y_ind` exists, both orders occur, and the real off/on arms pass `N1` neutrality and `N3`
final-readout parity. That preflight alone did not clear C6; the six-seed block below does. See
[`C6-ONE-SEED-PREFLIGHT.md`](C6-ONE-SEED-PREFLIGHT.md).

## 9.2 Six-seed block (2026-11-13)

The frozen block used seeds **20621101–20621106**, **120** cycles and cap **40**, with observer
off and on on every seed. Across the block, 653 world-edge rows entered `Y_full`; 586 had `Y_ind`
and 602 had `K`. The order counts were **183** `K_BEFORE_Y_IND`, **294** `Y_IND_BEFORE_K`, **58**
`SAME_CYCLE`, **51** `NO_K` and **67** `NO_Y_IND`.

The smallest per-seed counts were **22** `K_BEFORE_Y_IND` and **35** `Y_IND_BEFORE_K`; all six
seeds met the preregistered floor of 10 per order, and both orders occurred on all six. `N1`–`N7`
pass, including a fresh-process determinism rerun of seed 20621101. The final live-set intersection
was 442 of 672 world edges; the timing counts are over edge rows that appeared in the observer, not
only those still asserted at the final cycle.

**Outcome: `C6 ORDER VARIATION CONFIRMED`.** This clears the C6 temporal-resolution requirement. It
does not clear the two-path admission-by-carrier design, which still has `A−`, `K−` and `Y−` unbuilt
and unrun, and it is not a causal or capability result. See
[`C6-TIMING-BLOCK.md`](C6-TIMING-BLOCK.md).

## 10. Stop condition

**Build status: complete.** The observer, edge extractor and neutrality/mutation harness are
implemented; the self-test passes `N1`–`N3`; the preflight passes `N1`/`N3`; the frozen six-seed
block passes `N1`–`N7` and returns `C6 ORDER VARIATION CONFIRMED`. The block stopped at its
preregistered six seeds; no optional seeds were added after the outcome.

No feature may be added after the build closes. A new requirement goes to the wish-list.

## 11. What is not changed

- No file under `organica/` is edited.
- No frozen result artifact is rewritten.
- No live `memory.db` is opened for writing.
- No intervention (`A−`, `K−`, `Y−`) is implemented or run.
- The C6 block is run and recorded; the self-test still uses one synthetic stream and a fixed seed
  only for reproducibility.

## 12. Decisions fixed in the preregistration

These were fixed before the block ran and were not changed after the outcome:

1. **Minimum per order:** 10 edges per order on each seed, with both orders on at least 5 of 6 seeds.
2. **Readout:** `Y_ind` is the C6 readout; `Y_full` is parity only.
3. **Seed block and length:** seeds 20621101–20621106, 120 cycles, cap 40, observer off and on.
4. **Same-cycle edges:** reported separately as `SAME_CYCLE`; never folded into a direction.
5. **Carrier definition:** loop and dream candidates only.

No seed was replaced and no optional seed was added.
