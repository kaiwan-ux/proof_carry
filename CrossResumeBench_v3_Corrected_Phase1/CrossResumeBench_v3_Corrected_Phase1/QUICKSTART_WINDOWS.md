# Windows Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

$env:CREWAI_TRACING_ENABLED="false"
$env:CREWAI_DISABLE_TELEMETRY="true"
$env:CREWAI_DISABLE_TRACKING="true"
$env:OTEL_SDK_DISABLED="true"

Set-ExecutionPolicy -Scope Process Bypass
.\run_phase1.ps1
```

If preflight reports an unsupported API, do not fake the result. Save `results/capabilities.json` and treat it as a framework capability finding.
