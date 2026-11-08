import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sh(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
rec=json.loads((ROOT/'INFRAFIXA_RECORD.json').read_text(encoding='utf-8'))
# Scientific freeze must remain exactly equal to the original preregistration.
exp=json.loads((ROOT/'benchmark/EXPERIMENT_FREEZE_RECORD.json').read_text(encoding='utf-8'))
mech=json.loads((ROOT/'mechanism/MCCV3_FREEZE_RECORD.json').read_text(encoding='utf-8'))
assert exp['mechanism_sha256']==rec['scientific_freeze']['mechanism_sha256']==mech['combined_sha256']
assert exp['holdout_suite_sha256']==rec['scientific_freeze']['holdout_suite_sha256']
assert exp['evaluation_code_combined_sha256']==rec['scientific_freeze']['evaluation_code_combined_sha256']
for rel,h in rec['scientific_file_hashes'].items(): assert sh(rel)==h,(rel,sh(rel),h)
for rel,h in rec['infra_file_hashes'].items(): assert sh(rel)==h,(rel,sh(rel),h)
print('INFRAFIXA_OK',rec['infra_combined_sha256'])
