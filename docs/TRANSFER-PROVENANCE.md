# Transfer provenance (Q028) — the instrument, before the run

**Generated from [`docs/transfer_provenance.json`](transfer_provenance.json); do not
edit by hand.** Rebuild with `python -m benchmarks.transfer_provenance --measure`,
and re-check the page with `--check`.

## What this is

Q028 asks whether a transfer event can be traced to the role satisfaction that
licensed it. This instrument answers that from **recorded state only**, through two
readings of the same events. The **pair resolver** follows the priming id to the
stored schema row, reads its `source_role_id` and `target_role_id`, loads both role
rows, and resolves when the pair spans the schema's direction and an event asserts
it. The **single-role reading** is kept as the comparison: it asks one role to
contain both tags, which a schema built from two disjoint role sets cannot satisfy.
Anything unresolved is counted with its reason. **There is no threshold, no
verdict and no transfer claim in this document.**

## Controls, run before the measurement

| control | expected | observed | passed |
|---|---|---|---|
| `empty_denominator_is_not_measurable` | `measurable=True, share=None` | `measurable=False, share=None` | yes |
| `events_removed_flips` | `unresolved_missing_events` | `unresolved_missing_events` | yes |
| `missing_row` | `unresolved_missing_structure` | `unresolved_missing_structure` | yes |
| `no_events` | `unresolved_missing_events` | `unresolved_missing_events` | yes |
| `no_priming` | `unresolved_no_priming` | `unresolved_no_priming` | yes |
| `no_role` | `unresolved_no_role` | `unresolved_no_role` | yes |
| `priming_removed_flips` | `unresolved_no_priming` | `unresolved_no_priming` | yes |
| `resolved` | `resolved_role_match` | `resolved_role_match` | yes |
| `role_removed_flips` | `unresolved_no_role` | `unresolved_no_role` | yes |

The comparator was pointed at a tracer that always answers `resolved_role_match`,
and rejected it: yes. A control set that cannot fail would license a transfer claim
on nothing.

## The pre-run measurement

| quantity | value |
|---|---|
| transfer events (denominator) | 14 |
| resolved to a role match | 0 |
| unresolved | 14 |
| share resolved | 0.0000 |
| roles recorded | 7 (source `report.roles`) |
| events recorded | 200 |
| identically-paired reuses (cannot fire across contexts) | 0 |
| schema priors recorded in A | 7 |
| B priors whose id was also recorded in A | 0 |

| status | count |
|---|---|
| `resolved_role_match` | 0 |
| `unresolved_no_role` | 14 |
| `unresolved_missing_events` | 0 |
| `unresolved_no_priming` | 0 |
| `unresolved_missing_structure` | 0 |

## The pair resolver (P0): `schema_prior` -> the schema's role pair

A schema relates two disjoint role sets, so the single-role predicate above cannot
resolve a schema-primed transfer by construction. The pair resolver follows the
priming id to the stored schema row, reads `source_role_id` and `target_role_id`,
loads those two stored role rows, and resolves only when the pair spans the
schema's own direction and a recorded event asserts it. This is the resolution the
decision selects, and its claim is narrower than "resolved to a role".

| quantity | value |
|---|---|
| transfer events (denominator) | 14 |
| resolved to the schema's role pair | 8 |
| unresolved | 6 |
| share resolved | 0.5714 |
| schema rows read | 2 |
| role rows read | 4 |

| pair status | count |
|---|---|
| `resolved_role_pair` | 8 |
| `unresolved_no_schema` | 0 |
| `unresolved_schema_without_roles` | 0 |
| `unresolved_missing_role` | 0 |
| `unresolved_pair_not_in_roles` | 6 |
| `unresolved_missing_events` | 0 |
| `unresolved_no_priming` | 0 |
| `unresolved_missing_structure` | 0 |

| criterion | result |
|---|---|
| B1 every transfer resolves to a schema row or a named missing structure | yes |
| B2 the status distribution changes from the single-role reading | yes |
| B3 the claim is narrowed to resolved to the schema's role pair | recorded |

The pair controls were also run against a tracer that always answers
`resolved_role_pair`, and rejected it: yes.

## What the number is, and is not

- **Resolution is mixed by design.** The role leg is event-level: the events are the
  stored ones. The priming leg is structure-level: the engine records a schema id,
  not the events that created it. This does not claim observation-level provenance
  for the whole chain.
- **A zero denominator is not a zero share.** If the run records no transfer event,
  the share is reported as `null` and marked not measurable (AGENTS rule 13b).
- **A shared prior id is the stronger claim, and it is counted separately.** The two
  contexts use disjoint vocabularies, so a schema id recorded in A need not reappear
  in B. The table reports how many B priors were also seen in A; where that count is
  zero, "transfer" here means *licensed by a prior*, not *carried from A*.
- **A zero share with a real denominator is a measurement, not a null.** With
  transfers recorded and none resolved, the unresolved column names the leg that
  failed, which is the diagnostic Q028 asks for.
- **This is not the campaign's result.** It exists so the measure is in place, and
  proved able to fail, before the campaign runs; the campaign still needs its own
  preregistration.
