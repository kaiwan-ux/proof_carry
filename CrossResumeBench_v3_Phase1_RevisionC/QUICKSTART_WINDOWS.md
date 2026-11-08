# Windows Quick Start — Phase 1 Revision C

Open PowerShell in the extracted folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.\run_phase1_revisionC.ps1
```

No API key is needed.

The runner first verifies frozen MCC v2, pinned framework versions and unit tests. It then runs a **MAF-only native checkpoint probe**.

If the MAF probe fails, the 72-row grid is intentionally skipped. Upload:

```text
CrossResumeBench_v3_Phase1_RevisionC_MAF_probe_diagnostics.zip
```

If the MAF probe passes, the full Phase-1 matrix runs. Upload:

```text
CrossResumeBench_v3_Phase1_RevisionC_results.zip
```
