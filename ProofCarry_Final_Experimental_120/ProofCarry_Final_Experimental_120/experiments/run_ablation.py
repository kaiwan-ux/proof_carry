from __future__ import annotations
import argparse, copy, json
from pathlib import Path
from proofcarry.utils import RUNTIME_PAIRS, sha256_obj
from proofcarry.contracts import contract_from_case
from proofcarry.evidence import build_evidence
from proofcarry.engine import ProofCarryEngine
from proofcarry.security import make_attack
from proofcarry.evaluate import classify
from experiments.common import load_cases, make_writer, base_meta

FIELDS=['run_id','timestamp_utc','experiment','config_sha256','seed','case_id','workflow_family','source_runtime','target_runtime','ablation','challenge','expected_decision','actual_decision','safe_completion','safe_rejection','unsafe_violation','outcome_class','reason']
ENGINES={
 'full':{},
 'minus_closed_world':{'closed_world':False},
 'minus_authentication':{'authentication':False},
 'minus_identity_binding':{'identity_binding':False},
 'minus_complete_snapshot':{'complete_snapshot':False},
 'minus_dependency_reasoning':{'dependency_reasoning':False},
 'minus_certificate_verification':{'certificate_verification':False},
}

def run(root,out,run_id,seed=20260830):
    cfg=json.loads((root/'configs/ablation.json').read_text()); cfgsha=sha256_obj(cfg)
    fh,w=make_writer(out,FIELDS)
    try:
      for case in load_cases(root):
        contract=contract_from_case(case)
        for source,target in RUNTIME_PAIRS:
          for challenge in cfg['challenge_variants']:
            if challenge=='tampered_certificate':
                ev=make_attack(case,source,target,'rehashed_forgery'); expected='REJECT'
            else:
                ev=build_evidence(case,source,target,challenge if challenge!='enough' else 'enough')
                expected='CONTINUE' if challenge=='enough' else 'REJECT'
            for name,kwargs in ENGINES.items():
                eng=ProofCarryEngine(**kwargs)
                res=eng.resolve(case,contract,copy.deepcopy(ev))
                flags=classify(case,res,expected)
                row=base_meta(run_id,'ablation',cfgsha,seed,case,source,target)
                row.update({'ablation':name,'challenge':challenge,'expected_decision':expected,'actual_decision':res.decision.value,'reason':res.reason or '','outcome_class':('UNSAFE' if flags['unsafe_violation'] else ('SAFE_COMPLETION' if flags['safe_completion'] else 'SAFE_REJECTION')),**flags})
                w.writerow(row)
    finally: fh.close()
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--out',required=True); ap.add_argument('--run-id',required=True); a=ap.parse_args(); run(Path(a.root),Path(a.out),a.run_id)
