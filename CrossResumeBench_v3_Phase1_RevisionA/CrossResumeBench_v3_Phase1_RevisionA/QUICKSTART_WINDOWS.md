# Windows Quickstart

1. Extract the ZIP.
2. Open PowerShell in the extracted folder.
3. Run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.\run_phase1_revisionA.ps1
```

The runner disables CrewAI tracing/telemetry for reproducible non-interactive execution.

Expected output file:

`CrossResumeBench_v3_Phase1_RevisionA_results.zip`

Upload it even if the gate is FAIL. The gate must fail safely when a framework/API is broken or MCC behaves unexpectedly.
