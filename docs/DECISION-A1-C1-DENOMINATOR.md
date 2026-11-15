# Decision: the protocol's C1 denominator is authoritative

**Date:** 2026-11-15

**Status:** `ADOPTED — THE PROTOCOL DENOMINATOR IS AUTHORITATIVE; NO RUN AUTHORISED`

**Scope:** definition only. This document freezes no manifest, assigns no seed, changes no threshold, authorises no cell and records no result. C1 remains unscored.

## Decision

The protocol's C1 denominator is authoritative: C1 counts the observed paired-control rows across the cell stream, including baseline-available non-target edges.

The 63–64 candidate-count figure is a planning quantity, not C1's denominator.

The operative row is the recorded cell row, which is what `c1_rows` counts and `score_c1` scores.

No cell is authorised by this decision.

## Why

The protocol already fixes the denominator, `benchmarks/a1_arms.py:c1_rows()` already implements it, `score_c1()` already scores it, and three committed documents already distinguish the 63–64 planning figure from the scored denominator. The competing reading was not a second definition in the protocol; it was downstream interpretation drift — a sizing number quoted back as if it were the definition. Confirming the existing definition is not selecting a winning outcome, and it changes no evidence.

## What this settles

- **Which rows count.** Every observed paired-control row of the cell stream, non-target edges included. Not the candidate count.
- **Which row.** The recorded cell row — a directed orientation — because that is the row the adopting code counts and scores. The protocol text alone does not disambiguate a directed row from an undirected relation; this decision supplies the reading the implementation already has, rather than leaving two records to mean different things by one word.
- **C1 floor reachability.** Under that row, the adopted block's ceiling is **79, 64, 79, 74, 72, 74** against a floor of **60**, so the floor is reachable on every seed. Under a relation-level row it would not be. The reachability claim therefore rests on this decision, and is recorded as such.

## Boundary — one level below this decision

This decision fixes which rows participate and which denominator adjudicates. It does **not**
fix what counts as one observation within that denominator: whether `a → b` and `b → a` are two
C1 rows or one relation counted once. The protocol does not say, the implementation reads
directed edges, and target selection reads one orientation per unordered pair, so the repository
currently uses both units in different places. That question is set out on one page in
[`A1-C1-UNIT-OF-EVIDENCE`](A1-C1-UNIT-OF-EVIDENCE.md); it is an owner definition and remains open.

## What this does not settle

C1 has not been scored: no cell has run, and the floor applies to observed paired-control rows at run time, not to a ceiling. This decision does not make the A1 design viable, does not resolve C2/C8 target competence, does not resolve the C4 exposure over 108 non-target rows per seed, and does not authorise a freeze, a grant or a cell. The two freeze acts remain `DRAFT` and their blocker moves from the denominator to those two questions.

## Rejected alternatives

- **Treat 63–64 as the C1 denominator.** Rejected: the protocol defines the denominator and `c1_rows` implements it; the candidate count is a planning quantity that the downstream reading mistook for the definition.
- **Leave the definition open and let each record choose.** Rejected: a denominator that can differ between records cannot be compared across runs, and C1's floor is only meaningful against one denominator.
- **Decide C1's reachability from the availability ceiling alone.** Rejected: a ceiling is not an observation: no cell has run, so C1 remains unscored under the adopted definition.

## What would change this

An observed paired-control denominator that behaves like the relation-level quantity — for example a run whose distinct non-target relations, rather than its rows, are what the estimator can use — would reopen the row question with evidence rather than with reading. Until then the adopted definition stands and is the one every A1 record is read against.
