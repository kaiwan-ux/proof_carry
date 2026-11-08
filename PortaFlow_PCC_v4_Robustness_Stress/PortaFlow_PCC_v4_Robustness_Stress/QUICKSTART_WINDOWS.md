# Windows Quickstart

1. Extract the ZIP.
2. Open the extracted folder.
3. Click the address bar, type `powershell`, press Enter.
4. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_robustness.ps1
```

When complete, upload `PortaFlow_PCC_v4_robustness_results.zip`.

The deterministic experiment requires no API key.

Optional GPT-OSS-120B robustness stage:

```powershell
Copy-Item .env.example .env
notepad .env
# add GROQ_API_KEY
.\run_llm_robustness.ps1
```
