from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from crossresumebench_v2.generator import generate_suite
cfg=json.loads((ROOT/'config'/'benchmark.json').read_text()); cases=generate_suite(cfg['seed'],cfg['variants_per_family']); data=[c.to_dict() for c in cases]
(ROOT/'benchmark'/'generated_suite.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
h=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest(); (ROOT/'benchmark'/'FROZEN_SUITE_SHA256.txt').write_text(h+'\n'); print(len(data),h)
