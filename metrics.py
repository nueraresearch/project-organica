"""metrics.py
Utility functions for parsing organica.log and generating health & extended metrics.
Both the CLI dashboard (dashboard.py) and the Streamlit UI import these.
"""
import json
import re
import pathlib
import datetime
import collections
from typing import List, Dict, Any

# Path to the log file (relative to repository root)
LOG_PATH = pathlib.Path(__file__).parent / "organica.log"


def _load_log_lines() -> List[str]:
    """Yield log lines as raw strings, handling large files efficiently."""
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")


def parse_cycles() -> List[Dict[str, Any]]:
    """Parse the log and return a list of per‑cycle dictionaries.

    Expected log format (example)::

        2026-10-20T00:12:34Z | Cycle 1 | composites=120 | concepts=2 | loops=1 | hypotheses=0 | dreams=0

    The function is tolerant – it extracts any ``key=value`` pairs it finds.
    """
    cycles: List[Dict[str, Any]] = []
    # Rough pattern to capture cycle number and the remainder of the line
    pattern = re.compile(r"Cycle\s+(\d+).*?(\d{4}-\d{2}-\d{2}T[^|]+)\s*\|\s*(.*)")
    for line in _load_log_lines():
        if "Cycle" not in line or "|" not in line:
            continue
        match = pattern.search(line)
        if not match:
            continue
        cycle_num = int(match.group(1))
        timestamp = match.group(2)
        rest = match.group(3)
        kv: Dict[str, Any] = {"cycle": cycle_num, "timestamp": timestamp}
        for part in rest.split("|"):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                try:
                    kv[k.strip()] = int(v.strip())
                except ValueError:
                    kv[k.strip()] = v.strip()
        cycles.append(kv)
    return cycles


def aggregate_metrics(cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return a dictionary of aggregated statistics across all cycles."""
    agg: collections.Counter = collections.Counter()
    for c in cycles:
        for k, v in c.items():
            if isinstance(v, int):
                agg[k] += v
    total_cycles = len(cycles)
    agg["total_cycles"] = total_cycles
    if total_cycles:
        agg["avg_composites_per_cycle"] = agg.get("composites", 0) / total_cycles
    return dict(agg)


def event_type_counts() -> Dict[str, int]:
    """Count occurrences of different event keywords in the raw log.
    Keywords are domain‑specific (auth, session, expired, failure, resource, dream,
    hypothesis, experiment).
    """
    keywords = ["auth", "session", "expired", "failure", "resource", "dream", "hypothesis", "experiment"]
    counts = collections.Counter()
    for line in _load_log_lines():
        low = line.lower()
        for kw in keywords:
            if kw in low:
                counts[kw] += 1
    return dict(counts)


def dream_type_distribution() -> Dict[str, int]:
    """Extract dream sub‑type information if logged as ``dream=TYPE``.
    Returns a Counter dict of dream types.
    """
    dist = collections.Counter()
    for line in _load_log_lines():
        if "dream=" in line.lower():
            m = re.search(r"dream=([^|\s]+)", line, re.IGNORECASE)
            if m:
                dist[m.group(1).lower()] += 1
    return dict(dist)


def hypothesis_lifecycle() -> Dict[str, List[int]]:
    """Collect birth and death cycles for hypotheses.
    Expected fragments::
        Cycle 123 | hypothesis_birth=id42
        Cycle 145 | hypothesis_death=id42
    Returns ``{hypothesis_id: [birth_cycle, death_cycle]}`` (death may be ``None``).
    """
    lifecycles: Dict[str, List[int]] = {}
    birth_pat = re.compile(r"hypothesis_birth=([\w-]+)")
    death_pat = re.compile(r"hypothesis_death=([\w-]+)")
    for line in _load_log_lines():
        cycle = _extract_cycle_number(line)
        if "hypothesis_birth" in line:
            m = birth_pat.search(line)
            if m:
                hid = m.group(1)
                lifecycles.setdefault(hid, [None, None])[0] = cycle
        if "hypothesis_death" in line:
            m = death_pat.search(line)
            if m:
                hid = m.group(1)
                lifecycles.setdefault(hid, [None, None])[1] = cycle
    return {hid: vals for hid, vals in lifecycles.items()}


def _extract_cycle_number(line: str) -> int:
    """Helper to pull the cycle number from a log line. Returns -1 if not found."""
    m = re.search(r"Cycle\s+(\d+)", line)
    return int(m.group(1)) if m else -1


def snapshot_to_json(snapshot_path: pathlib.Path | None = None) -> Dict[str, Any]:
    """Collect all metrics into a single dict and optionally write to *snapshot_path* as JSON."""
    cycles = parse_cycles()
    data = {
        "aggregated": aggregate_metrics(cycles),
        "event_counts": event_type_counts(),
        "dream_distribution": dream_type_distribution(),
        "hypothesis_lifecycle": hypothesis_lifecycle(),
        "last_updated": datetime.datetime.utcnow().isoformat() + "Z",
    }
    if snapshot_path:
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        with snapshot_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    return data


if __name__ == "__main__":
    # Simple CLI entry point for debugging
    import pprint
    pprint.pprint(snapshot_to_json())
