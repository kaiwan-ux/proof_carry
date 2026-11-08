# Windows Quick Start
1. Extract the ZIP.
2. Open the extracted folder.
3. Right-click inside the folder and open PowerShell/Terminal.
4. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_minimal_subset.ps1
```

The script creates `.venv`, installs pinned dependencies, runs tests and native probes, performs the 64-subset search, confirms selected candidates on native frameworks, analyzes/validates outputs, and exports `PortaFlow_PCC_v2_minimal_subset_results.zip`.

Do not add an API key; no LLM is used.
