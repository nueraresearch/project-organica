# How often does V1 forget a carrier instead of retiring it?

**Status:** `MEASURED FROM THE STORE. No arm, no target, no freeze, no grant.`

**Answer: not once in 92 sleep cycles.** Every one of the 177 carrier identities either ended with a death record
(147) or was still inside the engine's memory at the last cycle (30); none left the 4,000-event window
while alive. The window cannot forget a lapsed carrier before decay kills it: a carrier absent from a cycle falls ×0.8, so it
crosses the 0.15 death threshold within nine cycles, while the window holds about 18 cycles of sleep
rows (20086 rows over 92 cycles). In this world the retirement count is not a lower bound at all: there is no
third category of carrier.

## 1. What was measured

`sleep_selection._load_prior_candidates` reads `memory.recent(n=4000, event_type="sleep")`, keeps the newest copy per
candidate id, and drops any copy marked retired. This study records the sleep-row boundary before every cycle and reloads
each cycle's prior from the store exactly as the engine would, so what the engine could see is read, not simulated.

| | |
|---|---|
| Sleep rows | 20086 |
| Sleep cycles run (of 120 world cycles) | 92 |
| Carrier rows | 4303 |
| Carrier identities | 177 |
| Retirement rows | 186 |
| Retirement events visible in a prior | 186 |
| …that superseded a live copy | 186 |

## 2. The accounting

| Final outcome | Identities |
|---|---|
| Ended with a death record | 147 |
| Still visible in the memory at the last cycle | 30 |
| **Forgotten alive** | **0** |

The three account for all 177 identities (conserved). There were 0 forgetting episodes over
0 identities: the window never dropped a live carrier.

## 3. Why the window cannot do it

A carrier that is not re-detected decays by ×0.8 per cycle from at most 1.0, so it dies in at most nine cycles. The window
holds 4,000 sleep rows; at 218.3 sleep rows per cycle that is about
18.3 cycles of memory — about twice the decay horizon. Forgetting a live carrier would require a carrier to sit above
0.15 for longer than the window holds, and decay does not permit that.

## 4. Validation, and a correction

Re-running the rules offline with the store's own visibility reproduces **186** retirement rows against 186 stored
(a match). The first version of the re-keying study reported 201 and blamed the window. It was
wrong: its simulator reinforced from the prior strength (`prior + 0.05`) instead of the fresh detection (`detection + 0.05`),
which is what `_reinforce_current` does. That was the source of the 15-retirement gap, not the window, and the other study
now reproduces all 186 retirement rows and has been re-run under the corrected rule.

## 5. What it means

- **The death count is not a lower bound in this world:** 147 carriers ended with a death record and 30 were still live.
  There is no third category.
- **The window's cost is growth, not forgetting.** Rows above the boundary stay on disk while cognition stops reading them;
  nothing in this run was saved by the window and nothing was lost to it.
- **The primitive's admission rule is unaffected.** It was motivated by re-detection after a lapse; that case did not occur
  here, but the lifetime argument for a content-free id stands on the storage accounting, not on this count.

## 6. Limits

One seed, one world, one window size, and 92 sleep cycles. A longer run with a denser candidate stream could
push the window below the decay horizon; that is a prediction of the arithmetic in §3, not something this study observed.
