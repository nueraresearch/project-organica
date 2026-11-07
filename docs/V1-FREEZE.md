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
| **A new `organica/` module that does not alter engine behavior** | additive and inert, with the freeze test still green |

**The one rule that covers the boundary:** nothing may change the *behavior*
of the frozen engine. If a change is behavior-preserving and proven so —
the pattern `tests/test_substrate_equivalence.py` already uses — it can
live in a new module. If it cannot be proven behavior-preserving, it is an
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

## 6. Amendment 1 — carried-forward structures are not current-cycle evidence (2026-11-06)

**Authorised by the owner, on the decision recorded in
`docs/DECISION-CANDIDATE-SUPERSESSION.md` §5.**

The freeze's boundary rule is that nothing may change the *behavior* of the frozen engine
without a recorded decision. This is that record, and it changes one behaviour: after
Layer 2–3 composition, `organica/sleep.py` re-admitted every stable prior G2/G3 structure
into the current cycle's candidate list. Natural selection therefore saw a structure that
had stopped being produced as if it had re-emerged, reinforced it every cycle, and never let
it decay or die.

What changed:

- `organica/candidates.py` — the five carried-prone dataclasses carry a transient
  `carried_forward` field (default `False`).
- `organica/sleep.py` — the five carry-forward grafts pass `carried_forward=True`.
- `organica/sleep_selection.py` — `_natural_selection` does not count a carried structure as
  current-cycle evidence, `_store_candidates` does not re-write one, and
  `_store_single_candidate` strips the marker so no stored record carries it.

What did not change: extraction, the confidence formula, the death and stability
thresholds, candidate keys, the priming gate, and the report's contents — carried
structures are still visible to downstream layers and telemetry, which is what the graft is
for. The engine-file identity check in `tests/test_v1_freeze.py` already skips at package
versions ≥ 0.12.0, so this amendment is recorded rather than enforced by editing that
mechanism; the archival `v0.9.0` tag remains the reference for what Organica 1 was.

**Measured consequence — this amendment is not measurement-neutral, and the record says so.**
The Gate 13 sufficiency harness (`benchmarks/acquisition_harness.py`, default seed,
120 cycles) reads its asserted basis off the surviving candidate set, so changing which
structures survive changes that figure. Three builds of the same seed and world:

| build | covered asserted edges | asserted coverage |
|---|---|---|
| `e6d1bcc` — before the supersession reader and before this amendment | 26 / 112 | 0.2321 |
| supersession reader only (newest copy per id, death records) | 22 / 112 | 0.1964 |
| reader + this amendment (carried structures are not evidence) | 34 / 112 | 0.3036 |

Raw temporal coverage is 112/112 in all three builds. The reader alone *lowers* the asserted
figure — duplicate copies of one candidate no longer count twice — and the guards then raise it.
The measurement separates those two steps and no further: the guards act on both the
current-cycle key set and the store, and this figure does not attribute the rise between them.

The gate's verdict does not move: 0.3036 is still far below the 0.50 threshold, so Gate 13
still fires and the acquisition finding stands. But **every Gate 13 figure recorded before this
amendment describes the pre-amendment engine** — `docs/acquisition_single_seed_pilot.json`
(asserted coverage 0 at the frozen cap of 20), `docs/gate13_allocation_rule.json` and
`docs/formation_utilization.json`. They are not re-scored here and none of their verdicts
changes; they are labelled pre-amendment measurements. The effect measurement is
`docs/candidate_supersession_gate13_effect.json`.

The same question on the paired capacity test's cap-20 basis behaves differently: there the
amendment *lowers* the asserted coverage, from 0.6607–0.8125
at `e6d1bcc` to 0.4821–0.7500 on the five diagnostic seeds, and the
recorded 0.0 %–2.7 % band is not where either build sits — it reproduces only on its own build
(`89b0744`, 2026-10-28). That re-measurement is recorded in
`docs/GATE13-PAIRED-CAPACITY-TEST.md` §5 and `docs/gate13_cap20_build_comparison.json`, and it is
a finding about the record's Gate 13 quotation rather than about this amendment.

**Measured consequence, amended (2026-11-06).** Sweeping the Layer-1 cap from 1 to 1,000 on all three
builds (`docs/gate13_cap_curve_by_build.json`) sharpens what the amendment does and does not do. Against `e6d1bcc` it
*shrinks* the asserted set — 129 edges against 173 at cap 1 — and lowers recall at every
cap below 500 (0.5089 against 0.7143 at cap 1, 0.5357 against 0.7768 at cap 20), reaching parity at
500 and 1,000, while precision does not move across the whole curve (0.0087 span). So the
carried-forward copies were not chiefly noise: removing them removes world and non-world edges at
about the same rate. The amendment is justified as a scoring correction — a prior carried across
cycles is not this cycle's evidence — and **not** as a coverage improvement, which this sweep rules
out. `docs/GATE13-PAIRED-CAPACITY-TEST.md` §8.

## 7. Amendment 2 — diversity-first admission (2026-11-07)

**Authorised by the owner, recorded in `docs/DECISION-ADMISSION-RULE.md`.** The licence is the
confirmatory block in `docs/RANKING-ADMISSION-PREREGISTRATION.md`, which ran after that
registration was committed and returned `ADOPT THE ADMISSION RULE`.

**What changed: nothing in this list.** The adopted rule lives in a new module,
`organica/admission.py`, as a `SleepService` subclass that overrides `_build_predictions`. No
frozen engine file is edited, and that is checked rather than declared: `git diff` over the seven
files in §1 must be empty, and the `count` arm of the new service delegates to
`SleepService._build_predictions` and must return exactly what it returns
(`tests/test_admission_rule.py`). The archival `v0.9.0` tag remains the reference for
what Organica 1 was, and `SleepService` itself still applies its own ordering: transition
probability inside a stratified quota. **The adopted order is therefore untested on this
layer** — the confirmatory block compared it against a count-ranked control over a pooled
edge table, not against the engine's prediction ordering, and the decision record says so.

**Why an amendment is the right instrument anyway.** A new module that reproduces the engine is
inert; a new module that an engine version uses is a cognition change, and rule 2 wants exactly
this: the decision recorded before the change. The decision is recorded, the change is in a new
module, and the frozen path is preserved rather than overwritten.

**Measured consequence — disclosed, not re-scored.** The behaviour of the reference engine is
unchanged, so no archived measurement moves. The consequence is prospective: any future run
through `DiversityFirstSleepService` admits a different set from the count-ranked engine, and the
published Gate 13 figures describe the count rule. A run through the adopted service must name
its arm. Nothing here shows that broader coverage improves behaviour; the confirmatory evidence
is coverage only.

**The identity check cannot police this, and the record says so.** `tests/test_v1_freeze.py`
skips its byte-identity comparison at package versions ≥ 0.12.0 (the guard Amendment 1 added), so
an edit to `sleep.py` would not be caught by it. This amendment is therefore not "allowed because
the test skips": it is allowed because no frozen file was edited, which `git diff` verifies
directly. An edit to a frozen file would be a different act and would need its own record.
