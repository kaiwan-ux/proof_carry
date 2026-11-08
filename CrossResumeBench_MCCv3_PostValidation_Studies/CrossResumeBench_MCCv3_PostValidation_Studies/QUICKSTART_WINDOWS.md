# Windows Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.\run_postvalidation.ps1
```

Default output: `CrossResumeBench_MCCv3_PostValidation_results.zip`.

Optional native latency:

```powershell
.\run_native_performance.ps1
```

If native latency is run, re-run `python scripts/export_results.py` afterward to include it in the ZIP.
