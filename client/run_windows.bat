@echo off
cd /d "%~dp0"

if not exist ".venv" (
    echo Setting up for the first time, this takes a minute...
    python -m venv .venv
    ".venv\Scripts\pip" install -r requirements.txt
)

".venv\Scripts\python" -m mis_pulse_client.main

pause
