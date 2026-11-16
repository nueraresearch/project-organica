# The code as evidence: what V1 already does, and what that changes

**Status:** a reading of the frozen engine. It adds no measurement, authorises no code, and does not move a verdict.

**In one paragraph.** Four of the project's live conclusions are decided in source rather than by any experiment, and reading
the source corrects the record on three of them. A carrier is not an unrepresented object: it is a report written to the
event store every cycle, with an id, a path and a strength that is reinforced by 0.05 or decayed by 0.8 in isolation. What V1
does not have is a composition that can be *edited* — no code path mutates a path — or any consumer that uses a carrier's
*cycle*: the only reader folds its tags into a bag for meta-concepts, and Layer-2 processes are composed from prediction
candidates only. So "V1 has no mutable identity" is too wide, "the composite is not stored" is too wide, and the V2
primitive's real delta is narrower than the charter assumed: a content-free id, a membership mutation, and a consumer.
The identity instability that was measured across 19 node sets is not an accident of hashing — the persistence key includes
the path's direction, so V1 deliberately treats the two orientations of one triangle as different candidates. Every claim
below is anchored to source and guarded by `tests/test_code_evidence.py`, which fails if the code stops matching.

## 1. Why the code is the stronger evidence

An experiment bounds behaviour on the worlds it sampled. The source defines behaviour on every world the engine can build,
including the ones the arms will never run. When the two disagree, the code wins about what the engine *can* do and the
experiment wins about what it *did*; the mistake is letting a measurement's scope decide a design question the code has
already settled.

## 2. What the code settles

| Claim | What it fixes | Kind |
|---|---|---|
| `carriers-are-reports` | each cycle builds `LoopCandidate` objects from the temporal graph; nothing is looked up by id | by construction |
| `identity-is-content-derived` | the id is `sha256(path)[:8]` — a label computed from composition, not an allocation | by construction |
| `identity-is-direction-bearing` | `canonical_cycle` rotates but never reflects, and the persistence key joins the path in order | by construction |
| `one-direction-per-cycle` | the dedupe key is the sorted triple with a call-local `seen`, so one cycle emits one orientation | by construction |
| `carriers-are-capped-and-entropy-ranked` | at most 15 carriers, lowest path entropy first | by construction |
| `carrier-rows-are-persisted` | every cycle's carriers are written as `sleep:loop_candidate` events | by construction |
| `carriers-have-isolated-numeric-mutation` | +0.05 reinforce, ×0.8 decay, prune below 0.15 with a retired record | by construction |
| `no-membership-mutation-exists` | no assignment to a path anywhere; the only stored-path reference is an equality test | absence |
| `only-tag-bag-readback` | meta-concepts read a carrier's path only to fold its tags into reference counts | by construction |
| `processes-read-predictions-not-carriers` | Layer 2 is composed from prediction candidates, never from carriers | by construction |
| `prediction-space-is-count-gated-and-entropy-ranked` | count ≥ 5, ordered by target entropy, then probability, then count | by construction |
| `graphs-are-world-only-and-lookback-local` | three-event lookback, sleep payloads excluded, world-scoped counters | by construction |
| `retention-bounds-the-candidate-layer` | newest 4,000 sleep events readable, 20,000 rows retained | by construction |
| `the-engine-composite-means-generation-two-plus` | `composites_created` counts Layer 2+ only, not carriers | by construction |

## 3. Three corrections to the record

**X1 — "the composite is not stored" is too wide.** A carrier *report* is stored every cycle, with its id, path, strength
and evidence. What does not exist is a composite whose composition can be mutated and which a consumer reads as a unit.
The precise statement is: *V1 stores a recomputation's output, not an object of cognition.*

**X2 — "V1 has no mutable identity" is too wide.** The id is stable while the content is stable, and the strength is updated
in place every cycle; that is a mutable record. What is missing is *durable* identity (a direction flip orphans the id, and
the old id decays to death) and *compositional* mutation.

**X3 — "the archive cannot name a carrier" holds only for the published artifacts.** No `docs/*.json` artifact or A1 run
part contains a loop id, which is what the scan checked. The live store can name one: `sleep:loop_candidate` rows carry it.
The claim should be read as a statement about the archive, and it is worth saying so explicitly wherever it is quoted.

## 4. What the code explains about the measurements

- **177 paths over 158 node sets, 19 in both directions, none in one cycle.** The dedupe key is the sorted triple with a
  call-local `seen`, so one call can emit only one orientation; the persistence key includes the path order, so the other
  orientation is a different candidate in a later cycle. The artifact and the source agree exactly, and the source shows
  which line to change if we wanted them to agree differently — the key, not the hash.
- **Ranking precision flat at 0.3438 across 36 measurements.** Candidates are count-gated at 5 and ordered by target
  entropy, probability and count. Every feature of the ranking is a function of the same counts the baseline uses, so no
  frequency-based ranking can separate a signal the counts do not separate. That is a property of the design, not of the
  campaign.
- **The spill is a theorem.** There is no membership mutation anywhere; `carrier_filter` removes whole paths from a pass and
  nothing else can remove an edge. The measured spill follows from the representation.
- **The store is mostly text and re-stored payloads.** Every event keeps its content, and every candidate is re-written each
  cycle, bounded by a 20,000-row retention. The primitive's 135,168 bytes is noise at that scale — the code's own comment
  records 1.65M candidate rows and 942 MB after ~500 cycles.

## 5. What the code cannot settle

`O1` whether a stored, addressed composite predicts better than the same atoms' pair counts; `O2` whether membership
mutation stays local once implemented (it can be proved by construction afterwards, not before); `O3` whether adding a
composition consumer changes selection or readout; `O4` which admission threshold `m` the charter wants. These are the only
genuinely empirical items left, and three of the four need a build before they need an arm.

## 6. What we want to know, and how the code gets us there

**The primitive's delta is three things, not five.** Storage exists (candidate rows). Identity exists (content-derived).
Isolated numeric mutation exists. Absent: a content-free id; a membership mutation; a consumer that reads composition. The
charter should be rewritten around those three, and requirement 6's "stored composite" should say *composition-bearing
object* to avoid claiming a storage capability V1 already has.

**The direction question can be answered offline, from stored rows.** Because the persistence key is a string built in
`_candidate_key`, a direction-free key can be simulated over the existing `sleep:loop_candidate` rows without touching the
engine: re-key each stored loop by its sorted tag triple, then compare reinforcement counts and deaths under the two keys.
That answers "would a direction-free identity have concentrated or scattered the evidence?" using data already on disk — no
arm, no freeze, no seed.

**The consumer question has a named insertion point.** The only reader of stored carriers is `_compose_meta_concepts`, and
it discards the cycle. Layer 2 reads predictions only. So a carrier-level readout must be added at Layer 2, and the code
shows exactly where — which is a build decision, not a measurement.

**The selection question is closed by the code.** Since the ranking is a deterministic function of counts, a better ranking
requires a different candidate space or a non-count feature. That is why the earlier "no ranking variant" conclusion was
right, and the code says why rather than the campaign.

## 7. What I would do next

1. **Guard these claims** — done in `tests/test_code_evidence.py`; 14 claims, 31 anchors, one absence check. A future engine
   change that breaks one of them is caught before a document can keep quoting it.
2. **Run the offline re-keying study** on stored rows — *done, [`V1-REKEYING-STUDY`](V1-REKEYING-STUDY.md)*. A direction-free
   key would have saved 19 identities and 16 retirements and turned 55 flips into reinforcements, with mean live strength
   0.8043 → 0.816. It confirms the specification's `cycle3` canonicalisation and leaves the consumer and mutation gaps
   untouched. The direction was replicated on a second world ([`V1-REKEYING-TWO-SEEDS`](V1-REKEYING-TWO-SEEDS.md)).
   A boundary measurement ([`V1-CARRIER-FORGETTING`](V1-CARRIER-FORGETTING.md)) then showed the prior window
   never forgets a live carrier: 147 of 177 identities retired, 30 stayed live, 0 vanished unrecorded.
3. **Then** sign or reject the primitive decision with a narrower scope: content-free id, membership mutation, and a
   composition consumer — and with the storage question retired (135,168 bytes against a store that grows by megabytes of
   event text per hundred cycles).
