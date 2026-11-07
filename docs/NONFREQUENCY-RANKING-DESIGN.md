# Ranking by something other than frequency: a design record, not an explanation (2026-11-07)

**Status: an untested hypothesis. No cell, no seed, no threshold, no bar, no claim.**
Every number is in `docs/nonfrequency_ranking_design.json`.

## 1. The non-inference to state first

The Gate 13 measurements established that the world's edges were **present** in memory and that
the engine's own count ordering did not surface them at its cap. They did not vary the **ordering
basis**: every rule tested was frequency-derived. So the finding is about a family of orderings,
not about ordering as such.

The **0.3438** precision maximum belongs to the two frequency-based allocation rules tested in one
world family. It is not an information-theoretic bound, and quoting it as "the ceiling" would close
a design space that was never measured.

The density record (`docs/WORLD-DENSITY-DESIGN.md`) varies **eligibility** — intra-cell rows are
made ineligible — at the same ordering. This record varies **ordering** at the same eligibility, so
every row stays eligible, including the intra-cell rows the density treatment excludes. Neither
record subsumes the other, and each can come back null without implicating the other.

## 2. What is actually being changed

- **Control — global count-ranked top-k.** The engine's own selection: rank every candidate by count
  and take the top k at the frozen cap.
- **Treatment — diversity-first ordering.** Greedy max-marginal-coverage over the source side of the
  pair: for each of the k slots, take the eligible candidate whose left-hand tag has the fewest
  already-selected outgoing edges. Ties break on count, then on a deterministic stable key.

Identical by construction: eligibility (all rows), the cap, the scoring function, the admission
window, the world family, the seeds per cell, the exposure scheme and the horizon. **Only the order
in which eligible candidates fill the budget differs.**

**Why this is not a frequency-derived variant.** The sort key's primary term counts *already-selected*
edges sharing a source, not the candidate's own frequency; frequency enters only as a tie-break, and
that is disclosed rather than hidden. A smoothed count, a per-source count, or a normalized count
would all be members of the family this record already treats as measured out.

## 3. Why diversity, and what it predicts

The measured defect is **spread**: the world's **112** edges are spread across the source side, not
clustered at the top of any count ordering. The top **20** recovers **0–1**, the top **40** recovers
**1–8**, and the top **320** — about **16×** the engine's budget — recovers **106–109**. A count
ordering spends the whole budget where the count mass already is; a diversity ordering spends it
across sources.

This is a different intervention from Gate 13's per-source **allocation** test. That test raised the
budget into the hundreds of edges and asked whether allocating it per source helps; this record keeps
the engine's own cap and asks whether the order helps.

## 4. Predictions, registered before any cell

1. The **control** reproduces the Gate 13 profile at cap 20. That is a control that must reproduce,
   not a result.
2. **Delta = treated − control** in world-edge coverage is positive at the lowest density and declines
   as density rises. At density 1 every candidate is a true edge, the two arms must select the same
   rows, and Delta must be **0**; a non-zero Delta there is a harness defect.
3. The arms' selected sets differ at the lowest density. If they are identical, the manipulation did
   not occur.

## 5. Falsifiers, named in advance

- **Flat** Delta across both caps and every density level: the ordering basis is not the lever, and
  the line closes as stated in §8.
- **Rising** Delta with density: the mechanism story is wrong, and something other than spreading the
  budget is being measured.
- Non-zero Delta at density 1: the arms are not identical where they must be.
- Identical selections at every level: an unrun experiment, not a null result.

## 6. The architectural decision, from both poles

- **Positive:** the count order is replaced by a diversity-based order in the next engine version,
  recorded as a cognition change. Phase A froze the selection primitives, `v0.9.0` is the archival
  reference and `0.12.0` is immutable, so this is an in-process arm and a recorded decision, never an
  edit to the frozen engine. The change is to *which eligible candidate occupies the budget*.
- **Negative:** the ordering basis is not the constraint. The line then moves to the candidate space —
  which rows exist to be ordered at all — and this record is **not** followed by another ordering
  variant. That is the stop, not a prompt for a third design.

**Neither pole licenses a behavioural claim.** Coverage is not behavior; the second half of the
selection row in `docs/BOTTLENECK-MAP.md` stays untested here.

## 7. Endpoints

- **Presence ceiling:** the world's edges present in memory over the world's edges, which must be
  **1.0** or the cell tests memory rather than ranking.
- **Coverage** at cap **20** and cap **40**, each reported with its denominator.
- **Precision** beside rho_rank, and bounded by it: precision cannot exceed the true-edge share of the
  population the arm selected from.
- **Overlap** between the arms' selected sets, which is the harness-validity check, not a result.
- **Recovery distribution** across budgets — a distribution, never the rank of the first edge.
- **Delta** with a paired interval on the difference.

## 8. Stop condition

Scope is fixed before the run: one world family, **16** tags, caps **20** and **40**, the density
levels declared in the density record, seeds fixed by a pre-registration with fresh seeds, one
horizon, one exposure scheme.

The line stops when either outcome arrives:

- **both** caps and **every** density level return flat Delta — then ordering is closed, and the next
  move is a separate design record about the candidate space or the readout, not a third ordering;
- the pre-registered adoption bar is met — then the decision in §6 is recorded and the engine change
  is specified separately.

**No ordering variant may be added to this record after the run.** It may be fixed if it is found
wrong; it may not grow.

## 9. What this record does not do

It allocates nothing: **0 seeds, 0 cells, 0 thresholds, 0 bars**. Bars and seeds are fixed in a
pre-registration with fresh seeds, per `docs/DECAY-TUNING-CYCLE.md`.

It does not change the bottleneck map. That artifact carries claim status and keeps **exactly one**
specified experiment, the density interaction; this is a second design record, not a second map row,
and a test asserts the map still has one.

It does not authorise an engine edit, and it does not name schema fields as facts: "source side" and
"left-hand tag" describe a pair's direction, and the pre-registration must confirm them against the
frozen schema rather than assume them.
