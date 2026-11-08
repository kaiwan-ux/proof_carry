#!/usr/bin/env bash
set -euo pipefail
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 MPLBACKEND=Agg
python scripts/verify_inputs.py
python scripts/run_postvalidation.py --bootstrap-reps 10000 --micro-repeats 10
python scripts/verify_postvalidation.py
python scripts/export_results.py
