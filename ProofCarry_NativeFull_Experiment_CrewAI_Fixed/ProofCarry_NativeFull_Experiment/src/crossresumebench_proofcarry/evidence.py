from __future__ import annotations
import copy,hashlib,json
from mechanism.certificates import issue_certificate
from mechanism.proofcarry import contract_hash
from mechanism.crypto import deterministic_test_private_key
RUNTIME_ALIAS={'langgraph':lambda s:f'lg.node::{s}','crewai':lambda s:f'crew.task::{s}','maf':lambda s:f'maf.activity::{s}'}
ISSUER='benchmark-trusted-witness'
VERIFICATION_TIME=1800000000

def workflow_hash(case): return hashlib.sha256(json.dumps({'family':case.family,'params':case.params},sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def target_contract(case,target):
    c=copy.deepcopy(case.continuation_contract)
    # Required subjects deliberately use target-native aliases.
    for r in c['required_facts']: r['subject']=RUNTIME_ALIAS[target](r['subject'])
    return c

def _cert(case,source,target,execution_id,ft,subject,value,evidence,expires=VERIFICATION_TIME+3600,nonce=None):
    wh=workflow_hash(case); con=target_contract(case,target)
    return issue_certificate(issuer_id=ISSUER,execution_id=execution_id,case_id=case.case_id,workflow_spec_hash=wh,contract_hash=contract_hash(con),source_runtime=source,target_runtime=target,fact_type=ft,subject=subject,value=value,evidence=evidence,issued_at=VERIFICATION_TIME-3600,expires_at=expires,nonce=nonce,private_key=deterministic_test_private_key())

def _subject(source,canonical): return RUNTIME_ALIAS[source](canonical)
def _bindings(case,source,target,execution_id):
    out=[]
    for s in case.subjects:
        out.append(_cert(case,source,target,execution_id,'identity_binding',RUNTIME_ALIAS[source](s),s,{'registry':'benchmark-semantic-registry'}))
        out.append(_cert(case,source,target,execution_id,'identity_binding',RUNTIME_ALIAS[target](s),s,{'registry':'benchmark-semantic-registry'}))
    return out

def base_capture(case,native,source,target,execution_id):
    h=[]; cs=[]
    # Facts are intentionally split: some are history-observable, others require certified evidence.
    snapshot_states={}
    for f in case.truth_facts:
        ft,canonical,val,src=f['fact_type'],f['subject'],f['value'],f.get('source','certificate'); alias=_subject(source,canonical)
        if src=='history':
            if ft in {'retry_current','retry_bound'}:
                # merge below by task
                pass
            elif ft=='loop_current': h.append({'type':'loop_observed','subject':alias,'data':{'current':val}})
            else: h.append({'type':'fact_observed','fact_type':ft,'subject':alias,'value':val,'data':{}})
        elif src=='snapshot': snapshot_states[alias]=val
        else: cs.append(_cert(case,source,target,execution_id,ft,alias,val,{'native_checkpoint_ref':native.checkpoint_ref}))
    # Retry history pairs.
    retry={}
    for f in case.truth_facts:
        if f['fact_type'] in {'retry_current','retry_bound'}:
            retry.setdefault(f['subject'],{})[f['fact_type']]=f['value']
    for sub,d in retry.items(): h.append({'type':'retry_observed','subject':_subject(source,sub),'data':{'current':d.get('retry_current',0),'bound':d.get('retry_bound',0)}})
    if snapshot_states:
        cs.append(_cert(case,source,target,execution_id,'fact_snapshot',f'{case.case_id}:snapshot',{'fact_type':'branch_state','states':snapshot_states,'complete':True},{'native_checkpoint_ref':native.checkpoint_ref}))
    cs += _bindings(case,source,target,execution_id)
    return {'case_id':case.case_id,'execution_id':execution_id,'workflow':f'proofcarry_{case.family}','source_runtime':source,'target_runtime':target,'app_state':{'phase':'mid_execution'},'history':h,'certificates':cs,'native_observation':dict(native.native_observation)}

def _drop_required(case,capture,source):
    x=copy.deepcopy(capture); d=case.drop_fact; alias=_subject(source,d['subject'])
    # Remove direct cert/fact and snapshot state. For retry bound, retain current but remove bound from history.
    nh=[]
    for e in x['history']:
        if d['fact_type']=='retry_bound' and e.get('type')=='retry_observed' and e.get('subject')==alias:
            e=copy.deepcopy(e); e['data'].pop('bound',None)
        elif e.get('type')=='fact_observed' and e.get('fact_type')==d['fact_type'] and e.get('subject')==alias: continue
        else: nh.append(e)
    x['history']=nh; nc=[]
    for c in x['certificates']:
        if c.get('fact_type')==d['fact_type'] and c.get('subject')==alias: continue
        if c.get('fact_type')=='fact_snapshot' and isinstance(c.get('value'),dict):
            c=copy.deepcopy(c); c['value'].get('states',{}).pop(alias,None)
            # Signature is now invalid if kept; remove snapshot entirely when it contained dropped fact.
            continue
        nc.append(c)
    x['certificates']=nc; return x

def generate(case,native,source,target,variant):
    execution_id=f'exec::{case.case_id}::{source}->{target}'; x=base_capture(case,native,source,target,execution_id)
    if variant=='missing_critical_fact': x=_drop_required(case,x,source)
    elif variant=='runtime_binding_missing':
        # Remove source binding for one required subject.
        victim=RUNTIME_ALIAS[source](case.subjects[0]); x['certificates']=[c for c in x['certificates'] if not (c.get('fact_type')=='identity_binding' and c.get('subject')==victim)]
    elif variant=='runtime_binding_complete': pass
    elif variant=='irrelevant_noise': x['history'].append({'type':'fact_observed','fact_type':'debug_flag','subject':'noise::debug','value':'irrelevant','data':{}})
    elif variant!='enough_evidence': raise KeyError(variant)
    return x
