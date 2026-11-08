# Windows Quick Start — Revision B

Open PowerShell inside the extracted folder.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Then run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_phase1_revisionB.ps1
```

The script disables CrewAI tracing/telemetry for a non-interactive benchmark run, verifies frozen MCC hashes, checks installed runtimes, runs unit/design tests, executes the experiment, analyzes the raw CSVs, validates row integrity and exports the result ZIP.

Expected output file:

```text
CrossResumeBench_v3_Phase1_RevisionB_results.zip
```

Upload that ZIP even if the screen says `GATE: FAIL`.

No API key and no LLM are needed.
