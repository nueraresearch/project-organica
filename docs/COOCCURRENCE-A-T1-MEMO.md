# The co-occurrence build: the (a)+T1 decision memo

**Status: the owner recorded (a)+T1 on 2026-11-19, the count-separation preflight passed the same
day, and the owner granted the block on 2026-11-20 at floor 35.**
([`constraint_decisions/DECISION-COOCCURRENCE-BUILD.json`](constraint_decisions/DECISION-COOCCURRENCE-BUILD.json))
The registration is written
([`constraint_registrations/CONSTRAINT-COOCCURRENCE-A-T1.json`](constraint_registrations/CONSTRAINT-COOCCURRENCE-A-T1.json)),
the grant is [`COOCCURRENCE-A-T1-GRANT.json`](COOCCURRENCE-A-T1-GRANT.json), the ledger row is
`in-test`, and seeds `20261300-20261309` are reserved; no campaign cell has run. The build it
describes is scoped in [`COOCCURRENCE-SELECTION-BUILD.md`](COOCCURRENCE-SELECTION-BUILD.md); this
memo chooses between that page's options and states the terms the grant carries.

## What it proposes

Adopt **allocation law (a)** — drop the partitioned allocation and serve one ranked list — and
**term sheet T1** — keep the registered 0.412011 bar and report the strongest-of-grid comparator
beside the endpoint. This is a recommendation; the owner decides, registers and grants.

## Why (a)

- It is the only law that can express the target. The served count has to sit in 18–69; the 56/56
  partition is dead on arrival, and its only viable form (quotas summing to ≤69) replaces one floor
  with two quotas, so a fail cannot be attributed to the mechanism rather than to the quota.
- One lever, one attribution: under (a) a fail points at the floor or the recall guard. Under (b)
  the axes are weak — entropy is a ranking prior the engine already uses, schema congruence can
  empty a bucket, and recency needs a new stored field, which stops being a one-variable change
  inside `_build_predictions`.
- The counter-argument for (b), preserving the engine's two-population structure, does not survive
  admission: that structure was built on transitions, and the admission rule empties them. Any
  replacement axis is invented for this build.

## Why T1, and what T2 would require

T2 is not merely harder; it is outside the frontier the comparator's own grid reached. Across all
**150** cooccurrence rows in the 0.15.0 artifact (ten seeds by fifteen configurations), the best F1
anywhere is **0.972973**. Precision 1.000000 appears in eight rows, all `window 30 / floor 10`, and
all eight pay for it in recall: **0.611111–0.888889**, or eleven to sixteen of the eighteen gold
pairs. No configuration serves all eighteen at precision 1.000000; the best full-recall point
carries one to five false pairs. T2 would require eighteen served pairs, all true — a point no count
configuration in the grid achieved. A T2 FAIL would therefore not distinguish "provenance is the
wrong lever" from "a count floor cannot express the band".

T1 keeps the criterion the build can plausibly meet and keeps the pre-registered threshold
(0.412011, fixed from the 0.15.0 artifact, not the block). The comparator is still reported per
seed, so the loss stays visible; what T1 gives up is the sentence that a PASS beats the baseline,
and that sentence has to be cut from the term sheet rather than left to be read into the result.

## What the build is under this decision

`_build_predictions` only:

- **Admission.** A relation is a candidate only when its unordered pair is in the co-occurrence
  table at count `>= F`. `F` is a fixed integer, not swept on the judged block.
- **Ranking.** One list, sorted by temporal count with the current tie-breaks.
- **Served.** `min(MAX_PREDICTIONS, M)`, where `M` is the number admitted. `MAX_PREDICTIONS` stays
  112; `transition_budget`, `cooccurrence_budget` and the backfill are deleted.
- **Version.** 0.16.0 in `organica/__init__.py`, `pyproject.toml` and `CITATION.cff`, a CHANGELOG
  entry, and `python -m benchmarks.engine_pin`.

## The count-separation preflight (the stop condition before any grant)

The arithmetic assumes a floor can leave a full-recall set in the band. That is an assumption, not
a measurement, and it is the one the build must test before it spends a seed.

**Data.** The committed K1 seeds `20261023`–`20261032`, the 0.15.0 build, the K1 world, at the
cycle the endpoint scores. No fresh seed is drawn, no campaign cell runs, and the preflight produces
no result; anything it writes is marked not-a-result.

**Measurement.** For every seed, take the co-occurrence count of each of the eighteen gold pairs and
of every pair the temporal path would admit. For each integer floor `F >= 1`, `M_s(F)` is the number
of admitted pairs whose count reaches `F`.

**Pass rule (fixed before the measurement).** Let `F` be the largest integer that keeps every gold
pair on every seed (recall 1.000). The preflight passes only if `18 <= M_s(F) <= 69` on every seed.
That `F` is written into the grant before the block and cannot change mid-block.

**Fail rule.** If the largest recall-preserving floor leaves more than 69 pairs on any seed, STOP.
No grant, no cell. Record the ordering as the constraint, and do not: tune `F` on the fresh block,
switch to T2, or widen the bar. The next work is a design question about ordering — a window, an
entropy rank, or a different candidate space — not another run. Rule 25(d) applies: when precision
does not improve with the budget, the defect is the candidate space, not the budget.

**Why it is a stop condition, not a criterion.** If no floor can express the band, every arm is
decided by arithmetic before the mechanism is read; a result would be a count, not evidence.

**Implementation.** `benchmarks/count_separation_preflight.py` fixes the rule above in code: the
floor is the minimum gold co-occurrence count across the seeds, `M_s(F)` counts the pairs the
temporal path admits (temporal count at or above the engine's `PREDICTION_MIN_COUNT`) whose
co-occurrence count reaches `F`, and `--self-test` proves the 18 and 69 boundaries, the failure at
70, the floorless gold set, the temporal gate and the global floor on synthetic fixtures. A
seed-free smoke test drives the collection path itself over a hand-built eighteen-pair event
stream, and `--run` prints a flushed per-seed heartbeat every 50 cycles so a ten-seed run is
visibly alive. Every report also prints, per seed, the gold pairs' minimum co-occurrence count
and the `M(F)` step curve — at each floor at or below `F*`, both the admitted pair count and the
directed admitted count — so the floor written into the grant can carry an explicit fresh-seed
margin below the pooled minimum rather than sitting exactly on it. Where the directed count
exceeds `MAX_PREDICTIONS` (112) the seed is marked `CAP BINDS` and the headline names the
binding seeds as `PASS OF THE BAND ONLY` rather than `PASS`, because the engine would truncate
before serving `M`; that is not a floor-only result. The diagnostics do not change the pass
rule; the band rule and the PASS/FAIL exit code are unchanged. `--run` is gated mechanically:
it refuses with exit code 2 unless a recorded owner decision chooses the (a)+T1 build, and the
check runs before the engine starts, so a missing decision cannot spend a seed.

**Where the record lives.** `docs/constraint_decisions/DECISION-COOCCURRENCE-BUILD.json`. That
directory is where the owner's constraint decisions live, but the two records in it are a
different object: a `constraint_decision` disposes of a **registered** constraint and must cite
its `registration` and a `result`, and `benchmarks/bottleneck_map.py` refuses a cited decision
without an `id` or whose `result` its ledger row does not carry. This decision precedes
registration, so there is no result to cite and reusing that schema would mean writing
references that do not exist. The common fields are kept — a `kind`, an ISO `date`, and
`decided_by "owner"` — and the file names its own kind, `build_decision`.

**The record is written.** It carries exactly these five fields, with the values the owner chose:

```json
{
  "kind": "build_decision",
  "date": "2026-11-19",
  "decided_by": "owner",
  "allocation_law": "a",
  "term_sheet": "T1"
}
```

The gate reads those five fields and nothing else, so an `id`, a rationale or a citation is not
required and cannot make a record inadmissible. Only **(a)+T1** unlocks `--run`; a record that
chooses (b) or T2 is a valid record and is refused as inapplicable, because the preflight
measures the (a)+T1 build.

`--run` is the only mode that touches the committed seeds; it draws no fresh seed, runs no
campaign cell and stamps every report `NOT A RESULT`. It ran to a report once, on 2026-11-19, under
the recorded decision; the earlier accidental invocation had been killed at 120 s before printing,
and both scratch databases were removed.

## The preflight, run (2026-11-19)

The owner recorded (a)+T1, and the stop condition was read once: the ten committed K1 seeds on the
0.15.0 engine, one report. **This is not a result** — no fresh seed was drawn, no campaign cell ran
and the scratch database was removed. The output, verbatim:

```text
largest recall-preserving floor: 44
  seed 20261023: M=19, gold min=47, directed admitted=38/112
    M(F)/directed(F): 1:24/48  25:23/46  29:22/44  35:21/42  38:20/40  41:19/38  44:19/38
  seed 20261024: M=20, gold min=54, directed admitted=40/112
    M(F)/directed(F): 1:24/48  34:23/46  35:22/44  37:21/42  41:20/40  44:20/40
  seed 20261025: M=19, gold min=53, directed admitted=38/112
    M(F)/directed(F): 1:24/48  31:23/46  39:22/44  40:21/42  44:19/38
  seed 20261026: M=19, gold min=46, directed admitted=38/112
    M(F)/directed(F): 1:24/48  32:23/46  35:22/44  38:20/40  39:19/38  44:19/38
  seed 20261027: M=21, gold min=53, directed admitted=42/112
    M(F)/directed(F): 1:24/48  26:23/46  31:22/44  43:21/42  44:21/42
  seed 20261028: M=21, gold min=44, directed admitted=42/112
    M(F)/directed(F): 1:24/48  37:23/46  40:22/44  42:21/42  44:21/42
  seed 20261029: M=18, gold min=55, directed admitted=36/112
    M(F)/directed(F): 1:24/48  37:23/46  38:22/44  40:21/42  41:19/38  42:18/36  44:18/36
  seed 20261030: M=20, gold min=48, directed admitted=40/112
    M(F)/directed(F): 1:24/48  33:23/46  36:22/44  39:21/42  44:20/40
  seed 20261031: M=19, gold min=50, directed admitted=38/112
    M(F)/directed(F): 1:24/48  35:23/46  37:21/42  39:20/40  44:19/38
  seed 20261032: M=20, gold min=50, directed admitted=40/112
    M(F)/directed(F): 1:24/48  35:23/46  39:22/44  43:21/42  44:20/40
PASS: 18 <= M_s(F*) <= 69 on every seed.
```

**Reading.** `F* = 44`, the pooled gold minimum, which seed `20261028` attains exactly; at that floor
every seed serves 18–21 pairs, so the band passes with no seed near its upper edge. The 112 cap does
not bind — directed admission is 36–42 — so the headline is a plain PASS rather than a PASS of the
band only. The slack has a measured cause: the co-occurrence table holds **24** pairs and all 24 are
on the temporal path, against **120** unordered temporal pairs, so `M` cannot exceed 24 at any floor
on this world family and the band's upper half is unreachable here. So the band could not fail on this
world family: `F*` is by definition the floor at which all eighteen gold pairs are retained, which
forces `M >= 18`, and only 24 pairs co-occur at all, which caps `M` at 24 — the PASS is arithmetic,
not evidence that the 18–69 band was at risk. The floor's only live hazard is
recall: a gold pair below `F*` on a fresh seed is dropped. The curve shows the margin a grant could
buy — at `F = 35` the same ten seeds serve 21–23 pairs, still inside the band — but the floor is the
grant's to fix, not this memo's.

## Grant terms

These are the terms a dated grant would carry **if** the preflight passes and the owner registers.
They are not in force; this memo issues nothing.

| Item | Term |
|---|---|
| Engine | 0.16.0, CHANGELOG entry, `engine_pin` re-pin |
| Change | `_build_predictions` only: admission by support at `F`; one ranked list; no partition or backfill |
| Floor | `F = 35`, fixed in the grant of 2026-11-20 for every seed, never changed mid-block |
| Seeds | ten fresh, reserved at grant time after a scan of `docs/`; disjoint from all consumed seeds; the committed ten are used only by the preflight and the reproduction control, and no fresh seed is spent on either |
| Cells | 20 = 10 treatment (0.16.0 × fresh seeds) + 10 reproduction (0.15.0 × committed seeds); 300 cycles; 8 workers |
| Readout | paired F1, 0.16.0 minus 0.15.0, 10,000 bootstrap replicates, 98.33% intervals; precision and recall beside it; the strongest-of-grid comparator reported per seed |
| Thresholds | the six ledger keys, fixed from 0.15.0: `baseline_gap -0.623961`, `pass_min_improvement 0.10`, `pass_max_k1_abs_change 0.05`, `fail_below_improvement 0.05`, `inconclusive_min_improvement 0.05`, `inconclusive_max_improvement 0.10` |
| Guards | recall `>= 0.95` on every seed and no gold pair dropped; K2 and K3 absolute change `<= 0.05` |
| Liveness | every seed serves fewer than 70 pairs; the floor removed at least one candidate; all eighteen gold pairs retained; otherwise VOID |
| Claim ceiling | T1: an improvement over 0.15.0 by at least 0.10 F1; not a win over the comparator |
| Execution | one block, no re-execution, no mid-block law switch |

**Signed 2026-11-20.** [`COOCCURRENCE-A-T1-REGISTRATION-DRAFT.md`](COOCCURRENCE-A-T1-REGISTRATION-DRAFT.md)
carries the signed text: the registration object, the grant object at `F = 35`, the ledger row and
the scanned seed block, with `F = 44` and `F = 35` side by side and the reason 35 was chosen. The
two objects are now files and the ledger row is `in-test`; no cell has run.

## The two outcomes, two decisions

- **Preflight passes** → register and grant. **A PASS confirms the counts and the liveness of the
  floor; it cannot show that admission by support improved the engine.** On this world family the
  improvement is fixed by arithmetic before a cell runs — `F1 = 36/(M+18)` at full recall is +0.545
  to +0.611 over the 0.15.0 gap for any `M` in 18–24 — so the information a PASS carries is that the
  floor retains all eighteen gold pairs on seeds it was not tuned on, that every fresh seed serves
  fewer than 70 pairs, and that the reproduction arm still returns `-0.623961`. Read it as an
  admission-and-liveness confirmation and say only that. **A FAIL is the outcome that carries new
  information**: it names a count, a guard or a drift the committed ten did not show. A fresh
  seed's tightest gold pair below `F`, or a seed serving 70 pairs or more, is a fact about the
  floor's margin — the recall hazard the preflight could not rule out. A K2 or K3 paired difference
  moving by more than 0.05 is not: it is a change in the guard families, and it says the admission
  rule reached beyond the endpoint the block is about.
- **Preflight fails** → stop. No cell. The ordering is the constraint; the next work is a design
  question, not another measurement of the same build.

## What this memo does not do

- It issues no grant itself: the registration, the ledger row, the seed reservation and the grant
  are dated records the owner signed on 2026-11-20, and this page states the terms they carry.
- It runs no cell, opens no database and writes no research result.
- It does not re-open K1, re-score the 0.9.0 campaign or the 0.15.0 replication.
- It does not claim T2 is unachievable in principle — only that no count configuration in the
  committed grid reached it, which is what a term sheet has to go on.

**Reproduce the frontier figures.** `docs/phase_k_results_0.15.0.json`, `per_model_detail`, K1
rows: 10 seeds × 15 configurations = 150 rows; maximum `primary` 0.972973; the eight rows with
`precision` 1.000000 are `window 30 / floor 10` with `recall` 0.611111-0.888889.
