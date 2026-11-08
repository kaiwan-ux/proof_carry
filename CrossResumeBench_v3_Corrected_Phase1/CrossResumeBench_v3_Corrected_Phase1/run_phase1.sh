#!/usr/bin/env bash
set -euo pipefail
python scripts/verify_frozen_v2.py
python scripts/preflight.py
python scripts/run_phase1.py
python scripts/analyze_phase1.py
python scripts/verify_phase1.py
python scripts/export_phase1.py
