from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from proofcarry.utils import RUNTIME_PAIRS, sha256_obj
from proofcarry.contracts import contract_from_case
from proofcarry.evidence import build_evidence
from proofcarry.engine import ProofCarryEngine
from proofcarry.runtime_repr import identity_mapping, build_runtime_state
from proofcarry.evaluate import classify
from experiments.common import load_cases, make_writer, base_meta

FIELDS=['run_id','timestamp_utc','experiment','config_sha256','seed','case_id','workflow_family','source_runtime','target_runtime','mapping_mode','source_native_state','target_native_identity','expected_decision','actual_decision','safe_completion','safe_rejection','unsafe_violation','outcome_class','reason']

def run(root,out,run_id,seed=20260830):
    cfg={'mapping_modes':['correct','missing','wrong','ambiguous']}; cfgsha=sha256_obj(cfg)
    fh,w=make_writer(out,FIELDS); eng=ProofCarryEngine()
    try:
        for case in load_cases(root):
            contract=contract_from_case(case)
            for source,target in RUNTIME_PAIRS:
                for mode in cfg['mapping_modes']:
                    ev=build_evidence(case,source,target,'enough')
                    ev['identity_mapping']=identity_mapping(case,source,target,mode)
                    expected='CONTINUE' if mode=='correct' else 'REJECT'
                    res=eng.resolve(case,contract,ev)
                    flags=classify(case,res,expected)
                    row=base_meta(run_id,'runtime_identity_semantic',cfgsha,seed,case,source,target)
                    row.update({'mapping_mode':mode,'source_native_state':json.dumps(build_runtime_state(case,source),sort_keys=True),'target_native_identity':json.dumps(ev['identity_mapping'],sort_keys=True),'expected_decision':expected,'actual_decision':res.decision.value,'reason':res.reason or '','outcome_class':('UNSAFE' if flags['unsafe_violation'] else ('SAFE_COMPLETION' if flags['safe_completion'] else 'SAFE_REJECTION')),**flags})
                    w.writerow(row)
    finally: fh.close()
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--out',required=True); ap.add_argument('--run-id',required=True); a=ap.parse_args(); run(Path(a.root),Path(a.out),a.run_id)
