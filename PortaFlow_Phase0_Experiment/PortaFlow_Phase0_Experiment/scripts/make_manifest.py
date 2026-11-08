from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"


def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024), b""):
            h.update(b)
    return h.hexdigest()

files=[]
for p in sorted(R.rglob("*")):
    if p.is_file() and p.name not in {"MANIFEST.json","CHECKSUMS_SHA256.txt"}:
        files.append({"path":str(p.relative_to(ROOT)).replace('\\','/'),"bytes":p.stat().st_size,"sha256":sha(p)})
(R/"MANIFEST.json").write_text(json.dumps({"schema":"0.1","files":files}, indent=2), encoding="utf-8")
lines=[f"{x['sha256']}  {x['path']}" for x in files]
(R/"CHECKSUMS_SHA256.txt").write_text("\n".join(lines)+"\n", encoding="utf-8")
print(f"Manifested {len(files)} files")
