$ErrorActionPreference = "Stop"
$env:CREWAI_TRACING_ENABLED="false"; $env:CREWAI_DISABLE_TELEMETRY="true"; $env:CREWAI_DISABLE_TRACKING="true"; $env:OTEL_SDK_DISABLED="true"
python scripts/verify_freeze.py
python scripts/preflight.py
python -m pytest -q
python scripts/run_holdout.py
if (!(Test-Path "results/migration_runs.csv")) {
  python scripts/export_native_gate_diagnostics.py
  throw "Native gate stopped before migration grid. Upload CrossResumeBench_MCCv3_Holdout_NATIVE_GATE_diagnostics.zip"
}
python scripts/verify_results.py
python scripts/analyze_results.py
python scripts/export_results.py
