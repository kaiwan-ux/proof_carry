#!/usr/bin/env bash
set -euo pipefail
python scripts/clean_results.py
python -m pytest -q
python scripts/run_native_holdout.py
python scripts/analyze_results.py
python scripts/verify_results.py
python scripts/make_manifest.py
python scripts/export_results_zip.py
