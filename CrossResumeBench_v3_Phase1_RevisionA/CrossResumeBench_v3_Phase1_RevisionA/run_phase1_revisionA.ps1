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
Run-Step "python scripts/run_phase1_revisionA.py"
Run-Step "python scripts/analyze_phase1_revisionA.py"
Run-Step "python scripts/verify_integrity.py"
Run-Step "python scripts/export_phase1_revisionA.py"
$gate = Get-Content "results/PHASE1_REVISIONA_GATE.json" | ConvertFrom-Json
if ($gate.go_for_full_v3) { Write-Host "PHASE 1 REVISION A GATE: PASS" -ForegroundColor Green }
else { Write-Host "PHASE 1 REVISION A GATE: FAIL — upload the results ZIP for analysis; do NOT start full v3." -ForegroundColor Yellow }
Write-Host "Upload CrossResumeBench_v3_Phase1_RevisionA_results.zip"
