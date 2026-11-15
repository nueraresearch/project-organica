# Primitive sizing on a longer and a denser world

**Status:** `MEASUREMENT. Planning-only; authorises no code, no table, no build.`

Companion to [`V2-PRIMITIVE-SIZING`](V2-PRIMITIVE-SIZING.md). That page measured one 120-cycle world and reported
938.7 bytes per composite, noting the figure was page-bound and therefore an upper
bound. This page tests the note: same seed, same generator, three worlds — the reference horizon, four times the horizon, and
twice the stimulus density. Rendered from [`docs/v2_primitive_sizing_scaled.json`](v2_primitive_sizing_scaled.json) by
`python -m benchmarks.v2_primitive_sizing_scaled`.

## 1. The three worlds

| World | Cycles | Events/cycle | Carrier appearances | Distinct node sets | Objects at `m>=2` | at `m>=3` | at `m>=5` | Bytes/object at `m>=2` | Pages | vs reference |
|---|---|---|---|---|---|---|---|---|---|---|
| `reference-120` | 120 | 8 | 1235 | 110 | 96 | 85 | 68 | 938.7 | 22 | 1.0 |
| `longer-480` | 480 | 8 | 6635 | 136 | 141 | 127 | 102 | 1,016.7 | 35 | 1.083 |
| `denser-2x` | 120 | 16 | 1385 | 111 | 100 | 92 | 61 | 983.0 | 24 | 1.047 |

## 2. The expectation did not hold

The conjecture was that a bigger world would amortise the fixed page cost, so bytes per object would fall. It did not.
The four-times-longer world has **141 objects at 1,016.7 bytes each**, and the twice-denser world has
**100 at 983.0** — both at or above the reference's 938.7. Nothing here is amortising.

## 3. Why, and what would actually test amortisation

The object population saturates, not the page cost. Carrier appearances grow fourfold (1235 to
6635) while *admitted* objects grow only from 96 to 141, because the compositional
generator draws from a fixed universe of 16 tags: the number of distinct triples is bounded well below the appearance count,
and after one horizon almost every triple that can clear `m>=2` already has. Density raises counts, not structures — the
denser world found 111 distinct node sets against the reference's 110.

So a longer or denser run of this world cannot test amortisation: it saturates the thing that would have to grow. The
measurement that would is a **wider tag universe**, which the compositional generator does not provide — the scale ladders
in `benchmarks/scale_streams.py` do, and that is where a real test belongs. Until then, the honest reading of both sizings
is that a composite costs on the order of a kilobyte, flat, at every population this project can currently generate.

## 4. What this changes

- The base page's note that a world with ten times the composites would give a much smaller bytes-per-object was a
  **conjecture**, and it is now labelled as untested rather than expected.
- The cost answer for the charter does not move: at ~1 KB per composite and populations in the low hundreds, the primitive
  is tens of kilobytes against a store that reaches hundreds of megabytes. Storage is not the constraint; the earning test
  is.
- The scaling question is now a question about the **structure count**, not the horizon: to make the primitive look cheap you
  need more distinct structures, not more cycles.

## 5. Limits

One seed, one generator, three worlds. The primitive side is the same schema-with-rows measurement as the base sizing, not
an implementation. The horizons share a seed, so the two horizon worlds are the same stream truncated, not independent
worlds; nothing here estimates variance across worlds.
