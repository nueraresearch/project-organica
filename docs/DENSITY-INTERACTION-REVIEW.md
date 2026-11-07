# The density interaction: pre-run review (2026-11-07)

**Verdict: HELD - NOT RUNNABLE AS REGISTERED.**

the block runs, and its dense end has no headroom: at rho_world 0.8 under fixed total exposure the control already scores precision 1.000, so the treatment cannot add anything there and the registered interaction cannot be positive

No judged cell ran, no registered seed was touched, and nothing in this document is
evidence for or against the density hypothesis.

## 1. Method

1. cold read of the committed artifacts, the frozen engine's API and the engine's own ordering
2. an engine dry run on five unregistered seeds (991001-991005), which are outside the registered block and produce no judged cell
3. no judged cell ran, no registered seed was touched, and nothing here is a result about the hypothesis

## 2. The evidence

Precision at cap 20, on the unregistered seeds 991001, 991002, 991003, 991004, 991005. The engine's pool at the
dense end is 240 rows, of which 192 are world edges (rho_rank 0.8).

| rho_world | scheme | seeds | control | treated | Delta per seed | mean Delta |
|---|---|---|---|---|---|---|
| 0.1 | primary | 5 | 0.35, 0.35, 0.25, 0.50, 0.45 | 0.45, 0.35, 0.35, 0.55, 0.50 | +0.10, +0.00, +0.10, +0.05, +0.05 | +0.060 |
| 0.8 | primary | 5 | 1.00, 1.00, 1.00, 1.00, 1.00 | 1.00, 1.00, 1.00, 1.00, 1.00 | +0.00, +0.00, +0.00, +0.00, +0.00 | +0.000 |
| 0.1 | sensitivity | 4 | 0.35, 0.25, 0.45, 0.45 | 0.35, 0.35, 0.50, 0.50 | +0.00, +0.10, +0.05, +0.05 | +0.050 |
| 0.8 | sensitivity | 4 | 0.80, 0.80, 0.80, 0.80 | 1.00, 1.00, 1.00, 1.00 | +0.20, +0.20, +0.20, +0.20 | +0.200 |

The interaction on precision — Delta(0.8) minus Delta(0.1) — is **-0.060** under fixed
total exposure and **+0.150** under fixed exposure per edge. The sign flips with the
exposure scheme, which the design record defines as an exposure artifact, and under the
primary scheme the dense end has no room to move: both arms are at 1.000.

## 3. Findings

| id | severity | what | disposition |
|---|---|---|---|
| F1 | blocking | the dense end is saturated by arithmetic: at rho_world 0.8 the pool is 240 rows of which 192 are world edges, so any count-ranked top-20 is all world edges and both arms score 1.000 on 5 of 5 seeds. Delta(0.8) is 0 by construction, C1's lower bound cannot exceed 0, and the primary scheme's interaction is negative (-0.06) while the per-edge scheme's is positive (+0.15). The design record defines a sign reversal between schemes as an exposure artifact | this is the design's budget, not a harness defect; changing the cap or the anchor after seeing a dry run is a new registration (A2), and it is the owner's call |
| F2 | blocking | amendment A1's direction (the advantage rises) was measured on the designed pools, whose count distribution at the dense end differs from the engine's. On the engine's pool the same world gives the opposite sign under the primary scheme. The designed-pool audit is a feasibility check on the world, not on the instrument, and the registration leaned on it as if it were one | the direction cannot be corrected again without new evidence from a redesigned budget; A1 is retained and marked as not transferring, and the block is held instead |
| F3 | high | the rho = 1 identity fixture selected the whole pool (cap = number of rows), so both arms were identical no matter what the eligibility filter did: a check that could not fail | fixed — cap is the primary cap, so the arms agree only if the filter removes nothing it should not; a guard asserts cap < pool and that G0 compares sets rather than stored order |
| F4 | high | gate G0 compared the arms' stored selection lists, so the same rows in a different order counted as liveness | fixed — G0 compares the selected sets; a test reverses one arm's list on every seed and asserts G0 fails and the block voids |
| F5 | medium | the world description said the filler's share of the event budget is (1 - rho_world). Its event count is proportional to (1 - rho) against a fixed peak budget, while the stream grows with |W|, so the share falls faster than (1 - rho) | fixed — the module docstring and the registration's world paragraph state the count and the faster-falling share; a test asserts the old sentence is gone and the proportionality that does hold |
| F6 | low | two literals: the provenance wrote `primary_cap and 400`, and the generator audit compared against a hardcoded 400 | fixed — both read TOTAL_EVENTS from the world module |
| F7 | medium | the design record's analysis rule that precision cannot exceed rho_rank is false: at rho_world 0.8 the control scored precision 1.000 against rho_rank 0.800. Only min(1, |W and P_rank| / k) binds | fixed — the rule and the design record are corrected with the counter-measurement disclosed; the registration never gated on the false bound |

## 4. What the review did confirm

* the runner opens a real engine pool (400 events, 50 cycles) and reads the precedes table: MemoryService.store, SleepService.run_sleep_cycle and the table's columns all match
* the control's tie-break (-count, tag_from, tag_to) is the engine's own ORDER BY, so the control is the engine's ordering rather than a lookalike
* presence is 1.0 in every dry-run cell, so the memory ceiling the design requires is reachable
* the harness self-tests pass and the full suite is green after the fixes

## 5. Recommendation

do not run this registration. A2 should make the budget a fixed fraction of |W| (cap = |W| / 4 holds the selection task comparable: 6 slots at 0.1, 48 at 0.8) or anchor the interaction on levels where the control is below the ceiling, reporting 0.8 as the demonstration that the ranking problem disappears. Either way the sparse end's headroom is bounded by |W| = 24, so the interaction is bounded well below the 0.35 the designed-pool audit suggested

## 6. What this is not

the dry-run figures describe the instrument on unregistered seeds. They are not evidence for or against the density hypothesis, and no criterion is read from them
