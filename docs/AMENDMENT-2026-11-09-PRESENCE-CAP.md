# Amendment — the presence artifact's cap note, 2026-11-09

**The note is wrong; the measurement is not.** `docs/temporal_presence_0.13.0.json` records a
`cap_note` saying "the frozen prediction cap of 20 does not apply". The engine at the recorded
commit defines `MAX_PREDICTIONS = 40` (`organica/sleep.py:99`), and the artifact's own rows
assert 28-36 world edges per seed, which a cap of 20 cannot produce. The number in the note is
stale: the cap moved from 20 to 40 before 0.13.0.

The presence figure is unaffected. Presence is counted in raw temporal memory before any cap is
applied, which is why it is 112 of 112 on every seed; the asserted coverage beside it
(0.2500-0.3214) is measured at cap 40. Nothing in this amendment changes a row, a ratio or a
seed.

The artifact is not rewritten: it is the record of what was measured, and a published number is
corrected by a dated amendment rather than by editing the file (AGENTS.md rule 16). This page is
the correction of record. Q002's closure and C003's promotion cite the artifact together with
this amendment, and C003's scope limitation already says the claim is about presence rather than
selection.

`python -m benchmarks.tier1_preflight --check` and the engine stamp are unaffected: no engine
file and no result artifact changed.
