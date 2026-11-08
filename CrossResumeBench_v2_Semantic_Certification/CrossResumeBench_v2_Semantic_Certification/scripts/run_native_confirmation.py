from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from crossresumebench_v2.models import CaseSpec
from crossresumebench_v2.native_runner import run_native
cfg=json.loads((ROOT/'config'/'benchmark.json').read_text()); allc=[CaseSpec.from_dict(x) for x in json.loads((ROOT/'benchmark'/'generated_suite.json').read_text())]; cases=[c for c in allc if c.variant==1]; rows=run_native(cases,cfg['frameworks'],cfg['native_baselines'],ROOT); print('native rows',len(rows))
