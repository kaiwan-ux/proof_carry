#!/usr/bin/env bash
set -euo pipefail
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
cd "$(dirname "$0")"
python scripts/clean_results.py
python -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
python scripts/preflight.py
pytest -q
python scripts/capture_environment.py
python scripts/run_probes.py
python scripts/run_native_robustness.py
python scripts/analyze_results.py
python scripts/verify_results.py
python scripts/make_manifest.py
python scripts/export_results_zip.py
