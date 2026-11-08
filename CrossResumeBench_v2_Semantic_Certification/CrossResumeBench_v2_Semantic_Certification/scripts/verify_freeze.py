from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def H(p): return hashlib.sha256(p.read_bytes()).hexdigest()
rec=json.loads((ROOT/'benchmark'/'FREEZE_RECORD.json').read_text())
mech=[ROOT/'src/crossresumebench_v2/mcc.py',ROOT/'schemas/mcc_v2.schema.json',ROOT/'src/crossresumebench_v2/certificates.py']; code=[ROOT/'src/crossresumebench_v2/evaluator.py',ROOT/'src/crossresumebench_v2/source_engine.py',ROOT/'src/crossresumebench_v2/target_engine.py',ROOT/'src/crossresumebench_v2/baselines/core.py',ROOT/'src/crossresumebench_v2/baselines/history_baseline.py',ROOT/'src/crossresumebench_v2/baselines/aaif_reference.py',ROOT/'src/crossresumebench_v2/baselines/caplease_reference.py',ROOT/'src/crossresumebench_v2/adapters/langgraph_adapter.py',ROOT/'src/crossresumebench_v2/adapters/crewai_adapter.py',ROOT/'src/crossresumebench_v2/adapters/maf_adapter.py']
mh=hashlib.sha256(''.join(H(p) for p in mech).encode()).hexdigest(); ch=hashlib.sha256(''.join(H(p) for p in code).encode()).hexdigest(); data=json.loads((ROOT/'benchmark'/'generated_suite.json').read_text()); sh=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()
errs=[]
if mh!=rec['mechanism_hash']: errs.append('mechanism hash mismatch')
if ch!=rec['evaluation_hash']: errs.append('evaluation hash mismatch')
if sh!=rec['suite_hash']: errs.append('suite hash mismatch')
if not rec.get('order_verified'): errs.append('mechanism-before-suite freeze order not verified')
print(json.dumps({"ok":not errs,"errors":errs,"mechanism":mh,"evaluation":ch,"suite":sh},indent=2)); sys.exit(1 if errs else 0)
