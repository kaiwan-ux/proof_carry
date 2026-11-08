
# Windows Quick Start — CrewAI Repaired Gate

```powershell
cd CrossResumeBench_v3_CrewAI_Repaired_Gate
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.\run_crewai_gate.ps1
```

At the end, send back either:

```text
CrossResumeBench_v3_CrewAI_Repaired_Gate_results.zip
```

or, if the pre-gate stops early:

```text
CrossResumeBench_v3_CrewAI_Repaired_Gate_diagnostics.zip
```
