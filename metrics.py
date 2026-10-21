"""metrics.py
Utility functions for parsing organica.log and generating health & extended metrics.
Both the CLI dashboard (dashboard.py) and the Streamlit UI import these.
"""
import json
import re
import pathlib
import datetime
import collections
from typing import List, Dict, Any, Optional

# Path to the log file (relative to repository root)
LOG_PATH = pathlib.Path(__file__).parent / "organica.log"

# Developmental ladder, in the order a generation is expected to appear.
POPULATION_KEYS = (
    "concepts", "predictions", "loops", "hypotheses", "theories",
    "questions", "dreams", "investigations", "experiments",
)

# Fields that represent current state (show latest, not sum), in report order.
STATE_FIELDS = POPULATION_KEYS + ("total_composites",)

# Minimum number of key=value pairs a legacy pipe-delimited line must yield
# before it is accepted as a cycle record.
MIN_FALLBACK_FIELDS = 2


def _load_log_lines(log_path: Optional[pathlib.Path] = None) -> List[str]:
    """Return the raw log lines as strings.

    The daemon rewrites ``organica.log`` on restart, so the file may be
    missing, truncated or half written; unreadable bytes are replaced instead
    of raising and a missing file yields an empty list.
    """
    path = pathlib.Path(log_path) if log_path is not None else LOG_PATH
    lines: List[str] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                lines.append(line.rstrip("\n"))
    except (OSError, ValueError):
        return lines
    return lines


def parse_cycles(log_path: Optional[pathlib.Path] = None) -> List[Dict[str, Any]]:
    """Parse the log and return a list of per-cycle dictionaries.

    Supports the actual log format::

        2026-10-20 22:57:46,154 INFO Cycle 140: {"cycle": 140, "sleep_cycle": 459, ...}

    Falls back to pipe-delimited key=value format if JSON is not found. That
    fallback is strict: a line is only accepted as a cycle record when it
    yielded at least ``MIN_FALLBACK_FIELDS`` usable key/value pairs, so a
    malformed JSON line can never masquerade as an (almost) empty cycle.

    A missing or half written log yields an empty list instead of raising.
    """
    cycles: List[Dict[str, Any]] = []
    # Match: <timestamp> INFO Cycle N: {JSON}
    json_pattern = re.compile(r"Cycle\s+\d+:\s+(\{.*\})")
    cycle_number_pattern = re.compile(r"Cycle\s+(\d+)")
    for line in _load_log_lines(log_path):
        if "Cycle" not in line:
            continue
        m = json_pattern.search(line)
        if m:
            try:
                kv = json.loads(m.group(1))
            except json.JSONDecodeError:
                kv = None
            if isinstance(kv, dict):
                if "cycle" not in kv:
                    cm = cycle_number_pattern.search(line)
                    if cm:
                        kv["cycle"] = int(cm.group(1))
                cycles.append(kv)
                continue
            # Malformed JSON: fall through to the strict legacy parser below.
        # Fallback: pipe-delimited key=value format
        if "|" not in line:
            continue
        cycle_m = cycle_number_pattern.search(line)
        if not cycle_m:
            continue
        kv = {"cycle": int(cycle_m.group(1))}
        usable = 0
        for part in line.split("|"):
            part = part.strip()
            if "=" not in part:
                continue
            k, v = part.split("=", 1)
            k = k.strip()
            if not k:
                continue
            try:
                kv[k] = int(v.strip())
            except ValueError:
                kv[k] = v.strip()
            usable += 1
        if usable < MIN_FALLBACK_FIELDS:
            continue
        cycles.append(kv)
    return cycles


def aggregate_metrics(cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return aggregated statistics across all cycles, plus latest-cycle snapshot.

    The current organism state is published under the ``latest_snapshot`` key;
    it is a plain key so the result stays a clean JSON document without
    underscore-prefixed entries.
    """
    if not cycles:
        return {"total_cycles": 0, "latest_snapshot": {}}

    # Fields that represent current state (show latest, not sum)
    state_fields = set(STATE_FIELDS)

    agg: collections.Counter = collections.Counter()
    total_duration_ms = 0
    status_counts: Dict[str, int] = {}
    max_consecutive_errors = 0

    for c in cycles:
        for k, v in c.items():
            if isinstance(v, int) and k not in state_fields and k not in (
                "cycle", "sleep_cycle", "consecutive_errors", "duration_ms"
            ):
                agg[k] += v

        s = c.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1
        total_duration_ms += c.get("duration_ms", 0)
        ce = c.get("consecutive_errors", 0)
        if ce > max_consecutive_errors:
            max_consecutive_errors = ce

    total_cycles = len(cycles)
    successful = status_counts.get("success", 0)
    failed = status_counts.get("failed", 0)

    # Latest cycle snapshot (current organism state)
    latest = cycles[-1]
    latest_snapshot = {k: latest.get(k, 0) for k in STATE_FIELDS}
    latest_snapshot["cycle"] = latest.get("cycle", 0)
    latest_snapshot["timestamp"] = latest.get("timestamp", "")

    result = dict(agg)
    result["total_cycles"] = total_cycles
    result["successful_cycles"] = successful
    result["failed_cycles"] = failed
    result["unknown_status_cycles"] = status_counts.get("unknown", 0)
    result["success_rate_pct"] = round(100 * successful / total_cycles, 2) if total_cycles else 0
    result["avg_duration_ms"] = round(total_duration_ms / total_cycles, 1) if total_cycles else 0
    result["max_consecutive_errors"] = max_consecutive_errors
    result["avg_composites_per_cycle"] = round(
        result.get("composites_created", 0) / total_cycles, 2
    ) if total_cycles else 0
    result["latest_snapshot"] = latest_snapshot
    return result


def population_counts(cycles: Optional[List[Dict[str, Any]]] = None) -> Dict[str, int]:
    """Return, per developmental population, the number of cycles it appeared in.

    A population counts as present in a cycle when its value is non-zero. The
    numbers are derived from the parsed cycle records, so they describe real
    activity instead of the JSON summary boilerplate present on every line.
    """
    if cycles is None:
        cycles = parse_cycles()
    counts: collections.Counter = collections.Counter()
    for c in cycles:
        for key in POPULATION_KEYS:
            value = c.get(key, 0)
            if isinstance(value, int) and value > 0:
                counts[key] += 1
    return {key: counts.get(key, 0) for key in POPULATION_KEYS}


def event_type_counts() -> Dict[str, int]:
    """Return event-type counts derived from the parsed cycle records.

    Thin wrapper around :func:`population_counts`, kept for backwards
    compatibility with existing callers.
    """
    return population_counts()


def legacy_keyword_counts() -> Dict[str, int]:
    """Count occurrences of raw keywords in the log text.

    Kept for reference only: the daemon writes its JSON summary on every
    cycle, so keywords such as "hypothesis" or "dream" are dominated by that
    boilerplate and the numbers say nothing about real events.
    """
    keywords = ["auth", "session", "expired", "failure", "resource", "dream", "hypothesis", "experiment"]
    counts = collections.Counter()
    for line in _load_log_lines():
        low = line.lower()
        for kw in keywords:
            if kw in low:
                counts[kw] += 1
    return dict(counts)


def dream_type_distribution(cycles: Optional[List[Dict[str, Any]]] = None) -> Dict[str, int]:
    """Return dream activity by category, read from dream_categories in each cycle's JSON log.

    Falls back to count-bucketing if dream_categories is not yet present
    (older log entries before the harness was updated).
    """
    if cycles is None:
        cycles = parse_cycles()
    dist: collections.Counter = collections.Counter()
    has_categories = False
    for c in cycles:
        cats = c.get("dream_categories")
        if cats and isinstance(cats, dict):
            has_categories = True
            for cat, count in cats.items():
                dist[cat] += count

    # Fallback: bucket by count if no category data yet
    if not has_categories:
        buckets: Dict[str, int] = {"0": 0, "1-3": 0, "4-6": 0, "7-10": 0, "10+": 0}
        for c in cycles:
            n = c.get("dreams", 0)
            if n == 0:
                buckets["0"] += 1
            elif n <= 3:
                buckets["1-3"] += 1
            elif n <= 6:
                buckets["4-6"] += 1
            elif n <= 10:
                buckets["7-10"] += 1
            else:
                buckets["10+"] += 1
        return buckets

    return dict(dist)


def dream_counts_over_time() -> Dict[int, int]:
    """Return {cycle_number: dream_count} for plotting dream activity over time."""
    return {c["cycle"]: c.get("dreams", 0) for c in parse_cycles()}


def hypothesis_lifecycle(cycles: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Track hypothesis population changes and individual hypothesis history.

    For cycles that include ``hypothesis_snapshot`` (new log format), tracks
    per-hypothesis confidence and support over time.
    For older cycles, detects birth/death events as count changes between cycles.

    Returns a dict with summary stats and recent events.
    """
    if cycles is None:
        cycles = parse_cycles()
    if not cycles:
        return {}

    # Per-hypothesis confidence history from snapshot data
    hyp_history: Dict[str, list] = {}
    events = []
    peak_count = 0
    peak_cycle = 0
    total_births = 0
    total_deaths = 0
    prev_ids: set = set()
    prev_count = cycles[0].get("hypotheses", 0)

    for c in cycles:
        cyc = c.get("cycle", 0)
        count = c.get("hypotheses", 0)
        snapshot = c.get("hypothesis_snapshot", [])

        if snapshot:
            current_ids = {h["id"] for h in snapshot if h.get("id")}
            born = current_ids - prev_ids
            died = prev_ids - current_ids
            for hid in born:
                events.append({"cycle": cyc, "type": "birth", "id": hid})
                total_births += 1
            for hid in died:
                events.append({"cycle": cyc, "type": "death", "id": hid})
                total_deaths += 1
            prev_ids = current_ids
            for h in snapshot:
                hid = h.get("id", "unknown")
                hyp_history.setdefault(hid, []).append({
                    "cycle": cyc,
                    "confidence": h.get("confidence", 0),
                    "support_count": h.get("support_count", 0),
                    "contradiction_count": h.get("contradiction_count", 0),
                })
        else:
            # Fallback: count-based birth/death detection
            delta = count - prev_count
            if delta > 0:
                total_births += delta
                events.append({"cycle": cyc, "type": "birth", "delta": delta, "count": count})
            elif delta < 0:
                total_deaths += abs(delta)
                events.append({"cycle": cyc, "type": "death", "delta": delta, "count": count})

        if count > peak_count:
            peak_count = count
            peak_cycle = cyc
        prev_count = count

    return {
        "total_births": total_births,
        "total_deaths": total_deaths,
        "peak_count": peak_count,
        "peak_cycle": peak_cycle,
        "tracked_hypotheses": len(hyp_history),
        "event_count": len(events),
        "recent_events": events[-20:],
        "hypothesis_histories": {
            hid: hist[-5:]  # last 5 observations per hypothesis
            for hid, hist in list(hyp_history.items())[:10]
        },
    }


def hypothesis_population_events(cycles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return exact per-hypothesis births and deaths derived from the log.

    Only cycles that carry a ``hypothesis_snapshot`` list can be diffed
    exactly; the id sets of consecutive snapshot-bearing cycles are compared to
    find the hypotheses that appeared (birth) or disappeared (death). Cycles
    without the field are skipped, so no event is invented for them.
    """
    events: List[Dict[str, Any]] = []
    prev_ids: set = set()
    for c in cycles:
        if "hypothesis_snapshot" not in c:
            continue
        snapshot = c.get("hypothesis_snapshot")
        if not isinstance(snapshot, list):
            continue
        current = {
            h.get("id"): h for h in snapshot
            if isinstance(h, dict) and h.get("id")
        }
        current_ids = set(current)
        cycle = c.get("cycle", 0)
        timestamp = c.get("timestamp", "")
        for hid in sorted(current_ids - prev_ids):
            h = current[hid]
            events.append({
                "type": "birth",
                "id": hid,
                "subject": h.get("subject", ""),
                "generation": h.get("generation", 0),
                "cycle": cycle,
                "timestamp": timestamp,
            })
        for hid in sorted(prev_ids - current_ids):
            events.append({
                "type": "death",
                "id": hid,
                "cycle": cycle,
                "timestamp": timestamp,
            })
        prev_ids = current_ids
    return events


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
        "dream_distribution": dream_type_distribution(cycles),
        "hypothesis_lifecycle": hypothesis_lifecycle(cycles),
        "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
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
