from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"native"; OUT.mkdir(parents=True,exist_ok=True)
probes={
    "langgraph":ROOT/"native_probes"/"langgraph"/"probe.py",
    "crewai":ROOT/"native_probes"/"crewai"/"probe.py",
    "maf":ROOT/"native_probes"/"maf"/"probe.py",
}
rows=[]
for name,path in probes.items():
    started=time.time(); status="ok"; err=""; payload=None; stdout=""; stderr=""
    try:
        p=subprocess.run([sys.executable,str(path)],cwd=ROOT,text=True,capture_output=True,timeout=120)
        stdout=p.stdout; stderr=p.stderr
        if p.returncode!=0:
            status="technical_failure"; err=f"exit={p.returncode}: {stderr[-4000:]}"
        else:
            # Last non-empty line must be JSON; preceding lines are framework logs.
            lines=[x for x in stdout.splitlines() if x.strip()]
            payload=json.loads(lines[-1]) if lines else None
    except Exception as e:
        status="technical_failure"; err=f"{type(e).__name__}: {e}"
    artifact={"framework":name,"status":status,"duration_seconds":round(time.time()-started,3),"payload":payload,"stdout":stdout,"stderr":stderr,"error":err}
    (OUT/f"{name}.json").write_text(json.dumps(artifact,indent=2,default=str),encoding="utf-8")
    rows.append({"framework":name,"status":status,"duration_seconds":artifact["duration_seconds"],"error":err})

with (ROOT/"results"/"native_probe_summary.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("Native probes complete")
for r in rows: print(f"{r['framework']}: {r['status']}")
