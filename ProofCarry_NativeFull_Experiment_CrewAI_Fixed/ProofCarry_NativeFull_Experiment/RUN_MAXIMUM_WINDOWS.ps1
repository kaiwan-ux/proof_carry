$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv")) { py -3.12 -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\verify_package.py
python scripts\verify_freeze.py
python scripts\native_doctor.py --out results\native_preflight

# Existing semantic/security/mechanism studies on this same 120-case suite.
python scripts\run_semantic.py
python scripts\run_security.py
python scripts\run_ablation.py
python scripts\run_performance.py

# Native smoke gate.
python scripts\run_native_full.py --cases smoke8 --profile proofcarry --variants enough
$smoke = Get-Content results\LATEST_NATIVE_RUN.txt
python scripts\analyze_native_full.py $smoke
python scripts\verify_native_full.py $smoke

# Maximum native matrix: 120 cases x 6 pairs x 5 variants x 10 methods.
python scripts\run_native_full.py --cases all120 --profile full --variants all
$native = Get-Content results\LATEST_NATIVE_RUN.txt
python scripts\analyze_native_full.py $native
python scripts\verify_native_full.py $native

python scripts\analyze_results.py
Write-Host "Maximum ProofCarry experiment complete. Native result: $native"
