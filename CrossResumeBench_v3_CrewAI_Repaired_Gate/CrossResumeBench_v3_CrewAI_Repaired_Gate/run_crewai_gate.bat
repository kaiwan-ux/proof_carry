
@echo off
set PYTHONUTF8=1
set CREWAI_TRACING_ENABLED=false
set CREWAI_DISABLE_TELEMETRY=true
set CREWAI_DISABLE_TRACKING=true
set OTEL_SDK_DISABLED=true
python scripts\verify_frozen_v2.py || exit /b 1
python scripts\preflight.py || exit /b 1
python -m pytest -q || exit /b 1
python scripts\run_crewai_gate.py || exit /b 1
python scripts\verify_results.py || exit /b 1
echo DONE. Upload CrossResumeBench_v3_CrewAI_Repaired_Gate_results.zip
