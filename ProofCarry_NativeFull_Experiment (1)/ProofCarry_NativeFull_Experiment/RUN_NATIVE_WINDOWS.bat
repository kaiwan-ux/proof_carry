@echo off
setlocal
if not exist .venv py -3.12 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\native_doctor.py --out results\native_preflight
if errorlevel 1 goto :fail
python scripts\run_native_full.py --cases smoke8 --profile proofcarry --variants enough
if errorlevel 1 goto :fail
for /f "usebackq delims=" %%i in ("results\LATEST_NATIVE_RUN.txt") do set SMOKE=%%i
python scripts\analyze_native_full.py "%SMOKE%"
python scripts\verify_native_full.py "%SMOKE%"
if errorlevel 1 goto :fail
python scripts\run_native_full.py --cases all120 --profile proofcarry --variants all
if errorlevel 1 goto :fail
for /f "usebackq delims=" %%i in ("results\LATEST_NATIVE_RUN.txt") do set RUN=%%i
python scripts\analyze_native_full.py "%RUN%"
python scripts\verify_native_full.py "%RUN%"
if errorlevel 1 goto :fail
echo Native run complete: %RUN%
exit /b 0
:fail
echo Native experiment stopped because a required step failed. Check the result/log files.
exit /b 1
