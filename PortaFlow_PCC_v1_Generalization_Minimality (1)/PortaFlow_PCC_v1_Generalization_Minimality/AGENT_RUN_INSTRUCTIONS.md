# Instructions for the execution agent

Your job is only to execute and return artifacts. **Do not interpret, rewrite, or optimize the research design.**

1. Extract the folder without renaming source files.
2. Open PowerShell in the project root.
3. Run `Set-ExecutionPolicy -Scope Process Bypass` if needed.
4. Run `.\run_pcc_v1.ps1`.
5. Do not manually edit generated CSV/JSON results.
6. If a framework installation or probe fails, preserve the complete error output. Do not convert a technical failure into a semantic failure.
7. Do not add an API key. No LLM is used in this experiment.
8. When finished, return the generated `PortaFlow_PCC_v1_results.zip` unchanged.

The analysis will be performed separately after execution.
