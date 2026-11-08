# Quickstart — Windows PowerShell

Extract the ZIP and open PowerShell in the extracted folder.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.\run_mccv3_holdout_infrafixA.ps1
```

The runner sets UTF-8 automatically, but you may also run:

```powershell
chcp 65001
$env:PYTHONUTF8="1"
$env:PYTHONIOENCODING="utf-8"
```

### If the native gate fails

The run continues through all 24 probes and writes progress incrementally. It then creates:

`CrossResumeBench_MCCv3_Holdout_InfraFixA_NATIVE_GATE_diagnostics.zip`

Upload that ZIP.

### If the native gate passes

The frozen 6,144-row holdout runs. At the end it creates:

`CrossResumeBench_MCCv3_Holdout_InfraFixA_results.zip`

Upload that ZIP whether the MCC v3 scientific verdict says PASS or FAIL.
