# Formation provenance — instrument specification

**Status: instrument built and proven on synthetic controls. It has not been run on
any study cell, calibration or confirmatory.** No threshold, no verdict and no seed
appears in this document; the prospective study that would use it is a separate
artifact, written after these controls pass.

Related: `benchmarks/formation_provenance.py`, `benchmarks/provenance_trace.py`
(the ancestry tracer this complements), `docs/PROVENANCE-ANALYSIS-PLAN.md` (the
closed diagnostic), `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` §20 (the closed
study).

## 1. The question

The tracer showed that prediction candidates carry **no parent ids** on these
cells, so their origins cannot be recovered from stored lineage. The question this
instrument exists for is therefore asked earlier:

> Which stored events supplied the tag pair a prediction asserts, and were those
> source rows the world's or the organism's own sleep payloads?

It is a question about recorded evidence, not about usefulness. Nothing here
measures whether the knowledge transfers.

## 2. What is captured, and when

At every sleep cycle, before the candidate is stored, a read-only hook:

1. calls the engine's own `SleepService._build_predictions(temporal, freqs)` and
   returns its list **unchanged**;
2. writes one **formation record** per candidate: cycle, id, source, target,
   generation, `parent_ids` (recorded even when empty, so "none" is a datum), the
   engine's own `temporal_count`, and the **origin** of the `(source, target)` pair.

The origin comes from a store-time recorder that mirrors
`MemoryService._record_temporal_edges` exactly: the same `LIMIT 3` window,
including the row just stored, and **no event-type filter**, because the engine has
none. The one thing it adds is the source row's `event_type`, which is what makes
world and self distinguishable at all.

The unit of attribution is therefore a **transition** — `(prior event row, stored
event row)` — never a count of observations that "supported" a belief, and never an
event id written into a payload.

## 3. Origin classes

| class | meaning |
|---|---|
| `pair_world_attributed` | every recorded transition behind the pair started at a world event |
| `pair_self_sourced` | every recorded transition started at a sleep payload |
| `pair_mixed` | both occurred |
| `pair_unattributed` | no recorded transition carries the pair |

`pair_unattributed` is **not zero support**. It means the recorder did not see the
events behind the edge — a recorder started mid-run, for instance — and it is
reported as its own category rather than folded into `pair_world_attributed` or
`pair_self_sourced`. This is the rule the tracer applies to unresolved ancestry, for the
same reason.

Attribution is **cumulative to the cycle** in which a candidate is met: the
transition set is everything recorded up to that store, because that is the
population the temporal graph's count aggregates. Re-reading the survivors each
cycle gives the growth curve of that support.

## 4. What it does not establish

- **Not observation-level origin.** A world source row says which kind of row
  carried the tags, not that the tags were first learned there. A sleep payload
  relaying world vocabulary produces `pair_mixed` or `pair_self_sourced` support, which is why
  the classes are kept apart rather than pooled.
- **Not usefulness.** Provenance is not generalization: a candidate with perfect
  world attribution may still be useless on held-out events, and one with
  self-sourced evidence may still transfer. A provenance measure on its own must
  never be reported as evidence that knowledge is reusable.
- **Not a mechanism claim.** The hook observes; it does not intervene, and it may
  not be used to argue that a structure *would* have formed differently.

## 5. Controls (they must be able to fail)

Run with `python -m benchmarks.formation_provenance --controls`. Each fixture is
synthetic, built in a scratch database, and has a known answer:

1. a world-only pair is `pair_world_attributed`;
2. a pair whose source rows are sleep payloads is `pair_self_sourced`;
3. a pair with both is `pair_mixed`;
4. a pair the recorder never saw is `pair_unattributed`, not world and not zero;
5. **the classifier can fire** — deleting the world transitions from the mixed
   recorder must flip it to `pair_self_sourced`;
6. **the hook does not change the engine** — candidates from the plain service and
   the recording service are compared by id, strength and count;
7. **the neutrality check can itself fail** — a deliberately mutating subclass must
   be detected;
8. **the axis is live** — reinforcing an edge must strictly increase its recorded
   world transitions between formation records.

A control that cannot fail proves nothing (AGENTS rule 25), and an observer that
changes behaviour is not an observer (rule 17c).

## 6. Stop condition

This build is closed when the eight controls pass. After that it may be **fixed**
if found wrong; no field may be **added** to satisfy a later result, and doing so
would be a new instrument requiring its own controls.

## 7. The prospective study (not yet written)

The question the instrument exists to serve:

> Can a candidate's recorded origins be traced, and does that trace predict
> successful held-out generalization?

Any study of that question must be preregistered separately, with **fresh seeds**,
an endpoint tied to held-out generalization rather than to provenance, and the
closed study's confirmatory seeds `20261207–20261226` left untouched. The closed
study's failure stays intact: it does not establish transfer failure, and it does
not establish anything either way about origins.
