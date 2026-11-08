from pathlib import Path
import json
from crossresumebench.models import CaseSpec
from crossresumebench.semantic_runner import run_suite
ROOT=Path(__file__).resolve().parents[1]; cfg=json.loads((ROOT/'config/benchmark.json').read_text()); cases=[CaseSpec(**x) for x in json.loads((ROOT/'benchmark/generated_suite.json').read_text())]
rows=run_suite(cases,cfg['baselines'],ROOT/'results/semantic'); print('semantic rows',len(rows))
