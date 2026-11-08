@echo off
setlocal
if not exist .venv py -3.12 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\verify_package.py || goto :fail
python scripts\verify_freeze.py || goto :fail
python scripts\native_doctor.py --out results\native_preflight || goto :fail
python scripts\run_semantic.py || goto :fail
python scripts\run_security.py || goto :fail
python scripts\run_ablation.py || goto :fail
python scripts\run_performance.py || goto :fail
python scripts\run_native_full.py --cases smoke8 --profile proofcarry --variants enough || goto :fail
for /f "usebackq delims=" %%i in ("results\LATEST_NATIVE_RUN.txt") do set SMOKE=%%i
python scripts\analyze_native_full.py "%SMOKE%" || goto :fail
python scripts\verify_native_full.py "%SMOKE%" || goto :fail
python scripts\run_native_full.py --cases all120 --profile full --variants all || goto :fail
for /f "usebackq delims=" %%i in ("results\LATEST_NATIVE_RUN.txt") do set NATIVE=%%i
python scripts\analyze_native_full.py "%NATIVE%" || goto :fail
python scripts\verify_native_full.py "%NATIVE%" || goto :fail
python scripts\analyze_results.py
echo Maximum ProofCarry experiment complete. Native result: %NATIVE%
exit /b 0
:fail
echo Experiment stopped. Inspect logs and result files; do not reinterpret technical failures as semantic results.
exit /b 1
