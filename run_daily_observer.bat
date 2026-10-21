@echo off
rem Run daily snapshot and append new events to the journal
set PYTHONPATH=%~dp0
python -c "import observation.metrics_observer as mo; mo.write_daily_snapshot(); mo.append_event_journal()"
