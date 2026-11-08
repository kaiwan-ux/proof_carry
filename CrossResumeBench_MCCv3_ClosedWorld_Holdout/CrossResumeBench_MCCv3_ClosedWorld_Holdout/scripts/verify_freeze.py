import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((ROOT/'mechanism/MCCV3_FREEZE_RECORD.json').read_text())
for rel,h in r['files'].items():
    a=sh(ROOT/rel); assert a==h,(rel,a,h)
import json as J
suite=J.loads((ROOT/'benchmark/generated_holdout_suite.json').read_text()); body=J.dumps(suite,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode(); hs=hashlib.sha256(body).hexdigest(); exp=(ROOT/'benchmark/HOLDOUT_SUITE_SHA256.txt').read_text().strip(); assert hs==exp,(hs,exp)
print('FREEZE_OK',r['combined_sha256'],hs)

exp=json.loads((ROOT/'benchmark/EXPERIMENT_FREEZE_RECORD.json').read_text())
for rel,h in exp['files'].items():
    a=sh(ROOT/rel); assert a==h,(rel,a,h)
assert exp['mechanism_sha256']==r['combined_sha256']
assert exp['holdout_suite_sha256']==hs
print('EXPERIMENT_FREEZE_OK',exp['evaluation_code_combined_sha256'])
