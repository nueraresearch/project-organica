"""Organica Health Dashboard UI."""

import datetime
import json
import pathlib
import subprocess
from typing import Any


class _NullWidget:
    """Falsy placeholder returned by the Streamlit stand-in.

    It is falsy so ``if st.button(...)`` blocks never run without the real
    Streamlit runtime, and it doubles as a context manager so
    ``with st.columns(2)[0]:`` keeps working.
    """

    def __bool__(self) -> bool:
        return False

    def __enter__(self) -> "_NullWidget":
        return self

    def __exit__(self, *exc_info: Any) -> bool:
        return False


class _NullStreamlit:
    """Minimal stand-in for Streamlit so this module stays importable headless."""

    def __init__(self) -> None:
        self.sidebar = self

    def __getattr__(self, name: str) -> Any:
        if name == "columns":
            def _columns(count: int = 1):
                return tuple(_NullWidget() for _ in range(count))
            return _columns
        if name == "time_input":
            def _time_input(label, value=None, **kwargs):
                return value
            return _time_input
        if name == "number_input":
            def _number_input(label, value=0, **kwargs):
                return value
            return _number_input
        if name == "selectbox":
            def _selectbox(label, options=(), **kwargs):
                return options[0] if options else ""
            return _selectbox
        if name in ("text_input", "text_area"):
            def _text(label, value="", **kwargs):
                return value
            return _text

        def _noop(*args, **kwargs):
            return _NullWidget()
        return _noop


try:  # Streamlit is only needed to actually render the dashboard.
    import requests
except ImportError:  # pragma: no cover - optional dependency
    requests = None

try:
    import streamlit as st
except ImportError:  # pragma: no cover - optional dependency
    st = _NullStreamlit()

# Local utilities
from metrics import (
    aggregate_metrics,
    dream_counts_over_time,
    dream_type_distribution,
    event_type_counts,
    hypothesis_lifecycle,
    parse_cycles,
    snapshot_to_json,
)

st.set_page_config(page_title="Organica Health Dashboard & Inception", layout="wide")
st.title(":microscope: Organica Health Dashboard")

# ---------------------------------------------------------------------
# Sidebar – Inception Control
# ---------------------------------------------------------------------
st.sidebar.header(":bulb: Inception Control")

seed_options = {
    "Auth Failure": {"event": "auth", "outcome": "failure"},
    "Contradictory Belief": {"event": "hypothesis", "action": "contradict"},
    "Dream Trigger – Completion": {"event": "dream", "type": "completion"},
}
selected_seed = st.sidebar.selectbox("Select a seed to inject", list(seed_options.keys()))
custom_json = st.sidebar.text_area("Or paste custom JSON payload", height=150)
endpoint = st.sidebar.text_input(
    "Inception endpoint (POST)",
    value="http://localhost:8000/inception",
    help="URL of the Inception module that accepts a JSON payload",
)

if st.sidebar.button("Send to Inception"):
    if requests is None:
        st.sidebar.error("The 'requests' package is not installed.")
        st.stop()
    payload = seed_options[selected_seed].copy()
    if custom_json.strip():
        try:
            extra = json.loads(custom_json)
            payload.update(extra)
        except json.JSONDecodeError as e:
            st.sidebar.error(f"Invalid JSON: {e}")
            st.stop()
    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        if response.ok:
            st.sidebar.success(f"Inception succeeded: {response.text}")
        else:
            st.sidebar.error(f"Inception error {response.status_code}: {response.text}")
    except Exception as exc:
        st.sidebar.error(f"Failed to contact endpoint: {exc}")

# ------------------------------------------------------------
# Sidebar – Manual Run Buttons
# ------------------------------------------------------------
st.sidebar.header(":runner: Manual Observation Runs")

if st.sidebar.button("Run Daily Snapshot Now"):
    subprocess.run(
        str(pathlib.Path(__file__).parent / "run_daily_observer.bat"), shell=True
    )
    st.sidebar.success("Daily snapshot executed.")

if st.sidebar.button("Run Weekly/Monthly Aggregates Now"):
    subprocess.run(
        str(pathlib.Path(__file__).parent / "run_weekly_monthly.bat"), shell=True
    )
    st.sidebar.success("Weekly and monthly aggregates executed.")

# ------------------------------------------------------------
# Sidebar – Scheduler Setup (Denver Time)
# ------------------------------------------------------------
st.sidebar.header(":alarm_clock: Scheduler Setup (Denver Time)")


def format_time(t: datetime.time) -> str:
    return t.strftime("%H:%M")


daily_time = st.sidebar.time_input("Daily snapshot time", value=datetime.time(2, 0))
weekly_day = st.sidebar.selectbox(
    "Weekly snapshot day",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    index=0,
)
weekly_time = st.sidebar.time_input("Weekly snapshot time", value=datetime.time(3, 0))
monthly_day = st.sidebar.number_input("Monthly snapshot day (1-28)", min_value=1, max_value=28, value=1)
monthly_time = st.sidebar.time_input("Monthly genome time", value=datetime.time(4, 0))

if st.sidebar.button("Create/Update Scheduler Tasks"):
    base = pathlib.Path(__file__).parent
    daily_cmd = (
        f'schtasks /Create /F /TN Organica_Daily_Observer '
        f'/TR "{base / "run_daily_observer.bat"}" '
        f'/SC DAILY /ST {format_time(daily_time)} /RL HIGHEST'
    )
    weekly_cmd = (
        f'schtasks /Create /F /TN Organica_Weekly_Aggregates '
        f'/TR "{base / "run_weekly_monthly.bat"}" '
        f'/SC WEEKLY /D {weekly_day[:3].upper()} /ST {format_time(weekly_time)} /RL HIGHEST'
    )
    monthly_cmd = (
        f'schtasks /Create /F /TN Organica_Monthly_Genome '
        f'/TR "{base / "run_weekly_monthly.bat"}" '
        f'/SC MONTHLY /D {int(monthly_day)} /ST {format_time(monthly_time)} /RL HIGHEST'
    )
    try:
        for cmd in [daily_cmd, weekly_cmd, monthly_cmd]:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        st.sidebar.success("Scheduler tasks created/updated successfully.")
    except subprocess.CalledProcessError as e:
        st.sidebar.error(f"Failed to create tasks (may need admin): {e.stderr.decode().strip()}")

# ---------------------------------------------------------------------
# Main view – Metrics
# ---------------------------------------------------------------------
col1, col2 = st.columns(2)

try:
    agg = aggregate_metrics(parse_cycles())
except Exception as e:
    agg = {}
    st.error(f"Error: {e}")

with col1:
    st.subheader("Current Organism State")
    try:
        latest = agg.pop("latest_snapshot", {})
        if latest:
            st.metric("Cycle", latest.get("cycle", "—"))
            st.metric("Concepts", latest.get("concepts", 0))
            st.metric("Hypotheses", latest.get("hypotheses", 0))
            st.metric("Theories", latest.get("theories", 0))
            st.metric("Dreams", latest.get("dreams", 0))
            st.metric("Questions", latest.get("questions", 0))
            st.metric("Experiments", latest.get("experiments", 0))
            st.metric("Total Composites", f"{latest.get('total_composites', 0):,}")
            st.caption(f"As of {latest.get('timestamp', '')}")
        else:
            st.info("No cycle data yet.")
    except Exception as e:
        st.error(f"Error: {e}")

with col2:
    st.subheader("Run Statistics")
    try:
        st.metric("Total Cycles Run", agg.get("total_cycles", 0))
        st.metric("Successful", agg.get("successful_cycles", 0))
        st.metric("Failed", agg.get("failed_cycles", 0))
        st.metric("Success Rate", f"{agg.get('success_rate_pct', 0)}%")
        st.metric("Avg Duration", f"{agg.get('avg_duration_ms', 0)} ms")
        st.metric("Avg Composites/Cycle", agg.get("avg_composites_per_cycle", 0))
        st.metric("Candidates Strengthened", f"{agg.get('candidates_strengthened', 0):,}")
        st.metric("Candidates Pruned", f"{agg.get('candidates_pruned', 0):,}")
    except Exception as e:
        st.error(f"Error: {e}")

st.subheader("Dream Type Distribution")
try:
    dist = dream_type_distribution()
    if dist:
        st.bar_chart(dist)
    else:
        st.info("No dream data yet.")
except Exception as e:
    st.warning(f"Dream distribution unavailable: {e}")

st.subheader("Hypothesis Lifecycle (sample)")
try:
    life = hypothesis_lifecycle()
    sample = dict(list(life.items())[:10])
    st.json(sample)
except Exception as e:
    st.warning(f"Lifecycle data unavailable: {e}")

if st.button("Create JSON Snapshot"):
    snapshot_path = (
        pathlib.Path(__file__).parent
        / "snapshots"
        / f"snapshot_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        snapshot_to_json(snapshot_path)
        st.success(f"Snapshot saved to {snapshot_path}")
    except Exception as e:
        st.error(f"Snapshot failed: {e}")
