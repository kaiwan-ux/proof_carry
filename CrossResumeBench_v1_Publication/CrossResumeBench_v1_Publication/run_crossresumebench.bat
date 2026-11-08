@echo off
set PYTHONPATH=%~dp0src
powershell -ExecutionPolicy Bypass -File "%~dp0run_crossresumebench.ps1"
pause
