# ProofCarry NativeFull Experiment

This package adds a **real native-runtime execution layer** to the ProofCarry / MCC v3 experimental program.

It keeps semantic and native evidence separate:

- semantic rows test ProofCarry's continuation logic under controlled evidence conditions;
- native rows require real LangGraph, CrewAI, or Microsoft Agent Framework execution for checkpoint/self-resume, source capture, and target continuation;
- missing packages, checkpoint failures, API failures, lifecycle hangs, and timeouts are **technical failures**, never semantic successes or unsafe outcomes.

The supplied `ProofCarry_Final_Experimental_120_Semantic_Companion.zip` is retained as the latest semantic-only companion package. This NativeFull package uses a 120-case native stress suite with the same eight continuation families and five evidence conditions.

## What NativeFull adds

1. **Environment doctor** — verifies imports, versions, and checkpoint/resume API capabilities.
2. **24 native family gates** — 8 families x 3 runtimes.
3. **Full self-resume controls** — 120 cases x 3 runtimes = 360 controls for `all120`.
4. **Full source-capture controls** — 120 cases x 3 runtimes = 360 captures.
5. **All six directed runtime pairs**:
   - LangGraph -> CrewAI
   - LangGraph -> MAF
   - CrewAI -> LangGraph
   - CrewAI -> MAF
   - MAF -> LangGraph
   - MAF -> CrewAI
6. **Five native evidence conditions**:
   - `enough_evidence`
   - `missing_critical_fact`
   - `runtime_binding_complete`
   - `runtime_binding_missing`
   - `irrelevant_noise`
7. **Three method profiles**:
   - `proofcarry`: ProofCarry only — 3,600 migration rows on all 120 cases.
   - `core`: 4 methods — 14,400 migration rows.
   - `full`: all 10 methods — 36,000 migration rows.
8. **Partial-matrix preservation** — if one runtime/family gate fails, passing runtime pairs still run; blocked rows are marked technical.
9. **Automatic analysis and verification** — method, pair, family, condition summaries plus a native research verdict.

## Recommended environment

Use a clean **Python 3.12.x** virtual environment.

Pinned native dependencies are in `requirements.txt`:

- `langgraph==1.2.11`
- `crewai==1.15.17`
- `agent-framework-core==1.15.0`

The exact versions are intentionally pinned because checkpoint/resume APIs change across releases.

## Windows: safest run sequence

PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

python scripts\native_doctor.py --out results\native_preflight

# Small real-native gate first
python scripts\run_native_full.py --cases smoke8 --profile proofcarry --variants enough
$smoke = Get-Content results\LATEST_NATIVE_RUN.txt
python scripts\analyze_native_full.py $smoke
python scripts\verify_native_full.py $smoke

# Main ProofCarry native matrix: 3,600 migration rows + controls
python scripts\run_native_full.py --cases all120 --profile proofcarry --variants all
$run = Get-Content results\LATEST_NATIVE_RUN.txt
python scripts\analyze_native_full.py $run
python scripts\verify_native_full.py $run

# Maximum comparison matrix: 36,000 migration rows + controls
python scripts\run_native_full.py --cases all120 --profile full --variants all
$full = Get-Content results\LATEST_NATIVE_RUN.txt
python scripts\analyze_native_full.py $full
python scripts\verify_native_full.py $full
```

Or run `RUN_NATIVE_WINDOWS.ps1`.

## Linux/macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/native_doctor.py --out results/native_preflight
python scripts/run_native_full.py --cases smoke8 --profile proofcarry --variants enough
RUN=$(cat results/LATEST_NATIVE_RUN.txt)
python scripts/analyze_native_full.py "$RUN"
python scripts/verify_native_full.py "$RUN"
```

Then use `--cases all120 --profile proofcarry --variants all` for the main native study, or `--profile full` for the maximum matrix.

## Paper-aligned 104-case preset

If you want a balanced 104-case native study matching the scale of the 104-case expanded paper experiment:

```bash
python scripts/run_native_full.py --cases paper104 --profile proofcarry --variants all
```

This selects 13 cases per family. It is a separate native study; do not merge its rows into the semantic CSV.

## Important CrewAI behavior

CrewAI receives special handling because checkpoint persistence was the unstable part of the previous re-check. The adapter:

1. first requests a `method_execution_finished` checkpoint;
2. if that event profile produces no persisted checkpoint, retries with `on_events=["*"]`;
3. still requires a **real persisted checkpoint file** containing the paused execution;
4. resumes through `Flow.from_checkpoint(...)` when supported, otherwise through `kickoff(from_checkpoint=CheckpointConfig(...))`;
5. never falls back to a synthetic checkpoint.

If both checkpoint modes fail, the CrewAI row is technical and the experiment continues for runtime pairs whose gates pass.

## Result files

Each native run contains:

```text
native_environment.csv
native_environment.json
native_family_gate.csv
native_self_resume.csv
native_source_captures.csv
native_runs.csv
native_method_summary.csv
native_pair_summary.csv
native_family_summary.csv
native_condition_summary.csv
NATIVE_RUN_META.json
NATIVE_EXPECTED_COUNTS.json
NATIVE_ANALYSIS_SUMMARY.md
NATIVE_RESEARCH_VERDICT.json
NATIVE_VERIFICATION.json
native_work/
```

`native_work/` contains per-operation checkpoints/logs and is deliberately retained for auditability.

## Scientific interpretation rule

A row is evidence of native cross-runtime continuation only when:

1. the source family's native gate passed;
2. source native checkpoint/capture succeeded;
3. ProofCarry/baseline produced its decision from portable evidence;
4. for `CONTINUE`, the target runtime actually executed the lowered plan;
5. no technical failure occurred.

A safe rejection does not execute the target workflow because ProofCarry has deliberately denied continuation.

## Current package validation

The package passes its Python/unit test suite (`7 passed`) and all files compile. The environment used to build this ZIP did **not** have LangGraph/CrewAI/MAF installed and did not have network access to install them, so fresh native result CSVs are intentionally **not pre-populated**. See `build_validation/current_container_doctor/` and `BUILD_NATIVEFULL_VALIDATION.md`.

That is preferable to fabricating or relabeling semantic rows as native execution.

## Integrated one-command run

After the pinned native environment is installed:

```bash
python scripts/run_all.py
```

This runs package/freeze verification, semantic, security, ablation, performance, and the **3,600-row ProofCarry-only native matrix**. For the ten-method maximum native matrix use `RUN_MAXIMUM_WINDOWS.ps1` or `--profile full` explicitly.
