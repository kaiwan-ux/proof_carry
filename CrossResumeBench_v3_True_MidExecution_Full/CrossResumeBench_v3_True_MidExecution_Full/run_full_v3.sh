#!/usr/bin/env bash
set -euo pipefail
export CREWAI_TRACING_ENABLED=false CREWAI_DISABLE_TELEMETRY=true CREWAI_DISABLE_TRACKING=true OTEL_SDK_DISABLED=true
python scripts/preflight.py
python scripts/verify_frozen_v2.py
python scripts/generate_suite.py
python scripts/verify_experiment_freeze.py
python -m pytest -q
find results -type f ! -name .gitkeep -delete
if ! python scripts/run_native_family_gate.py; then python scripts/export_native_gate_diagnostics.py; exit 4; fi
python scripts/run_full_v3.py
python scripts/analyze_results.py
python scripts/verify_results.py
python scripts/make_manifest.py
python scripts/export_results.py
