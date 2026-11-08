@echo off
setlocal
cd /d "%~dp0"
echo === PortaFlow Phase-0 ===

if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>nul
    if %errorlevel%==0 (
        py -3.11 -m venv .venv
        if errorlevel 1 py -3 -m venv .venv
    ) else (
        python -m venv .venv
    )
)

set PY=.venv\Scripts\python.exe
%PY% -m pip install --upgrade pip
if errorlevel 1 goto :fail
%PY% -m pip install -r requirements.txt
if errorlevel 1 goto :fail
%PY% -m pip install --pre -r requirements-maf.txt
if errorlevel 1 echo WARNING: Microsoft Agent Framework installation failed; native MAF probe may be recorded as technical_failure.

%PY% scripts\preflight.py
%PY% -m pytest -q
if errorlevel 1 goto :fail
%PY% scripts\run_experiment.py
if errorlevel 1 goto :fail
%PY% scripts\run_native_probes.py
%PY% scripts\analyze_results.py
if errorlevel 1 goto :fail
%PY% scripts\make_manifest.py
if errorlevel 1 goto :fail

echo.
echo DONE. Send the complete results folder back for analysis:
echo %cd%\results
exit /b 0

:fail
echo.
echo ERROR: Phase-0 stopped. Copy the console error and send it back.
exit /b 1
