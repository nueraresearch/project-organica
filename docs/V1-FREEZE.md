# Organica 1 — The Freeze

> **Status: FROZEN as of the `v0.9.0` tag (2026-10-24).**

Organica 1 is now a **fixed reference object**. It is not abandoned and it is
not being worked on any more: it is finished, and it is the thing every
subsequent measurement is taken against.

This is a deliberate act, not an abandonment, and it is recorded here so that
its scope is unambiguous.

---

## 1. What is frozen

**The cognitive engine.** These files define what Organica 1 *is* — what it
attends to, what it retains, how it composes, and what it revises:

| File | What it defines |
|---|---|
| `organica/sleep.py` | the eight-layer sleep transformation, the retention policy, the gates, the per-layer caps |
| `organica/memory.py` | the substrate: events, co-occurrence and temporal graphs, the monotonic cycle counter |
| `organica/paths.py` | the canonical path layout and the scratch-space discipline |
| `organica/streams.py` | the study streams the published campaigns ran against |
| `organica/branch_streams.py` | the branch-structured stimulus |
| `organica/scale_streams.py` | the world-complexity ladder |
| `organica/ground_truth_worlds.py` | the synthetic causes, regime changes and hidden-label worlds |

`organica/__init__.py` is **not** in this list, and deliberately so: it carries the
package version, which has to be able to move. It holds no cognitive logic.

**These files must not change.** Not for performance, not for a bug fix, not
for a new experiment. `tests/test_v1_freeze.py` enforces this by comparing
them against the `v0.9.0` tag and failing if they differ.

The freeze covers the **architecture**, not the archive. A frozen architecture
whose published results could drift is not frozen at all, so the campaigns
that produced the published numbers stay reproducible too.

---

## 2. What is *not* frozen

Freezing the engine does not freeze the project. This is the important half.

| Still free | Why |
|---|---|
| **Benchmarks and harnesses** (`benchmarks/`) | Phase L and everything after it lives here. A harness is an instrument, and instruments are supposed to be built. |
| **Documentation** (`docs/`, `README.md`, `CHANGELOG.md`, the journal) | the record must keep tracking the work, including work about the frozen engine |
| **The manual and the owner's action list** | the owner's decisions are not a change to the architecture |
| **Tests for new instrumentation** | a new harness needs its own regression tests |
| **A new `organica/` module that does not alter engine behaviour** | additive and inert, with the freeze test still green |

**The one rule that covers the boundary:** nothing may change the *behaviour*
of the frozen engine. If a change is behaviour-preserving and proven so —
the pattern `tests/test_substrate_equivalence.py` already uses — it can
live in a new module. If it cannot be proven behaviour-preserving, it is an
architecture change, and the answer is no.

---

## 3. Why it is enforced, not just declared

A freeze that lives only in a README is a promise. This repository's whole
history is that promises drift: the version declared a release master was not,
the changelog linked a 404, the "structure flat" claim was an overstatement,
the tag-frequency counter measured the wrong population. Every one of those
was a documentation-versus-evidence gap.

So the freeze is a **test**:

```
python -m pytest tests/test_v1_freeze.py -v
```

It reads the frozen files from the `v0.9.0` tag and compares them byte for
byte with the working tree. If they differ, the test fails and says what
changed. That makes *"nothing afterwards quietly changes it"* a property the
repository checks on every test run, rather than a sentence someone can forget.

The test is deliberately allowed to **skip** when the `v0.9.0` tag is not
reachable — a shallow clone has no ancestor tags — and says so, rather
than passing silently.

---

## 4. The archival reference

| | |
|---|---|
| **Archival tag** | `v0.9.0` |
| **What it marks** | the V1 record complete: evidence synchronised with documentation, corrections incorporated, the negative-results map established (six task families), and the V1 synthesis written |
| **What it freezes** | the engine files listed in §1 |
| **What it does not do** | it does not authorise a V2, and it does not close the research question |

The synthesis is [`docs/V1-SYNTHESIS.md`](V1-SYNTHESIS.md). The journal
record is §34. The negative-results map is §32–§33.

---

## 5. What happens next

Phase L measures the property that the evidence identifies as governing:
**the coherence–plasticity boundary**. It is a *measurement* phase, not a
benchmark hunt and not a redesign — it takes Organica 1 as the fixed
reference object and asks **how much pressure is required for new structure to
displace old structure**.

The protocol is frozen in
[`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`](PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md),
committed before any outcome exists.

**The order is deliberate: launch is not run.** The protocol is written, the
harness is built and validated, and the protocol is reviewed — *then* the
campaign runs. The synthesis's strongest recommendation is to stop producing
outcomes long enough to decide exactly what property is being measured.
