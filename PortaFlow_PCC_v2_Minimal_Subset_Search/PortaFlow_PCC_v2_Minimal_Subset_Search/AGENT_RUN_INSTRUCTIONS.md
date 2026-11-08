# Agent Run Instructions
Your job is execution only. Do not modify the research design, do not reinterpret failures as successes, and do not edit result files.

From the project root run `run_minimal_subset.ps1` on Windows or `run_minimal_subset.sh` on Linux/macOS.

Success criteria:
- tests pass,
- all three native probes are `status=ok`,
- Stage A contains 1,024 workflow rows and 128 subset summaries,
- Stage B has the exact row count implied by `selected_native_conditions.json`,
- zero technical failures,
- `VERIFY_RESULTS.json` says `ok: true`,
- result ZIP is produced.

If a technical failure occurs, preserve the error output; do not manually change scientific rows.
