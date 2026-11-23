# Authorisation — CONFIRMATORY-RETENTION-INCREMENTAL-1

Dated 2026-11-12. The owner authorised the following instruction:

> Grant the retention block and run its twelve cells, then adjudicate the result.

This grant covers the twelve cells frozen in `docs/retention_incremental_prereg.json`:
seeds `20618101-20618112`, 120 cycles each, cap 40, one replay per seed, followed by
the block's own `--finish` adjudication.

It does not authorise an engine edit, a different cap, a different seed, an extra
cell, or a promotion. A preliminary collection that did not meet the frozen
120-cycle design was discarded before adjudication; the corrected parts and
their regeneration are disclosed in the result page.
