from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
from portaflow_phase0.llm import configured, choose_action

load_dotenv(ROOT / ".env")

if not configured():
    raise SystemExit("GROQ_API_KEY is not set. Copy .env.example to .env and add your key.")

# This is intentionally a connectivity/structured-decision smoke test only.
# Do not mix it into deterministic Phase-0 results.
prompt = """You are inside a controlled agent-workflow experiment. Decide the next action.
State: branch_input=approve. Allowed actions: approved_path, rejected_path.
Return JSON with one key action."""
print(choose_action(prompt, {"action":"approved_path"}))
