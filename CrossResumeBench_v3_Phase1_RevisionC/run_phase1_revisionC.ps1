$ErrorActionPreference = "Stop"

function Run-Step([string]$cmd) {
  Write-Host "> $cmd"
  Invoke-Expression $cmd
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$env:CREWAI_TRACING_ENABLED="false"
$env:CREWAI_DISABLE_TELEMETRY="true"
$env:CREWAI_DISABLE_TRACKING="true"
$env:OTEL_SDK_DISABLED="true"

Run-Step "python scripts/verify_frozen_v2.py"
Run-Step "python scripts/preflight.py"
Run-Step "python -m pytest -q"

Write-Host "> python scripts/probe_maf_revisionC.py"
python scripts/probe_maf_revisionC.py
if ($LASTEXITCODE -ne 0) {
  Write-Host "MAF Revision C probe FAILED. The 72-row migration grid will NOT run." -ForegroundColor Yellow
  python scripts/export_maf_probe_diagnostics.py
  Write-Host "Upload CrossResumeBench_v3_Phase1_RevisionC_MAF_probe_diagnostics.zip" -ForegroundColor Yellow
  exit 2
}

Run-Step "python scripts/run_phase1_revisionC.py"
Run-Step "python scripts/analyze_phase1_revisionC.py"
Run-Step "python scripts/verify_integrity.py"
Run-Step "python scripts/export_phase1_revisionC.py"

$gate = Get-Content "results/PHASE1_REVISIONC_GATE.json" | ConvertFrom-Json
if ($gate.go_for_full_v3) {
  Write-Host "PHASE 1 REVISION C GATE: PASS" -ForegroundColor Green
} else {
  Write-Host "PHASE 1 REVISION C GATE: FAIL - upload the results ZIP; do NOT start full v3." -ForegroundColor Yellow
}
Write-Host "Upload CrossResumeBench_v3_Phase1_RevisionC_results.zip"
