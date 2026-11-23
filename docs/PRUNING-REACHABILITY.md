# Can a `pruned` edge death happen? — measurement

Generated from `docs/pruning_reachability.json` by
`python -m benchmarks.pruning_reachability --render`. Do not edit by hand.

## Label

**UNREACHABLE_IN_THE_LEDGER**

The branch is unreachable from any edge the attribution ledger follows, and the engine
prunes on the same run. The record's fourth category was never observed because the
instrument stops at the stable threshold, not because the mechanism is absent.

## The arithmetic

The ledger judges an edge on the step from a strength to `strength x 0.8`, and it only
judges an edge that was stable last cycle:

| Quantity | Value |
| --- | --- |
| Stable threshold (read from the engine) | 0.3 |
| Death threshold (read from the engine) | 0.15 |
| Factor | 0.8, from the 0.8 literal in SleepService._natural_selection |
| Weakest stable edge, after one step | 0.24 |
| Strength the pruning branch would need | 0.1875 |
| Margin above the branch | 0.09 |

So the branch needs an input below the threshold at which the edge counts as stable. That
is not a property of this world, this seed or this build; it holds for every edge the
ledger is able to follow.

## The branch, driven by the ledger's own rule

| Step | Prior strength | After decay | Reason the ledger assigns |
| --- | --- | --- | --- |
| 1 | 0.3 | 0.24 | `decayed` |
| 2 | 0.24 | 0.192 | `decayed` |
| 3 | 0.192 | 0.1536 | `decayed` |
| 4 | 0.1536 | 0.12288 | `pruned` |

The ledger takes step **1** and stops; the branch fires at step **4**. The rule is
live, and the silence is the window's.

## What the same 300 cycles recorded

| Quantity | Engine arm | No-decay control |
| --- | --- | --- |
| Seeds | 3 | 3 |
| Cycles per seed | 300 | 300 |
| Ledger edge deaths | 1044 | 273 |
| Of those, `pruned` | 0 | 0 |
| Engine candidates strengthened | 105111 | 140247 |
| Engine candidates decayed | 21522 | 27819 |
| Engine candidates pruned | 7122 | 4920 |
| Cycles with at least one pruning | 894 | 885 |

## What this changes

- **`decayed 0.6897` and `below_threshold 0.3103` are statements about strength crossing
  the stable threshold.** They are not a comparison between decay and pruning, because
  pruning is not on the instrument's axis.
- **`pruned | not measurable` should read `unreachable in this ledger`.** A structural zero
  and an unmeasured quantity are different claims, and the published cell does not say
  which one it is.
- **Pruning is live in the engine** on the run that produced the published numbers. It is a
  later stage of the same decay process the ledger does watch: an edge that crosses 0.30 is
  classified `decayed`, and the candidate it belongs to is retired when it reaches 0.15.

## What this does not establish

- **The engine's counter is not split by candidate type.** It counts every surviving
  generation, so it shows that pruning happens, not how much of it is prediction edges.
- **No published artifact is restamped or rewritten.** The attribution result stands; the
  interpretation placed on one of its cells is what this record corrects.
- **It runs no cell.** Every number above is read from artifacts already committed, apart
  from the trace, which is the ledger's rule applied to a constructed chain.
