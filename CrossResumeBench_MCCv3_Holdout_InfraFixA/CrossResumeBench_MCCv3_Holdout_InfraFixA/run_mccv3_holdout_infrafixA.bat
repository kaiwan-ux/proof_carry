@echo off
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
set CREWAI_TRACING_ENABLED=false
set CREWAI_DISABLE_TELEMETRY=true
set CREWAI_DISABLE_TRACKING=true
set OTEL_SDK_DISABLED=true
chcp 65001 >nul
python scripts\verify_freeze.py || exit /b 1
python scripts\validate_infrafixA.py || exit /b 1
python scripts\preflight.py || exit /b 1
python -m pytest -q || exit /b 1
if exist native_gate_results rmdir /s /q native_gate_results
if exist results rmdir /s /q results
python scripts\native_gate_infrafixA.py
if errorlevel 1 (
  python scripts\export_native_gate_diagnostics_infrafixA.py
  echo Native gate did not pass. Upload CrossResumeBench_MCCv3_Holdout_InfraFixA_NATIVE_GATE_diagnostics.zip
  exit /b 2
)
python scripts\run_holdout_infrafixA.py || exit /b 1
python scripts\verify_results_infrafixA.py || exit /b 1
python scripts\analyze_results.py
python scripts\export_results_infrafixA.py
echo Complete. Upload CrossResumeBench_MCCv3_Holdout_InfraFixA_results.zip
