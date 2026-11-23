# The Q052 census: is `burst_L1`'s late collapse competition loss?

Generated from `docs/q052_competition_census.json` by `python -m benchmarks.competition_census --render`. Do not edit by hand.

Design: `docs/Q052-FRAMING-DESIGN.md`. Window: cycles 1-300.

**Label: `VOID`**

## The control, reproduced through this instrument

| Field | Value | Expected |
| --- | --- | --- |
| last live cycle | 299 | 299 |
| death cycle | 300 | 300 |
| top subject | bravo | bravo |
| top support | 866 | 866 |
| competing supports | [433, 433] | [433, 433] |
| competing at death | 0 subject(s) | empty |
| mass ratio | 0.578178 | 0.9 or more |

## The probed arm

`burst_L1` at factor `0.9925`, seeds 20302901, 20302902, 20302903. Live-to-dead transitions in the window: 20302901: 1, 20302902: 1, 20302903: 1.

| Seed | Last live | Death | Top subject | Support | Pairs at death | Competing at death | Mass ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20302901 | 134 | 135 | delta | 628 | 2 | 0 | 0.313853 |
| 20302902 | 130 | 131 | delta | 645 | 2 | 0 | 0.1843 |
| 20302903 | 130 | 131 | delta | 629 | 0 | 0 | 0.041041 |

## Which conditions fired

| Condition | Fired |
| --- | --- |
| control_reproduced | True |
| control_mass_floor | False |
| dying_cells | 3 |
| intermittent | False |
| support_collapse | True |
| competition_present | False |
| same | False |

## Scope

One family, one factor, three fresh seeds. The classification decides Q053's scope; it is not a capability result and scores no prediction task.
The supports are temporal transition counts, not observations, and survival is theory-layer presence, not theory identity. A label here decides which families Q053 may test; it says nothing about capability.
