$ErrorActionPreference = "Stop"
function Run-Step([string]$cmd) {
  Write-Host "> $cmd"
  Invoke-Expression $cmd
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
Run-Step "python scripts/verify_frozen_v2.py"
Run-Step "python scripts/preflight.py"
Run-Step "python scripts/run_phase1.py"
Run-Step "python scripts/analyze_phase1.py"
Run-Step "python scripts/verify_phase1.py"
Run-Step "python scripts/export_phase1.py"
Write-Host "Phase 1 PASS. Upload CrossResumeBench_v3_Phase1_results.zip"
