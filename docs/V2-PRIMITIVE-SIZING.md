# The primitive's storage cost on a real V1 world

**Status:** `PLANNING-ONLY ESTIMATE. Authorises no code, no table, no build.`

Serves [`DECISION-V2-PRIMITIVE-RESOLUTIONS`](DECISION-V2-PRIMITIVE-RESOLUTIONS.md) and §12 of
[`V2-MUTABLE-IDENTITY-SPEC`](V2-MUTABLE-IDENTITY-SPEC.md): the charter should know what it is buying before it signs. The
numbers come from [`docs/v2_primitive_sizing.json`](v2_primitive_sizing.json); this page is rendered from that artifact by
`python -m benchmarks.v2_primitive_sizing --doc`, and a test fails if the two differ.

## 1. What was measured, and what was modelled

Two different things, kept apart:

- **Measured.** The store itself: a replay of one no-arm world (120 cycles), read with SQLite's own `dbstat` so every
  table's pages are counted, not estimated.
- **Modelled.** The primitive's tables. Nothing implements the primitive, so its four tables were created in SQLite and
  filled with the measured row counts, then measured the same way. That is a sizing estimate, not a benchmark.

Both sides use 4096-byte pages, and the per-table bytes reconcile to the store's page count except for one page —
SQLite's schema page. The store's **total** size is not bit-reproducible: the event table's overflow pages move by a page or
two between replays, which is why the identity check asserts row counts and the pair tables' pages rather than the total.

## 2. The store as it actually is

| Table | Rows | Bytes |
|---|---|---|
| `events` | 20,916 | 19,304,448 |
| `precedes` | 240 | 32,768 |
| `cooccurrences` | 24 | 12,288 |
| `tag_counts` | 16 | 8,192 |
| `sleep_cycles` | 92 | 4,096 |
| **whole store** | — | **19,374,080** |

**Events are 99.6% of the store.** The pair graph the primitive annotates is 53,248 bytes —
24 co-occurrence rows, 240 precedence rows and 16 tag rows. Any overhead figure quoted against the
whole store is really a statement about how loud the event text is; the honest comparator is the pair tables.

## 3. Admission is the lever, and it is not fixed

The decision adopts admission on total appearances `m` without fixing `m`. That matters more than any other choice here:

| Threshold | Composites | References | Primitive bytes | Ratio to pair tables | Ratio to store |
|---|---|---|---|---|---|
| `m>=2` | 115 | 345 | 135,168 | 2.538× | 0.00698 |
| `m>=3` | 97 | 291 | 90,112 | 1.692× | 0.00465 |
| `m>=5` | 66 | 198 | 73,728 | 1.385× | 0.00381 |
| `m>=10` | 33 | 99 | 53,248 | 1.0× | 0.00275 |
| `m>=20` | 20 | 60 | 45,056 | 0.846× | 0.00233 |

At the loosest threshold the primitive holds 115 objects — 72.8% of the 158 distinct carriers the world
produces — and at `m>=20` it holds 20. That is a 5.75× range in population from one unset parameter, so the
charter should fix `m` with the population it wants, not default to "seen twice".

## 4. The cost

At `m>=2`: **135,168 bytes** — 33 pages, 2.538× the pair tables it annotates, and **0.7% of the
store**.

Per composite that is 1,175 bytes, which is an upper bound rather than a marginal cost: at this scale the tables
are page-bound, so a few rows cost a whole 4096-byte page. The figure that scales is the reference count, not the byte
count.

The atom index costs 12,288 bytes at this population; without it the tables are
122,880.

## 5. References: where the sharing shows up

345 references over 24 atoms — 14.4 references per atom, three per composite. The atom table is
24 rows and is not copied per composite, which is the collision rule doing its job: sharing is free because
atoms are immutable, and what is per-composite is the reference.

## 6. Mutation does not grow the store

Under binding-level copy-on-write a member change updates one row and increments an integer, so storage is invariant in the
number of mutations. Keeping history instead — one row per version — costs
45,056 bytes at this population (180,224 against
135,168), about 33% more, and it buys a history the specification does not need.

## 7. What this does not establish

- **Not built.** The primitive side is a schema with rows, not the engine's implementation; a real implementation could be
  smaller or larger depending on its indexes.
- **One world.** 120 cycles, one seed (recorded in the source artifact, not here). No denser or longer world was sized.
- **Page-bound, and not amortised.** At 33 pages the measurement is dominated by page granularity, so the
  per-composite figure is an upper bound. Whether a larger world amortises it is now **tested and not confirmed**: four
  times the horizon and twice the density both stay at or above this figure, because the object population saturates
  against a fixed tag universe. See [`V2-PRIMITIVE-SIZING-SCALED`](V2-PRIMITIVE-SIZING-SCALED.md).
- **Store size moves.** The total is a page or two unstable between replays, so the store ratios carry that noise; the pair
  tables' pages and every row count are stable.
- **`m` is unset.** The five rows above are five different primitives, not one estimate with error bars.

## 8. What it does say

Storage is not the obstacle. At 135,168 bytes the primitive is 0.7% of this world's store and about
2.538× the pair tables it annotates — small enough that the decision to build should turn entirely on
the earning test, which is the one thing no storage measurement can answer.
