#!/usr/bin/env bash
set -euo pipefail
export CREWAI_TRACING_ENABLED=false CREWAI_DISABLE_TELEMETRY=true CREWAI_DISABLE_TRACKING=true OTEL_SDK_DISABLED=true
python scripts/verify_freeze.py
python scripts/preflight.py
python -m pytest -q
python scripts/run_holdout.py
test -f results/migration_runs.csv
python scripts/verify_results.py
python scripts/analyze_results.py
python scripts/export_results.py
