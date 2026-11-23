# Decision: the G1 reference-arm witness

**Date:** 2026-11-09
**Status:** **ADOPTED (amended 2026-11-10).** The Tier-1 pre-flight is re-based on a witness the
arm is alive at, and the campaign is gated on a persistence pre-flight it has never had. D3's
matched-frequency repair is now adopted and promoted into the engine; see §9. The dated statements
in §§1–8 are the filing record and are not rewritten.
**Scope:** the witness `benchmarks/run_matrix.py` uses to verify the reference arm (G1), and the
condition under which the Tier-1 campaign may launch. Not the decay rule, not the matrix's
metrics, not any published artifact.

## 1. What was found

`benchmarks/run_matrix.py` refuses to launch when G1 reports a problem, and on 0.13.0 G1 reported
`FULL produced no theories -- the reference arm is broken`. The arm is not broken. Run at
single-cycle resolution on the frozen `L1_hub1_t3_disjoint` stimulus, the reference colony reaches
its full plateau by cycle 5 and holds it for thirty-one cycles:

| Cycle | Questions | Dreams | Experiments | Beliefs | Theories |
| --- | --- | --- | --- | --- | --- |
| 5–36 | 5 | 8 | 5 | **18** | **5** |
| 37 | 5 | 8 | 5 | 14 | 5 |
| 38 | 3 | 8 | 5 | 10 | 3 |
| 39 | 0 | 8 | 5 | 6 | **0** |
| 40–60 | 0 | 8 | 5 | 6 | 0 |

The probe captures a terminal snapshot at cycle **40**, which is one cycle past the collapse. The
recorded G1 in the matrix's own provenance at `v0.7.0-14-gea8e6d2` reports `questions=5, dreams=7,
experiments=5, beliefs=18, theories=5` — the plateau, not a different behaviour. Formation is intact;
the snapshot landed before the cliff.

## 2. Why the theories disappear

Theory and question formation requires **at least two hypotheses for the same subject**
(`organica/sleep.py:415`: `if len(hyps) < 2: continue`). As the belief population decays, subjects
fall to one hypothesis and both layers stop producing. The cascade is the engine's own natural
selection operating on a stimulus that repeats the same 216 events every cycle, so support is never
renewed and the decay wins. That is the same mechanism the pruning record measures; it is not a
question-generation regression.

Two further facts rule out the alternatives. The pinned engine still forms theories where the
stimulus renews: `docs/pruning_by_type.json`, stamped `0.13.0` / `6e0ff24`, retires **51 theories**
on the degree-12 world (33 in its no-decay control). And the frozen stimulus module
(`organica/branch_streams.py`) and the G1 probe code are unchanged since the matrix was recorded —
the diff since `ea8e6d2` adds only `engine_stamp` and the two fail-closed helpers. The variable is
the engine's persistence, not its formation.

## 3. The witness is design-dependent

All four designs in the frozen stream module, run 40 cycles on the reference colony:

| Design | Questions | Beliefs | Theories |
| --- | --- | --- | --- |
| `L1_hub1_t3_disjoint` | 0 | 6 | **0** |
| `L2_hub1_t3_shared` | 0 | 2 | **0** |
| `L3_hub1_t3_mixed` | 4 | 12 | **4** |
| `L4_hub2_t3` | 0 | 2 | **0** |

G1's witness was therefore always a property of the design and the horizon, not only of the code
paths it exists to verify. On `L3` the same six colonies are distinguishable at the same horizon.

## 4. Decision

**D1 — the witness is a trace, on a design the arm is alive at.** G1's witness is the per-cycle
trace on a design the arm is alive at, not a terminal snapshot. The probe records the trace for
every colony and fails when a colony formed no theory in any cycle; the `L1` collapse above is
recorded in the artifact beside the pass, so the change is disclosed rather than hidden. The
negative-control arms (`NO_DREAMS`, `NO_QUESTIONS`) must still report zero in every cycle, which is
what keeps the check able to fail.

**D2 — the campaign is gated on persistence, not on the pre-flight alone.** The Tier-1 campaign may
not launch until a persistence pre-flight on its own stimulus shows the reference arm alive at the
campaign horizon. The pre-flight measures the cycle at which the reference arm's theory count first
reaches zero on the campaign's `L1` stimulus at the campaign's cycle count. If that cycle is below
the horizon, the campaign is reported **not measurable as designed** and does not run. The horizon
is not shortened to fit the arm, and cells are not dropped after the fact.

**D3 — restoring persistence is a separate decision (PENDING).** The reference arm's survival on a
repeated stimulus is a cognition question. It is not decided here, and no engine file is changed by
this record. It needs its own preregistration and the owner's decision, exactly as the withdrawal of
the degree-invariant strength rule left it (`docs/USER-MANUAL.md` action row 51).

## 5. Rejected alternatives

- **Keep the 40-cycle L1 snapshot and lower the probe to 35 cycles.** It moves the witness to a
  cliff edge and passes only because the collapse is three cycles later, so the next unrelated
  change re-breaks it.
- **Run the Tier-1 matrix and drop the early cycles afterwards.** Selecting the window after seeing
  the result is the defect the preregistration exists to prevent.
- **Change the decay rule so the reference arm survives.** It is a cognition change with no
  preregistration, and it would make the run measure the fix rather than the engine.

## 6. Falsifiers

This decision is void if a trace-based G1 finds no theory in any cycle for the reference colony on
any design, or if the persistence pre-flight shows the arm alive at the horizon and the campaign
still fails its own final-tenth rule. Either outcome means the witness was not the defect and the
engine question is the whole of it.

## 7. What this does not change

No metric, no threshold, no engine file, no published result, and no claim. The matrix artifact
remains what it is: measured at `ea8e6d2`, not reproducible on `0.13.0` until D2 passes. The claim
ledger's `v0.7.0-14-gea8e6d2` attribution for C003 is correct and is unaffected.

## 8. Implementation record (2026-11-09)

D1 and D2 are implemented in `benchmarks/force_matrix.py` (`verify_colonies` reads the trace,
`trace_reference` measures the horizon, `persistence_verdict` applies D2) and in
`benchmarks/tier1_preflight.py`. `benchmarks/run_matrix.py` now witnesses on `L3_hub1_t3_mixed`
and refuses to launch unless the persistence pre-flight returns `ALIVE_AT_HORIZON`.

The pre-flight run of 2026-11-09 reports:

- witness: the reference arm formed a theory in **39 of 40** cycles (peak 6);
- negative controls: `NO_DREAMS` and `NO_QUESTIONS` recorded zero in every cycle;
- campaign stimulus `L1_hub1_t3_disjoint`: first zero at cycle **39**, peak 6, against a
  3000-cycle horizon;
- verdict: **`CAMPAIGN_NOT_MEASURABLE`**.

Record: `docs/tier1_preflight.json`, page `docs/TIER1-PREFLIGHT.md`. D3 (restoring persistence)
remains PENDING: no engine file changed and no published result was rebuilt.

**D3 result (2026-11-09, post-freeze).** The frozen block ran: **`PERSISTENCE REPAIRED`**. The
control's first zero is cycle 60 on every seed; the treatment has no first zero through cycle 3000
and at least four theories in its last 100 cycles; the early-recall median gap is 0.0 against the
-0.01 bar. **The six seeds are byte-identical**, so the block is one deterministic trajectory
repeated six times, effective n = 1, and its seed axis is a design defect. The pass does not
establish seed robustness, and D3's adoption remains PENDING. Record:
`docs/d3_persistence_run.json`, page `docs/D3-PERSISTENCE-RESULT.md`.

**D3 preregistration (2026-11-09).** D3 now has the preregistration it required:
`docs/D3-PERSISTENCE-PREREGISTRATION.md`, frozen and unrun. It specifies matched
source-frequency decay on 24 cells over six fresh seeds, measured on this decision's L3
witness and on D2's L1 pre-flight at the 3000-cycle horizon. It does not change this
decision's PENDING status, and no cell has run.

**D3 seed-varying result (2026-11-10, post-freeze).** The frozen `D3-PERSISTENCE-2` block reran
the same 24 cells on six seeds that shuffle and rotate the design's fixed triangle lattice. The
six preflight treatment trajectories are distinct; all six are alive at the 3,000-cycle horizon
(with at least four theories in the last 100 cycles), and the early-recall median gap is 0.0
against the -0.01 bar. The witness holds 39 of 40 cycles and peak 6 on all six seeds, and both
negative controls remain at zero. **The seed axis is live and effective n = 6**, so the
persistence repair survives independent trajectories. The prior `D3-PERSISTENCE-1` single-world
result is preserved, not rewritten. No engine file changed; the arm remains in-process only, and
D3's adoption stays PENDING for the owner. Both D3 result writers now refuse to write a result
when more than one seed produces fewer than two distinct preflight treatment trajectories, so a
single-world pass cannot be reported as six confirmations; the preserved D3-1 record remains
readable and caveated. Record: `docs/d3_persistence_seed_varying_run.json`,
page `docs/D3-PERSISTENCE-SEED-VARYING-RESULT.md`.


## 9. D3 promotion — owner decision (2026-11-10)

**Status: ADOPTED.** The owner directed that the matched-frequency persistence repair be promoted
into the engine, re-pinned, and D2's pre-flight rerun. This supersedes the PENDING clause in §4 D3.

The matched-frequency persistence repair is promoted into the engine on 2026-11-10. Each sleep cycle
maintains a per-tag denominator `D = 0.95 * D_previous + delta`, where `delta` is the increase in
`MemoryService.tag_frequencies()` since the previous cycle; prediction strength divides the temporal
count by `max(D, 1)`. The temporal decay constant, death threshold, stable threshold, candidate decay,
admission floor, caps, retention policy and candidate set are unchanged. `MatchedFrequencySleepService`
remains only as a compatibility name and no longer overrides engine behavior.

**Why this is enough.** The frozen `D3-PERSISTENCE-2` block produced six distinct preflight treatment
trajectories, all six alive through 3,000 cycles, with the L3 witness and early-recall criteria intact.
The earlier `D3-PERSISTENCE-1` single-world result remains caveated and is not re-scored. The owner's
decision is the adoption step the preregistration required; it is not a new statistical result.

**Rejected — keep the repair in process only.** It would leave D2's gate measured on an engine that is
not the one the campaign would run.

**Rejected — promote without a version bump and re-pin.** The pin would stop describing the engine,
and AGENTS.md rule 12 would record the change as unrecorded bytes.
