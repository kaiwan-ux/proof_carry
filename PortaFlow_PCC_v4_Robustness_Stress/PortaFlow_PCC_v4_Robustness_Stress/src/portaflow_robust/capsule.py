from __future__ import annotations
import json
from dataclasses import dataclass,asdict
from copy import deepcopy
from typing import Any
from .models import SourceCapture,ExecutionState
from .history import portable_history,infer_semantics,apply_inferred,normalize_history
from .benchmark import static_spec,split_case
from .components import COMPONENTS,subset_key
SCHEMA_VERSION='4.0-robustness'
@dataclass
class Capsule:
    schema_version:str; workflow:str; request_id:str; application_state:dict[str,Any]; components:list[str]; inference_mode:str
    semantic_history:list[dict[str,Any]]|None=None; completed:list[str]|None=None; retry_counts:dict[str,int]|None=None; decisions:dict[str,str]|None=None; loop_counters:dict[str,int]|None=None
    control_frontier:dict[str,Any]|None=None; pending_obligations:list[dict[str,Any]]|None=None; effect_receipts:dict[str,dict[str,Any]]|None=None; continuation_contract:dict[str,Any]|None=None; provenance:dict[str,Any]|None=None
    def to_dict(self):return asdict(self)
    def payload_dict(self):
        d=self.to_dict(); d.pop('components',None); d.pop('inference_mode',None); return {k:v for k,v in d.items() if v is not None}
    def byte_size(self):return len(json.dumps(self.payload_dict(),sort_keys=True,separators=(',',':')).encode())
    @property
    def subset_key(self):return subset_key(self.components)

def _corrupt_history(history,profile):
    h=deepcopy(history)
    if profile=='baseline': return h
    if profile=='noise_duplicate':
        maxseq=max([int(e.get('seq',0)) for e in h] or [0])
        h.append({'seq':maxseq+1,'kind':'observation_noise','step':'telemetry','detail':{'message':'heartbeat'}})
        h.append({'seq':maxseq+2,'kind':'observation_noise','step':'telemetry','detail':{'message':'debug'}})
        meaningful=next((e for e in h if e.get('kind') in {'decision_made','effect_commit_ack','obligation_opened','retry_failed'}),None)
        if meaningful:
            dup=deepcopy(meaningful); dup['seq']=maxseq+3; h.append(dup)
        return h
    if profile=='out_of_order': return list(reversed(h))
    if profile=='partial_history_loss':
        for k in ['decision_made','obligation_opened','loop_iteration_completed','retry_failed','effect_commit_ack']:
            for i,e in enumerate(h):
                if e.get('kind')==k:
                    h.pop(i); return h
        return h
    return h

def _corrupt_receipts(receipts,history,profile):
    r=deepcopy(receipts)
    if profile!='receipt_conflict': return r
    ack=next((e for e in normalize_history(history or []) if e.get('kind')=='effect_commit_ack'),None)
    if ack:
        op=ack.get('step')
        if op in r: r[op]={**r[op],'status':'not_committed','replay':'allowed'}
    return r

def build_capsule(source,components,inference_mode):
    components=tuple(components); bad=set(components)-set(COMPONENTS)
    if bad:raise KeyError(bad)
    s=ExecutionState.from_dict(source.state); _,profile=split_case(s.workflow); cap=Capsule(SCHEMA_VERSION,s.workflow,s.request_id,deepcopy(s.inputs),list(components),inference_mode,provenance={'source_framework':source.framework,'native_snapshot_kind':source.native_snapshot.get('kind','canonical'),'evidence_profile':profile})
    if 'history' in components:cap.semantic_history=_corrupt_history(portable_history(s.trace),profile)
    if 'progress' in components:cap.completed=list(s.completed); cap.retry_counts=deepcopy(s.retry_counts); cap.decisions=deepcopy(s.decisions); cap.loop_counters=deepcopy(s.loop_counters)
    if 'frontier' in components:cap.control_frontier=deepcopy(s.control_frontier)
    if 'obligations' in components:cap.pending_obligations=deepcopy(s.pending_obligations)
    if 'receipts' in components:cap.effect_receipts=_corrupt_receipts(s.effect_receipts,s.trace,profile)
    if 'contract' in components:cap.continuation_contract=deepcopy(s.continuation_contract)
    return cap

def _receipt_resolves(s,op):return s.effect_receipts.get(op,{}).get('status') in {'committed','not_committed'}
def _history_acks(history):
    out={}
    for e in normalize_history(history or []):
        if e.get('kind')=='effect_commit_ack':out[e.get('step')]=e.get('detail',{}).get('status','committed')
    return out

def _validate_receipts(s,history):
    issues=[]; acks=_history_acks(history)
    for op,r in s.effect_receipts.items():
        if r.get('status') not in {'committed','not_committed'}: issues.append({'type':'invalid_receipt_status','operation':op})
        if not r.get('operation_id'): issues.append({'type':'missing_operation_id','operation':op})
        if op in acks and acks[op]!=r.get('status'): issues.append({'type':'receipt_history_conflict','operation':op,'history':acks[op],'receipt':r.get('status')})
    return issues

def _requirements_missing(s,spec):
    req=spec.get('resume_requirements',{}); miss=[]
    for k in req.get('frontier_keys',[]):
        if k not in s.control_frontier or s.control_frontier.get(k) in {None,''}:miss.append(f'frontier:{k}')
    for typ in req.get('obligation_types',[]):
        if not any(x.get('type')==typ for x in s.pending_obligations):miss.append(f'obligation:{typ}')
    for typ,n in (req.get('obligation_min_counts') or {}).items():
        if sum(1 for x in s.pending_obligations if x.get('type')==typ) < int(n): miss.append(f'obligation_count:{typ}>={n}')
    for k in req.get('decision_keys',[]):
        if k not in s.decisions:miss.append(f'decision:{k}')
    for k in req.get('loop_ids',[]):
        if k not in s.loop_counters:miss.append(f'loop:{k}')
    for k in req.get('retry_steps',[]):
        if k not in s.retry_counts:miss.append(f'retry:{k}')
    return miss

def lower_capsule(cap):
    s=ExecutionState(workflow=cap.workflow,request_id=cap.request_id,inputs=deepcopy(cap.application_state))
    if cap.semantic_history is not None:s.trace=deepcopy(cap.semantic_history)
    if cap.completed is not None:s.completed=list(cap.completed)
    if cap.retry_counts is not None:s.retry_counts=deepcopy(cap.retry_counts)
    if cap.decisions is not None:s.decisions=deepcopy(cap.decisions)
    if cap.loop_counters is not None:s.loop_counters=deepcopy(cap.loop_counters)
    if cap.control_frontier is not None:s.control_frontier=deepcopy(cap.control_frontier)
    if cap.pending_obligations is not None:s.pending_obligations=deepcopy(cap.pending_obligations)
    if cap.effect_receipts is not None:s.effect_receipts=deepcopy(cap.effect_receipts)
    if cap.continuation_contract is not None:s.continuation_contract=deepcopy(cap.continuation_contract)
    spec=static_spec(cap.workflow); report={'mode':cap.inference_mode,'ambiguities':[],'inferred_fields':[],'unresolved_critical_facts':[],'validation_issues':[],'missing_requirements':[]}
    if cap.inference_mode=='hybrid' and cap.semantic_history is not None:
        inf,rep=infer_semantics(cap.workflow,cap.semantic_history,spec); report.update(rep); report['mode']='history_plus_static_reconstruction'; s=apply_inferred(s,inf,only_missing=True)
        unresolved=[]
        for a in rep.get('ambiguities',[]):
            if a.get('type')=='effect_commit_unknown' and not _receipt_resolves(s,a.get('operation')):unresolved.append(a)
        report['unresolved_critical_facts']=unresolved
        if unresolved:return s,report,False,'AMBIGUOUS_EXTERNAL_COMMIT'
    issues=_validate_receipts(s,cap.semantic_history)
    if issues:
        report['validation_issues']=issues; return s,report,False,'CONFLICTING_EFFECT_EVIDENCE'
    # Only enforce reconstructability requirements for history-based representations. Explicit candidates already carry semantic state directly.
    if cap.inference_mode=='hybrid' and cap.semantic_history is not None:
        missing=_requirements_missing(s,spec); report['missing_requirements']=missing
        if missing:return s,report,False,'INSUFFICIENT_CONTINUATION_EVIDENCE'
    return s,report,True,None
