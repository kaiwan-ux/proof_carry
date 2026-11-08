# Agent Run Instructions

1. Do not edit `config/frozen_candidates.json`.
2. Run `run_true_holdout.ps1` from the project root.
3. Do not manually modify generated CSV/JSON results.
4. If a framework API fails, preserve the traceback in `results/technical_failures.json`; do not silently substitute fake adapters.
5. Do not run the optional LLM stage unless `.env` contains the user's own Groq API key.
6. For the optional stage, use exactly the configured `openai/gpt-oss-120b` model unless the user explicitly changes it.
7. Return the generated result ZIP without interpreting or altering it.
