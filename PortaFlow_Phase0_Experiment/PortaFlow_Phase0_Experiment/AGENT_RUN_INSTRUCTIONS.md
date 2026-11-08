# Instructions for a Coding/Execution Agent

Your job is **only to execute the experiment and preserve artifacts**. Do not reinterpret the research hypothesis, modify scoring rules, remove failed runs, or 'improve' results.

1. Read `README.md`, `RESEARCH_PROTOCOL.md`, and `config/experiment.json`.
2. Use Python 3.11 or 3.12.
3. Create an isolated `.venv`.
4. Install `requirements.txt`; install `agent-framework` with `--pre` if normal install does not resolve it.
5. Run `python scripts/preflight.py` and save console output.
6. Run `python -m pytest -q`.
7. Run `python scripts/run_experiment.py`.
8. Run `python scripts/run_native_probes.py`.
9. Run `python scripts/analyze_results.py`.
10. Run `python scripts/make_manifest.py`.
11. Do not delete technical failures.
12. Do not manually edit `results/raw_runs.csv` or any generated output.
13. Return the entire `results/` directory unchanged.
14. Also return `pip freeze` if preflight did not capture it correctly.
15. If a native probe breaks because of framework API drift, record the full error and continue the remaining probes.
16. Do not use an LLM unless explicitly running `scripts/run_llm_extension.py`.
17. Never place an API key in logs, source code, screenshots, or result files.
