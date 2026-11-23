# Version-state sweep, 2026-11-09

Every statement about the package version, or about what is tagged, released or
unreleased, checked against the repository rather than against the document that
makes it. The sweep enumerated every occurrence of a version number or a
release-state word in every tracked `.md`, `.json`, `.cff` and `.py` file and judged
each one. This note adds no evidence and changes no number; it is the dated record
of a text correction pass.

## Ground truth at this commit

- Package version **0.13.0** in `organica/__init__.py`, `pyproject.toml` and
  `CITATION.cff`, and the changelog heading for 0.13.0 says `(unreleased)`.
- Tags: `v0.6.0`, `v0.7.0`, `v0.8.0`, `v0.9.0`, `v0.10.0` (`f3a42a7`, 2026-10-31),
  `v0.12.0` (`5804e60`, 2026-11-06), and `audit-trace-v1`. There is no `v0.11.0` and
  no `v0.13.0` tag, and no tracked file claims either one exists.
- `0.11.0` and `0.12.1` are working versions that were never released or tagged;
  0.12.1 was superseded by 0.13.0 before either was cut.

## Corrected in place

These are current-state statements, so they were corrected rather than annotated.

| Where | Said | Now says |
|---|---|---|
| `docs/USER-MANUAL.md`, Git status row | package version **0.12.1**; "the identity and freeze tests skip their engine checks for an unreleased version by design" | version **0.13.0**; the freeze test compares the published artifacts against `v0.9.0` and `docs/engine_pin.json` pins every module at 0.13.0 — the version-gated skip was removed on 2026-11-08 |
| `CHANGELOG.md`, 0.12.1 heading | `## [0.12.1] — (unreleased)` | `## [0.12.1] — (unreleased; superseded by 0.13.0)`, the wording the 0.11.0 heading already uses |
| `README.md`, banner (twice) | "the package version stays untagged" | "was left untagged at that freeze and was released later as `v0.10.0`" |
| `CHANGELOG.md`, 0.10.0 body | "**The package version stays untagged.**" | "**was left untagged at that freeze**", with a dated correction naming 2026-10-31 and 2026-11-06 |
| `docs/USER-MANUAL.md`, Phase M section | "The **package version stays untagged**" | the same restatement corrected, dated |
| `docs/FACTS-SHEET.md` | AA26 asserted "the **package version stays untagged**" as current | new row AA27 records that the claim was true at the 2026-10-28 freeze and was overtaken on 2026-10-31 |

## Disclosed, not rewritten

Dated records whose wording was true when written. They are left byte-identical;
this note is the disclosure the 2026-10-31 decision asked for.

| Where | What it says | Why it stands |
|---|---|---|
| `docs/AUDIT-TRACE-SPEC.md`, sections 6 and 7 | "the **package version stays untagged**" | the specification of the 2026-10-28 freeze; a frozen document, and true at the freeze |
| `docs/DECISION-V2-SCOPE.md` | "package version `0.10.0` remains untagged" | a dated decision record written on 2026-10-31, before that day's tag existed |
| `docs/V1-FREEZE.md`, section 7 | "`tests/test_v1_freeze.py` skips its byte-identity comparison at package versions at or above 0.12.0" | a dated amendment record; the skip was removed on 2026-11-08, and the file's own header says its sections are left as written |
| `research-journal/phase_g_findings_20261021.md`, the freeze-decision section | "0.10.0, unreleased and untagged" | the research record of the 2026-10-28 decision, which is what was true then |
| `CITATION.cff` | `date-released: 2026-11-06` beside `version: 0.13.0` | there is no release date for an unreleased version; the field carries the 0.12.0 deposit tag's date, and the file's comment block says so |

## Checked and found consistent

- `CHANGELOG.md` head table: 0.13.0 unreleased, 0.12.0 cut 2026-11-06, `v0.10.0` the
  previous tag, `v0.9.0` the latest published release.
- `README.md` status section: 0.13.0 unreleased on top of the 0.12.0 deposit, latest
  cut version 0.12.0, `v0.9.0` the archival reference for the frozen engine.
- `.zenodo.json` and `zenodo/software-v0.12.0.json`: both describe the v0.12.0
  deposit and say it is cut and tagged with no GitHub release page.
- `docs/ENGINE-VERSION-AUDIT.md`: "0.11.0 and 0.13.0 were never tagged" — true.
- `docs/RESEARCH-FINDINGS.md`, the engine-stamped artifacts and the question registry
  use 0.13.0 as the pinned engine, which is what `docs/engine_pin.json` records.

## What did not change, and the limits

No version number, tag, engine file, result artifact, test count or protocol. The
three declarations still say 0.13.0, the pin still records 0.13.0 at `6e0ff24`, and
`v0.13.0` still does not exist — which rule 10 allows while the changelog heading
says `(unreleased)`.

The sweep matched text, not meaning: each occurrence of a version number or a
release-state word was judged, so a stale statement phrased without either would
not have been found. Claims about GitHub release pages were not re-verified, because
this workspace cannot query them; they are consistent across the documents that
make them.
