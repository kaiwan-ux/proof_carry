#!/usr/bin/env bash
set -euo pipefail
PYTHON=${PYTHON:-python3.12}
if [ ! -d .venv ]; then "$PYTHON" -m venv .venv; fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/native_doctor.py --out results/native_preflight
python scripts/run_native_full.py --cases smoke8 --profile proofcarry --variants enough
SMOKE=$(cat results/LATEST_NATIVE_RUN.txt)
python scripts/analyze_native_full.py "$SMOKE"
python scripts/verify_native_full.py "$SMOKE"
python scripts/run_native_full.py --cases all120 --profile proofcarry --variants all
RUN=$(cat results/LATEST_NATIVE_RUN.txt)
python scripts/analyze_native_full.py "$RUN"
python scripts/verify_native_full.py "$RUN"
echo "Native run complete: $RUN"
