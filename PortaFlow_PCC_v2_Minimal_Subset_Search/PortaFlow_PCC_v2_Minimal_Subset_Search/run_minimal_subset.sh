#!/usr/bin/env bash
set -euo pipefail
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
cd "$(dirname "$0")"
python scripts/clean_results.py
[ -d .venv ] || python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
python scripts/preflight.py
pytest -q
python scripts/capture_environment.py
python scripts/run_probes.py
python scripts/run_subset_search.py
python scripts/run_native_confirmation.py
python scripts/analyze_results.py
python scripts/verify_results.py
python scripts/make_manifest.py
python scripts/export_results_zip.py
echo "DONE. Upload PortaFlow_PCC_v2_minimal_subset_results.zip"
