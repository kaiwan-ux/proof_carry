
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"results/CREWAI_REPAIRED_GATE.json"
if not p.exists(): raise SystemExit("Missing CREWAI_REPAIRED_GATE.json; run experiment first")
v=json.loads(p.read_text(encoding="utf-8"))
for k,val in v["gates"].items(): print(("PASS" if val else "FAIL"),k)
if not v.get("crewai_repaired_gate_pass"): raise SystemExit("CrewAI repaired gate FAILED")
print("PASS: CrewAI repaired gate")
