# CrossResumeBench MCC v3 — Post-Validation Study Pack

**Status:** Post-validation analysis package. The successful MCC v3 holdout is frozen and treated as read-only evidence.

## What this package does

1. **Paired statistical validation** of the real 6,144-row passed holdout.
2. **Post-validation ablation** of MCC v3 components (explanatory, not a new independent holdout).
3. **Mechanism performance/overhead** benchmark.
4. **Optional native end-to-end latency** on 8 canonical cases across all six directed runtime pairs.

## What it does NOT do

- It does not modify MCC v3.
- It does not modify the 32-case holdout.
- It does not replace or overwrite the passed `RESEARCH_VERDICT.json`.
- Ablation results must not be described as independent confirmatory validation because the holdout is already seen.

## One-command default study

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.\run_postvalidation.ps1
```

This runs input verification, paired statistics, 7-way ablation, mechanism microbenchmark, verification, and exports `CrossResumeBench_MCCv3_PostValidation_results.zip`.

For native timing after the default study:

```powershell
.\run_native_performance.ps1
```

## Research interpretation

The passed holdout remains the safety/generalization evidence. This package answers: **how strong is the paired evidence, which MCC v3 components matter, and what overhead does the proof-obligation mechanism add?**
