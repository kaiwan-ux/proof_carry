from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
rec=json.loads((ROOT/'INPUT_FREEZE_SHA256.json').read_text())
bad=[]
for rel,want in rec['files'].items():
    p=ROOT/rel
    got=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else 'MISSING'
    if got!=want: bad.append((rel,want,got))
if bad:
    print('INPUT FREEZE FAIL')
    for x in bad: print(x)
    sys.exit(2)
print(f"INPUT FREEZE PASS ({len(rec['files'])} files)")
