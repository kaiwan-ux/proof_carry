$ErrorActionPreference='Stop'
$env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'; $env:MPLBACKEND='Agg'
python scripts/verify_inputs.py
python scripts/run_postvalidation.py --bootstrap-reps 10000 --micro-repeats 10
python scripts/verify_postvalidation.py
python scripts/export_results.py
Write-Host 'POST-VALIDATION STUDIES COMPLETE'
