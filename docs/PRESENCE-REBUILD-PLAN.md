# Plan: rebuilding the three build-stamped presence blocks on the split engine

**Status, 2026-11-11: plan only. To be explicit: no rebuild has run, the rebuild is not authorised, and no artifact has been
restamped.** The split engine is already in force: `organica/sleep_extraction.py` names the returned
window and derives the transition and cooccurrence allocations from it, and `docs/engine_lineage.json`
carries the frozen blocks from the build they were recorded on (`477aeb2f…`) to the split build
(`1fc7be8f…`) on unchanged canary digests. A rebuild is therefore **not** needed to land the split.
It is needed only for a different claim: *the block's verdict holds on the engine that now ships.*

## 1. The verdicts, stated up front

Each row is the artifact's verdict on the build it names, what a rebuild would derive instead, and the
set of verdicts that block's own decision table can return. A re-derived verdict is **accepted** when
it is in that set and was produced by that block's own code from that block's own rows.

| Block | Artifact | Verdict on `477aeb2f…` | A rebuild re-derives | Accepted if it is one of |
| --- | --- | --- | --- | --- |
| Same-build assertion audit (the comparator) | `docs/presence_assertion_audit_0.14.0.json` | `PRESENCE NOT ASSERTION` | `_verdict(rows)` over the six audit seeds | `PRESENCE NOT FULL`, `PRESENCE NOT ASSERTION`, `PRESENCE AND ASSERTION COINCIDE` |
| `PRESENCE-CONSTRUCT-1` (Q1) | `docs/presence_construct_audit_run.json` | `CONSTRUCT VALID`, all nine gates true | gates `C1`–`C9` on six reading cells plus the control | `CONSTRUCT VALID`, `OBJECT MISMATCH`, `NOT MEASURABLE`, `VOID` |
| `PRESENCE-CAP-1` (Q2) | `docs/presence_cap_run.json` | `CAP LIMITING` (mean gain **15.833333**, lower bound **8.081175**, bar **10**) | gates `K1`–`K6` and the gain rule over 24 cells | `VOID`, `CAP NOT BINDING`, `ADMISSION-ONLY BOTTLENECK`, `CAP LIMITING`, `CAP LIMITING BELOW BAR`, `CAP NOT LIMITING`, `MIXED` |

**What "accepted" means.** The verdict is recorded as that block's reading **on the split build**, in
a new run record, beside the predecessor's verdict — which stays standing for its own build. It is not
a re-score of the predecessor, not a pooled result, and not a replacement of a frozen decision.

**What a VOID means.** No reading was made. It is accepted as `VOID` and nothing else: rule 31, a block
that fails its own gate is not evidence, and the decision table's instruction for `VOID` is to repair
the build and register a fresh block — never to re-read this one.

## 2. Scope: exactly three, and why the others are not in it

The three artifacts above are the ones whose own checks required the engine bytes that produced them.
The lineage now carries all three, so this plan touches only their measurement contents.

- **`PRESENCE-CONVERSION-1` (Q3) is out of scope.** Its verdict, `OBSERVER NOT NEUTRAL`, is an
  instrument failure, not a conversion result. Re-running it would re-ask a question its own design
  could not answer, and the repaired observer is a different block.
- **`PRESENCE-CONVERSION-2` (Q4) is out of scope.** It is frozen, unrun and unauthorised; there is no
  result to re-derive.
- **The block canaries are not re-run or re-recorded.** They are the proof that the split serves the
  same rows; re-recording them would destroy that proof. They must stay byte-identical through the
  rebuild, which is also the rebuild's tripwire (§3).
- **The pin, the lineage and the Stage B protocol are not touched.** The rebuild measures the build
  that is already pinned at `1fc7be8f…`; it does not move it.

## 3. What the split predicts about the rebuild

The canaries say the split changed no served row. If that is true, a rebuild on the same seeds,
cycles, cap and arms must reproduce the predecessor's per-seed values exactly, and therefore its
verdicts. **Expected outcome: identity** — `PRESENCE NOT ASSERTION`, `CONSTRUCT VALID`, `CAP LIMITING`,
with the same gain vector and lower bound for Q2.

Equality is the replication; a difference is a finding about the split, not a licence to choose the
newer number. If a per-seed row or a canary digest moves, stop the rebuild and record that the split
was not behaviour-identical after all — the block's own gates then decide whether it is `VOID`.

## 4. Preconditions

1. **An owner grant.** The 2026-11-10 grants cover the cells each frozen record fixes, on that date,
   on the build they were recorded on. A rebuild is a new campaign; it needs its own dated
   authorisation document naming these three blocks and this build.
2. **No live study run** against `memory.db`, and scratch databases only (the blocks use scratch).
3. **The predecessor is preserved before anything is written.** Copy the three artifacts and their
   pages aside as `*_pre-split.json` / `*_pre-split.md` and name them in the new pages. The canonical
   paths then describe the split build; the historical files describe the predecessor.
4. **Frozen records are amended, never edited.** The pre-registrations' seeds, cycles, gates and
   decision tables do not change. A disclosure row records that a rebuild ran, on which build, and
   that the predecessor's verdict stands for its own.
5. **No version bump.** The engine bytes do not move during the rebuild; the pin already names them.
   The artifacts carry the new `engine_sha256` themselves, which is what distinguishes the two runs.

## 5. Procedure

```bash
# 0. preserve the predecessor (three artifacts and their pages)
cp docs/presence_assertion_audit_0.14.0.json docs/presence_assertion_audit_0.14.0_pre-split.json
cp docs/presence_construct_audit_run.json  docs/presence_construct_audit_run_0.14.0_pre-split.json
cp docs/presence_cap_run.json              docs/presence_cap_run_0.14.0_pre-split.json

# 1. the comparator first: Q1's C9 and Q2's K5 read its rows
python -m benchmarks.presence_assertion_audit --run
python -m benchmarks.presence_assertion_audit --check

# 2. Q1: six reading cells, seeds 20261100, 20261101, 20261102, 20261103, 20261104, 20261105, 120 cycles, cap 40, plus the control
python -m benchmarks.presence_construct_audit --measure     # only under the new grant
python -m benchmarks.presence_construct_audit --finish
python -m benchmarks.presence_construct_audit --check

# 3. Q2: six seeds 20611401, 20611402, 20611403, 20611404, 20611405, 20611406 x levels 40/80/112/1000000000, 120 cycles, 24 cells
python -m benchmarks.presence_cap_experiment --run
python -m benchmarks.presence_cap_experiment --check

# 4. the tripwires: the split must still be behaviour-identical
python -m benchmarks.block_canaries --check
python -m benchmarks.engine_lineage --check
```

The comparator runs `SHORT_CYCLES` cycles (120) on seeds 20261100, 20261101, 20261102, 20261103, 20261104, 20261105 at cap 40, so
its rows are the same-object comparator Q1's `C9` reproduces and Q2's `K5` takes its witness from.
Q2's fourth level is the diagnostic ceiling, not a setting. Every `--check` above must pass on the new
artifact; `C1`/`K1` must name the split build, not the predecessor.

## 6. What the re-derivation may not do

- **Not re-score the predecessor.** Its verdict is a fact about `477aeb2f…`; the rebuild adds a second
  fact about `1fc7be8f…`. Neither revises the other.
- **Not pool rows across builds.** Two builds, two artifacts, no shared denominator.
- **Not re-read a failed gate into a verdict.** A gate failure is `VOID` (or the table's named failure),
  and the plan's response is a fresh block, not a looser gate.
- **Not treat `VOID` as a negative result**, and not report a ratio with an empty denominator as `0.0`.
- **Not re-record the canaries, the pin or the verdicts of Q3/Q4** to make the three new artifacts
  agree with the old ones.
- **Not cite the rebuild as independent evidence.** Same seeds, same world, same code path: it is a
  replication under a different byte set, which is exactly what the behaviour-identity claim needs and
  nothing more.

## 7. If a gate fails

Follow the block's own decision table: `VOID` → repair and register a fresh block; `OBJECT MISMATCH` →
stop the construct reading; `NOT MEASURABLE` → report the empty stage and no ratio; `CAP NOT BINDING`
or `CAP NOT LIMITING` → close the budget route. None of these is repaired by re-running until the
verdict changes.

## 8. Cost

The comparator is six cells at 120 cycles; Q1 is six reading cells plus one control at
120 cycles; Q2 is 24 cells at 120 cycles (six seeds x four levels). The audit and Q1 share the six
audit seeds, so the block set is the comparator, then Q1, then Q2, in that order. The rebuild writes
three artifacts and three pages, preserves three predecessor pairs, and changes no engine byte.

## 9. The decision this plan asks for

**Authorise the rebuild, or decline it.** Declining is coherent: the split is already in force through
the lineage, and the predecessor verdicts remain valid for their build. Authorising buys one thing —
the same three verdicts, re-derived on the engine that now ships — and the plan predicts they will be
identical, which is also the sharpest available test that E1 changed no behaviour.

**Sequencing note (2026-11-11).** Question 2 is now recorded as option C — raise the cap to 112 — not yet in
force. If it lands, this plan is superseded rather than merely delayed: the comparator refuses any cap but 40 and
Q1's design is cap 40, so the three blocks cannot be re-run under 112 — they need fresh records at the new cap. A
rebuild on the split build must therefore not run before the level decision lands.
