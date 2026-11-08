$ErrorActionPreference = "Stop"
$env:PYTHONUTF8="1"
$env:PYTHONIOENCODING="utf-8"

Write-Host "=== PortaFlow Corrected Native Phase-0 ===" -ForegroundColor Cyan
if (-not (Test-Path ".venv")) { py -3.12 -m venv .venv }
$python = Join-Path $PWD ".venv\Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt

& $python scripts\clean_results.py
& $python scripts\preflight.py
& $python -m pytest -q
& $python scripts\run_probes.py
& $python scripts\run_native_cross_runtime.py
& $python scripts\analyze_native.py
& $python scripts\make_manifest.py
& $python scripts\export_results_zip.py
& $python scripts\verify_results.py

Write-Host "DONE. Upload the complete results folder for analysis." -ForegroundColor Green
