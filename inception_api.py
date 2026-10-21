"""
inception_api.py
------------------------------------------------------------------
A minimal HTTP interface to a running Organica instance.

Two jobs:

  1. **Read** the current health metrics as JSON.
  2. **Inject** an experience event into the live substrate, so a running
     daemon picks it up on its next sleep cycle. This is the "Inception"
     idea: perturb a live organism without stopping it.

SQLite allows multiple connections, so the API can write to `memory.db`
while the daemon holds it open. The daemon sees the new event on its next
cycle.

Requires Flask:  pip install -r requirements.txt   (or: pip install flask)

Run it:
    python inception_api.py                 # serves on 127.0.0.1:8000
    python inception_api.py --port 8080
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sys
import threading

from flask import Flask, jsonify, request

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from metrics import snapshot_to_json  # noqa: E402
from organica.paths import LIVE_DB, REPO_ROOT, SCRATCH_DIR  # noqa: E402

app = Flask(__name__)

SNAPSHOT_DIR = REPO_ROOT / "snapshots"


@app.route("/", methods=["GET"])
def index():
    """Describe the available endpoints."""
    return jsonify({
        "service": "Organica Inception API",
        "endpoints": {
            "GET  /health": "liveness and substrate status",
            "GET  /metrics": "full health metrics as JSON",
            "POST /metrics/snapshot": "write a metrics snapshot to snapshots/",
            "POST /inception": "inject an experience event into the live substrate",
        },
        "inception_payload": {
            "content": "the raw text of the event (required)",
            "event_type": "default 'event'",
            "source": "default 'inception'",
        },
    })


@app.route("/health", methods=["GET"])
def health():
    """Liveness plus a quick look at the substrate."""
    status = {"ok": True, "live_db": str(LIVE_DB)}
    try:
        if LIVE_DB.exists():
            import sqlite3
            conn = sqlite3.connect(f"file:{LIVE_DB}?mode=ro", uri=True)
            status["events"] = conn.execute(
                "SELECT COUNT(*) FROM events").fetchone()[0]
            row = conn.execute("SELECT MAX(cycle) FROM sleep_cycles").fetchone()
            status["sleep_cycle"] = row[0] if row else 0
            conn.close()
        else:
            status["events"] = 0
            status["sleep_cycle"] = 0
            status["note"] = "no live database yet -- start run_continuous.py"
    except Exception as exc:  # pragma: no cover - defensive
        status["ok"] = False
        status["error"] = str(exc)
    return jsonify(status)


@app.route("/metrics", methods=["GET"])
def get_metrics():
    """Return the current health metrics."""
    return jsonify(snapshot_to_json())


@app.route("/metrics/snapshot", methods=["POST"])
def create_snapshot():
    """Write a metrics snapshot to `snapshots/` and return its path."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = SNAPSHOT_DIR / f"snapshot_{timestamp}.json"
    data = snapshot_to_json(path)
    return jsonify({
        "snapshot_path": str(path),
        "status": "created",
        "cycles": data.get("aggregated", {}).get("total_cycles", 0),
    })


@app.route("/inception", methods=["POST"])
def inception():
    """Inject an experience event into the live substrate.

    The running daemon picks it up on its next sleep cycle, so you can
    perturb a live organism without stopping it.
    """
    payload = request.get_json(silent=True) or {}
    content = payload.get("content")
    if not content or not str(content).strip():
        return jsonify({
            "status": "error",
            "error": "payload must include a non-empty 'content' field",
            "example": {"content": "auth failure on login attempt"},
        }), 400

    event_type = payload.get("event_type", "event")
    source = payload.get("source", "inception")

    try:
        from organica.memory import MemoryService
        mem = MemoryService(LIVE_DB)
        event = mem.store(str(content), event_type=event_type, source=source)
        mem.close()
    except Exception as exc:
        return jsonify({"status": "error", "error": str(exc)}), 500

    return jsonify({
        "status": "injected",
        "event_id": event.id,
        "content": event.content,
        "event_type": event.event_type,
        "source": event.source,
        "tags": event.tags,
        "note": "the daemon will incorporate this on its next sleep cycle",
    })


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Serve the API (blocking)."""
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organica Inception API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    print(f"Inception API listening on http://{args.host}:{args.port}")
    print(f"  live substrate : {LIVE_DB}")
    print(f"  snapshots      : {SCRATCH_DIR.parent / 'snapshots'}")
    run_server(args.host, args.port)
