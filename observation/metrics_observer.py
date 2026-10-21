"""metrics_observer.py
Utility module that builds on `metrics.py` to produce the observation artifacts required for the 90‑day longitudinal study.
This code **does not modify** the Organica core daemon; it lives entirely in the `observation/` package.

Every window in this module is wall‑clock based: a "daily" artefact covers the
last 24 hours of recorded cycles, a "weekly" artefact the last 7 days. The
daemon rewrites `organica.log` on restart, so the observer tolerates a missing
or half written log and never writes an empty artefact.
"""

import datetime
import json
import logging
import pathlib
import sys
from typing import Any, Dict, List, Optional, Tuple

# Make the repository root importable however this module is launched
# (``python observation/metrics_observer.py`` or ``python -m observation.metrics_observer``).
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from metrics import (
    POPULATION_KEYS,
    aggregate_metrics,
    dream_type_distribution,
    event_type_counts,
    hypothesis_lifecycle,
    hypothesis_population_events,
    parse_cycles,
)

log = logging.getLogger(__name__)

# Base directory for all generated study artefacts
BASE_DIR = pathlib.Path(__file__).parent.parent / "snapshots"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Window widths of the artefacts, in hours
DAILY_WINDOW_HOURS = 24
WEEKLY_WINDOW_HOURS = 24 * 7

# Tolerance for clock skew between the daemon host and this observer
_CLOCK_SKEW = datetime.timedelta(minutes=5)


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------
def _now_utc() -> datetime.datetime:
    """Return the current time as an aware UTC datetime."""
    return datetime.datetime.now(datetime.timezone.utc)


def _iso_utc(moment: datetime.datetime) -> str:
    """Format an aware datetime as an ISO-8601 UTC string."""
    return moment.astimezone(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: Any) -> Optional[datetime.datetime]:
    """Parse a cycle ``timestamp`` (e.g. ``2026-10-21T05:30:32Z``) into aware UTC.

    Returns ``None`` when the value is missing or unparsable.
    """
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def _select_window(
    cycles: List[Dict[str, Any]], hours: int
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Return the cycles inside the trailing *hours* wall-clock window.

    The window ends at the current time. When the log is older than the window
    (the daemon is stopped) it is anchored on the newest recorded cycle
    instead, so the artefact still describes the last active period. Only
    cycles carrying a parsable ISO-8601 ``timestamp`` can be placed in the
    window; when no cycle carries one, every cycle is used.
    """
    meta: Dict[str, Any] = {
        "window_hours": hours,
        "window_start": None,
        "window_end": None,
        "window_anchor": "now",
        "cycles_in_window": 0,
        "cycles_total": len(cycles),
        "cycles_without_timestamp": 0,
    }
    timed: List[Tuple[datetime.datetime, Dict[str, Any]]] = []
    for c in cycles:
        stamp = _parse_timestamp(c.get("timestamp"))
        if stamp is not None:
            timed.append((stamp, c))
    if not timed:
        # No usable timestamps: keep every cycle rather than dropping all data.
        meta["window_anchor"] = "no_timestamps"
        meta["cycles_in_window"] = len(cycles)
        meta["cycles_without_timestamp"] = len(cycles)
        return list(cycles), meta

    timed.sort(key=lambda item: item[0])
    span = datetime.timedelta(hours=hours)
    end = _now_utc()
    selected = [(ts, c) for ts, c in timed if end - span <= ts <= end + _CLOCK_SKEW]
    if not selected:
        # Stale log: anchor the window on the newest recorded cycle.
        end = timed[-1][0]
        selected = [(ts, c) for ts, c in timed if end - span <= ts <= end]
        meta["window_anchor"] = "latest_cycle"
    meta["window_start"] = _iso_utc(end - span)
    meta["window_end"] = _iso_utc(end)
    meta["cycles_in_window"] = len(selected)
    meta["cycles_without_timestamp"] = len(cycles) - len(timed)
    return [c for _, c in selected], meta


def _observed_days(window: List[Dict[str, Any]]) -> float:
    """Return the wall-clock span of *window* in days (never below one hour)."""
    stamps = [ts for ts in (_parse_timestamp(c.get("timestamp")) for c in window) if ts]
    if len(stamps) < 2:
        return 0.0
    span_days = (stamps[-1] - stamps[0]).total_seconds() / 86400.0
    return max(span_days, 1.0 / 24.0)


# ---------------------------------------------------------------------------
# Population helpers
# ---------------------------------------------------------------------------
def _population_deltas(window: List[Dict[str, Any]]) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Return per-population births and deaths summed over the window.

    Every consecutive pair of cycles inside the window contributes the
    positive (birth) or negative (death) change of each population.
    """
    births = {key: 0 for key in POPULATION_KEYS}
    deaths = {key: 0 for key in POPULATION_KEYS}
    for previous, current in zip(window, window[1:]):
        for key in POPULATION_KEYS:
            before = previous.get(key, 0)
            after = current.get(key, 0)
            if not isinstance(before, int) or not isinstance(after, int):
                continue
            if after > before:
                births[key] += after - before
            elif after < before:
                deaths[key] += before - after
    return births, deaths


def _largest_step(window: List[Dict[str, Any]]) -> Tuple[int, int]:
    """Return the largest single-cycle birth and death seen inside the window."""
    largest_birth = 0
    largest_death = 0
    for previous, current in zip(window, window[1:]):
        step_birth = 0
        step_death = 0
        for key in POPULATION_KEYS:
            before = previous.get(key, 0)
            after = current.get(key, 0)
            if not isinstance(before, int) or not isinstance(after, int):
                continue
            if after > before:
                step_birth += after - before
            elif after < before:
                step_death += before - after
        largest_birth = max(largest_birth, step_birth)
        largest_death = max(largest_death, step_death)
    return largest_birth, largest_death


def _latest_cycle_info(cycles: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Return the state of the newest cycle, or ``{}`` when the log holds none."""
    if cycles is None:
        cycles = parse_cycles()
    if not cycles:
        return {}
    latest = cycles[-1]
    active = {
        "active_concepts": latest.get("concepts", 0),
        "active_predictions": latest.get("predictions", 0),
        "active_loops": latest.get("loops", 0),
        "active_hypotheses": latest.get("hypotheses", 0),
        "active_theories": latest.get("theories", 0),
        "active_questions": latest.get("questions", 0),
        "active_dreams": latest.get("dreams", 0),
        "active_investigations": latest.get("investigations", 0),
        "active_experiments": latest.get("experiments", 0),
    }
    return {
        "cycle": latest.get("cycle", 0),
        "timestamp": latest.get("timestamp", ""),
        **active,
    }


# ---------------------------------------------------------------------------
# Daily snapshot (essential)
# ---------------------------------------------------------------------------
def daily_snapshot(
    hours: int = DAILY_WINDOW_HOURS, log_path: Optional[pathlib.Path] = None
) -> Dict[str, Any]:
    """Aggregate the organism state over the trailing *hours* (24 h by default).

    ``births``/``deaths`` are summed over every consecutive cycle pair inside
    the window, so they describe the whole window instead of the 30-second
    step between the last two cycles. Returns ``{}`` when the log holds no
    usable cycles, so that no empty artefact is ever written.
    """
    cycles = parse_cycles(log_path)
    if not cycles:
        return {}
    window, meta = _select_window(cycles, hours)
    if not window:
        return {}
    latest = window[-1]
    births, deaths = _population_deltas(window)
    hypothesis_events = hypothesis_population_events(window)
    snapshot: Dict[str, Any] = {
        "cycle": latest.get("cycle", 0),
        "timestamp": latest.get("timestamp", ""),
        "active_concepts": latest.get("concepts", 0),
        "active_predictions": latest.get("predictions", 0),
        "active_loops": latest.get("loops", 0),
        "active_hypotheses": latest.get("hypotheses", 0),
        "active_theories": latest.get("theories", 0),
        "active_questions": latest.get("questions", 0),
        "active_dreams": latest.get("dreams", 0),
        "active_investigations": latest.get("investigations", 0),
        "active_experiments": latest.get("experiments", 0),
        "window_hours": meta["window_hours"],
        "window_start": meta["window_start"],
        "window_end": meta["window_end"],
        "window_anchor": meta["window_anchor"],
        "cycles_in_window": meta["cycles_in_window"],
        "births_in_window": sum(births.values()),
        "deaths_in_window": sum(deaths.values()),
        "births_by_population": births,
        "deaths_by_population": deaths,
        "hypothesis_births_in_window": sum(1 for e in hypothesis_events if e["type"] == "birth"),
        "hypothesis_deaths_in_window": sum(1 for e in hypothesis_events if e["type"] == "death"),
        "top_theories": [],  # placeholders – can be filled later from domain‑specific ranking
        "top_questions": [],
    }
    if hours == DAILY_WINDOW_HOURS:
        snapshot["births_last_24h"] = snapshot["births_in_window"]
        snapshot["deaths_last_24h"] = snapshot["deaths_in_window"]
    return snapshot


# ---------------------------------------------------------------------------
# Weekly aggregate (strongly recommended)
# ---------------------------------------------------------------------------
def weekly_aggregate(
    hours: int = WEEKLY_WINDOW_HOURS, log_path: Optional[pathlib.Path] = None
) -> Dict[str, Any]:
    """Aggregate the cycles of the trailing *hours* window (7 days by default).

    The window is wall-clock based, not "the last N cycles". Returns ``{}``
    when the log holds no usable cycles, so that no empty artefact is written.
    """
    cycles = parse_cycles(log_path)
    if not cycles:
        return {}
    window, meta = _select_window(cycles, hours)
    if not window:
        return {}
    births, deaths = _population_deltas(window)
    largest_birth, largest_death = _largest_step(window)
    weekly = {
        "window_hours": meta["window_hours"],
        "window_start": meta["window_start"],
        "window_end": meta["window_end"],
        "window_anchor": meta["window_anchor"],
        "window_cycles": len(window),
        "cycles_in_window": meta["cycles_in_window"],
        "aggregated": aggregate_metrics(window),
        "largest_births": largest_birth,
        "largest_deaths": largest_death,
        "births_by_population": births,
        "deaths_by_population": deaths,
        "top_theories": [],
        "top_questions": [],
    }
    return weekly


# ---------------------------------------------------------------------------
# Monthly genome (valuable)
# ---------------------------------------------------------------------------
def monthly_genome(log_path: Optional[pathlib.Path] = None) -> Dict[str, Any]:
    """Return the current belief population plus lifecycle and activity summaries.

    Returns ``{}`` when the log holds no usable cycles.
    """
    cycles = parse_cycles(log_path)
    latest = _latest_cycle_info(cycles)
    if not latest:
        return {}
    genome = {
        "cycle": latest["cycle"],
        "timestamp": latest["timestamp"],
        "belief_population": {
            "concepts": latest["active_concepts"],
            "predictions": latest["active_predictions"],
            "loops": latest["active_loops"],
            "hypotheses": latest["active_hypotheses"],
            "theories": latest["active_theories"],
            "questions": latest["active_questions"],
            "dreams": latest["active_dreams"],
            "investigations": latest["active_investigations"],
            "experiments": latest["active_experiments"],
        },
        "hypothesis_lifecycle": hypothesis_lifecycle(cycles),
        "population_counts": event_type_counts(),
        "dream_distribution": dream_type_distribution(cycles),
    }
    return genome


# ---------------------------------------------------------------------------
# Event journal – records major structural changes detected in the log
# ---------------------------------------------------------------------------
# Default journal locations (the paths actually used are resolved at call
# time, so a redirected BASE_DIR is honoured).
EVENT_JOURNAL = BASE_DIR / "event_journal.log"
EVENT_JOURNAL_STATE = BASE_DIR / "event_journal.state.json"


def _journal_path() -> pathlib.Path:
    """Return the journal path, resolved at call time (BASE_DIR can move)."""
    return BASE_DIR / "event_journal.log"


def _state_path() -> pathlib.Path:
    """Return the journal state cursor path, resolved at call time."""
    return BASE_DIR / "event_journal.state.json"


def _event_key(event: Dict[str, Any]) -> str:
    """Return the dedupe key of one event.

    The daemon restarts reset the cycle counter, so the cycle number alone is
    not unique; the ISO timestamp is part of the key to keep distinct events
    apart while repeated runs stay idempotent.
    """
    detail = event.get("id") or event.get("generation") or ""
    return "{cycle}|{timestamp}|{event}|{detail}".format(
        cycle=event.get("cycle", 0),
        timestamp=event.get("timestamp", ""),
        event=event.get("event", ""),
        detail=detail,
    )


def _detect_events(
    cycles: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """Derive structural events from consecutive cycles of the JSON log.

    The daemon writes one JSON summary per cycle, so events are inferred from
    the population changes between consecutive cycles:

    * ``generation_milestone`` – the first cycle in which a developmental
      generation (concepts, predictions, loops, …) is non-empty.
    * ``theory_birth`` / ``theory_death`` – the theory population grows or
      shrinks.
    * ``hypothesis_birth`` / ``hypothesis_death`` – exact per-hypothesis id
      differences when a cycle carries ``hypothesis_snapshot``; count deltas
      for the older cycles that do not.
    """
    if cycles is None:
        cycles = parse_cycles()
    events: List[Dict[str, Any]] = []
    seen_generations: set = set()
    previous: Optional[Dict[str, Any]] = None
    previous_hypothesis_ids: set = set()

    for cycle_record in cycles:
        cycle = cycle_record.get("cycle", 0)
        timestamp = cycle_record.get("timestamp", "")

        # Generation milestones: first cycle where a generation is non-empty.
        for key in POPULATION_KEYS:
            if key in seen_generations:
                continue
            value = cycle_record.get(key, 0)
            if isinstance(value, int) and value > 0:
                seen_generations.add(key)
                events.append({
                    "event": "generation_milestone",
                    "cycle": cycle,
                    "timestamp": timestamp,
                    "generation": key,
                    "count": value,
                })

        if previous is not None:
            # Theory population growth / shrinkage.
            theories_before = previous.get("theories", 0)
            theories_after = cycle_record.get("theories", 0)
            if isinstance(theories_before, int) and isinstance(theories_after, int):
                if theories_after > theories_before:
                    events.append({
                        "event": "theory_birth",
                        "cycle": cycle,
                        "timestamp": timestamp,
                        "delta": theories_after - theories_before,
                        "count": theories_after,
                    })
                elif theories_after < theories_before:
                    events.append({
                        "event": "theory_death",
                        "cycle": cycle,
                        "timestamp": timestamp,
                        "delta": theories_after - theories_before,
                        "count": theories_after,
                    })

            # Hypotheses: exact ids when a snapshot is available, counts else.
            snapshot = cycle_record.get("hypothesis_snapshot")
            if isinstance(snapshot, list):
                current = {
                    h.get("id"): h for h in snapshot
                    if isinstance(h, dict) and h.get("id")
                }
                current_ids = set(current)
                for hid in sorted(current_ids - previous_hypothesis_ids):
                    entry = current[hid]
                    events.append({
                        "event": "hypothesis_birth",
                        "cycle": cycle,
                        "timestamp": timestamp,
                        "id": hid,
                        "subject": entry.get("subject", ""),
                        "generation": entry.get("generation", 0),
                        "source": "snapshot_id_diff",
                    })
                for hid in sorted(previous_hypothesis_ids - current_ids):
                    events.append({
                        "event": "hypothesis_death",
                        "cycle": cycle,
                        "timestamp": timestamp,
                        "id": hid,
                        "source": "snapshot_id_diff",
                    })
                previous_hypothesis_ids = current_ids
            else:
                hypotheses_before = previous.get("hypotheses", 0)
                hypotheses_after = cycle_record.get("hypotheses", 0)
                if isinstance(hypotheses_before, int) and isinstance(hypotheses_after, int):
                    if hypotheses_after > hypotheses_before:
                        events.append({
                            "event": "hypothesis_birth",
                            "cycle": cycle,
                            "timestamp": timestamp,
                            "delta": hypotheses_after - hypotheses_before,
                            "count": hypotheses_after,
                            "source": "count_delta",
                        })
                    elif hypotheses_after < hypotheses_before:
                        events.append({
                            "event": "hypothesis_death",
                            "cycle": cycle,
                            "timestamp": timestamp,
                            "delta": hypotheses_after - hypotheses_before,
                            "count": hypotheses_after,
                            "source": "count_delta",
                        })

        previous = cycle_record

    return events


def _read_journal_keys() -> set:
    """Return the dedupe keys of the events already written to the journal."""
    keys: set = set()
    path = _journal_path()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        return keys
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            keys.add(_event_key(event))
    return keys


def append_event_journal(log_path: Optional[pathlib.Path] = None) -> int:
    """Append newly detected events to the journal and return how many were added.

    The journal is append-only and idempotent: an event that is already
    recorded (same cycle, timestamp, name and subject) is never written twice,
    so repeated runs report 0 new events.
    """
    cycles = parse_cycles(log_path)
    if not cycles:
        log.warning("No cycles parsed from the log; event journal not updated")
        return 0
    events = _detect_events(cycles)
    if not events:
        return 0

    known = _read_journal_keys()
    fresh: List[Dict[str, Any]] = []
    for event in events:
        key = _event_key(event)
        if key in known:
            continue
        known.add(key)
        fresh.append(event)
    if not fresh:
        return 0

    path = _journal_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        for event in fresh:
            f.write(json.dumps(event) + "\n")

    last = cycles[-1]
    state = {
        "events_written": len(known),
        "last_cycle": last.get("cycle", 0),
        "last_timestamp": last.get("timestamp", ""),
        "journal": path.name,
        "updated": _iso_utc(_now_utc()),
    }
    state_path = _state_path()
    with state_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, indent=2)
    return len(fresh)


# ---------------------------------------------------------------------------
# Development velocity – new items per day (recommended)
# ---------------------------------------------------------------------------
def development_velocity(
    days: int = 7, log_path: Optional[pathlib.Path] = None
) -> Dict[str, Any]:
    """Return new items per day over the trailing *days* window.

    The window is wall-clock based (the last *days* days of recorded cycles),
    not "the last *days* cycles": with a 30-second cycle the old behaviour
    covered minutes instead of days and understated the velocity by orders of
    magnitude. The per-day rate divides the net change by the number of days
    actually covered by the selected cycles (``observed_days``).
    """
    hours = max(days, 1) * 24
    cycles = parse_cycles(log_path)
    if not cycles:
        return {}
    window, meta = _select_window(cycles, hours)
    if not window:
        return {}
    start = window[0]
    end = window[-1]
    observed_days = _observed_days(window)

    def rate(key: str) -> float:
        if observed_days <= 0:
            return 0.0
        return round((end.get(key, 0) - start.get(key, 0)) / observed_days, 4)

    velocity = {
        "window_days": days,
        "window_hours": hours,
        "window_start": meta["window_start"],
        "window_end": meta["window_end"],
        "window_anchor": meta["window_anchor"],
        "cycles_in_window": len(window),
        "observed_days": round(observed_days, 4),
        "new_theories_per_day": rate("theories"),
        "new_questions_per_day": rate("questions"),
        "new_dreams_per_day": rate("dreams"),
        "new_experiments_per_day": rate("experiments"),
        "new_hypotheses_per_day": rate("hypotheses"),
    }
    return velocity


# ---------------------------------------------------------------------------
# Internal helper to write JSON snapshot files
# ---------------------------------------------------------------------------
def _write_snapshot(data: Dict[str, Any], prefix: str) -> Optional[pathlib.Path]:
    """Write *data* to ``snapshots/<prefix>/<prefix>_<date>.json``.

    Returns the written path, or ``None`` when there is nothing to write: an
    empty artefact is never created, because the daemon rewrites the log on
    restart and the observer may run while the log is empty.
    """
    if not data:
        log.warning("No data available for the %s snapshot; nothing written", prefix)
        return None
    today = _now_utc().strftime("%Y%m%d")
    out_dir = BASE_DIR / prefix
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = out_dir / f"{prefix}_{today}.json"
    with filename.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return filename


def write_daily_snapshot(
    hours: int = DAILY_WINDOW_HOURS, log_path: Optional[pathlib.Path] = None
) -> Optional[pathlib.Path]:
    """Write the daily snapshot; returns the path, or ``None`` when there is no data."""
    return _write_snapshot(daily_snapshot(hours, log_path), "daily")


def write_weekly_snapshot(
    hours: int = WEEKLY_WINDOW_HOURS, log_path: Optional[pathlib.Path] = None
) -> Optional[pathlib.Path]:
    """Write the weekly aggregate; returns the path, or ``None`` when there is no data."""
    return _write_snapshot(weekly_aggregate(hours, log_path), "weekly")


def write_monthly_genome(log_path: Optional[pathlib.Path] = None) -> Optional[pathlib.Path]:
    """Write the monthly genome; returns the path, or ``None`` when there is no data."""
    return _write_snapshot(monthly_genome(log_path), "monthly")


def write_velocity_snapshot(
    days: int = 7, log_path: Optional[pathlib.Path] = None
) -> Optional[pathlib.Path]:
    """Write the velocity snapshot; returns the path, or ``None`` when there is no data."""
    return _write_snapshot(development_velocity(days, log_path), "velocity")


if __name__ == "__main__":
    print("Daily snapshot written to", write_daily_snapshot())
    print("Weekly snapshot written to", write_weekly_snapshot())
    print("Monthly genome written to", write_monthly_genome())
    print("Velocity snapshot written to", write_velocity_snapshot())
    print("Appended", append_event_journal(), "new events to journal")
