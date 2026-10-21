@echo off
rem Run weekly aggregates and monthly genome snapshots
set PYTHONPATH=%~dp0
python -c "import observation.metrics_observer as mo; mo.write_weekly_snapshot(); mo.write_monthly_genome(); mo.write_velocity_snapshot()"
