from __future__ import annotations
from .models import EvalResult

def evaluate(case,capture,target,rejected=False):
    if rejected: return EvalResult(0,1,0,[])
    fail=[]; dup=wrongledger=replayed=missing=0
    expected=set(case.expected_semantic_units); done=set(target.completed_units)
    missing_units=expected-done
    if missing_units: fail.append("REQUIRED_SEMANTIC_UNIT_MISSING"); missing=len(missing_units)
    source_done=set(capture.truth_completed_units)
    for x in target.executed_units:
        clean=x.split(":",1)[-1] if x.startswith("reconcile:") else x
        if clean in source_done and not x.startswith("reconcile:"):
            replayed+=1
    if replayed: fail.append("COMPLETED_SEMANTIC_UNIT_REPLAYED")
    for op,exp in case.expected_effect_counts.items():
        got=target.final_ledger.get(op,0)
        if got>exp: dup+=got-exp
        if got!=exp: wrongledger+=1
    if dup: fail.append("DUPLICATE_EXTERNAL_EFFECT")
    if wrongledger: fail.append("LEDGER_MISMATCH")
    if target.outcome!="done": fail.append("OUTCOME_MISMATCH")
    if not target.terminated: fail.append("NOT_TERMINATED")
    return EvalResult(int(not fail),0,int(bool(fail)),sorted(set(fail)),dup,replayed,missing,wrongledger,int(target.outcome!="done"))
