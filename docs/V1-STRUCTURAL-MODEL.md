# V1 structural model — the ontology of the stored object

**Status:** first pass, derived from the frozen engine's code and committed artifacts. **No experiment was run for this
document, and it makes no behavioural claim.**
**Scope:** Organica 1 at the `v0.9.0` pin. Every code reference is to the frozen files; if any of them changes, this
document is void for that build and the test beside it says so.

## 1. Why this exists

Three results have been read as separate failures: the ranking ceiling (precision never above 0.3438, coverage needing
240–244 asserted edges), the readout result (no held-out gain, 0.005647 nats of headroom), and A1's `VOID` (510 of 2,785
non-target rows over tolerance). This document asks whether they are three failures or one architecture, by describing
what the engine actually stores, retrieves and manipulates.

It follows a distinction the record has not been using: some limits are **empirical** (what happened) and some are
**structural** (what must happen, given the code). Only the first kind needs a run.

## 2. What is stored

The substrate is six tables: four carry content, one is a counter, and one is key/value metadata (`organica/memory.py`):

| Object | Shape | Key | Written by |
|---|---|---|---|
| `events` | `id, time, source, event_type, content, tags` | `id TEXT PRIMARY KEY`, a `uuid4` (`memory.py:262`) | `MemoryService.store` (`memory.py:260`) |
| `cooccurrences` | `tag_a, tag_b, count` | `PRIMARY KEY (tag_a, tag_b)` (`memory.py:118`) | `_record_cooccurrences` |
| `precedes` | `tag_from, tag_to, count` | `PRIMARY KEY (tag_from, tag_to)` (`memory.py:126`) | `_record_temporal_edges` |
| `tag_counts` | `tag, count` | `PRIMARY KEY (tag)` (`memory.py:164`) | `_record_tag_counts` |
| `meta` | `key, value` | `PRIMARY KEY (key)` (`memory.py:152`) | bookkeeping |
| `sleep_cycles` | `cycle, ran_at` | `PRIMARY KEY (cycle)` (`memory.py:176`) | `record_sleep_cycle` |

Two details are load-bearing. Sleep payloads are stored as **events with `event_type="sleep"` and are explicitly kept out
of the graph** (`memory.py:276`–`290`), so the operative substrate is the pair graph, not the payloads. And the event
`id` is a random uuid, not a content address: nothing in the engine reads it back.

## 3. What is retrieved

Three retrieval surfaces, none of which takes an identifier:

- **Recency and type**: `recent(n, event_type)` orders by `time DESC, rowid DESC` (`memory.py:432`); `since()` by time.
- **Substring and tag match**: `search()` is a `LIKE` over `content` or `tags` (`memory.py:449`).
- **Typed prior payloads**: the previous cycle's sleep events are re-read and filtered by `type` and a confidence
  threshold — `prior_schemas = [c for c in prior if c.get("type") == "schema_candidate" and … >= STABLE_THRESHOLD]`
  (`sleep.py:204`) — then matched by their fields, never looked up by id.

Structures are **recomputed, not fetched**. `_build_loops(temporal)` rebuilds every 2- and 3-cycle from `precedes` on
each consolidation (`sleep_extraction.py:251`), giving each loop an id that is a hash of its own nodes
(`_make_id("loop", a, b)`, `candidates.py:20`). The id is a *derived label*: there is no row to fetch between cycles, so a
loop has no identity that outlives the computation that produced it.

## 4. What is manipulated

A1's intervention is a filter, not a mutation. `carrier_filter` keeps exactly those loops and dreams whose path does
**not** contain a blocked edge (`a1_arms.py:76`); the `A-` arm filters the served prediction window; the `Y-` arm filters
the assertion readout. Nothing in the store is edited — the blocked set is applied while the cycle's payload is assembled,
and the next cycle's graph is built from the same pairs as before.

So the manipulated object is the **derived carrier set**, and its identity is its edge content.

## 5. The five questions

**1. What object is actually stored?** Event rows plus three content-keyed aggregates over tag pairs. The aggregates have
no structure beyond a count.

**2. What object is actually retrieved?** Windows, matches and typed payloads; and, for behaviour, structures recomputed
from the pair graph on demand.

**3. What object is actually manipulated?** A filtered view of the recomputed structures and of the served/asserted
outputs — never a stored object.

**4. Can those ever be distinct?** They are distinct as sets — what is stored is never what is retrieved as a structure —
but they are not *addressable* as distinct objects: nothing names a stored structure and operates on it.

**5. Does the architecture contain a true addressing primitive anywhere?** **No — no explicit one.** There are
identifiers (a random uuid on events, a content hash on candidates) but no primitive that *takes* an identifier: no
retrieval by id, no mutation by id, no reference to a stored composite from the graph. An address in the sense the A1
estimand needs — name a structure, then operate on that structure alone — does not exist here. This is the central
structural fact of V1, and it is derivable from the code rather than from any run.

**What that "no" covers, and what it does not.** It establishes the absence of an **explicit** address. It is *not* a
claim that no **functional** address exists: if some key computed from the stored state — an exact path signature, a
subgraph hash, a feature vector unique to one carrier — reliably isolates a composite, then an address has effectively
emerged without ever being stored. Whether such a key exists is **open**, and it is a different question from the one this
document answers.

The distinction matters because the two addresses buy different things. A derived key would buy *selection and
retrieval*. It would not buy *non-colliding mutation*, because the mutation still acts on shared pairs, and every carrier
that traverses them moves with it. The A1 estimand needs the second, so a derived address — even a perfect one — does not
satisfy the charter's mutable-identity requirement.

## 6. The spill is a theorem, given the representation

Let *G* be the directed pair graph with counts (`precedes`), and let the carrier set *C* be the paths of length 2–3 over
*G* that consolidation returns. Let the block be an edge *e*. The intervention is:

> *R(e) = { c ∈ C : e ∈ pairs(c) }* — remove every carrier whose path contains *e*.

Then for any other edge *f*, the change in *f*'s carrier support is

> *−|{ c ∈ C : {e, f} ⊆ pairs(c) }|*,

the number of carriers that carry both. **The spill is forced by the representation**, not by the particular block: as
soon as carriers are paths over a shared graph and removal is defined by path membership, removing one edge's carriers
removes carrier support from every edge that shares a path with it.

What is **empirical** is the magnitude: 510 of 2,785 non-target rows over tolerance, a maximum K/Y delta of 0.575 against
a 0.05 tolerance (A1's C4). Those numbers depend on how often the world's edges share carriers; the existence of the spill
does not.

A corollary worth stating plainly: **A1's `VOID` was derivable before the block ran**, from the carrier inventory alone,
by computing *R(e)* for the target block. The run measured the size of the spill, not its occurrence.

## 7. What this makes unsurprising

- **The ranking ceiling.** Layer-1 strength is `count / max(source_freq, 1)` (`memory.py:282`–`290`), a function of pair
  counts only. No ordering available to the engine can express "this structure matters" independently of frequency, which
  is why precision stayed flat at 0.3438 as the budget rose and why a per-source rule did no better.
- **A1's `VOID`.** Section 6: a removal defined by path membership cannot be edge-local while carriers share pairs.
- **The readout result.** The only thing stored about an edge is its pair count; nothing stores a prediction relation
  between structures. A structure that carries no information beyond the counts it is made of cannot out-predict those
  counts — which is consistent with an interval crossing zero and 0.005647 nats of headroom. (This is a consistency
  argument, not a theorem: the confirmatory test is the measurement, this is the reason to expect it.)

## 8. What this does not establish

- It does **not** say nothing is stored. Events and counts are stored, and they carry the world's statistics.
- It does **not** say addressability is impossible in principle — only that this code has no address and that every
  operation it offers is keyed by time, type, content or count.
- It does **not** convert the measured magnitudes into derivations.
- It does **not** test any behavioural claim, and it licenses no result by itself.
- It does **not** settle whether a functional (derived) address exists; §5 says what would follow if one did.

## 9. What would refute it

Three deliberate falsifiers, which is what makes this a model rather than a description:

1. **An address appears.** If a stored composite gains a stable identifier *and* a mutation that leaves shared parts
   untouched, then §5 and §6 are void for that build. `tests/test_v1_structural_model.py` parses the substrate's schema and
   retrieval surface and fails when that happens, so the claim cannot rot silently.
2. **A local removal is found.** A block whose carrier set is disjoint in pairs from every non-target edge would be a
   counterexample to §6's corollary; §6 predicts none exists while carriers are paths over a shared graph.
3. **Precision exceeds the ceiling with a count-derived key.** If a count-based ordering clears 0.3438 on the same world
   family, §7's first bullet is wrong.
4. **A derived address is found.** A key computed from the stored state that isolates one composite and nothing else
   would refute the *functional* reading of §5, while leaving its explicit claim and the mutation argument intact — which
   is why the two are stated separately.

## 10. What follows for the programme

The next lineage should not ask another behavioural question first. It should ask, in code: *what object would have to
exist for the estimand to be expressible?* The answer this document implies is a stored composite with a stable address
and an operation that can change it without changing its parts — a primitive V1 does not have, and which no amount of
carrier blocking can substitute for.
