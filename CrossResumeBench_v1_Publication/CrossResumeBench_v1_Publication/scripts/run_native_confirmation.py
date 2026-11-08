from pathlib import Path
import json
from crossresumebench.models import CaseSpec
from crossresumebench.native_runner import run_native
ROOT=Path(__file__).resolve().parents[1]; cfg=json.loads((ROOT/'config/benchmark.json').read_text()); allcases=[CaseSpec(**x) for x in json.loads((ROOT/'benchmark/generated_suite.json').read_text())]
# One frozen variant per family for native confirmation; semantic suite remains the larger generalization test.
seen=set(); cases=[]
for c in allcases:
    if c.family not in seen: cases.append(c); seen.add(c.family)
rows=run_native(cases,cfg['frameworks'],cfg['native_confirmation']['baselines'],ROOT); print('native rows',len(rows))
