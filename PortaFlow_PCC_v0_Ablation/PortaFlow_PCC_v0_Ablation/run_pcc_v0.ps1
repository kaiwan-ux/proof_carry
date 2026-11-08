$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
Set-Location $PSScriptRoot

function Invoke-Native([string]$Exe, [string[]]$Arguments) {
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Exe $($Arguments -join ' ')" }
}

Write-Host "=== PortaFlow PCC v0 Ablation ===" -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.12 -c "import sys" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Invoke-Native "py" @("-3.12","-m","venv",".venv")
        } else {
            & py -3.11 -c "import sys" 2>$null
            if ($LASTEXITCODE -eq 0) { Invoke-Native "py" @("-3.11","-m","venv",".venv") }
            else { Invoke-Native "py" @("-3","-m","venv",".venv") }
        }
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        Invoke-Native "python" @("-m","venv",".venv")
    } else {
        throw "Python 3 is not installed or not on PATH. Python 3.12 is recommended."
    }
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Virtual environment Python not found: $python" }

Invoke-Native $python @("-m","pip","install","--upgrade","pip")
Invoke-Native $python @("-m","pip","install","-r","requirements.txt")
Invoke-Native $python @("-m","pip","install","-e",".")
Invoke-Native $python @("scripts/clean_results.py")
Invoke-Native $python @("scripts/preflight.py")
Invoke-Native $python @("-m","pytest","-q")
Invoke-Native $python @("scripts/run_probes.py")
Invoke-Native $python @("scripts/run_pcc_ablation.py")
Invoke-Native $python @("scripts/analyze_pcc.py")
Invoke-Native $python @("scripts/capture_environment.py")
Invoke-Native $python @("scripts/verify_results.py")
Invoke-Native $python @("scripts/make_manifest.py")
Invoke-Native $python @("scripts/export_results_zip.py")

Write-Host ""
Write-Host "SUCCESS. Upload PortaFlow_PCC_v0_results.zip back to ChatGPT." -ForegroundColor Green
