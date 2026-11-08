$ErrorActionPreference='Stop'
$env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'; $env:CREWAI_TRACING_ENABLED='false'; $env:CREWAI_DISABLE_TELEMETRY='true'; $env:CREWAI_DISABLE_TRACKING='true'; $env:OTEL_SDK_DISABLED='true'
python -m studies.performance.run_native_latency --repeats 3
python scripts/export_results.py
