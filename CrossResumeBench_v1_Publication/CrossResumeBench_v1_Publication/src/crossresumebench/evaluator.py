from __future__ import annotations
from collections import Counter
from .models import EvalResult,RuntimeState

def evaluate(case,target:RuntimeState|None,final_ledger:dict[str,int]|None,rejected:bool=False):
    if rejected:
        return EvalResult(0,1,0,[])
    ref=RuntimeState.from_dict(case.reference_final_state); final_ledger=final_ledger or {}
    failures=[]
    duplicate=0
    for op,expected in case.reference_final_ledger.items():
        got=final_ledger.get(op,0)
        if got>expected: duplicate += got-expected
    if duplicate: failures.append("DUPLICATE_EXTERNAL_EFFECT")
    if final_ledger!=case.reference_final_ledger: failures.append("LEDGER_MISMATCH")
    if target is None: failures.append("NO_TARGET_STATE")
    else:
        if target.outcome!=ref.outcome: failures.append("OUTCOME_MISMATCH")
        if not target.terminated: failures.append("NOT_TERMINATED")
        # replayed logical work: target trace contains a source-completed step again, excluding safe bookkeeping names
        src_state=RuntimeState.from_dict(case.source_state); src=set(src_state.completed_steps)
        new_trace=target.trace[len(src_state.trace):] if target.trace[:len(src_state.trace)]==src_state.trace else target.trace
        replay=sum(1 for x in new_trace if x in src)
        if replay: failures.append("COMPLETED_STEP_REPLAYED")
    unsafe=bool(failures)
    return EvalResult(int(not unsafe),0,int(unsafe),sorted(set(failures)),duplicate, replay if target else 0,int("LEDGER_MISMATCH" in failures),int("OUTCOME_MISMATCH" in failures))
