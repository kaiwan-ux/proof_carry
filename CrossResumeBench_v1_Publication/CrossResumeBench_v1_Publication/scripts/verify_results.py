from pathlib import Path
import json,pandas as pd,hashlib
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; errors=[]
sem=R/'semantic_runs.csv'
if not sem.exists(): errors.append('missing semantic_runs.csv')
else:
    d=pd.read_csv(sem); exp=60*11
    if len(d)!=exp: errors.append(f'semantic rows {len(d)} != {exp}')
    if d.run_id.nunique()!=len(d): errors.append('duplicate semantic run IDs')
nat=R/'native_runs.csv'
if nat.exists():
    d=pd.read_csv(nat); exp=3*2*12*7
    if len(d)!=exp: errors.append(f'native rows {len(d)} != {exp}')
    if d.run_id.nunique()!=len(d): errors.append('duplicate native run IDs')
    if int(d.technical_failure.sum())!=0: errors.append(f'native technical failures: {int(d.technical_failure.sum())}')
tf=R/'technical_failures.json'
if tf.exists():
    try:
        items=json.loads(tf.read_text())
        if items: errors.append(f'technical_failures.json contains {len(items)} entries')
    except Exception as e: errors.append(f'cannot read technical_failures.json: {e}')

# Freeze hash integrity
for filename,paths in [('FROZEN_MCC_SHA256.txt',[ROOT/'src/crossresumebench/inference.py',ROOT/'src/crossresumebench/baselines/core.py',ROOT/'docs/FROZEN_MCC_SPEC.md'])]:
    hp=ROOT/'benchmark'/filename
    if hp.exists():
        h=hashlib.sha256(); [h.update(p.read_bytes()) for p in paths]
        if h.hexdigest()!=hp.read_text().strip(): errors.append('frozen MCC hash mismatch')

# Benchmark-code freeze integrity
bench_files=[ROOT/'src/crossresumebench/generator.py',ROOT/'src/crossresumebench/semantics.py',ROOT/'src/crossresumebench/evaluator.py',ROOT/'src/crossresumebench/models.py',ROOT/'benchmark/generated_suite.json']
hb=hashlib.sha256(); [hb.update(p.read_bytes()) for p in bench_files]
if hb.hexdigest()!=(ROOT/'benchmark/FROZEN_BENCHMARK_CODE_SHA256.txt').read_text().strip(): errors.append('frozen benchmark code hash mismatch')

res={'ok':not errors,'errors':errors}; (R/'VERIFY_RESULTS.json').write_text(json.dumps(res,indent=2),encoding='utf-8'); print(json.dumps(res,indent=2)); raise SystemExit(0 if not errors else 1)
