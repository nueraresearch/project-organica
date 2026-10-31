# Candidate-membership audit — the campaign’s candidate IDs, and ours

**Status.** Measured 2026-10-31, at the owner’s direction: artifact provenance reconstruction, not another diagnostic layer. It does not amend D0, it does not re-score the campaign, and it does not change any verdict.

## 1. The question, and the pivotal unknown

Eight seeds fail the D0 reproduction. Their per-type candidate **counts** were known; their candidate **identity** was not. This audit names the candidate IDs on each side and locates the first point at which the two populations differ.

The campaign artifact records a per-type table of `unique_count` and `edge_weight` and nothing else. **No candidate ID appears in `docs/formation_utilization.json`, `docs/use_path_diagnostic.json` or `docs/use_path_audit.json`.** The campaign-side population is therefore recoverable only by re-running the campaign harness and keeping the run whose fingerprint equals the campaign’s. That was the pivotal unknown, and it is now settled.

## 2. The code revision is excluded

**By provenance.** `git diff a95305d HEAD -- organica/` is empty: the engine is byte-identical to the state the campaign ran against, and `a95305d` (2026-10-25 09:21 -0600) precedes the campaign’s generation stamp (`2026-10-31T02:09:33.631084+00:00`). Every file the harness executes was last modified before the campaign ran. The one file whose campaign-time state is not pinned by a commit — `benchmarks/formation_utilization.py`, committed 89 minutes after the campaign finished — is closed by measurement rather than by argument.

**By measurement.** Under the committed code, with `PYTHONHASHSEED` varied and nothing else changed, the campaign’s own per-type table is reproduced **exactly** on **8 of the 8 failing seeds**. The code state is sufficient to produce the campaign’s population, so the divergence is not in the code.

## 3. The environment: the hash seed

The engine iterates sets of strings, and CPython randomises string hashing per process unless `PYTHONHASHSEED` is pinned. The use-path audit and the diagnostic pinned `PYTHONHASHSEED=0`; the campaign artifact records neither the hash seed nor the tie order, and the campaign ran with `--workers 10`, so each of its worker processes carried its own hash seed.

| Task | Seed | Hash seeds that reproduce the campaign | D0 limbs that failed |
|---|---|---|---|
| T1 | 20261125 | 2, 5, 9, 15 | retention, transfer, revision |
| T1 | 20261128 | 7, 8, 10, 12, 13, 14 | transfer, revision |
| T1 | 20261129 | 2, 5, 9, 15 | retention, transfer, revision |
| T2 | 20261118 | 1, 2, 4, 5, 9, 10, 14 | retention |
| T2 | 20261120 | 13 | revision |
| T2 | 20261121 | 2, 4, 5, 6, 8, 9 | retention, revision |
| T2 | 20261123 | 8, 10, 12, 14 | retention, transfer, revision |
| T2 | 20261130 | 2, 3, 9, 15 | retention, transfer, revision |
| T1 | 20261101 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 | control (reproduces) |

## 4. The membership, per seed

**Campaign candidates** are the run whose fingerprint equals the campaign’s. **Current candidates** are the run at the pinned hash seed, which is what the use-path audit measured. *Missing* is present in the campaign and absent from the current reconstruction; *Added* is present in the current reconstruction and absent from the campaign.

| Task | Seed | Both | Missing (campaign only) | Added (current only) | Types that differ |
|---|---|---|---|---|---|
| T1 | 20261125 | 254 | 35 | 65 | 11 |
| T1 | 20261128 | 234 | 63 | 75 | 12 |
| T1 | 20261129 | 231 | 62 | 64 | 12 |
| T2 | 20261118 | 227 | 9 | 7 | 7 |
| T2 | 20261120 | 215 | 21 | 11 | 7 |
| T2 | 20261121 | 210 | 32 | 36 | 9 |
| T2 | 20261123 | 212 | 20 | 14 | 7 |
| T2 | 20261130 | 221 | 10 | 16 | 7 |
| T1 | 20261101 | 303 | 0 | 0 | 0 |

### T1 / 20261125

Campaign side: hash seed **2**. Current reconstruction: hash seed **0**. Arm B’s own table matches the campaign’s on the campaign side and does not match it on the current side.

| Type | Both | Missing (campaign only) | Added (current only) |
|---|---|---|---|
| anomaly | 4 | 6 | 7 |
| dream | 5 | 5 | 9 |
| experiment | 6 | 2 | 4 |
| hypothesis | 31 | 3 | 6 |
| investigation | 6 | 2 | 4 |
| loop_candidate | 19 | 3 | 9 |
| meta_concept | 15 | 0 | 0 |
| prediction_candidate | 147 | 0 | 9 |
| process_candidate | 5 | 5 | 5 |
| question | 6 | 2 | 3 |
| theory | 5 | 2 | 4 |
| workflow_concept | 5 | 5 | 5 |

**anomaly**

- Missing — campaign only (6): `anomaly_0227c36a`, `anomaly_05233da0`, `anomaly_ab247c3d`, `anomaly_cb5d773a`, `anomaly_d0ab3749`, `anomaly_e77a2e6f`
- Added — current reconstruction only (7): `anomaly_0f874250`, `anomaly_619ad80b`, `anomaly_7e5369fd`, `anomaly_995f43fa`, `anomaly_bc2e5616`, `anomaly_d9d9956a`, `anomaly_f5973cc8`

**dream**

- Missing — campaign only (5): `dream_cond_abc3c91a`, `dream_cond_bbedbdd9`, `dream_cond_d04fa6f7`, `dream_mut_3a660042`, `dream_mut_ede4b5ce`
- Added — current reconstruction only (9): `dream_analogy_36e8eb9f`, `dream_analogy_8b383d73`, `dream_cond_0834bc52`, `dream_cond_31b9db0e`, `dream_cond_81149fad`, `dream_mut_212feb33`, `dream_mut_3091a9c8`, `dream_mut_83be8949`, `dream_mut_95bf7351`

**experiment**

- Missing — campaign only (2): `exp_6a2dbdd3`, `exp_6d041780`
- Added — current reconstruction only (4): `exp_773fe6b0`, `exp_77d7b739`, `exp_9d96fa8f`, `exp_ec637548`

**hypothesis**

- Missing — campaign only (3): `hyp_050c5ef4`, `hyp_0f32fe15`, `hyp_a04f50f2`
- Added — current reconstruction only (6): `hyp_33f01105`, `hyp_5be3da66`, `hyp_81149fad`, `hyp_974c6a02`, `hyp_b3c6c90d`, `hyp_c36bbb91`

**investigation**

- Missing — campaign only (2): `inv_2177d7b0`, `inv_d59a7095`
- Added — current reconstruction only (4): `inv_5f69cdf1`, `inv_af1a9d80`, `inv_f58ca877`, `inv_fab54b72`

**loop_candidate**

- Missing — campaign only (3): `loop_0cb127a1`, `loop_1908f98b`, `loop_41f383df`
- Added — current reconstruction only (9): `loop_050c5ef4`, `loop_0eaab7d0`, `loop_1c53486b`, `loop_33f01105`, `loop_417da26f`, `loop_682c6a54`, `loop_7ff50e2b`, `loop_dc1ceb15`, `loop_ebd022b8`

**prediction_candidate**

- Added — current reconstruction only (9): `pred_331be2d4`, `pred_37fddf24`, `pred_3d5d6904`, `pred_545db9b2`, `pred_67ebfc76`, `pred_bc95dc38`, `pred_bd43b9ff`, `pred_c4c60019`, `pred_f50bd924`

**process_candidate**

- Missing — campaign only (5): `process_188d0d36`, `process_45ba4f3d`, `process_7498423f`, `process_b1b5b638`, `process_ed9d7ae1`
- Added — current reconstruction only (5): `process_0834bc52`, `process_33f01105`, `process_5be3da66`, `process_81149fad`, `process_974c6a02`

**question**

- Missing — campaign only (2): `question_44a7337b`, `question_f88106c4`
- Added — current reconstruction only (3): `question_4081f8ec`, `question_d7bdfd35`, `question_e5a539be`

**theory**

- Missing — campaign only (2): `theory_44a7337b`, `theory_f88106c4`
- Added — current reconstruction only (4): `theory_9e847117`, `theory_d7bdfd35`, `theory_e5a539be`, `theory_e5b9b5aa`

**workflow_concept**

- Missing — campaign only (5): `workflow_188d0d36`, `workflow_45ba4f3d`, `workflow_7498423f`, `workflow_b1b5b638`, `workflow_ed9d7ae1`
- Added — current reconstruction only (5): `workflow_0834bc52`, `workflow_33f01105`, `workflow_5be3da66`, `workflow_81149fad`, `workflow_974c6a02`

### T1 / 20261128

Campaign side: hash seed **7**. Current reconstruction: hash seed **0**. Arm B’s own table matches the campaign’s on the campaign side and does not match it on the current side.

| Type | Both | Missing (campaign only) | Added (current only) |
|---|---|---|---|
| anomaly | 1 | 12 | 11 |
| dream | 1 | 8 | 14 |
| experiment | 2 | 5 | 5 |
| hypothesis | 29 | 5 | 8 |
| investigation | 2 | 5 | 5 |
| loop_candidate | 18 | 3 | 7 |
| meta_concept | 15 | 1 | 0 |
| prediction_candidate | 153 | 3 | 4 |
| process_candidate | 5 | 5 | 5 |
| question | 2 | 5 | 5 |
| theory | 1 | 6 | 6 |
| workflow_concept | 5 | 5 | 5 |

**anomaly**

- Missing — campaign only (12): `anomaly_07edbffc`, `anomaly_0e04fdf5`, `anomaly_13d30962`, `anomaly_544200c6`, `anomaly_6fb27e4f`, `anomaly_70d2981f`, `anomaly_7b7cca4d`, `anomaly_9e2309d9`, `anomaly_aa6b1046`, `anomaly_e3f06f4a`, `anomaly_efa23355`, `anomaly_f3e25d78`
- Added — current reconstruction only (11): `anomaly_0f73e2a3`, `anomaly_35390cdb`, `anomaly_4c03e0df`, `anomaly_6a4e5036`, `anomaly_7bb4f4b8`, `anomaly_7e162c66`, `anomaly_7efb5b29`, `anomaly_8bb741ed`, `anomaly_a7f81276`, `anomaly_ab247c3d`, `anomaly_f1b2d9f1`

**dream**

- Missing — campaign only (8): `dream_analogy_2996247c`, `dream_analogy_456a14f9`, `dream_analogy_a9ca2e7b`, `dream_cond_18e1d6f5`, `dream_cond_313a43d6`, `dream_cond_972d3173`, `dream_mut_760fc7e7`, `dream_mut_cf4ee5a4`
- Added — current reconstruction only (14): `dream_analogy_1082cbdc`, `dream_analogy_2d3acaa8`, `dream_analogy_437c3c21`, `dream_analogy_4b43bbec`, `dream_analogy_545db9b2`, `dream_analogy_dd9f100a`, `dream_cond_29982b00`, `dream_cond_44c9dff5`, `dream_cond_c36bbb91`, `dream_cond_fc1dfe44`, `dream_mut_5df557dd`, `dream_mut_6bc421d1`, `dream_mut_9025f7e7`, `dream_mut_d3bef9c7`

**experiment**

- Missing — campaign only (5): `exp_036d5ff8`, `exp_0b49e797`, `exp_6c1435f5`, `exp_ab789ab9`, `exp_b342b9ae`
- Added — current reconstruction only (5): `exp_2c081649`, `exp_49bd10fa`, `exp_d2a48eb8`, `exp_d32915ad`, `exp_ef5d1290`

**hypothesis**

- Missing — campaign only (5): `hyp_050eeda2`, `hyp_313a43d6`, `hyp_417da26f`, `hyp_45ba4f3d`, `hyp_ecfe4694`
- Added — current reconstruction only (8): `hyp_5be3da66`, `hyp_63603176`, `hyp_81149fad`, `hyp_974c6a02`, `hyp_ad3bd3c0`, `hyp_b516bed8`, `hyp_b67853a9`, `hyp_c36bbb91`

**investigation**

- Missing — campaign only (5): `inv_201b5d69`, `inv_23f27572`, `inv_6683982e`, `inv_d358fa26`, `inv_f3dc6feb`
- Added — current reconstruction only (5): `inv_9dd836d3`, `inv_b0a57b4f`, `inv_b7645ed4`, `inv_de75b7d6`, `inv_e286bead`

**loop_candidate**

- Missing — campaign only (3): `loop_2f69dab0`, `loop_81149fad`, `loop_e5a539be`
- Added — current reconstruction only (7): `loop_050c5ef4`, `loop_0834bc52`, `loop_1e90ba45`, `loop_62b49344`, `loop_bbedbdd9`, `loop_e5b9b5aa`, `loop_f73e398a`

**meta_concept**

- Missing — campaign only (1): `meta_b62f3b3b`

**prediction_candidate**

- Missing — campaign only (3): `pred_295b39a6`, `pred_37fddf24`, `pred_f50bd924`
- Added — current reconstruction only (4): `pred_30746580`, `pred_7828dcdf`, `pred_a72ccfd6`, `pred_e2dd31dc`

**process_candidate**

- Missing — campaign only (5): `process_18e1d6f5`, `process_313a43d6`, `process_34e4a7fb`, `process_417da26f`, `process_fc1dfe44`
- Added — current reconstruction only (5): `process_0834bc52`, `process_33f01105`, `process_81149fad`, `process_974c6a02`, `process_b516bed8`

**question**

- Missing — campaign only (5): `question_1c53486b`, `question_6eef169e`, `question_727759c9`, `question_9a93b25b`, `question_d81bba30`
- Added — current reconstruction only (5): `question_16c21146`, `question_1840a04d`, `question_c21ab2ba`, `question_cfac41a8`, `question_f1f0cae3`

**theory**

- Missing — campaign only (6): `theory_1c53486b`, `theory_6eef169e`, `theory_727759c9`, `theory_93d31c0d`, `theory_d73713a5`, `theory_e2484dcd`
- Added — current reconstruction only (6): `theory_16c21146`, `theory_1840a04d`, `theory_9e847117`, `theory_c21ab2ba`, `theory_cfac41a8`, `theory_e70d60c0`

**workflow_concept**

- Missing — campaign only (5): `workflow_18e1d6f5`, `workflow_313a43d6`, `workflow_34e4a7fb`, `workflow_417da26f`, `workflow_fc1dfe44`
- Added — current reconstruction only (5): `workflow_0834bc52`, `workflow_33f01105`, `workflow_81149fad`, `workflow_974c6a02`, `workflow_b516bed8`

### T1 / 20261129

Campaign side: hash seed **2**. Current reconstruction: hash seed **0**. Arm B’s own table matches the campaign’s on the campaign side and does not match it on the current side.

| Type | Both | Missing (campaign only) | Added (current only) |
|---|---|---|---|
| anomaly | 4 | 6 | 8 |
| dream | 2 | 8 | 8 |
| experiment | 1 | 6 | 6 |
| hypothesis | 24 | 10 | 12 |
| investigation | 1 | 6 | 6 |
| loop_candidate | 22 | 2 | 0 |
| meta_concept | 14 | 1 | 1 |
| prediction_candidate | 147 | 2 | 2 |
| process_candidate | 7 | 4 | 4 |
| question | 2 | 5 | 6 |
| theory | 2 | 6 | 7 |
| workflow_concept | 5 | 6 | 4 |

**anomaly**

- Missing — campaign only (6): `anomaly_4a426aff`, `anomaly_9aeacb9c`, `anomaly_a549fc1e`, `anomaly_ca7eadc0`, `anomaly_cbd68ab6`, `anomaly_f9fcafcc`
- Added — current reconstruction only (8): `anomaly_2472412a`, `anomaly_49524ec9`, `anomaly_7f9a4193`, `anomaly_9b0155ab`, `anomaly_b17cef4a`, `anomaly_b382ac17`, `anomaly_f653cd89`, `anomaly_fcf2138e`

**dream**

- Missing — campaign only (8): `dream_analogy_a2582513`, `dream_analogy_b0a67091`, `dream_cond_0f32fe15`, `dream_cond_9e19432e`, `dream_cond_cf11d4d4`, `dream_cond_d04fa6f7`, `dream_mut_71c2842d`, `dream_mut_d0ba2a1c`
- Added — current reconstruction only (8): `dream_analogy_456a14f9`, `dream_cond_0834bc52`, `dream_cond_188d0d36`, `dream_cond_44c9dff5`, `dream_cond_a04f50f2`, `dream_cond_b516bed8`, `dream_mut_376e2422`, `dream_mut_ec8ca00e`

**experiment**

- Missing — campaign only (6): `exp_1a9157a6`, `exp_2d9b8480`, `exp_6d041780`, `exp_861d6320`, `exp_e9d0504a`, `exp_f023341f`
- Added — current reconstruction only (6): `exp_49bd10fa`, `exp_77d7b739`, `exp_810b7597`, `exp_ce2d9695`, `exp_ec637548`, `exp_f10c1cec`

**hypothesis**

- Missing — campaign only (10): `hyp_050c5ef4`, `hyp_0c1536ac`, `hyp_2ff50859`, `hyp_63603176`, `hyp_7498423f`, `hyp_a04f50f2`, `hyp_abc3c91a`, `hyp_b67853a9`, `hyp_d04fa6f7`, `hyp_ed9d7ae1`
- Added — current reconstruction only (12): `hyp_188d0d36`, `hyp_29982b00`, `hyp_33f01105`, `hyp_45ba4f3d`, `hyp_5711aaab`, `hyp_5be3da66`, `hyp_6ea36d82`, `hyp_aa517900`, `hyp_ad3bd3c0`, `hyp_aeff9bcd`, `hyp_b1b5b638`, `hyp_c86f2f15`

**investigation**

- Missing — campaign only (6): `inv_0f81c50c`, `inv_2f331edb`, `inv_a45fe6df`, `inv_cbfe0c4b`, `inv_d59a7095`, `inv_eabddf8d`
- Added — current reconstruction only (6): `inv_678ec104`, `inv_863ba5d4`, `inv_a7825392`, `inv_e286bead`, `inv_f58ca877`, `inv_fab54b72`

**loop_candidate**

- Missing — campaign only (2): `loop_33f01105`, `loop_88b09a7d`

**meta_concept**

- Missing — campaign only (1): `meta_fa659831`
- Added — current reconstruction only (1): `meta_efd764d8`

**prediction_candidate**

- Missing — campaign only (2): `pred_437c3c21`, `pred_fb0a30c1`
- Added — current reconstruction only (2): `pred_3c3ad17b`, `pred_f23e4eb4`

**process_candidate**

- Missing — campaign only (4): `process_050c5ef4`, `process_7498423f`, `process_abc3c91a`, `process_ed9d7ae1`
- Added — current reconstruction only (4): `process_1e90ba45`, `process_29982b00`, `process_45ba4f3d`, `process_b1b5b638`

**question**

- Missing — campaign only (5): `question_41f383df`, `question_44a7337b`, `question_6de83bcd`, `question_7a870b89`, `question_f73e398a`
- Added — current reconstruction only (6): `question_6eef169e`, `question_b680bbc5`, `question_cfac41a8`, `question_d7bdfd35`, `question_e5a539be`, `question_ebd022b8`

**theory**

- Missing — campaign only (6): `theory_44a7337b`, `theory_73dcc480`, `theory_9e4ea125`, `theory_d4679169`, `theory_df5d794e`, `theory_f73e398a`
- Added — current reconstruction only (7): `theory_6eef169e`, `theory_b680bbc5`, `theory_cfac41a8`, `theory_d73713a5`, `theory_d7bdfd35`, `theory_e5a539be`, `theory_ebd022b8`

**workflow_concept**

- Missing — campaign only (6): `workflow_050c5ef4`, `workflow_33f01105`, `workflow_7498423f`, `workflow_974c6a02`, `workflow_abc3c91a`, `workflow_ed9d7ae1`
- Added — current reconstruction only (4): `workflow_1e90ba45`, `workflow_29982b00`, `workflow_45ba4f3d`, `workflow_b1b5b638`

### T2 / 20261118

Campaign side: hash seed **1**. Current reconstruction: hash seed **0**. Arm B’s own table matches the campaign’s on the campaign side and does not match it on the current side.

| Type | Both | Missing (campaign only) | Added (current only) |
|---|---|---|---|
| anomaly | 13 | 0 | 1 |
| dream | 7 | 2 | 0 |
| experiment | 6 | 2 | 1 |
| hypothesis | 14 | 1 | 1 |
| investigation | 6 | 2 | 1 |
| loop_candidate | 20 | 1 | 2 |
| meta_concept | 14 | 1 | 1 |
| prediction_candidate | 127 | 0 | 0 |
| process_candidate | 10 | 0 | 0 |
| workflow_concept | 10 | 0 | 0 |

**anomaly**

- Added — current reconstruction only (1): `anomaly_87d00f22`

**dream**

- Missing — campaign only (2): `dream_mut_1d6be603`, `dream_mut_99db68ee`

**experiment**

- Missing — campaign only (2): `exp_70af02fd`, `exp_856772ae`
- Added — current reconstruction only (1): `exp_50745d5d`

**hypothesis**

- Missing — campaign only (1): `hyp_642bc75f`
- Added — current reconstruction only (1): `hyp_21019ffd`

**investigation**

- Missing — campaign only (2): `inv_55c5ae20`, `inv_f19a99a0`
- Added — current reconstruction only (1): `inv_0dd174cc`

**loop_candidate**

- Missing — campaign only (1): `loop_7b6cccbe`
- Added — current reconstruction only (2): `loop_3c1f4563`, `loop_f4d07b74`

**meta_concept**

- Missing — campaign only (1): `meta_f0a5da17`
- Added — current reconstruction only (1): `meta_548a4251`

### T2 / 20261120

Campaign side: hash seed **13**. Current reconstruction: hash seed **0**. Arm B’s own table matches the campaign’s on the campaign side and does not match it on the current side.

| Type | Both | Missing (campaign only) | Added (current only) |
|---|---|---|---|
| anomaly | 9 | 1 | 1 |
| dream | 5 | 4 | 2 |
| experiment | 3 | 5 | 2 |
| hypothesis | 15 | 0 | 0 |
| investigation | 3 | 5 | 2 |
| loop_candidate | 19 | 2 | 2 |
| meta_concept | 15 | 0 | 0 |
| prediction_candidate | 128 | 0 | 0 |
| process_candidate | 9 | 2 | 1 |
| workflow_concept | 9 | 2 | 1 |

**anomaly**

- Missing — campaign only (1): `anomaly_cd14865c`
- Added — current reconstruction only (1): `anomaly_03a55a49`

**dream**

- Missing — campaign only (4): `dream_mut_4e1a17e3`, `dream_mut_789461af`, `dream_mut_83e68d9e`, `dream_mut_c25fb32c`
- Added — current reconstruction only (2): `dream_mut_0845d1af`, `dream_mut_a9c044dd`

**experiment**

- Missing — campaign only (5): `exp_1ee41bf1`, `exp_5049533c`, `exp_b145e6e6`, `exp_bacdd248`, `exp_eb3f20a6`
- Added — current reconstruction only (2): `exp_36d7793f`, `exp_52975371`

**investigation**

- Missing — campaign only (5): `inv_570017c3`, `inv_7bc8a3f5`, `inv_80ac10bd`, `inv_e89d3c9b`, `inv_f64690f5`
- Added — current reconstruction only (2): `inv_384fb501`, `inv_ee3cae25`

**loop_candidate**

- Missing — campaign only (2): `loop_0352a0ca`, `loop_79d55589`
- Added — current reconstruction only (2): `loop_188d0d36`, `loop_59acd3b4`

**process_candidate**

- Missing — campaign only (2): `process_731b5bcc`, `process_bd43b9ff`
- Added — current reconstruction only (1): `process_63ac32e2`

**workflow_concept**

- Missing — campaign only (2): `workflow_731b5bcc`, `workflow_bd43b9ff`
- Added — current reconstruction only (1): `workflow_63ac32e2`

### T2 / 20261121

Campaign side: hash seed **2**. Current reconstruction: hash seed **0**. Arm B’s own table matches the campaign’s on the campaign side and does not match it on the current side.

| Type | Both | Missing (campaign only) | Added (current only) |
|---|---|---|---|
| anomaly | 5 | 6 | 5 |
| dream | 6 | 5 | 7 |
| experiment | 2 | 6 | 8 |
| hypothesis | 14 | 1 | 1 |
| investigation | 2 | 6 | 8 |
| loop_candidate | 19 | 5 | 4 |
| meta_concept | 14 | 1 | 1 |
| prediction_candidate | 128 | 0 | 0 |
| process_candidate | 10 | 1 | 1 |
| workflow_concept | 10 | 1 | 1 |

**anomaly**

- Missing — campaign only (6): `anomaly_1d484abf`, `anomaly_2ec970a8`, `anomaly_4057e86a`, `anomaly_acad1716`, `anomaly_bfc259b2`, `anomaly_f81f97d2`
- Added — current reconstruction only (5): `anomaly_0adbf6a6`, `anomaly_19b9cf80`, `anomaly_83159aa6`, `anomaly_ad4bf299`, `anomaly_ff19b360`

**dream**

- Missing — campaign only (5): `dream_analogy_2d3acaa8`, `dream_analogy_a9ca2e7b`, `dream_analogy_fabff6cc`, `dream_mut_083924d0`, `dream_mut_2cc51ecf`
- Added — current reconstruction only (7): `dream_analogy_456a14f9`, `dream_analogy_c11b7d29`, `dream_mut_0845d073`, `dream_mut_55debe1d`, `dream_mut_5eda8d1f`, `dream_mut_d1dfdaa3`, `dream_mut_f7cd379f`

**experiment**

- Missing — campaign only (6): `exp_14f62bf0`, `exp_55c6ebe6`, `exp_b1c99bf0`, `exp_c9ab6eb3`, `exp_d4cbfabd`, `exp_eb3f20a6`
- Added — current reconstruction only (8): `exp_014833fe`, `exp_0bdebaf7`, `exp_0cc541ce`, `exp_2ebafecf`, `exp_5e7a1d0c`, `exp_860c52f6`, `exp_b805662b`, `exp_f4931acf`

**hypothesis**

- Missing — campaign only (1): `hyp_a3c4b048`
- Added — current reconstruction only (1): `hyp_c1ff7ade`

**investigation**

- Missing — campaign only (6): `inv_1320ba16`, `inv_4675a777`, `inv_50aefa31`, `inv_6111b8d8`, `inv_7bc8a3f5`, `inv_bff73c2a`
- Added — current reconstruction only (8): `inv_20943a38`, `inv_43bb6dc1`, `inv_6cdc4284`, `inv_93a919ca`, `inv_95b5d3fd`, `inv_980c117c`, `inv_9ae205dc`, `inv_b12ec5cd`

**loop_candidate**

- Missing — campaign only (5): `loop_37096883`, `loop_51a5a3d0`, `loop_6ff069dc`, `loop_79e2c60e`, `loop_e78a4f4f`
- Added — current reconstruction only (4): `loop_229f18fb`, `loop_2b5e0921`, `loop_3fc6da84`, `loop_65e4fe8b`

**meta_concept**

- Missing — campaign only (1): `meta_f0e14f7f`
- Added — current reconstruction only (1): `meta_2655399a`

**process_candidate**

- Missing — campaign only (1): `process_76eafd70`
- Added — current reconstruction only (1): `process_80289c93`

**workflow_concept**

- Missing — campaign only (1): `workflow_76eafd70`
- Added — current reconstruction only (1): `workflow_80289c93`

### T2 / 20261123

Campaign side: hash seed **8**. Current reconstruction: hash seed **0**. Arm B’s own table matches the campaign’s on the campaign side and does not match it on the current side.

| Type | Both | Missing (campaign only) | Added (current only) |
|---|---|---|---|
| anomaly | 8 | 2 | 2 |
| dream | 7 | 2 | 1 |
| experiment | 3 | 4 | 2 |
| hypothesis | 15 | 0 | 0 |
| investigation | 3 | 4 | 2 |
| loop_candidate | 19 | 2 | 1 |
| meta_concept | 15 | 0 | 0 |
| prediction_candidate | 128 | 0 | 0 |
| process_candidate | 7 | 3 | 3 |
| workflow_concept | 7 | 3 | 3 |

**anomaly**

- Missing — campaign only (2): `anomaly_7469bf7e`, `anomaly_a0b40d09`
- Added — current reconstruction only (2): `anomaly_a36fb389`, `anomaly_f7911631`

**dream**

- Missing — campaign only (2): `dream_mut_05941165`, `dream_mut_d1b48758`
- Added — current reconstruction only (1): `dream_mut_c05659e6`

**experiment**

- Missing — campaign only (4): `exp_98c9df9c`, `exp_da6b19a8`, `exp_f505f94c`, `exp_fa481f50`
- Added — current reconstruction only (2): `exp_014833fe`, `exp_bbe4f9e1`

**investigation**

- Missing — campaign only (4): `inv_598afb2a`, `inv_65fa330c`, `inv_839735fb`, `inv_cddce600`
- Added — current reconstruction only (2): `inv_7ce3505d`, `inv_980c117c`

**loop_candidate**

- Missing — campaign only (2): `loop_7828dcdf`, `loop_8d444d28`
- Added — current reconstruction only (1): `loop_cf7c2929`

**process_candidate**

- Missing — campaign only (3): `process_5da281f1`, `process_8c033fb0`, `process_e6f8a3e6`
- Added — current reconstruction only (3): `process_57b28f60`, `process_9a19e7b4`, `process_fc8aae1c`

**workflow_concept**

- Missing — campaign only (3): `workflow_5da281f1`, `workflow_8c033fb0`, `workflow_e6f8a3e6`
- Added — current reconstruction only (3): `workflow_57b28f60`, `workflow_9a19e7b4`, `workflow_fc8aae1c`

### T2 / 20261130

Campaign side: hash seed **2**. Current reconstruction: hash seed **0**. Arm B’s own table matches the campaign’s on the campaign side and does not match it on the current side.

| Type | Both | Missing (campaign only) | Added (current only) |
|---|---|---|---|
| anomaly | 8 | 3 | 2 |
| dream | 5 | 1 | 4 |
| experiment | 4 | 1 | 2 |
| hypothesis | 15 | 0 | 0 |
| investigation | 4 | 1 | 2 |
| loop_candidate | 22 | 4 | 4 |
| meta_concept | 15 | 0 | 0 |
| prediction_candidate | 128 | 0 | 0 |
| process_candidate | 10 | 0 | 1 |
| workflow_concept | 10 | 0 | 1 |

**anomaly**

- Missing — campaign only (3): `anomaly_5434a4df`, `anomaly_57c30947`, `anomaly_748bf27e`
- Added — current reconstruction only (2): `anomaly_24a4bbe3`, `anomaly_f6e71d1a`

**dream**

- Missing — campaign only (1): `dream_mut_591c5ffa`
- Added — current reconstruction only (4): `dream_analogy_4b43bbec`, `dream_analogy_a2582513`, `dream_analogy_a6157fa7`, `dream_mut_dc876dfe`

**experiment**

- Missing — campaign only (1): `exp_1b28ef91`
- Added — current reconstruction only (2): `exp_0c67b08a`, `exp_4e8f09df`

**investigation**

- Missing — campaign only (1): `inv_e0bba53c`
- Added — current reconstruction only (2): `inv_1cea4d72`, `inv_8b05d0b5`

**loop_candidate**

- Missing — campaign only (4): `loop_3905cc6e`, `loop_57b28f60`, `loop_6db71a7a`, `loop_f2f056c8`
- Added — current reconstruction only (4): `loop_2c6266bc`, `loop_9d02a89e`, `loop_a554fa2a`, `loop_e5648c4c`

**process_candidate**

- Added — current reconstruction only (1): `process_fc5933f7`

**workflow_concept**

- Added — current reconstruction only (1): `workflow_fc5933f7`

### T1 / 20261101 — control

Campaign side: hash seed **0**. Current reconstruction: hash seed **0**. Arm B’s own table matches the campaign’s on the campaign side and matches it on the current side.

| Type | Both | Missing (campaign only) | Added (current only) |
|---|---|---|---|
| anomaly | 10 | 0 | 0 |
| dream | 8 | 0 | 0 |
| experiment | 5 | 0 | 0 |
| hypothesis | 33 | 0 | 0 |
| investigation | 5 | 0 | 0 |
| loop_candidate | 29 | 0 | 0 |
| meta_concept | 15 | 0 | 0 |
| prediction_candidate | 170 | 0 | 0 |
| process_candidate | 10 | 0 | 0 |
| question | 4 | 0 | 0 |
| theory | 4 | 0 | 0 |
| workflow_concept | 10 | 0 | 0 |

No type differs: the two populations are the same set of candidate IDs.

### 4.1 What the counts could not see

The use-path audit recorded a per-type delta only for the types whose **count** moved. A type can keep its count and swap candidate IDs, and on these seeds it does: **22 type/seed pairs** differ in identity while their count is unchanged, spread over **7 of the 8** failing seeds. The net difference is zero in every one of them, which is exactly why the count-based audit did not list them.

| Task | Seed | Types whose count held but whose IDs did not |
|---|---|---|
| T1 | 20261125 | process_candidate, workflow_concept |
| T1 | 20261128 | experiment, investigation, process_candidate, question, theory, workflow_concept |
| T1 | 20261129 | experiment, investigation, meta_concept, process_candidate |
| T2 | 20261118 | hypothesis, meta_concept |
| T2 | 20261120 | anomaly |
| T2 | 20261121 | hypothesis, meta_concept, process_candidate, workflow_concept |
| T2 | 20261123 | anomaly, process_candidate, workflow_concept |

This is why the membership audit is not a restatement of the use-path audit. The count audit said eight seeds failed to reproduce; the membership says **which candidates** differed, and finds 22 differences the count audit could not see.

## 5. Where the two sets first diverge

Arm C’s per-cycle admitted candidate stream is the membership as it was decided, cycle by cycle, and arm C reads arm B’s recorded temporal graphs. The first cycle whose admitted stream differs is therefore the first cycle at which the organism’s candidate population differed.

| Task | Seed | First differing cycle | Sleep window captured |
|---|---|---|---|
| T1 | 20261125 | 11 | yes |
| T1 | 20261128 | 3 | yes |
| T1 | 20261129 | 2 | yes |
| T2 | 20261118 | 5 | yes |
| T2 | 20261120 | 5 | yes |
| T2 | 20261121 | 5 | yes |
| T2 | 20261123 | 5 | yes |
| T2 | 20261130 | 5 | yes |
| T1 | 20261101 | None | yes |

**T1 / 20261125, cycle 11.** The two admitted streams differ at this cycle (campaign digest `b911f7d7531c6485`, current digest `d4eddc359892b8b9`).

The captured sleep window is the engine’s read-back of candidates from sleep events at the arm’s snapshot point — the newest 4000 rows the engine read. On the campaign side it covers engine sleep cycles 109–110; on the current side, 108–110.

The first differing window row is at index 0: the campaign side read `exp_80b9b2ca` and the current side read `exp_9d96fa8f`.

**T1 / 20261128, cycle 3.** The two admitted streams differ at this cycle (campaign digest `54d4cc1b3b3b253d`, current digest `71294d99aad91510`).

The captured sleep window is the engine’s read-back of candidates from sleep events at the arm’s snapshot point — the newest 4000 rows the engine read. On the campaign side it covers engine sleep cycles 109–110; on the current side, 109–110.

The first differing window row is at index 0: the campaign side read `exp_6c1435f5` and the current side read `exp_80b9b2ca`.

**T1 / 20261129, cycle 2.** The two admitted streams differ at this cycle (campaign digest `470c5b28836262f8`, current digest `c7471095b21ba506`).

The captured sleep window is the engine’s read-back of candidates from sleep events at the arm’s snapshot point — the newest 4000 rows the engine read. On the campaign side it covers engine sleep cycles 109–110; on the current side, 109–110.

The first differing window row is at index 0: the campaign side read `exp_e9d0504a` and the current side read `exp_ce2d9695`.

**T2 / 20261118, cycle 5.** The two admitted streams differ at this cycle (campaign digest `a62d6eeb75d09493`, current digest `0a11ed6816efe664`).

The captured sleep window is the engine’s read-back of candidates from sleep events at the arm’s snapshot point — the newest 4000 rows the engine read. On the campaign side it covers engine sleep cycles 74–76; on the current side, 74–76.

The first differing window row is at index 0: the campaign side read `exp_c75d3786` and the current side read `exp_143db930`.

**T2 / 20261120, cycle 5.** The two admitted streams differ at this cycle (campaign digest `85693ab1d5063b85`, current digest `ae5a2b7c98a9b044`).

The captured sleep window is the engine’s read-back of candidates from sleep events at the arm’s snapshot point — the newest 4000 rows the engine read. On the campaign side it covers engine sleep cycles 109–110; on the current side, 109–110.

The first differing window row is at index 0: the campaign side read `exp_bacdd248` and the current side read `exp_52975371`.

**T2 / 20261121, cycle 5.** The two admitted streams differ at this cycle (campaign digest `2f2073ec13f1cdc0`, current digest `1b1849bf0a42defa`).

The captured sleep window is the engine’s read-back of candidates from sleep events at the arm’s snapshot point — the newest 4000 rows the engine read. On the campaign side it covers engine sleep cycles 77–80; on the current side, 79–80.

The first differing window row is at index 0: the campaign side read `exp_b1c99bf0` and the current side read `exp_860c52f6`.

**T2 / 20261123, cycle 5.** The two admitted streams differ at this cycle (campaign digest `f02ed8beb22fa8cc`, current digest `53f7c20fe95e4197`).

The captured sleep window is the engine’s read-back of candidates from sleep events at the arm’s snapshot point — the newest 4000 rows the engine read. On the campaign side it covers engine sleep cycles 109–110; on the current side, 109–110.

The first differing window row is at index 0: the campaign side read `exp_da6b19a8` and the current side read `exp_bbe4f9e1`.

**T2 / 20261130, cycle 5.** The two admitted streams differ at this cycle (campaign digest `90aade4bfee56bbb`, current digest `c8f2fa79cee8d7f7`).

The captured sleep window is the engine’s read-back of candidates from sleep events at the arm’s snapshot point — the newest 4000 rows the engine read. On the campaign side it covers engine sleep cycles 80–81; on the current side, 79–81.

The first differing window row is at index 1: the campaign side read `exp_1b28ef91` and the current side read `exp_0c67b08a`.

**T1 / 20261101.** The two admitted streams do not differ at any cycle: the populations are the same.

**What the window cannot do.** The window is a snapshot of the read-back at the arm’s snapshot point, not a per-cycle record. It shows the population the engine read near the snapshot point, and it shows that the two populations are not the same population. It does **not** name the candidate that entered or left at the divergence: the divergences above are at admitted-stream indices 2, 3, 5, 11, and the admitted stream indexes the arm’s own sleep cycles while the window’s markers carry the engine’s global cycle numbers. The two cannot be aligned from what was captured, so the window cannot bridge the gap between them. Isolating the candidate that entered or left there would need the candidate population per cycle, which this instrument did not capture.

## 6. The controls

- **The pinned hash seed reproduces the use-path audit.** The run at the pinned hash seed reproduces the reconstruction the use-path audit recorded, on every type of every seed: 8 of 9 seeds checked, and 0 seed(s) failed this check. Without it the audit would be measuring a different object from the one the audit measured.
- **The control seed is identical at every hash seed swept.** The positive control T1/20261101 reproduces the campaign at all 16 hash seeds swept, with 0 candidate-ID differences in total, so the instrument is able to return “identical” and not only “different”.
- **The runs that reproduce the campaign agree with one another.** 9 of 9 reproduced seeds have matching hash seeds that produce the same candidate IDs, so the membership is determined by the artifact’s fingerprint rather than by a guess.
- **Arm B matches where arm C matches.** 9 of 9 reproduced seeds have arm B’s own table matching the campaign under the reproducing hash seed; on the current side 0 of 8 failing seeds have arm B’s table differing from the campaign’s. Arm C reads arm B’s recorded temporal graphs, so where arm B differs the divergence entered upstream of arm C’s admission filter.
- **The sleep window was captured for 9 of 9 reproduced seeds.** Where it was not captured, no window position is reported.
- **The membership is finer than the count.** 22 type/seed pairs differ in candidate identity while their count is unchanged; the count-based audit could not see them, and the cross-validation in section 6.1 confirms the membership reproduces the count audit’s own numbers wherever it did record them.

### 6.1 The cross-validation

The membership diff is derived from regenerated populations; the use-path audit’s per-type deltas were recorded earlier, from the same populations, by a different instrument. Where the audit recorded a delta, the membership’s net per-type difference reproduces it exactly, on every type of every seed (`tests/test_candidate_membership_audit.py`). Two derivations, one answer, and no hand transcription anywhere between them.

## 7. What this does not establish

It does not re-score D0, and it does not change the campaign’s verdict. It says where the two candidate populations came from. The sweep covers hash seeds 0–15; a hash seed outside that range would produce a different population. The campaign’s own hash seeds are not recoverable — only its population is.

It does not identify a single mechanism. Hash-order sensitivity is the measured *difference in the environment* that reproduces the campaign’s population; which of the engine’s order-dependent code paths turns that difference into a different candidate set is a separate question. The per-cycle admitted-stream digests localise it to a cycle, and the arm B comparison localises it upstream of arm C’s admission filter, but neither names the code path, and the sleep window cannot name the candidate.

## Provenance

- Artifact: `docs/candidate_membership_audit.json`.
- Command: `python benchmarks/candidate_membership_audit.py --hash-seeds 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 --workers 4`.
- Observer version: 2.
- Campaign reference: `docs/formation_utilization.json` (sha256 `7c78215ea785ad7d384b3bb8dd17964a04a3e00f1681b60dc797ea4e822a2e65`), generated `2026-10-31T02:09:33.631084+00:00`, assembled `2026-10-31T02:20:59.593005+00:00`.
- Audit reference: `docs/use_path_audit.json` (sha256 `08f0f0137e71fa3855f3d632e170732b4ced5797f0649c9b16b0b4a2c7cb135f`).
- Instrument: `benchmarks/candidate_membership_audit.py`; checks: `tests/test_candidate_membership_audit.py`.
