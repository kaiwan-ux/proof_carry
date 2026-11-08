# Windows Quick Start

## Deterministic true hold-out experiment

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.un_true_holdout.ps1
```

This does **not** require an API key.

## Optional GPT-OSS-120B stage

After the deterministic run:

```powershell
Copy-Item .env.example .env
notepad .env
```

Add your `GROQ_API_KEY`, save, then:

```powershell
.un_llm_stage.ps1
```
