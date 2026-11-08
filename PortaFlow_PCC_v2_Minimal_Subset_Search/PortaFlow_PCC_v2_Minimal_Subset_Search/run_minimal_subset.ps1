$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
Write-Host "[1/13] Cleaning previous results"; python scripts/clean_results.py
if (-not (Test-Path ".venv")) { Write-Host "[2/13] Creating virtual environment"; python -m venv .venv } else { Write-Host "[2/13] Reusing .venv" }
$py = Join-Path $root ".venv\Scripts\python.exe"
Write-Host "[3/13] Installing dependencies"; & $py -m pip install --upgrade pip; & $py -m pip install -r requirements.txt; & $py -m pip install -e .
Write-Host "[4/13] Preflight"; & $py scripts/preflight.py
Write-Host "[5/13] Tests"; & $py -m pytest -q
Write-Host "[6/13] Environment"; & $py scripts/capture_environment.py
Write-Host "[7/13] Native probes"; & $py scripts/run_probes.py
Write-Host "[8/13] Stage A: exhaustive 64-subset search"; & $py scripts/run_subset_search.py
Write-Host "[9/13] Stage B: native confirmation of minimal candidates"; & $py scripts/run_native_confirmation.py
Write-Host "[10/13] Analysis"; & $py scripts/analyze_results.py
Write-Host "[11/13] Verification"; & $py scripts/verify_results.py
Write-Host "[12/13] Manifest + checksums"; & $py scripts/make_manifest.py
Write-Host "[13/13] Export result ZIP"; & $py scripts/export_results_zip.py
Write-Host "DONE. Upload PortaFlow_PCC_v2_minimal_subset_results.zip for analysis."
