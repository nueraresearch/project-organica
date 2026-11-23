# Interpretation note: the asserted-but-never-served edges

Derived from `docs/presence_unexplained_edges.json` by `python -m benchmarks.presence_unexplained_edges --write`. Do not edit by hand.

**An interpretation of a committed record, not a second measurement.** It re-reads the edges, their ranks and their bands; it runs no cell and re-scores no verdict.

## The set

Of the **247** asserted world edges, **221** were served at least once and **26** never entered a served window (10.5%). Every unexplained edge is a transition. Their best recorded rank runs **22-127** -- a position in the ceiling call's list, where transitions precede cooccurrences, not an admission position. Per seed: 20611601: 4, 20611602: 4, 20611603: 9, 20611604: 2, 20611605: 3, 20611606: 4. **10** of the 26 sit inside the cap (rank <= 40); **0** sit inside the transitions actually served in the cycle that ranked them; the closest in-cap miss is **2** rank(s) short. By band: 1-20: 0, 21-40: 10, 41-80: 10, 81-112: 4, 113+: 2.

## What it licenses

- **The assertion step is not lossless, and it is not the served union.** 26 of 247 asserted world edges were never served, so `A_W` contains edges the served window never carried and the `S_ever`-to-`A_W` step cannot be read as a pure conversion loss.
- **The remainder is small and second-order.** 10.5% of asserted edges, against 221 that were served.
- **It is not a late-window artefact.** The served asserted edges have a per-seed median last-served cycle of 116, 117, 119, 116, 119, 117, against a last cycle of 120, so the unexplained set is not merely an early cohort.
- **'In cap' is not 'inside the budget'.** 10 sit inside the cap, but 0 sat inside the transitions actually served in the cycle that ranked them; the cap bound that matters here is the 20-slot transition allocation, not 40.
- **It is a location, not a cause.** It names which edges, at what best rank, in which band; it identifies no rule that excluded them and no mechanism that produced the assertion.

## What it does not license

- **Not a mechanism, and not a defect in the admission rule.** The recorded rank is a block position in the ceiling call's list, not an admission position; 0 of the 26 ranked inside the transitions served in their best cycle, so a claim that the ranking skipped them cannot be made from rank alone.
- **Not a claim that serving them would have changed `A_W`.** `A_W` is an end-state stock; an edge that is asserted without being served is evidence about the path, not about what the stock would have been.
- **Not a prediction about cap 112.** 10 of the 26 sit inside the cap at cap 40; nothing here says a 112-slot build would serve them. That is the registered cap-112 arm's question, not this record's answer.
- **Not a capability, retention or transfer claim.** One world family, six seeds, one cap, one 0.14.0 build, 120 cycles.
- **Not an attribution.** The asserted edge lists are stored as an input; their count and digest are checked against the run, but storing them is not a second measurement and does not name the events behind an assertion.
- **Not a reconciliation of `S_ever` and `A_W`.** One is a cumulative union and the other an end-state stock; their difference is not a loss count.

## Three readings it rules out

1. **'The assertion step loses nothing.'** False: 26 asserted edges were never served.
2. **'The loss is at construction.'** False for this set: these are present world edges, so they were constructed as candidates; the Q4 stage table's 179 never-admitted candidates are a different set with a different denominator.
3. **'Inside the cap means it was served.'** False: 0 of the 10 in-cap edges were inside the served transitions of their best cycle; the closest was 2 rank(s) short.

## What would change this note

- **The cap-112 admission arm.** If the 21-40 transitions are served at 112, per seed and with the block's gates passing, the capacity reading of these ten edges strengthens; if they are not, the next step is the admission rule rather than another level, as `docs/DECISION-ADMISSION-STEP.md` fixes.
- **A different world family or seed block.** The shape here -- most of the remainder in 41-80 and 21-40, none inside the served transitions -- is one family's shape, and a fresh block could move it.

## Scope

The record this note interprets was produced on the 0.14.0 build at cap 40, 120 cycles, six seeds of the Gate-13 compositional world. The note restates and bounds the record; it does not re-score it, and it adds no evidence.
