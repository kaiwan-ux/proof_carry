from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parents[1]; out=ROOT/'results/probes'; out.mkdir(parents=True,exist_ok=True); summary=[]
for p in sorted((ROOT/'native_probes').glob('*.py')):
    r=subprocess.run([sys.executable,str(p)],capture_output=True,text=True); rec={'probe':p.name,'returncode':r.returncode,'stdout':r.stdout.strip(),'stderr':r.stderr.strip()}; summary.append(rec); (out/(p.stem+'.json')).write_text(json.dumps(rec,indent=2),encoding='utf-8')
(ROOT/'results/PROBE_SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8'); print(json.dumps(summary,indent=2))
