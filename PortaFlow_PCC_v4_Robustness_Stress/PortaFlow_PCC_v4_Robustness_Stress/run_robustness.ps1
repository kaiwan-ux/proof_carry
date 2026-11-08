$ErrorActionPreference="Stop"
$env:PYTHONUTF8="1"; $env:PYTHONIOENCODING="utf-8"
$root=Split-Path -Parent $MyInvocation.MyCommand.Path; Set-Location $root
Write-Host "[1/11] Clean"; python scripts/clean_results.py
if (-not (Test-Path ".venv")) { Write-Host "[2/11] Create venv"; python -m venv .venv } else { Write-Host "[2/11] Reuse venv" }
$py=Join-Path $root ".venv\Scripts\python.exe"
Write-Host "[3/11] Install pinned environment"; & $py -m pip install --upgrade pip; & $py -m pip install -r requirements.txt; & $py -m pip install -e .
Write-Host "[4/11] Preflight"; & $py scripts/preflight.py
Write-Host "[5/11] Tests"; & $py -m pytest -q
Write-Host "[6/11] Environment"; & $py scripts/capture_environment.py
Write-Host "[7/11] Native probes"; & $py scripts/run_probes.py
Write-Host "[8/11] 1,200-run native robustness matrix"; & $py scripts/run_native_robustness.py
Write-Host "[9/11] Analysis"; & $py scripts/analyze_results.py
Write-Host "[10/11] Verify"; & $py scripts/verify_results.py
Write-Host "[11/11] Manifest + export"; & $py scripts/make_manifest.py; & $py scripts/export_results_zip.py
Write-Host "DONE. Upload PortaFlow_PCC_v4_robustness_results.zip"
