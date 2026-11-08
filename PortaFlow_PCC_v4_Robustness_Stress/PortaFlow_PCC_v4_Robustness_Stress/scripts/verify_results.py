from pathlib import Path
import json,pandas as pd
from portaflow_robust.benchmark import SCENARIOS
from portaflow_robust.conditions import FROZEN_CONDITIONS
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; errs=[]; N=pd.read_csv(R/'native_confirmation.csv')
expected=len(SCENARIOS)*6*len(FROZEN_CONDITIONS)
if len(N)!=expected:errs.append(f'expected {expected} native rows, got {len(N)}')
if N.run_id.nunique()!=len(N):errs.append('duplicate run IDs')
if N.technical_failure.sum()!=0:errs.append(f'technical failures={int(N.technical_failure.sum())}')
if len(list((R/'native_sources').glob('*.json')))!=len(SCENARIOS)*3:errs.append(f'expected {len(SCENARIOS)*3} native source captures')
for p in (R/'capsules').glob('*.json'):
    s=p.read_text(encoding='utf-8')
    for bad in ['"native_snapshot"','"checkpoint_id"','"latest_checkpoint"','"flow_id"']:
        if bad in s:errs.append(f'native checkpoint leak {bad} in {p.name}');break
out={'ok':not errs,'errors':errs,'native_rows':len(N),'expected_rows':expected,'unique_run_ids':N.run_id.nunique(),'technical_failures':int(N.technical_failure.sum()),'source_captures':len(list((R/'native_sources').glob('*.json')))}
(R/'VERIFY_RESULTS.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
if errs:raise SystemExit(2)
