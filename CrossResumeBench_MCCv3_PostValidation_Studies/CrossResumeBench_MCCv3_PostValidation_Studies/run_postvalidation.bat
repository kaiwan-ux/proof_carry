@echo off
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set MPLBACKEND=Agg
python scripts\verify_inputs.py && python scripts\run_postvalidation.py --bootstrap-reps 10000 --micro-repeats 10 && python scripts\verify_postvalidation.py && python scripts\export_results.py
