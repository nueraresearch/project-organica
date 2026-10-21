"""metrics_observer.py
Utility module that builds on `metrics.py` to produce the observation artifacts required for the 90‑day longitudinal study.
This code **does not modify** the Organica core daemon; it lives entirely in the `observation/` package.
"""

import pathlib
import json
import datetime
from typing import Dict, Any, List

# Import core metric helpers (pure functions, safe to reuse)
from metrics import (
    parse_cycles,
    aggregate_metrics,
    event_type_counts,
    dream_type_distribution,
    hypothesis_lifecycle,
)

# Base directory for all generated study artefacts
BASE_DIR = pathlib.Path(__file__).parent.parent / "snapshots"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Helper to compute active counts for the *latest* cycle
# ---------------------------------------------------------------------------
def _latest_cycle_info() -> Dict[str, Any]:
    cycles = parse_cycles()
    if not cycles:
        raise RuntimeError("No cycles parsed from organica.log")
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
    return {"cycle": latest["cycle"], "timestamp": latest["timestamp"], **active}

# ---------------------------------------------------------------------------
# Daily snapshot (essential)
# ---------------------------------------------------------------------------
def daily_snapshot() -> Dict[str, Any]:
    latest = _latest_cycle_info()
    cycles = parse_cycles()
    births_today = 0
    deaths_today = 0
    if len(cycles) >= 2:
        today_cycle = cycles[-1]
        yesterday_cycle = cycles[-2]
        for key in ["concepts", "predictions", "loops", "hypotheses", "theories", "questions", "dreams", "investigations", "experiments"]:
            today = today_cycle.get(key, 0)
            yest = yesterday_cycle.get(key, 0)
            if today > yest:
                births_today += today - yest
            elif today < yest:
                deaths_today += yest - today
    else:
        births_today = sum(latest.get(k, 0) for k in latest if k.startswith("active_"))
        deaths_today = 0
    snapshot = {
        **latest,
        "births_today": births_today,
        "deaths_today": deaths_today,
        "top_theories": [],  # placeholders – can be filled later from domain‑specific ranking
        "top_questions": [],
    }
    return snapshot

# ---------------------------------------------------------------------------
# Weekly aggregate (strongly recommended)
# ---------------------------------------------------------------------------
def weekly_aggregate() -> Dict[str, Any]:
    cycles = parse_cycles()[-7:]
    if not cycles:
        return {}
    agg = aggregate_metrics(cycles)
    weekly = {
        "window_cycles": len(cycles),
        "aggregated": agg,
        "largest_births": max(c.get("concepts", 0) for c in cycles),
        "largest_deaths": max(c.get("deaths", 0) for c in cycles),
        "top_theories": [],
        "top_questions": [],
    }
    return weekly

# ---------------------------------------------------------------------------
# Monthly genome (valuable)
# ---------------------------------------------------------------------------
def monthly_genome() -> Dict[str, Any]:
    latest = _latest_cycle_info()
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
        "hypothesis_lifecycle": hypothesis_lifecycle(),
        "event_counts": event_type_counts(),
        "dream_distribution": dream_type_distribution(),
    }
    return genome

# ---------------------------------------------------------------------------
# Event journal – records major structural changes detected in the log
# ---------------------------------------------------------------------------
EVENT_JOURNAL = BASE_DIR / "event_journal.log"

def _detect_events() -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    log_path = pathlib.Path(__file__).parent.parent / "organica.log"
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if "theory_birth" in line:
            parts = line.split("|")
            cycle = int([p for p in parts if "Cycle" in p][0].split()[1])
            theory = line.split("theory_birth=")[1].split()[0]
            events.append({"event": "theory_birth", "cycle": cycle, "theory": theory})
        if "theory_death" in line:
            parts = line.split("|")
            cycle = int([p for p in parts if "Cycle" in p][0].split()[1])
            theory = line.split("theory_death=")[1].split()[0]
            events.append({"event": "theory_death", "cycle": cycle, "theory": theory})
        if "cognitive_revolution" in line:
            parts = line.split("|")
            cycle = int([p for p in parts if "Cycle" in p][0].split()[1])
            old = line.split("old=")[1].split()[0]
            new = line.split("new=")[1].split()[0]
            events.append({"event": "cognitive_revolution", "cycle": cycle, "old_dominant": old, "new_dominant": new})
    return events

def append_event_journal() -> int:
    events = _detect_events()
    if not events:
        return 0
    with EVENT_JOURNAL.open("a", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    return len(events)

# ---------------------------------------------------------------------------
# Development velocity – new items per day (recommended)
# ---------------------------------------------------------------------------
def development_velocity(days: int = 7) -> Dict[str, float]:
    cycles = parse_cycles()[-days:]
    if not cycles:
        return {}
    start = cycles[0]
    end = cycles[-1]
    def diff(key: str) -> int:
        return end.get(key, 0) - start.get(key, 0)
    velocity = {
        "new_theories_per_day": diff("theories") / days if "theories" in end else 0,
        "new_questions_per_day": diff("questions") / days if "questions" in end else 0,
        "new_dreams_per_day": diff("dreams") / days if "dreams" in end else 0,
        "new_experiments_per_day": diff("experiments") / days if "experiments" in end else 0,
    }
    return velocity

# ---------------------------------------------------------------------------
# Internal helper to write JSON snapshot files
# ---------------------------------------------------------------------------
def _write_snapshot(data: Dict[str, Any], prefix: str) -> pathlib.Path:
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    out_dir = BASE_DIR / prefix
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = out_dir / f"{prefix}_{today}.json"
    with filename.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return filename

def write_daily_snapshot() -> pathlib.Path:
    return _write_snapshot(daily_snapshot(), "daily")

def write_weekly_snapshot() -> pathlib.Path:
    return _write_snapshot(weekly_aggregate(), "weekly")

def write_monthly_genome() -> pathlib.Path:
    return _write_snapshot(monthly_genome(), "monthly")

def write_velocity_snapshot() -> pathlib.Path:
    return _write_snapshot(development_velocity(days=7), "velocity")

if __name__ == "__main__":
    print("Daily snapshot written to", write_daily_snapshot())
    print("Weekly snapshot written to", write_weekly_snapshot())
    print("Monthly genome written to", write_monthly_genome())
    print("Velocity snapshot written to", write_velocity_snapshot())
    print("Appended", append_event_journal(), "new events to journal")
