from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]; r=ROOT/"results"; files=[]
for p in sorted(r.rglob("*")):
    if p.is_file() and p.name!="RESULT_MANIFEST_SHA256.json": files.append({"path":str(p.relative_to(r)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size})
(r/"RESULT_MANIFEST_SHA256.json").write_text(json.dumps({"files":files},indent=2),encoding="utf-8"); print(len(files))
