from pathlib import Path
import csv, json, sys
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'; cfg=json.loads((ROOT/'config'/'experiment.json').read_text())
errors=[]
p=RES/'pcc_ablation_runs.csv'
if not p.exists(): errors.append('missing pcc_ablation_runs.csv')
else:
    rows=list(csv.DictReader(p.open(encoding='utf-8')))
    if len(rows)!=cfg['expected_cross_runtime_rows']: errors.append(f'expected {cfg["expected_cross_runtime_rows"]} rows, got {len(rows)}')
    ids=[r['run_id'] for r in rows]
    if len(ids)!=len(set(ids)): errors.append('duplicate run IDs')
    technical=sum(int(r['technical_failure']) for r in rows)
    if technical: errors.append(f'{technical} technical-failure rows present')
# Check source capture count
src=list((RES/'native_sources').glob('*.json'))
if len(src)!=cfg['expected_native_source_captures']: errors.append(f'expected {cfg["expected_native_source_captures"]} native source captures, got {len(src)}')
# Anti-cheating audit
for cp in (RES/'capsules').glob('*.json'):
    txt=cp.read_text(encoding='utf-8')
    if 'source_native_snapshot' in txt: errors.append(f'native checkpoint leak in {cp.name}')
report={'ok':not errors,'errors':errors,'source_capture_count':len(src)}
(RES/'VERIFY_RESULTS.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
if errors: raise SystemExit(3)
