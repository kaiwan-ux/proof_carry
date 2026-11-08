from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parents[1]; out={}
for name in ['langgraph','crewai','maf']:
 p=subprocess.run([sys.executable,str(ROOT/'native_probes'/f'{name}_probe.py')],capture_output=True,text=True); (ROOT/'results'/'probes'/f'{name}.json').write_text(json.dumps({'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)); out[name]=p.returncode
print(out); raise SystemExit(1 if any(out.values()) else 0)
