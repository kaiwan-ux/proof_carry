from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
files=[
    "src/crossresumebench_v2/mcc.py",
    "src/crossresumebench_v2/certificates.py",
    "src/crossresumebench_v2/models.py",
    "schemas/mcc_v2.schema.json",
]
record=json.loads((ROOT/"frozen_v2/REVISIONC_FROZEN_HASHES.json").read_text(encoding="utf-8"))
bad=[]
for rel in files:
    got=hashlib.sha256((ROOT/"frozen_v2"/rel).read_bytes()).hexdigest(); exp=record[rel]
    print(rel,got,"PASS" if got==exp else "FAIL")
    if got!=exp: bad.append(rel)
if bad: raise SystemExit(f"Frozen MCC v2 changed: {bad}")
print("PASS: frozen MCC v2 integrity")
