from __future__ import annotations
import argparse, json, time
from pathlib import Path
from proofcarry.contracts import contract_from_case
from proofcarry.engine import ProofCarryEngine
from proofcarry.runtime_repr import build_runtime_state, identity_mapping
from proofcarry.certificates import issue_certificate, verify_authenticated, DEFAULT_TEST_KEY
from proofcarry.types import RuntimeContext, Decision
from proofcarry.utils import RUNTIME_PAIRS, sha256_obj, canonical_json
from experiments.common import load_cases, make_writer, base_meta

FIELDS=['run_id','timestamp_utc','experiment','config_sha256','seed','case_id','workflow_family','source_runtime','target_runtime','repetition','mode','capture_ms','evidence_ms','signing_ms','serialization_ms','transfer_ms','verification_ms','proof_ms','translation_ms','resume_ms','total_ms','raw_checkpoint_bytes','evidence_bytes','certificate_bytes','total_transferred_bytes','decision']
def ms(a,b): return (b-a)/1e6

def one(case,source,target):
    T=time.perf_counter_ns; start=T()
    native=build_runtime_state(case,source); t1=T()
    contract=contract_from_case(case)
    ctx=RuntimeContext(case['workflow_id'],case['execution_id'],source,target,contract['contract_hash'])
    # Evidence generation excluding certificate issuance/signing.
    history={}; snapshots={'obligations':{'complete':True,'members':{},'universe':[]}}
    cert_specs=[]
    for f in case['required_facts']:
        if f.get('source')=='history': history[f['name']]=f['expected']
        elif f.get('source')=='snapshot':
            snapshots['obligations']['members'][f['name']]=f['expected']; snapshots['obligations']['universe'].append(f['name'])
        else: cert_specs.append((f['name'],f['expected']))
    for f in case.get('support_facts',[]):
        if f.get('source')=='history': history[f['name']]=f['truth']
        else: cert_specs.append((f['name'],f['truth']))
    ev={'case_id':case['case_id'],'source_runtime':source,'target_runtime':target,'source_state':native,'history':history,'certificates':[],'snapshots':snapshots,'identity_mapping':identity_mapping(case,source,target,'correct'),'noise':{}}
    t2=T()
    # Certificate generation/signing measured separately.
    for i,(name,value) in enumerate(cert_specs):
        ev['certificates'].append(issue_certificate(subject=name,value=value,context=ctx,nonce=f"perf:{case['case_id']}:{source}:{target}:{i}",key=DEFAULT_TEST_KEY))
    t3=T()
    blob=canonical_json({'contract':contract,'evidence':ev}).encode(); t4=T()
    transferred=bytes(blob); t5=T()
    parsed=json.loads(transferred.decode())
    used=set(); ok=True
    for cert in parsed['evidence'].get('certificates',[]):
        good,_=verify_authenticated(cert,ctx,DEFAULT_TEST_KEY,used_nonces=used,consume_nonce=True); ok=ok and good
    t6=T()
    if ok:
        # Certificate layer already verified above, so proof timing excludes crypto verification.
        res=ProofCarryEngine(certificate_verification=False).resolve(case,parsed['contract'],parsed['evidence'])
    else:
        res=None
    t7=T()
    plan={'runtime':target,'action':res.plan if res else None,'case_id':case['case_id']}; t8=T()
    resume_ok=bool(res and res.decision==Decision.CONTINUE and plan['action']==case['safe_plan']); t9=T()
    cert_blob=canonical_json(ev['certificates']).encode()
    return {
        'capture_ms':ms(start,t1),'evidence_ms':ms(t1,t2),'signing_ms':ms(t2,t3),'serialization_ms':ms(t3,t4),
        'transfer_ms':ms(t4,t5),'verification_ms':ms(t5,t6),'proof_ms':ms(t6,t7),'translation_ms':ms(t7,t8),
        'resume_ms':ms(t8,t9),'total_ms':ms(start,t9),'raw_checkpoint_bytes':len(canonical_json(native).encode()),
        'evidence_bytes':len(canonical_json(ev).encode()),'certificate_bytes':len(cert_blob),'total_transferred_bytes':len(blob),
        'decision':res.decision.value if res else 'REJECT'
    }

def run(root,out,run_id,seed=20260830,warmups=5,repetitions=30,max_cases=None):
    cfg={'warmups':warmups,'repetitions':repetitions,'max_cases':max_cases,'mode':'semantic_e2e'}; cfgsha=sha256_obj(cfg)
    cases=load_cases(root); cases=cases[:max_cases] if max_cases else cases
    fh,w=make_writer(out,FIELDS)
    try:
        for case in cases:
            for source,target in RUNTIME_PAIRS:
                for _ in range(warmups): one(case,source,target)
                for r in range(repetitions):
                    m=one(case,source,target); row=base_meta(run_id,'performance_semantic_e2e',cfgsha,seed,case,source,target); row.update({'repetition':r,'mode':'semantic_e2e',**m}); w.writerow(row)
    finally: fh.close()
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--out',required=True); ap.add_argument('--run-id',required=True); ap.add_argument('--warmups',type=int,default=5); ap.add_argument('--repetitions',type=int,default=30); ap.add_argument('--max-cases',type=int); a=ap.parse_args(); run(Path(a.root),Path(a.out),a.run_id,warmups=a.warmups,repetitions=a.repetitions,max_cases=a.max_cases)
