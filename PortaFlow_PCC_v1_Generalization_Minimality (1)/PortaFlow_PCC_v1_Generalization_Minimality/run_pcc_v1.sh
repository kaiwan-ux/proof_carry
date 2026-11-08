#!/usr/bin/env bash
set -euo pipefail
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
cd "$(dirname "$0")"
python3 scripts/clean_results.py
[ -d .venv ] || python3 -m venv .venv
PY=.venv/bin/python
$PY -m pip install --upgrade pip
$PY -m pip install -r requirements.txt
$PY -m pip install -e .
$PY scripts/preflight.py
$PY -m pytest -q
$PY scripts/capture_environment.py
$PY scripts/run_probes.py
$PY scripts/run_generalization.py
$PY scripts/analyze_results.py
$PY scripts/verify_results.py
$PY scripts/make_manifest.py
$PY scripts/export_results_zip.py
echo "DONE. Upload PortaFlow_PCC_v1_results.zip for analysis."
