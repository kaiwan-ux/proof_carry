from __future__ import annotations
import copy
def _strip(d): x=copy.deepcopy(d); x.pop('trace',None); return x
def evaluate(expected,actual):
    e,a=_strip(expected),_strip(actual)
    if e==a:return True,[]
    failures=[]
    for k in ['effects','units','approvals','callbacks','compensations','counters','decisions','finish_count']:
        if e.get(k)!=a.get(k): failures.append(k.upper()+'_MISMATCH')
    return False,failures or ['STATE_MISMATCH']
