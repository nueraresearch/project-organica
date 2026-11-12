# How loops and dreams assert the 26 never-served pairs

Generated from `docs/assertion_carrier_trace.json` by `python -m benchmarks.assertion_carrier_trace --write`. Do not edit by hand.

**Not a result artifact.** A replay-only trace of the same six Q4 seeds. It starts at the loop/dream carrier's formation, not at a new cell: no seed, arm, cap, engine edit or treatment is added.

## What the trace found

| Question | Measurement |
| --- | --- |
| Rows traced | 26 |
| Rows with a loop carrier | 26 |
| Rows with a dream carrier | 1 |
| Loop candidates carrying a row | 61 |
| Dream candidates carrying a row | 1 |
| Loop path lengths | 3 2-cycles, 58 3-cycles |
| Direct temporal count range | 23-47 (floor 5) |
| Reverse temporal count range | 23-45 |
| Direct edges at/above prediction floor | 26 |
| Final prediction sources | 0 |
| Carrier formation cycles | 37-117 (median 78.5) |

The direct edge is present in the temporal graph in every row; it is not a floor miss. The assertion is supplied by a loop path that contains the pair. `structure_edges` expands every loop path in both directions, so a path that contains the reverse orientation also asserts the direct orientation. The dream path is a co-carrier in one row; no row is dream-only.

## Every edge

| Seed | Edge | Category | Reverse served | Temporal direct / reverse | Carriers | Formation cycles | Why it is asserted |
| ---: | --- | --- | ---: | ---: | --- | --- | --- |
| 20611601 | `olive>umber` | identity mismatch | 1 | 43 / 25 | loop direct [olive>umber>teal>olive] @62 str=1 | 62 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611601 | `olive>willow` | alternate assertion path | 0 | 38 / 23 | loop direct [olive>willow>teal>olive] @104 str=0.512 | 104 | A loop path contains the pair from the temporal graph; structure_edges adds both directions of that path, even though neither orientation is served. |
| 20611601 | `willow>olive` | alternate assertion path | 0 | 23 / 38 | loop reverse [olive>willow>teal>olive] @104 str=0.512 | 104 | A loop path contains the pair from the temporal graph; structure_edges adds both directions of that path, even though neither orientation is served. |
| 20611601 | `willow>teal` | identity mismatch | 46 | 36 / 32 | loop direct [teal>verdant>willow>teal] @109 str=1; loop direct [cedar>willow>teal>cedar] @62 str=3.8654; loop direct [olive>willow>teal>olive] @104 str=0.512; loop direct [amber>willow>teal>amber] @62 str=0.512; loop direct [teal>umber>willow>teal] @62 str=0.512 | 109, 62, 104, 62, 62 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611602 | `amber>umber` | identity mismatch | 55 | 34 / 27 | loop direct [amber>umber>ochre>amber] @50 str=5.201 | 50 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611602 | `indigo>umber` | identity mismatch | 56 | 28 / 36 | loop reverse [indigo>ochre>umber>indigo] @110 str=1; loop reverse [indigo>slate>umber>indigo] @114 str=1; loop reverse [indigo>willow>umber>indigo] @112 str=5.201 | 110, 114, 112 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611602 | `sable>slate` | identity mismatch | 3 | 43 / 32 | loop direct [sable>slate>umber>sable] @49 str=1 | 49 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611602 | `willow>umber` | identity mismatch | 55 | 33 / 42 | dream direct [indigo>willow>umber] @84 str=0.04; loop direct [fern>willow>umber>fern] @49 str=1; loop direct [ochre>willow>umber>ochre] @68 str=1; loop direct [indigo>willow>umber>indigo] @112 str=5.201; loop reverse [ochre>umber>willow>ochre] @51 str=5.3687; loop direct [sable>willow>umber>sable] @37 str=0.2098; loop direct [umber>verdant>willow>umber] @37 str=0.2098; loop direct [slate>willow>umber>slate] @56 str=0.2098 | 84, 49, 68, 112, 51, 37, 37, 56 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. A dream path is a co-carrier, not the sole source. |
| 20611603 | `sable>yarrow` | alternate assertion path | 0 | 39 / 35 | loop direct [sable>yarrow>verdant>sable] @76 str=1 | 76 | A loop path contains the pair from the temporal graph; structure_edges adds both directions of that path, even though neither orientation is served. |
| 20611603 | `slate>umber` | identity mismatch | 3 | 40 / 37 | loop reverse [slate>teal>umber>slate] @66 str=0.64 | 66 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611603 | `slate>yarrow` | alternate assertion path | 0 | 42 / 32 | loop reverse [slate>teal>yarrow>slate] @67 str=15.36 | 67 | A loop path contains the pair from the temporal graph; structure_edges adds both directions of that path, even though neither orientation is served. |
| 20611603 | `umber>teal` | identity mismatch | 26 | 30 / 33 | loop reverse [indigo>teal>umber>indigo] @117 str=0.64; loop reverse [teal>umber>verdant>teal] @66 str=0.64; loop reverse [slate>teal>umber>slate] @66 str=0.64 | 117, 66, 66 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611603 | `willow>verdant` | identity mismatch | 41 | 32 / 43 | loop reverse [verdant>willow>yarrow>verdant] @69 str=1 | 69 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611603 | `yarrow>indigo` | identity mismatch | 10 | 30 / 42 | loop reverse [indigo>yarrow>verdant>indigo] @76 str=38; loop direct [indigo>teal>yarrow>indigo] @117 str=0.64 | 76, 117 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611603 | `yarrow>sable` | alternate assertion path | 0 | 35 / 39 | loop reverse [sable>yarrow>verdant>sable] @76 str=1 | 76 | A loop path contains the pair from the temporal graph; structure_edges adds both directions of that path, even though neither orientation is served. |
| 20611603 | `yarrow>slate` | alternate assertion path | 0 | 32 / 42 | loop direct [slate>teal>yarrow>slate] @67 str=15.36 | 67 | A loop path contains the pair from the temporal graph; structure_edges adds both directions of that path, even though neither orientation is served. |
| 20611603 | `yarrow>verdant` | identity mismatch | 41 | 38 / 42 | loop direct [ochre>yarrow>verdant>ochre] @96 str=1; loop direct [sable>yarrow>verdant>sable] @76 str=1; loop direct [fern>yarrow>verdant>fern] @76 str=1; loop direct [umber>yarrow>verdant>umber] @76 str=1; loop direct [indigo>yarrow>verdant>indigo] @76 str=38; loop both [verdant>yarrow>verdant] @69 str=1; loop direct [verdant>willow>yarrow>verdant] @69 str=1; loop direct [teal>yarrow>verdant>teal] @66 str=21.12 | 96, 76, 76, 76, 76, 69, 69, 66 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611604 | `amber>maple` | alternate assertion path | 0 | 36 / 27 | loop direct [amber>maple>crimson>amber] @79 str=1 | 79 | A loop path contains the pair from the temporal graph; structure_edges adds both directions of that path, even though neither orientation is served. |
| 20611604 | `maple>amber` | alternate assertion path | 0 | 27 / 36 | loop reverse [amber>maple>crimson>amber] @79 str=1 | 79 | A loop path contains the pair from the temporal graph; structure_edges adds both directions of that path, even though neither orientation is served. |
| 20611605 | `amber>birch` | identity mismatch | 23 | 23 / 34 | loop reverse [amber>teal>birch>amber] @100 str=1; loop reverse [amber>sable>birch>amber] @111 str=1; loop reverse [amber>umber>birch>amber] @102 str=0.4863 | 100, 111, 102 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611605 | `sable>birch` | identity mismatch | 24 | 33 / 39 | loop direct [birch>olive>sable>birch] @111 str=1; loop reverse [birch>sable>teal>birch] @85 str=1; loop reverse [birch>sable>willow>birch] @102 str=1; loop direct [amber>sable>birch>amber] @111 str=1; loop both [birch>sable>birch] @111 str=1; loop reverse [birch>sable>umber>birch] @102 str=0.2622 | 111, 85, 102, 111, 111, 102 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611605 | `sable>teal` | identity mismatch | 68 | 31 / 37 | loop direct [birch>sable>teal>birch] @85 str=1; loop direct [sable>teal>willow>sable] @112 str=4.8654; loop direct [olive>sable>teal>olive] @73 str=0.1678; loop both [sable>teal>sable] @110 str=3.1138 | 85, 112, 73, 110 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611606 | `crimson>teal` | identity mismatch | 4 | 47 / 45 | loop direct [crimson>teal>verdant>crimson] @78 str=0.64 | 78 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611606 | `ochre>amber` | identity mismatch | 27 | 27 / 32 | loop reverse [amber>ochre>verdant>amber] @114 str=0.512 | 114 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611606 | `teal>amber` | identity mismatch | 28 | 31 / 39 | loop reverse [amber>teal>verdant>amber] @77 str=1; loop reverse [amber>teal>sable>amber] @99 str=1; loop reverse [amber>teal>willow>amber] @97 str=1; loop reverse [amber>teal>fern>amber] @85 str=1 | 77, 99, 97, 85 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |
| 20611606 | `teal>willow` | identity mismatch | 2 | 39 / 37 | loop direct [amber>teal>willow>amber] @97 str=1 | 97 | A loop path contains the served reverse orientation; structure_edges adds both directions of that path. |

## The mechanism chain

1. **Temporal presence.** Every direct edge is already in the final temporal graph at count 23-47, above the prediction floor. The trace therefore starts from a real temporal edge, not from a floor miss.
2. **Loop formation.** The loop builder reads temporal 2-cycles and 3-cycles, requires a minimum edge count of 5, and does not consult served windows. The first observed carrier formations span cycles 37-117.
3. **Symmetric readout.** `structure_edges` expands a loop path in both directions. On the 18 reverse-served rows this turns the served reverse pair into the direct assertion; on the 8 alternate rows it asserts a pair for which neither orientation was served.
4. **Dream co-carrier.** One row also has a dream carrier. It is not necessary for the readout and is not the sole source of any row.
5. **Prediction is a different path.** No row has a final prediction source, even though every direct temporal count clears the prediction floor. The loop path, not the prediction window, is the final carrier.

## Controls

| Control | Path | Edge | Hits | Expected | Passes |
| --- | --- | --- | --- | --- | --- |
| loop_symmetry_control | amber>birch>amber | `amber>birch` | direct, reverse | direct, reverse | yes |
| loop_reverse_control | birch>amber>birch | `amber>birch` | direct, reverse | direct, reverse | yes |
| dream_direct_control | amber>birch | `amber>birch` | direct | direct | yes |
| loop_missing_control | amber>cedar>amber | `amber>birch` | none | none | yes |
| dream_missing_control | amber>cedar | `amber>birch` | none | none | yes |

## What this does not claim

A replay-only carrier trace on six committed Q4 seeds, one world family, one build and one cap. It explains how loop/dream paths reach the readout; it does not show that serving the direct edge would change A_W, does not decompose the full prediction-ranking history, and does not establish capability, retention, transfer or a general engine property.
