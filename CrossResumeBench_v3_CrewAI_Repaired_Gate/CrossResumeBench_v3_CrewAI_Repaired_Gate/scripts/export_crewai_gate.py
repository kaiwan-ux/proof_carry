
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"CrossResumeBench_v3_CrewAI_Repaired_Gate_results.zip"
include=["results","README.md","RESEARCH_PROTOCOL.md","config/crewai_gate.json","frozen_v2/REVISIONC_FROZEN_HASHES.json","requirements.txt"]
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for rel in include:
        p=ROOT/rel
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file(): z.write(f,f.relative_to(ROOT))
        elif p.exists(): z.write(p,p.relative_to(ROOT))
print(out)
