#!/usr/bin/env bash
set -euo pipefail
export CREWAI_TRACING_ENABLED=false
export CREWAI_DISABLE_TELEMETRY=true
export CREWAI_DISABLE_TRACKING=true
export OTEL_SDK_DISABLED=true
python scripts/verify_frozen_v2.py
python scripts/preflight.py
python -m pytest -q
python scripts/run_phase1_revisionB.py
python scripts/analyze_phase1_revisionB.py
python scripts/verify_integrity.py
python scripts/export_phase1_revisionB.py
