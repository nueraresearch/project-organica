# Use-path reproduction audit — three layers on the failing seeds

**Status.** Post-hoc audit observation, 2026-10-30. It is not a protocol, it does not amend D0, and it does not re-score the formation-vs-utilization campaign or the use-path diagnostic. D0 remains score-based and unchanged, and the diagnostic's `AUDIT REQUIRED` verdict stands.

**Machine-readable counts:** `seeds=8 repeats=3 runs=48 no_tiebreak_stable=8 tiebreak_stable=8 arms_agree=8 digests_agree=8 campaign_no_match=0 campaign_tie_match=0 diagnostic_no_match=8 diagnostic_tie_match=8 layer3_entered=0`

The campaign's per-type table is the intermediate endpoint, as §68 specified. A seed is compared on its candidate table first; its scores are compared only if the table reproduces.

## 1. Design and intervention

Eight seeds failed D0. Each was run 3 times under the shipped `MemoryService.recent()` (no tiebreak) and the same number of times with the same query plus `rowid DESC`, in the same process, each run against a fresh database. The audit temporarily replaces the method in-process and restores it; `organica/` is not edited. `PYTHONHASHSEED=0` is required and inherited by every worker.

The layer order is the one committed in §68: repeatability, then structural reproduction, then score reproduction. Candidate IDs and the temporal-graph digest are recorded because neither campaign artifact carries them.

## 2. Layer 1 — repeatability

| Task | Seed | D0 failed limbs | No tiebreak | `rowid` tiebreak | Configurations identical |
|---|---|---|---|---|---|
| T1 | 20261125 | retention, transfer, revision | 3/3 | 3/3 | yes |
| T1 | 20261128 | transfer, revision | 3/3 | 3/3 | yes |
| T1 | 20261129 | retention, transfer, revision | 3/3 | 3/3 | yes |
| T2 | 20261118 | retention | 3/3 | 3/3 | yes |
| T2 | 20261120 | revision | 3/3 | 3/3 | yes |
| T2 | 20261121 | retention, revision | 3/3 | 3/3 | yes |
| T2 | 20261123 | retention, transfer, revision | 3/3 | 3/3 | yes |
| T2 | 20261130 | retention, transfer, revision | 3/3 | 3/3 | yes |

Each cell is identical tables out of independent runs. The no-tiebreak and `rowid` configurations were stable on 8/8 and 8/8 seeds respectively, and the two configurations agreed on 8/8.

## 3. Layer 2 — structural reproduction

| Task | Seed | Campaign table reproduced | Asserted edges (campaign → audit) | Coverage (campaign → audit) | Per-type deltas |
|---|---|---|---|---|---|
| T1 | 20261125 | no-tiebreak no; rowid no | 165 → 177 | 0.8812 → 0.9187 | anomaly (+1 ids, +0.0 weight); dream (+4 ids, +6.0 weight); experiment (+2 ids, +0.0 weight); hypothesis (+3 ids, +3.0 weight); investigation (+2 ids, +0.0 weight); loop_candidate (+6 ids, +32.0 weight); prediction_candidate (+9 ids, -27.0 weight); question (+1 ids, +0.0 weight); theory (+2 ids, +0.0 weight) |
| T1 | 20261128 | no-tiebreak no; rowid no | 175 → 179 | 0.9682 → 0.9745 | anomaly (-1 ids, +0.0 weight); dream (+6 ids, +10.0 weight); hypothesis (+3 ids, +3.0 weight); loop_candidate (+4 ids, +18.0 weight); meta_concept (-1 ids, +0.0 weight); prediction_candidate (+1 ids, -86.0 weight) |
| T1 | 20261129 | no-tiebreak no; rowid no | 170 → 167 | 0.9161 → 0.9226 | anomaly (+2 ids, +0.0 weight); dream (+0 ids, +2.0 weight); hypothesis (+2 ids, +2.0 weight); loop_candidate (-2 ids, -10.0 weight); prediction_candidate (+0 ids, -17.0 weight); question (+1 ids, +0.0 weight); theory (+1 ids, +0.0 weight); workflow_concept (-2 ids, -2.0 weight) |
| T2 | 20261118 | no-tiebreak no; rowid no | 172 → 172 | 0.9911 → 0.9911 | anomaly (+1 ids, +0.0 weight); dream (-2 ids, -4.0 weight); experiment (-1 ids, +0.0 weight); investigation (-1 ids, +0.0 weight); loop_candidate (+1 ids, +4.0 weight) |
| T2 | 20261120 | no-tiebreak no; rowid no | 171 → 173 | 1.0000 → 1.0000 | dream (-2 ids, -4.0 weight); experiment (-3 ids, +0.0 weight); investigation (-3 ids, +0.0 weight); loop_candidate (+0 ids, -2.0 weight); prediction_candidate (+0 ids, +24.0 weight); process_candidate (-1 ids, -2.0 weight); workflow_concept (-1 ids, -1.0 weight) |
| T2 | 20261121 | no-tiebreak no; rowid no | 178 → 181 | 1.0000 → 1.0000 | anomaly (-1 ids, +0.0 weight); dream (+2 ids, +5.0 weight); experiment (+2 ids, +0.0 weight); investigation (+2 ids, +0.0 weight); loop_candidate (-1 ids, -4.0 weight); prediction_candidate (+0 ids, +20.0 weight) |
| T2 | 20261123 | no-tiebreak no; rowid no | 178 → 175 | 1.0000 → 1.0000 | dream (-1 ids, -2.0 weight); experiment (-2 ids, +0.0 weight); investigation (-2 ids, +0.0 weight); loop_candidate (-1 ids, -4.0 weight); prediction_candidate (+0 ids, +36.0 weight) |
| T2 | 20261130 | no-tiebreak no; rowid no | 178 → 181 | 1.0000 → 1.0000 | anomaly (-1 ids, +0.0 weight); dream (+3 ids, +3.0 weight); experiment (+1 ids, +0.0 weight); investigation (+1 ids, +0.0 weight); loop_candidate (+0 ids, +2.0 weight); prediction_candidate (+0 ids, +2.0 weight); process_candidate (+1 ids, +2.0 weight); workflow_concept (+1 ids, +1.0 weight) |

The campaign table reproduced on 0 of 8 seeds under the shipped order and 0 of 8 under the tiebreak. The deltas are candidate-id counts and edge weights, per type; they move in both directions, so this is a different candidate population, not a consistent shift.

## 4. Layer 3 — score reproduction (not entered)

No seed reached layer 3: the candidate population did not reproduce on any of them. The score differences are recorded below so the next audit does not need to re-run them, and they are not a reproduction result.

| Task | Seed | max abs delta, retention | transfer | revision |
|---|---|---|---|---|
| T1 | 20261125 | 0.000766 | 0.000319 | 0.001787 |
| T1 | 20261128 | 4.8e-05 | 0.00109 | 0.004386 |
| T1 | 20261129 | 0.00057 | 0.000507 | 0.001359 |
| T2 | 20261118 | 0.00014 | 3e-06 | 6.1e-05 |
| T2 | 20261120 | 1.5e-05 | 2e-05 | 0.000647 |
| T2 | 20261121 | 0.000424 | 9.6e-05 | 0.000621 |
| T2 | 20261123 | 0.000656 | 0.00102 | 0.000742 |
| T2 | 20261130 | 0.00032 | 0.000454 | 0.000743 |

The two configurations produced identical scores, so one set of columns covers both.

## 5. Verdict

**Instrument check: passed on 8 of 8 seeds.** Both configurations reproduce the diagnostic's per-type table and its three D0 scores exactly, to the diagnostic artifact's six-decimal rounding. The audit is therefore a re-run of the object D0 failed on, not a measurement of a different object.

**Layer 1: passed.** Each configuration reproduced its own per-type table on 8 of 8 seeds and in every one of the 3 repeats. The repeats are independent databases with independent wall-clock timestamps; they share the pinned hash seed, which is the declared constant. There is no run-to-run instability to explain on these seeds.

**The intervention is inert.** The no-tiebreak and `rowid DESC` configurations produced identical per-type tables and identical scores on every audited seed. The tiebreak is a real change to the query -- the self-test fires it on equal timestamps -- but on these worlds it changes nothing the run reads. The candidate-ID digests and the B-arm temporal-graph digest are also identical on 8 of 8 seeds. A cause cannot be a difference that makes no difference.

**Layer 2: failed on every seed.** Neither configuration reproduced the campaign's per-type table. The differences are structural, not a single drifted score: unique candidate counts move in both directions and edge weights move with them.

**Layer 3: not entered.** The design compares scores only after the candidate population reproduces, and it did not reproduce on any seed. The score differences in the table are recorded as observations, not as a score-reproduction result.

**Verdict: retrieval-order instability is not supported as the cause of the D0 mismatch.** The `rowid`-tiebreak hypothesis, as §67 stated it, does not survive its own falsifier: adding the tiebreak did not move the object, and the object is repeatable without it. The divergence is upstream of `recent()`'s tie order.

This is the outcome §68 pre-declared for exactly this pattern -- both configurations stable and both differing from the campaign → look upstream of retrieval order, beginning with the code revision. The audit follows that rule rather than inventing one.

The audit does not name the upstream cause. Two candidates remain, both campaign-side and both unrecorded: a campaign-time harness revision (the harness was uncommitted when the campaign ran and was committed later) and the campaign's execution environment (the artifact records neither the hash seed nor the tie order). The diagnostic's structure check constrains the first: 51 of 60 campaign units reproduce their table under this same pinned code, so a code difference that affected every unit is excluded. What is not excluded is a difference that acts only on ordering-sensitive units. The audit cannot separate that from an environment difference, and does not.


The diagnostic's structure check supplies the constraint on the remaining candidates: 51 identical/pass, 0 identical/fail, 8 different/fail and 1 different/pass. The eight different/fail units are the eight audited here; T2 `20261122` is the different/pass exception and is outside this audit.

## 6. What would settle the remaining question

A hash-seed sensitivity sweep on one failing seed is the cheapest next test: if the per-type table moves across hash seeds, the campaign's unrecorded environment is sufficient to explain the mismatch; if it does not, the remaining candidate is the campaign-time code, which needs a campaign-time copy rather than another re-run. The sweep was not run here: the audit's stop condition is the three layers above, and adding a fourth after seeing the result would be a new instrument.

## 7. What is not claimed

No mechanism, no room estimate, no component, no V2 brief and no re-score of the campaign or the diagnostic. The campaign's recorded verdicts stand. The diagnostic's D0 gate fired and its `AUDIT REQUIRED` outcome stands; this audit tests one hypothesis about why it fired and does not support that hypothesis as the cause, which is not the same as passing D0.

## Provenance

- Artifact: `docs/use_path_audit.json` (generated 2026-10-31T06:10:04.962312+00:00).
- Command: `PYTHONHASHSEED=0 python benchmarks/use_path_audit.py --repeats 3 --workers 8  # reanalysed in place`.
- Hash seed: `PYTHONHASHSEED=0`.
- Campaign reference: `docs/formation_utilization.json`.
- Diagnostic reference: `docs/use_path_diagnostic.json`.
- Structure check: `docs/use_path_diagnostic_structure.json`.
- Instrument: `benchmarks/use_path_audit.py`; checks: `tests/test_use_path_audit.py`.
