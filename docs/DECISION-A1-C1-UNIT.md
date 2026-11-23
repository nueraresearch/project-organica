# Decision: C1's unit of evidence is the directed edge, with the relation as a declared dependence class

**Date:** 2026-11-15

**ID:** `DECISION-A1-C1-UNIT-1`

**Status:** `ADOPTED BY OWNER 2026-11-15 — DIRECTED EDGE IS THE UNIT; RELATION IS A DECLARED SENSITIVITY; NOT FROZEN, NOT RUN`

**Scope:** the unit of evidence for C1 only. This decision changes no threshold, freezes no manifest, reserves no seed, authorises no cell, and alters no code — the adopted unit is what the implementation already reads.

## Decision

C1's unit of evidence is the directed edge. The undirected relation is a dependence class, not a competing denominator.

The protocol never said which it was: `A1-DESIGN-VIABILITY-1` records that whether two orientations of one relation are independent C1 observations "is a convention the protocol does not fix", and `score_c1` reads whatever `c1_rows` counts, which is directed rows. This decision supplies the reading the text leaves open, so that the choice is recorded rather than inherited from the implementation.

**What follows, in obligations rather than preferences:**

1. **The estimate is directed.** C1 counts and scores paired-control rows as directed edges, over the C4-expanded cell stream, at the 0.95 floor — unchanged.
2. **The relation is reported, not pooled.** The run record carries a relation-level C1 proportion counted **once per undirected relation**, on its own denominator (31–51 relations per seed on the adopted block), with its own count form, never averaged with or substituted into the directed result.
3. **Neither reading rescues the other.** A directed pass and a relation-level shortfall are both reported. A relation-level result may not be converted into a directed one by doubling, and the directed denominator may not be described as "more rows" without saying that they are two orientations of the same relations.
4. **C4's protected set is the directed one.** 108 non-target rows per seed at N=4 and 92 at N=20 stand; the relation reading's 59–60 / 43–44 is recorded as the alternative, not adopted.
5. **No threshold moves.** 0.95, the C4-expanded denominator, and the C1/C4 VOID gate are unchanged.

## Why this reading and not the other

**The estimand decides it.** C1 asks whether a *carrier path* survives A−. The carrier is directional in this engine: availability is orientation-specific, and A availability differs across orientations on **15–28 of 64 relations** per seed. A relation-level count answers "does the coupling survive", which is a different and weaker-matched claim than "does the directed path survive". Choosing the unit that matches the estimand is not a preference between numbers; it is the only choice under which the gate measures the thing the design asserts.

**The orientations are neither duplicates nor free observations**, and both halves matter. Because A differs on 15–28 of 64 relations, discarding one orientation discards real variation. Because they are two readings of one coupling — and K is 97.2% concordant across candidate/reverse pairs (278/286) — counting both inflates n with correlated members. The directed denominator therefore *overstates* independence, which is why the relation is a dependence class and why it must be reported rather than assumed away.

**The directed reading is also the one that clears.** On the adopted block directed rows clear the 0.95 floor on 6 of 6 seeds (64–79 against 61) and on 4 of 6 of the earlier block (58–72 against 60); the relation reading, read as a proportion on its own denominator, tolerates one or two failures rather than three. The relation reading is stricter, not impossible — and it is reported precisely so that no reader has to take the directed result on trust.

**Consistency with selection.** Target selection already takes one orientation per unordered pair, so C8's twenty rows are twenty relations. Recording the mixture — relations for selection, directed edges for C1's estimate — turns an undocumented inconsistency into a stated design: the two estimands differ, and each uses the unit its claim requires.

## What this does not do

It does not amend `DECISION-A1-C1-DENOMINATOR-1`, which fixed *which rows participate*; this decision fixes *what one of them is*, one level below. It does not change the protocol text, so `A1-DESIGN-VIABILITY-1` keeps its `OPEN` status deliberately — the protocol is still silent, and the record should not pretend a decision amends it. It does not halve C4's protected set, does not change any code, and does not authorise a run.

## Rejected alternatives

**Make the relation the unit outright.** Rejected because C1's claim is about a directed carrier path: a relation-level proportion answers whether the coupling survives, not whether the path does, and adopting it would have the gate measuring a different quantity than the design asserts.

**Count both orientations and treat them as independent.** Rejected because K is 97.2% concordant across candidate/reverse pairs and the two orientations share one coupling; counting both inflates n with correlated members, and no correction for that dependence is declared anywhere in the C1 machinery.

**Leave it to the implementation.** Rejected because that is the current state: `c1_rows` counts directed rows while selection takes one orientation per pair, so the mixture exists by default rather than by decision, and a reader cannot tell which reading a later result was scored under.

**Adopt the directed unit and drop the relation reading.** Rejected because the orientations differ on 15–28 of 64 relations; without the relation-level proportion a reader cannot see how much of the directed result is two views of one coupling.

## What this unblocks

The checklist's remaining substantive owner choice is now **C4's exposure** alone. The disposition settles against C4; freeze and grant follow from the disposition. The unit question no longer sits underneath them.

## Reproduce

```bash
python -m benchmarks.a1_design_viability --check     # directed and relation ceilings, per seed
python -m benchmarks.a1_competence_filter_draft --check   # one orientation per pair in selection
```

Reads committed no-arm artifacts; runs no engine. The 15–28 and 278/286 figures are `A1-DESIGN-VIABILITY-1` and `A1-K-DECOMPOSITION-1`; the tolerance arithmetic is `floor(0.05 × N)` applied at each unit's own denominator.
