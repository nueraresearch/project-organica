@echo off
rem ===================================================================
rem  Organica -- continuous daemon launcher
rem
rem  The daemon writes its own log (organica.log) through a logging
rem  FileHandler opened in APPEND mode. Two things used to go wrong
rem  during the first attempt at the 90-day study:
rem
rem    1. Redirecting stdout into organica.log with ">" TRUNCATED the
rem       file on every restart, destroying the longitudinal record.
rem    2. Sending stdout into the same file the FileHandler owns would
rem       write every log line twice.
rem
rem  So organica.log is appended to and never truncated, and the
rem  console mirror goes to console.log instead.
rem ===================================================================
set PYTHON=C:\Users\monte\.local\bin\python.exe
if not exist "%PYTHON%" set PYTHON=python

start "Organica" /b "%PYTHON%" "%~dp0run_continuous.py" >> "%~dp0console.log" 2>&1
echo Organica continuous run started.
echo   organica.log : appended to, never truncated
echo   console.log  : stdout/stderr mirror
