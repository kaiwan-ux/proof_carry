from pathlib import Path
import json,pandas as pd
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; cfg=json.loads((ROOT/'config/experiment.json').read_text()); errors=[]
# Stage A
p=R/'subset_workflow_results.csv'
if not p.exists(): errors.append('missing subset_workflow_results.csv')
else:
    a=pd.read_csv(p)
    if len(a)!=cfg['stage_a_expected_workflow_rows']: errors.append(f"stage A workflow rows {len(a)} != {cfg['stage_a_expected_workflow_rows']}")
s=R/'subset_summary.csv'
if not s.exists(): errors.append('missing subset_summary.csv')
else:
    q=pd.read_csv(s)
    if len(q)!=cfg['stage_a_expected_subset_rows']: errors.append(f"stage A subset rows {len(q)} != {cfg['stage_a_expected_subset_rows']}")
# Stage B
selp=R/'selected_native_conditions.json'
if not selp.exists(): errors.append('missing selected_native_conditions.json'); selected=[]
else: selected=json.loads(selp.read_text())
np=R/'native_confirmation.csv'
if not np.exists(): errors.append('missing native_confirmation.csv')
else:
    n=pd.read_csv(np); exp=cfg['native_cases_per_condition']*len(selected)
    if len(n)!=exp: errors.append(f'native rows {len(n)} != expected {exp}')
    if n.run_id.nunique()!=len(n): errors.append('native run IDs not unique')
    if int(n.technical_failure.sum())>0: errors.append(f'technical failures present: {int(n.technical_failure.sum())}')
sources=list((R/'native_sources').glob('*.json'))
if len(sources)!=cfg['source_capture_count']: errors.append(f"source captures {len(sources)} != {cfg['source_capture_count']}")
for name in ['langgraph','crewai','maf']:
    pp=R/'probes'/f'{name}.json'
    if not pp.exists(): errors.append(f'missing native probe: {name}')
    else:
        try:
            if json.loads(pp.read_text()).get('status')!='ok': errors.append(f'native probe failed: {name}')
        except Exception as e: errors.append(f'invalid probe {name}: {e}')
# anti-leak
for f in (R/'capsules').glob('*.json'):
    txt=f.read_text()
    for forbidden in ['"native_snapshot"','"latest_checkpoint"','"checkpoint_id"','"flow_id"']:
        if forbidden in txt: errors.append(f'native leakage in {f.name}: {forbidden}')
obj={'ok':not errors,'errors':errors,'selected_native_conditions':len(selected),'source_captures':len(sources)}
(R/'VERIFY_RESULTS.json').write_text(json.dumps(obj,indent=2)); print(json.dumps(obj,indent=2))
if errors: raise SystemExit(2)
