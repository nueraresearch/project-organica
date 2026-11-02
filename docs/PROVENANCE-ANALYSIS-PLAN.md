# Provenance tracer — analysis plan (frozen before the run)

**Status: committed before the diagnostic was run.** This document fixes how the
provenance tracer's output is read. It was written and committed in the same
working session as the instrument, and *before* the tracer was pointed at any
recorded run. The diagnostic's artifact records the commit this plan was frozen
at. Nothing below may be reinterpreted after the counts are seen; a change is an
amendment with a date and a disclosure that the earlier wording was superseded.

Related: `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` §20 (the closed study),
`research-journal/phase_g_findings_20261021.md` §101 (the tracer and its
controls), `benchmarks/provenance_trace.py` (the instrument).

## 1. What the diagnostic measures

For each traced claim, the tracer follows the `parent_ids` its payload carries to
the structures those ids name, and asks whether each structure on that ancestor
chain carries **tags the world also uses**.

- `world_rooted` — every resolved ancestor carries world vocabulary.
- `self_only` — no resolved ancestor does.
- `mixed` — some do, some do not.
- `unresolved_*` — the walk could not reach a terminal, with the reason named.

**`world_rooted` means vocabulary overlap across a complete ancestor chain. It is
not observation-level provenance.** Nothing in a stored payload names the world
events behind its content, so this instrument cannot show that a structure
descends from a particular observation, and no wording anywhere may imply it.

## 2. How the counts are reported

1. **Incomplete and unresolved lineages are reported separately and are never
   folded into `world_rooted` or `self_only`.** A claim with one resolvable branch
   and one missing, cyclic or truncation-cut branch is `*_incomplete`; it is
   counted there, and its resolved branch is reported as a resolved branch. The
   number of complete `world_rooted` claims is the only count that may be
   described as rooted.
2. **By claim type**, so a result carried by one structure type is visible as
   one structure type rather than as a property of claims in general.
3. **By lineage depth** — the number of ancestors actually resolved — bucketed
   `1`, `2`, `3`, `4–6`, `7+`, with unresolved lineages counted in their own
   column, so a shallow result cannot look deep.
4. **No threshold and no verdict.** There is no pass mark, no success criterion
   and no comparative bar. The artifact carries `no_threshold: true` and
   `no_verdict: true`, and no sentence in the results may name a winner.

## 3. Population and seeds

- Seeds: the five **already-used calibration seeds** `20261201–20261205`, at the
  calibration cap. Confirmatory seeds `20261207–20261226` stay closed; `20261206`
  stays burned.
- Snapshots: the readout frozen after formation and after revision learning.
- Claims: the stored structures of claim type (`prediction_candidate`,
  `hypothesis_candidate` — any type containing `prediction` or `hypothesis`),
  deduplicated by id keeping the highest-generation snapshot of each. The study's
  own claim selector (`_claim_edges`) drops ids and parent ids, so the traced
  population is claim-typed structures from the same snapshot; the count that
  carries an asserted edge is reported beside it so the difference is visible.
- World vocabulary: the tags occurring in the formation and revision event
  streams for that seed — the same set the study's readout scores against.

## 4. What this run can and cannot establish

It can say **whether useful parent chains exist in the recorded structures at
all, and how often the tracer can resolve them** — a diagnostic of the
instrument and of the recorded lineage.

It cannot validate transfer, cannot re-score the closed study, cannot authorise a
confirmatory run, and cannot show that vocabulary-overlapping links track actual
world evidence.

Two outcomes and what they would mean, stated in advance:

- **Mostly unresolved.** The recorded structures do not carry enough lineage for
  this question to be answered by tracing. That is a finding about what the
  engine stores, and the next instrument would need a store-time record of the
  content's origin rather than a walk over ids.
- **Mostly vocabulary-overlap "rooted".** Useful chains exist. That does **not**
  establish that the links track world experience: shared vocabulary is
  consistent with world inheritance and with self-generated content that reuses
  world words. The next question would be whether those links track actual world
  evidence, and answering it needs its own design.

Either way, any confirmatory study of provenance needs its **own preregistration
and fresh seeds**. The closed study's failure stays intact and is not reopened by
anything here.
