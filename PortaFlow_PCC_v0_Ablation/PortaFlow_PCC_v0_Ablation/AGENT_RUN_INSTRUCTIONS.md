# Agent Run Instructions

If a coding/execution agent is running this package, its job is **execution only**.

1. Do not redesign PCC.
2. Do not change evaluator rules to improve results.
3. Do not insert an LLM.
4. Do not remove technical failures from CSV/JSON.
5. Do not manually edit native source/target artifacts.
6. Run `run_pcc_v0.ps1` on Windows or `run_pcc_v0.sh` on Linux/macOS.
7. If dependency installation or a framework API fails, fix only the compatibility issue while preserving the declared experiment semantics, then document the exact patch in `results/TECHNICAL_PATCHES.md`.
8. Re-run from a clean `results/` folder after any patch.
9. Return `PortaFlow_PCC_v0_results.zip` unchanged for analysis.

The analysis and research interpretation will be done separately after execution.
