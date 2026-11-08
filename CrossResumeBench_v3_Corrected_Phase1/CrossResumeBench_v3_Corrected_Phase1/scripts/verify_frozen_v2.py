from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
manifest={}
for rel in ['frozen_v2/src/crossresumebench_v2/mcc.py','frozen_v2/src/crossresumebench_v2/certificates.py','frozen_v2/src/crossresumebench_v2/models.py','frozen_v2/schemas/mcc_v2.schema.json']:
    p=ROOT/rel; manifest[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
expected=json.loads((ROOT/'frozen_v2/PHASE1_FROZEN_HASHES.json').read_text())
ok=manifest==expected
print(json.dumps({"ok":ok,"actual":manifest,"expected":expected},indent=2))
if not ok: raise SystemExit(3)
