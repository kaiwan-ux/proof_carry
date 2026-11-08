from __future__ import annotations
import argparse, copy, json
from pathlib import Path
from proofcarry.utils import RUNTIME_PAIRS, sha256_obj
from proofcarry.contracts import contract_from_case
from proofcarry.engine import ProofCarryEngine
from proofcarry.security import ATTACKS, make_attack
from proofcarry.evaluate import classify
from experiments.common import load_cases, make_writer, base_meta

FIELDS=['run_id','timestamp_utc','experiment','config_sha256','seed','case_id','workflow_family','source_runtime','target_runtime','security_mode','attack','expected_decision','actual_decision','safe_completion','safe_rejection','unsafe_violation','outcome_class','reason']

def run(root,out,run_id,seed=20260830):
    cfg=json.loads((root/'configs/security.json').read_text()); cfgsha=sha256_obj(cfg)
    fh,w=make_writer(out,FIELDS)
    try:
        for case in load_cases(root):
            contract=contract_from_case(case)
            for source,target in RUNTIME_PAIRS:
                attacks=['valid_control']+list(ATTACKS)
                for attack in attacks:
                    for mode in ['authenticated_proofcarry','hash_only_control']:
                        eng=ProofCarryEngine(authentication=(mode=='authenticated_proofcarry'))
                        ev=make_attack(case,source,target,attack)
                        used=set()
                        if attack=='nonce_reuse' and ev.get('certificates'):
                            # Prime the registry with the certificate nonce. The tested verification is the replay.
                            used.add(ev['certificates'][0]['nonce'])
                        res=eng.resolve(case,contract,ev,used_nonces=used,consume_nonces=True)
                        expected='CONTINUE' if attack=='valid_control' else 'REJECT'
                        flags=classify(case,res,expected)
                        row=base_meta(run_id,'security',cfgsha,seed,case,source,target)
                        row.update({'security_mode':mode,'attack':attack,'expected_decision':expected,'actual_decision':res.decision.value,'reason':res.reason or '','outcome_class':('UNSAFE' if flags['unsafe_violation'] else ('SAFE_COMPLETION' if flags['safe_completion'] else 'SAFE_REJECTION')),**flags})
                        w.writerow(row)
    finally: fh.close()
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--out',required=True); ap.add_argument('--run-id',required=True); a=ap.parse_args(); run(Path(a.root),Path(a.out),a.run_id)
