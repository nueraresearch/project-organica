# Authorisation provenance audit

**Date:** 2026-11-13. **Scope:** every `docs/AUTHORISATION-*.md` document (14 files) and every `docs/*.json` record carrying an `authorisation` block (21 records). This audit runs no cell and changes no result.

**Question:** does any record with `cells_run > 0`, or status `FROZEN, RUN`, cite a quote that authorises only preparation?

## Finding 1 — the cap-112 run records cite a preparation-only quote

`docs/AUTHORISATION-PRESENCE-CAP-112.md` has one block quote:

> Write the dated cap-112 authorisation document for the comparator, Q1 and Q2, recording the owner's grant against the three frozen records.

That is an instruction to **write the document**, not to run cells. The document's body says it is the grant and describes the three campaigns, but the recorded verbatim quote does not authorise a run.

Three records cite this document:

| Record | Status | Cells run | Result | Finding |
| --- | --- | ---: | --- | --- |
| `PRESENCE-COMPARATOR-112` | `FROZEN, RUN` | **7** | `PRESENCE NOT ASSERTION` | **Preparation-only quote used for a run record.** |
| `PRESENCE-CAP-1-112` | `FROZEN, RUN` | **25** | `CAP LIMITING` | **Preparation-only quote used for a run record.** |
| `PRESENCE-CONSTRUCT-1-112` | `FROZEN, NOT RUN` | **0** | none | Preparation-only quote with `granted: true`; no run yet. |

The first two records also retain this stale `not_evidence` sentence:

> A draft is not a run. No cell has executed, no verdict is adjudicated, and none of these records may be cited as a cap-112 result.

That sentence contradicts their own `FROZEN, RUN` status and result. It is a separate provenance defect from the quote.

**What this establishes:** the two cap-112 results are **provenance-incomplete for owner authorisation**. It does **not** say their gates failed, their numbers are wrong, or their verdicts should be re-scored. It says the records do not contain the owner's actual run words. No quote has been invented to fill the gap.

## Finding 2 — BAND-3 is preparation-only but correctly unrun

`docs/AUTHORISATION-PRESENCE-BAND-3.md` quotes:

> Preregister a repaired band block with fresh seeds and the fixed harness, with B5 still able to fail, and record its grant before running.

The record `PRESENCE-BAND-3` is `FROZEN, NOT RUN`, `cells_run` 0, `granted: true`. There is no false run, but the grant flag should be read as permission to build the arm and pass preflight, not as permission to run cells. Before any cell, the record needs the owner's actual run quote.

## Finding 3 — the formation-anchored grant was already corrected

`CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1` now records both:

- `preparation_quote`: “Prepare the dated grant document … without running it.”
- `quote`: “Fix the post-landmark assertion cycle and rerun the twelve cells.”

It is the reference repair, not a finding.

## Passing records

These run records contain operative run language, even where the first block quote in the document is a research question:

| Record/document | Recorded run words |
| --- | --- |
| `PRESENCE-CAP-1` / `AUTHORISATION-PRESENCE-CAP-1.md` | `Authorize all runs` in the decision table |
| `PRESENCE-CONSTRUCT-1` / `AUTHORISATION-PRESENCE-CONSTRUCT-1.md` | `Authorize all runs` in the decision table |
| `PRESENCE-CONVERSION-1` / `AUTHORISATION-PRESENCE-CONVERSION-1.md` | `Authorize all runs` in the decision table |
| `PRESENCE-CONVERSION-2` | “then run the twelve-cell campaign and adjudicate N1–N7” |
| `CORE-BAND-ADMISSION-1` | “Preregister and run …” |
| `PRESENCE-BAND-1` | “Build … then run the 12 cells …” |
| `PRESENCE-BAND-5` | “Register … then run its twelve cells …” |
| `CONFIRMATORY-RETENTION-INCREMENTAL-1` | “Grant the retention block and run its twelve cells …” |
| `CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1` | “Fix … and rerun the twelve cells.” |
| `T1-PERSISTENCE-OFF` | “Run the T1 persistence-off block …” |
| `T1B-PERSISTENCE-OFF` | “Preregister T1b … then run it.” |
| Stage B allocation / `AUTHORISATION-STAGE-B.md` | “i authorize it” |

The cap-40 conversion documents are a presentation caveat, not a preparation-only grant: the first block quote is the research question, while the decision table contains the verbatim `Authorize all runs`. A reader who stops at the first quote sees a question where a grant exists.

Records with no grant and `cells_run` 0 are out of scope: `PERSISTENCE-MECHANISM-1`, `PRESENCE-BAND-2`, `PRESENCE-BAND-4`, `PRESENCE-CAP-LADDER-1`, and `CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1`.

## Recommended actions

1. **Locate the owner's actual cap-112 run authorisation.** If it exists, record it as `authorisation.quote` in the two run records and in the shared document. If it does not, record the runs as **not owner-authorised** and treat their results as provisional; do not invent a quote.
2. **Fix the stale `not_evidence` text** in `PRESENCE-COMPARATOR-112` and `PRESENCE-CAP-1-112` only after deciding what the provenance finding is called.
3. **Do not run `PRESENCE-BAND-3`** under its preparation-only quote. Add a dated run quote first, or leave `cells_run` at 0.
4. **Add a preflight guard:** a record with status `FROZEN, RUN` or `cells_run > 0` whose quote matches preparation-only language (`without running`, `record its grant before running`, `write the dated authorisation document`) must fail until a run quote is recorded. **Implemented 2026-11-13:** `benchmarks/authorisation_guard.py` classifies preparation-only quotes and is wired into the retention formation, entry-transition and incremental preflights. `tests/test_authorisation_guard.py` proves the guard rejects the cap-112 quote and accepts the recorded run quote, and `authorisation_guard.scan()` flags the two known cap-112 records without changing them, and `python -m benchmarks.authorisation_guard --check` exits 1 on those violations.

## What this audit does not do

- It does not re-score a gate, coefficient, verdict or result.
- It does not change any `status`, `cells_run`, `authorisation.granted` or result artifact.
- It does not establish that the cap-112 runs were unauthorised. It establishes that their records do not show the run authorisation.
- It does not change Stage B: **1644** consumed seeds across **209** artifacts.
