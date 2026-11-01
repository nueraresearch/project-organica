# Divergence-cycle capture — the candidate pool at the cycle where the populations part company

**Status.** Measured 2026-10-31. It is the instrument the candidate-membership audit named as the next one: the membership audit found *where* the two candidate populations diverge, and this names *which candidates* were in the pool at that cycle. It does not re-score D0 and it does not change any verdict.

## 1. Why a second capture was needed

The membership audit captured the engine’s 4,000-row sleep window, and reported honestly that it could not explain the divergence: the window is a snapshot of the read-back at the arm’s snapshot point, which is two or three cycles before the end of the run, while the divergences are at sleep cycles 2 to 11. The window shows the population *near the snapshot point*; it cannot show the pool *at the divergence*.

This instrument captures the window at the divergence cycle itself.

## 2. How the capture is addressed, and how that is proved

The sleep service reads its window once per cycle, and the harness’s arm loop adds exactly two reads outside the cycle loop — one after the acquisition phase and one after the revision phase. So the i-th window read of an arm is the i-th cycle of that arm.

That correspondence is not assumed. The engine stores one `sleep:meta` event per cycle carrying that cycle’s number, and the window is read newest-first, so **the newest cycle marker in the i-th window must carry cycle *i***. The capture refuses to report a window whose marker does not say so, and the addressability of every window used below is recorded in the artifact.

**16 of 16** captured window pairs are addressed by their own marker.

## 3. The pool at the divergence cycle

**Campaign side** is the run whose fingerprint equals the campaign’s; **current side** is the run at the pinned hash seed, which is what the use-path audit measured. Arm C is the arm the D0 verdict was scored on; arm B is shown alongside it because arm C reads arm B’s recorded temporal graphs.

| Task | Seed | Divergence cycle | Arm | Campaign pool | Current pool | Both | Campaign only | Current only | Same set | Same order |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 | 20261125 | 11 | B | 280 | 274 | 272 | 8 | 2 | no | no |
| T1 | 20261125 | 11 | C | 260 | 255 | 252 | 8 | 3 | no | no |
| T1 | 20261128 | 3 | B | 37 | 37 | 37 | 0 | 0 | yes | no |
| T1 | 20261128 | 3 | C | 37 | 37 | 37 | 0 | 0 | yes | no |
| T1 | 20261129 | 2 | B | 39 | 39 | 39 | 0 | 0 | yes | no |
| T1 | 20261129 | 2 | C | 39 | 39 | 39 | 0 | 0 | yes | no |
| T2 | 20261118 | 5 | B | 28 | 28 | 28 | 0 | 0 | yes | no |
| T2 | 20261118 | 5 | C | 8 | 8 | 8 | 0 | 0 | yes | yes |
| T2 | 20261120 | 5 | B | 59 | 61 | 55 | 4 | 6 | no | no |
| T2 | 20261120 | 5 | C | 23 | 22 | 22 | 1 | 0 | no | no |
| T2 | 20261121 | 5 | B | 62 | 61 | 61 | 1 | 0 | no | no |
| T2 | 20261121 | 5 | C | 18 | 18 | 18 | 0 | 0 | yes | no |
| T2 | 20261123 | 5 | B | 23 | 23 | 23 | 0 | 0 | yes | no |
| T2 | 20261123 | 5 | C | 4 | 4 | 4 | 0 | 0 | yes | yes |
| T2 | 20261130 | 5 | B | 37 | 37 | 37 | 0 | 0 | yes | no |
| T2 | 20261130 | 5 | C | 10 | 10 | 10 | 0 | 0 | yes | yes |

### T1 / 20261125, cycle 11, arm B

- **In the campaign’s pool and not ours (8):** `anomaly_5d10a623`, `anomaly_ae98fe13`, `anomaly_e3f06f4a`, `dream_cond_bbedbdd9`, `exp_6a2dbdd3`, `inv_2177d7b0`, `question_f88106c4`, `theory_f88106c4`
- **In our pool and not the campaign’s (2):** `anomaly_c34c86c1`, `dream_cond_0f32fe15`

**Since the previous cycle.** The campaign side gained 48 candidate(s) and lost 48; the current side gained 43 and lost 48.

- gained by the campaign side: `anomaly_23b63138`, `anomaly_54edd873`, `anomaly_7291f90a`, `anomaly_ae98fe13`, `anomaly_c9ea3d58`, `dream_cond_81149fad`, `dream_cond_bbedbdd9`, `dream_mut_3f2f69c4`, `dream_mut_eed6dbe9`, `exp_48d69d81`, `exp_51248508`, `exp_6a2dbdd3`, `exp_773fe6b0`, `hyp_0834bc52`, `hyp_2ff50859`, `hyp_33f01105`, `hyp_5be3da66`, `hyp_8f1c7481`, `hyp_a3c4b048`, `hyp_b3c6c90d`, `hyp_c36bbb91`, `hyp_cecbe745`, `inv_02e7b18b`, `inv_1f070e58`, `inv_2177d7b0`, `inv_af1a9d80`, `loop_0834bc52`, `loop_33f01105`, `loop_69e70153`, `meta_cfd90af8`, `pred_050c5ef4`, `pred_b67853a9`, `process_0834bc52`, `process_33f01105`, `process_45ba4f3d`, `process_5be3da66`, `question_4081f8ec`, `question_5dcbf6cd`, `question_69e70153`, `question_f88106c4`, `theory_4081f8ec`, `theory_5dcbf6cd`, `theory_69e70153`, `theory_f88106c4`, `workflow_0834bc52`, `workflow_33f01105`, `workflow_45ba4f3d`, `workflow_5be3da66`
- gained by the current side: `anomaly_23b63138`, `anomaly_54edd873`, `anomaly_7291f90a`, `anomaly_c9ea3d58`, `dream_cond_0f32fe15`, `dream_cond_81149fad`, `dream_mut_3f2f69c4`, `dream_mut_eed6dbe9`, `exp_48d69d81`, `exp_51248508`, `exp_773fe6b0`, `hyp_0834bc52`, `hyp_2ff50859`, `hyp_33f01105`, `hyp_5be3da66`, `hyp_8f1c7481`, `hyp_a3c4b048`, `hyp_b3c6c90d`, `hyp_c36bbb91`, `hyp_cecbe745`, `inv_02e7b18b`, `inv_1f070e58`, `inv_af1a9d80`, `loop_0834bc52`, `loop_33f01105`, `loop_69e70153`, `meta_cfd90af8`, `pred_050c5ef4`, `pred_b67853a9`, `process_0834bc52`, `process_33f01105`, `process_45ba4f3d`, `process_5be3da66`, `question_4081f8ec`, `question_5dcbf6cd`, `question_69e70153`, `theory_4081f8ec`, `theory_5dcbf6cd`, `theory_69e70153`, `workflow_0834bc52`, `workflow_33f01105`, `workflow_45ba4f3d`, `workflow_5be3da66`
- lost by the campaign side: `anomaly_27da00e9`, `anomaly_28d771b0`, `anomaly_41f383df`, `anomaly_4a426aff`, `anomaly_54bbc07a`, `anomaly_85adf0bb`, `anomaly_931689a6`, `anomaly_b17cef4a`, `anomaly_b55ed761`, `anomaly_cbe369ec`, `anomaly_d1f50b4c`, `anomaly_e604a0c2`, `anomaly_efd4670a`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_cond_45ba4f3d`, `dream_cond_aeff9bcd`, `dream_mut_55337662`, `exp_14f62bf0`, `exp_4963470c`, `exp_4e8f09df`, `exp_695edb13`, `exp_ed2c60fa`, `hyp_18e1d6f5`, `hyp_45ba4f3d`, `hyp_5711aaab`, `hyp_aa517900`, `hyp_aeff9bcd`, `hyp_b516bed8`, `hyp_c86f2f15`, `inv_6111b8d8`, `inv_7c1ea7a8`, `inv_8b05d0b5`, `inv_943684a9`, `inv_b28ec89c`, `process_8e76c158`, `process_c9409791`, `process_e70d60c0`, `question_0cc6644f`, `theory_17655226`, `theory_27da00e9`, `theory_bef66e35`, `theory_d73713a5`, `theory_f2459dc9`, `workflow_7ff50e2b`, `workflow_c9409791`, `workflow_e70d60c0`
- lost by the current side: `anomaly_27da00e9`, `anomaly_28d771b0`, `anomaly_41f383df`, `anomaly_4a426aff`, `anomaly_54bbc07a`, `anomaly_85adf0bb`, `anomaly_931689a6`, `anomaly_b17cef4a`, `anomaly_b55ed761`, `anomaly_cbe369ec`, `anomaly_e3f06f4a`, `anomaly_e604a0c2`, `anomaly_efd4670a`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_cond_45ba4f3d`, `dream_cond_aeff9bcd`, `dream_mut_55337662`, `exp_14f62bf0`, `exp_4963470c`, `exp_4e8f09df`, `exp_695edb13`, `exp_ed2c60fa`, `hyp_18e1d6f5`, `hyp_45ba4f3d`, `hyp_5711aaab`, `hyp_aa517900`, `hyp_aeff9bcd`, `hyp_b516bed8`, `hyp_c86f2f15`, `inv_6111b8d8`, `inv_7c1ea7a8`, `inv_8b05d0b5`, `inv_943684a9`, `inv_b28ec89c`, `process_8e76c158`, `process_c9409791`, `process_e70d60c0`, `question_0cc6644f`, `theory_17655226`, `theory_27da00e9`, `theory_bef66e35`, `theory_d73713a5`, `theory_f2459dc9`, `workflow_7ff50e2b`, `workflow_c9409791`, `workflow_e70d60c0`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 20 | 18 |
| dream | 14 | 14 |
| experiment | 11 | 10 |
| hypothesis | 40 | 40 |
| investigation | 11 | 10 |
| loop_candidate | 35 | 35 |
| meta_concept | 16 | 16 |
| phrase_candidate | 6 | 6 |
| prediction_candidate | 71 | 71 |
| process_candidate | 17 | 17 |
| question | 11 | 10 |
| theory | 11 | 10 |
| workflow_concept | 17 | 17 |

### T1 / 20261125, cycle 11, arm C

- **In the campaign’s pool and not ours (8):** `anomaly_5d10a623`, `anomaly_ae98fe13`, `anomaly_e3f06f4a`, `dream_cond_bbedbdd9`, `exp_6a2dbdd3`, `inv_2177d7b0`, `question_f88106c4`, `theory_f88106c4`
- **In our pool and not the campaign’s (3):** `anomaly_c34c86c1`, `dream_cond_0f32fe15`, `question_0cc6644f`

**Since the previous cycle.** The campaign side gained 48 candidate(s) and lost 45; the current side gained 43 and lost 44.

- gained by the campaign side: `anomaly_23b63138`, `anomaly_54edd873`, `anomaly_7291f90a`, `anomaly_ae98fe13`, `anomaly_c9ea3d58`, `dream_cond_81149fad`, `dream_cond_bbedbdd9`, `dream_mut_3f2f69c4`, `dream_mut_eed6dbe9`, `exp_48d69d81`, `exp_51248508`, `exp_6a2dbdd3`, `exp_773fe6b0`, `hyp_0834bc52`, `hyp_2ff50859`, `hyp_33f01105`, `hyp_5be3da66`, `hyp_8f1c7481`, `hyp_a3c4b048`, `hyp_b3c6c90d`, `hyp_c36bbb91`, `hyp_cecbe745`, `inv_02e7b18b`, `inv_1f070e58`, `inv_2177d7b0`, `inv_af1a9d80`, `loop_0834bc52`, `loop_33f01105`, `loop_69e70153`, `meta_cfd90af8`, `pred_050c5ef4`, `pred_b67853a9`, `process_0834bc52`, `process_33f01105`, `process_45ba4f3d`, `process_5be3da66`, `question_4081f8ec`, `question_5dcbf6cd`, `question_69e70153`, `question_f88106c4`, `theory_4081f8ec`, `theory_5dcbf6cd`, `theory_69e70153`, `theory_f88106c4`, `workflow_0834bc52`, `workflow_33f01105`, `workflow_45ba4f3d`, `workflow_5be3da66`
- gained by the current side: `anomaly_23b63138`, `anomaly_54edd873`, `anomaly_7291f90a`, `anomaly_c9ea3d58`, `dream_cond_0f32fe15`, `dream_cond_81149fad`, `dream_mut_3f2f69c4`, `dream_mut_eed6dbe9`, `exp_48d69d81`, `exp_51248508`, `exp_773fe6b0`, `hyp_0834bc52`, `hyp_2ff50859`, `hyp_33f01105`, `hyp_5be3da66`, `hyp_8f1c7481`, `hyp_a3c4b048`, `hyp_b3c6c90d`, `hyp_c36bbb91`, `hyp_cecbe745`, `inv_02e7b18b`, `inv_1f070e58`, `inv_af1a9d80`, `loop_0834bc52`, `loop_33f01105`, `loop_69e70153`, `meta_cfd90af8`, `pred_050c5ef4`, `pred_b67853a9`, `process_0834bc52`, `process_33f01105`, `process_45ba4f3d`, `process_5be3da66`, `question_4081f8ec`, `question_5dcbf6cd`, `question_69e70153`, `theory_4081f8ec`, `theory_5dcbf6cd`, `theory_69e70153`, `workflow_0834bc52`, `workflow_33f01105`, `workflow_45ba4f3d`, `workflow_5be3da66`
- lost by the campaign side: `anomaly_27da00e9`, `anomaly_28d771b0`, `anomaly_41f383df`, `anomaly_4a426aff`, `anomaly_54bbc07a`, `anomaly_85adf0bb`, `anomaly_931689a6`, `anomaly_b17cef4a`, `anomaly_b55ed761`, `anomaly_cbe369ec`, `anomaly_d1f50b4c`, `anomaly_e604a0c2`, `anomaly_efd4670a`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_cond_45ba4f3d`, `dream_mut_55337662`, `exp_14f62bf0`, `exp_4963470c`, `exp_4e8f09df`, `exp_ed2c60fa`, `hyp_18e1d6f5`, `hyp_45ba4f3d`, `hyp_5711aaab`, `hyp_aa517900`, `hyp_aeff9bcd`, `hyp_b516bed8`, `hyp_c86f2f15`, `inv_6111b8d8`, `inv_7c1ea7a8`, `inv_8b05d0b5`, `inv_b28ec89c`, `process_8e76c158`, `process_c9409791`, `process_e70d60c0`, `question_0cc6644f`, `theory_17655226`, `theory_27da00e9`, `theory_bef66e35`, `theory_d73713a5`, `theory_f2459dc9`, `workflow_7ff50e2b`, `workflow_c9409791`, `workflow_e70d60c0`
- lost by the current side: `anomaly_27da00e9`, `anomaly_28d771b0`, `anomaly_41f383df`, `anomaly_4a426aff`, `anomaly_54bbc07a`, `anomaly_85adf0bb`, `anomaly_931689a6`, `anomaly_b17cef4a`, `anomaly_b55ed761`, `anomaly_cbe369ec`, `anomaly_e3f06f4a`, `anomaly_e604a0c2`, `anomaly_efd4670a`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_cond_45ba4f3d`, `dream_mut_55337662`, `exp_14f62bf0`, `exp_4963470c`, `exp_4e8f09df`, `exp_ed2c60fa`, `hyp_18e1d6f5`, `hyp_45ba4f3d`, `hyp_5711aaab`, `hyp_aa517900`, `hyp_aeff9bcd`, `hyp_b516bed8`, `hyp_c86f2f15`, `inv_6111b8d8`, `inv_7c1ea7a8`, `inv_8b05d0b5`, `inv_b28ec89c`, `process_8e76c158`, `process_c9409791`, `process_e70d60c0`, `theory_17655226`, `theory_27da00e9`, `theory_bef66e35`, `theory_d73713a5`, `theory_f2459dc9`, `workflow_7ff50e2b`, `workflow_c9409791`, `workflow_e70d60c0`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 20 | 18 |
| dream | 15 | 15 |
| experiment | 12 | 11 |
| hypothesis | 40 | 40 |
| investigation | 12 | 11 |
| loop_candidate | 35 | 35 |
| meta_concept | 16 | 16 |
| phrase_candidate | 6 | 6 |
| prediction_candidate | 48 | 48 |
| process_candidate | 17 | 17 |
| question | 11 | 11 |
| theory | 11 | 10 |
| workflow_concept | 17 | 17 |

### T1 / 20261128, cycle 3, arm B

- In the campaign’s pool and not ours: **none**.
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 28 candidate(s) and lost 0; the current side gained 28 and lost 0.

- gained by the campaign side: `anomaly_2f69dab0`, `anomaly_d81bba30`, `anomaly_eb5eb07e`, `anomaly_f98b9a8a`, `dream_analogy_2996247c`, `dream_analogy_456a14f9`, `dream_analogy_a9ca2e7b`, `exp_a1917fa9`, `exp_b805662b`, `exp_eb3f20a6`, `hyp_34e4a7fb`, `hyp_5ec1ef7e`, `inv_6cdc4284`, `inv_7bc8a3f5`, `inv_ab46b17a`, `loop_417da26f`, `loop_d81bba30`, `loop_fc1dfe44`, `meta_2655399a`, `meta_fd8ed7f1`, `phrase_e2484dcd`, `pred_1908f98b`, `pred_417da26f`, `pred_5242671c`, `pred_b38b643c`, `pred_fc1dfe44`, `process_34e4a7fb`, `workflow_34e4a7fb`
- gained by the current side: `anomaly_2f69dab0`, `anomaly_d81bba30`, `anomaly_eb5eb07e`, `anomaly_f98b9a8a`, `dream_analogy_2996247c`, `dream_analogy_456a14f9`, `dream_analogy_a9ca2e7b`, `exp_a1917fa9`, `exp_b805662b`, `exp_eb3f20a6`, `hyp_34e4a7fb`, `hyp_5ec1ef7e`, `inv_6cdc4284`, `inv_7bc8a3f5`, `inv_ab46b17a`, `loop_417da26f`, `loop_d81bba30`, `loop_fc1dfe44`, `meta_2655399a`, `meta_fd8ed7f1`, `phrase_e2484dcd`, `pred_1908f98b`, `pred_417da26f`, `pred_5242671c`, `pred_b38b643c`, `pred_fc1dfe44`, `process_34e4a7fb`, `workflow_34e4a7fb`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 5 | 5 |
| dream | 3 | 3 |
| experiment | 3 | 3 |
| hypothesis | 2 | 2 |
| investigation | 3 | 3 |
| loop_candidate | 4 | 4 |
| meta_concept | 2 | 2 |
| phrase_candidate | 3 | 3 |
| prediction_candidate | 10 | 10 |
| process_candidate | 1 | 1 |
| workflow_concept | 1 | 1 |

### T1 / 20261128, cycle 3, arm C

- In the campaign’s pool and not ours: **none**.
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 28 candidate(s) and lost 0; the current side gained 28 and lost 0.

- gained by the campaign side: `anomaly_2f69dab0`, `anomaly_d81bba30`, `anomaly_eb5eb07e`, `anomaly_f98b9a8a`, `dream_analogy_2996247c`, `dream_analogy_456a14f9`, `dream_analogy_a9ca2e7b`, `exp_a1917fa9`, `exp_b805662b`, `exp_eb3f20a6`, `hyp_34e4a7fb`, `hyp_5ec1ef7e`, `inv_6cdc4284`, `inv_7bc8a3f5`, `inv_ab46b17a`, `loop_417da26f`, `loop_d81bba30`, `loop_fc1dfe44`, `meta_2655399a`, `meta_fd8ed7f1`, `phrase_e2484dcd`, `pred_1908f98b`, `pred_417da26f`, `pred_5242671c`, `pred_b38b643c`, `pred_fc1dfe44`, `process_34e4a7fb`, `workflow_34e4a7fb`
- gained by the current side: `anomaly_2f69dab0`, `anomaly_d81bba30`, `anomaly_eb5eb07e`, `anomaly_f98b9a8a`, `dream_analogy_2996247c`, `dream_analogy_456a14f9`, `dream_analogy_a9ca2e7b`, `exp_a1917fa9`, `exp_b805662b`, `exp_eb3f20a6`, `hyp_34e4a7fb`, `hyp_5ec1ef7e`, `inv_6cdc4284`, `inv_7bc8a3f5`, `inv_ab46b17a`, `loop_417da26f`, `loop_d81bba30`, `loop_fc1dfe44`, `meta_2655399a`, `meta_fd8ed7f1`, `phrase_e2484dcd`, `pred_1908f98b`, `pred_417da26f`, `pred_5242671c`, `pred_b38b643c`, `pred_fc1dfe44`, `process_34e4a7fb`, `workflow_34e4a7fb`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 5 | 5 |
| dream | 3 | 3 |
| experiment | 3 | 3 |
| hypothesis | 2 | 2 |
| investigation | 3 | 3 |
| loop_candidate | 4 | 4 |
| meta_concept | 2 | 2 |
| phrase_candidate | 3 | 3 |
| prediction_candidate | 10 | 10 |
| process_candidate | 1 | 1 |
| workflow_concept | 1 | 1 |

### T1 / 20261129, cycle 2, arm B

- In the campaign’s pool and not ours: **none**.
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 32 candidate(s) and lost 0; the current side gained 32 and lost 0.

- gained by the campaign side: `anomaly_07edbffc`, `anomaly_e5da7fbd`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_analogy_b0a67091`, `exp_14f62bf0`, `exp_296eb82c`, `exp_4e8f09df`, `exp_ed2c60fa`, `hyp_23c7c1fa`, `hyp_9e19432e`, `inv_2395dfbb`, `inv_6111b8d8`, `inv_8b05d0b5`, `inv_b28ec89c`, `loop_1908f98b`, `loop_313a43d6`, `loop_417da26f`, `loop_b58e2626`, `meta_548a4251`, `meta_b1601f69`, `phrase_b58e2626`, `pred_1908f98b`, `pred_313a43d6`, `pred_417da26f`, `pred_5242671c`, `pred_972d3173`, `pred_d22148a4`, `pred_de4bea22`, `process_23c7c1fa`, `workflow_23c7c1fa`
- gained by the current side: `anomaly_07edbffc`, `anomaly_e5da7fbd`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_analogy_b0a67091`, `exp_14f62bf0`, `exp_296eb82c`, `exp_4e8f09df`, `exp_ed2c60fa`, `hyp_23c7c1fa`, `hyp_9e19432e`, `inv_2395dfbb`, `inv_6111b8d8`, `inv_8b05d0b5`, `inv_b28ec89c`, `loop_1908f98b`, `loop_313a43d6`, `loop_417da26f`, `loop_b58e2626`, `meta_548a4251`, `meta_b1601f69`, `phrase_b58e2626`, `pred_1908f98b`, `pred_313a43d6`, `pred_417da26f`, `pred_5242671c`, `pred_972d3173`, `pred_d22148a4`, `pred_de4bea22`, `process_23c7c1fa`, `workflow_23c7c1fa`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 6 | 6 |
| dream | 4 | 4 |
| experiment | 4 | 4 |
| hypothesis | 2 | 2 |
| investigation | 4 | 4 |
| loop_candidate | 5 | 5 |
| meta_concept | 2 | 2 |
| phrase_candidate | 1 | 1 |
| prediction_candidate | 9 | 9 |
| process_candidate | 1 | 1 |
| workflow_concept | 1 | 1 |

### T1 / 20261129, cycle 2, arm C

- In the campaign’s pool and not ours: **none**.
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 32 candidate(s) and lost 0; the current side gained 32 and lost 0.

- gained by the campaign side: `anomaly_07edbffc`, `anomaly_e5da7fbd`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_analogy_b0a67091`, `exp_14f62bf0`, `exp_296eb82c`, `exp_4e8f09df`, `exp_ed2c60fa`, `hyp_23c7c1fa`, `hyp_9e19432e`, `inv_2395dfbb`, `inv_6111b8d8`, `inv_8b05d0b5`, `inv_b28ec89c`, `loop_1908f98b`, `loop_313a43d6`, `loop_417da26f`, `loop_b58e2626`, `meta_548a4251`, `meta_b1601f69`, `phrase_b58e2626`, `pred_1908f98b`, `pred_313a43d6`, `pred_417da26f`, `pred_5242671c`, `pred_972d3173`, `pred_d22148a4`, `pred_de4bea22`, `process_23c7c1fa`, `workflow_23c7c1fa`
- gained by the current side: `anomaly_07edbffc`, `anomaly_e5da7fbd`, `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_analogy_a2582513`, `dream_analogy_b0a67091`, `exp_14f62bf0`, `exp_296eb82c`, `exp_4e8f09df`, `exp_ed2c60fa`, `hyp_23c7c1fa`, `hyp_9e19432e`, `inv_2395dfbb`, `inv_6111b8d8`, `inv_8b05d0b5`, `inv_b28ec89c`, `loop_1908f98b`, `loop_313a43d6`, `loop_417da26f`, `loop_b58e2626`, `meta_548a4251`, `meta_b1601f69`, `phrase_b58e2626`, `pred_1908f98b`, `pred_313a43d6`, `pred_417da26f`, `pred_5242671c`, `pred_972d3173`, `pred_d22148a4`, `pred_de4bea22`, `process_23c7c1fa`, `workflow_23c7c1fa`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 6 | 6 |
| dream | 4 | 4 |
| experiment | 4 | 4 |
| hypothesis | 2 | 2 |
| investigation | 4 | 4 |
| loop_candidate | 5 | 5 |
| meta_concept | 2 | 2 |
| phrase_candidate | 1 | 1 |
| prediction_candidate | 9 | 9 |
| process_candidate | 1 | 1 |
| workflow_concept | 1 | 1 |

### T2 / 20261118, cycle 5, arm B

- In the campaign’s pool and not ours: **none**.
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 25 candidate(s) and lost 0; the current side gained 25 and lost 0.

- gained by the campaign side: `anomaly_7a9d11ec`, `anomaly_9218f450`, `anomaly_f55ba952`, `anomaly_fe1fa533`, `dream_analogy_456a14f9`, `dream_analogy_68b6162d`, `dream_analogy_85c565a9`, `exp_29143192`, `exp_2c10c6c8`, `exp_b805662b`, `hyp_48d0e5fd`, `hyp_8c033fb0`, `inv_6cdc4284`, `inv_92a76c4d`, `inv_c2cd4e42`, `loop_e6f8a3e6`, `meta_fa659831`, `meta_fd8ed7f1`, `pred_120eb70a`, `pred_53a54188`, `pred_a2efceaf`, `pred_a908d7e0`, `pred_e6f8a3e6`, `process_8c033fb0`, `workflow_8c033fb0`
- gained by the current side: `anomaly_7a9d11ec`, `anomaly_9218f450`, `anomaly_f55ba952`, `anomaly_fe1fa533`, `dream_analogy_456a14f9`, `dream_analogy_68b6162d`, `dream_analogy_85c565a9`, `exp_29143192`, `exp_2c10c6c8`, `exp_b805662b`, `hyp_48d0e5fd`, `hyp_8c033fb0`, `inv_6cdc4284`, `inv_92a76c4d`, `inv_c2cd4e42`, `loop_e6f8a3e6`, `meta_fa659831`, `meta_fd8ed7f1`, `pred_120eb70a`, `pred_53a54188`, `pred_a2efceaf`, `pred_a908d7e0`, `pred_e6f8a3e6`, `process_8c033fb0`, `workflow_8c033fb0`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 4 | 4 |
| dream | 3 | 3 |
| experiment | 3 | 3 |
| hypothesis | 2 | 2 |
| investigation | 3 | 3 |
| loop_candidate | 2 | 2 |
| meta_concept | 2 | 2 |
| prediction_candidate | 7 | 7 |
| process_candidate | 1 | 1 |
| workflow_concept | 1 | 1 |

### T2 / 20261118, cycle 5, arm C

- In the campaign’s pool and not ours: **none**.
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 7 candidate(s) and lost 0; the current side gained 7 and lost 0.

- gained by the campaign side: `anomaly_7a9d11ec`, `anomaly_9218f450`, `anomaly_f55ba952`, `anomaly_fe1fa533`, `loop_e6f8a3e6`, `pred_53a54188`, `pred_a908d7e0`
- gained by the current side: `anomaly_7a9d11ec`, `anomaly_9218f450`, `anomaly_f55ba952`, `anomaly_fe1fa533`, `loop_e6f8a3e6`, `pred_53a54188`, `pred_a908d7e0`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 4 | 4 |
| loop_candidate | 2 | 2 |
| prediction_candidate | 2 | 2 |

### T2 / 20261120, cycle 5, arm B

- **In the campaign’s pool and not ours (4):** `anomaly_9ac06e8c`, `exp_1b0b3869`, `inv_81f1ef91`, `pred_4dc93d10`
- **In our pool and not the campaign’s (6):** `dream_analogy_7fd9b8ba`, `dream_analogy_ae902b2a`, `exp_4b8bb67f`, `exp_d7c5ea03`, `inv_494e629a`, `inv_85f71f22`

**Since the previous cycle.** The campaign side gained 13 candidate(s) and lost 0; the current side gained 13 and lost 0.

- gained by the campaign side: `anomaly_0f9a2c29`, `anomaly_29e93ad4`, `anomaly_3329a612`, `dream_analogy_fabff6cc`, `exp_c9ab6eb3`, `inv_1320ba16`, `loop_18e1d6f5`, `loop_57b28f60`, `pred_050eeda2`, `pred_18e1d6f5`, `pred_4dc93d10`, `pred_76555b97`, `pred_fc1dfe44`
- gained by the current side: `anomaly_0f9a2c29`, `anomaly_29e93ad4`, `anomaly_3329a612`, `dream_analogy_fabff6cc`, `exp_c9ab6eb3`, `inv_1320ba16`, `loop_18e1d6f5`, `loop_57b28f60`, `pred_050eeda2`, `pred_18e1d6f5`, `pred_57b28f60`, `pred_76555b97`, `pred_fc1dfe44`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 18 | 17 |
| dream | 7 | 9 |
| experiment | 7 | 8 |
| hypothesis | 4 | 4 |
| investigation | 7 | 8 |
| loop_candidate | 3 | 3 |
| meta_concept | 2 | 2 |
| phrase_candidate | 1 | 1 |
| prediction_candidate | 8 | 7 |
| process_candidate | 1 | 1 |
| workflow_concept | 1 | 1 |

### T2 / 20261120, cycle 5, arm C

- **In the campaign’s pool and not ours (1):** `anomaly_9ac06e8c`
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 6 candidate(s) and lost 0; the current side gained 6 and lost 0.

- gained by the campaign side: `anomaly_0f9a2c29`, `anomaly_29e93ad4`, `anomaly_3329a612`, `loop_18e1d6f5`, `loop_57b28f60`, `pred_fc1dfe44`
- gained by the current side: `anomaly_0f9a2c29`, `anomaly_29e93ad4`, `anomaly_3329a612`, `loop_18e1d6f5`, `loop_57b28f60`, `pred_fc1dfe44`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 18 | 17 |
| loop_candidate | 3 | 3 |
| phrase_candidate | 1 | 1 |
| prediction_candidate | 1 | 1 |

### T2 / 20261121, cycle 5, arm B

- **In the campaign’s pool and not ours (1):** `dream_analogy_b8830751`
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 23 candidate(s) and lost 0; the current side gained 22 and lost 0.

- gained by the campaign side: `anomaly_2cb3d759`, `anomaly_3b873ad2`, `anomaly_a382afab`, `dream_analogy_b8830751`, `dream_mut_9edcf1b0`, `dream_mut_e8ebfc53`, `exp_2f41537f`, `exp_da612387`, `exp_deaf7644`, `hyp_7fa4e5dd`, `hyp_b1b5b638`, `hyp_c86f2f15`, `hyp_ecfe4694`, `inv_578ae685`, `inv_a9c92401`, `inv_f2956ebf`, `loop_a5f498cc`, `meta_f0a5da17`, `pred_70575cbc`, `process_b1b5b638`, `question_49e76748`, `theory_49e76748`, `workflow_b1b5b638`
- gained by the current side: `anomaly_2cb3d759`, `anomaly_3b873ad2`, `anomaly_a382afab`, `dream_mut_9edcf1b0`, `dream_mut_e8ebfc53`, `exp_2f41537f`, `exp_da612387`, `exp_deaf7644`, `hyp_7fa4e5dd`, `hyp_b1b5b638`, `hyp_c86f2f15`, `hyp_ecfe4694`, `inv_578ae685`, `inv_a9c92401`, `inv_f2956ebf`, `loop_a5f498cc`, `meta_f0a5da17`, `pred_70575cbc`, `process_b1b5b638`, `question_49e76748`, `theory_49e76748`, `workflow_b1b5b638`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 14 | 14 |
| dream | 7 | 6 |
| experiment | 7 | 7 |
| hypothesis | 6 | 6 |
| investigation | 7 | 7 |
| loop_candidate | 3 | 3 |
| meta_concept | 3 | 3 |
| prediction_candidate | 9 | 9 |
| process_candidate | 2 | 2 |
| question | 1 | 1 |
| theory | 1 | 1 |
| workflow_concept | 2 | 2 |

### T2 / 20261121, cycle 5, arm C

- In the campaign’s pool and not ours: **none**.
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 4 candidate(s) and lost 0; the current side gained 4 and lost 0.

- gained by the campaign side: `anomaly_2cb3d759`, `anomaly_3b873ad2`, `anomaly_a382afab`, `loop_a5f498cc`
- gained by the current side: `anomaly_2cb3d759`, `anomaly_3b873ad2`, `anomaly_a382afab`, `loop_a5f498cc`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 14 | 14 |
| loop_candidate | 3 | 3 |
| prediction_candidate | 1 | 1 |

### T2 / 20261123, cycle 5, arm B

- In the campaign’s pool and not ours: **none**.
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 18 candidate(s) and lost 0; the current side gained 18 and lost 0.

- gained by the campaign side: `anomaly_156c72ae`, `anomaly_54d9f6f7`, `anomaly_ba445078`, `dream_analogy_2996247c`, `dream_analogy_85c565a9`, `dream_analogy_fabff6cc`, `exp_29143192`, `exp_a1917fa9`, `exp_c9ab6eb3`, `hyp_2350911c`, `inv_1320ba16`, `inv_92a76c4d`, `inv_ab46b17a`, `meta_2655399a`, `meta_fa659831`, `pred_03b0ce09`, `process_103be77b`, `workflow_103be77b`
- gained by the current side: `anomaly_156c72ae`, `anomaly_54d9f6f7`, `anomaly_ba445078`, `dream_analogy_2996247c`, `dream_analogy_85c565a9`, `dream_analogy_fabff6cc`, `exp_29143192`, `exp_a1917fa9`, `exp_c9ab6eb3`, `hyp_2350911c`, `inv_1320ba16`, `inv_92a76c4d`, `inv_ab46b17a`, `meta_2655399a`, `meta_fa659831`, `pred_03b0ce09`, `process_103be77b`, `workflow_103be77b`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 3 | 3 |
| dream | 3 | 3 |
| experiment | 3 | 3 |
| hypothesis | 1 | 1 |
| investigation | 3 | 3 |
| loop_candidate | 1 | 1 |
| meta_concept | 2 | 2 |
| prediction_candidate | 5 | 5 |
| process_candidate | 1 | 1 |
| workflow_concept | 1 | 1 |

### T2 / 20261123, cycle 5, arm C

- In the campaign’s pool and not ours: **none**.
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 3 candidate(s) and lost 0; the current side gained 3 and lost 0.

- gained by the campaign side: `anomaly_156c72ae`, `anomaly_54d9f6f7`, `anomaly_ba445078`
- gained by the current side: `anomaly_156c72ae`, `anomaly_54d9f6f7`, `anomaly_ba445078`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 3 | 3 |
| loop_candidate | 1 | 1 |

### T2 / 20261130, cycle 5, arm B

- In the campaign’s pool and not ours: **none**.
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 33 candidate(s) and lost 0; the current side gained 33 and lost 0.

- gained by the campaign side: `anomaly_2020d089`, `anomaly_30647f48`, `anomaly_41a060d2`, `anomaly_f2052a36`, `dream_analogy_36e8eb9f`, `dream_analogy_6399c069`, `dream_analogy_8b383d73`, `dream_analogy_a9ca2e7b`, `dream_analogy_fabff6cc`, `exp_14f62bf0`, `exp_c9ab6eb3`, `exp_d31ecf56`, `exp_eb3f20a6`, `exp_ed2c60fa`, `hyp_03ca6880`, `hyp_c81c8901`, `inv_0a1a36b6`, `inv_1320ba16`, `inv_6111b8d8`, `inv_7bc8a3f5`, `inv_b28ec89c`, `loop_63ac32e2`, `meta_548a4251`, `meta_e0592018`, `pred_44c9dff5`, `pred_63ac32e2`, `pred_7498423f`, `pred_78029800`, `pred_a6f80540`, `pred_c39ad859`, `pred_dc7da818`, `process_c81c8901`, `workflow_c81c8901`
- gained by the current side: `anomaly_2020d089`, `anomaly_30647f48`, `anomaly_41a060d2`, `anomaly_f2052a36`, `dream_analogy_36e8eb9f`, `dream_analogy_6399c069`, `dream_analogy_8b383d73`, `dream_analogy_a9ca2e7b`, `dream_analogy_fabff6cc`, `exp_14f62bf0`, `exp_c9ab6eb3`, `exp_d31ecf56`, `exp_eb3f20a6`, `exp_ed2c60fa`, `hyp_03ca6880`, `hyp_c81c8901`, `inv_0a1a36b6`, `inv_1320ba16`, `inv_6111b8d8`, `inv_7bc8a3f5`, `inv_b28ec89c`, `loop_63ac32e2`, `meta_548a4251`, `meta_e0592018`, `pred_44c9dff5`, `pred_63ac32e2`, `pred_7498423f`, `pred_78029800`, `pred_a6f80540`, `pred_c39ad859`, `pred_dc7da818`, `process_c81c8901`, `workflow_c81c8901`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 4 | 4 |
| dream | 5 | 5 |
| experiment | 5 | 5 |
| hypothesis | 2 | 2 |
| investigation | 5 | 5 |
| loop_candidate | 2 | 2 |
| meta_concept | 2 | 2 |
| phrase_candidate | 1 | 1 |
| prediction_candidate | 9 | 9 |
| process_candidate | 1 | 1 |
| workflow_concept | 1 | 1 |

### T2 / 20261130, cycle 5, arm C

- In the campaign’s pool and not ours: **none**.
- In our pool and not the campaign’s: **none**.

**Since the previous cycle.** The campaign side gained 8 candidate(s) and lost 0; the current side gained 8 and lost 0.

- gained by the campaign side: `anomaly_2020d089`, `anomaly_30647f48`, `anomaly_41a060d2`, `anomaly_f2052a36`, `loop_63ac32e2`, `pred_7498423f`, `pred_a6f80540`, `pred_c39ad859`
- gained by the current side: `anomaly_2020d089`, `anomaly_30647f48`, `anomaly_41a060d2`, `anomaly_f2052a36`, `loop_63ac32e2`, `pred_7498423f`, `pred_a6f80540`, `pred_c39ad859`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 4 | 4 |
| loop_candidate | 2 | 2 |
| phrase_candidate | 1 | 1 |
| prediction_candidate | 3 | 3 |

## 4. The order of the pool, and where the order parts company

**The set and the order are two different findings.** A pool is a sequence: the engine reads the sleep window back newest-first and hands the candidates to the rest of the cycle in that order. Two pools can hold exactly the same candidates and still be different pools, so which of the two things happened on a given seed is the question this section answers.

Across the 16 arm-pairs, the two sides hold the **same set** of candidate IDs at the divergence cycle in **11** of them, and the **same order** in **3**.

| Task | Seed | Cycle | Arm | Same set | Same order | First differing position | Campaign’s candidate there | Ours |
|---|---|---|---|---|---|---|---|---|
| T1 | 20261125 | 11 | B | no | no | 0 | `exp_51248508` | `exp_80d6e0b7` |
| T1 | 20261125 | 11 | C | no | no | 0 | `exp_51248508` | `exp_80d6e0b7` |
| T1 | 20261128 | 3 | B | yes | no | 0 | `exp_b805662b` | `exp_a1917fa9` |
| T1 | 20261128 | 3 | C | yes | no | 0 | `exp_b805662b` | `exp_a1917fa9` |
| T1 | 20261129 | 2 | B | yes | no | 0 | `exp_296eb82c` | `exp_14f62bf0` |
| T1 | 20261129 | 2 | C | yes | no | 0 | `exp_296eb82c` | `exp_14f62bf0` |
| T2 | 20261118 | 5 | B | yes | no | 0 | `exp_29143192` | `exp_b805662b` |
| T2 | 20261118 | 5 | C | yes | yes | — | `—` | `—` |
| T2 | 20261120 | 5 | B | no | no | 2 | `exp_b805662b` | `exp_d7c5ea03` |
| T2 | 20261120 | 5 | C | no | no | 18 | `anomaly_9ac06e8c` | `anomaly_14a18614` |
| T2 | 20261121 | 5 | B | no | no | 10 | `dream_analogy_b8830751` | `dream_analogy_a9ca2e7b` |
| T2 | 20261121 | 5 | C | yes | no | 3 | `anomaly_2cb3d759` | `anomaly_a5dcb0c7` |
| T2 | 20261123 | 5 | B | yes | no | 0 | `exp_29143192` | `exp_a1917fa9` |
| T2 | 20261123 | 5 | C | yes | yes | — | `—` | `—` |
| T2 | 20261130 | 5 | B | yes | no | 0 | `exp_c9ab6eb3` | `exp_14f62bf0` |
| T2 | 20261130 | 5 | C | yes | yes | — | `—` | `—` |

**Did the reordering happen at the divergence cycle, or was it already there?** The capture holds the window for the cycle before the divergence as well. Where the two sides’ pools were identical in set *and* order at that earlier cycle, and identical in set but different in order at the divergence cycle, the reordering and the divergence are the same event.

| Task | Seed | Cycle | Arm | Previous cycle — same set / same order | This cycle — same set / same order | The reordering coincides with the divergence |
|---|---|---|---|---|---|---|
| T1 | 20261125 | 11 | B | no / no | no / no | no |
| T1 | 20261125 | 11 | C | no / no | no / no | no |
| T1 | 20261128 | 3 | B | yes / no | yes / no | no |
| T1 | 20261128 | 3 | C | yes / no | yes / no | no |
| T1 | 20261129 | 2 | B | yes / yes | yes / no | yes |
| T1 | 20261129 | 2 | C | yes / yes | yes / no | yes |
| T2 | 20261118 | 5 | B | yes / yes | yes / no | yes |
| T2 | 20261118 | 5 | C | yes / yes | yes / yes | no |
| T2 | 20261120 | 5 | B | no / no | no / no | no |
| T2 | 20261120 | 5 | C | no / no | no / no | no |
| T2 | 20261121 | 5 | B | yes / no | no / no | no |
| T2 | 20261121 | 5 | C | yes / yes | yes / no | yes |
| T2 | 20261123 | 5 | B | yes / yes | yes / no | yes |
| T2 | 20261123 | 5 | C | yes / yes | yes / yes | no |
| T2 | 20261130 | 5 | B | yes / yes | yes / no | yes |
| T2 | 20261130 | 5 | C | yes / yes | yes / yes | no |

**3 arm-C pairs show the pool identical in set *and* order, and the admitted stream differs anyway.** For T2 / 20261118, T2 / 20261123, T2 / 20261130 in arm C, the two sides’ pools at the divergence cycle are identical candidate-for-candidate and in the same sequence, and arm C’s admitted stream still differs at that cycle. For those, the divergence cannot be attributed to the pool at the divergence cycle at all: the same candidates, read back in the same order, were available, and the difference arose inside the cycle.

**Two orders, and this capture measures one of them.** The engine reads its window back with `ORDER BY time DESC` and no rowid tiebreak (`organica/memory.py:390`), so the pool arrives as a sequence and the capture measures that sequence. Inside the cycle, the candidate list is assembled from that sequence in an order that is *not* the sequence: the tags of each prior candidate are collected into a `set` (`organica/sleep.py:1201`) and the candidates of each tag into another (`organica/sleep.py:1223`, `distinct_ids = list(set(cid for cid, _ in refs))`). Set iteration order over strings follows the process’s hash seed, so two processes reading the *same* pool assemble it in *different* orders.

That is the mechanism the identical-pool pairs point at, and it is consistent with the whole table: the pool’s membership differs on some seeds, its read-back order differs on most, and where even the read-back order is identical the divergence is still there — which is what an order-sensitive assembly step inside the cycle predicts.

**What it does not establish.** That the order difference *caused* the admitted-stream difference, and it does not measure the order the ranking actually saw. The admitted stream is the engine’s ranking of the pool; this capture observes the pool and the admitted stream, and does not decompose the ranking between them, nor the assembly step that precedes it. The supported claim is the narrower one: **at the cycle where the populations part company, the pool differs in membership on some seeds and in read-back order on most, and on 3 seeds the pool is identical and the divergence is still there.**

## 5. What this does not establish

It names the candidate pool at the cycle where the two populations part company, what changed in it since the cycle before, and the order in which the engine read it back. It does not establish which candidate caused the divergence: the pool is the input to the decision, and the decision is the admitted stream, whose contents are recorded but whose internal ranking is not decomposed here. It does not re-score D0, and it does not change any verdict.

## Provenance

- Artifact: `docs/divergence_cycle_capture.json`.
- Instrument: `benchmarks/divergence_cycle_capture.py`.
- Membership reference: `docs/candidate_membership_audit.json` (sha256 `15bf5ffba2f77431f52344b558a7e7d72068a8fa5b12767953d63700cca23f23`).
- Observer version: 2.
- Capture command: `python benchmarks/divergence_cycle_capture.py --workers 4` — 16 worker runs, 0 cached.
- Re-render from the artifact: `python benchmarks/divergence_cycle_capture.py --render-only`.
- The capture’s own determinism control: `python benchmarks/divergence_cycle_capture.py --compare-parts <dir>` compares the parts on disk against another directory of parts, field by field, with the observer-version field set aside.
