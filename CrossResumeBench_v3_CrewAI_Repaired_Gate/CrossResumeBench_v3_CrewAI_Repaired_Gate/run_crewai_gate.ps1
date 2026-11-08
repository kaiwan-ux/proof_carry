
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:CREWAI_TRACING_ENABLED = "false"
$env:CREWAI_DISABLE_TELEMETRY = "true"
$env:CREWAI_DISABLE_TRACKING = "true"
$env:OTEL_SDK_DISABLED = "true"

python scripts/verify_frozen_v2.py
python scripts/preflight.py
python -m pytest -q
python scripts/run_crewai_gate.py
python scripts/verify_results.py
Write-Host "DONE. Upload CrossResumeBench_v3_CrewAI_Repaired_Gate_results.zip"
