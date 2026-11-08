def evaluate(expected,actual):
    e=dict(expected); a=dict(actual); e.pop('trace',None); a.pop('trace',None)
    if e==a: return True,[]
    failures=[]
    for k in ['effects','units','approvals','callbacks','compensations','counters','decisions','finish_count']:
        if e.get(k)!=a.get(k): failures.append(f'{k.upper()}_MISMATCH')
    return False,failures or ['OUTCOME_MISMATCH']
