$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "[1/12] Cleaning previous results"
python scripts/clean_results.py

if (-not (Test-Path ".venv")) {
  Write-Host "[2/12] Creating virtual environment"
  python -m venv .venv
} else { Write-Host "[2/12] Reusing .venv" }

$py = Join-Path $root ".venv\Scripts\python.exe"
Write-Host "[3/12] Installing dependencies"
& $py -m pip install --upgrade pip
& $py -m pip install -r requirements.txt
& $py -m pip install -e .

Write-Host "[4/12] Preflight"
& $py scripts/preflight.py
Write-Host "[5/12] Unit/research tests"
& $py -m pytest -q
Write-Host "[6/12] Capturing environment"
& $py scripts/capture_environment.py
Write-Host "[7/12] Native framework probes"
& $py scripts/run_probes.py
Write-Host "[8/12] Running 432-row generalization/minimality experiment"
& $py scripts/run_generalization.py
Write-Host "[9/12] Analyzing"
& $py scripts/analyze_results.py
Write-Host "[10/12] Verifying completeness and anti-leak rules"
& $py scripts/verify_results.py
Write-Host "[11/12] Manifest + checksums"
& $py scripts/make_manifest.py
Write-Host "[12/12] Exporting result ZIP"
& $py scripts/export_results_zip.py
Write-Host "DONE. Upload PortaFlow_PCC_v1_results.zip for analysis."
