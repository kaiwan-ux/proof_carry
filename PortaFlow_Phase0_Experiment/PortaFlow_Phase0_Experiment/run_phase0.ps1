$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "=== PortaFlow Phase-0 ==="
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.11 -m venv .venv
        if ($LASTEXITCODE -ne 0) { & py -3 -m venv .venv }
    } else {
        & python -m venv .venv
    }
}

$Py = Join-Path $Root ".venv\Scripts\python.exe"
& $Py -m pip install --upgrade pip
& $Py -m pip install -r requirements.txt
& $Py -m pip install --pre -r requirements-maf.txt

& $Py scripts\preflight.py
& $Py -m pytest -q
& $Py scripts\run_experiment.py
& $Py scripts\run_native_probes.py
& $Py scripts\analyze_results.py
& $Py scripts\make_manifest.py

Write-Host ""
Write-Host "DONE. Send the complete results folder back for analysis:"
Write-Host (Join-Path $Root "results")
