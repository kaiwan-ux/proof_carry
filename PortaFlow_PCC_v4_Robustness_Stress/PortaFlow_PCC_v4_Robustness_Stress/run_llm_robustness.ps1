$ErrorActionPreference="Stop"; $root=Split-Path -Parent $MyInvocation.MyCommand.Path; Set-Location $root
$py=Join-Path $root ".venv\Scripts\python.exe"; if (-not (Test-Path $py)) { throw "Run run_robustness.ps1 first." }
if (-not (Test-Path ".env")) { throw "Copy .env.example to .env and add GROQ_API_KEY first." }
& $py scripts/run_llm_stage.py; & $py scripts/analyze_llm.py; & $py scripts/make_manifest.py; & $py scripts/export_results_zip.py
Write-Host "LLM robustness stage complete."
