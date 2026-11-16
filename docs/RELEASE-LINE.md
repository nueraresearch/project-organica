# Release line — the programme called V2 is pre-1.0, targeted at 0.20.0

**Recorded 2026-11-16 on the owner's instruction.** This note defines a label. It changes no code, no version, no pin and no
decision.

## What "V2" means here

"V2" is the internal shorthand for the project's second research programme — the mutable-identity line
([`DECISION-V2-CHARTER`](DECISION-V2-CHARTER.md), [`V2-MUTABLE-IDENTITY-SPEC`](V2-MUTABLE-IDENTITY-SPEC.md),
[`V2-FIRST-EXPERIMENT-PREREGISTRATION`](V2-FIRST-EXPERIMENT-PREREGISTRATION.md) and its diagnostics). It is a **programme
label, not a version number.**

## The release it belongs to

The line is a **pre-1.0** release. It is **not a 2.x release**, and no document should describe it as "version 2" or
"2.0.0".

The first release of this line will be numbered **0.20.0** — "somewhere around 0.20.0" in the owner's words — under the
existing SemVer pre-1.0 convention: the MINOR number carries the meaning and the public API is not yet declared stable. The
exact number is fixed when the release is cut, and that is the owner's decision.

## What this note does not change

The package version remains **0.15.0** and the engine stays pinned at 0.15.0. The three version declarations
(`organica.__version__`, `pyproject.toml`, `CITATION.cff`) are unchanged, and no tag is moved. A bump to 0.20.0 is a future
release action: it needs the owner's decision, the three declarations updated together, a changelog entry, and — because the
engine files are pinned — the pin updated in the same recorded act (AGENTS.md rule 10).

## Why the V2 file and decision names stay

Renaming the `DECISION-V2-*` and `V2-*` documents, the benchmark modules and their artifacts would break references across
more than sixty documents and every result that cites them, for no gain in precision. The names are kept as the programme's
internal label; this note is the definition that keeps "V2" from being read as a version number.

## The three namespaces still hold

Package version (`0.x.y`, currently `0.15.0`), architecture generation (*Organica 1* frozen, *Organica 2* planning only), and
research campaign (this programme, releasing as 0.20.0). See [`USER-MANUAL`](USER-MANUAL.md) §11.6.
