# Windows Quick Start

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:PYTHONPATH = "$PWD/src;$PWD/frozen_v2/src;$PWD"
python scripts/verify_package.py
python scripts/preflight.py
pytest -q
python scripts/verify_freeze.py
python scripts/run_all.py
python scripts/verify_results.py
```

If native framework lifecycle issues occur, preserve the logs and do not delete failed rows. A technical failure is not a scientific failure and must not be silently removed.
