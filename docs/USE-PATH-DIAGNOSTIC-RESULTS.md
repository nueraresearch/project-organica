# AUDIT REQUIRED — the use-path diagnostic

**No room estimate and no mechanism mapping are reported.**

## 0. The D0 validity gate

D0 was required to reproduce the formation-utilization campaign's arm-C scores on all 60 units and every scored limb within 0.000100. Units present: 60. Seed-limbs checked: 180. Largest absolute difference: 0.004386. Failures span 8 distinct seed(s); 17 of 18 are below 0.002.

**18 failure(s)**:

- T1 / 20261125 / retention: expected 0.230747, actual 0.229981, |Δ| 0.000766
- T1 / 20261125 / transfer: expected 0.229070, actual 0.229389, |Δ| 0.000319
- T1 / 20261125 / revision: expected 0.386263, actual 0.388050, |Δ| 0.001787
- T1 / 20261128 / transfer: expected 0.247592, actual 0.246502, |Δ| 0.001090
- T1 / 20261128 / revision: expected 0.393873, actual 0.389487, |Δ| 0.004386
- T1 / 20261129 / retention: expected 0.234546, actual 0.233976, |Δ| 0.000570
- T1 / 20261129 / transfer: expected 0.234862, actual 0.234355, |Δ| 0.000507
- T1 / 20261129 / revision: expected 0.382793, actual 0.381434, |Δ| 0.001359
- T2 / 20261118 / retention: expected 0.360933, actual 0.361073, |Δ| 0.000140
- T2 / 20261120 / revision: expected 0.350555, actual 0.349908, |Δ| 0.000647
- T2 / 20261121 / retention: expected 0.364982, actual 0.364558, |Δ| 0.000424
- T2 / 20261121 / revision: expected 0.346944, actual 0.346323, |Δ| 0.000621
- T2 / 20261123 / retention: expected 0.360591, actual 0.361247, |Δ| 0.000656
- T2 / 20261123 / transfer: expected 0.366038, actual 0.367058, |Δ| 0.001020
- T2 / 20261123 / revision: expected 0.344579, actual 0.343837, |Δ| 0.000742
- T2 / 20261130 / retention: expected 0.366642, actual 0.366962, |Δ| 0.000320
- T2 / 20261130 / transfer: expected 0.365604, actual 0.366058, |Δ| 0.000454
- T2 / 20261130 / revision: expected 0.350402, actual 0.349659, |Δ| 0.000743

## 1. What this means

The diagnostic is decomposing a different object than the one that produced the campaign's ceiling result. A decomposition of that object cannot select a mechanism. The next step is an audit of the reproduction — the recorder, the fixed temporal basis, the engine version, or the saved structures — not a reading of D1–D5.

## 2. What is not reported

- No room estimate.
- No variant effect.
- No component, and no `evidence-limited` conclusion.

## 3. The reproduction diagnosis (hypothesis, not established)

Sleep rows stored in the same time.time() tick share a timestamp. MemoryService.recent() orders only by time DESC, so their order is unspecified. _load_prior_candidates reads the newest 4,000 sleep rows and structure_edges keeps the first snapshot per candidate id. A different tie order keeps a different snapshot, which moves the readout by up to the observed 0.0044 nats.

**Code-path evidence**

- organica/memory.py:247 — store() stamps every event with time.time().
- organica/memory.py:390 — recent() orders by time DESC and has no rowid tiebreak.
- organica/memory.py:465-477 — prune_sleep_candidates() already uses rowid DESC as a tiebreak, so the omission is specific to recent().
- organica/sleep.py:877 — _load_prior_candidates() calls recent(n=4000, event_type='sleep').
- benchmarks/acquisition_runner.py:155 — structure_edges() dedupes by id and keeps the first encounter.

**Falsifier.** Re-run a failing seed twice with an in-process recent() that adds rowid DESC. If the two runs agree and the campaign artifact does not, the tie order is the cause. Not yet run.

**Why this is not a mechanism.** It is a property of the saved object, not of the use path. It does not name retrieval, activation or the readout form.

## 4. Provenance

- Protocol: `docs/USE-PATH-DIAGNOSTIC-PREREGISTRATION.md`
- Protocol SHA-256: `ddc6ae3a2c16ce10dd6d61c71deb56f20ae5f58d2238d8de4eb5948a626014a8`
- Freeze commit: `a700e83f3d383c03d7eaa1072d17726c2082de68`
- Campaign artifact: `docs/formation_utilization.json`
- Engine: 0.10.0
- Hash seed: `PYTHONHASHSEED=0`
- Generated: 2026-10-31T04:30:16Z
