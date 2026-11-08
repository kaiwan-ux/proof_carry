from __future__ import annotations
import copy

def _strip_trace(d):
    x=copy.deepcopy(d); x.pop("trace",None); return x

def evaluate(expected,actual):
    e=_strip_trace(expected); a=_strip_trace(actual)
    if e==a: return True,[]
    failures=[]
    for key in ["effects","units","approvals","callbacks","compensations","counters","decisions","finish_count"]:
        if e.get(key)!=a.get(key): failures.append(f"{key.upper()}_MISMATCH")
    return False,failures or ["STATE_MISMATCH"]
