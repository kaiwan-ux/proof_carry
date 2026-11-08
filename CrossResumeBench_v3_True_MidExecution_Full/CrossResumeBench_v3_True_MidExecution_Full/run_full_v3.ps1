$ErrorActionPreference = "Stop"
$env:CREWAI_TRACING_ENABLED="false"
$env:CREWAI_DISABLE_TELEMETRY="true"
$env:CREWAI_DISABLE_TRACKING="true"
$env:OTEL_SDK_DISABLED="true"

function Run-Step([string]$Script) {
  python $Script
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Run-Step "scripts/preflight.py"
Run-Step "scripts/verify_frozen_v2.py"
Run-Step "scripts/generate_suite.py"
Run-Step "scripts/verify_experiment_freeze.py"

python -m pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Clean prior generated results but preserve directory placeholders.
Get-ChildItem results -Recurse -File | Where-Object { $_.Name -ne ".gitkeep" } | Remove-Item -Force

python scripts/run_native_family_gate.py
if ($LASTEXITCODE -ne 0) {
  python scripts/export_native_gate_diagnostics.py
  Write-Host "Native family gate failed. Upload CrossResumeBench_v3_Full_NATIVE_GATE_diagnostics.zip"
  exit 4
}

Run-Step "scripts/run_full_v3.py"
Run-Step "scripts/analyze_results.py"

python scripts/verify_results.py
$verifyExit = $LASTEXITCODE
python scripts/make_manifest.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python scripts/export_results.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($verifyExit -ne 0) {
  Write-Host "Full results were exported, but infrastructure verification reported problems. Upload CrossResumeBench_v3_Full_results.zip."
  exit $verifyExit
}

Write-Host "Done. Upload CrossResumeBench_v3_Full_results.zip"
