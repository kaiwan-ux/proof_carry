from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'results/PHASE1_GATE.json'
if not p.exists(): raise SystemExit('Missing PHASE1_GATE.json')
g=json.loads(p.read_text())
if not g.get('go_for_full_v3'): raise SystemExit('PHASE 1 GATE DID NOT PASS. Do not proceed to full v3.')
print('PASS: Phase 1 gate allows full v3 design work.')
