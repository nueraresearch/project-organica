# Divergence onset — the first cycle at which the candidate pools differ

**Status.** Measured. Pre-registered in `docs/ONSET-INSTRUMENT-BRIEF.md` and journal §75 before this instrument existed.

**The question.** At what earliest engine cycle do the campaign-side and current-side candidate pools differ in membership, and what entered or left there? Not why identical pools admit differently — that question lost its subject on 2026-11-01 — and not where the admitted streams first differ, which the membership audit already answers analytically.

## 1. The checks

**F1 — reproduction of the corrected capture.** Cycles *k* and *k−1* captured here must reproduce `docs/divergence_cycle_capture.json`'s `set_identical` values **and** its pool IDs, on every arm-pair. **Passed on all 16 arm-pairs.**

**C1 — the control seed.** T1/20261101 at hash seeds 0 and 1, both arms, every captured cycle: the two runs hold **different** sets (21 of 24 measured cycles identical). **The membership difference is generic to hash-seeded construction, not specific to the divergence; no onset below is informative.**

## 2. Onset per arm-pair

**Witness cases** have an onset already fixed by arithmetic and are instrumentation validation; **search cases** were already divergent at *k−1* and carry the scientific content.

| Task | Seed | Divergence cycle *k* | Arm | Case | Onset | Entered | Left |
|---|---|---|---|---|---|---|---|
| T1 | 20261125 | 12 | B | search | cycle 3 | 70 | 0 |
| T1 | 20261125 | 12 | C | search | cycle 3 | 70 | 0 |
| T1 | 20261128 | 4 | B | witness | cycle 4 | 47 | 0 |
| T1 | 20261128 | 4 | C | witness | cycle 4 | 47 | 0 |
| T1 | 20261129 | 3 | B | witness | cycle 3 | 62 | 0 |
| T1 | 20261129 | 3 | C | witness | cycle 3 | 62 | 0 |
| T2 | 20261118 | 6 | B | witness | cycle 6 | 20 | 0 |
| T2 | 20261118 | 6 | C | witness | cycle 6 | 2 | 0 |
| T2 | 20261120 | 6 | B | search | cycle 4 | 11 | 0 |
| T2 | 20261120 | 6 | C | search | cycle 4 | 5 | 0 |
| T2 | 20261121 | 6 | B | search | cycle 5 | 23 | 0 |
| T2 | 20261121 | 6 | C | witness | cycle 6 | 6 | 0 |
| T2 | 20261123 | 6 | B | witness | cycle 6 | 19 | 0 |
| T2 | 20261123 | 6 | C | witness | cycle 6 | 14 | 0 |
| T2 | 20261130 | 6 | B | witness | cycle 6 | 32 | 0 |
| T2 | 20261130 | 6 | C | witness | cycle 6 | 28 | 0 |

**The five search cases.** **4 of 5** reached onset **strictly before *k−1***, which is what P2 asks; **5 of 5** were located at a specific cycle in total. A case that bottoms out at cycle 1 is reported as **≤ 1**, never as introduced there.

**The witness cases.** **11 of 11** landed at *k*, as arithmetic requires. A witness case landing anywhere else would be an instrument defect and is reported rather than reconciled.

**Insertion or replacement?** Across the 16 arm-pairs with a located onset, **0** candidate(s) left a pool at the cycle it first differed. Every onset is an **insertion**: the pools never shrink at the transition, they gain candidates.

## 3. What entered and left at each onset

- **T1/20261125 arm B, cycle 3** — entered 70, left 0
  - entered: `dream_analogy_1082cbdc`, `dream_analogy_4b43bbec`, `dream_analogy_68b6162d`, `dream_cond_45ba4f3d`, `dream_cond_aeff9bcd`, `dream_cond_c86f2f15`, `dream_mut_55337662`, `dream_mut_aa7e1065`, `exp_4963470c`, `exp_695edb13` …
- **T1/20261125 arm C, cycle 3** — entered 70, left 0
  - entered: `dream_analogy_1082cbdc`, `dream_analogy_4b43bbec`, `dream_analogy_68b6162d`, `dream_cond_45ba4f3d`, `dream_cond_aeff9bcd`, `dream_cond_c86f2f15`, `dream_mut_55337662`, `dream_mut_aa7e1065`, `exp_4963470c`, `exp_695edb13` …
- **T1/20261128 arm B, cycle 4** — entered 47, left 0
  - entered: `dream_analogy_fabff6cc`, `dream_cond_18e1d6f5`, `dream_cond_313a43d6`, `dream_cond_972d3173`, `dream_mut_760fc7e7`, `dream_mut_e71ad475`, `exp_036d5ff8`, `exp_0b49e797`, `exp_69fefc7c`, `exp_72ed1e29` …
- **T1/20261128 arm C, cycle 4** — entered 47, left 0
  - entered: `dream_analogy_fabff6cc`, `dream_cond_18e1d6f5`, `dream_cond_313a43d6`, `dream_cond_972d3173`, `dream_mut_760fc7e7`, `dream_mut_e71ad475`, `exp_036d5ff8`, `exp_0b49e797`, `exp_69fefc7c`, `exp_72ed1e29` …
- **T1/20261129 arm B, cycle 3** — entered 62, left 0
  - entered: `anomaly_aa6b1046`, `anomaly_e5a539be`, `anomaly_fb6ccd1e`, `dream_analogy_2996247c`, `dream_analogy_a9ca2e7b`, `dream_analogy_fabff6cc`, `dream_mut_1a1cab04`, `dream_mut_6c81b628`, `exp_08858048`, `exp_481eaeea` …
- **T1/20261129 arm C, cycle 3** — entered 62, left 0
  - entered: `anomaly_aa6b1046`, `anomaly_e5a539be`, `anomaly_fb6ccd1e`, `dream_analogy_2996247c`, `dream_analogy_a9ca2e7b`, `dream_analogy_fabff6cc`, `dream_mut_1a1cab04`, `dream_mut_6c81b628`, `exp_08858048`, `exp_481eaeea` …
- **T2/20261118 arm B, cycle 6** — entered 20, left 0
  - entered: `anomaly_29b7be02`, `anomaly_842c5bcc`, `dream_mut_70e14748`, `dream_mut_f06ec067`, `exp_107d054c`, `exp_e128d375`, `hyp_120eb70a`, `hyp_2ff50859`, `hyp_70f7c838`, `hyp_e6f8a3e6` …
- **T2/20261118 arm C, cycle 6** — entered 2, left 0
  - entered: `anomaly_29b7be02`, `anomaly_842c5bcc`
- **T2/20261120 arm B, cycle 4** — entered 11, left 0
  - entered: `anomaly_1c6de26c`, `anomaly_28f69a24`, `anomaly_7d77c40c`, `anomaly_82441e05`, `anomaly_9ac06e8c`, `dream_analogy_e5c75b28`, `exp_1b0b3869`, `hyp_9d441b50`, `hyp_a3c4b048`, `inv_81f1ef91` …
- **T2/20261120 arm C, cycle 4** — entered 5, left 0
  - entered: `anomaly_1c6de26c`, `anomaly_28f69a24`, `anomaly_7d77c40c`, `anomaly_82441e05`, `anomaly_9ac06e8c`
- **T2/20261121 arm B, cycle 5** — entered 23, left 0
  - entered: `anomaly_2cb3d759`, `anomaly_3b873ad2`, `anomaly_a382afab`, `dream_analogy_b8830751`, `dream_mut_9edcf1b0`, `dream_mut_e8ebfc53`, `exp_2f41537f`, `exp_da612387`, `exp_deaf7644`, `hyp_7fa4e5dd` …
- **T2/20261121 arm C, cycle 6** — entered 6, left 0
  - entered: `anomaly_1a1b1338`, `anomaly_8352ad0d`, `anomaly_8c8e09e6`, `anomaly_9db5184e`, `anomaly_a0072b14`, `loop_dc361b05`
- **T2/20261123 arm B, cycle 6** — entered 19, left 0
  - entered: `anomaly_21df6694`, `anomaly_3b1e873d`, `anomaly_41012317`, `anomaly_677c03f0`, `anomaly_7ad942e0`, `anomaly_9719b7a0`, `anomaly_9acd947b`, `anomaly_e6dced8c`, `anomaly_f5244467`, `anomaly_fe1ef7a5` …
- **T2/20261123 arm C, cycle 6** — entered 14, left 0
  - entered: `anomaly_21df6694`, `anomaly_3b1e873d`, `anomaly_41012317`, `anomaly_677c03f0`, `anomaly_7ad942e0`, `anomaly_9719b7a0`, `anomaly_9acd947b`, `anomaly_e6dced8c`, `anomaly_f5244467`, `anomaly_fe1ef7a5` …
- **T2/20261130 arm B, cycle 6** — entered 32, left 0
  - entered: `anomaly_98de25a9`, `anomaly_9d31c463`, `anomaly_a8af7322`, `anomaly_beb97bfb`, `anomaly_cf7c2929`, `dream_analogy_68b6162d`, `dream_mut_64b4d86f`, `dream_mut_859d957b`, `exp_85461809`, `exp_9cdfc6aa` …
- **T2/20261130 arm C, cycle 6** — entered 28, left 0
  - entered: `anomaly_98de25a9`, `anomaly_9d31c463`, `anomaly_a8af7322`, `anomaly_beb97bfb`, `anomaly_cf7c2929`, `dream_analogy_1082cbdc`, `dream_analogy_36e8eb9f`, `dream_analogy_6399c069`, `dream_analogy_68b6162d`, `dream_analogy_8b383d73` …

## 4. What this does not establish

It does not name the operation that introduces the difference. A candidate entering the pool at cycle *c* says an upstream write changed at *c*, not that a named function is responsible. It does not test H2, does not reopen the mechanism experiment, does not re-score D0, and changes no engine file.

**What C1 now licenses.** The control was re-run at the declared pair 0 and 1 — the audit's own pair is one seed twice, which is why the first pass could not adjudicate it. Its pools **differ**, so a membership difference is a generic consequence of hash-seeded construction and the onsets carry no divergence-specific weight.

## Provenance

- Artifact: `docs/divergence_onset.json` (membership audit sha256 `544ebd87bf86a7b38e98815449cd86e66a9ed75dbc3ffb1431cae34c76365e17`).
- Instrument: `benchmarks/divergence_onset.py`; the worker is `benchmarks/divergence_cycle_capture.py`, reused unchanged.
- Observer version: 1.
- Command: `python benchmarks/divergence_onset.py --workers 4` — 18 run(s), 0 cached, 637.1 s.

