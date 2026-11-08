
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
record=json.loads((ROOT/"frozen_v2/REVISIONC_FROZEN_HASHES.json").read_text(encoding="utf-8"))
bad=[]
for rel,exp in record.items():
    got=hashlib.sha256((ROOT/"frozen_v2"/rel).read_bytes()).hexdigest()
    print(rel,got,"PASS" if got==exp else "FAIL")
    if got!=exp: bad.append(rel)
if bad: raise SystemExit(f"Frozen MCC v2 changed: {bad}")
print("PASS: frozen MCC v2 byte integrity")
