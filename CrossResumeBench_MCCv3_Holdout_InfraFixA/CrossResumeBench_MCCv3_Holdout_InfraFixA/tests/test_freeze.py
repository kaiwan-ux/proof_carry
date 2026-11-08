import json,hashlib
from pathlib import Path
def test_freeze():
    root=Path(__file__).resolve().parents[1]; r=json.loads((root/'mechanism/MCCV3_FREEZE_RECORD.json').read_text())
    for rel,h in r['files'].items(): assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==h
