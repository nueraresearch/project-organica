# Decision: what an engine-effect claim must rest on

Dated 2026-11-10. Recorded after the D3 persistence chain, which demonstrated the standard by
meeting it and by failing one of its arms.

## The decision

An engine-effect claim rests on a single-variable arm, a same-build control, a shipped-build reproduction and a live seed axis.

A treatment that changes one engine constant and nothing else is measured in process first, against the shipped arm on the same seeds.

## The standard

1. A treatment that changes one engine constant and nothing else is measured in process first, against the shipped arm on the same seeds.
2. The control is the same build the claim names: the pre-repair behaviour is measured, not inferred from an earlier version.
3. The repair is reproduced with the shipped engine at the new version, end to end.
4. The seed axis must be live: distinct per-seed trajectories, or the block is a single case wearing a seed count.
5. Gates are fixed before the run, and a block that fails its own preflight gate is VOID.
6. A VOID block may not be cited as confirmation and may not be cited as a failed replication; it measured nothing about the engine.
7. The claim's build is derived from artifact stamps, and a chain that spans builds says so instead of naming one of them.
8. Promotion into the engine is a separate owner decision with its own date, its own record and a version bump.

## Rejected alternatives

**Alternative.** Accept the in-process treatment as evidence about the shipped engine.
**Because.** An in-process subclass is not the shipped build, and rule 22 already separates a perturbation of the observer from one of the organism.

**Alternative.** Cite the VOID replication arm as a failed replication.
**Because.** A block that fails its own preflight gate measured nothing about the engine, and reporting it as a failed replication turns an inadmissible run into evidence.

**Alternative.** Let the claim's engine version be the one the author remembers.
**Because.** The build is derived from artifact stamps; a chain that spans builds must say so, and a mixed field is the honest record.

## Why the D3 chain is the example

The seed block measured the repair in process on the unchanged 0.13.0 engine, so it satisfies the
single-variable and same-build conditions but not the shipped-build one. The recalibrated G1 arm
then reproduced repaired persistence with the shipped 0.14.0 engine, which is the reproduction the
first arm could not provide. The engine-replication arm is `VOID` on its preflight gate, and the
standard says what that means: the arm measured nothing about the engine, so it is neither
confirmation nor a failed replication. The claim ledger records the chain under the mixed build the
stamps yield, because naming either version alone would be false.

## What this does not license

It does not make a repaired measurement a capability claim, and it does not let a passing block
skip the promotion decision: the engine change remains the owner's decision, with its own record
and its own version bump. It also does not retire any earlier result; a result measured on an
earlier build stays a statement about that build.

## Evidence

- `docs/D3-PERSISTENCE-SEED-VARYING-RESULT.md`
- `docs/D3-PERSISTENCE-ENGINE-REPLICATION-RESULT.md`
- `docs/D3-PERSISTENCE-G1-RECALIBRATED-RESULT.md`
- `docs/d3_persistence_g1_recalibrated_run.json`
- `docs/claim_ledger.json`
- `docs/ENGINE-CHANGE-AUDIT.md`

## C012 conformance check (2026-11-10)

Written after the decision was recorded, and reading the ledger's claim rather than adding a
result. C012 is `HYPOTHESIS` / `ACTIVE` at build `mixed:0.13.0+0.14.0`. Each clause names the
evidence that carries it; the figures stay in those artifacts and are not restated here.

| Clause | Evidence | Status |
| --- | --- | --- |
| 1. One changed variable, measured in process first | Seed block: `MatchedFrequencySleepService`, one constant (the source-frequency denominator), six seeds, engine unchanged at 0.13.0 — `docs/D3-PERSISTENCE-SEED-VARYING-RESULT.md` | met |
| 2. Control on the build the claim names | The same block's control arm runs the unchanged 0.13.0 build on the same seeds and per-seed worlds, so the pre-repair behaviour is measured rather than inferred — same page | met |
| 3. Reproduction on the shipped build | Shipped `organica.sleep.SleepService` at 0.14.0, six fresh seeds, control an ablation of the raw denominator — `docs/D3-PERSISTENCE-G1-RECALIBRATED-RESULT.md` | met |
| 4. Live seed axis | Six distinct preflight treatment trajectories in each arm, and a distinct world digest per seed; the seed block's treatment digest differs for every seed — both result pages | met |
| 5. Gates fixed before the run | Both arms have a preregistration page that predates the run and report the same criteria — `docs/D3-PERSISTENCE-SEED-VARYING-PREREGISTRATION.md`, `docs/D3-PERSISTENCE-G1-RECALIBRATED-PREREGISTRATION.md` | met |
| 6. VOID rule | `docs/D3-PERSISTENCE-ENGINE-REPLICATION-RESULT.md` is `VOID`: the preflight baseline gate failed on control mortality outside its recorded bound, before any criterion was read. C012 records cross-harness replication as not established and does not cite the arm as confirmation or as a failed replication. | met — arm excluded, not failed |
| 7. Build derived from stamps | The chain spans 0.13.0 (the in-process seed block) and 0.14.0 (the G1 reproduction and the VOID arm); `engine_version` is the derived `mixed:0.13.0+0.14.0`, checked by the ledger against the cited artifacts. | met |
| 8. Promotion is separate | The seed block's scope says a pass licenses no adoption; the G1 page describes itself as a replication of promoted behaviour, not a new adoption decision. | met |

**Why the tag is still `HYPOTHESIS`.** Not because a clause failed. C012 cites Q044 and Q045, both
open, and an `ACTIVE` load-bearing claim may cite only a question that is closed with outcome
`SUPPORTED`. The tag records what the classification rests on, not how strong the measurement is,
so closing those questions is what would change it; this standard does not owe another engine run.

**What this note does not cover.** Twelve cells (six seeds, two arms) on one compositional world
family at the shipped cap, so no second family is measured. One changed constant measures its
effect on persistence, not the mechanism by which persistence is maintained; an in-process
treatment is a direction, not a description of the shipped engine's internals. Persistence here is
structure surviving cycle gaps in these artifacts, and says nothing about belief persistence,
transfer or any capability. Cross-harness replication is absent rather than refuted: the arm is
`VOID`, so a second harness remains untested. The witness stage covers the short window, and the
long-horizon survival reading belongs to the preflight stage. Builds after 0.14.0 are outside the
claim; the ledger's build field is a two-build string, not a range.
