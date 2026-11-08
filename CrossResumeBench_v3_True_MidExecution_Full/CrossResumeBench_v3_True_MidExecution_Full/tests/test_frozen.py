from pathlib import Path
import json,hashlib
from crossresumebench_v3_full.frozen import FROZEN
def test_frozen_hashes():
    exp=json.loads((FROZEN/"REVISIONC_FROZEN_HASHES.json").read_text(encoding="utf-8"))
    for rel,h in exp.items(): assert hashlib.sha256((FROZEN/rel).read_bytes()).hexdigest()==h
