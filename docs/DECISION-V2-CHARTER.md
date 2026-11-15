# `DECISION-V2-CHARTER` — commission a V2 charter

**Status:** `DRAFT — AWAITING THE OWNER'S SIGNATURE; A CHARTER, NOT A BUILD`

**Decision ID:** `DECISION-V2-CHARTER-1` · **Date:** 2026-11-15

**Narrows:** clause D1 of [`DECISION-V2-SCOPE`](DECISION-V2-SCOPE.md) (2026-10-30), the prohibition on *designing* a V2.
**Leaves untouched:** D2 of that decision — the G13-D diagnostic, which ran and is recorded — together with every frozen
engine file, every published artifact, every verdict, and the planning-only status of
[`ORGANICA-V2-DESIGN-BRIEF`](ORGANICA-V2-DESIGN-BRIEF.md).

## 1. What H2 binds, and what it rested on

Phase K's pre-committed outcome H2 reads: no task family was supported, so V2 must not be designed. `DECISION-V2-SCOPE`
D1 carried that into a standing prohibition, and D2 carved out one five-seed diagnostic. Q009 closed the narrower reading
— the prohibition binds design, not diagnostics — and `docs/G13D-DIAGNOSTIC.md` records the diagnostic that followed.

**The prohibition's evidentiary basis is disclosed as absent.** `docs/claim_ledger.json` records, under C006 (a transfer
claim since withdrawn for unrelated reasons), the scope limitation:

> "No admissible test of H2 was ever run: F2 fired before the arm that would have tested it."

A withdrawn claim's status does not change the fact it records. The arm that would have tested whether a task family
supported comparative advantage never ran, so the record supports *no task family was found*, not *a search established
that none exists*. That distinction is the whole reason this draft exists: a pre-commitment that was never tested is
still binding, and it is still the owner's to narrow.

## 2. Three lines that converge

These are three different experiments, on different harnesses, that name the same missing capability.

| Line | What was measured | The number |
|---|---|---|
| **Selection** (Gate 13) | Under the engine's own global count-ranked selection, the world's 112 edges are spread, not clustered | top 20 recovers 0–1; top 320 — about 16× the budget — recovers 106–109; precision never exceeds **0.3438** across 36 measurements under two allocation rules; coverage needs 240–244 claimed edges, about **12×** the budget |
| **Readout** (capacity-1,000 confirmatory) | Structure forms, but does not convert into held-out prediction | no improvement detected, 98.33% interval crossing zero; headroom against the strongest simple baseline **0.005647** nats |
| **Intervention** (A1 / C4) | Carriers cannot be removed without moving their neighbours | assembly **VOID**; 510 of 2,785 non-target rows over tolerance; max K/Y delta **0.575** against 0.05; the closure of the 20-edge block is **180 of 200** carrier edges, and **none** of the 93 target-carrying carriers is clean |

**The diagnosis in one sentence:** V1 has no addressable, intervention-relevant handle on what it stores — selection orders
by frequency, readout does not turn structure into prediction, and carrier removal is not edge-local.

**The one measured improvement in hand is not a substitute.** G13-D (capacity 1,000 with sleep-sourced provenance removed)
improved log-loss by about **0.03 nats** on five diagnostic seeds. It is a diagnostic, it is unpromoted, and it addresses
capacity and provenance — not addressability.

## 3. The decision

### The decision, in four sentences

A V2 charter is commissioned: a design document with one pre-committed question, one pre-committed failure criterion, and its own freeze, written before any V2 cell runs.
The charter's first experiment tests the converged diagnosis: that V1 has no addressable, intervention-relevant handle on what it stores, at selection, at readout and at manipulation.
V2 is a separate lineage: V1 stays frozen at its pin as the reference object, and no V1 result may be cited as V2 evidence.
No V2 cell, module or engine change is authorised by this decision; the charter returns to the owner for its own adoption.

### What the charter must contain

1. **One question**, stated so that it can fail, and **one failure criterion** fixed in the charter before any cell runs.
2. **A first experiment aimed at addressability** — the one capability all three lines name — with its comparison, its
   control and its stop condition named in advance.
3. **A lineage statement**: what V2 inherits from V1 (the framing, the laws, the measurement discipline; no behavioural
   constant), what it must independently reproduce (nothing), and how the two are kept separate (its own pin, its own
   freeze, its own version line).
4. **The same discipline that made A1 readable**: a freeze act, a pin on whatever produces the verdict, and a gate order
   in which a `VOID` stops interpretation before any effect is quoted.
5. **A stop condition** in the sense of rule 23(c): the charter closes after its first experiment reports, pass or fail.
   Extending it, or adding a feature to it, needs a new decision.

## 4. What this does not do

- It authorises **no code, no cells, no engine change, no promotion and no spending**.
- It does not withdraw, re-score or reinterpret H2, Phase K, Phase L, Gate 13 or any other verdict.
- It does not turn `ORGANICA-V2-DESIGN-BRIEF.md` into a design; that brief stays a set of options.
- It does not let a V1 result be cited as V2 evidence, or the reverse.
- It does not touch the frozen engine files or `docs/engine_pin.json`.

## 5. Rejected alternatives

**Keep H2's prohibition in force and continue harness-only work.** Because the prohibition rests on an arm that never ran, while three independent measurements now name the same missing capability.

**Treat the charter as permission to build.** Because a charter that arrives with an implementation is a design decision made by whoever wrote the code.

**Rewrite the frozen engine in place.** Because it would break comparability with the published record and the pin that enforces it.

**Commission a charter without a pre-committed failure criterion.** Because V1's record shows how easily an architecture programme becomes unfalsifiable.

## 6. Evidence

- `docs/claim_ledger.json` (C006, scope limitation)
- `docs/DECISION-V2-SCOPE.md`, `docs/ORGANICA-V2-DESIGN-BRIEF.md`
- `docs/GATE13-RANKING-CRITERION.md`, `docs/BOTTLENECK-MAP.md`
- `docs/functional_structure_confirmatory.json`
- [`A1-RUN`](A1-RUN.md), `docs/a1_two_path_result.json`
- [`DECISION-A1-VOID-ACCEPTED`](DECISION-A1-VOID-ACCEPTED.md)

## 7. Signature

**Sign:** `DECISION-V2-CHARTER — ADOPTED`, owner, date. **Narrow further:** `ADOPTED WITH LIMITS`, owner, date, and the
limits in the same line. **Withdraw:** `WITHDRAWN`, owner, date, reason.

Until signed, this document is a **draft**: it commissions nothing, and the prohibition in `DECISION-V2-SCOPE` D1 stands
exactly as recorded.
