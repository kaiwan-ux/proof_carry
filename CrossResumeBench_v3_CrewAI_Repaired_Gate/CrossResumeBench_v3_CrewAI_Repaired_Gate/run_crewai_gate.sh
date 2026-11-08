#!/usr/bin/env bash
set -euo pipefail
export PYTHONUTF8=1
export CREWAI_TRACING_ENABLED=false
export CREWAI_DISABLE_TELEMETRY=true
export CREWAI_DISABLE_TRACKING=true
export OTEL_SDK_DISABLED=true
python scripts/verify_frozen_v2.py
python scripts/preflight.py
python -m pytest -q
python scripts/run_crewai_gate.py
python scripts/verify_results.py
echo "DONE. Upload CrossResumeBench_v3_CrewAI_Repaired_Gate_results.zip"
