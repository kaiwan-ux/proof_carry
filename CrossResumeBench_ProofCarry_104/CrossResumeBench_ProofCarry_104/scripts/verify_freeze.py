import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'benchmark'/'generated_suite.json'; got=hashlib.sha256(json.dumps(json.loads(p.read_text()),sort_keys=True,separators=(',',':')).encode()).hexdigest(); exp=(ROOT/'benchmark'/'SUITE_SHA256.txt').read_text().strip(); assert got==exp,(got,exp); print('suite SHA verified',got)
rec=json.loads((ROOT/'mechanism'/'METHOD_BUNDLE_FILES.json').read_text()); parts=[]
for rel in rec['files']:
    h=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(); assert h==rec['component_hashes'][rel],f'component hash mismatch {rel}'; parts.append(rel+'='+h)
bundle=hashlib.sha256('\n'.join(parts).encode()).hexdigest(); expb=(ROOT/'mechanism'/'MECHANISM_SHA256.txt').read_text().strip(); assert bundle==expb==rec['bundle_sha256'],(bundle,expb); print('mechanism bundle SHA verified',bundle)
