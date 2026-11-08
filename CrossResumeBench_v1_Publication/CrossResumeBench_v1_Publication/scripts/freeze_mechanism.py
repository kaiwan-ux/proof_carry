# DEVELOPMENT ONLY: do not run on the frozen v1 benchmark after observing results. Use only when creating a new version.
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
files=[ROOT/'src/crossresumebench/inference.py',ROOT/'src/crossresumebench/baselines/core.py',ROOT/'docs/FROZEN_MCC_SPEC.md']
h=hashlib.sha256()
for p in files: h.update(p.read_bytes())
digest=h.hexdigest(); (ROOT/'benchmark/FROZEN_MCC_SHA256.txt').write_text(digest+'\n',encoding='utf-8')
print('MCC SHA256',digest)
