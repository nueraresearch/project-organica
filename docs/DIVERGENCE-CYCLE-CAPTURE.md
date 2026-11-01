# Divergence-cycle capture — the pool just before the divergence and the transition into it

**Status.** Measured 2026-10-31; **cycle base corrected and re-measured 2026-11-01**. It is the instrument the candidate-membership audit named as the next one: the membership audit found *where* the two candidate populations diverge, and this names *which candidates* were in the pool at the divergence cycle and in the cycle before it, and what entered or left on the way in. The 2026-10-31 run read the cycle before the divergence and labelled it with the divergence cycle's number; §1 states the correction. It does not re-score D0 and it does not change any verdict.

## 1. Why a second capture was needed

The membership audit captured the engine’s 4,000-row sleep window, and reported honestly that it could not explain the divergence: the window is a snapshot of the read-back at the arm’s snapshot point, which is two or three cycles before the end of the run, while the divergences are at sleep cycles 2 to 11. The window shows the population *near the snapshot point*; it cannot show the pool *at the divergence*.

The 2026-10-31 run did not do that. The audit stores `first_cycle` as a **zero-based index**, and a window's index here is an engine cycle counted from one, so the capture read the cycle **before** the divergence and labelled it with the divergence cycle's own number. The 2026-11-01 re-measurement reads the divergence cycle and the cycle before it.

## 2. How the capture is addressed, and how that is proved

The sleep service reads its window once per cycle, and the harness’s arm loop adds exactly two reads outside the cycle loop — one after the acquisition phase and one after the revision phase. So the i-th window read of an arm is the i-th cycle of that arm.

That correspondence is not assumed. The engine stores one `sleep:meta` event per cycle carrying that cycle’s number, and the window is read newest-first, so **the newest cycle marker in the i-th window must carry cycle *i***. The capture refuses to report a window whose marker does not say so, and the addressability of every window used below is recorded in the artifact.

**16 of 16** captured window pairs are addressed by their own marker.

## 3. The pool at the divergence cycle, and the cycle before it

**Campaign side** is the run whose fingerprint equals the campaign’s; **current side** is the run at the pinned hash seed, which is what the use-path audit measured. Arm C is the arm the D0 verdict was scored on; arm B is shown alongside it because arm C reads arm B’s recorded temporal graphs.

| Task | Seed | Audit index | Cycle captured | Arm | Campaign pool | Current pool | Both | Campaign only | Current only | Same set | Same order |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | 20261125 | 11 | 12 | B | 271 | 268 | 256 | 15 | 12 | no | no |
| T1 | 20261125 | 11 | 12 | C | 238 | 235 | 223 | 15 | 12 | no | no |
| T1 | 20261128 | 3 | 4 | B | 84 | 84 | 81 | 3 | 3 | no | no |
| T1 | 20261128 | 3 | 4 | C | 84 | 84 | 81 | 3 | 3 | no | no |
| T1 | 20261129 | 2 | 3 | B | 101 | 95 | 95 | 6 | 0 | no | no |
| T1 | 20261129 | 2 | 3 | C | 101 | 95 | 95 | 6 | 0 | no | no |
| T2 | 20261118 | 5 | 6 | B | 48 | 49 | 46 | 2 | 3 | no | no |
| T2 | 20261118 | 5 | 6 | C | 10 | 11 | 8 | 2 | 3 | no | no |
| T2 | 20261120 | 5 | 6 | B | 98 | 98 | 91 | 7 | 7 | no | no |
| T2 | 20261120 | 5 | 6 | C | 36 | 34 | 33 | 3 | 1 | no | no |
| T2 | 20261121 | 5 | 6 | B | 82 | 82 | 79 | 3 | 3 | no | no |
| T2 | 20261121 | 5 | 6 | C | 24 | 25 | 23 | 1 | 2 | no | no |
| T2 | 20261123 | 5 | 6 | B | 42 | 41 | 41 | 1 | 0 | no | no |
| T2 | 20261123 | 5 | 6 | C | 18 | 17 | 17 | 1 | 0 | no | no |
| T2 | 20261130 | 5 | 6 | B | 69 | 69 | 64 | 5 | 5 | no | no |
| T2 | 20261130 | 5 | 6 | C | 38 | 34 | 33 | 5 | 1 | no | no |

### T1 / 20261125, cycle 12 (audit index 11), arm B

- **In the campaign’s pool and not ours (15):** `anomaly_ae98fe13`, `dream_cond_188d0d36`, `dream_cond_bbedbdd9`, `exp_6a2dbdd3`, `exp_810b7597`, `exp_f52c7b1e`, `hyp_abc3c91a`, `inv_2177d7b0`, `inv_69c5feca`, `inv_a7825392`, `loop_5be3da66`, `question_6eef169e`, `question_f88106c4`, `theory_6eef169e`, `theory_f88106c4`
- **In our pool and not the campaign’s (12):** `anomaly_02502914`, `anomaly_46973ab1`, `anomaly_fea6cc1b`, `dream_cond_0f32fe15`, `dream_cond_45ba4f3d`, `exp_2e3a7c5f`, `exp_80d6e0b7`, `inv_777a5a3f`, `inv_b85f57f1`, `pred_76eafd70`, `question_477196e4`, `theory_d73713a5`

**From cycle 11 into cycle 12, the divergence.** The campaign side gained 43 candidate(s) and lost 52; the current side gained 42 and lost 48.

- gained by the campaign side: `anomaly_65c93280`, `anomaly_715d4088`, `anomaly_7b6cccbe`, `anomaly_ebb4d391`, `dream_analogy_2996247c`, `dream_analogy_456a14f9`, `dream_cond_188d0d36`, `dream_cond_63603176`, `dream_mut_0d1b208d`, `dream_mut_73a2d262`, `exp_65f48707`, `exp_810b7597`, `exp_c33c72a0`, `exp_f52c7b1e`, `hyp_050c5ef4`, `hyp_0f32fe15`, `hyp_18e1d6f5`, `hyp_45ba4f3d`, `hyp_81149fad`, `hyp_aeff9bcd`, `hyp_b67853a9`, `inv_57770c98`, `inv_69c5feca`, `inv_90bc3495`, `inv_a7825392`, `loop_5be3da66`, `loop_974c6a02`, `phrase_5be3da66`, `pred_10a9fca1`, `pred_28bc53a8`, `pred_67fd326f`, `pred_c64358ce`, `pred_c696d32c`, `pred_ddb4ec6f`, `pred_df531f25`, `pred_e161befe`, `pred_f26fb19e`, `process_050c5ef4`, `process_81149fad`, `question_62b49344`, `question_6eef169e`, `theory_62b49344`, `theory_6eef169e`
- gained by the current side: `anomaly_46973ab1`, `anomaly_65c93280`, `anomaly_715d4088`, `anomaly_7b6cccbe`, `anomaly_ebb4d391`, `anomaly_fea6cc1b`, `dream_analogy_2996247c`, `dream_analogy_456a14f9`, `dream_cond_45ba4f3d`, `dream_cond_63603176`, `dream_mut_0d1b208d`, `dream_mut_73a2d262`, `exp_2e3a7c5f`, `exp_65f48707`, `exp_c33c72a0`, `hyp_050c5ef4`, `hyp_0f32fe15`, `hyp_18e1d6f5`, `hyp_45ba4f3d`, `hyp_81149fad`, `hyp_aeff9bcd`, `hyp_b67853a9`, `inv_57770c98`, `inv_90bc3495`, `inv_b85f57f1`, `loop_974c6a02`, `phrase_5be3da66`, `pred_10a9fca1`, `pred_28bc53a8`, `pred_67fd326f`, `pred_76eafd70`, `pred_c64358ce`, `pred_c696d32c`, `pred_ddb4ec6f`, `pred_df531f25`, `pred_e161befe`, `pred_f26fb19e`, `process_050c5ef4`, `process_81149fad`, `question_62b49344`, `theory_62b49344`, `theory_d73713a5`
- lost by the campaign side: `anomaly_02502914`, `anomaly_086ea9a1`, `anomaly_5d10a623`, `anomaly_875176b0`, `anomaly_ade88418`, `anomaly_bef44adf`, `anomaly_d6f7598f`, `anomaly_e3f06f4a`, `anomaly_f0114205`, `anomaly_f09f9863`, `dream_cond_5242671c`, `dream_cond_abc3c91a`, `dream_mut_7f43155c`, `dream_mut_aa7e1065`, `dream_mut_d3bef9c7`, `exp_47c4cb5e`, `exp_6d4ee01d`, `exp_80d6e0b7`, `exp_a7926761`, `exp_ce2d9695`, `hyp_050eeda2`, `hyp_1908f98b`, `hyp_31b9db0e`, `hyp_972d3173`, `hyp_9e19432e`, `hyp_d04fa6f7`, `hyp_e9822ccf`, `inv_055ad1c2`, `inv_425979b7`, `inv_777a5a3f`, `inv_863ba5d4`, `inv_b5abc76a`, `meta_1f543cef`, `process_18e1d6f5`, `process_1908f98b`, `process_23c7c1fa`, `process_31b9db0e`, `process_6eef169e`, `process_abc3c91a`, `question_27da00e9`, `question_477196e4`, `question_5f8f5cae`, `question_9f149b79`, `theory_5f8f5cae`, `theory_73dcc480`, `theory_9f149b79`, `workflow_18e1d6f5`, `workflow_1908f98b`, `workflow_23c7c1fa`, `workflow_31b9db0e`, `workflow_6eef169e`, `workflow_abc3c91a`
- lost by the current side: `anomaly_086ea9a1`, `anomaly_875176b0`, `anomaly_ade88418`, `anomaly_bef44adf`, `anomaly_c34c86c1`, `anomaly_d6f7598f`, `anomaly_f0114205`, `anomaly_f09f9863`, `dream_cond_5242671c`, `dream_cond_abc3c91a`, `dream_mut_7f43155c`, `dream_mut_aa7e1065`, `dream_mut_d3bef9c7`, `exp_47c4cb5e`, `exp_6d4ee01d`, `exp_a7926761`, `exp_ce2d9695`, `hyp_050eeda2`, `hyp_1908f98b`, `hyp_31b9db0e`, `hyp_972d3173`, `hyp_9e19432e`, `hyp_abc3c91a`, `hyp_d04fa6f7`, `hyp_e9822ccf`, `inv_055ad1c2`, `inv_425979b7`, `inv_863ba5d4`, `inv_b5abc76a`, `meta_1f543cef`, `process_18e1d6f5`, `process_1908f98b`, `process_23c7c1fa`, `process_31b9db0e`, `process_6eef169e`, `process_abc3c91a`, `question_27da00e9`, `question_5f8f5cae`, `question_9f149b79`, `theory_5f8f5cae`, `theory_73dcc480`, `theory_9f149b79`, `workflow_18e1d6f5`, `workflow_1908f98b`, `workflow_23c7c1fa`, `workflow_31b9db0e`, `workflow_6eef169e`, `workflow_abc3c91a`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 14 | 16 |
| dream | 15 | 15 |
| experiment | 10 | 9 |
| hypothesis | 40 | 39 |
| investigation | 10 | 9 |
| loop_candidate | 37 | 36 |
| meta_concept | 15 | 15 |
| phrase_candidate | 7 | 7 |
| prediction_candidate | 80 | 81 |
| process_candidate | 13 | 13 |
| question | 9 | 8 |
| theory | 10 | 9 |
| workflow_concept | 11 | 11 |

### T1 / 20261125, cycle 12 (audit index 11), arm C

- **In the campaign’s pool and not ours (15):** `anomaly_ae98fe13`, `dream_cond_188d0d36`, `dream_cond_bbedbdd9`, `exp_6a2dbdd3`, `exp_810b7597`, `exp_f52c7b1e`, `hyp_abc3c91a`, `inv_2177d7b0`, `inv_69c5feca`, `inv_a7825392`, `loop_5be3da66`, `question_6eef169e`, `question_f88106c4`, `theory_6eef169e`, `theory_f88106c4`
- **In our pool and not the campaign’s (12):** `anomaly_02502914`, `anomaly_46973ab1`, `anomaly_fea6cc1b`, `dream_cond_0f32fe15`, `dream_cond_45ba4f3d`, `exp_2e3a7c5f`, `exp_80d6e0b7`, `inv_777a5a3f`, `inv_b85f57f1`, `pred_76eafd70`, `question_477196e4`, `theory_d73713a5`

**From cycle 11 into cycle 12, the divergence.** The campaign side gained 33 candidate(s) and lost 55; the current side gained 32 and lost 52.

- gained by the campaign side: `anomaly_65c93280`, `anomaly_715d4088`, `anomaly_7b6cccbe`, `anomaly_ebb4d391`, `dream_analogy_2d3acaa8`, `dream_cond_188d0d36`, `dream_cond_63603176`, `dream_mut_0ea76f71`, `dream_mut_5dec4e89`, `exp_65f48707`, `exp_810b7597`, `exp_c33c72a0`, `exp_f52c7b1e`, `hyp_050c5ef4`, `hyp_0f32fe15`, `hyp_18e1d6f5`, `hyp_45ba4f3d`, `hyp_81149fad`, `hyp_aeff9bcd`, `hyp_b67853a9`, `inv_57770c98`, `inv_69c5feca`, `inv_90bc3495`, `inv_a7825392`, `loop_5be3da66`, `loop_974c6a02`, `phrase_5be3da66`, `process_050c5ef4`, `process_81149fad`, `question_62b49344`, `question_6eef169e`, `theory_62b49344`, `theory_6eef169e`
- gained by the current side: `anomaly_46973ab1`, `anomaly_65c93280`, `anomaly_715d4088`, `anomaly_7b6cccbe`, `anomaly_ebb4d391`, `anomaly_fea6cc1b`, `dream_analogy_2d3acaa8`, `dream_cond_45ba4f3d`, `dream_cond_63603176`, `dream_mut_0ea76f71`, `dream_mut_5dec4e89`, `exp_2e3a7c5f`, `exp_65f48707`, `exp_c33c72a0`, `hyp_050c5ef4`, `hyp_0f32fe15`, `hyp_18e1d6f5`, `hyp_45ba4f3d`, `hyp_81149fad`, `hyp_aeff9bcd`, `hyp_b67853a9`, `inv_57770c98`, `inv_90bc3495`, `inv_b85f57f1`, `loop_974c6a02`, `phrase_5be3da66`, `pred_76eafd70`, `process_050c5ef4`, `process_81149fad`, `question_62b49344`, `theory_62b49344`, `theory_d73713a5`
- lost by the campaign side: `anomaly_02502914`, `anomaly_086ea9a1`, `anomaly_5d10a623`, `anomaly_875176b0`, `anomaly_ade88418`, `anomaly_bef44adf`, `anomaly_d6f7598f`, `anomaly_e3f06f4a`, `anomaly_f0114205`, `anomaly_f09f9863`, `dream_cond_5242671c`, `dream_cond_abc3c91a`, `dream_cond_aeff9bcd`, `dream_mut_7f43155c`, `dream_mut_aa7e1065`, `dream_mut_d3bef9c7`, `exp_47c4cb5e`, `exp_695edb13`, `exp_6d4ee01d`, `exp_80d6e0b7`, `exp_a7926761`, `exp_ce2d9695`, `hyp_050eeda2`, `hyp_1908f98b`, `hyp_31b9db0e`, `hyp_972d3173`, `hyp_9e19432e`, `hyp_d04fa6f7`, `hyp_e9822ccf`, `inv_055ad1c2`, `inv_425979b7`, `inv_777a5a3f`, `inv_863ba5d4`, `inv_943684a9`, `inv_b5abc76a`, `meta_1f543cef`, `process_18e1d6f5`, `process_1908f98b`, `process_23c7c1fa`, `process_31b9db0e`, `process_6eef169e`, `process_abc3c91a`, `question_27da00e9`, `question_477196e4`, `question_5f8f5cae`, `question_9f149b79`, `theory_5f8f5cae`, `theory_73dcc480`, `theory_9f149b79`, `workflow_18e1d6f5`, `workflow_1908f98b`, `workflow_23c7c1fa`, `workflow_31b9db0e`, `workflow_6eef169e`, `workflow_abc3c91a`
- lost by the current side: `anomaly_086ea9a1`, `anomaly_875176b0`, `anomaly_ade88418`, `anomaly_bef44adf`, `anomaly_c34c86c1`, `anomaly_d6f7598f`, `anomaly_f0114205`, `anomaly_f09f9863`, `dream_cond_5242671c`, `dream_cond_abc3c91a`, `dream_cond_aeff9bcd`, `dream_mut_7f43155c`, `dream_mut_aa7e1065`, `dream_mut_d3bef9c7`, `exp_47c4cb5e`, `exp_695edb13`, `exp_6d4ee01d`, `exp_a7926761`, `exp_ce2d9695`, `hyp_050eeda2`, `hyp_1908f98b`, `hyp_31b9db0e`, `hyp_972d3173`, `hyp_9e19432e`, `hyp_abc3c91a`, `hyp_d04fa6f7`, `hyp_e9822ccf`, `inv_055ad1c2`, `inv_425979b7`, `inv_863ba5d4`, `inv_943684a9`, `inv_b5abc76a`, `meta_1f543cef`, `process_18e1d6f5`, `process_1908f98b`, `process_23c7c1fa`, `process_31b9db0e`, `process_6eef169e`, `process_abc3c91a`, `question_0cc6644f`, `question_27da00e9`, `question_5f8f5cae`, `question_9f149b79`, `theory_5f8f5cae`, `theory_73dcc480`, `theory_9f149b79`, `workflow_18e1d6f5`, `workflow_1908f98b`, `workflow_23c7c1fa`, `workflow_31b9db0e`, `workflow_6eef169e`, `workflow_abc3c91a`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 14 | 16 |
| dream | 14 | 14 |
| experiment | 10 | 9 |
| hypothesis | 40 | 39 |
| investigation | 10 | 9 |
| loop_candidate | 37 | 36 |
| meta_concept | 15 | 15 |
| phrase_candidate | 7 | 7 |
| prediction_candidate | 48 | 49 |
| process_candidate | 13 | 13 |
| question | 9 | 8 |
| theory | 10 | 9 |
| workflow_concept | 11 | 11 |

### T1 / 20261128, cycle 4 (audit index 3), arm B

- **In the campaign’s pool and not ours (3):** `exp_69fefc7c`, `inv_1efb3c2a`, `loop_d66d0d78`
- **In our pool and not the campaign’s (3):** `exp_b342b9ae`, `inv_201b5d69`, `loop_f98b9a8a`

**From cycle 3 into cycle 4, the divergence.** The campaign side gained 47 candidate(s) and lost 0; the current side gained 47 and lost 0.

- gained by the campaign side: `dream_analogy_fabff6cc`, `dream_cond_18e1d6f5`, `dream_cond_313a43d6`, `dream_cond_972d3173`, `dream_mut_760fc7e7`, `dream_mut_e71ad475`, `exp_036d5ff8`, `exp_0b49e797`, `exp_69fefc7c`, `exp_72ed1e29`, `exp_ab789ab9`, `hyp_417da26f`, `hyp_70f7c838`, `hyp_b38b643c`, `hyp_c1ff7ade`, `hyp_c8225c8d`, `hyp_d22148a4`, `hyp_fc1dfe44`, `inv_1efb3c2a`, `inv_23f27572`, `inv_4c3f9caf`, `inv_6683982e`, `inv_d358fa26`, `loop_18e1d6f5`, `loop_1908f98b`, `loop_2f69dab0`, `loop_313a43d6`, `loop_d66d0d78`, `loop_e8b925e0`, `meta_b62f3b3b`, `meta_e0592018`, `pred_050eeda2`, `pred_18e1d6f5`, `pred_313a43d6`, `pred_972d3173`, `process_417da26f`, `process_90cf00ae`, `process_fc1dfe44`, `question_1c53486b`, `question_9a93b25b`, `question_d81bba30`, `theory_1c53486b`, `theory_9a93b25b`, `theory_d81bba30`, `workflow_417da26f`, `workflow_9a93b25b`, `workflow_fc1dfe44`
- gained by the current side: `dream_analogy_fabff6cc`, `dream_cond_18e1d6f5`, `dream_cond_313a43d6`, `dream_cond_972d3173`, `dream_mut_760fc7e7`, `dream_mut_e71ad475`, `exp_036d5ff8`, `exp_0b49e797`, `exp_72ed1e29`, `exp_ab789ab9`, `exp_b342b9ae`, `hyp_417da26f`, `hyp_70f7c838`, `hyp_b38b643c`, `hyp_c1ff7ade`, `hyp_c8225c8d`, `hyp_d22148a4`, `hyp_fc1dfe44`, `inv_201b5d69`, `inv_23f27572`, `inv_4c3f9caf`, `inv_6683982e`, `inv_d358fa26`, `loop_18e1d6f5`, `loop_1908f98b`, `loop_2f69dab0`, `loop_313a43d6`, `loop_e8b925e0`, `loop_f98b9a8a`, `meta_b62f3b3b`, `meta_e0592018`, `pred_050eeda2`, `pred_18e1d6f5`, `pred_313a43d6`, `pred_972d3173`, `process_417da26f`, `process_90cf00ae`, `process_fc1dfe44`, `question_1c53486b`, `question_9a93b25b`, `question_d81bba30`, `theory_1c53486b`, `theory_9a93b25b`, `theory_d81bba30`, `workflow_417da26f`, `workflow_9a93b25b`, `workflow_fc1dfe44`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 5 | 5 |
| dream | 9 | 9 |
| experiment | 8 | 8 |
| hypothesis | 9 | 9 |
| investigation | 8 | 8 |
| loop_candidate | 10 | 10 |
| meta_concept | 4 | 4 |
| phrase_candidate | 3 | 3 |
| prediction_candidate | 14 | 14 |
| process_candidate | 4 | 4 |
| question | 3 | 3 |
| theory | 3 | 3 |
| workflow_concept | 4 | 4 |

### T1 / 20261128, cycle 4 (audit index 3), arm C

- **In the campaign’s pool and not ours (3):** `exp_69fefc7c`, `inv_1efb3c2a`, `loop_d66d0d78`
- **In our pool and not the campaign’s (3):** `exp_b342b9ae`, `inv_201b5d69`, `loop_f98b9a8a`

**From cycle 3 into cycle 4, the divergence.** The campaign side gained 47 candidate(s) and lost 0; the current side gained 47 and lost 0.

- gained by the campaign side: `dream_analogy_fabff6cc`, `dream_cond_18e1d6f5`, `dream_cond_313a43d6`, `dream_cond_972d3173`, `dream_mut_760fc7e7`, `dream_mut_e71ad475`, `exp_036d5ff8`, `exp_0b49e797`, `exp_69fefc7c`, `exp_72ed1e29`, `exp_ab789ab9`, `hyp_417da26f`, `hyp_70f7c838`, `hyp_b38b643c`, `hyp_c1ff7ade`, `hyp_c8225c8d`, `hyp_d22148a4`, `hyp_fc1dfe44`, `inv_1efb3c2a`, `inv_23f27572`, `inv_4c3f9caf`, `inv_6683982e`, `inv_d358fa26`, `loop_18e1d6f5`, `loop_1908f98b`, `loop_2f69dab0`, `loop_313a43d6`, `loop_d66d0d78`, `loop_e8b925e0`, `meta_b62f3b3b`, `meta_e0592018`, `pred_050eeda2`, `pred_18e1d6f5`, `pred_313a43d6`, `pred_972d3173`, `process_417da26f`, `process_90cf00ae`, `process_fc1dfe44`, `question_1c53486b`, `question_9a93b25b`, `question_d81bba30`, `theory_1c53486b`, `theory_9a93b25b`, `theory_d81bba30`, `workflow_417da26f`, `workflow_9a93b25b`, `workflow_fc1dfe44`
- gained by the current side: `dream_analogy_fabff6cc`, `dream_cond_18e1d6f5`, `dream_cond_313a43d6`, `dream_cond_972d3173`, `dream_mut_760fc7e7`, `dream_mut_e71ad475`, `exp_036d5ff8`, `exp_0b49e797`, `exp_72ed1e29`, `exp_ab789ab9`, `exp_b342b9ae`, `hyp_417da26f`, `hyp_70f7c838`, `hyp_b38b643c`, `hyp_c1ff7ade`, `hyp_c8225c8d`, `hyp_d22148a4`, `hyp_fc1dfe44`, `inv_201b5d69`, `inv_23f27572`, `inv_4c3f9caf`, `inv_6683982e`, `inv_d358fa26`, `loop_18e1d6f5`, `loop_1908f98b`, `loop_2f69dab0`, `loop_313a43d6`, `loop_e8b925e0`, `loop_f98b9a8a`, `meta_b62f3b3b`, `meta_e0592018`, `pred_050eeda2`, `pred_18e1d6f5`, `pred_313a43d6`, `pred_972d3173`, `process_417da26f`, `process_90cf00ae`, `process_fc1dfe44`, `question_1c53486b`, `question_9a93b25b`, `question_d81bba30`, `theory_1c53486b`, `theory_9a93b25b`, `theory_d81bba30`, `workflow_417da26f`, `workflow_9a93b25b`, `workflow_fc1dfe44`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 5 | 5 |
| dream | 9 | 9 |
| experiment | 8 | 8 |
| hypothesis | 9 | 9 |
| investigation | 8 | 8 |
| loop_candidate | 10 | 10 |
| meta_concept | 4 | 4 |
| phrase_candidate | 3 | 3 |
| prediction_candidate | 14 | 14 |
| process_candidate | 4 | 4 |
| question | 3 | 3 |
| theory | 3 | 3 |
| workflow_concept | 4 | 4 |

### T1 / 20261129, cycle 3 (audit index 2), arm B

- **In the campaign’s pool and not ours (6):** `loop_41f383df`, `loop_abc3c91a`, `loop_b13b5e52`, `loop_dc1ceb15`, `pred_d04fa6f7`, `pred_e9822ccf`
- In our pool and not the campaign’s: **none**.

**From cycle 2 into cycle 3, the divergence.** The campaign side gained 62 candidate(s) and lost 0; the current side gained 56 and lost 0.

- gained by the campaign side: `anomaly_aa6b1046`, `anomaly_e5a539be`, `anomaly_fb6ccd1e`, `dream_analogy_2996247c`, `dream_analogy_a9ca2e7b`, `dream_analogy_fabff6cc`, `dream_mut_1a1cab04`, `dream_mut_6c81b628`, `exp_08858048`, `exp_481eaeea`, `exp_71deae9f`, `exp_8c58ab2d`, `exp_e241856f`, `hyp_1908f98b`, `hyp_21019ffd`, `hyp_313a43d6`, `hyp_417da26f`, `hyp_5242671c`, `hyp_972d3173`, `hyp_9d441b50`, `hyp_c1ff7ade`, `hyp_c8225c8d`, `hyp_d22148a4`, `hyp_ecfe4694`, `inv_0bd24d28`, `inv_56fe9728`, `inv_7c7d3b4d`, `inv_9c9b4b8b`, `inv_e534a813`, `loop_27da00e9`, `loop_31b9db0e`, `loop_41f383df`, `loop_abc3c91a`, `loop_b13b5e52`, `loop_dc1ceb15`, `loop_ed9d7ae1`, `meta_2655399a`, `meta_b62f3b3b`, `meta_e0592018`, `phrase_49ead2b1`, `pred_31b9db0e`, `pred_7498423f`, `pred_a04f50f2`, `pred_abc3c91a`, `pred_cf11d4d4`, `pred_d04fa6f7`, `pred_e9822ccf`, `pred_ed9d7ae1`, `process_1908f98b`, `process_313a43d6`, `process_417da26f`, `process_f0e2067b`, `question_b58e2626`, `question_d0a0293b`, `question_d9230abf`, `theory_b58e2626`, `theory_d0a0293b`, `theory_d9230abf`, `workflow_1908f98b`, `workflow_313a43d6`, `workflow_417da26f`, `workflow_b58e2626`
- gained by the current side: `anomaly_aa6b1046`, `anomaly_e5a539be`, `anomaly_fb6ccd1e`, `dream_analogy_2996247c`, `dream_analogy_a9ca2e7b`, `dream_analogy_fabff6cc`, `dream_mut_1a1cab04`, `dream_mut_6c81b628`, `exp_08858048`, `exp_481eaeea`, `exp_71deae9f`, `exp_8c58ab2d`, `exp_e241856f`, `hyp_1908f98b`, `hyp_21019ffd`, `hyp_313a43d6`, `hyp_417da26f`, `hyp_5242671c`, `hyp_972d3173`, `hyp_9d441b50`, `hyp_c1ff7ade`, `hyp_c8225c8d`, `hyp_d22148a4`, `hyp_ecfe4694`, `inv_0bd24d28`, `inv_56fe9728`, `inv_7c7d3b4d`, `inv_9c9b4b8b`, `inv_e534a813`, `loop_27da00e9`, `loop_31b9db0e`, `loop_ed9d7ae1`, `meta_2655399a`, `meta_b62f3b3b`, `meta_e0592018`, `phrase_49ead2b1`, `pred_31b9db0e`, `pred_7498423f`, `pred_a04f50f2`, `pred_abc3c91a`, `pred_cf11d4d4`, `pred_ed9d7ae1`, `process_1908f98b`, `process_313a43d6`, `process_417da26f`, `process_f0e2067b`, `question_b58e2626`, `question_d0a0293b`, `question_d9230abf`, `theory_b58e2626`, `theory_d0a0293b`, `theory_d9230abf`, `workflow_1908f98b`, `workflow_313a43d6`, `workflow_417da26f`, `workflow_b58e2626`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 9 | 9 |
| dream | 9 | 9 |
| experiment | 9 | 9 |
| hypothesis | 13 | 13 |
| investigation | 9 | 9 |
| loop_candidate | 12 | 8 |
| meta_concept | 5 | 5 |
| phrase_candidate | 2 | 2 |
| prediction_candidate | 17 | 15 |
| process_candidate | 5 | 5 |
| question | 3 | 3 |
| theory | 3 | 3 |
| workflow_concept | 5 | 5 |

### T1 / 20261129, cycle 3 (audit index 2), arm C

- **In the campaign’s pool and not ours (6):** `loop_41f383df`, `loop_abc3c91a`, `loop_b13b5e52`, `loop_dc1ceb15`, `pred_d04fa6f7`, `pred_e9822ccf`
- In our pool and not the campaign’s: **none**.

**From cycle 2 into cycle 3, the divergence.** The campaign side gained 62 candidate(s) and lost 0; the current side gained 56 and lost 0.

- gained by the campaign side: `anomaly_aa6b1046`, `anomaly_e5a539be`, `anomaly_fb6ccd1e`, `dream_analogy_2996247c`, `dream_analogy_a9ca2e7b`, `dream_analogy_fabff6cc`, `dream_mut_1a1cab04`, `dream_mut_6c81b628`, `exp_08858048`, `exp_481eaeea`, `exp_71deae9f`, `exp_8c58ab2d`, `exp_e241856f`, `hyp_1908f98b`, `hyp_21019ffd`, `hyp_313a43d6`, `hyp_417da26f`, `hyp_5242671c`, `hyp_972d3173`, `hyp_9d441b50`, `hyp_c1ff7ade`, `hyp_c8225c8d`, `hyp_d22148a4`, `hyp_ecfe4694`, `inv_0bd24d28`, `inv_56fe9728`, `inv_7c7d3b4d`, `inv_9c9b4b8b`, `inv_e534a813`, `loop_27da00e9`, `loop_31b9db0e`, `loop_41f383df`, `loop_abc3c91a`, `loop_b13b5e52`, `loop_dc1ceb15`, `loop_ed9d7ae1`, `meta_2655399a`, `meta_b62f3b3b`, `meta_e0592018`, `phrase_49ead2b1`, `pred_31b9db0e`, `pred_7498423f`, `pred_a04f50f2`, `pred_abc3c91a`, `pred_cf11d4d4`, `pred_d04fa6f7`, `pred_e9822ccf`, `pred_ed9d7ae1`, `process_1908f98b`, `process_313a43d6`, `process_417da26f`, `process_f0e2067b`, `question_b58e2626`, `question_d0a0293b`, `question_d9230abf`, `theory_b58e2626`, `theory_d0a0293b`, `theory_d9230abf`, `workflow_1908f98b`, `workflow_313a43d6`, `workflow_417da26f`, `workflow_b58e2626`
- gained by the current side: `anomaly_aa6b1046`, `anomaly_e5a539be`, `anomaly_fb6ccd1e`, `dream_analogy_2996247c`, `dream_analogy_a9ca2e7b`, `dream_analogy_fabff6cc`, `dream_mut_1a1cab04`, `dream_mut_6c81b628`, `exp_08858048`, `exp_481eaeea`, `exp_71deae9f`, `exp_8c58ab2d`, `exp_e241856f`, `hyp_1908f98b`, `hyp_21019ffd`, `hyp_313a43d6`, `hyp_417da26f`, `hyp_5242671c`, `hyp_972d3173`, `hyp_9d441b50`, `hyp_c1ff7ade`, `hyp_c8225c8d`, `hyp_d22148a4`, `hyp_ecfe4694`, `inv_0bd24d28`, `inv_56fe9728`, `inv_7c7d3b4d`, `inv_9c9b4b8b`, `inv_e534a813`, `loop_27da00e9`, `loop_31b9db0e`, `loop_ed9d7ae1`, `meta_2655399a`, `meta_b62f3b3b`, `meta_e0592018`, `phrase_49ead2b1`, `pred_31b9db0e`, `pred_7498423f`, `pred_a04f50f2`, `pred_abc3c91a`, `pred_cf11d4d4`, `pred_ed9d7ae1`, `process_1908f98b`, `process_313a43d6`, `process_417da26f`, `process_f0e2067b`, `question_b58e2626`, `question_d0a0293b`, `question_d9230abf`, `theory_b58e2626`, `theory_d0a0293b`, `theory_d9230abf`, `workflow_1908f98b`, `workflow_313a43d6`, `workflow_417da26f`, `workflow_b58e2626`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 9 | 9 |
| dream | 9 | 9 |
| experiment | 9 | 9 |
| hypothesis | 13 | 13 |
| investigation | 9 | 9 |
| loop_candidate | 12 | 8 |
| meta_concept | 5 | 5 |
| phrase_candidate | 2 | 2 |
| prediction_candidate | 17 | 15 |
| process_candidate | 5 | 5 |
| question | 3 | 3 |
| theory | 3 | 3 |
| workflow_concept | 5 | 5 |

### T2 / 20261118, cycle 6 (audit index 5), arm B

- **In the campaign’s pool and not ours (2):** `anomaly_29b7be02`, `anomaly_842c5bcc`
- **In our pool and not the campaign’s (3):** `anomaly_1d754f3e`, `anomaly_2267c895`, `anomaly_f561a8e9`

**From cycle 5 into cycle 6, the divergence.** The campaign side gained 20 candidate(s) and lost 0; the current side gained 21 and lost 0.

- gained by the campaign side: `anomaly_29b7be02`, `anomaly_842c5bcc`, `dream_mut_70e14748`, `dream_mut_f06ec067`, `exp_107d054c`, `exp_e128d375`, `hyp_120eb70a`, `hyp_2ff50859`, `hyp_70f7c838`, `hyp_e6f8a3e6`, `inv_c53ffe1f`, `inv_e2d7bf47`, `meta_1f543cef`, `meta_efd764d8`, `pred_1908f98b`, `pred_331be2d4`, `pred_d22148a4`, `pred_dc361b05`, `process_e6f8a3e6`, `workflow_e6f8a3e6`
- gained by the current side: `anomaly_1d754f3e`, `anomaly_2267c895`, `anomaly_f561a8e9`, `dream_mut_70e14748`, `dream_mut_f06ec067`, `exp_107d054c`, `exp_e128d375`, `hyp_120eb70a`, `hyp_2ff50859`, `hyp_70f7c838`, `hyp_e6f8a3e6`, `inv_c53ffe1f`, `inv_e2d7bf47`, `meta_1f543cef`, `meta_efd764d8`, `pred_1908f98b`, `pred_331be2d4`, `pred_d22148a4`, `pred_dc361b05`, `process_e6f8a3e6`, `workflow_e6f8a3e6`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 6 | 7 |
| dream | 5 | 5 |
| experiment | 5 | 5 |
| hypothesis | 6 | 6 |
| investigation | 5 | 5 |
| loop_candidate | 2 | 2 |
| meta_concept | 4 | 4 |
| prediction_candidate | 11 | 11 |
| process_candidate | 2 | 2 |
| workflow_concept | 2 | 2 |

### T2 / 20261118, cycle 6 (audit index 5), arm C

- **In the campaign’s pool and not ours (2):** `anomaly_29b7be02`, `anomaly_842c5bcc`
- **In our pool and not the campaign’s (3):** `anomaly_1d754f3e`, `anomaly_2267c895`, `anomaly_f561a8e9`

**From cycle 5 into cycle 6, the divergence.** The campaign side gained 2 candidate(s) and lost 0; the current side gained 3 and lost 0.

- gained by the campaign side: `anomaly_29b7be02`, `anomaly_842c5bcc`
- gained by the current side: `anomaly_1d754f3e`, `anomaly_2267c895`, `anomaly_f561a8e9`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 6 | 7 |
| loop_candidate | 2 | 2 |
| prediction_candidate | 2 | 2 |

### T2 / 20261120, cycle 6 (audit index 5), arm B

- **In the campaign’s pool and not ours (7):** `anomaly_92221878`, `anomaly_9ac06e8c`, `exp_1b0b3869`, `inv_81f1ef91`, `loop_a816b62b`, `pred_4dc93d10`, `pred_f419a820`
- **In our pool and not the campaign’s (7):** `dream_analogy_7fd9b8ba`, `dream_analogy_ae902b2a`, `exp_4b8bb67f`, `exp_d7c5ea03`, `inv_494e629a`, `inv_85f71f22`, `pred_0f32fe15`

**From cycle 5 into cycle 6, the divergence.** The campaign side gained 39 candidate(s) and lost 0; the current side gained 37 and lost 0.

- gained by the campaign side: `anomaly_92221878`, `dream_analogy_e826e850`, `dream_mut_764cfdcd`, `dream_mut_f7c795e6`, `exp_a4b1ea14`, `exp_d2533d09`, `exp_dfd71827`, `hyp_18e1d6f5`, `hyp_57b28f60`, `hyp_70f7c838`, `inv_1d3f8bfa`, `inv_33e9ad17`, `inv_68605975`, `loop_25ccf231`, `loop_2968df09`, `loop_a816b62b`, `meta_b62f3b3b`, `meta_fd8ed7f1`, `pred_11ef7647`, `pred_1acba7c9`, `pred_230ab6eb`, `pred_2968df09`, `pred_5242671c`, `pred_7bc3a33b`, `pred_7bded4f6`, `pred_ab29f7d1`, `pred_ae531a4c`, `pred_bbedbdd9`, `pred_c27a66c7`, `pred_d7623706`, `pred_e36e8e35`, `pred_e40bdd72`, `pred_f419a820`, `process_18e1d6f5`, `process_57b28f60`, `question_8a744ff6`, `theory_8a744ff6`, `workflow_18e1d6f5`, `workflow_57b28f60`
- gained by the current side: `dream_analogy_e826e850`, `dream_mut_764cfdcd`, `dream_mut_f7c795e6`, `exp_a4b1ea14`, `exp_d2533d09`, `exp_dfd71827`, `hyp_18e1d6f5`, `hyp_57b28f60`, `hyp_70f7c838`, `inv_1d3f8bfa`, `inv_33e9ad17`, `inv_68605975`, `loop_25ccf231`, `loop_2968df09`, `meta_b62f3b3b`, `meta_fd8ed7f1`, `pred_0f32fe15`, `pred_11ef7647`, `pred_1acba7c9`, `pred_230ab6eb`, `pred_2968df09`, `pred_5242671c`, `pred_7bc3a33b`, `pred_7bded4f6`, `pred_ab29f7d1`, `pred_ae531a4c`, `pred_bbedbdd9`, `pred_c27a66c7`, `pred_d7623706`, `pred_e36e8e35`, `pred_e40bdd72`, `process_18e1d6f5`, `process_57b28f60`, `question_8a744ff6`, `theory_8a744ff6`, `workflow_18e1d6f5`, `workflow_57b28f60`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 19 | 17 |
| dream | 10 | 12 |
| experiment | 10 | 11 |
| hypothesis | 7 | 7 |
| investigation | 10 | 11 |
| loop_candidate | 6 | 5 |
| meta_concept | 4 | 4 |
| phrase_candidate | 1 | 1 |
| prediction_candidate | 23 | 22 |
| process_candidate | 3 | 3 |
| question | 1 | 1 |
| theory | 1 | 1 |
| workflow_concept | 3 | 3 |

### T2 / 20261120, cycle 6 (audit index 5), arm C

- **In the campaign’s pool and not ours (3):** `anomaly_92221878`, `anomaly_9ac06e8c`, `loop_a816b62b`
- **In our pool and not the campaign’s (1):** `pred_0f32fe15`

**From cycle 5 into cycle 6, the divergence.** The campaign side gained 13 candidate(s) and lost 0; the current side gained 12 and lost 0.

- gained by the campaign side: `anomaly_92221878`, `dream_analogy_dd9f100a`, `dream_analogy_fabff6cc`, `exp_c9ab6eb3`, `exp_fa481f50`, `inv_1320ba16`, `inv_65fa330c`, `loop_25ccf231`, `loop_2968df09`, `loop_a816b62b`, `meta_fd8ed7f1`, `pred_5242671c`, `pred_ab29f7d1`
- gained by the current side: `dream_analogy_dd9f100a`, `dream_analogy_fabff6cc`, `exp_c9ab6eb3`, `exp_fa481f50`, `inv_1320ba16`, `inv_65fa330c`, `loop_25ccf231`, `loop_2968df09`, `meta_fd8ed7f1`, `pred_0f32fe15`, `pred_5242671c`, `pred_ab29f7d1`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 19 | 17 |
| dream | 2 | 2 |
| experiment | 2 | 2 |
| investigation | 2 | 2 |
| loop_candidate | 6 | 5 |
| meta_concept | 1 | 1 |
| phrase_candidate | 1 | 1 |
| prediction_candidate | 3 | 4 |

### T2 / 20261121, cycle 6 (audit index 5), arm B

- **In the campaign’s pool and not ours (3):** `anomaly_a0072b14`, `dream_analogy_a6f80540`, `dream_analogy_b8830751`
- **In our pool and not the campaign’s (3):** `anomaly_c8edf4ca`, `dream_analogy_b38b643c`, `pred_3c1f4563`

**From cycle 5 into cycle 6, the divergence.** The campaign side gained 20 candidate(s) and lost 0; the current side gained 21 and lost 0.

- gained by the campaign side: `anomaly_1a1b1338`, `anomaly_8352ad0d`, `anomaly_8c8e09e6`, `anomaly_9db5184e`, `anomaly_a0072b14`, `dream_analogy_a6f80540`, `dream_mut_8f35869e`, `exp_2fb697de`, `hyp_642bc75f`, `hyp_70575cbc`, `hyp_a5f498cc`, `inv_df5c59a8`, `loop_dc361b05`, `meta_b1601f69`, `meta_fa659831`, `pred_4d9c1cf6`, `pred_c7d16b2f`, `pred_dc361b05`, `process_a5f498cc`, `workflow_a5f498cc`
- gained by the current side: `anomaly_1a1b1338`, `anomaly_8352ad0d`, `anomaly_8c8e09e6`, `anomaly_9db5184e`, `anomaly_c8edf4ca`, `dream_analogy_b38b643c`, `dream_mut_8f35869e`, `exp_2fb697de`, `hyp_642bc75f`, `hyp_70575cbc`, `hyp_a5f498cc`, `inv_df5c59a8`, `loop_dc361b05`, `meta_b1601f69`, `meta_fa659831`, `pred_3c1f4563`, `pred_4d9c1cf6`, `pred_c7d16b2f`, `pred_dc361b05`, `process_a5f498cc`, `workflow_a5f498cc`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 19 | 19 |
| dream | 9 | 8 |
| experiment | 8 | 8 |
| hypothesis | 9 | 9 |
| investigation | 8 | 8 |
| loop_candidate | 4 | 4 |
| meta_concept | 5 | 5 |
| prediction_candidate | 12 | 13 |
| process_candidate | 3 | 3 |
| question | 1 | 1 |
| theory | 1 | 1 |
| workflow_concept | 3 | 3 |

### T2 / 20261121, cycle 6 (audit index 5), arm C

- **In the campaign’s pool and not ours (1):** `anomaly_a0072b14`
- **In our pool and not the campaign’s (2):** `anomaly_c8edf4ca`, `pred_3c1f4563`

**From cycle 5 into cycle 6, the divergence.** The campaign side gained 6 candidate(s) and lost 0; the current side gained 7 and lost 0.

- gained by the campaign side: `anomaly_1a1b1338`, `anomaly_8352ad0d`, `anomaly_8c8e09e6`, `anomaly_9db5184e`, `anomaly_a0072b14`, `loop_dc361b05`
- gained by the current side: `anomaly_1a1b1338`, `anomaly_8352ad0d`, `anomaly_8c8e09e6`, `anomaly_9db5184e`, `anomaly_c8edf4ca`, `loop_dc361b05`, `pred_3c1f4563`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 19 | 19 |
| loop_candidate | 4 | 4 |
| prediction_candidate | 1 | 2 |

### T2 / 20261123, cycle 6 (audit index 5), arm B

- **In the campaign’s pool and not ours (1):** `pred_bc95dc38`
- In our pool and not the campaign’s: **none**.

**From cycle 5 into cycle 6, the divergence.** The campaign side gained 19 candidate(s) and lost 0; the current side gained 18 and lost 0.

- gained by the campaign side: `anomaly_21df6694`, `anomaly_3b1e873d`, `anomaly_41012317`, `anomaly_677c03f0`, `anomaly_7ad942e0`, `anomaly_9719b7a0`, `anomaly_9acd947b`, `anomaly_e6dced8c`, `anomaly_f5244467`, `anomaly_fe1ef7a5`, `hyp_2ff50859`, `hyp_c1ff7ade`, `loop_40d1fa1e`, `loop_5e4af209`, `pred_40d1fa1e`, `pred_5e4af209`, `pred_974c6a02`, `pred_bc95dc38`, `pred_d98266c8`
- gained by the current side: `anomaly_21df6694`, `anomaly_3b1e873d`, `anomaly_41012317`, `anomaly_677c03f0`, `anomaly_7ad942e0`, `anomaly_9719b7a0`, `anomaly_9acd947b`, `anomaly_e6dced8c`, `anomaly_f5244467`, `anomaly_fe1ef7a5`, `hyp_2ff50859`, `hyp_c1ff7ade`, `loop_40d1fa1e`, `loop_5e4af209`, `pred_40d1fa1e`, `pred_5e4af209`, `pred_974c6a02`, `pred_d98266c8`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 13 | 13 |
| dream | 3 | 3 |
| experiment | 3 | 3 |
| hypothesis | 3 | 3 |
| investigation | 3 | 3 |
| loop_candidate | 3 | 3 |
| meta_concept | 2 | 2 |
| prediction_candidate | 10 | 9 |
| process_candidate | 1 | 1 |
| workflow_concept | 1 | 1 |

### T2 / 20261123, cycle 6 (audit index 5), arm C

- **In the campaign’s pool and not ours (1):** `pred_bc95dc38`
- In our pool and not the campaign’s: **none**.

**From cycle 5 into cycle 6, the divergence.** The campaign side gained 14 candidate(s) and lost 0; the current side gained 13 and lost 0.

- gained by the campaign side: `anomaly_21df6694`, `anomaly_3b1e873d`, `anomaly_41012317`, `anomaly_677c03f0`, `anomaly_7ad942e0`, `anomaly_9719b7a0`, `anomaly_9acd947b`, `anomaly_e6dced8c`, `anomaly_f5244467`, `anomaly_fe1ef7a5`, `loop_40d1fa1e`, `loop_5e4af209`, `pred_974c6a02`, `pred_bc95dc38`
- gained by the current side: `anomaly_21df6694`, `anomaly_3b1e873d`, `anomaly_41012317`, `anomaly_677c03f0`, `anomaly_7ad942e0`, `anomaly_9719b7a0`, `anomaly_9acd947b`, `anomaly_e6dced8c`, `anomaly_f5244467`, `anomaly_fe1ef7a5`, `loop_40d1fa1e`, `loop_5e4af209`, `pred_974c6a02`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 13 | 13 |
| loop_candidate | 3 | 3 |
| prediction_candidate | 2 | 1 |

### T2 / 20261130, cycle 6 (audit index 5), arm B

- **In the campaign’s pool and not ours (5):** `dream_mut_64b4d86f`, `exp_85461809`, `inv_f01a0351`, `loop_a72ccfd6`, `pred_c7846f44`
- **In our pool and not the campaign’s (5):** `anomaly_bd4667f1`, `dream_analogy_1082cbdc`, `dream_mut_36a0c98a`, `exp_f47b21f5`, `inv_beeae18e`

**From cycle 5 into cycle 6, the divergence.** The campaign side gained 32 candidate(s) and lost 0; the current side gained 32 and lost 0.

- gained by the campaign side: `anomaly_98de25a9`, `anomaly_9d31c463`, `anomaly_a8af7322`, `anomaly_beb97bfb`, `anomaly_cf7c2929`, `dream_analogy_68b6162d`, `dream_mut_64b4d86f`, `dream_mut_859d957b`, `exp_85461809`, `exp_9cdfc6aa`, `hyp_21019ffd`, `hyp_5fa8f2d2`, `hyp_c8225c8d`, `hyp_dc7da818`, `inv_7f10e8f8`, `inv_f01a0351`, `loop_78029800`, `loop_93632860`, `loop_a72ccfd6`, `loop_d3d58048`, `meta_49ead2b1`, `meta_da454b02`, `meta_efd764d8`, `pred_2dcbe185`, `pred_a240a7be`, `pred_a32a9909`, `pred_a72ccfd6`, `pred_c7846f44`, `pred_d3d58048`, `pred_e5c75b28`, `process_63ac32e2`, `workflow_63ac32e2`
- gained by the current side: `anomaly_98de25a9`, `anomaly_9d31c463`, `anomaly_a8af7322`, `anomaly_bd4667f1`, `anomaly_beb97bfb`, `anomaly_cf7c2929`, `dream_analogy_1082cbdc`, `dream_analogy_68b6162d`, `dream_mut_36a0c98a`, `dream_mut_859d957b`, `exp_9cdfc6aa`, `exp_f47b21f5`, `hyp_21019ffd`, `hyp_5fa8f2d2`, `hyp_c8225c8d`, `hyp_dc7da818`, `inv_7f10e8f8`, `inv_beeae18e`, `loop_78029800`, `loop_93632860`, `loop_d3d58048`, `meta_49ead2b1`, `meta_da454b02`, `meta_efd764d8`, `pred_2dcbe185`, `pred_a240a7be`, `pred_a32a9909`, `pred_a72ccfd6`, `pred_d3d58048`, `pred_e5c75b28`, `process_63ac32e2`, `workflow_63ac32e2`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 9 | 10 |
| dream | 8 | 9 |
| experiment | 7 | 7 |
| hypothesis | 6 | 6 |
| investigation | 7 | 7 |
| loop_candidate | 6 | 5 |
| meta_concept | 5 | 5 |
| phrase_candidate | 1 | 1 |
| prediction_candidate | 16 | 15 |
| process_candidate | 2 | 2 |
| workflow_concept | 2 | 2 |

### T2 / 20261130, cycle 6 (audit index 5), arm C

- **In the campaign’s pool and not ours (5):** `dream_analogy_6399c069`, `exp_d31ecf56`, `inv_0a1a36b6`, `loop_a72ccfd6`, `pred_c7846f44`
- **In our pool and not the campaign’s (1):** `anomaly_bd4667f1`

**From cycle 5 into cycle 6, the divergence.** The campaign side gained 28 candidate(s) and lost 0; the current side gained 24 and lost 0.

- gained by the campaign side: `anomaly_98de25a9`, `anomaly_9d31c463`, `anomaly_a8af7322`, `anomaly_beb97bfb`, `anomaly_cf7c2929`, `dream_analogy_1082cbdc`, `dream_analogy_36e8eb9f`, `dream_analogy_6399c069`, `dream_analogy_68b6162d`, `dream_analogy_8b383d73`, `exp_14f62bf0`, `exp_2c10c6c8`, `exp_2ebafecf`, `exp_d31ecf56`, `exp_ed2c60fa`, `inv_0a1a36b6`, `inv_6111b8d8`, `inv_93a919ca`, `inv_b28ec89c`, `inv_c2cd4e42`, `loop_78029800`, `loop_93632860`, `loop_a72ccfd6`, `loop_d3d58048`, `meta_49ead2b1`, `meta_e0592018`, `pred_a72ccfd6`, `pred_c7846f44`
- gained by the current side: `anomaly_98de25a9`, `anomaly_9d31c463`, `anomaly_a8af7322`, `anomaly_bd4667f1`, `anomaly_beb97bfb`, `anomaly_cf7c2929`, `dream_analogy_1082cbdc`, `dream_analogy_36e8eb9f`, `dream_analogy_68b6162d`, `dream_analogy_8b383d73`, `exp_14f62bf0`, `exp_2c10c6c8`, `exp_2ebafecf`, `exp_ed2c60fa`, `inv_6111b8d8`, `inv_93a919ca`, `inv_b28ec89c`, `inv_c2cd4e42`, `loop_78029800`, `loop_93632860`, `loop_d3d58048`, `meta_49ead2b1`, `meta_e0592018`, `pred_a72ccfd6`

| Candidate type | Campaign side | Current side |
|---|---|---|
| anomaly | 9 | 10 |
| dream | 5 | 4 |
| experiment | 5 | 4 |
| investigation | 5 | 4 |
| loop_candidate | 6 | 5 |
| meta_concept | 2 | 2 |
| phrase_candidate | 1 | 1 |
| prediction_candidate | 5 | 4 |

## 4. The order of the pool, and where the order parts company

**The set and the order are two different findings.** A pool is a sequence: the engine reads the sleep window back newest-first and hands the candidates to the rest of the cycle in that order. Two pools can hold exactly the same candidates and still be different pools, so which of the two things happened on a given seed is the question this section answers.

Across the 16 arm-pairs, the two sides hold the **same set** of candidate IDs at the divergence cycle in **0** of them, and the **same order** in **0**.

| Task | Seed | Cycle | Arm | Same set | Same order | First differing position | Campaign’s candidate there | Ours |
|---|---|---|---|---|---|---|---|---|
| T1 | 20261125 | 11 | B | no | no | 0 | `exp_f52c7b1e` | `exp_2e3a7c5f` |
| T1 | 20261125 | 11 | C | no | no | 0 | `exp_f52c7b1e` | `exp_2e3a7c5f` |
| T1 | 20261128 | 3 | B | no | no | 0 | `exp_69fefc7c` | `exp_b342b9ae` |
| T1 | 20261128 | 3 | C | no | no | 0 | `exp_69fefc7c` | `exp_b342b9ae` |
| T1 | 20261129 | 2 | B | no | no | 44 | `meta_548a4251` | `meta_b1601f69` |
| T1 | 20261129 | 2 | C | no | no | 44 | `meta_548a4251` | `meta_b1601f69` |
| T2 | 20261118 | 5 | B | no | no | 17 | `hyp_8c033fb0` | `hyp_48d0e5fd` |
| T2 | 20261118 | 5 | C | no | no | 0 | `anomaly_29b7be02` | `anomaly_fe1fa533` |
| T2 | 20261120 | 5 | B | no | no | 13 | `dream_analogy_456a14f9` | `dream_analogy_7fd9b8ba` |
| T2 | 20261120 | 5 | C | no | no | 9 | `anomaly_92221878` | `anomaly_3329a612` |
| T2 | 20261121 | 5 | B | no | no | 10 | `dream_analogy_a6f80540` | `dream_analogy_b38b643c` |
| T2 | 20261121 | 5 | C | no | no | 0 | `anomaly_a0072b14` | `anomaly_c8edf4ca` |
| T2 | 20261123 | 5 | B | no | no | 27 | `pred_bc95dc38` | `pred_974c6a02` |
| T2 | 20261123 | 5 | C | no | no | 10 | `pred_bc95dc38` | `pred_974c6a02` |
| T2 | 20261130 | 5 | B | no | no | 0 | `exp_85461809` | `exp_f47b21f5` |
| T2 | 20261130 | 5 | C | no | no | 3 | `exp_d31ecf56` | `exp_ed2c60fa` |

**Did the reordering happen at the divergence cycle, or was it already there?** The capture holds the window for the cycle before the divergence as well. Where the two sides’ pools were identical in set *and* order at that earlier cycle, and identical in set but different in order at the divergence cycle, the reordering and the divergence are the same event.

| Task | Seed | Cycle | Arm | Previous cycle — same set / same order | This cycle — same set / same order | The reordering coincides with the divergence |
|---|---|---|---|---|---|---|
| T1 | 20261125 | 11 | B | no / no | no / no | no |
| T1 | 20261125 | 11 | C | no / no | no / no | no |
| T1 | 20261128 | 3 | B | yes / no | no / no | no |
| T1 | 20261128 | 3 | C | yes / no | no / no | no |
| T1 | 20261129 | 2 | B | yes / no | no / no | no |
| T1 | 20261129 | 2 | C | yes / no | no / no | no |
| T2 | 20261118 | 5 | B | yes / no | no / no | no |
| T2 | 20261118 | 5 | C | yes / yes | no / no | yes |
| T2 | 20261120 | 5 | B | no / no | no / no | no |
| T2 | 20261120 | 5 | C | no / no | no / no | no |
| T2 | 20261121 | 5 | B | no / no | no / no | no |
| T2 | 20261121 | 5 | C | yes / no | no / no | no |
| T2 | 20261123 | 5 | B | yes / no | no / no | no |
| T2 | 20261123 | 5 | C | yes / yes | no / no | yes |
| T2 | 20261130 | 5 | B | yes / no | no / no | no |
| T2 | 20261130 | 5 | C | yes / yes | no / no | yes |

**No arm-C pair shows the pool identical in set *and* order at the divergence cycle.** Across all 16 arm-pairs, on both arms, the two sides differ in membership at the cycle where the admitted streams part company, so on these seeds the divergence is a difference in which candidates were in the pool, not in the order they were read in. The identical-pool pairs this section reported on 2026-10-31 were measured one cycle early (see the correction at the head of this document); re-measured at the divergence cycle they are gone.

**Two orders, and this capture measures one of them.** The engine reads its window back with `ORDER BY time DESC` and no rowid tiebreak (`organica/memory.py:390`), so the pool arrives as a sequence and the capture measures that sequence. Inside the cycle, the candidate list is assembled from that sequence in an order that is *not* the sequence: the tags of each prior candidate are collected into a `set` (`organica/sleep.py:1201`) and the candidates of each tag into another (`organica/sleep.py:1223`, `distinct_ids = list(set(cid for cid, _ in refs))`). Set iteration order over strings follows the process’s hash seed, so two processes reading the *same* pool assemble it in *different* orders.

**What the pairs point at.** Set iteration order over strings is hash-seeded, so two processes reading the *same* pool can assemble it in different orders, and that step is active from cycle 1 on every seed including the control (`docs/DIVERGENCE-MECHANISM-RESULTS.md`). This capture reports the narrower fact: the membership difference is present at the cycle where the admitted streams part company, so there is no identical pool here from which to attribute the divergence to order alone.

**What it does not establish.** That the order difference *caused* the admitted-stream difference, and it does not measure the order the ranking actually saw. The admitted stream is the engine’s ranking of the pool; this capture observes the pool and the admitted stream, and does not decompose the ranking between them, nor the assembly step that precedes it. The supported claim is the narrower one: **at the cycle where the populations part company, the two sides hold the same set in **0** of 16 arm-pairs and the same order in **0** of 16, so the membership difference is present wherever the admitted streams diverge.**

## 5. What this does not establish

It names the candidate pool at the cycle where the two populations part company, what changed in it since the cycle before, and the order in which the engine read it back. It does not establish which candidate caused the divergence: the pool is the input to the decision, and the decision is the admitted stream, whose contents are recorded but whose internal ranking is not decomposed here. It does not re-score D0, and it does not change any verdict.

## Provenance

- Artifact: `docs/divergence_cycle_capture.json`.
- Instrument: `benchmarks/divergence_cycle_capture.py`.
- Membership reference: `docs/candidate_membership_audit.json` (sha256 `544ebd87bf86a7b38e98815449cd86e66a9ed75dbc3ffb1431cae34c76365e17`).
- Observer version: 3.
- Capture command: `python benchmarks/divergence_cycle_capture.py --workers 4`.
- Seeds in the artifact: **8** (16 arm-pairs), all regenerated by the worker processes under observer version 3 after the cycle base changed; the parent process records 0 run(s) and 16 part(s) found current, because under `--workers` it assembles parts the workers wrote.
- Re-render from the artifact: `python benchmarks/divergence_cycle_capture.py --render-only`.
- The capture’s own determinism control: `python benchmarks/divergence_cycle_capture.py --compare-parts <dir>` compares the parts on disk against another directory of parts, field by field, with the observer-version field set aside.
