@echo off
set CREWAI_TRACING_ENABLED=false
set CREWAI_DISABLE_TELEMETRY=true
set CREWAI_DISABLE_TRACKING=true
set OTEL_SDK_DISABLED=true
powershell -ExecutionPolicy Bypass -File "%~dp0run_phase1_revisionA.ps1"
pause
