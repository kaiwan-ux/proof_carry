# Agent execution instructions

Execute only; do not redesign the experiment.

1. Do not modify `config/frozen_candidates.json`.
2. Do not change workflow/profile definitions after seeing outcomes.
3. Run `run_robustness.ps1` on Windows.
4. If a framework/API error occurs, record the technical failure. Do not convert it into a semantic result.
5. Do not run the optional LLM stage unless a user-provided `GROQ_API_KEY` is present in `.env`.
6. Return the generated result ZIP unchanged for analysis.
