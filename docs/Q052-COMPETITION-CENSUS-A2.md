# Q052 census, amendment A2: a mass the death cannot move

Generated from `docs/q052_competition_census_a2.json` by `python -m benchmarks.q052_amendment_a2 --render`. Do not edit by hand.

The first run is `docs/q052_competition_census.json` and stands as it was recorded: `VOID`, because its control's mass ratio was below its floor. This page is the amended run, on a fresh probed block.

**Label: `DIFFERENT_SUPPORT_COLLAPSE`**

## The two changes

| Field | A1 | A2 |
| --- | --- | --- |
| mass | every retained hypothesis, each cycle | the pairs retained at the last live cycle, tracked to death |
| floor | 0.90, fixed in the design | 0.5282, calibrated below |
| probed seeds | 20302901-20302903 | 20303001, 20303002, 20303003 |

## The calibration (committed data, not judged by this run)

Source: `docs/decay_competition/parts`, seeds 20302702, 20302703.

| Seed | Cohort mass at last live | At death | Ratio |
| --- | --- | --- | --- |
| 20302702 | | | 0.578178 |
| 20302703 | | | 0.578178 |

Floor = lowest calibration ratio minus the margin 0.05 = **0.5282**.

## The control, under the amended mass

| Field | Value |
| --- | --- |
| reproduced the committed census | True |
| cohort size at last live | 17 |
| of which survived to death | 13 |
| mass at last live | 4106 |
| mass at death | 2374 |
| ratio | 0.578178 |
| floor met | True |

## The probed arm

`burst_L1` at `0.9925`, seeds 20303001, 20303002, 20303003. Live-to-dead transitions: 20303001: 1, 20303002: 1, 20303003: 1.

| Seed | Last live | Death | Top subject | Support | Cohort | Survived | Pairs at death | Competing at death | Mass ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20303001 | 133 | 134 | foxtrot | 642 | 14 | 11 | 2 | 0 | 0.307747 |
| 20303002 | 130 | 131 | delta | 629 | 16 | 12 | 2 | 0 | 0.315296 |
| 20303003 | 130 | 131 | bravo | 636 | 15 | 7 | 0 | 0 | 0.033821 |

## Which conditions fired

| Condition | Fired |
| --- | --- |
| control_reproduced | True |
| control_mass_floor | True |
| dying_cells | 3 |
| intermittent | False |
| support_collapse | True |
| competition_present | False |
| same | False |

## Scope

One family, one factor, three fresh seeds. The classification decides Q053's scope; it is not a capability result and scores no prediction task.
The supports are temporal transition counts, not observations, and survival is theory-layer presence, not theory identity. A label here decides which families Q053 may test; it says nothing about capability.
