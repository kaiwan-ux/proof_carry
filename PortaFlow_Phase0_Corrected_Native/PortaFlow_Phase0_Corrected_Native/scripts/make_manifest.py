from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/"results"
items=[]
for p in sorted(RES.rglob('*')):
    if p.is_file() and p.name not in {"MANIFEST.json","CHECKSUMS_SHA256.txt"}:
        b=p.read_bytes(); items.append({"path":str(p.relative_to(ROOT)).replace('\\','/'),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()})
(RES/"MANIFEST.json").write_text(json.dumps({"files":items},indent=2),encoding='utf-8')
(RES/"CHECKSUMS_SHA256.txt").write_text(''.join(f"{x['sha256']}  {x['path']}\n" for x in items),encoding='utf-8')
print(f"Manifested {len(items)} files")
