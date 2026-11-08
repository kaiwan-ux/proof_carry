from __future__ import annotations
import argparse, json
from pathlib import Path
from proofcarry.utils import RUNTIME_PAIRS, sha256_obj
from proofcarry.contracts import contract_from_case
from proofcarry.evidence import build_evidence
from proofcarry.engine import ProofCarryEngine
from proofcarry.baselines import BASELINES
from proofcarry.evaluate import expected_for_variant, classify
from experiments.common import load_cases, make_writer, base_meta

METHODS=['proofcarry','mcc_v2_frozen','history_only','aaif_reference','caplease_reference','aaif_plus_caplease_reference','always_reject','oracle']
FIELDS=['run_id','timestamp_utc','experiment','config_sha256','seed','case_id','workflow_family','source_runtime','target_runtime','method','evidence_variant','contract','required_facts','available_evidence','expected_decision','actual_decision','safe_completion','safe_rejection','unsafe_violation','outcome_class','reason','safe_plan','actual_plan']

def run(root: Path, out: Path, run_id: str, seed: int=20260830):
    cfg=json.loads((root/'configs/expanded120.json').read_text())
    cfgsha=sha256_obj(cfg); cases=load_cases(root)
    fh,w=make_writer(out,FIELDS)
    eng=ProofCarryEngine()
    try:
        for case in cases:
            contract=contract_from_case(case)
            for source,target in RUNTIME_PAIRS:
                for variant in cfg['variants']:
                    ev=build_evidence(case,source,target,variant)
                    expected=expected_for_variant(variant)
                    for method in METHODS:
                        if method=='proofcarry': res=eng.resolve(case,contract,ev)
                        else: res=BASELINES[method](case,contract,ev)
                        classification_expected = 'CONTINUE' if method == 'oracle' else expected
                        flags=classify(case,res,classification_expected)
                        row=base_meta(run_id,'expanded120_semantic',cfgsha,seed,case,source,target)
                        row.update({
                            'method':method,'evidence_variant':variant,'contract':json.dumps(contract,sort_keys=True),
                            'required_facts':json.dumps(contract['required_facts'],sort_keys=True),
                            'available_evidence':json.dumps({'history':ev['history'],'certified_facts':[{'subject':c.get('subject'),'value':c.get('value'),'issuer':c.get('issuer'),'digest':c.get('digest')} for c in ev['certificates']], 'snapshots':ev['snapshots'], 'identity_mapping':ev['identity_mapping'], 'noise':ev.get('noise',{})},sort_keys=True),
                            'expected_decision':expected,'actual_decision':res.decision.value,'reason':res.reason or '',
                            'safe_plan':case['safe_plan'],'actual_plan':res.plan or '', 'outcome_class':('UNSAFE' if flags['unsafe_violation'] else ('SAFE_COMPLETION' if flags['safe_completion'] else 'SAFE_REJECTION')), **flags})
                        w.writerow(row)
    finally: fh.close()
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--out',required=True); ap.add_argument('--run-id',required=True); ap.add_argument('--seed',type=int,default=20260830); a=ap.parse_args()
    run(Path(a.root),Path(a.out),a.run_id,a.seed)
