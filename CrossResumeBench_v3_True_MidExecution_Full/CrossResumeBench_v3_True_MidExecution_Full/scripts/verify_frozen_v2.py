from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]; frozen=ROOT/"frozen_v2"; expected=json.loads((frozen/"REVISIONC_FROZEN_HASHES.json").read_text(encoding="utf-8")); bad=[]
for rel,h in expected.items():
    p=frozen/rel; got=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "MISSING"
    if got!=h: bad.append({"file":rel,"expected":h,"actual":got})
print(json.dumps({"ok":not bad,"bad":bad},indent=2)); raise SystemExit(0 if not bad else 3)
