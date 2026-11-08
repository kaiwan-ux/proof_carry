$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv")) { py -3.12 -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\native_doctor.py --out results\native_preflight
python scripts\run_native_full.py --cases smoke8 --profile proofcarry --variants enough
$smoke = Get-Content results\LATEST_NATIVE_RUN.txt
python scripts\analyze_native_full.py $smoke
python scripts\verify_native_full.py $smoke
python scripts\run_native_full.py --cases all120 --profile proofcarry --variants all
$run = Get-Content results\LATEST_NATIVE_RUN.txt
python scripts\analyze_native_full.py $run
python scripts\verify_native_full.py $run
Write-Host "ProofCarry native run complete: $run"
