# Within-cycle world-edge count distribution

Generated from `docs/within_cycle_distribution.json` by `python -m benchmarks.within_cycle_distribution --write`. Do not edit by hand.

**Not a result artifact.** It measures the population behind the 1-4 maxima. It runs no engine cell, consumes no fresh seed and changes no floor.

## What is counted

A world edge's engine count in one processed reset group is the number of ordered source-then-target tag pairs within the engine's three-event lookback, restricted to edges in the world's training-edge set. The counts reset at the group boundary, but the event history does not: a current group can pair with the last two events of the previous group. The strict count uses only events in the same group. A withheld block-end event can make a group longer than the nominal eight events.

The unit is an **edge-cycle observation**: one world edge in one processed reset group. An edge can contribute several observations in the same group; those are the counts in the histogram. This is not the number of distinct world edges in a cycle. The engine count is the primary measure; the strict same-group count is reported to show what the previous group's tail contributes.

## Per cell

| Block | Seed | Role | S_ever | Groups | Group lengths | Engine max | Same-group max | Engine observations | Cross-group observations | Count 1 row share | Lag-1 pair share |
| --- | ---: | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T1 | 20612204 | zero | 0 | 120 | 4:3, 5:10, 6:22, 7:30, 8:55 | 4 | 4 | 3192 | 512 | 0.8501 | 0.8596 |
| T1 | 20612205 | zero | 0 | 120 | 4:1, 5:7, 6:21, 7:34, 8:57 | 3 | 3 | 3360 | 480 | 0.8597 | 0.8571 |
| T1b | 20612208 | zero | 0 | 120 | 5:12, 6:20, 7:35, 8:53 | 4 | 3 | 3328 | 504 | 0.8581 | 0.8522 |
| T1b | 20612210 | zero | 0 | 120 | 4:4, 5:7, 6:21, 7:31, 8:57 | 3 | 3 | 3268 | 516 | 0.8697 | 0.8654 |
| T1b | 20612212 | zero | 0 | 120 | 4:3, 5:9, 6:22, 7:28, 8:58 | 4 | 4 | 3276 | 496 | 0.8612 | 0.8596 |
| T1 | 20612201 | control | 9 | 91 | 5:2, 6:7, 7:15, 8:49, 12:7, 13:3, 14:2, 15:1, 20:2, 21:1, 28:1, 48:1 | 6 | 6 | 3264 | 424 | 0.8094 | 0.8456 |
| T1 | 20612202 | control | 3 | 85 | 5:3, 6:5, 7:9, 8:46, 11:1, 12:4, 13:4, 14:2, 15:1, 17:2, 18:2, 20:5, 34:1 | 6 | 6 | 3152 | 396 | 0.7869 | 0.8490 |
| T1 | 20612203 | control | 6 | 88 | 6:8, 7:13, 8:46, 9:1, 12:5, 13:6, 14:2, 15:2, 19:1, 20:1, 25:1, 29:1, 40:1 | 5 | 5 | 3252 | 408 | 0.7968 | 0.8573 |
| T1 | 20612206 | control | 5 | 85 | 5:1, 6:4, 7:7, 8:50, 11:2, 12:1, 13:2, 14:9, 16:1, 17:1, 18:1, 19:2, 21:1, 22:1, 25:1, 26:1 | 6 | 6 | 3232 | 384 | 0.8083 | 0.8589 |
| T1b | 20612209 | control | 1 | 87 | 6:8, 7:13, 8:43, 11:2, 12:3, 13:5, 14:2, 15:3, 18:2, 19:2, 20:1, 21:2, 24:1 | 5 | 5 | 3208 | 404 | 0.7946 | 0.8529 |
| T1b | 20612211 | control | 3 | 89 | 5:2, 6:9, 7:9, 8:48, 10:1, 11:3, 12:1, 13:2, 14:6, 15:1, 17:1, 18:1, 19:1, 21:1, 22:1, 27:1, 31:1 | 6 | 5 | 3232 | 420 | 0.8056 | 0.8676 |
| T1b | 20612213 | control | 3 | 84 | 5:1, 6:5, 7:13, 8:44, 12:1, 13:5, 14:6, 16:1, 19:1, 20:1, 21:1, 24:1, 26:3, 27:1 | 5 | 5 | 3252 | 364 | 0.8040 | 0.8536 |

## The count histogram

| Count | Zero-cell engine observations | Zero-cell same-group observations | Control engine observations | Control same-group observations |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 12278 | 10852 | 14598 | 13204 |
| 2 | 1861 | 1408 | 3043 | 2534 |
| 3 | 136 | 80 | 471 | 372 |
| 4 | 4 | 2 | 85 | 69 |
| 5 | 0 | 0 | 25 | 22 |
| 6 | 0 | 0 | 5 | 3 |

## Short versus merged groups

| Pool | Group length | Groups | Engine max | Same-group max | Engine count 5+ observations | Same-group count 5+ observations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| zero | <=8 | 600 | 4 | 4 | 0 | 0 |
| zero | >8 | 0 | 0 | 0 | 0 | 0 |
| control | <=8 | 460 | 4 | 4 | 0 | 0 |
| control | >8 | 149 | 6 | 6 | 30 | 25 |

## Why the mass is at 1-4

- The five zero cells have no reset group longer than 8 events; across 600 groups their engine counts are 1-4 and never 5.
- Count 1 is the count in 0.8599 of zero-cell edge-cycle rows; count 2 in 0.1303, count 3 in 0.0095, count 4 in 0.0003.
- Every count is an in-window source-target event pair: lag 0 supplies 0.0000 of zero-cell observations, lag 1 supplies 0.8587 and lag 2 supplies 0.1413. Cross-group lookback supplies 0.1527 of them but never lifts a zero group above 4.
- Groups of at most 8 events have a maximum of 4 in both roles, even with cross-group lookback; the controls' 5-6 counts occur only in the 149 groups longer than 8, created when a withheld block-end event suppresses the reset.
- Count 1 is the common case because each event contributes only two tags and most source-target pairs are seen once inside the three-event lookback; higher counts require the same two tags to recur in nearby events.

## Positive control

| Control | Events | Max count | Lag 0 | Lag 1 | Lag 2 | Passes >4 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| repeated_pair_control | 8 | 21 | 8 | 7 | 6 | yes |

The control repeats one pair in every event, so the same edge has more than four in-window opportunities. It proves the 1-4 observation is not a hard-coded detector limit; the zero cells simply never contain that much repetition inside a short group.

## What this does not claim

A descriptive distribution on six committed seeds, one world family and one persistence-off replay. It does not test a floor, change a floor, run a cell or claim that the 1-4 concentration is a general property of the engine. The split between short and merged groups is a record-arithmetic distinction, not a treatment, and the cross-group lookback is part of the committed replay rather than an added mechanism.
