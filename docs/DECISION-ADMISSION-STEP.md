# Decision: the admission step is named — constructed, not admitted

Dated 2026-11-11. Recorded by the owner against Question Q054 and the decision table of
`docs/presence_conversion_repair_prereg.json`, whose measured row ends with an owner decision on
the named step and implies no engine change.

## The decision

**The step is named: constructed but not admitted.** The conversion stage table's loss sits between
the candidate list and the served window, not at construction: 671 of 672 present world edges became
candidates, and 179 of those candidates (16–41 per seed) never entered a served window.

The step is not "admitted but not constructed". Served edges are a subset of the recorded universe in
every one of the 720 cycles, so that count is zero by construction; the measured direction is the
opposite one, and the record must not be named after something it does not measure.

## Status

Decided, not in force: the cap is still 40, no cap-112 runner exists, and the three cap-112 records
are frozen and unrun. Nothing on disk in the engine changes. **Superseded later on 2026-11-11:** the level landed in 0.15.0 and the three runners are runnable; the decision and its acceptance condition are unchanged, and the amendment below records the build state.

## The decision, in full

- Name the step: the loss is constructed but not admitted — 179 of 671 candidate world edges, 16–41 per seed, never entered a served window.
- Do not change the engine on this record: a stage measurement authorises no cap, allocation, ranking or threshold edit.
- Test the step with an allocation arm, not another description: the registered cap-112 records raise the guaranteed transition budget from 20 to 56; at 112 the band arm observed 64-69 transitions because unused cooccurrence slots were backfilled, and the arm is the designated counterfactual.
- Accept the allocation explanation only if the 21–40 transitions are served at 112 and the block's own gates pass; if they are not, the explanation is refuted and the next step is the admission rule.
- No capability, retention or transfer claim follows from this record; it locates a loss, it does not measure an ability.
- Record BAND-5 as a fresh-world confirmation of the allocation-law mechanism, not as a re-score of BAND-1 and not as acceptance of the named-Q4-edge condition.

## The conditions

**What must hold before the test runs.** Version 0.15.0 must land (three version declarations,
changelog, re-pin), the canaries must be re-recorded for the level, and the three cap-112 records
need runners; their 2026-11-11 grant authorises the cells, not the build.

**What counts as the mechanism being measured.** The 21–40 transitions must be served at 112 and
the block's own gates must pass, per seed, with the seed axis live.

**What counts as it being refuted.** If those transitions still are not served with a guaranteed
56-slot transition floor (at least 56 served), the allocation explanation is wrong at this world
family and the next step is the admission rule, not another level.

**What may not be done with this record.** Pooling the stage table across seeds, citing it as a
capability result, or landing the cap without the version and canary record this decision already
requires.

## Amendment, 2026-11-11

The three cap-112 runners are now built at `benchmarks/presence_cap112_runners.py` (comparator,
Q1, Q2), against the frozen designs and their gates. Nothing else moved: the cap is still 40, no
cell has run, no verdict is adjudicated, and the runners refuse on this build before a database is
opened. The decision remains **PENDING**, and the acceptance condition above is unchanged.

## Amendment, 2026-11-11 (the level landed)

The precondition this decision names is now satisfied. Version **0.15.0** landed on 2026-11-11:
the cap is **112**, the version declarations and changelog moved, the pin was re-recorded and the
four canaries were re-recorded on the installed bytes. The three cap-112 runners are built, and
`preflight()` now reports **zero** unmet conditions, so `--measure` no longer refuses and the cells
are runnable.

Nothing about the decision moved. The step is still **constructed but not admitted**, the status is
still **PENDING**, and the acceptance condition is unchanged: the **21-40** transitions must be
served at 112, with the block's own gates passing per seed and the seed axis live. No cap-112 cell
has run and no verdict is adjudicated. The first amendment's statement that the cap is still 40 and
that the runners refuse on this build is superseded by this one; the record of what was true then
is kept, not rewritten.

## Amendment, 2026-11-11 (the arm ran)

The cap-112 arm ran after the comparator. All 24 cells and the 112 witness executed; the block
returns **CAP LIMITING** with K1-K6 passing, a mean paired gain of 17.833333 and a 95% lower bound
of 13.613754 against the bar of 10, positive on 6 of 6 seeds. At 112, asserted world edges are
44-58, and admitted world edges rise from 63-88 to 96-102.

The **21-40 band itself is not identifiable** from this block: its fresh seeds have different
worlds from Q4's, and its cells record counts rather than per-edge ranks. The block therefore
shows that more world edges enter service at 112, not that the named Q4 edges do. The acceptance
condition is **unadjudicated**, the decision remains **PENDING**, and the condition itself is
unchanged.

## Amendment, 2026-11-11 (the band arm is frozen)

The instrument this condition needed now exists as a frozen record:
`docs/presence_band_rank_prereg.json` and its page. It names all **62** Q4 rank-21-40 transition
edges by identity and fixes a twelve-cell arm at cap **40** and **112** on Q4's six worlds, with
the 40 arm as the pre-treatment control, a per-edge ledger and gates B1-B8. The acceptance
condition above is quoted verbatim in that record, and nothing about it changes.

No authorisation is recorded and no cell has run. The decision remains **PENDING**, the acceptance
condition remains **unadjudicated**, and this is not a re-read of Q2: `CAP LIMITING` stands, and
the new record measures the named edges rather than the aggregate Q2 measured.

## Amendment, 2026-11-11 (the designated test is the band arm)

The test this decision's acceptance condition names is `PRESENCE-BAND-1`
(`docs/presence_band_rank_prereg.json`), not the cap-112 allocation arm alone. Q2 ran the
allocation arm and returned `CAP LIMITING` without recording per-edge ceiling ranks, so it
cannot adjudicate the condition. The band arm reads the **62** named rank-21-40 edges at cap
**40** and **112** on Q4's six worlds, with a per-edge ledger and gates B1-B8.

It is frozen, its runner is built, and it is **ungranted**: its preflight refuses before a
database is opened, and no cell has run. The decision remains **PENDING**, the acceptance
condition is unchanged, and Q2's `CAP LIMITING` is not re-read.

## Amendment, 2026-11-11 (the band arm ran and returned VOID)

`PRESENCE-BAND-1` ran its twelve cells and the determinism rerun under
`docs/AUTHORISATION-PRESENCE-BAND-1.md`. The band was served in full at 112: all **62**
named edges entered service on every seed (12, 9, 16, 9, 14, 2) and **0** at 40. The block
is nevertheless **VOID**, because gate **B5** failed on every seed: the cap-112 transition
allocation is 64-69, not the **56** the frozen gate fixes, and the rank comparison read no
served edge's block rank. Seven of eight gates pass. Under the frozen table a gate failure
reads no acceptance, so the condition stays **unadjudicated** and the decision stays
**PENDING** for the owner; Q2's `CAP LIMITING` and Q4's `CONVERSION STAGE MEASURED` are not
re-scored, and these cells are not re-read.

## Amendment, 2026-11-11 (the 56-transition budget is a floor)

The engine's `transition_budget` is `returned_budget // 2`, a guaranteed floor. When cooccurrence
candidates do not fill the returned window, `_build_predictions` backfills the unused slots with
further transitions (`more_trans`). At 112 the floor is 56, and the band arm's cells served 64-69
transitions. BAND-1's B5 required exactly 56, so its **VOID is a gate defect**, not evidence that
the allocation explanation failed.

BAND-2 (`docs/presence_band_rank_2_prereg.json`) freezes the corrected `>= 56` condition and the
strict rank reader; it is frozen, unrun and ungranted. The decision remains **PENDING**, the
acceptance condition is unchanged, and BAND-1 is not re-scored.

## Open question: the outcome is answered, the mechanism stays unadjudicated

The record now has two questions that must not be read as one. The **outcome question** -- does raising the Layer-1 cap from 40 to 112 increase admission and assertion? -- is answered: `CAP LIMITING`, positive on 6 of 6 seeds, with a mean paired gain of **17.833333** asserted world edges and a 95% lower bound of **13.613754** against the bar of **10**. The **mechanism question** -- do the specific rank-21-40 transitions named by this decision enter service? -- stays **unadjudicated**: BAND-5 confirmed the allocation-law band on fresh worlds, with **89 of 89** measured rank-21-40 edges served at 112 and **0** at 40, but its fresh seeds and measured band are not the **62** named Q4 edges, so it is not a re-score and does not satisfy this decision's specific condition.

**BAND-5 verdict.** `PRESENCE-BAND-5` ran twelve cells on fresh seeds 20612601-20612606 at caps 40 and 112, plus the determinism rerun. B1-B8 pass; every full cap-112 window has 64-68 transitions and 48 cooccurrences, satisfying the full-window allocation law; all 89 measured rank-21-40 edges are served at 112 and none at 40. The block is a fresh-world confirmation of the allocation-law mechanism, not a re-score of BAND-1.

**What remains open.** The specific acceptance condition in this decision is about the 62 Q4 rank-21-40 edges named by BAND-1. BAND-5 does not measure those edges, because its worlds and its measured band are fresh. The named-edge mechanism question therefore stays **unadjudicated**; the decision remains **PENDING**; Q2's `CAP LIMITING` and Q4's `CONVERSION STAGE MEASURED` are not re-read.

Record BAND-5 as a fresh-world confirmation of the allocation-law mechanism, not as a re-score of BAND-1 and not as acceptance of the named-Q4-edge condition.

Neither question licenses a capability, retention or transfer claim. The decision remains **PENDING**, and the acceptance condition is unchanged.

## Rejected alternatives

**Alternative.** Treat the 62 rank-21–40 misses as a ranking defect and change the ranking.
**Because.** The 62 rank-21–40 misses are outside the 20-slot transition allocation, so changing the ranking would answer a defect the record did not find.

**Alternative.** Close the conversion route as "assertion loses nothing".
**Because.** A_W is an end-state stock and S_ever a cumulative union, and 26 asserted edges were never admitted, so the assertion step was not measured as a loss.

**Alternative.** Call the step "admitted but not constructed".
**Because.** Served edges are a subset of the recorded universe in every cycle, so admitted-but-not-constructed is zero by construction and cannot be the step that was measured.

## Evidence

`docs/presence_conversion_repair_run.json`, `docs/PRESENCE-CONVERSION-2-RESULT.md`,
`docs/presence_conversion_repair_prereg.json`, `docs/presence_conversion_2_n3_tables.json`,
`docs/DECISION-CAP-LEVEL.md`, `docs/LANDING-0.15.0.md`.

## What this does not cover

Any claim that admission is the only loss, that construction is healthy in general, or that
assertion is lossless. The stage table measures one world family at cap 40 on six seeds, and the
assertion step is reported but not adjudicated.
