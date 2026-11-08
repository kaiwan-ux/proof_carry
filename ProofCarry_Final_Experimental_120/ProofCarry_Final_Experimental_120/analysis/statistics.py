from __future__ import annotations
import math
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import wilcoxon

def bootstrap_paired_ci(a,b,blocks=10000,seed=20260830):
    a=np.asarray(a,float); b=np.asarray(b,float); d=a-b
    rng=np.random.default_rng(seed); n=len(d)
    if n==0: return (float('nan'),float('nan'),float('nan'))
    vals=np.empty(blocks)
    for i in range(blocks):
        idx=rng.integers(0,n,size=n); vals[i]=d[idx].mean()
    return float(d.mean()), float(np.quantile(vals,.025)), float(np.quantile(vals,.975))

def rank_biserial(d):
    d=np.asarray(d,float); d=d[d!=0]
    if len(d)==0:return 0.0
    ranks=pd.Series(np.abs(d)).rank(method='average').to_numpy()
    pos=ranks[d>0].sum(); neg=ranks[d<0].sum()
    return float((pos-neg)/(pos+neg)) if pos+neg else 0.0

def holm(pvals):
    n=len(pvals); order=np.argsort(pvals); out=np.empty(n); prev=0
    for rank,idx in enumerate(order):
        adj=min(1.0,(n-rank)*pvals[idx]); adj=max(adj,prev); out[idx]=adj; prev=adj
    return out.tolist()

def paired_method_comparisons(df, metric='unsafe_violation', focal='proofcarry'):
    # Primary unit = base case. Runtime pairs / variants are aggregated within each case, not treated as independent samples.
    case=df.groupby(['case_id','method'])[metric].mean().unstack('method')
    rows=[]; raw=[]
    for other in case.columns:
        if other==focal: continue
        sub=case[[focal,other]].dropna(); a=sub[focal].to_numpy(); b=sub[other].to_numpy(); d=a-b
        mean,lo,hi=bootstrap_paired_ci(a,b)
        try:
            p=float(wilcoxon(d,zero_method='zsplit',alternative='two-sided').pvalue)
        except Exception: p=1.0
        raw.append(p); rows.append({'focal':focal,'other':other,'n_base_cases':len(d),'metric':metric,'mean_difference':mean,'ci95_low':lo,'ci95_high':hi,'rank_biserial':rank_biserial(d),'p_raw':p})
    adj=holm(raw) if raw else []
    for r,p in zip(rows,adj): r['p_holm']=p
    return pd.DataFrame(rows)
