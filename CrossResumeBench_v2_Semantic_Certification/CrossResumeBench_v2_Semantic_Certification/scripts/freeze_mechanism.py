from pathlib import Path
import hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[1]
def H(p): return hashlib.sha256(p.read_bytes()).hexdigest()
mech=[ROOT/'src/crossresumebench_v2/mcc.py',ROOT/'schemas/mcc_v2.schema.json',ROOT/'src/crossresumebench_v2/certificates.py']
code=[ROOT/'src/crossresumebench_v2/evaluator.py',ROOT/'src/crossresumebench_v2/source_engine.py',ROOT/'src/crossresumebench_v2/target_engine.py',ROOT/'src/crossresumebench_v2/baselines/core.py',ROOT/'src/crossresumebench_v2/baselines/history_baseline.py',ROOT/'src/crossresumebench_v2/baselines/aaif_reference.py',ROOT/'src/crossresumebench_v2/baselines/caplease_reference.py',ROOT/'src/crossresumebench_v2/adapters/langgraph_adapter.py',ROOT/'src/crossresumebench_v2/adapters/crewai_adapter.py',ROOT/'src/crossresumebench_v2/adapters/maf_adapter.py']
mh=hashlib.sha256(''.join(H(p) for p in mech).encode()).hexdigest(); ch=hashlib.sha256(''.join(H(p) for p in code).encode()).hexdigest()
(ROOT/'benchmark'/'FROZEN_MCC_V2_SHA256.txt').write_text(mh+'\n'); (ROOT/'benchmark'/'FROZEN_EVALUATION_CODE_SHA256.txt').write_text(ch+'\n')
record={"benchmark":"CrossResumeBench v2","mechanism_hash":mh,"evaluation_hash":ch,"mechanism_frozen_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"policy":"Generate/freeze hold-out suite only after this record exists. Never overwrite v2 hashes after observing results."}; (ROOT/'benchmark'/'MECHANISM_FREEZE_RECORD.json').write_text(json.dumps(record,indent=2)); print(json.dumps(record,indent=2))
