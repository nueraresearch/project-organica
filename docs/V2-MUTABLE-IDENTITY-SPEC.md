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

## 10. Open questions the charter must answer

1. Are members atoms (pairs) or carriers? Pairs keep the vocabulary frozen; carriers need the composite to hold another
   composite.
2. Is `canonical_key` direction-free for pairs only, or for longer paths too — and what normalisation makes two paths that
   differ only in rotation collide deterministically?
3. Reclamation: retired atoms and superseded references accumulate; what bounds the store, and does compaction ever change
   a resolution?
4. Does registration happen at every consolidation, and if so, is `register` cheap enough to run per detected structure?
