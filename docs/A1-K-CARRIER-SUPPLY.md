# A1 carrier supply — what bounds absolute K?

Generated from `docs/a1_k_carrier_supply.json` by `python -m benchmarks.a1_k_carrier_supply --write`. Do not edit by hand.

**Not a result artifact.** A per-cycle replay of the 18 committed no-arm seeds. No target, threshold, freeze, grant or A1 cell.

## The question

The predictor join found no pre-run structural feature that predicts absolute K across worlds. This trace follows the carrier path itself: which edges become eligible for a loop, which enter the returned loop window, and which become K.

## What the trace shows

| Quantity | Value |
| --- | ---: |
| Seeds | 18 |
| Candidate edges | 1765 |
| Candidate K | 714 |
| Candidate K from loops | 653 |
| Candidate K dream-only | 61 |
| Engine-wide directed K (summed) | 3548 |
| Candidate edges never loop-eligible | 48 |
| Candidate edges eligible but never K | 1004 |
| Possible 2/3-cycles | 1421231 |
| Returned loops | 26932 |
| Loop slot share | 1.90% |
| Cycles at the 15-loop cap | 1753 of 2160 (81.16%) |

Candidate selection guarantees a directed-cycle member, but not a 2- or 3-cycle at the loop floor: **48** candidate edges never become loop-eligible. The much larger loss comes after eligibility: **1004** eligible candidates never become K. The loop builder sees hundreds of 2- and 3-cycles each cycle and returns at most **15**. Across all 18 seeds, only **1.90%** of the possible loops enter that window.

## Per block

| Block | Candidates | Candidate K | Engine-wide K | Candidate coverage | Never eligible | Eligible, never K | Cap cycles | Saturation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| current-16 | 382 | 228 | 980 | 59.7% | 0 | 154 | 85.3% | 48-107 |
| fresh-16 | 383 | 242 | 1031 | 63.2% | 0 | 141 | 81.7% | 36-119 |
| larger-28 | 1000 | 244 | 1537 | 24.4% | 48 | 709 | 76.5% | 60-113 |

The 28-tag block has roughly **2.6x** the candidate edges of a 16-tag block and produces almost exactly the same candidate K: **244** against **228** and **242**. More candidates enter the same 15-loop window, so coverage falls from **59.7-63.2%** to **24.4%** rather than the absolute count rising.

## What controls the count

1. **Eligibility is a small secondary gate.** The candidate stream is built from directed-cycle members, and the trace finds **48** candidate edges that never form a 2- or 3-cycle at the loop floor; one of those still becomes K through a dream. The other **1717** candidate edges are loop-eligible.
2. **The 15-loop output cap is the dominant window.** The loop builder sees **1421231** possible loops across the run and returns **26932**. In **81.2%** of seed-cycles the possible count exceeds the cap. An eligible edge becomes K only when a loop containing it ranks in the top 15 by path entropy, then strength, then id.
3. **The rank boundary is exact in the trace.** Every loop-carried K edge has a best rank of **1-15**; every eligible candidate that never becomes K has a best rank of **16 or higher** (median **49**, maximum **1217**). Of the **714** K candidate edges, **653** are loop-carried and **61** are dream-only.
4. **The carrier set stops growing before the horizon, but not always early.** Candidate K reaches its final value by cycle **36-119**; the median is **81.5**. The 120-cycle totals are fixed, but one seed adds its last candidate only at cycle 119.
5. **The A1 absolute K is candidate-stream K, not engine-wide K.** Summed across the 18 seed runs, the engine carries **3548** directed edges, while the one-orientation candidate stream records **714**. The difference is the candidate stream's chosen orientation and its pre-37 membership filter, not a second carrier process.

So the current answer is: **absolute candidate K is dominated by the fixed 15-loop output window**. Candidate supply does not scale with the number of candidate edges; the 28-tag block is the direct evidence. Eligibility adds a small 28-tag penalty, and dreams add a small number of K edges outside the loop window. This is a supply-window account, not a causal one: the trace does not raise the cap, so it cannot show that a larger window would raise K rather than reshuffle it.

## Per-seed summaries

| Block | Seed | Candidates | Candidate K | All K | Never eligible | Eligible, never K | Saturation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | 20630101 | 64 | 44 | 183 | 0 | 20 | 100 |
| current-16 | 20630102 | 63 | 31 | 151 | 0 | 32 | 76 |
| current-16 | 20630103 | 64 | 39 | 155 | 0 | 25 | 107 |
| current-16 | 20630104 | 64 | 35 | 147 | 0 | 29 | 88 |
| current-16 | 20630105 | 64 | 43 | 171 | 0 | 21 | 63 |
| current-16 | 20630106 | 63 | 36 | 173 | 0 | 27 | 48 |
| fresh-16 | 20650101 | 64 | 40 | 161 | 0 | 24 | 119 |
| fresh-16 | 20650102 | 64 | 37 | 164 | 0 | 27 | 36 |
| fresh-16 | 20650103 | 64 | 46 | 193 | 0 | 18 | 80 |
| fresh-16 | 20650104 | 64 | 42 | 184 | 0 | 22 | 111 |
| fresh-16 | 20650105 | 63 | 39 | 178 | 0 | 24 | 71 |
| fresh-16 | 20650106 | 64 | 38 | 151 | 0 | 26 | 113 |
| larger-28 | 20660101 | 169 | 23 | 174 | 9 | 137 | 79 |
| larger-28 | 20660102 | 167 | 40 | 268 | 9 | 118 | 80 |
| larger-28 | 20660103 | 172 | 42 | 254 | 13 | 117 | 60 |
| larger-28 | 20660104 | 165 | 55 | 277 | 3 | 107 | 113 |
| larger-28 | 20660105 | 169 | 47 | 303 | 4 | 118 | 83 |
| larger-28 | 20660106 | 158 | 37 | 261 | 10 | 112 | 96 |

## Reproduce

```bash
python -m benchmarks.a1_k_carrier_supply --check
python -m benchmarks.a1_k_carrier_supply --self-test
```

## What this does not claim

A replay-only trace on 18 committed no-arm seeds, two world families and one build. It shows which edges enter the capped loop readout and which do not; it does not raise the loop cap, does not show that raising it would increase K, and establishes no causal, capability, retention or transfer claim.
