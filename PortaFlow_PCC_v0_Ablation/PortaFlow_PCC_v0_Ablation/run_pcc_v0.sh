#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python scripts/clean_results.py
python scripts/preflight.py
python -m pytest -q
python scripts/run_probes.py
python scripts/run_pcc_ablation.py
python scripts/analyze_pcc.py
python scripts/capture_environment.py
python scripts/verify_results.py
python scripts/make_manifest.py
python scripts/export_results_zip.py
echo "SUCCESS. Upload PortaFlow_PCC_v0_results.zip back to ChatGPT."
