from pathlib import Path
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/"results"
out=ROOT/"CrossResumeBench_v3_Phase1_RevisionB_results.zip"
manifest={}
for p in sorted(RES.rglob("*")):
    if p.is_file() and p.name!=".gitkeep":
        manifest[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
(RES/"RESULT_MANIFEST_SHA256.json").write_text(json.dumps(manifest,indent=2,sort_keys=True),encoding="utf-8")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for p in sorted(RES.rglob("*")):
        if p.is_file() and p.name!=".gitkeep": z.write(p,p.relative_to(ROOT))
print(out)
