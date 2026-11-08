@echo off
python scripts\verify_frozen_v2.py || exit /b 1
python scripts\preflight.py || exit /b 1
python scripts\run_phase1.py || exit /b 1
python scripts\analyze_phase1.py || exit /b 1
python scripts\verify_phase1.py || exit /b 1
python scripts\export_phase1.py || exit /b 1
