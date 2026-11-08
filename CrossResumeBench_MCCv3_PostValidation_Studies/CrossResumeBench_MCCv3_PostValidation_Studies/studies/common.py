from __future__ import annotations
import hashlib, json, os, platform, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
for _p in [ROOT, ROOT/'src', ROOT/'frozen_v2'/'src']:
    if str(_p) not in sys.path: sys.path.insert(0,str(_p))
INPUT=ROOT/'inputs'/'passed_holdout'

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def verify_passed_holdout_inputs()->dict:
    rec=json.loads((INPUT/'PASSED_HOLDOUT_INPUT_SHA256.json').read_text(encoding='utf-8'))
    bad=[]
    for name,want in rec['files'].items():
        p=INPUT/name
        if not p.exists(): bad.append({'file':name,'reason':'missing'}); continue
        got=sha256_file(p)
        if got!=want: bad.append({'file':name,'reason':'hash_mismatch','expected':want,'actual':got})
    if bad: raise RuntimeError(f'Passed-holdout input integrity failure: {bad}')
    verdict=json.loads((INPUT/'RESEARCH_VERDICT.json').read_text(encoding='utf-8'))
    if not verdict.get('gate',{}).get('go_for_mccv3_claims',False):
        raise RuntimeError('Input RESEARCH_VERDICT.json is not a passed MCC v3 holdout verdict')
    return {'verified':True,'file_count':len(rec['files']),'verdict_gate':True}

def environment_metadata():
    return {
        'python':sys.version,
        'platform':platform.platform(),
        'processor':platform.processor(),
        'machine':platform.machine(),
        'cpu_count':os.cpu_count(),
    }
