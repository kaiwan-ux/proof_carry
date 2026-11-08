from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
from crossresumebench_v2.certificates import issue_certificate

SAFE_APP_STATE={'phase':'mid_execution'}
def cert(case,ft,subject,value,evidence): return issue_certificate(case.case_id,ft,subject,value,case.case_id,evidence).to_dict()
def _components(case): return case.params['components'] if case.family=='composite' else [{'kind':case.family,'params':case.params}]
def _base(case,native):
    h=[]; cs=[]
    for comp in _components(case):
        f,p=comp['kind'],comp['params']; ref=native.checkpoint_ref
        if f=='effect_commitment':
            h.append({'type':'tool_call_observed','semantic_unit':p['effect_unit'],'data':{'operation':p['operation'],'commit_status':'unknown','parent_unit':p['effect_unit'],'unit_completion_observable':True}})
            cs.append(cert(case,'effect_commitment',p['operation'],p['effect_status'],{'native_checkpoint_ref':ref}))
        elif f=='retry_pause':
            h.append({'type':'retry_failed','semantic_unit':p['retry_unit'],'data':{'attempt':p['current_attempt'],'max_attempts':p['max_attempts']}})
        elif f=='approval_wait':
            if p['approval_state']=='pending':
                h.append({'type':'approval_requested','semantic_unit':p['approval_unit'],'data':{'request_id':p['request_id'],'blocks':p['approval_unit']}})
                cs.append(cert(case,'obligation_state',p['request_id'],'pending',{'kind':'approval','blocks':p['approval_unit'],'native_checkpoint_ref':ref}))
            else:
                cs.append(cert(case,'approval_state',p['request_id'],'absent',{'kind':'approval','native_checkpoint_ref':ref}))
        elif f=='parallel_join':
            h.append({'type':'join_observed','semantic_unit':p['join'],'data':{'requires':list(p['branches'])}})
            cs.append(cert(case,'completion_snapshot',p['join'],{'members':list(p['completed']),'universe':list(p['branches']),'complete':True},{'native_checkpoint_ref':ref}))
        elif f=='loop_pause':
            h.append({'type':'counter_observed','data':{'key':p['counter_key'],'value':p['current']}})
            cs.append(cert(case,'counter_bound',p['counter_key'],p['total'],{'native_checkpoint_ref':ref}))
            cs.append(cert(case,'decision_state',p['break_key'],p['break'],{'native_checkpoint_ref':ref}))
        elif f=='compensation_pending':
            h.append({'type':'tool_call_observed','semantic_unit':p['effect_unit'],'data':{'operation':p['operation'],'commit_status':'unknown','parent_unit':p['effect_unit'],'unit_completion_observable':True}})
            cs.append(cert(case,'effect_commitment',p['operation'],p['effect_status'],{'native_checkpoint_ref':ref}))
            if p['compensation_state']=='pending':
                h.append({'type':'compensation_required','semantic_unit':p['comp_unit'],'data':{'compensation_action':p['compensation'],'effect':p['operation']}})
                cs.append(cert(case,'obligation_state',p['compensation'],'pending',{'kind':'compensation','native_checkpoint_ref':ref}))
            else:
                cs.append(cert(case,'compensation_state',p['compensation'],'absent',{'kind':'compensation','native_checkpoint_ref':ref}))
        elif f=='async_callback':
            if p['callback_state']=='pending':
                h.append({'type':'callback_pending','semantic_unit':p['callback_unit'],'data':{'callback_id':p['callback_id'],'operation':p['operation'],'blocks':p['callback_unit']}})
                cs.append(cert(case,'obligation_state',p['callback_id'],'pending',{'kind':'callback','native_checkpoint_ref':ref}))
            else:
                cs.append(cert(case,'callback_state',p['callback_id'],'absent',{'kind':'callback','native_checkpoint_ref':ref}))
    return h,cs

def _drop_fact(case,h,cs):
    ft=case.drop_fact['fact_type']; sub=case.drop_fact['subject']
    out_h=[]
    for e in h:
        d=e.get('data',{}); typ=e.get('type'); u=e.get('semantic_unit')
        remove=False
        if ft=='effect_status' and typ=='tool_call_observed' and d.get('operation')==sub: pass # keep unknown history, certificate is removed below
        elif ft=='retry_bound' and typ=='retry_failed' and u==sub:
            e=copy.deepcopy(e); e['data'].pop('max_attempts',None)
        elif ft=='retry_current' and typ=='retry_failed' and u==sub: remove=True
        elif ft=='approval_state' and typ=='approval_requested' and d.get('request_id')==sub: remove=True
        elif ft=='callback_state' and typ=='callback_pending' and d.get('callback_id')==sub: remove=True
        elif ft=='compensation_state' and typ=='compensation_required' and d.get('compensation_action')==sub: remove=True
        elif ft=='counter_state' and typ=='counter_observed' and str(d.get('key'))==sub: remove=True
        if not remove: out_h.append(e)
    def maps(c):
        cft,csub=c.get('fact_type'),str(c.get('subject')); val=c.get('value')
        universe=val.get('universe',[]) if isinstance(val,dict) else []
        if ft=='effect_status': return cft=='effect_commitment' and csub==sub
        if ft=='approval_state': return (cft in {'obligation_state','approval_state'} and csub==sub) or (cft=='obligation_snapshot' and sub in universe)
        if ft=='callback_state': return (cft in {'obligation_state','callback_state'} and csub==sub) or (cft=='obligation_snapshot' and sub in universe)
        if ft=='compensation_state': return (cft in {'obligation_state','compensation_state'} and csub==sub) or (cft=='obligation_snapshot' and sub in universe)
        if ft=='semantic_completion': return cft=='completion_snapshot' and sub in universe
        if ft=='counter_state': return cft=='counter_state' and csub==sub
        if ft=='counter_bound': return cft=='counter_bound' and csub==sub
        if ft=='retry_bound': return cft=='retry_bound' and csub==sub
        if ft=='decision_state': return cft=='decision_state' and csub==sub
        return False
    return out_h,[c for c in cs if not maps(c)]

def _replace_subject(obj,old,new):
    x=copy.deepcopy(obj)
    def walk(v):
        if isinstance(v,dict):
            for k,a in list(v.items()):
                if isinstance(a,str) and a==old: v[k]=new
                else: walk(a)
        elif isinstance(v,list):
            for i,a in enumerate(v):
                if isinstance(a,str) and a==old: v[i]=new
                else: walk(a)
    walk(x); return x

def generate(case,native,variant):
    h,cs=_base(case,native)
    if variant=='missing_critical_fact': h,cs=_drop_fact(case,h,cs)
    elif variant=='irrelevant_noise':
        h.append({'type':'decision_made','data':{'key':'irrelevant_debug_flag','choice':'noise'}})
        cs.append(cert(case,'fact_value','irrelevant_subject','irrelevant_value',{'fact_type':'irrelevant_fact','native_checkpoint_ref':native.checkpoint_ref}))
    elif variant in {'identity_alias_with_binding','identity_alias_without_binding'}:
        old=case.alias_subject; new='src_alias__'+old; h=[_replace_subject(e,old,new) for e in h]; cs=[_replace_subject(c,old,new) for c in cs]
        # subject replacement invalidates old hashes, so reissue any altered cert using its content.
        fixed=[]
        for c in cs:
            if c.get('subject')==new or (isinstance(c.get('value'),dict) and new in json.dumps(c.get('value'))):
                fixed.append(cert(case,c['fact_type'],c['subject'],c.get('value'),c.get('evidence',{})))
            else: fixed.append(c)
        cs=fixed
        if variant=='identity_alias_with_binding': cs.append(cert(case,'identity_binding',new,old,{'native_checkpoint_ref':native.checkpoint_ref}))
    elif variant=='tampered_attestation':
        # corrupt first relevant certificate; if none, create and corrupt a required fact attestation.
        if not cs:
            r=case.continuation_contract['required_facts'][0]; cs.append(cert(case,'fact_value',r['subject'],'tamper_probe',{'fact_type':r['fact_type']}))
        cs=copy.deepcopy(cs); cs[0]['evidence_hash']='0'*64
    elif variant=='complete_negative_snapshot':
        # Replace direct absent state with a complete empty-domain snapshot.
        replaced=False; n=[]
        for c in cs:
            if c.get('fact_type') in {'approval_state','callback_state','compensation_state'} and c.get('value')=='absent':
                kind=c['fact_type'].replace('_state',''); n.append(cert(case,'obligation_snapshot',kind,{'kind':kind,'members':[],'universe':[c['subject']],'complete':True},{'kind':kind,'native_checkpoint_ref':native.checkpoint_ref})); replaced=True
            else: n.append(c)
        cs=n
        if not replaced: raise ValueError(f'negative snapshot not applicable {case.case_id}')
    elif variant!='enough_evidence': raise KeyError(variant)
    capture={'case_id':case.case_id,'workflow':f'mccv3_holdout_{case.family}','app_state':dict(SAFE_APP_STATE),'history':h,'certificates':cs,'native_observation':dict(native.native_observation)}
    capture['native_observation']['framework']=native.framework
    return capture

def legacy_capture(capture):
    allowed={'effect_commitment','semantic_completion','obligation_state','dependency_state'}
    x=copy.deepcopy(capture); x['certificates']=[c for c in x['certificates'] if c.get('fact_type') in allowed]; return x
