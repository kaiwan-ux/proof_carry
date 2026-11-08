import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'PACKAGE_MANIFEST.json').read_text())
bad=[]
for x in manifest['files']:
    p=ROOT/x['path']
    if not p.exists(): bad.append((x['path'],'MISSING')); continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=x['sha256'] or p.stat().st_size!=x['bytes']: bad.append((x['path'],'MISMATCH'))
if bad: raise SystemExit('package integrity failure: '+repr(bad[:10]))
print('package manifest verified',len(manifest['files']),'files')
