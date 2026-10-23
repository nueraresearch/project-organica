"""
Archive the daemon's run log into a per-cycle series.

Why this is a tool and not a one-off script
--------------------------------------------
The first version of this lived in .scratch/ and had a defect: it copied
`rec["contradiction_total"]` out of each log record, but run_continuous.py
never writes that key. Every archived value was therefore `null`, which
reads as "zero contradiction everywhere" -- and the real final value is
400,550. The contradiction totals are re-derived here from the hypothesis
snapshot, which IS in the record, and the raw contradiction is also
available per hypothesis.

The archived series is the "before" arm of the longitudinal record, so it
has to be right.

Usage:
    python benchmarks/archive_run.py --log logs/organica_prefix_20261022.log
    python benchmarks/archive_run.py --log organica.log --out docs/current_series.json

The log line format is:
    2026-10-22 16:10:08,894 INFO Cycle 3457: {json...}
so the JSON starts at the first '{'.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

FIELDS = ("cycle", "sleep_cycle", "theories", "questions", "hypotheses",
          "dreams", "investigations", "experiments")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=str(REPO / "logs" /
                                         "organica_prefix_20261022.log"))
    ap.add_argument("--out", default=str(REPO / "docs" / "prefix_run_series.json"))
    ap.add_argument("--note", default="the 'before' series for the "
                                      "retention-policy comparison")
    args = ap.parse_args()

    log = Path(args.log)
    if not log.exists():
        raise SystemExit(f"log not found: {log}")

    series = []
    with log.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            brace = line.find("{")
            if brace < 0:
                continue
            try:
                rec = json.loads(line[brace:])
            except json.JSONDecodeError:
                continue
            snap = rec.get("hypothesis_snapshot") or []

            # Re-derive the contradiction total from the snapshot. The
            # daemon does not write a `contradiction_total` field; reading
            # one from the record yields null for every cycle.
            contradiction_total = sum(h.get("contradiction_count") or 0
                                      for h in snap)
            support_total = sum(h.get("support_count") or 0 for h in snap)

            row = {k: rec.get(k) for k in FIELDS}
            row["contradiction_total"] = contradiction_total
            row["support_total"] = support_total
            row["hypotheses_detail"] = [
                {"id": h.get("id"), "subject": h.get("subject"),
                 "confidence": h.get("confidence"),
                 "support": h.get("support_count"),
                 "contradiction": h.get("contradiction_count"),
                 "generation": h.get("generation")}
                for h in snap
            ]
            series.append(row)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "source": f"{log} (raw copy archived to {log})",
        "note": args.note,
        "contradiction_derivation": "summed from hypothesis_snapshot; the "
                                    "daemon log does not carry a "
                                    "contradiction_total field",
        "cycles": len(series),
        "series": series,
    }, indent=1), encoding="utf-8")

    print(f"{len(series)} cycles -> {out}")
    if series:
        print(f"final contradiction_total = {series[-1]['contradiction_total']}")
        print(f"final support_total       = {series[-1]['support_total']}")


if __name__ == "__main__":
    main()
