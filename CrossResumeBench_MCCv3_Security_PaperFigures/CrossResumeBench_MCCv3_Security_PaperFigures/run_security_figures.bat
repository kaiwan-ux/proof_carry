@echo off
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
python scripts\run_all.py
if errorlevel 1 exit /b %errorlevel%
