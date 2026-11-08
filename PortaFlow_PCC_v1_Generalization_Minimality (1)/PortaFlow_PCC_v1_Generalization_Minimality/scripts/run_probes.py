import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; out=ROOT/"results"/"probes"; out.mkdir(parents=True,exist_ok=True)
env=dict(os.environ); env["PYTHONUTF8"]="1"; env["PYTHONIOENCODING"]="utf-8"
for name in ["langgraph","crewai","maf"]:
    p=subprocess.run([sys.executable,str(ROOT/"native_probes"/f"{name}_probe.py")],capture_output=True,text=True,env=env)
    obj={"framework":name,"returncode":p.returncode,"status":"ok" if p.returncode==0 else "failed","stdout":p.stdout,"stderr":p.stderr}
    (out/f"{name}.json").write_text(json.dumps(obj,indent=2),encoding="utf-8")
    print(name,obj["status"])
