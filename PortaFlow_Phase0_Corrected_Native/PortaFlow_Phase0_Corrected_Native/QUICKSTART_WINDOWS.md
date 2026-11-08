# Windows Quick Start

Recommended: Python 3.12 x64.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_corrected_phase0.ps1
```

The script creates `.venv`, installs pinned native frameworks, enables UTF-8 output, runs unit tests, runs framework probes, executes 54 native cross-runtime condition runs, analyzes them, verifies the 54-case matrix, and creates checksums.

No API key is needed.
