from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/"results"; items=[]
for p in sorted(R.rglob("*")):
    if p.is_file() and p.name not in {"MANIFEST.json","CHECKSUMS_SHA256.txt"}:
        b=p.read_bytes(); items.append({"path":str(p.relative_to(R)),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()})
(R/"MANIFEST.json").write_text(json.dumps({"files":items},indent=2),encoding="utf-8")
(R/"CHECKSUMS_SHA256.txt").write_text("\n".join(f"{x['sha256']}  {x['path']}" for x in items)+"\n",encoding="utf-8")
print(f"Manifested {len(items)} files.")
