from __future__ import annotations
from collections import Counter
from typing import Any
from .models import ExecutionState
from .benchmark import continuation_transition


def _event_signature(e):
    return (e.get("kind"),e.get("step"),tuple(sorted((e.get("detail") or {}).items())))

def evaluate(source:ExecutionState,target:ExecutionState,initial_target_trace_len:int,final_ledger:dict[str,int],source_ledger:dict[str,int])->dict[str,Any]:
    # Oracle continuation is generated from the FULL source semantic state, not from the tested representation.
    oracle_ledger=dict(source_ledger); oracle=continuation_transition(source.clone(),oracle_ledger)
    oracle_new=oracle.trace[len(source.trace):]
    actual_new=target.trace[initial_target_trace_len:]
    failures=[]
    wrong_ledger=int(final_ledger!=oracle_ledger)
    wrong_outcome=int((target.outcome,target.terminated)!=(oracle.outcome,oracle.terminated))
    # Compare action/event kinds+steps; ignore incidental target event counters.
    o=[(e.get("kind"),e.get("step")) for e in oracle_new]; a=[(e.get("kind"),e.get("step")) for e in actual_new]
    wrong_trace=int(a!=o)
    if wrong_ledger: failures.append("LEDGER_MISMATCH")
    if wrong_outcome: failures.append("OUTCOME_MISMATCH")
    if wrong_trace: failures.append("CONTINUATION_TRACE_MISMATCH")
    # Explicit safety diagnostics.
    duplicate_effects=sum(max(0,final_ledger.get(k,0)-oracle_ledger.get(k,0)) for k in set(final_ledger)|set(oracle_ledger))
    if duplicate_effects: failures.append("DUPLICATE_EXTERNAL_EFFECT")
    # A repeated step is unsafe only when the oracle does NOT intentionally replay it.
    # This matters for explicitly replay-safe/idempotent effects.
    src_steps=Counter(source.completed)
    target_new_steps=Counter(e.get("step") for e in actual_new if e.get("kind")=="step_completed")
    oracle_new_steps=Counter(e.get("step") for e in oracle_new if e.get("kind")=="step_completed")
    replayed=0
    for k in src_steps:
        unexpected=max(0,target_new_steps[k]-oracle_new_steps[k])
        replayed += min(src_steps[k],unexpected)
    if replayed: failures.append("COMPLETED_STEP_REPLAYED")
    safe=not failures
    return {"safe":safe,"failure_types":sorted(set(failures)),"duplicate_effects":duplicate_effects,"replayed_steps":replayed,"wrong_outcome":wrong_outcome,"wrong_ledger":wrong_ledger,"wrong_trace":wrong_trace,"oracle_new":oracle_new,"actual_new":actual_new,"oracle_ledger":oracle_ledger}
