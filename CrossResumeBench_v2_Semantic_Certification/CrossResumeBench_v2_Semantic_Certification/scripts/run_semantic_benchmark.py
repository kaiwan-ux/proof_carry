from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from crossresumebench_v2.models import CaseSpec
from crossresumebench_v2.semantic_runner import run_semantic
cfg=json.loads((ROOT/'config'/'benchmark.json').read_text()); cases=[CaseSpec.from_dict(x) for x in json.loads((ROOT/'benchmark'/'generated_suite.json').read_text())]; rows=run_semantic(cases,cfg['semantic_baselines'],ROOT); print('semantic rows',len(rows))
