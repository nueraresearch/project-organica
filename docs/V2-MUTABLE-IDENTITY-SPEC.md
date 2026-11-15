# V2 mutable-identity primitive — specification

**Status:** `PLANNING ONLY. No code, no cells, no engine change. Nothing here is authorised.`
**Serves:** requirement 6 of [`DECISION-V2-CHARTER`](DECISION-V2-CHARTER.md) (draft, unsigned) — a stored composite, an
identifier assigned independently of content, and a mutation that cannot alter a shared part.
**Does not amend V1.** V1 stays frozen at its pin; nothing in this document changes `organica/` or any published artifact.

## 1. The problem this has to solve

Measured, not assumed ([`V1-STRUCTURAL-MODEL`](V1-STRUCTURAL-MODEL.md) §5–§6a):

| V1 property | Measurement | What a primitive must supply |
|---|---|---|
| the composite is not stored | structures recomputed each consolidation | a table that holds it |
| identity is content identity | 177 paths over 158 node sets; 19 node sets emitted in **both directions** across cycles | an identifier that survives a direction change |
| the archive cannot name one | no `docs/*.json` and no A1 part contains a loop id | a key that can be recorded and cited |
| mutation is path membership | spill is a theorem given shared pairs | a mutation that cannot touch a non-member |

The primitive is therefore not "add an id column". It is a stored, addressed, **revisable** object layered beside the pair
graph — and it must not alter the graph, or V1's selection and counts change and the lineage comparison dies.

## 2. The object

A **composite** is a stored object with:

- `id` — opaque, allocated once, never derived from content (§3);
- `version` — incremented on every successful mutation;
- `members` — ordered references to **atoms**, each reference carrying the atom and the atom version it is bound to;
- `canonical_key` — a normalised description used **only** by the registry to recognise a re-detected structure (§4); it is
  never the identity, and changing it does not change the id;
- `created_cycle`, `retired_cycle` — lifecycle, with tombstones rather than deletion.

An **atom** is a member of the frozen substrate's vocabulary — a tag pair `(a, b)` — and it is *immutable*. Atoms are never
edited; a composite that needs a different atom binds a different one.

## 3. Identifier semantics

| Id | Invariant | Why |
|---|---|---|
| `I1` | The id never changes for the lifetime of the composite, including across version bumps, member changes and a direction flip. | The measured failure was identity changing when direction changed. |
| `I2` | The id is not a function of the members and cannot be computed from them. | A content hash is a label: it changes when content changes, so it cannot survive revision. |
| `I3` | Ids are never reused after retirement; a retired id resolves to a tombstone. | Reuse would silently alias two objects in the archive. |
| `I4` | Retrieval accepts the id and only the id; content queries may filter but never select a unique composite. | Selection by content is re-identification, not addressing. |
| `I5` | A version is not an identity: `(id, version)` names a state, `id` names the object. | Mutation needs both, and conflating them loses one of the two. |

**Allocation.** Ids come from a monotone counter in a `composite_ids` table, or a `uuid4` where a counter would leak
ordering. The choice is recorded with the primitive, because "monotone" and "opaque" trade off: a counter is auditable, a
uuid is unguessable.

## 4. Registration: how a structure becomes an object

Creation is the one place content matters, and it is a **registration** step, not an identity:

1. Consolidation detects a candidate structure (e.g. a 3-cycle).
2. It computes the `canonical_key`: the node set, **direction-free**, and sorted — so `(a,b,c)` and `(a,c,b)` collide by
   construction.
3. `register(canonical_key)` returns the existing composite's `id` if the key is known, otherwise allocates a new id and
   stores the key.
4. If the detected direction differs from the composite's recorded direction, that is a **mutation** (§5, `set_direction`)
   — not a new object.

This is precisely what the measurement asks for: 19 node sets emitted in both directions become one composite with one id
and a direction that changes, instead of two ids that never coexist.

**Registration must be deterministic.** Two cycles that detect the same key must resolve to the same id regardless of
iteration order; the registry is keyed on `canonical_key` with a uniqueness constraint, and a duplicate insert is an error
rather than a silent second object.

## 5. Mutation semantics

Operations: `create` (via `register`), `add_member`, `remove_member`, `replace_member`, `set_direction`, `fork`, `retire`.

| Id | Guarantee | Enforcement |
|---|---|---|
| `M1` | A mutation on composite `c` changes only rows whose `composite_id` is `c`, plus atoms created for `c`. No other composite's resolved member set changes. | Every mutation statement carries `WHERE composite_id = ?`; a test asserts a bystander composite is byte-identical before and after. |
| `M2` | Atoms are immutable, so a member change cannot alter a shared pair's count or any other composite's binding. | No `UPDATE` on the atom table exists. |
| `M3` | A mutation is atomic and versioned: it either applies fully at `version + 1` or not at all, and a stale `version` is rejected. | Single transaction; compare-and-set on `version`. |
| `M4` | `retire` writes a tombstone and preserves the id; no later allocation may reuse it. | `retired_cycle` set; allocation checks the id is unused including tombstones. |
| `M5` | A mutation never edits the frozen graph: counts, `precedes`, `cooccurrences` and `tag_counts` are read-only to this layer. | The primitive owns its own tables; a test asserts V1's graph tables are unchanged by every operation. |

`fork` exists so that a branch of a composite's history can be named rather than silently overwriting: it allocates a new
id and copies the member references (not the atoms). It is the only operation that creates an object from another.

## 6. The collision rule

The measured spill comes from shared pairs. The rule that removes it:

> **A composite never edits an atom. When a composite needs a binding that any other composite also holds, it binds its own
> reference to the atom version it needs; the shared atom is not touched.**

Consequences:

- **No copying of atoms is required** — the atom table stays a single shared vocabulary, which preserves V1's count
  semantics and storage profile.
- **No reference-count split is required** — because atoms are immutable, sharing is free; what is per-composite is the
  *reference and its version*, not the atom.
- **Removal cannot spill**: removing a member removes a reference, and no other composite holds that reference.

This is copy-on-write at the level of *bindings*, not of atoms. It is the cheapest rule that satisfies `M1` and `M2`, and
it is the reason the primitive does not need ownership of shared structure.

## 7. What the primitive does not fix

- It does not make the composite *predictive*. A stored, addressable object that carries no information beyond its atoms
  will lose the earning test (§8), and the primitive will then be bookkeeping.
- It does not give the composite a semantics. What a composite *means*, and whether a theory is a composite of composites,
  is the charter's question, not this specification's.
- It does not change V1, and it cannot be validated against V1's measurements — it needs its own build and its own freeze.

## 8. The earning test this primitive must pass

Requirement 7 of the charter, made concrete:

1. **Prediction arm.** Use the addressed composite's members to predict the next asserted edge, against a baseline that uses
   the same atoms' pair counts and nothing else. The composite must beat that baseline on held-out cycles.
2. **Control arm.** Intervene on one composite (`retire` or `remove_member`) and measure the effect on its members only,
   with a bystander composite as the control. A tie on the bystander is a *pass* for `M1`; a tie on the members is a *fail*
   for the primitive's usefulness.
3. **Decision rule, fixed before the build.** If the prediction arm's interval includes zero, the primitive is
   **bookkeeping** and the charter fails at its first experiment. That outcome is a result, not a reason to add features.

## 9. Non-goals

No self-model, no Generation 9, no Phase A primitive change, no modification of the six design laws, no claim that this
reaches G4–G8, and no authorisation to build. This document exists so that the charter can be argued about concretely.

## 10. The open questions, argued

Each question gets a recommendation, the reason it beats the alternatives, and what would change it. These are
*recommendations for the charter*, not decisions: nothing here is adopted until the charter is signed.

### 10.1 Are members atoms or carriers?

Three levels, not two. `0` = atom (a tag pair, immutable, shared). `1` = composite whose members are atoms — this is
exactly a V1 carrier, now stored. `2` = composite whose members are composites — a theory candidate.

**First, a precision the question hides: members are edges, not tags.** A 3-cycle over tags `{a, b, c}` is a composite of
three *pair bindings*; the tag triple is the canonical key, not the member list. This matters because a set of three tags
whose third edge is absent is not a carrier at all, and because the baseline the primitive must beat is a table of pair
counts — the member is the unit whose count the baseline uses.

| Option | Verdict |
|---|---|
| **A. Atoms only** | Simple, and it covers the first experiment. But it makes "a theory is a composite of composites" unrepresentable *by schema*, so the primitive would decide a substantive question by accident. |
| **B. Carriers all the way up** | No base case. Level 1 needs stored anchors before anything can exist, so the first build stalls on an object it has not defined yet, and storage grows multiplicatively with depth. |
| **C. Typed members, homogeneous per composite** | **Recommended.** A composite declares its member level; all members share it. Level 1 is the first build; level 2 is permitted by the schema but unbuilt. |

**Argument.** The charter's first experiment needs an object whose intervention can be compared with V1's spill, and that is
a level-1 composite: a V1 carrier is a set of pairs, and the spill is defined over pairs. Level 2 is the question the charter
actually cares about — *is a theory a composite of composites?* — but building it first means paying for two unvalidated
layers at once, and a failure at level 2 could not be attributed between them.

**Homogeneity is not tidiness.** If a composite mixed atoms and composites, an intervention's effect could not be attributed
to a level, and the earning test would lose its denominator. Homogeneity keeps every composite commensurable with its own
level's baseline.

**What would change it:** if the first experiment requires a composite whose parts are themselves composites (testing
whether a theory predicts better than its constituent carriers), level 2 must be built before the test. The schema already
allows it; only the order changes.

### 10.2 What normalisation makes rotated paths collide deterministically?

Canonicalisation must be declared **per structure kind**, never guessed:

| Kind | Canonical key | Justification |
|---|---|---|
| `cycle3` | sorted tag triple | measured: 177 directed paths over 158 node sets, so 19 keys carry two directions and no key carries two different node sets |
| `cycle_n` (n > 3) | lexicographically least of the `2n` rotations of the path and its reverse | rotation- and direction-invariant, O(n), collision-free up to exactly those two symmetries |
| `path` (open) | least of the two orientations **only if the kind is declared undirected**; otherwise the ordered path itself | an open chain's direction can carry meaning, and merging it would silently delete information |

**Invariant.** A canonicaliser may merge two detections into one object only when the merge is justified by the structure
kind, and never across kinds. **Acceptance test, already satisfied by the measurement:** applying `cycle3` to the 177
measured paths must yield exactly 158 keys with multiplicities `{1: 139, 2: 19}` — a key count equal to the node-set count,
and no key mixing two different node sets.

**What would change it:** a structure kind whose two orientations are semantically distinct (a causal chain, a sequence)
must not use a direction-free key at all; it keeps its order, and `set_direction` does not apply to it.

### 10.3 How is the store compacted without changing a resolution?

**Argument.** Atoms are immutable *values*, so an atom unreferenced by any composite — live or retired — can be dropped and
rebuilt identically from the pair graph on demand. Reclamation is safe in a way it would not be if atoms were editable:
nothing is lost that cannot be recomputed, and no live resolution depends on the atom's row existing.

**Recommendation.** Reference-count references, not atoms. Reclaim an atom at zero references across live *and* retired
composites. **Never reclaim** a composite id, its canonical key, or its tombstone — that is the part of the store which is
not reconstructible, and reclaiming it would let a later id alias an earlier object.

**Invariant.** For every live composite, the resolved member set before and after compaction is identical. A compaction
that changes one resolution is a bug, not a trade-off.

**Open sub-question:** whether retired composites keep their member references. Recommendation: keep them — they are the
evidence for the control arm, and a tombstone whose members were dropped can no longer prove what it was.

### 10.4 Is registration cheap enough to run per detected structure?

**Cost is not the problem.** V1 emits 1,299 carrier appearances over 120 cycles, 177 distinct: about eleven detections per
consolidation against an indexed uniqueness check. The primitive could register everything at negligible cost.

**The problem is semantic.** Registering on first detection makes the object population an artifact of detection thresholds:
a structure seen once and never again becomes a permanently named object, and "how many composites exist" stops meaning
anything.

**Recommendation.** Admit on **total appearances** `m`, not on consecutive appearances — precisely because direction flips
make consecutiveness brittle: a triangle alternating direction could never accumulate a streak while being perfectly stable
as an object. Until admitted, a structure is a *candidate*, tracked by key but not given an id. The first experiment uses
admitted objects only, so that "addressed" means something; candidates are recomputation, i.e. V1.

**What would change it:** if admission by stability biases the population toward high-frequency structures in a way that
favours the pair-count baseline, the threshold must be lowered, or the arm must be run over candidates too — and that
choice must be declared before the build.

## 11. Recommendation summary

| Question | Recommendation | Rejected |
|---|---|---|
| Members | edges as members, tags as the key; homogeneous typed members; level 1 built first, level 2 permitted but unbuilt | atoms-only (decides a substantive question by schema); carriers-only (no base case); tags as members (a missing third edge would still look like a carrier) |
| Canonicalisation | per-kind: sorted triple for `cycle3`, least rotation/reflection for `cycle_n`, preserve order for open paths | one global normalisation rule |
| Reclamation | reference-count references; reclaim unreferenced atoms; never reclaim ids, keys or tombstones | never reclaim; reclaim ids |
| Registration | admit on total appearances `m`; candidates carry no id | register on first detection; register per streak |
