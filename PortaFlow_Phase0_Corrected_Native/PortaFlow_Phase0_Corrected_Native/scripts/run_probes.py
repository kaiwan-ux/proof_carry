from pathlib import Path
import json, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1]; out=ROOT/"results/probes"; out.mkdir(parents=True,exist_ok=True)
probes={"langgraph":ROOT/"native_probes/langgraph_probe.py","crewai":ROOT/"native_probes/crewai_probe.py","maf":ROOT/"native_probes/maf_probe.py"}
summary=[]
for name,path in probes.items():
    t=time.time(); env=dict(__import__('os').environ); env["PYTHONUTF8"]="1"; env["PYTHONIOENCODING"]="utf-8"
    p=subprocess.run([sys.executable,str(path)],capture_output=True,text=True,encoding="utf-8",errors="replace",env=env,timeout=90)
    rec={"framework":name,"status":"ok" if p.returncode==0 else "technical_failure","duration_seconds":round(time.time()-t,3),"stderr":p.stderr[-8000:]}
    if p.returncode==0:
        lines=[x for x in p.stdout.splitlines() if x.strip()]
        try: payload=json.loads(lines[-1]); (out/f"{name}.json").write_text(json.dumps(payload,indent=2,default=str),encoding="utf-8")
        except Exception as e: rec["status"]="technical_failure"; rec["stderr"]+=f"\nJSON parse: {e}\nstdout={p.stdout[-8000:]}"
    summary.append(rec)
(ROOT/"results/probe_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps(summary,indent=2))
