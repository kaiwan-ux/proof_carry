#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export CREWAI_TRACING_ENABLED=false
export CREWAI_DISABLE_TELEMETRY=true
export CREWAI_DISABLE_TRACKING=true
export OTEL_SDK_DISABLED=true
python scripts/verify_frozen_v2.py
python scripts/preflight.py
python -m pytest -q
if ! python scripts/probe_maf_revisionC.py; then
  echo "MAF Revision C probe FAILED. The 72-row migration grid will NOT run."
  python scripts/export_maf_probe_diagnostics.py
  echo "Upload CrossResumeBench_v3_Phase1_RevisionC_MAF_probe_diagnostics.zip"
  exit 2
fi
python scripts/run_phase1_revisionC.py
python scripts/analyze_phase1_revisionC.py
python scripts/verify_integrity.py
python scripts/export_phase1_revisionC.py
