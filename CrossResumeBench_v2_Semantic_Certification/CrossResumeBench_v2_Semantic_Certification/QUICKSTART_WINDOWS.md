# Windows Quickstart

```powershell
cd CrossResumeBench_v2_Semantic_Certification
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.un_crossresumebench_v2.ps1
```

Expected output: `CrossResumeBench_v2_results.zip`.

No LLM/API key is used.
