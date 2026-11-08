
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"CrossResumeBench_v3_CrewAI_Repaired_Gate_diagnostics.zip"
for rel in ["results/CREWAI_REPAIR_PROBE.json","results/capabilities.json","README.md","requirements.txt"]:
    pass
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for rel in ["results/CREWAI_REPAIR_PROBE.json","results/capabilities.json","README.md","RESEARCH_PROTOCOL.md","requirements.txt"]:
        p=ROOT/rel
        if p.exists(): z.write(p,p.relative_to(ROOT))
    work=ROOT/"results/work/probe"
    if work.exists():
        for f in sorted(work.rglob("*")):
            if f.is_file(): z.write(f,f.relative_to(ROOT))
print(out)
