from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def digest(paths):
    h=hashlib.sha256()
    for p in paths: h.update(p.read_bytes())
    return h.hexdigest()
mech=digest([ROOT/'src/crossresumebench/inference.py',ROOT/'src/crossresumebench/baselines/core.py',ROOT/'docs/FROZEN_MCC_SPEC.md'])
suite=hashlib.sha256((ROOT/'benchmark/generated_suite.json').read_bytes()).hexdigest()
bench=digest([ROOT/'src/crossresumebench/generator.py',ROOT/'src/crossresumebench/semantics.py',ROOT/'src/crossresumebench/evaluator.py',ROOT/'src/crossresumebench/models.py',ROOT/'benchmark/generated_suite.json'])
expected={'mcc':(ROOT/'benchmark/FROZEN_MCC_SHA256.txt').read_text().strip(),'suite':(ROOT/'benchmark/FROZEN_SUITE_SHA256.txt').read_text().strip(),'benchmark':(ROOT/'benchmark/FROZEN_BENCHMARK_CODE_SHA256.txt').read_text().strip()}
actual={'mcc':mech,'suite':suite,'benchmark':bench}
errors=[f'{k} hash mismatch' for k in actual if actual[k]!=expected[k]]
print(json.dumps({'ok':not errors,'expected':expected,'actual':actual,'errors':errors},indent=2))
raise SystemExit(0 if not errors else 1)
