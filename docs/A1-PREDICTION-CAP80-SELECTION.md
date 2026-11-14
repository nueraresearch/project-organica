# A1 larger-28 overlap: selection-rule trace at cap 80

Generated from `docs/a1_prediction_cap80_selection.json` by `python -m benchmarks.a1_prediction_cap80_selection --write`. Do not edit by hand.

**Availability-only rule trace, not an A1 result.** Six larger-28 seeds at loop cap **120** / prediction cap **80**. No target, freeze, grant or A1 cell.

## Result

The 104 A\K edges are dominated by `loop_rank_above_loop_cap` (104/104); the 338 K\A edges are dominated by `transition_rank_below_half_budget` (254/338). The overlap loss is therefore a K-side loop-rank effect plus an A-side budget/rank effect, with the support floor a minority component.

| Seeds | A | K | A∩K | A\K | K\A |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 498 | 732 | 394 | 104 | 338 |

## K-side reasons for A\K

| Gate | Edges |
| --- | ---: |
| no_2_or_3_cycle | 0 |
| loop_rank_above_loop_cap | 104 |
| carried_by_selected_loop | 0 |
| carried_by_dream | 0 |
| unclassified | 0 |

## A-side reasons for K\A

| Gate | Edges |
| --- | ---: |
| support_below_prediction_floor | 68 |
| transition_rank_below_half_budget | 254 |
| cooccurrence_rank_below_quota | 0 |
| no_prediction_candidate | 16 |
| inside_returned_window | 0 |
| unclassified | 0 |

## Per seed

| Seed | A | K | A∩K | A\K | K\A |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20660101 | 86 | 111 | 68 | 18 | 43 |
| 20660102 | 75 | 124 | 56 | 19 | 68 |
| 20660103 | 83 | 105 | 51 | 32 | 54 |
| 20660104 | 88 | 138 | 77 | 11 | 61 |
| 20660105 | 91 | 121 | 72 | 19 | 49 |
| 20660106 | 75 | 133 | 70 | 5 | 63 |

## K-side by seed

| Seed | A\K | No cycle | Rank >120 | Other |
| ---: | ---: | ---: | ---: | ---: |
| 20660101 | 18 | 0 | 18 | 0 |
| 20660102 | 19 | 0 | 19 | 0 |
| 20660103 | 32 | 0 | 32 | 0 |
| 20660104 | 11 | 0 | 11 | 0 |
| 20660105 | 19 | 0 | 19 | 0 |
| 20660106 | 5 | 0 | 5 | 0 |

## A-side by seed

| Seed | K\A | Support<5 | Transition quota | Cooccurrence quota | Other |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20660101 | 43 | 5 | 36 | 0 | 2 |
| 20660102 | 68 | 10 | 54 | 0 | 4 |
| 20660103 | 54 | 10 | 43 | 0 | 1 |
| 20660104 | 61 | 14 | 43 | 0 | 4 |
| 20660105 | 49 | 14 | 35 | 0 | 0 |
| 20660106 | 63 | 15 | 43 | 0 | 5 |

## Exact A\K edges

| Seed | Edge | Support | Best loop rank |
| ---: | --- | ---: | ---: |
| 20660101 | ochre>teal | 8 | 223 |
| 20660101 | ochre>willow | 7 | 272 |
| 20660101 | tagbb>taggg | 5 | 240 |
| 20660101 | tagcc>tagaa | 4 | 295 |
| 20660101 | tagcc>willow | 12 | 162 |
| 20660101 | tagee>birch | 7 | 171 |
| 20660101 | tagee>indigo | 9 | 242 |
| 20660101 | tagee>olive | 15 | 225 |
| 20660101 | tagee>tagaa | 5 | 230 |
| 20660101 | tagff>indigo | 5 | 807 |
| 20660101 | tagff>maple | 8 | 790 |
| 20660101 | tagff>teal | 7 | 246 |
| 20660101 | tagff>verdant | 14 | 746 |
| 20660101 | tagff>willow | 4 | 828 |
| 20660101 | taggg>tagkk | 13 | 169 |
| 20660101 | tagii>birch | 10 | 170 |
| 20660101 | tagii>olive | 13 | 398 |
| 20660101 | tagii>teal | 8 | 206 |
| 20660102 | amber>taggg | 12 | 166 |
| 20660102 | birch>maple | 11 | 163 |
| 20660102 | birch>taggg | 7 | 159 |
| 20660102 | birch>teal | 17 | 137 |
| 20660102 | cedar>tagii | 3 | 712 |
| 20660102 | cedar>teal | 9 | 788 |
| 20660102 | tagbb>tagkk | 13 | 133 |
| 20660102 | taghh>fern | 14 | 164 |
| 20660102 | taghh>teal | 8 | 176 |
| 20660102 | taghh>yarrow | 6 | 204 |
| 20660102 | tagll>maple | 10 | 285 |
| 20660102 | tagll>taggg | 10 | 266 |
| 20660102 | teal>willow | 4 | 183 |
| 20660102 | umber>taggg | 12 | 410 |
| 20660102 | umber>tagjj | 11 | 225 |
| 20660102 | verdant>teal | 5 | 234 |
| 20660102 | willow>tagaa | 7 | 140 |
| 20660102 | yarrow>amber | 7 | 121 |
| 20660102 | yarrow>tagll | 6 | 121 |
| 20660103 | fern>birch | 8 | 281 |
| 20660103 | fern>crimson | 5 | 247 |
| 20660103 | indigo>olive | 7 | 130 |
| 20660103 | olive>birch | 6 | 654 |
| 20660103 | olive>crimson | 9 | 156 |
| 20660103 | olive>teal | 8 | 244 |
| 20660103 | sable>taggg | 8 | 148 |
| 20660103 | slate>crimson | 5 | 356 |
| 20660103 | slate>maple | 7 | 641 |
| 20660103 | slate>taghh | 8 | 720 |
| 20660103 | tagaa>taggg | 3 | 127 |
| 20660103 | tagcc>indigo | 8 | 500 |
| 20660103 | tagcc>maple | 8 | 318 |
| 20660103 | tagcc>ochre | 13 | 749 |
| 20660103 | tagcc>sable | 9 | 168 |
| 20660103 | tagcc>tagdd | 13 | 748 |
| 20660103 | tagcc>taghh | 14 | 261 |
| 20660103 | tagcc>tagll | 17 | 162 |
| 20660103 | tagkk>birch | 8 | 205 |
| 20660103 | tagkk>sable | 7 | 143 |
| 20660103 | tagkk>tagaa | 8 | 276 |
| 20660103 | teal>fern | 3 | 225 |
| 20660103 | verdant>ochre | 3 | 564 |
| 20660103 | verdant>tagaa | 8 | 125 |
| 20660103 | verdant>tagdd | 6 | 160 |
| 20660103 | verdant>taghh | 10 | 170 |
| 20660103 | yarrow>crimson | 12 | 138 |
| 20660103 | yarrow>maple | 11 | 206 |
| 20660103 | yarrow>ochre | 7 | 197 |
| 20660103 | yarrow>tagdd | 11 | 209 |
| 20660103 | yarrow>taghh | 9 | 269 |
| 20660103 | yarrow>umber | 12 | 172 |
| 20660104 | cedar>indigo | 6 | 848 |
| 20660104 | cedar>taghh | 6 | 258 |
| 20660104 | cedar>willow | 22 | 194 |
| 20660104 | crimson>slate | 4 | 292 |
| 20660104 | sable>taggg | 8 | 196 |
| 20660104 | tagee>fern | 12 | 130 |
| 20660104 | taggg>ochre | 6 | 228 |
| 20660104 | taggg>slate | 2 | 301 |
| 20660104 | taggg>taghh | 10 | 184 |
| 20660104 | umber>olive | 8 | 553 |
| 20660104 | umber>willow | 11 | 469 |
| 20660105 | birch>slate | 6 | 172 |
| 20660105 | cedar>amber | 9 | 124 |
| 20660105 | slate>sable | 4 | 187 |
| 20660105 | tagaa>olive | 14 | 129 |
| 20660105 | tagbb>crimson | 13 | 230 |
| 20660105 | tagbb>ochre | 12 | 212 |
| 20660105 | tagbb>tagcc | 9 | 207 |
| 20660105 | tagcc>verdant | 5 | 154 |
| 20660105 | tagdd>fern | 8 | 303 |
| 20660105 | tagdd>ochre | 8 | 348 |
| 20660105 | tagdd>taggg | 4 | 446 |
| 20660105 | tagee>olive | 7 | 224 |
| 20660105 | tagee>tagjj | 8 | 179 |
| 20660105 | willow>ochre | 10 | 194 |
| 20660105 | willow>olive | 6 | 197 |
| 20660105 | willow>tagcc | 3 | 436 |
| 20660105 | yarrow>olive | 10 | 431 |
| 20660105 | yarrow>tagkk | 5 | 522 |
| 20660105 | yarrow>teal | 9 | 489 |
| 20660106 | amber>tagkk | 3 | 128 |
| 20660106 | tagaa>tagff | 10 | 123 |
| 20660106 | willow>slate | 12 | 162 |
| 20660106 | willow>tagjj | 5 | 128 |
| 20660106 | yarrow>indigo | 11 | 130 |

## Reading

The K-side loss is not a prediction-ranking loss: the A\K edges are already served by A, often at rank 1. They are absent from K because their best loop rank is above the 120-loop cut, not because they lack a 2-/3-cycle. The A-side loss is the mirror: K\A edges are carried, but they either fall below the prediction support floor, sit below the cap-80 half-budget transition quota, or sit below the cooccurrence quota.

## What this does not claim

A descriptive rule trace on six no-arm larger-28 seeds at one cap pair. It attributes excluded edges to the engine gate they hit; it does not establish that changing that gate would repair the overlap, and it is not a treatment, target viability or a successor.
