$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "$PSScriptRoot\src"
python scripts/clean_results.py
python scripts/preflight.py
python scripts/verify_freeze.py
python scripts/capture_environment.py
python scripts/run_semantic_benchmark.py
python scripts/run_probes.py
python scripts/run_native_confirmation.py
python scripts/analyze_results.py
python scripts/verify_results.py
python scripts/make_manifest.py
python scripts/export_results_zip.py
Write-Host "DONE: CrossResumeBench_v1_results.zip"
