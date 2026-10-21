@echo off
rem Start the Inception API server in a new window
start "" cmd /c "python \"%~dp0inception_api.py\""

rem Wait a moment for API to start (optional)
timeout /t 2 > nul

rem Start the Streamlit dashboard UI
cd /d "%~dp0"
python -m streamlit run dashboard_ui.py

