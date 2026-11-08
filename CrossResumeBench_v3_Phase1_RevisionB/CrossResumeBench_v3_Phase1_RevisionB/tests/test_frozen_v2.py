from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def test_frozen_hashes():
    rec=json.loads((ROOT/"frozen_v2/REVISIONB_FROZEN_HASHES.json").read_text())
    for rel,exp in rec.items(): assert hashlib.sha256((ROOT/"frozen_v2"/rel).read_bytes()).hexdigest()==exp
