$ErrorActionPreference = "Stop"
$env:PYTHONUTF8="1"
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONUNBUFFERED="1"
$env:CREWAI_TRACING_ENABLED="false"
$env:CREWAI_DISABLE_TELEMETRY="true"
$env:CREWAI_DISABLE_TRACKING="true"
$env:OTEL_SDK_DISABLED="true"
try { chcp 65001 | Out-Null } catch {}

python scripts/verify_freeze.py
if ($LASTEXITCODE -ne 0) { throw "Scientific freeze verification failed." }
python scripts/validate_infrafixA.py
if ($LASTEXITCODE -ne 0) { throw "InfraFixA verification failed." }
python scripts/preflight.py
if ($LASTEXITCODE -ne 0) { throw "Preflight failed." }
python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed." }

Remove-Item -Recurse -Force native_gate_results -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force results -ErrorAction SilentlyContinue

python scripts/native_gate_infrafixA.py
$gateCode=$LASTEXITCODE
if ($gateCode -ne 0) {
    python scripts/export_native_gate_diagnostics_infrafixA.py
    Write-Host "Native gate did not pass. Upload CrossResumeBench_MCCv3_Holdout_InfraFixA_NATIVE_GATE_diagnostics.zip"
    exit $gateCode
}

python scripts/run_holdout_infrafixA.py
if ($LASTEXITCODE -ne 0) { throw "Holdout runner failed before complete row export." }
python scripts/verify_results_infrafixA.py
if ($LASTEXITCODE -ne 0) { throw "Result structure is incomplete." }
python scripts/analyze_results.py
python scripts/export_results_infrafixA.py
Write-Host "Complete. Upload CrossResumeBench_MCCv3_Holdout_InfraFixA_results.zip"
