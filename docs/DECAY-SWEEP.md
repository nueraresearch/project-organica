# The decay factor sweep — result

Generated from `docs/decay_sweep.json` by `python -m benchmarks.decay_sweep --render`.
Do not edit by hand.

Pre-registration: `docs/DECAY-SWEEP-PREREGISTRATION.md`. Seven factors on the
falsifier's `lattice_L1` world, reference arm FULL, seeds 20302501-20302503.

**Label: `STEP`**

| Factor | Death cycles | Median | Alive at 300 | Stable zero | Peak stable | Final stable |
| --- | --- | --- | --- | --- | --- | --- |
| 0.985 | [150, 150, 150] | 150 | 0/3 | [301, 301, 301] | 21 | 12 |
| 0.99 | [228, 228, 228] | 228 | 0/3 | [301, 301, 301] | 21 | 12 |
| 0.9925 | [301, 301, 301] | 301 | 3/3 | [301, 301, 301] | 21 | 14 |
| 0.995 | [301, 301, 301] | 301 | 3/3 | [301, 301, 301] | 21 | 18 |
| 0.9975 | [301, 301, 301] | 301 | 3/3 | [301, 301, 301] | 21 | 21 |
| 0.999 | [301, 301, 301] | 301 | 3/3 | [301, 301, 301] | 21 | 21 |
| 1.0 | [301, 301, 301] | 301 | 3/3 | [301, 301, 301] | 21 | 21 |

**Smallest factor alive at cycle 300:** 0.9925.

**Largest adjacent step:** 78 cycles, from 0.985 to 0.99.

## Survival versus decay

<svg xmlns="http://www.w3.org/2000/svg" width="760" height="380" viewBox="0 0 760 380" role="img" aria-label="Theory death and stable-edge zero against decay factor">
<rect width="100%" height="100%" fill="white"/>
<text x="60" y="20" font-family="sans-serif" font-size="15" fill="#111">Theory death and stable-edge zero vs decay factor (lattice_L1)</text>
<line x1="70" y1="310.0" x2="720" y2="310.0" stroke="#e5e7eb" stroke-width="1"/>
<text x="62" y="314.0" text-anchor="end" font-family="sans-serif" font-size="11" fill="#667085">0</text>
<line x1="70" y1="265.1" x2="720" y2="265.1" stroke="#e5e7eb" stroke-width="1"/>
<text x="62" y="269.1" text-anchor="end" font-family="sans-serif" font-size="11" fill="#667085">50</text>
<line x1="70" y1="220.3" x2="720" y2="220.3" stroke="#e5e7eb" stroke-width="1"/>
<text x="62" y="224.3" text-anchor="end" font-family="sans-serif" font-size="11" fill="#667085">100</text>
<line x1="70" y1="175.4" x2="720" y2="175.4" stroke="#e5e7eb" stroke-width="1"/>
<text x="62" y="179.4" text-anchor="end" font-family="sans-serif" font-size="11" fill="#667085">150</text>
<line x1="70" y1="130.6" x2="720" y2="130.6" stroke="#e5e7eb" stroke-width="1"/>
<text x="62" y="134.6" text-anchor="end" font-family="sans-serif" font-size="11" fill="#667085">200</text>
<line x1="70" y1="85.7" x2="720" y2="85.7" stroke="#e5e7eb" stroke-width="1"/>
<text x="62" y="89.7" text-anchor="end" font-family="sans-serif" font-size="11" fill="#667085">250</text>
<line x1="70" y1="40.9" x2="720" y2="40.9" stroke="#e5e7eb" stroke-width="1"/>
<text x="62" y="44.9" text-anchor="end" font-family="sans-serif" font-size="11" fill="#667085">300</text>
<text x="18" y="175" transform="rotate(-90 18 175)" font-family="sans-serif" font-size="12" fill="#344054">survival / zero cycle</text>
<text x="70.0" y="330" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#344054">0.985</text>
<text x="178.3" y="330" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#344054">0.99</text>
<text x="286.7" y="330" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#344054">0.9925</text>
<text x="395.0" y="330" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#344054">0.995</text>
<text x="503.3" y="330" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#344054">0.9975</text>
<text x="611.7" y="330" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#344054">0.999</text>
<text x="720.0" y="330" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#344054">1.0</text>
<line x1="70" y1="40" x2="70" y2="310" stroke="#667085" stroke-width="1"/>
<line x1="70" y1="310" x2="720" y2="310" stroke="#667085" stroke-width="1"/>
<text x="395" y="368" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#344054">temporal decay factor</text>
<polyline points="70.0,175.4 178.3,105.5 286.7,40.0 395.0,40.0 503.3,40.0 611.7,40.0 720.0,40.0" fill="none" stroke="#1d4ed8" stroke-width="2"/>
<circle cx="70.0" cy="175.4" r="3.5" fill="#1d4ed8"/>
<circle cx="178.3" cy="105.5" r="3.5" fill="#1d4ed8"/>
<circle cx="286.7" cy="40.0" r="3.5" fill="#1d4ed8"/>
<circle cx="395.0" cy="40.0" r="3.5" fill="#1d4ed8"/>
<circle cx="503.3" cy="40.0" r="3.5" fill="#1d4ed8"/>
<circle cx="611.7" cy="40.0" r="3.5" fill="#1d4ed8"/>
<circle cx="720.0" cy="40.0" r="3.5" fill="#1d4ed8"/>
<text x="82" y="56" font-family="sans-serif" font-size="11" fill="#1d4ed8">theory death (301 = alive)</text>
<polyline points="70.0,40.0 178.3,40.0 286.7,40.0 395.0,40.0 503.3,40.0 611.7,40.0 720.0,40.0" fill="none" stroke="#c2410c" stroke-width="2" stroke-dasharray="6 4"/>
<circle cx="70.0" cy="40.0" r="3.5" fill="#c2410c"/>
<circle cx="178.3" cy="40.0" r="3.5" fill="#c2410c"/>
<circle cx="286.7" cy="40.0" r="3.5" fill="#c2410c"/>
<circle cx="395.0" cy="40.0" r="3.5" fill="#c2410c"/>
<circle cx="503.3" cy="40.0" r="3.5" fill="#c2410c"/>
<circle cx="611.7" cy="40.0" r="3.5" fill="#c2410c"/>
<circle cx="720.0" cy="40.0" r="3.5" fill="#c2410c"/>
<text x="82" y="74" font-family="sans-serif" font-size="11" fill="#c2410c">stable-edge zero</text>
<text x="720" y="36" text-anchor="end" font-family="sans-serif" font-size="11" fill="#667085">301 = alive at cycle 300</text>
</svg>

The blue series is the median theory death cycle, with 301 at the top meaning the theory
layer was still live at cycle 300. The orange series is the first stable-edge zero, also
capped at 301. Both are read from the artifact; the plot is generated, not transcribed.

## Gates

| Gate | Result |
| --- | --- |
| G1_neutral_observer | pass |
| G2_anchor_228 | pass |
| G3_factor_live | pass |
| G4_denominators | pass |
| G5_seed_independence | pass |

## Predictions

| Prediction | Result |
| --- | --- |
| P1_anchor_228 | held |
| P2_monotone_death | held |
| P3_0985_before_099 | held |
| P4_no_decay_survives | held |
| P5_step_at_least_50 | held |
| P6_stable_zero_monotone | held |
| P7_interior_survivor | held |

## Reading

A step means the operating point is a threshold on this range; a smooth curve means a
gradient exists; only 1.0 surviving means the interior of this range is empty. In every
case, 1.0 is the ceiling control, not an adoption recommendation.

**`no_decay` survival is not adaptation.** This world is static and the protocol scores
no held-out prediction, revision or adaptation task. The 42 and 30 figures from the
degree-12 hub are not used here; Q047's `lattice_L1` `no_decay` stable peak is 21, and
this sweep's stable peak is reported above.

The control (shipped FULL at seed 20261023) matched the committed falsifier theories: **True**;
beliefs: **True**.
