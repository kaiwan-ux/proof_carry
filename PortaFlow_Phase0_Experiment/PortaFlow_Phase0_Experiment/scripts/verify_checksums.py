from __future__ import annotations

import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
checksum=ROOT/"results"/"CHECKSUMS_SHA256.txt"
if not checksum.exists(): raise SystemExit("No checksum file. Run make_manifest.py first.")
failed=[]
for line in checksum.read_text().splitlines():
    if not line.strip(): continue
    expected, rel=line.split("  ",1)
    p=ROOT/rel
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual!=expected: failed.append(rel)
print("OK" if not failed else "FAILED: "+", ".join(failed))
raise SystemExit(1 if failed else 0)
