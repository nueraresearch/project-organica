@echo off
rem Start Organica continuous run as a background process
rem Adjust the path to your Python interpreter if needed
set PYTHON=c:\\Users\\monte\\.local\\bin\\python.exe
if not exist "%PYTHON%" set PYTHON=python
start "Organica" /b "%PYTHON%" "%~dp0run_continuous.py" > "%~dp0organica.log" 2>&1
echo Organica continuous run started. Logs are written to organica.log
