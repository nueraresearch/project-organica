# V2 first cell — report template

**Generated** from the seeds, the matched-control artifacts and the reading decision by
`python -m benchmarks.v2_first_cell_report --write-template`. Do not edit it by hand;
`--check` fails when the page and the renderer disagree.

No cell has run. This page fixes the one shape a cell report may take, so the report is not
composed after the numbers are seen. `--render RESULT.json` validates a result and emits that
shape; every case listed under "What the renderer refuses" stops it.

The four labels and what each authorises are fixed by
[`DECISION-V2-FIRST-CELL-INTERPRETATION`](DECISION-V2-FIRST-CELL-INTERPRETATION.md); the report quotes that decision verbatim rather than
paraphrasing it.

## The fixed shape

| Section | Must contain |
|---|---|
| Header | the outcome label, the protocol, the scorer pin, the date, the reading decision |
| 1. What ran | declared, measurable and excluded seed counts; arms; endpoint; interval rule |
| 2. Gates | `A1`–`A5`, each `PASS`, `FAIL` or `NOT RUN`, with its evidence; `NOT RUN` only in a `VOID` |
| 3. Exclusions | every unmeasured seed and its reason |
| 4. Interval | mean, 99% interval, level and resamples — or "no interval" when `VOID` |
| 5. Beta selections | per seed, arm B and arm C; arm A selects none |
| 6. Decomposition | mean `d_C`, mean `d_B`, and their difference |
| 7. Selection comparison | the committed matched controls and the cell's margin against them |
| 8. Control arm (`M1`) | target, intervention, bystander, metric, member and bystander deltas; a bystander change is `M1` FAIL |
| 9. What this authorises | the adopted sentence for the label, quoted |
| 10. What this does not authorise | the floor for that label |
| 11. Not evidence | the scope of one cell |

## The result artifact

`--render` accepts this schema. Extra fields are ignored; a missing field is refused.

```json
{
  "kind": "v2_first_cell_result",
  "id": "V2-FIRST-CELL-RESULT-1",
  "date": "2026-11-16",
  "protocol": "docs/V2-FIRST-EXPERIMENT-PREREGISTRATION.md",
  "scorer_pin": "docs/v2_first_cell_scorer_pin.json",
  "scorer_pin_ok": true,
  "outcome": "PASS",
  "gates": {
    "A1": {
      "status": "PASS",
      "evidence": "what was checked"
    },
    "A2": {
      "status": "PASS",
      "evidence": "what was checked"
    },
    "A3": {
      "status": "PASS",
      "evidence": "what was checked"
    },
    "A4": {
      "status": "PASS",
      "evidence": "what was checked"
    },
    "A5": {
      "status": "PASS",
      "evidence": "what was checked"
    }
  },
  "per_seed": [
    {
      "seed": 20910101,
      "measurable": true,
      "d": -0.001,
      "d_B": -0.0005,
      "beta": {
        "B": 1,
        "C": 2
      }
    },
    {
      "seed": 20910102,
      "measurable": true,
      "d": -0.001,
      "d_B": -0.0005,
      "beta": {
        "B": 1,
        "C": 2
      }
    },
    {
      "seed": 20910103,
      "measurable": true,
      "d": -0.001,
      "d_B": -0.0005,
      "beta": {
        "B": 1,
        "C": 2
      }
    },
    {
      "seed": 20910104,
      "measurable": true,
      "d": -0.001,
      "d_B": -0.0005,
      "beta": {
        "B": 1,
        "C": 2
      }
    },
    {
      "seed": 20910105,
      "measurable": true,
      "d": -0.001,
      "d_B": -0.0005,
      "beta": {
        "B": 1,
        "C": 2
      }
    },
    {
      "seed": 20910106,
      "measurable": true,
      "d": -0.001,
      "d_B": -0.0005,
      "beta": {
        "B": 1,
        "C": 2
      }
    },
    {
      "seed": 20910107,
      "measurable": true,
      "d": -0.001,
      "d_B": -0.0005,
      "beta": {
        "B": 1,
        "C": 2
      }
    },
    {
      "seed": 20910108,
      "measurable": true,
      "d": -0.001,
      "d_B": -0.0005,
      "beta": {
        "B": 1,
        "C": 2
      }
    },
    {
      "seed": 20910109,
      "measurable": true,
      "d": -0.001,
      "d_B": -0.0005,
      "beta": {
        "B": 1,
        "C": 2
      }
    },
    {
      "seed": 20910110,
      "measurable": false,
      "exclusion": "no held-out positives"
    }
  ],
  "interval": {
    "mean": -0.001,
    "lo": -0.0012,
    "hi": -0.0008,
    "level": 0.99,
    "resamples": 10000
  },
  "control": {
    "status": "PASS",
    "seed": 20910101,
    "intervention": "remove_member",
    "composite_id": "c-000001",
    "removed_member": "a->b",
    "bystander_id": "c-000002",
    "metric": "resolved member count",
    "member_delta": 1.0,
    "bystander_delta": 0.0,
    "detail": "the target lost one member; the bystander did not move"
  },
  "void": null
}
```

`VOID` replaces the interval with `null` and adds
`"void": {"codes": [...], "detail": "..."}`; a non-`VOID` result carries `"void": null`.

## What the renderer refuses

- an outcome label that contradicts its interval — the label is derived, not typed;
- an interval whose mean is not the mean of the measurable seeds, or whose level is not 99%
  with 10,000 resamples;
- a missing, duplicated or undeclared seed, or an unmeasured seed with no reason;
- fewer than 8 measurable seeds without `VOID`, and a `VOID` without the `SEEDS_MEASURABLE` code;
- a failed `A1`–`A5` gate without `VOID`, or a `VOID` without that gate's code;
- a gate marked `NOT RUN` outside a `VOID`, or a `VOID` without the `GATES_NOT_RUN` code;
- a `VOID` that carries an interval;
- a beta outside `{1, 2, 4, 8}`, a missing B or C selection, or a beta for arm A;
- a stale or missing scorer pin without `VOID`;
- a control arm that is missing, names its own composite as the bystander, or whose status contradicts
  the bystander delta;
- an `M1` violation without `VOID` and the `M1_CONTROL` code, or a control that did not run without
  a reason;
- a `VOID` whose codes name no condition the result shows.

## The control arm

The section 8 arm intervenes on one composite — `remove_member` or `retire` — and measures the effect on
its members, with a bystander composite as the control. The bystander delta must be exactly zero: `M1`
requires the bystander to be byte-identical, so any movement is `M1` FAIL and the cell is `VOID`. A member
delta of zero is a tie on the members — the primitive is useless for control — and is reported as the
secondary finding; it neither passes nor fails the charter. A control that was not run is reported with its
reason and makes no `M1` claim, because the arm is secondary and adds no VOID trigger.

## The committed selection comparison

These numbers are read from the artifacts at render time, never from the result: at equal mass and
key count the matched control is `-0.000497` on the null worlds and
`+0.002091` on the planted world, `4.05%` of its
`0.051685` gain (`-0.000460` at equal mass alone).
A `PASS` states the cell's margin against `+0.002091`; a `REVERSAL` states its
cost against `0.000497`.
