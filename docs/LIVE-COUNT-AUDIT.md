# Live-count audit — which figures quote a quantity that moves?

**Date:** 2026-11-15

**Status:** `AUDIT — THREE STALE LIVE COUNTS CORRECTED, ONE ALREADY FIXED, ONE GUARD ADDED`

**Scope:** prose figures in `CHANGELOG.md` and `docs/*.md` that quote a **live count** — a quantity that grows
as records land — as distinct from a **frozen measurement** (a cell count inside a recorded run, a seed count
inside a frozen block, a threshold, a coefficient). No measurement, threshold, gate or verdict is touched.

## The distinction this audit is drawn on

A frozen measurement is a fact about a run that already happened: `448 cells on 0.12.0`, `275 cells`,
`240 of 240 cells`. It cannot drift, because nothing re-runs it. A **live count** is a fact about the tree:
how many artifacts the Stage B scan covers, how many decisions the index holds, how many questions the
registry carries, how many modules the layer census covers, how many tests the suite runs. Those numbers change
whenever someone lands a record, and a document that quotes one is making a claim with a shelf life.

The failure mode is not that the prose is wrong when written — it is that nothing notices when it stops being
true. The 0.13.0 entry quoted `214` artifacts for weeks after the artifact read `228`, and the only reason it
was caught is that someone read it.

## Method

A census over `CHANGELOG.md` and every `docs/*.md`: find every `<number> <noun>` where the noun is artifact,
question, decision, module, test or document; compare each number against its live source; then classify each
surviving mismatch by **where the line sits** — inside a dated revision-log row (a snapshot of that date, and by
this repo's convention left as written) or in undated prose that a reader takes as current.

Live sources and their values on this date:

| Source | Quantity | Value |
| --- | --- | ---: |
| `docs/decisions.json` | decisions (18 ADOPTED, 1 WITHDRAWN, 6 PENDING) | **25** |
| `docs/research_question_registry.json` | questions (15 closed, 31 open, 2 retired, 6 future) | **54** |
| `docs/stage_b_protocol.json` | `disjoint_proved_against` artifacts | **228** |
| `docs/stage_b_protocol.json` | `consumed_total` seeds | **1,668** |
| `tests/test_*.py` | test modules | **247** |
| `docs/*.md` | documents | **385** |

## Findings

| Where | Quote | Live at writing | Now | Disposition |
| --- | --- | ---: | ---: | --- |
| `CHANGELOG.md`, 0.13.0 entry | "covers **228** artifacts" | 214 | 228 | **corrected 2026-11-15**, with the earlier value kept as superseded; guarded by `tests/test_changelog_figures.py` |
| `docs/CONTEXT.md` | "which of the 54 questions in `docs/RESEARCH-QUESTION-REGISTRY.md` (count as of 2026-11-15)" | 23 | 54 | **corrected today**, with an as-of marker; guarded by `tests/test_live_counts.py` |
| `docs/AUTHORISATION-PROVENANCE-AUDIT.md` | "**1644** consumed seeds across **209** artifacts *at this audit's date*" | 1,644 / 209 on 2026-11-13 | 1,668 / 228 | **superseded note added today**; the sentence stays as written because it was true then |
| `docs/RESEARCH-HIERARCHY.md` | "14 documents and 21 records at that audit's 2026-11-13 date … the sets have since grown to 16 and 23" | 14 / 21 | 16 / 23 | **scope dated in place today** |

Three of these were live claims a reader would take as current, and all three had drifted. The fourth — the
Stage B figure — was fixed earlier today in the entry that tracks it.

### What the census cleared

- **The manual's revision log.** It quotes decision counts (`13 decisions: 9 adopted…`), question counts
  (`53`, `41`, `28`, `23`), the layer census (`157 modules`) and dozens of Stage B figures. Every one sits
  inside a dated row. Rows record what was true on their date; rewriting them would destroy the record that
  makes the log useful. They are cleared as historical, not as current claims.
- **Dated changelog entries.** `209`, `208`, `188`, `184`, `183`, `180` artifacts all belong to dated entries,
  each of which says what the tree held then, and several already carry "Superseded later on …" markers.
- **Generated documents.** `docs/RESEARCH-QUESTION-REGISTRY.md`, `docs/RESEARCH-FINDINGS.md`,
  `docs/RESEARCH-DASHBOARD.md`, `docs/question_survival.md` and `docs/DECISIONS.md` are rendered from their
  JSON sources; their counts cannot drift without `--check` failing.
- **The test count in `AGENTS.md`.** Written between the machine-readable test-count markers by
  `benchmarks/test_count.py`, so it is machine-maintained rather than transcribed. (This document does not
  quote those markers literally: a markdown file that contains the marker string itself becomes one of the
  files the changelog-figure check counts, which is how writing this audit broke that check once.)

## The guard

`tests/test_live_counts.py` scans every `docs/*.md` for `N questions in docs/RESEARCH-QUESTION-REGISTRY.md`
and requires `N` to equal the registry's length today. It carries its own control: the census function is
asserted to *reject* the stale value it was written for, so the check cannot pass by matching nothing.

This covers the one live count that was both stale and hand-written in prose. The other two were fixed by
dating the statement rather than by tracking it, which is the cheaper repair when the number belongs to a
specific audit's scope.

## What this does not claim

It does not make the corpus free of live counts — the ones inside dated rows remain, deliberately. It does not
audit frozen measurements for correctness; a product count, a seed count or a coefficient is a different kind
of claim and is guarded, where it is guarded at all, by the artifact tests. And it does not add a general
"no undated numbers" rule: the useful rule is narrower — **a live count in undated prose must equal its source
or say when it was true**, and that rule now has a test behind it.

## Reproduce

```bash
python -m pytest tests/test_live_counts.py -q                    # the registry-size guard and its control
python -m pytest tests/test_changelog_figures.py -q              # the Stage B figure and its drift control
python -m benchmarks.test_count --check                          # the AGENTS.md test count (pre-existing drift)
```
