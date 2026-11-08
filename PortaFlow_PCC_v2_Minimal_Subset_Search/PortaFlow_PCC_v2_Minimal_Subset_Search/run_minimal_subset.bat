@echo off
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_minimal_subset.ps1"
pause
