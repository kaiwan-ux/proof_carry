from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from copy import deepcopy
from typing import Any
from .models import SourceCapture, ExecutionState
from .history import portable_history, infer_semantics, apply_inferred
from .benchmark import static_spec

SCHEMA_VERSION="1.0"
CONDITIONS=[
    "state_only","raw_history","history_inference","full_pcc_v1",
    "pcc_minus_history","pcc_minus_frontier","pcc_minus_obligations","pcc_minus_receipts","pcc_minus_contract",
]

@dataclass
class Capsule:
    schema_version:str; condition:str; workflow:str; request_id:str; application_state:dict[str,Any]
    semantic_history:list[dict[str,Any]]|None=None
    completed:list[str]|None=None
    retry_counts:dict[str,int]|None=None
    decisions:dict[str,str]|None=None
    loop_counters:dict[str,int]|None=None
    control_frontier:dict[str,Any]|None=None
    pending_obligations:list[dict[str,Any]]|None=None
    effect_receipts:dict[str,dict[str,Any]]|None=None
    continuation_contract:dict[str,Any]|None=None
    provenance:dict[str,Any]|None=None
    def to_dict(self): return asdict(self)
    def byte_size(self):
        d=self.to_dict(); d.pop("condition",None); d={k:v for k,v in d.items() if v is not None}
        return len(json.dumps(d,sort_keys=True,separators=(",",":")).encode())


def build_capsule(c:SourceCapture, condition:str)->Capsule:
    if condition not in CONDITIONS: raise KeyError(condition)
    s=ExecutionState.from_dict(c.state)
    cap=Capsule(SCHEMA_VERSION,condition,s.workflow,s.request_id,deepcopy(s.inputs),provenance={"source_framework":c.framework,"native_snapshot_kind":c.native_snapshot.get("kind","unknown")})
    if condition=="state_only": return cap
    cap.semantic_history=portable_history(s.trace)
    if condition in {"raw_history","history_inference"}: return cap
    # PCC explicit semantics. Leave-one-out conditions remove exactly one semantic family.
    cap.completed=list(s.completed); cap.retry_counts=deepcopy(s.retry_counts); cap.decisions=deepcopy(s.decisions); cap.loop_counters=deepcopy(s.loop_counters)
    cap.control_frontier=deepcopy(s.control_frontier); cap.pending_obligations=deepcopy(s.pending_obligations); cap.effect_receipts=deepcopy(s.effect_receipts); cap.continuation_contract=deepcopy(s.continuation_contract)
    if condition=="pcc_minus_history": cap.semantic_history=None
    elif condition=="pcc_minus_frontier": cap.control_frontier=None
    elif condition=="pcc_minus_obligations": cap.pending_obligations=None
    elif condition=="pcc_minus_receipts": cap.effect_receipts=None
    elif condition=="pcc_minus_contract": cap.continuation_contract=None
    return cap


def lower_capsule(cap:Capsule)->tuple[ExecutionState,dict[str,Any],bool,str|None]:
    s=ExecutionState(workflow=cap.workflow,request_id=cap.request_id,inputs=deepcopy(cap.application_state))
    report={"ambiguities":[],"inferred_fields":[],"mode":"none"}
    if cap.semantic_history is not None: s.trace=deepcopy(cap.semantic_history)
    if cap.completed is not None: s.completed=list(cap.completed)
    if cap.retry_counts is not None: s.retry_counts=deepcopy(cap.retry_counts)
    if cap.decisions is not None: s.decisions=deepcopy(cap.decisions)
    if cap.loop_counters is not None: s.loop_counters=deepcopy(cap.loop_counters)
    if cap.control_frontier is not None: s.control_frontier=deepcopy(cap.control_frontier)
    if cap.pending_obligations is not None: s.pending_obligations=deepcopy(cap.pending_obligations)
    if cap.effect_receipts is not None: s.effect_receipts=deepcopy(cap.effect_receipts)
    if cap.continuation_contract is not None: s.continuation_contract=deepcopy(cap.continuation_contract)

    if cap.condition in {"history_inference","pcc_minus_frontier","pcc_minus_obligations","pcc_minus_receipts","pcc_minus_contract"} and cap.semantic_history is not None:
        inf, rep=infer_semantics(cap.workflow,cap.semantic_history,static_spec(cap.workflow)); report=rep; report["mode"]="history_plus_static_reconstruction"
        s=apply_inferred(s,inf,only_missing=True)
    # Strong inference baseline is allowed to REFUSE rather than cause an unsafe side effect when commit is unknowable.
    if cap.condition=="history_inference" and any(a.get("type")=="effect_commit_unknown" for a in report.get("ambiguities",[])):
        return s,report,False,"AMBIGUOUS_EXTERNAL_COMMIT"
    # Leave-one-out PCC is not automatically rejected: it tests whether fallback reconstruction can replace the omitted field.
    return s,report,True,None
