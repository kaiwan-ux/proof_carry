#!/usr/bin/env bash
set -euo pipefail
export CREWAI_TRACING_ENABLED=false CREWAI_DISABLE_TELEMETRY=true CREWAI_DISABLE_TRACKING=true OTEL_SDK_DISABLED=true
python scripts/verify_frozen_v2.py
python scripts/preflight.py
python scripts/run_phase1_revisionA.py
python scripts/analyze_phase1_revisionA.py
python scripts/verify_integrity.py
python scripts/export_phase1_revisionA.py
python - <<'PY2'
import json
v=json.load(open('results/PHASE1_REVISIONA_GATE.json'))
print('PHASE 1 REVISION A GATE:', 'PASS' if v['go_for_full_v3'] else 'FAIL — upload results for analysis; do not start full v3')
PY2
