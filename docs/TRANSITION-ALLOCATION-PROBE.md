# Does a larger transition allocation serve the 21-40 transitions?

Generated from `docs/transition_allocation_probe.json` by `python -m benchmarks.transition_allocation_probe --write`. Do not edit by hand.

**Not a result.** One seed, two in-process arms, one build. It answers a narrow question left open by `docs/PRESENCE-UNEXPLAINED-EDGES.md` and licenses no claim.

## The question

At cap 40 the engine served half the window as transitions, 20. Ten asserted world edges ranked 21-40 and were never served. At cap 112 the shipped transition share is 56. Does that serve them, and does giving transitions the whole window change it?

## Design

| Field | Value |
| --- | --- |
| Seed | `20611603` (the band's densest seed; 3 of the ten edges) |
| Cycles | `120` |
| Cap | `112` |
| Edges | `slate>umber`, `slate>yarrow`, `umber>teal` |
| Control | the shipped half-and-half allocation, same seed and cap |
| Manipulation | transitions are given the whole processed window for the duration of one `_build_predictions` call; the returned list is truncated to the shipped cap |
| Seed reuse | one of `PRESENCE-CONVERSION-2`'s design seeds, reused for a derived one-seed diagnostic and declared as an allowed source in that block's freshness scan |

## Result

| Arm | Band served | Band asserted | Served world | Asserted world | Returned window (median) |
| --- | ---: | ---: | ---: | ---: | ---: |
| shipped-112 | 3 / 3 | 2 / 3 | 109 | 47 | 112 |
| all-transitions-112 | 3 / 3 | 3 / 3 | 112 | 77 | 112 |

### Per edge

| Edge | Shipped: served (first, admissions) | All-transitions: served (first, admissions) | Min rank at 112 | Cycles in universe |
| --- | --- | --- | ---: | ---: |
| `slate>umber` | yes (39, 61) | yes (39, 82) | 20 | 82 |
| `slate>yarrow` | yes (30, 70) | yes (30, 91) | 19 | 91 |
| `umber>teal` | yes (51, 2) | yes (38, 60) | 4 | 83 |

## What the transition label means

Within a cycle a transition-labelled edge is absent from the cooccurrence table by construction: the engine sets `is_cooccurrence` from that table and appends the candidate to one list or the other, so the zero is an invariant, not a finding. Both labels carry `temporal_count`, so the label names the branch the candidate took, not the kind of evidence behind it.

| Arm | Transition rows | Cooc rows | In cooc within a cycle | Dual-labelled edges across cycles | Max duplicate pairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| shipped-112 | 18959 | 5335 | 0 | 0 | 0 |
| all-transitions-112 | 18959 | 5335 | 0 | 0 | 0 |

The band's label history: `slate>umber` transition in 82 cycles, cooccurrence in 0; `slate>yarrow` transition in 91 cycles, cooccurrence in 0; `umber>teal` transition in 83 cycles, cooccurrence in 0.

So the band is not a set of temporal-only edges: `transition` means the pair was outside the cooccurrence table in the cycle that ranked it. On this seed no band edge ever carried the other label, and no edge at all carried both (0 of 240), so the label was stable across the 120 cycles; a flip is possible in the engine but was not observed here.


## What this does and does not license

- It answers, for one seed, whether the band is served at 112: 3 of 3 on the shipped allocation and 3 of 3 when transitions get the whole window.
- A rank is the edge's position in the ceiling call's list. `Min rank at 112` is the smallest rank the edge reached in 120 cycles, so a minimum above 112 means the allocation was never the binding constraint on this seed; a null minimum means the edge was not constructed at all and `Cycles in universe` is zero.
- The recorded split counts in the artifact are the observer's own call. For the all-transitions arm they are taken before this arm truncates to 112, so the returned window is the comparable field across arms.
- It does not establish that serving these edges changes assertion, conversion or capability: the asserted-set counts are reported, not interpreted.
- It is not a cap-112 block result, not a preregistered comparison, and not a mechanism. The registered comparator, Q1 and Q2 remain unrun.
