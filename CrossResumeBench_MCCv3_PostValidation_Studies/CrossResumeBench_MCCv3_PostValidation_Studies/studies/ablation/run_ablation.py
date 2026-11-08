from __future__ import annotations
import argparse, csv, json, shutil, tempfile, hashlib
from pathlib import Path
from studies.common import ROOT, verify_passed_holdout_inputs
from studies.ablation.ablation_engine import ABLATIONS, resolve_ablation
from crossresumebench_mccv3.cases import CASES
from crossresumebench_mccv3.models import NativePause
from crossresumebench_mccv3.evidence import generate
from crossresumebench_mccv3.semantics import expected_source, expected_final, apply_source_pause, apply_plan
from crossresumebench_mccv3.store import SemanticStore
from crossresumebench_mccv3.evaluator import evaluate
from mechanism.mcc_v3 import build_mcc_v3
from crossresumebench_mccv3.baselines import _workflow_hash
from crossresumebench_mccv3.legacy import v2_case_spec

FRAMEWORKS=['langgraph','crewai','maf']
def fake_native(framework,case):
    return NativePause(framework,case.case_id,f'ablation://{framework}/{case.case_id}','mechanism_replay',['continuation'],{'phase':'mid_execution'},{'framework':framework,'study':'post_validation_ablation'},expected_source(case))
def sha(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def write_csv(path,rows):
    rows=list(rows); keys=[]
    for r in rows:
        for k in r:
            if k not in keys:keys.append(k)
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def run(out_dir:Path):
    verify_passed_holdout_inputs(); out_dir.mkdir(parents=True,exist_ok=True); rows=[]
    for case in CASES:
        wh=_workflow_hash(v2_case_spec(case)); exp=expected_final(case)
        for variant in case.variants:
            for s in FRAMEWORKS:
                cap=generate(case,fake_native(s,case),variant)
                for t in FRAMEWORKS:
                    if s==t:continue
                    base=build_mcc_v3(cap,t,wh,case.continuation_contract,ROOT/'mechanism')
                    for abl in ABLATIONS:
                        payload,plan,reject,report=resolve_ablation(base,case,abl)
                        if plan is None:
                            rows.append({'ablation':abl,'source':s,'target':t,'case_id':case.case_id,'family':case.family,'evidence_variant':variant,'safe_completion':0,'safe_rejection':1,'unsafe':0,'reject_reason':reject,'payload_bytes':len(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()),'payload_sha256':sha(payload)})
                        else:
                            with tempfile.TemporaryDirectory() as td:
                                p=Path(td)/'s.json'; apply_source_pause(case,p); actual=apply_plan(plan,p); safe,fail=evaluate(exp,actual)
                            rows.append({'ablation':abl,'source':s,'target':t,'case_id':case.case_id,'family':case.family,'evidence_variant':variant,'safe_completion':int(safe),'safe_rejection':0,'unsafe':int(not safe),'reject_reason':'','failure_types':json.dumps(fail),'payload_bytes':len(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()),'payload_sha256':sha(payload)})
    write_csv(out_dir/'ablation_runs.csv',rows)
    import pandas as pd
    df=pd.DataFrame(rows)
    summ=df.groupby('ablation')[['safe_completion','safe_rejection','unsafe']].sum(); summ['rows']=df.groupby('ablation').size(); summ.to_csv(out_dir/'ablation_summary.csv')
    fam=df.groupby(['ablation','family'])[['safe_completion','safe_rejection','unsafe']].sum();fam.to_csv(out_dir/'ablation_by_family.csv')
    var=df.groupby(['ablation','evidence_variant'])[['safe_completion','safe_rejection','unsafe']].sum();var.to_csv(out_dir/'ablation_by_evidence.csv')
    lines=['# MCC v3 Post-validation Ablation','', '> **Interpretation:** explanatory post-validation analysis on the already-seen holdout semantics. It is not a second independent validation set.','', '## Summary','',summ.to_markdown(),'','## Ablation definitions','- `minus_closed_world_gate`: allows fixed-default continuation when the only missing proof is a required fact.','- `minus_integrity_verification`: accepts certificate contents despite bad evidence hashes.','- `minus_identity_binding`: removes semantic identity-binding certificates.','- `minus_complete_snapshots`: removes complete positive/negative snapshot evidence.','- `history_only`: removes all certificates.','- `certificates_only`: removes portable history.','', 'The full mechanism remains frozen and untouched; ablations are implemented in separate study code.']
    (out_dir/'ABLATION_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return {'rows':len(df),'ablations':len(ABLATIONS),'base_mcc_rows':len(df)//len(ABLATIONS)}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(ROOT/'results'/'ablation'));a=ap.parse_args();print(json.dumps(run(Path(a.out)),indent=2))
