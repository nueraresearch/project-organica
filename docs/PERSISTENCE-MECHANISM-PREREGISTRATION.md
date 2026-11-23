# PERSISTENCE-MECHANISM-1 — decay and the read floor at cap 112

**Status.** FROZEN, NOT RUN. This page is rendered from `docs/persistence_mechanism_prereg.json`; it is not edited by hand.

| Field | Value |
| --- | --- |
| Preregistration | `PERSISTENCE-MECHANISM-1` |
| Frozen on | 2026-11-11 |
| Engine | 0.15.0, cap 112, none |
| Cells planned | 24 (4 arms x 6 seeds = 24 cells) |
| Seeds | 20612301, 20612302, 20612303, 20612304, 20612305, 20612306; bootstrap 20612307 |
| Cycles | 120 |
| Runner | not built |
| Cells run | 0 |
| Authorisation | not granted |

## Why this block

T1b's result decision says: **Pursue the persistence mechanism (decay, floor, denominator); the cap arm does not answer this question.**

T1b returned PERSISTENCE CONTRIBUTES: removing carried temporal counts removed served world edges on every seed at cap 112. Its decision says to pursue the persistence mechanism (decay, floor, denominator). This block follows that decision by separating decay from the read floor in one factorial. It does not re-read T1 or T1b, and it does not re-open T1b's corrected denominator reading.

## The two mechanisms

| Arm | Decay factor | Read floor | What changes |
| --- | ---: | ---: | --- |
| `shipped` | 0.95 | 5 | the shipped decay factor and the shipped read floor |
| `no_decay` | 1.0 | 5 | no temporal decay, shipped read floor |
| `floor_one` | 0.95 | 1 | shipped decay, read floor lowered to 1 |
| `no_decay_floor_one` | 1.0 | 1 | no temporal decay and read floor lowered to 1 |

**Manipulation.** An in-process SleepService/MemoryService subclass applies the arm's decay factor (shipped 0.95 -> no-decay 1.0) at the engine's temporal-decay call and sets the arm's PREDICTION_MIN_COUNT (shipped 5 -> floor 1). The engine files, pin and cap are unchanged.

## Endpoints

| Stage | Definition | Role |
| --- | --- | --- |
| P | present world edges: the denominator of every share | denominator |
| S_ever | served world edges: the union of every served window intersect the world, counted once; zero is measured | primary |
| A_W | asserted world edges at the end of the run | secondary |
| C | constructed candidates: the pre-cap universe intersect the world | reported |

**Primary effects.** `decay_effect` = S_ever(no_decay, floor 5) - S_ever(shipped), paired by seed. `floor_effect` = S_ever(floor_one, decay 0.95) - S_ever(shipped), paired by seed. Interactive contrast: (S_ever(no_decay_floor_one) - S_ever(no_decay)) - (S_ever(floor_one) - S_ever(shipped)), paired by seed.

**Bar.** an effect passes when its mean paired difference is at least 10 edges, at least 5 of 6 seeds are positive, and the paired 95% lower bound is above zero. Margin 10 edges, 5 of 6 positive seeds, 95% paired interval, 10000 resamples at seed 20612307.

## Gates

| Gate | Rule |
| --- | --- |
| `G1_build` | all 24 cells run the shipped 0.15.0 build at cap 112 with one sha256 and no engine edit; a mixed build or an edited engine is VOID |
| `G2_world` | each seed's world digest and present fingerprint are identical across all four arms and the six seeds are the frozen block; a differing world is VOID |
| `G3_treatments_live` | each arm records its designed decay factor and read floor (0.95/5, 1.0/5, 0.95/1, 1.0/1); an arm whose configured factor or floor is the control value is TREATMENT NOT LIVE, not a null |
| `G4_denominator` | P is non-zero in every cell; S_ever is a measured count, so a zero S_ever is read as zero served edges; a zero P is not measurable and VOIDS the block |
| `G5_seed_axis` | the six shipped cells hold at least three distinct (S_ever, A_W) pairs; one outcome repeated six times is not a seed axis |
| `G6_determinism` | a fresh-process rerun of seed 20612301 reproduces its four-arm stage rows exactly |
| `G7_cells` | exactly 24 cells, four arms x six seeds, with no extra seed, cap, cycle or arm |

## Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
| any gate fails | **VOID** | the block is unrun or non-measurable and the failed gate names what did not happen | record VOID; fix the harness and register a new block; read no mechanism |
| gates pass; both the decay effect and the read-floor effect meet the bar | **BOTH MECHANISMS CARRY PERSISTENCE** | removing decay and lowering the floor each add served world edges; the interaction is reported but is not required | pursue both mechanisms jointly in a mechanism block; no adoption or capability claim follows |
| gates pass; the decay effect meets the bar and the read-floor effect does not | **DECAY CARRIES PERSISTENCE** | the decay factor is the live lever at cap 112; the floor does not move the endpoint on this block | isolate decay levels next; do not treat the floor as the conversion lever |
| gates pass; the read-floor effect meets the bar and the decay effect does not | **READ FLOOR CARRIES PERSISTENCE** | the read/admission floor is the live lever at cap 112; decay does not move the endpoint on this block | isolate floor values and precision next; do not treat decay as the conversion lever |
| gates pass; neither effect meets the bar | **NO MECHANISM DETECTED** | neither contrast locates the persistence contribution at this cap and world family | make no mechanism claim; the next probe is the in-cycle construction or admission stage, or a larger fresh seed axis, not another re-read |

## Prediction, stated before any cell

**Prediction.** Both main effects on S_ever are positive, and the read-floor effect is larger than the decay effect; the interaction is not predicted to be necessary.

**Because.** T1b's zero cells are threshold-limited: no world edge reaches 5 within-cycle observations after the reset, so lowering the read floor has a direct route to served edges. Decay is the other carried-count mechanism and should add a smaller positive effect at cap 112.

**Falsifier.** Either effect at or below the bar, a negative paired mean, a failed treatment-live check, or any gate failure.

A pass is a mechanism-direction result, not an effect-size or capability result; a failure does not re-read T1b's PERSISTENCE CONTRIBUTES verdict.

## No cell has run

**Authorisation.** No dated grant exists. A grant naming the 24 cells, the rerun and the result artifact is required before an arm is built or a cell is opened. This preregistration authorises nothing to run.

**Cost.** 24 cells plus one fresh-process determinism rerun of seed 20612301, 120 cycles each.

**Stop condition.** No cell runs until a dated grant is recorded. After the grant, the block closes when the 24 cells and the rerun have produced their parts, G1-G7 have been scored once in the frozen order, and the verdict is recorded. Any gate failure is VOID; no cell is rerun to escape a gate and no gate is amended after a result.

## What this record does not license

A preregistration, not a result. No cell has run. It does not re-read T1 or T1b, does not re-open the denominator, and licenses no capability, retention or transfer claim. A mechanism direction is not an adoption recommendation.
