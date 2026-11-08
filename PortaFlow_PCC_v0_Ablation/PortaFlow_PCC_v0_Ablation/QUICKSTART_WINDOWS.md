# Windows Quick Start

1. Extract the ZIP to a normal local folder, for example `C:\Research\PortaFlow_PCC_v0_Ablation`.
2. Open that folder.
3. Right-click empty space and choose **Open in Terminal**, or type `powershell` in the Explorer address bar.
4. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_pcc_v0.ps1
```

The script creates `.venv`, installs pinned framework versions, runs preflight/tests/native probes, executes the PCC ablation, analyzes results, verifies completeness and creates:

`PortaFlow_PCC_v0_results.zip`

Upload that ZIP back to ChatGPT for analysis.

## No API key

Do not add a Groq/GPT-OSS key for this experiment. The deterministic ablation deliberately has no LLM.
