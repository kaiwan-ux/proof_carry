from __future__ import annotations
from copy import deepcopy
from typing import Any
from .models import ExecutionState

BASE_WORKFLOWS=[
    "escrow_callback_release",
    "two_phase_reservation_commit",
    "quorum_write_cancel",
    "race_cleanup_notify",
    "nested_review_retry_publish",
    "dual_approval_release",
    "saga_shipping_refund",
    "batch_reduce_invoice",
]
PROFILES=["baseline","noise_duplicate","out_of_order","partial_history_loss","receipt_conflict"]
SCENARIOS=[f"{w}::{p}" for w in BASE_WORKFLOWS for p in PROFILES]

def split_case(case:str):
    if '::' not in case: return case,'baseline'
    return tuple(case.split('::',1))

STATIC_SPECS={
"escrow_callback_release":{
 "nodes":["start","hold_funds","await_callback","release","finish"],
 "contract":{"requires_obligation":"webhook","effect_exactly_once":["hold_funds"]},
 "frontier_rules":[{"when":{"obligation_type":"webhook"},"frontier":{"next":"callback_then_release"}}],
 "resume_requirements":{"frontier_keys":["next"],"obligation_types":["webhook"]},
},
"two_phase_reservation_commit":{
 "nodes":["start","prepare_reservation","commit_reservation","verify","finish"],
 "contract":{"effect_exactly_once":["prepare_reservation","commit_reservation"]},
 "frontier_rules":[{"when":{"completed_all":["commit_reservation"]},"frontier":{"next":"verify"}}],
 "resume_requirements":{"frontier_keys":["next"]},
},
"quorum_write_cancel":{
 "nodes":["start","fanout","write_a","write_b","write_c","quorum","finish"],
 "contract":{"join":"quorum","members":["write_a","write_b","write_c"],"quorum":2,"cancel_remainder":True},
 "frontier_rules":[{"when":{"obligation_type":"cancel_branch"},"frontier":{"next":"cancel_then_quorum"}}],
 "resume_requirements":{"frontier_keys":["next"],"obligation_types":["cancel_branch"]},
},
"race_cleanup_notify":{
 "nodes":["start","fanout","fast","slow_a","slow_b","cleanup","notify","finish"],
 "contract":{"race":"first_success","winner":"fast","cancel":["slow_a","slow_b"],"requires_obligation":"cleanup"},
 "frontier_rules":[{"when":{"completed_all":["fast"],"obligation_type":"cleanup"},"frontier":{"next":"cleanup_then_notify"}}],
 "resume_requirements":{"frontier_keys":["next"],"obligation_types":["cleanup"]},
},
"nested_review_retry_publish":{
 "nodes":["start","review","choose","fast_tool","approval","publish","finish"],
 "contract":{"loop_id":"review","loop_limit":3,"decision_key":"lane","retry_step":"fast_tool","requires_approval_before":"publish"},
 "frontier_rules":[{"when":{"decision":{"lane":"fast"},"retry_at_least":{"fast_tool":1},"obligation_type":"human_approval"},"frontier":{"next":"retry_then_review3_then_approve","branch":"$decision:lane","iteration":"$loop_next:review"}}],
 "resume_requirements":{"frontier_keys":["next","branch","iteration"],"obligation_types":["human_approval","retry"],"decision_keys":["lane"],"loop_ids":["review"],"retry_steps":["fast_tool"]},
},
"dual_approval_release":{
 "nodes":["start","edit","legal_approval","finance_approval","release","finish"],
 "contract":{"approval_quorum":2,"requires_before":"release"},
 "frontier_rules":[{"when":{"obligation_type":"human_approval"},"frontier":{"next":"resolve_two_approvals_then_release"}}],
 "resume_requirements":{"frontier_keys":["next"],"obligation_types":["human_approval"],"obligation_min_counts":{"human_approval":2}},
},
"saga_shipping_refund":{
 "nodes":["start","debit","reserve","ship","release_stock","refund","finish"],
 "contract":{"compensation_order":["release_stock","refund"],"forward_effects":["debit","reserve"]},
 "frontier_rules":[{"when":{"obligation_type":"compensation"},"frontier":{"next":"compensate_reverse_order"}}],
 "resume_requirements":{"frontier_keys":["next"],"obligation_types":["compensation"],"obligation_min_counts":{"compensation":2}},
},
"batch_reduce_invoice":{
 "nodes":["start","fanout","shard1","shard2","shard3","shard4","reduce","invoice","finish"],
 "contract":{"join":"reduce","members":["shard1","shard2","shard3","shard4"],"quorum":3,"effect_exactly_once":["invoice"]},
 "frontier_rules":[{"when":{"obligation_type":"cancel_branch"},"frontier":{"next":"reduce_then_invoice"}}],
 "resume_requirements":{"frontier_keys":["next"],"obligation_types":["cancel_branch"]},
},
}

def static_spec(case:str): return deepcopy(STATIC_SPECS[split_case(case)[0]])

def initial_state(case:str):
    return ExecutionState(workflow=case,request_id=f"robust-{case.replace('::','-')}-001",inputs={"amount":100,"document":"draft-v1","logical_tick":20})

def _receipt(s,ledger,op,ack=True,replay='forbidden'):
    ledger[op]=ledger.get(op,0)+1
    s.effect_receipts[op]={"operation_id":f"{s.request_id}:{op}","status":"committed","replay":replay,"idempotency_key":f"idem:{s.request_id}:{op}"}
    if ack:s.event("effect_commit_ack",op,operation_id=f"{s.request_id}:{op}",status="committed",replay=replay)
    else:s.event("tool_call_observed",op,result="returned_or_timeout",commit_status="unknown",replay_class="unknown")

def _obl(s,typ,oid,**detail):
    rec={"type":typ,"id":oid,**detail}; s.pending_obligations.append(rec); d={"id":oid,**detail}
    if 'step' in d: d['obligation_step']=d.pop('step')
    s.event("obligation_opened",typ,**d)

def _resolve(s,typ):
    xs=[x for x in s.pending_obligations if x.get('type')==typ]
    for x in xs:s.event('obligation_resolved',typ,id=x.get('id'))
    s.pending_obligations=[x for x in s.pending_obligations if x.get('type')!=typ]

def _do_if_needed(s,ledger,op):
    r=s.effect_receipts.get(op,{})
    if r.get('status')=='committed' and r.get('replay')=='forbidden': return
    if r.get('status')=='not_committed' or not r:
        ledger[op]=ledger.get(op,0)+1; s.event('effect_executed_target',op,count=ledger[op]); s.step(op)

def _baseline_prefix(s,ledger):
    w,_=split_case(s.workflow); spec=STATIC_SPECS[w]
    if w=='escrow_callback_release':
        s.step('start'); _receipt(s,ledger,'hold_funds',ack=True); s.step('hold_funds'); _obl(s,'webhook','escrow-cb',blocks='release'); s.control_frontier={'next':'callback_then_release'}
    elif w=='two_phase_reservation_commit':
        s.step('start'); _receipt(s,ledger,'prepare_reservation',ack=True); s.step('prepare_reservation'); _receipt(s,ledger,'commit_reservation',ack=False); s.step('commit_reservation'); s.control_frontier={'next':'verify'}
    elif w=='quorum_write_cancel':
        s.step('start'); s.event('fanout_started','fanout',branches=['write_a','write_b','write_c']); s.step('fanout'); s.step('write_a'); s.step('write_b'); _obl(s,'cancel_branch','cancel-c',branch='write_c'); s.control_frontier={'next':'cancel_then_quorum'}
    elif w=='race_cleanup_notify':
        s.step('start'); s.event('fanout_started','fanout',branches=['fast','slow_a','slow_b']); s.step('fanout'); s.step('fast'); s.event('race_winner','fast'); _obl(s,'cleanup','cleanup-losers',branches=['slow_a','slow_b']); s.control_frontier={'next':'cleanup_then_notify'}
    elif w=='nested_review_retry_publish':
        s.step('start')
        for i in (1,2): s.loop_counters['review']=i; s.event('loop_iteration_completed','review',loop_id='review',iteration=i); s.step(f'review_{i}')
        s.decisions['lane']='fast'; s.event('decision_made','choose',key='lane',choice='fast'); s.step('choose'); s.retry_counts['fast_tool']=1; s.event('retry_failed','fast_tool',attempt=1,max_attempts=2); s.step('fast_attempt_1'); _obl(s,'retry','retry-fast',step='fast_tool',next_attempt=2,max_attempts=2); _obl(s,'human_approval','publish-approval',blocks='publish'); s.control_frontier={'next':'retry_then_review3_then_approve','branch':'fast','iteration':3}
    elif w=='dual_approval_release':
        s.step('start'); s.inputs['document']='edited-v2'; s.event('application_state_updated','edit',field='document',value='edited-v2'); s.step('edit'); _obl(s,'human_approval','legal',role='legal'); _obl(s,'human_approval','finance',role='finance'); s.control_frontier={'next':'resolve_two_approvals_then_release'}
    elif w=='saga_shipping_refund':
        s.step('start'); _receipt(s,ledger,'debit',ack=True); s.step('debit'); _receipt(s,ledger,'reserve',ack=True); s.step('reserve'); s.event('retry_failed','ship',attempt=1,max_attempts=1,reason='permanent'); s.step('ship_failed'); _obl(s,'compensation','release-stock',action='release_stock'); _obl(s,'compensation','refund-debit',action='refund'); s.control_frontier={'next':'compensate_reverse_order'}
    elif w=='batch_reduce_invoice':
        s.step('start'); s.event('fanout_started','fanout',branches=['shard1','shard2','shard3','shard4']); s.step('fanout'); s.step('shard1'); s.step('shard2'); s.step('shard3'); _obl(s,'cancel_branch','cancel-shard4',branch='shard4'); _receipt(s,ledger,'invoice',ack=False); s.step('invoice'); s.control_frontier={'next':'reduce_then_invoice'}
    s.continuation_contract=deepcopy(spec['contract']); return s

def _event_key(e):
    import json
    return (e.get('kind'),e.get('step'),json.dumps(e.get('detail',{}),sort_keys=True,default=str))

def _apply_profile(s,profile):
    if profile=='baseline': return s
    if profile=='noise_duplicate':
        # Add irrelevant observability and duplicate one semantic event; generic normalizer must ignore/dedupe safely.
        s.event('observation_noise','telemetry',message='heartbeat'); s.event('observation_noise','telemetry',message='debug')
        meaningful=next((e for e in s.trace if e.get('kind') in {'decision_made','effect_commit_ack','obligation_opened','retry_failed'}),None)
        if meaningful:
            dup=deepcopy(meaningful); dup['seq']=len(s.trace)+1; s.trace.append(dup)
        return s
    if profile=='out_of_order':
        # Preserve original sequence numbers, scramble list order deterministically.
        s.trace=list(reversed(s.trace)); return s
    if profile=='partial_history_loss':
        # Remove one critical reconstructable event, while the explicit semantic state remains intact.
        priorities=['decision_made','obligation_opened','loop_iteration_completed','retry_failed','effect_commit_ack']
        for k in priorities:
            for i,e in enumerate(s.trace):
                if e.get('kind')==k:
                    s.trace.pop(i); return s
        return s
    if profile=='receipt_conflict':
        # Contradict one observable commit acknowledgement. Safe systems should reject conflict, not guess.
        ack=next((e for e in s.trace if e.get('kind')=='effect_commit_ack'),None)
        if ack:
            op=ack.get('step')
            if op in s.effect_receipts: s.effect_receipts[op]={**s.effect_receipts[op],'status':'not_committed','replay':'allowed'}
        return s
    raise KeyError(profile)

def source_prefix_transition(state,ledger):
    # Source/native truth is never corrupted by a robustness profile. Profiles modify only portable evidence in build_capsule().
    return _baseline_prefix(state.clone(),ledger)

def _has(s,typ): return any(x.get('type')==typ for x in s.pending_obligations)

def continuation_transition(state,ledger):
    s=state.clone(); w,_=split_case(s.workflow)
    if w=='escrow_callback_release':
        _do_if_needed(s,ledger,'hold_funds');
        if _has(s,'webhook'):_resolve(s,'webhook')
        else:s.step('callback_missing')
        s.step('release'); s.step('finish'); s.terminated=True; s.outcome='released'
    elif w=='two_phase_reservation_commit':
        _do_if_needed(s,ledger,'prepare_reservation'); _do_if_needed(s,ledger,'commit_reservation'); s.step('verify'); s.step('finish'); s.terminated=True; s.outcome='verified'
    elif w=='quorum_write_cancel':
        if _has(s,'cancel_branch') and s.continuation_contract.get('quorum')==2:_resolve(s,'cancel_branch'); s.step('quorum')
        else:s.step('write_c'); s.step('quorum')
        s.step('finish'); s.terminated=True; s.outcome='quorum_done'
    elif w=='race_cleanup_notify':
        if _has(s,'cleanup'):_resolve(s,'cleanup')
        else:s.step('cleanup_missing')
        s.step('notify'); s.step('finish'); s.terminated=True; s.outcome='notified'
    elif w=='nested_review_retry_publish':
        good=s.control_frontier.get('branch')=='fast' and int(s.control_frontier.get('iteration',0))==3 and _has(s,'retry') and _has(s,'human_approval')
        if good:
            _resolve(s,'retry'); s.retry_counts['fast_tool']=2; s.event('retry_succeeded','fast_tool',attempt=2); s.step('fast_tool'); s.loop_counters['review']=3; s.event('loop_iteration_completed','review',loop_id='review',iteration=3); s.step('review_3'); _resolve(s,'human_approval'); s.step('publish')
        else:s.step('continuation_semantics_missing')
        s.step('finish'); s.terminated=True; s.outcome='published' if good else 'wrong'
    elif w=='dual_approval_release':
        n=sum(1 for x in s.pending_obligations if x.get('type')=='human_approval')
        if n>=2:_resolve(s,'human_approval'); s.step('release')
        else:s.step('approval_quorum_missing')
        s.step('finish'); s.terminated=True; s.outcome=s.inputs.get('document') if n>=2 else 'wrong'
    elif w=='saga_shipping_refund':
        _do_if_needed(s,ledger,'debit'); _do_if_needed(s,ledger,'reserve'); acts=[x.get('action') for x in s.pending_obligations if x.get('type')=='compensation']
        if s.continuation_contract.get('compensation_order')==['release_stock','refund'] and set(acts)=={'release_stock','refund'}:
            for op in ['release_stock','refund']: ledger[op]=ledger.get(op,0)+1; s.event('effect_executed_target',op,count=ledger[op]); s.step(op)
            _resolve(s,'compensation')
        else:s.step('compensation_missing')
        s.step('finish'); s.terminated=True; s.outcome='compensated'
    elif w=='batch_reduce_invoice':
        if _has(s,'cancel_branch') and s.continuation_contract.get('quorum')==3:_resolve(s,'cancel_branch'); s.step('reduce')
        else:s.step('shard4'); s.step('reduce')
        _do_if_needed(s,ledger,'invoice'); s.step('finish'); s.terminated=True; s.outcome='invoiced'
    return s
