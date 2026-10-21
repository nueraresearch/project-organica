# Project Organica — Agent Guide

This file is the standing brief for any agent (or person) working on this repository. Read it before changing anything.

## What this project is

Project Organica is a research codebase for a *developmental* machine intelligence: a program that grows cognitive structures from a raw event stream through repeated sleep/consolidation cycles, rather than loading pre-trained weights. The full architecture, the nine emergence targets, the six design laws, and the current state of the 90-day longitudinal study are documented in:

- **`docs/USER-MANUAL.md`** — the owner's manual. Start here. It covers what the project is, how to run everything, how to read the telemetry, the action list, and troubleshooting.
- `research-journal/phase_g_findings_20261021.md` — the Phase G audit (nine findings, with evidence).
- `CHALLENGE.md` — the nine emergence targets and the integrity constraint.
- `docs/DESIGN_LAWS.md` — the six inviolable laws.

## Standing rule — keep the manual current

> **`docs/USER-MANUAL.md` must be updated in the same turn as any change it describes.**

This is not optional and not deferrable. Specifically, update the manual when any of these change:

- the daemon's running state or any metric in its status section
- a command, launcher, script, or path
- the meaning of a log field or snapshot artifact
- the study protocol or the emergence targets
- **the owner's action list** — when a decision is made, record it with a date and a one-line rationale
- a finding
- a troubleshooting symptom or fix
- a file's role in the file map

Also append a row to the manual's **Revision log** whenever you edit it.

Rationale: the manual is the single place the owner looks to answer "where are we at, what do I need to do, and what does this output mean". A stale manual is worse than no manual, because it is trusted. The research journal is the scientific record and is updated separately; the manual is the operational one.

## Rules that are not negotiable in this repo

1. **Generation 9 is locked.** Do not implement self-modeling. The project exists to earn it.
2. **Phase A froze the cognitive primitives at v1.0.** Do not change *which* structures compete, how confidence is computed, or how the layers select candidates without an explicit recorded decision. Substrate and measurement changes are fine; cognition changes need a decision first. There is a known pending amendment (journal §7) — do not silently apply it.
3. **Never truncate `organica.log`.** It is the longitudinal record and is append-only. The daemon owns it through its logging `FileHandler`.
4. **The sleep-cycle counter must stay monotonic.** `organica/memory.py` keeps it in the `sleep_cycles` table. Do not reintroduce a sliding-window read of the events table for this — that was the bug that reset the counter mid-run.
5. **Substrate changes must be behaviour-preserving and proven so.** `tests/test_substrate_equivalence.py` is the pattern: if you change how anything is read or written, add a test showing the result is identical to the old behaviour.
6. **Do not commit or push without being asked.** The owner has not authorized commits; work is currently uncommitted by design.
7. **Do not add third-party runtime dependencies.** The core is standard library only.

## If a study run is live, the engine is frozen

A live run is one constant engine plus one constant stimulus. While the daemon is running against `memory.db`:

- **Do not change `organica/sleep.py` or the semantics of `organica/memory.py`.** That ends the run; the old one must be archived and a fresh database started.
- **Do not change the event stream in `organica/streams.py`.** A different stimulus is a different experiment.
- **Performance-only substrate changes are allowed only if a test proves the result is identical.** That is what `tests/test_substrate_equivalence.py` is for.
- Everything else — harness, metrics, dashboards, API, benchmarks, examples, docs — is free to change.

Pausing and restarting the daemon are both fine: the counter is monotonic and the log appends across restarts. Note any pause in the write-up, because the organism did not experience the missing wall-clock time.

**Never let a script write to the live `memory.db`.** Use `organica.paths.scratch_db()` for anything disposable. Several example scripts used to open `Path("memory.db")` in the working directory, which would have deleted the live study's substrate; they now write to `.scratch/`.

See `docs/USER-MANUAL.md` §6.4 for the full table.


## Verifying a change

```bash
python -m pytest tests -q                 # 17 tests, must be green
python benchmarks/study_health.py          # study must stay healthy
python benchmarks/lineage_audit.py         # Law II must stay at 100% grounded
python benchmarks/g5_gap_diagnostic.py --cycles 10   # G5 must remain reachable
```

The study daemon may be running against `memory.db`. Prefer read-only inspection, or work on a copy, so you do not disturb a multi-week run.
