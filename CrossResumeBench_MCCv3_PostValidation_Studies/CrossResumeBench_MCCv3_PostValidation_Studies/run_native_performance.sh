#!/usr/bin/env bash
set -euo pipefail
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 CREWAI_TRACING_ENABLED=false CREWAI_DISABLE_TELEMETRY=true CREWAI_DISABLE_TRACKING=true OTEL_SDK_DISABLED=true
python -m studies.performance.run_native_latency --repeats 3
python scripts/export_results.py
