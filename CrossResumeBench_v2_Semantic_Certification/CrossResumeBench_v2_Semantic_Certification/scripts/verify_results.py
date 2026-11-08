from pathlib import Path
import csv,json,sys
ROOT=Path(__file__).resolve().parents[1]; cfg=json.loads((ROOT/'config'/'benchmark.json').read_text()); suite=json.loads((ROOT/'benchmark'/'generated_suite.json').read_text()); exp_sem=len(suite)*len(cfg['semantic_baselines']); canon=sum(1 for c in suite if c['variant']==1); exp_nat=canon*len(cfg['frameworks'])*(len(cfg['frameworks'])-1)*len(cfg['native_baselines']); errs=[]
def rows(p):
    with p.open(encoding='utf-8') as f:return list(csv.DictReader(f))
s=rows(ROOT/'results'/'semantic_runs.csv'); n=rows(ROOT/'results'/'native_runs.csv')
if len(s)!=exp_sem: errs.append(f'semantic rows {len(s)} != {exp_sem}')
if len(n)!=exp_nat: errs.append(f'native rows {len(n)} != {exp_nat}')
if len({r['run_id'] for r in s})!=len(s): errs.append('duplicate semantic run ids')
if len({r['run_id'] for r in n})!=len(n): errs.append('duplicate native run ids')
tech=json.loads((ROOT/'results'/'technical_failures.json').read_text())
if cfg.get('require_zero_technical_failures') and tech: errs.append(f'{len(tech)} technical failures')
# MCC payload conformance: no forbidden derived state and every MCC artifact can be schema-validated.
sys.path.insert(0,str(ROOT/'src')); from crossresumebench_v2.mcc import validate_mcc_payload
for p in (ROOT/'results'/'artifacts').glob('*.json'):
    d=json.loads(p.read_text()); tr=d.get('transfer',{}); 
    if isinstance(tr,dict) and tr.get('mcc_version')=='2.0':
        try: validate_mcc_payload(tr,ROOT)
        except Exception as e: errs.append(f'MCC schema failure {p.name}: {e}')
out={"ok":not errs,"errors":errs,"expected_semantic":exp_sem,"actual_semantic":len(s),"expected_native":exp_nat,"actual_native":len(n),"technical_failures":len(tech)}; (ROOT/'results'/'VERIFY_RESULTS.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2)); sys.exit(1 if errs else 0)
