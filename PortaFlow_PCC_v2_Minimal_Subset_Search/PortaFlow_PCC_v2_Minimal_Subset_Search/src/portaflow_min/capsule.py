from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from copy import deepcopy
from typing import Any
from .models import SourceCapture, ExecutionState
from .history import portable_history, infer_semantics, apply_inferred
from .benchmark import static_spec
from .components import COMPONENTS, subset_key

SCHEMA_VERSION = "2.0-minimality"

@dataclass
class Capsule:
    schema_version: str
    workflow: str
    request_id: str
    application_state: dict[str, Any]
    components: list[str]
    inference_mode: str
    semantic_history: list[dict[str, Any]]|None=None
    completed: list[str]|None=None
    retry_counts: dict[str,int]|None=None
    decisions: dict[str,str]|None=None
    loop_counters: dict[str,int]|None=None
    control_frontier: dict[str,Any]|None=None
    pending_obligations: list[dict[str,Any]]|None=None
    effect_receipts: dict[str,dict[str,Any]]|None=None
    continuation_contract: dict[str,Any]|None=None
    provenance: dict[str,Any]|None=None
    def to_dict(self): return asdict(self)
    def payload_dict(self):
        d=self.to_dict()
        # Search/experiment metadata is not part of the semantic payload size.
        for k in ["components","inference_mode"]: d.pop(k,None)
        return {k:v for k,v in d.items() if v is not None}
    def byte_size(self):
        return len(json.dumps(self.payload_dict(),sort_keys=True,separators=(",",":")).encode())
    @property
    def subset_key(self): return subset_key(self.components)


def build_capsule(source: SourceCapture, components, inference_mode: str) -> Capsule:
    components=tuple(components)
    bad=set(components)-set(COMPONENTS)
    if bad: raise KeyError(f"unknown components: {sorted(bad)}")
    if inference_mode not in {"explicit","hybrid"}: raise ValueError(inference_mode)
    s=ExecutionState.from_dict(source.state)
    cap=Capsule(SCHEMA_VERSION,s.workflow,s.request_id,deepcopy(s.inputs),list(components),inference_mode,
                provenance={"source_framework":source.framework,"native_snapshot_kind":source.native_snapshot.get("kind","canonical")})
    if "history" in components: cap.semantic_history=portable_history(s.trace)
    if "progress" in components:
        cap.completed=list(s.completed); cap.retry_counts=deepcopy(s.retry_counts); cap.decisions=deepcopy(s.decisions); cap.loop_counters=deepcopy(s.loop_counters)
    if "frontier" in components: cap.control_frontier=deepcopy(s.control_frontier)
    if "obligations" in components: cap.pending_obligations=deepcopy(s.pending_obligations)
    if "receipts" in components: cap.effect_receipts=deepcopy(s.effect_receipts)
    if "contract" in components: cap.continuation_contract=deepcopy(s.continuation_contract)
    return cap


def _receipt_resolves(state:ExecutionState, op:str)->bool:
    r=state.effect_receipts.get(op,{})
    return r.get("status") in {"committed","not_committed"}


def lower_capsule(cap: Capsule):
    s=ExecutionState(workflow=cap.workflow,request_id=cap.request_id,inputs=deepcopy(cap.application_state))
    if cap.semantic_history is not None: s.trace=deepcopy(cap.semantic_history)
    if cap.completed is not None: s.completed=list(cap.completed)
    if cap.retry_counts is not None: s.retry_counts=deepcopy(cap.retry_counts)
    if cap.decisions is not None: s.decisions=deepcopy(cap.decisions)
    if cap.loop_counters is not None: s.loop_counters=deepcopy(cap.loop_counters)
    if cap.control_frontier is not None: s.control_frontier=deepcopy(cap.control_frontier)
    if cap.pending_obligations is not None: s.pending_obligations=deepcopy(cap.pending_obligations)
    if cap.effect_receipts is not None: s.effect_receipts=deepcopy(cap.effect_receipts)
    if cap.continuation_contract is not None: s.continuation_contract=deepcopy(cap.continuation_contract)
    report={"mode":cap.inference_mode,"ambiguities":[],"inferred_fields":[],"unresolved_critical_facts":[]}
    if cap.inference_mode=="hybrid" and cap.semantic_history is not None:
        inf,rep=infer_semantics(cap.workflow,cap.semantic_history,static_spec(cap.workflow))
        report.update(rep); report["mode"]="history_plus_static_reconstruction"
        s=apply_inferred(s,inf,only_missing=True)
        unresolved=[]
        for a in rep.get("ambiguities",[]):
            if a.get("type")=="effect_commit_unknown":
                op=a.get("operation")
                if not _receipt_resolves(s,op): unresolved.append({"type":"effect_commit_unknown","operation":op})
        report["unresolved_critical_facts"]=unresolved
        if unresolved:
            return s,report,False,"AMBIGUOUS_EXTERNAL_COMMIT"
    return s,report,True,None
