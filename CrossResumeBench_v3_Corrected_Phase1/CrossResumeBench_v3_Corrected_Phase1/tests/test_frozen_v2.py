import json,hashlib,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def test_frozen_hashes():
    exp=json.loads((ROOT/'frozen_v2/PHASE1_FROZEN_HASHES.json').read_text())
    for rel,h in exp.items(): assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h
