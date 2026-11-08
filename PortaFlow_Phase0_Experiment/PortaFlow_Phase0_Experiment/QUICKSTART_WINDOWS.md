# Windows Quick Start

## Option A — easiest

Open PowerShell in this folder and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_phase0.ps1
```

## Option B — Command Prompt

Double-click or run:

```bat
run_phase0.bat
```

## Manual commands

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install --pre agent-framework
python scripts\preflight.py
python -m pytest -q
python scripts\run_experiment.py
python scripts\run_native_probes.py
python scripts\analyze_results.py
python scripts\make_manifest.py
```

## If Microsoft Agent Framework fails to install

Its Python package may still require prerelease installation:

```powershell
pip install --pre agent-framework
```

The rest of the experiment can still run; the MAF native probe will be marked as a technical failure until the package is available.

## If you are in a hurry for proposal evidence

Run:

```powershell
python scripts\run_experiment.py
python scripts\analyze_results.py
```

This generates the controlled baseline matrix immediately. Then run the native probes as soon as the three frameworks install successfully.

## Optional GPT-OSS-120B extension

Copy:

```text
.env.example -> .env
```

Then set:

```text
GROQ_API_KEY=your_key_here
```

Run:

```powershell
python scripts\run_llm_extension.py
```

The key is **not needed for Phase-0**.
