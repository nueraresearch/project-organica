# The co-occurrence selection build: scope

**Status: scoped, not started. No cell, no seed, no ledger row, no grant.**

The pressure test of `CONSTRAINT-ASSERTION-PROVENANCE-1`
([`ASSERTION-PROVENANCE-PRESSURE-TEST.md`](ASSERTION-PROVENANCE-PRESSURE-TEST.md)) withdrew the
readout-side version: the rule is a label the engine already computes, and the strongest simple
baseline already applies it and wins by more than half an F1 point. What the test did establish is
that the information is present and the engine's readout discards it. This page scopes the build
that follows from that — inside `_build_predictions`, not in a scorer — and states when it stops.

## What changes, and where

`organica/sleep_extraction.py`, `_build_predictions` (line 353). Today a relation becomes a
prediction candidate when its temporal count reaches `PREDICTION_MIN_COUNT`; the co-occurrence test
runs *afterwards* and only labels and buckets the row:

```python
is_cooc = tuple(sorted([tag_from, tag_to])) in cooc_pairs
...
if is_cooc:
    cooccurrences.append(cand)
else:
    transitions.append(cand)
```

The build moves that test into **admission**: a relation is a candidate only if its unordered pair
is in the co-occurrence graph at a count floor fixed before the block. The floor is declared in the
preregistration, not swept on the judged block: if it is calibrated at all, the calibration block is
a separate, declared block that is not being judged (rule 19). Its effect on the served count is set
out under the allocation law below.

## Why it is not a one-line filter

Allocation is stratified: `budget // 2` transitions first, then cooccurrences, then a backfill from
further transitions. That law assumes two populations exist, and the presence gates the project
already runs test the assumption (`transitions + cooccurrences = 112`, `transitions >= 56`,
`cooccurrences <= 56`). If admission requires within-event support, the transition population
empties, `transitions >= 56` becomes unsatisfiable, and every full window is VOID on its own gate.

So the build has to re-derive the allocation law before the code lands. That is a cognition change
under rule 2 — which structures compete and how the layers select candidates — not a substrate
tweak, so it needs a recorded decision first. The two candidate laws, their effect on the
112-seat budget and their effect on the presence gates are set out below. The preregistration must
choose one before the build starts. It may not be chosen after seeing a result, and it may not be
switched mid-block.

## The allocation law: two options

Both laws inherit one arithmetic fact that neither can tune away, so it is stated first.

### The budget arithmetic neither option escapes

The endpoint is paired K1 F1 on a fresh block, and on 0.15.0 every seed recalls all eighteen gold
pairs (recall 1.000, false negatives 0). With recall held at 1.000, F1 depends on precision alone:
`F1 = 2P/(1+P)` with `P = 18/N` for `N` distinct served pairs. The registered bar is 0.412011, so
the arm needs `P >= 0.412011/(2 - 0.412011) = 0.259455`, which is `N <= 69.376` — **at most 69
served pairs**.

| Served pairs | Precision | F1 | Against the 0.412011 bar |
|---|---|---|---|
| 19-23 (the comparator's best point) | 0.782609-0.947368 | 0.878049-0.972973 | pass, far above |
| 56 | 0.321429 | 0.486486 | pass |
| 69 | 0.260870 | 0.413793 | pass, by 0.001782 |
| 70 | 0.257143 | 0.409091 | fail |
| 95-99 (0.15.0 Organica) | 0.181818-0.189474 | 0.307692-0.318584 | fail |
| 112 | 0.160714 | 0.276923 | fail |

**A law that fills all 112 seats fails by arithmetic, whatever its split.** The 112-seat window is
a ceiling on what may be served, not a quota to spend. What the choice actually decides is what
sets the served count — and therefore whether the window binds at all.

There is a second consequence, and it is a term-sheet problem rather than an allocation one. The
comparator serves 19-23 pairs at F1 0.878049-0.972973. An arm at 69 pairs passes the bar at
0.413793 and still trails the comparator by 0.464256 in F1 at its weakest seed. The bar was fixed
against Organica's own mean, not against the model the build says it must beat, so a PASS between
24 and 69 served pairs would certify a change that still loses. The preregistration has to say
which of the two it is testing; the choice of allocation law does not settle that, and the two
term sheets that do are set out below.

### Option (a): drop the partition, rank by count

The law: admit a relation only when its unordered pair is in the co-occurrence table at count
`>= F`; sort the admitted candidates by temporal count, tie-broken as today; serve the first
`min(MAX_PREDICTIONS, M)`, where `M` is the number admitted.

The code shape deletes `transition_budget`, `cooccurrence_budget` and the backfill, because those
three exist only to divide a window that is now one ranked list:

```python
candidates = sorted(admitted, key=lambda p: (-p.evidence["temporal_count"], p.source, p.target))
return candidates[:self.MAX_PREDICTIONS]
```

`MAX_PREDICTIONS` stays 112; nothing in the build changes the constant.

**Effect on the 112-seat budget.** The cap stops binding as soon as `M < 112`, which it must be for
the arm to pass. `F` is the effective budget: the law reads "serve every supported pair at
`count >= F`, up to 112", and the pass condition is `18 <= M <= 69` on every seed. A floor that
leaves `M > 69` fails by the table above; a floor that leaves `M < 18` cannot recall every gold
pair and fails the recall guard.

**Effect on the presence gates.** `transitions + cooccurrences = 112`, `transitions >= 56` and
`cooccurrences <= 56` are keyed to the two buckets this law deletes. Under admission by support
every admitted row carries `is_cooccurrence: true` (the build does not change the label), so
`transitions = 0` and `cooccurrences = M`: the first two gates fail on every window, and the sum
gate fails whenever `M < 112`, which is every window that could pass. The gates cannot be carried
forward, and a renamed copy is a different gate (rule 25). Under (a) the presence blocks'
full-window fixtures do not exist at 0.16.0, and the build's liveness gate has to be re-expressed
in terms of `M` and the retained set, not in terms of two non-empty populations.

**What a fail means.** One population, one ranking, one lever: a fail is attributable to `F`
(too low, `M > 69`) or to the recall guard (too high), and the preregistration says which was
read. This is the option that can attribute its own failure.

**What the floor needs.** The artifact cannot calibrate `F`. The comparator's winning
configurations are windowed (30 or 75 cycles) and the artifact records their results, not the
engine's co-occurrence counts.
`_load_cooccurrences` reads the whole `cooccurrences` table — `(tag_a, tag_b, count)`, no
timestamp, no window — at `count >= 1`, so the engine's supported set at a floor is cumulative over
the run and is not the comparator's 19-23. `F` must therefore be declared in the preregistration or
calibrated on a declared calibration block that is not the judged block (rule 19). A declared
floor chosen from theory alone is permissible but may leave `M > 69`; the preregistration must say
in advance that this is a FAIL, not a licence to re-tune. A calibration block consumes seeds, so
it is a cost of the option, not a detail.

### Option (b): keep a partition

The 56/56 law cannot pass: 56 transitions plus 56 cooccurrences is 112 served pairs, F1 0.276923.
Keeping a partition therefore means changing the quotas, not just the buckets — to keep two
populations and pass, `q1 + q2 <= 69` (34 + 35, or 23 + 23 to match the comparator's scale), or one
quota must be allowed to run short with no backfill. Whichever is chosen, it is a different law
from the one shipping today and has to be written down before the grant.

Three axes have been named for the partition, and they are not interchangeable:

| Axis | Available today? | Both buckets populated? | Cost |
|---|---|---|---|
| Target entropy | yes — computed per source in `_build_predictions` | yes whenever `M >= 2` | none; a 34/35 split changes which pairs are served |
| Schema congruence | yes — `_current_prior_schemas` | no — a bucket can be empty on any cycle with no stable schema | the liveness gate goes VOID on those cycles, and the earned-evidence contract lets a schema reorder, never admit |
| Recency | no — `cooccurrences` carries `(tag_a, tag_b, count)` and no timestamp | — | a new stored field is a substrate change with its own equivalence proof (rule 5), or a per-cycle event scan; either leaves the one-variable claim |

**Effect on the 112-seat budget.** The partition decides *which* pairs are served; the quotas
decide how many. With quotas summing to 69 the window is 43 seats under-filled on every cycle, and
`MAX_PREDICTIONS` stops describing the served set — it is the same ceiling as in (a), reached by a
different route.

**Effect on the presence gates.** The existing names cannot certify the new buckets. At 0.16.0
every admitted row is co-occurrence-labelled, so `transitions >= 56` is unsatisfiable under any
partition; the gates must be renamed and re-derived from the chosen axis, and the presence
campaign's B5 record certifies a law whose buckets are labelled transitions and cooccurrences and
whose window fills to 112 — the 0.15.0 law, not this one. Renaming is not enough: the new gate has
to be able to fail on the new axis and has to be shown firing before any criterion is read.

**What a fail means.** Not attributable to one variable. A fail can be the axis, the quotas or the
floor, and the preregistration cannot say in advance which one it learned about.

### The choice, side by side

| | (a) drop the partition | (b) keep one |
|---|---|---|
| Served count set by | the floor `F` | the quotas `q1 + q2` |
| The 112 cap | a ceiling that must not bind | a ceiling the quotas leave partly empty |
| Variables changed | one (admission rule, with its floor) | two (admission, plus the axis and quotas) |
| Presence gates | none survive; a new gate on `M` and the retained set | none survive; a new gate per bucket, shown firing |
| What a fail attributes to | `F`, or the recall guard | the axis, the quota or the floor |
| Pre-build requirement | declare or calibrate `F` outside the judged block | show both buckets populated on the axis, and fix the quotas |
| Against the comparator | the same model, unwindowed; F1 compared on the same terms | the same, plus a split the comparator does not make |

Both options keep `MAX_PREDICTIONS = 112`, change `organica/sleep_extraction.py` only, need the
0.16.0 bump and a re-pin, and leave the term sheet's endpoint, comparator, recall guard and
negative control in place. The exception is (b) on recency, which adds a substrate field and is no
longer confined to `_build_predictions`. Neither option is registered by this page, and neither
runs a cell. The choice is the owner's — action 60 in the manual.

## The version (rule 12)

An engine file changes, so the package must name a different commit:

| File | Now | Build |
|---|---|---|
| `organica/__init__.py` | `__version__ = "0.15.0"` (line 25) | `0.16.0` |
| `pyproject.toml` | `version = "0.15.0"` (line 9) | `0.16.0` |
| `CITATION.cff` | `version: 0.15.0` (line 14) | `0.16.0` |
| `CHANGELOG.md` | — | a `## 0.16.0 (unreleased)` entry naming this change |

Then `python -m benchmarks.engine_pin` re-pins, and `python -m benchmarks.engine_pin --check`
verifies. The pin holds a SHA-256 for all fourteen modules and the version, so a changed module
without a bump fails by construction — the bump is not bookkeeping, it is the mechanism.

A tag is the owner's decision, not the build's (rule 10 allows an untagged `unreleased` heading).

## The preregistration: a term sheet, not a registration

These are the terms the build inherits from the withdrawn draft, restated subject-side. They are
**not in force**: the owner registers the constraint and issues a dated grant, and the ledger row
is created then, not now.

- **Hypothesis (subject-side).** Admitting only within-event-supported pairs makes the engine's own
  assertions precise, without a filter in the scorer.
- **Endpoint.** Paired K1 F1, 0.15.0 against 0.16.0 on a fresh seed block, with its 98.33%
  interval; precision and recall reported beside it.
- **Comparator.** Strongest-of-grid, **including the cooccurrence model**. This is the point of the
  build: if the engine cannot beat the baseline it internalizes, it has gained nothing over calling
  it.
- **Recall guard, now live.** A gold pair whose only evidence is temporal is dropped by admission.
  That is the firing condition the readout version lacked. It is attributable on this world because
  the guard only fires when a gold pair reaches the engine through the temporal path alone, and the
  artifact shows none currently needs that path — so a drop in the build is a property of the
  change, not of the world.
- **Liveness gate.** The chosen allocation law must yield both populations non-empty on at least one
  cycle of the block; if law (b) leaves one empty, the law is degenerate and the arm is VOID before
  any criterion is read.
- **Negative control.** The unchanged 0.15.0 build must reproduce the committed K1 figures exactly.
  If the harness has moved, nothing else can be read.
- **Seed block.** Fresh, reserved at grant time. The Phase K ten are spent; reusing them would
  reanalyse a known endpoint.
- **Threshold values.** Fixed at registration from the 0.15.0 artifact, not computed from the 0.16.0
  run (rule 19).

## The bar versus the comparator: two term sheets

The term sheet above states an endpoint (0.16.0 against 0.15.0), a bar (0.412011) and a comparator
the build says it must beat. Those three do not fit together, and the gap is arithmetic:

- the bar is met at up to 69 served pairs (the table in the allocation section);
- the comparator serves 19-23 pairs at F1 0.878049-0.972973;
- so an arm can PASS at 24-69 pairs and still trail the comparator by 0.464256 at its weakest seed.

A PASS therefore does not certify the sentence the build exists to test. Two term sheets settle it,
and they are different claims, not two estimates of one claim.

### T1 — keep the registered bar; the comparator is reported

**Criterion.** PASS is the registered one: the 0.16.0 mean F1 reaches 0.412011 (a 0.10 improvement
on the 0.15.0 gap), the recall guard holds and the liveness gate passed. The comparator is a
reported column beside the endpoint, per seed, with no threshold attached.

**What a PASS claims.** That the engine's own assertions improved on its previous build by at least
0.10 F1. It explicitly does not claim the engine beats the strongest simple baseline, and the claim
ceiling must say so in those words, because a PASS at 69 pairs (0.413793) is still 0.464256 below
the comparator's weakest seed.

**What it costs.** No threshold moves: 0.412011 is already fixed from the 0.15.0 artifact. But the
Comparator bullet above — "if the engine cannot beat the baseline it internalizes, it has gained
nothing over calling it" — has to be cut, or T1 is incoherent. The build would then be testing
"does admission by support improve the engine", not "can the engine internalize the comparison".

**Gate.** Every seed must serve fewer than 70 pairs. At 70 a seed's F1 is at most 0.409091, below
the bar, so that seed's outcome is arithmetic rather than evidence; a block that breaches the bound
is VOID, not a fail.

### T2 — make the comparator the criterion

**Criterion.** The endpoint's difference becomes 0.16.0 minus each seed's strongest-of-grid
comparator; PASS requires the 98.33% interval of that paired difference to be wholly at or above
zero, with the recall guard and liveness gate passing. The 0.15.0 build is retained as the negative
control, not as the baseline.

**What a PASS claims.** That the engine's own assertions beat the model it internalizes — the
sentence the build exists to test, at the standard the project uses for a direction (an interval
that excludes zero).

**What it implies about the served count.** Beat-the-comparator needs almost exactly the eighteen
gold pairs. At 19 pairs the best possible F1 is 0.972973, which is the comparator's best seed, so
the difference there is at best zero; at 18 pairs F1 is 1.000 and every per-seed difference is
positive. At 23 pairs the maximum F1 is 0.878049, equal to the comparator's weakest seed, so 24
pairs (F1 at most 0.857143) cannot beat the comparator at all.

**What the frontier shows.** Across all **150** cooccurrence rows in the 0.15.0 artifact — ten seeds
by fifteen configurations — the best F1 anywhere is **0.972973**. Precision 1.000000 appears in
eight rows, all of them `window 30 / floor 10`, and every one pays for it in recall: **0.611111 to
0.888889**, or eleven to sixteen of the eighteen gold pairs. No configuration serves all eighteen at
precision 1.000000; the best full-recall point carries one to five false pairs. T2 would therefore
require a point the tuned count ordering never reached: eighteen served pairs, all true. That is not
merely unobserved at the engine's counts — it is outside the frontier the comparator's own grid
achieved, so a T2 FAIL could not distinguish "provenance is the wrong lever" from "a count floor
cannot express the band".

**What it costs.** A different endpoint and a re-registered threshold on a different quantity. The
six-key schema can carry it — `baseline_gap = -0.623961` and `pass_min_improvement = 0.623961` for
parity — but the operative criterion is the interval, so the point value is a floor rather than the
bar, and the fail and inconclusive bands have to be written against it rather than copied from the
0.412011 sheet. The floor also has to leave 18-19 pairs in practice on every seed, a much narrower
target than either allocation option otherwise needs.

**Gate.** Every seed's served count must be 18-23. Below 18 recall fails; at 24 a seed's F1 is at
most 0.857143, below the comparator's weakest point, so that seed cannot contribute a win. A block
outside the band is VOID rather than a fail: the count, not the mechanism, would decide it. Within
the band, 18 pairs beats the comparator on every seed; 19 ties its best seed and must win on the
rest; from 20 up at least one seed's difference is negative.

### The choice

| | T1 | T2 |
|---|---|---|
| PASS compares | 0.16.0 against 0.15.0 | 0.16.0 against the strongest-of-grid |
| Bar | 0.412011, already fixed | paired difference interval at or above zero |
| Claim a PASS supports | the engine improved; not that it beats the baseline | the engine beats the model it internalizes |
| Served pairs | 18-69 | 18-19 in practice (18 beats the best seed outright) |
| A 24-69 pair arm | can PASS | cannot PASS |
| Re-registration | none | new endpoint and threshold values |
| The comparator bullet | must be cut | becomes the criterion |

Neither term sheet is registered here, and neither substitutes for the allocation choice: T1 works
with (a) or (b) unchanged, while T2 constrains the floor to leave 18-19 pairs and therefore also
constrains (b)'s quotas. If the owner wants the build's own sentence to be the thing tested, T2 is
the only term sheet that does it; if the owner wants the improvement claim only, T1 is honest
provided the comparator bullet is removed. No cell runs under either.

**Drafted:** [`COOCCURRENCE-A-T1-MEMO.md`](COOCCURRENCE-A-T1-MEMO.md) recommends (a)+T1, states the
grant terms a registration would carry and makes the count-separation preflight a stop condition.
It registers nothing.

## Stop condition (rule 23c)

The build is done when all five hold, and then no feature may be added to it — only defects fixed:

1. the pin matches a 0.16.0 engine and `engine_pin --check` passes;
2. the full suite is green and the test count is rewritten;
3. the unchanged-build control reproduces the committed 0.15.0 K1 numbers;
4. the recall guard and the liveness gate both run and are shown capable of firing;
5. the build is recorded in the CHANGELOG as one change with one variable.

## What this does not do

- It runs no cell, reserves no seed, allocates no grant and creates no ledger row.
- It does not re-open K1, re-score the 0.9.0 campaign or the 0.15.0 replication.
- It does not claim within-event support is sufficient — a baseline already shows it is, and the
  build's job is to make the engine, not the scorer, achieve it.
- It does not decide the allocation law. That decision is named above and is the owner's.
