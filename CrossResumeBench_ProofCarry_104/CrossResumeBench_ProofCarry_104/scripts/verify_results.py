from __future__ import annotations
import json,pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; cfg=json.loads((ROOT/'config'/'experiment.json').read_text())
required=['semantic_runs.csv','security_runs.csv','ablation_runs.csv','native_runs.csv','native_family_gate.csv','native_self_resume.csv','native_source_captures.csv','performance_runs.csv']
for x in required:
    p=R/x; assert p.exists(),f'missing {x}'
sem=pd.read_csv(R/'semantic_runs.csv').fillna(0); assert len(sem)==104*5*6*10,f'unexpected semantic rows {len(sem)}'; pc=sem[sem.method=='proofcarry']; assert int(pc.technical_failure.sum())==0; assert int(pc.unsafe_violation.sum())==0
assert (pc[pc.condition.isin(['enough_evidence','runtime_binding_complete','irrelevant_noise'])].safe_completion==1).all(); assert (pc[pc.condition.isin(['missing_critical_fact','runtime_binding_missing'])].safe_rejection==1).all()
sec=pd.read_csv(R/'security_runs.csv').fillna(0); assert len(sec)==104*6*9*2,f'unexpected security rows {len(sec)}'; pcs=sec[sec.method=='proofcarry']; assert int(pcs.technical_failure.sum())==0 and int(pcs.unsafe.sum())==0; assert (pcs[pcs.attack!='valid_control'].outcome=='safe_rejection').all(); assert (pcs[pcs.attack=='valid_control'].outcome=='safe_completion').all()
abl=pd.read_csv(R/'ablation_runs.csv').fillna(0); assert len(abl)==104*6*4*7,f'unexpected ablation rows {len(abl)}'; assert int(abl.get('technical_failure',0).sum())==0
ng=pd.read_csv(R/'native_family_gate.csv').fillna(0); assert len(ng)==24 and int(ng['pass'].sum())==24,'native family gate not 24/24'
selfr=pd.read_csv(R/'native_self_resume.csv').fillna(0); srcc=pd.read_csv(R/'native_source_captures.csv').fillna(0); nat=pd.read_csv(R/'native_runs.csv').fillna(0); assert len(selfr)==312 and len(srcc)==312 and len(nat)==104*6*3; assert int(selfr.technical_failure.sum())==0 and int(srcc.technical_failure.sum())==0; pcn=nat[nat.method=='proofcarry']; assert int(pcn.technical_failure.sum())==0 and int(pcn.unsafe_violation.sum())==0
perf=pd.read_csv(R/'performance_runs.csv').fillna(0); expected=24*6*int(cfg['performance_repeats_default'])*2; assert len(perf)==expected,f'performance rows {len(perf)} != {expected}'
print('All preregistered structural and primary ProofCarry gates PASS')
