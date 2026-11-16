# `DECISION-V2-PRIMITIVE-BUILD` — authorise the primitive build, not the cell

**Status:** `ADOPTED 2026-11-16 — THE BOUNDED BUILD IS AUTHORISED; THIS RECORD WRITES NO CODE`

**Decision ID:** `DECISION-V2-PRIMITIVE-BUILD-1` · **Date:** 2026-11-16

**Instruction:** adopt the decision that authorises building the mutable-identity primitive, without writing the primitive
(owner, 2026-11-16).

**Narrows:** the planning-only status of [`V2-MUTABLE-IDENTITY-SPEC`](V2-MUTABLE-IDENTITY-SPEC.md), and only enough to
build the object its §2–§6 specify. **Leaves untouched:** the frozen engine, the readout pin, `m`, the endpoint, the seed
block, and [`DECISION-V2-FIRST-CELL`](DECISION-V2-FIRST-CELL.md), which still authorises no cell until it is signed.

## 1. The decision

1. Authorise a bounded build of the level-1 mutable-identity primitive — a separate SQLite store with a monotone
   content-free id, a canonical-key registry, versioned member references, copy-on-write add and remove, tombstones and
   reference-count reclamation — solely so the A2–A5 gates can be run.
2. The build is confined to one new benchmark module and its tests; it writes only its own scratch store, never the live
   memory.db, and it may not change the readout, `m`, the endpoint or any frozen engine file.
3. The build stops when A2–A5 have a gate record and the named tests pass; running the cell still needs
   `DECISION-V2-FIRST-CELL`, and any second feature needs a new decision.

Adoption authorises the build; it does not perform it. This record writes no module and no test, and the gate record
remains A1 PASS, A2–A5 NOT RUN until the build lands and the gates are rerun.

## 2. Why the cell is blocked

The A1–A5 gate record is committed and it does not pass: **A1 PASS, A2–A5 NOT RUN**. The primitive those four gates test
does not exist. The readout keys membership by the canonical tag set and recomputes it in memory; there is no stored
composite id, no mutation API, no rebuilt store and no id/version/tombstone sequence. The sizing artifact is a static
estimate, not the page count A4 requires ([`V2-FIRST-CELL-GATES`](V2-FIRST-CELL-GATES.md)).

The runner treats `NOT RUN` as a gate failure. Signing the cell authorisation now would therefore write a `VOID` artifact
without executing a seed: the block would be spent to learn that the gates were never run. The missing object is the
primitive, not the authorisation.

## 3. What is built, and what it is not

| | |
|---|---|
| **Module** | one new file, `benchmarks/v2_primitive.py`; the frozen `organica/` tree is not touched and the engine pin does not move |
| **Level** | level 1 only: members are undirected edges, the key is the canonical tag set, level 2 is unbuilt |
| **Admission** | total appearances at `m = 2`, the value the pre-registration fixed; the build takes it as a parameter but does not retune it |
| **Identity** | a monotone counter in its own table; ids are never derived from members, never reused, and a retired id resolves to a tombstone |
| **Registry** | canonical key → id, deterministic; a repeated key returns the existing id, a duplicate insert is an error |
| **Members** | per-composite references to immutable edges; add and remove are copy-on-write at the binding, so no other composite's member set moves |
| **Versions** | every change is a compare-and-set at `version + 1`; a stale version is rejected; there is no per-mutation history table |
| **Retirement** | a tombstone preserves the id and the member references for the control arm; allocation never reuses the id |
| **Reclamation** | reference-counted references; unreferenced atoms are reclaimed, ids, keys and tombstones are not |
| **Store** | its own SQLite file under the scratch path, never `memory.db`; the live study is not opened for writing |
| **API** | `register`, `add_member`, `remove_member`, `retire`, `resolve`, `members`; `replace_member` is remove-then-add, and `fork` is out of scope because level 1 needs no branch. A direction flip is a registration of the same undirected key, so `I1`'s flip case is tested through `register`, not a mutation |

The build may add private helpers and schema migrations inside its own module. It may not add a second public object type,
a readout change or a consumer: requirement 6(h)'s consumer already exists in the readout adapter.

## 4. What this does not authorise

No cell, no arm, no seed spent, no `m` change, no readout or endpoint change, no engine file, no level 2, no `fork`, no
per-version history and no promotion. It does not authorise a capability, transfer or G4 claim, and it does not make the
primitive predictive: the earning test still decides that, and it is still allowed to fail.

## 5. Acceptance and stop condition

The build is accepted only when the gate suite can move A2–A5 off `NOT RUN`:

| Gate | What must hold |
|---|---|
| **A2** | the specification's `I1`–`I5` tests pass, each written to fail before the implementation and shown to do so |
| **A3** | `M1`–`M5` pass, with the bystander resolved member set asserted byte-identical before and after each mutation |
| **A4** | a page-count of the rebuilt store at `m = 2` is at most **135,168 bytes** on the base world, with no per-mutation history table, and compaction restores every live composite's resolved member set exactly |
| **A5** | two replays of the same stored detection stream produce the same keys, member resolutions and allocation order; ids are monotonic and retirement never frees one |

A1 stays as recorded: the rule and the two committed regressions. A failed acceptance criterion is recorded, not tuned
away, and the gate suite remains the judge. The build stops when the gate record is regenerated and the tests pass; it
does not continue into the cell. The cell still needs its own signed authorisation and its own gate record, and any
second feature — level 2, `fork`, history, a changed `m` — needs a new decision.

## 6. Rejected alternatives

**Build the primitive inside `organica/`.** Adding a module moves the engine pin and the frozen reference object, and the
first experiment's primitive can live in the harness without changing V1.

**Authorise the cell and let A2–A5 fail there.** The runner treats a failed or unrun gate as `VOID`, so the block would be
spent without scoring an arm.

**Use a content hash as the id.** A hash is a function of the members, so it changes when the object is revised; `I2` is
the invariant the primitive exists to satisfy.

**Keep a history row for every version.** A4 forbids a per-mutation history table and the sizing puts it about a third
higher; the current version plus a tombstone is the specification's surface.

**Build the primitive and run the cell in one act.** It would confound the primitive's validity gates with the cell's
endpoint, and the cell still needs its own authorisation and its own seed block.

## 7. Evidence

- [`V2-MUTABLE-IDENTITY-SPEC`](V2-MUTABLE-IDENTITY-SPEC.md) §2–§6 — the object, identity, registration, mutation and collision rule.
- [`DECISION-V2-PRIMITIVE-RESOLUTIONS`](DECISION-V2-PRIMITIVE-RESOLUTIONS.md) — the four adopted resolutions.
- [`V2-FIRST-CELL-GATES`](V2-FIRST-CELL-GATES.md), `docs/v2_first_cell_gates.json` — A1 PASS; A2–A5 NOT RUN and why.
- [`V2-PRIMITIVE-SIZING`](V2-PRIMITIVE-SIZING.md), `docs/v2_primitive_sizing.json` — the 135,168-byte budget at `m = 2`.
- [`V2-FIRST-EXPERIMENT-PREREGISTRATION`](V2-FIRST-EXPERIMENT-PREREGISTRATION.md) §6 — the A1–A5 acceptance gates.
- `benchmarks/v2_first_cell_runner.py` — the guard that treats a not-run gate as `VOID`.

## 8. Signature

Adoption authorises the bounded build in §1 and nothing else; the cell remains unauthorised.

| | |
|---|---|
| **Owner** | owner |
| **Adopt / reject** | `ADOPTED` |
| **Date** | 2026-11-16 |
| **Note** | The build is authorised; this record writes no code. |
