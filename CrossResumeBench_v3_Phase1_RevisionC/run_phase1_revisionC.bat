@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0run_phase1_revisionC.ps1"
exit /b %ERRORLEVEL%
