
from pathlib import Path
import json,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2/src")]
from crossresumebench_crewai_gate.probe import run_probe
from crossresumebench_crewai_gate.runner import run
from crossresumebench_crewai_gate.analysis import analyze

results=ROOT/"results"
# Keep capability file if preflight already produced it, clean experimental outputs only.
for rel in ["artifacts","native_sources","native_targets","work"]:
    p=results/rel
    if p.exists(): shutil.rmtree(p)
    p.mkdir(parents=True,exist_ok=True)
for f in ["self_resume.csv","source_capture_results.csv","crewai_gate_runs.csv","CREWAI_REPAIRED_GATE.json","ANALYSIS_SUMMARY.md","CREWAI_REPAIR_PROBE.json"]:
    p=results/f
    if p.exists(): p.unlink()

probe=run_probe(results)
print(json.dumps(probe,indent=2,default=str))
if not probe["probe_pass"]:
    subprocess.run([sys.executable,str(ROOT/"scripts/export_diagnostics.py")],check=False)
    raise SystemExit("CrewAI repair probe FAILED. Diagnostic ZIP exported; full 12-row gate was not run.")

run(results)
verdict=analyze(results)
print(json.dumps(verdict,indent=2))
subprocess.run([sys.executable,str(ROOT/"scripts/export_crewai_gate.py")],check=True)
raise SystemExit(0 if verdict["crewai_repaired_gate_pass"] else 3)
