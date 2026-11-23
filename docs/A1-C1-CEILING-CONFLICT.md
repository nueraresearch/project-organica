# A1 C1 denominator ceiling — two adopted records disagree

**ID:** `A1-C1-CEILING-CONFLICT-1`
**Date:** 2026-11-15
**Status:** `FLAGGED — TWO ADOPTED RECORDS CONFLICT ON THE ADOPTED BLOCK; OWNER DECISION REQUIRED`

**This is not an A1 result and not a decision.** It records a conflict between two records the owner has already
adopted, quantifies it against the adopted block's own baseline, and names what would resolve it. No cell ran.

## The two records

[`DECISION-A1-PATH-A-C1-RULE`](DECISION-A1-PATH-A-C1-RULE.md) (`A1-PATH-A-C1-RULE-1`, adopted 2026-11-14, *binding
for A1*) maps the C1 denominator to an acceptance band and closes the top of it:

> | 64 | 61 | 3 | C1 may be read |
> | >64 | n/a | n/a | `VOID — design inconsistency; score preplanned rows only` |

> If the observed minimum is **above 64**, the run is **`VOID — design inconsistency`**.

[`DECISION-A1-C1-DENOMINATOR`](DECISION-A1-C1-DENOMINATOR.md) (`DECISION-A1-C1-DENOMINATOR-1`, adopted
2026-11-15) fixes the operative denominator as the **recorded cell row** — "every observed paired-control row of the
cell stream, non-target edges included. Not the candidate count" — and notes that the cell stream can exceed the
63–64 planning figure. It does not mention the `>64` clause, does not narrow it, and neither record names the other
superseded.

## The measurement

The adopted block's own no-arm baseline
([`a1_baseline_availability_adopted.json`](a1_baseline_availability_adopted.json)) observes, per seed, a minimum
paired-control denominator of:

| Seed | `20740101` | `20740102` | `20740103` | `20740104` | `20740105` | `20740106` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Observed minimum | **79** | 64 | **79** | **74** | **72** | **74** |
| Above 64? | yes | no | yes | yes | yes | yes |

**Five of six seeds are above 64 on the operative row.** Read literally, `A1-PATH-A-C1-RULE-1` makes the run
`VOID — design inconsistency` on those five seeds before any retention is inspected — not because preservation
failed, but because the denominator is larger than the band the rule was written against.

## The two readings

**Narrow reading.** The clause governs the *candidate-plan* denominator. Its neighbouring sentences describe 63–64 as
"an upper bound from candidate counts, not an observed baseline-availability denominator", and its stated purpose is
to stop rows being added after the fact. On this reading the cell-row denominator is a different quantity and the
clause does not apply; nothing changes.

**Literal reading.** The clause governs whatever the operative denominator is — which, after 2026-11-15, is the cell
row. On this reading five seeds are VOID, and the adopted block cannot produce a readable C1 at all.

Neither reading is established by the text. The narrow one requires importing a distinction the 2026-11-14 rule did
not make; the literal one applies a band designed against one quantity to another. **A footnote cannot settle this,
and a later record that changes the denominator without amending the ceiling has left the conflict in place.**

## What would resolve it

One of two explicit decisions:

1. **Narrow the clause to the candidate-plan quantity**, stating that the operative cell-row denominator has no
   numeric ceiling and that the anti-p-hacking intent is carried by "no rows may be added after the fact" instead; or
2. **Keep the ceiling** and treat the adopted block as unable to support a readable C1, which voids the freeze
   rather than the analysis.

Either is a decision record. Until one exists, any statement that the C1 branch is closed is true of the floor and
silent about the ceiling.

## Correction this record carries

A checklist note written earlier today asserted the narrow reading as settled — "it is a candidate-stream rule, not a
validity ceiling." That was a documentation edit standing in for a decision on a binding record. This file replaces
the assertion with the conflict it was hiding.

## Limits

Reads committed artifacts only: the two decision records and one baseline. It scores nothing, voids nothing and
changes no threshold.

## Reproduce

```bash
.venv/bin/python -c "
import json
d=json.load(open('docs/a1_baseline_availability_adopted.json'))
print([r['c1_min_denominator'] for r in d['per_seed']])"
```
