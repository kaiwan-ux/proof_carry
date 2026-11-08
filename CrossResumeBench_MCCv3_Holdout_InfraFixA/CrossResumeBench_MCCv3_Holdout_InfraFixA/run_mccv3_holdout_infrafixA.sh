#!/usr/bin/env bash
set -euo pipefail
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1
export CREWAI_TRACING_ENABLED=false CREWAI_DISABLE_TELEMETRY=true CREWAI_DISABLE_TRACKING=true OTEL_SDK_DISABLED=true
python scripts/verify_freeze.py
python scripts/validate_infrafixA.py
python scripts/preflight.py
python -m pytest -q
rm -rf native_gate_results results
set +e
python scripts/native_gate_infrafixA.py
gate=$?
set -e
if [ "$gate" -ne 0 ]; then
  python scripts/export_native_gate_diagnostics_infrafixA.py
  echo "Native gate did not pass. Upload CrossResumeBench_MCCv3_Holdout_InfraFixA_NATIVE_GATE_diagnostics.zip"
  exit "$gate"
fi
python scripts/run_holdout_infrafixA.py
python scripts/verify_results_infrafixA.py
python scripts/analyze_results.py
python scripts/export_results_infrafixA.py
echo "Complete. Upload CrossResumeBench_MCCv3_Holdout_InfraFixA_results.zip"
