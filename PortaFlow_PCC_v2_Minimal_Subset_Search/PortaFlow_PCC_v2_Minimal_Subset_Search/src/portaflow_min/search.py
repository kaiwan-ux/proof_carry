from __future__ import annotations
import json
from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import Any
from .components import all_subsets, subset_key, COMPONENTS
from .benchmark import SCENARIOS, initial_state, source_prefix_transition, continuation_transition
from .models import SourceCapture, ExecutionState
from .capsule import build_capsule, lower_capsule
from .evaluator import evaluate

@dataclass
class SearchRow:
    workflow:str; inference_mode:str; subset_key:str; components:str; component_count:int
    safe_completion:int; migration_rejected:int; unsafe_violation:int; failure_types:str
    ambiguity_count:int; inferred_fields:int; capsule_bytes:int
    def to_dict(self): return asdict(self)


def canonical_source(workflow:str)->SourceCapture:
    ledger={}; s=source_prefix_transition(initial_state(workflow),ledger)
    return SourceCapture("canonical",workflow,s.to_dict(),{"kind":"canonical_semantic_state"},dict(ledger))


def evaluate_subset(workflow:str, components, inference_mode:str)->SearchRow:
    source=canonical_source(workflow)
    cap=build_capsule(source,components,inference_mode)
    imported,rep,accepted,reason=lower_capsule(cap)
    if not accepted:
        return SearchRow(workflow,inference_mode,subset_key(components),",".join(components),len(components),0,1,0,reason or "REJECTED",len(rep.get("ambiguities",[])),len(rep.get("inferred_fields",[])),cap.byte_size())
    ledger=dict(source.external_ledger); initial_len=len(imported.trace)
    target=continuation_transition(imported,ledger)
    ev=evaluate(ExecutionState.from_dict(source.state),target,initial_len,ledger,source.external_ledger)
    return SearchRow(workflow,inference_mode,subset_key(components),",".join(components),len(components),int(ev["safe"]),0,int(not ev["safe"]),";".join(ev["failure_types"]),len(rep.get("ambiguities",[])),len(rep.get("inferred_fields",[])),cap.byte_size())


def exhaustive_rows():
    rows=[]
    for mode in ["explicit","hybrid"]:
        for subset in all_subsets():
            for wf in SCENARIOS:
                rows.append(evaluate_subset(wf,subset,mode))
    return rows


def pareto(rows):
    # rows = aggregate dicts. Desired: zero unsafe, maximize safe coverage, then minimize rejects/components/bytes.
    eligible=[r for r in rows if r["unsafe_violations"]==0]
    out=[]
    for r in eligible:
        dominated=False
        for q in eligible:
            if q is r: continue
            no_worse=(q["safe_completions"]>=r["safe_completions"] and q["rejections"]<=r["rejections"] and q["component_count"]<=r["component_count"] and q["mean_capsule_bytes"]<=r["mean_capsule_bytes"])
            strictly=(q["safe_completions"]>r["safe_completions"] or q["rejections"]<r["rejections"] or q["component_count"]<r["component_count"] or q["mean_capsule_bytes"]<r["mean_capsule_bytes"])
            if no_worse and strictly: dominated=True; break
        if not dominated: out.append(r)
    return sorted(out,key=lambda x:(x["inference_mode"],x["component_count"],-x["safe_completions"],x["mean_capsule_bytes"],x["subset_key"]))


def choose_minimal(aggregates, mode):
    full=[r for r in aggregates if r["inference_mode"]==mode and r["safe_completions"]==len(SCENARIOS) and r["rejections"]==0 and r["unsafe_violations"]==0]
    if not full: return None
    return sorted(full,key=lambda r:(r["component_count"],r["mean_capsule_bytes"],r["subset_key"]))[0]
