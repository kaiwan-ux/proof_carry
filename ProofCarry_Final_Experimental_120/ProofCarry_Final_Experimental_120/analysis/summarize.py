from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd

def rate_summary(df, group):
    s=df.groupby(group,dropna=False).agg(rows=('case_id','size'),safe_completion=('safe_completion','sum'),safe_rejection=('safe_rejection','sum'),unsafe=('unsafe_violation','sum')).reset_index()
    for n,col in [('completion_rate','safe_completion'),('rejection_rate','safe_rejection'),('unsafe_rate','unsafe')]: s[n]=s[col]/s['rows']
    return s

def describe_perf(df):
    metrics=['capture_ms','evidence_ms','signing_ms','serialization_ms','transfer_ms','verification_ms','proof_ms','translation_ms','resume_ms','total_ms','raw_checkpoint_bytes','evidence_bytes','certificate_bytes','total_transferred_bytes']
    rows=[]
    for m in metrics:
        x=df[m].dropna().astype(float).to_numpy()
        rows.append({'metric':m,'n':len(x),'mean':float(np.mean(x)),'std':float(np.std(x,ddof=1)) if len(x)>1 else 0.0,'min':float(np.min(x)),'median':float(np.median(x)),'p95':float(np.quantile(x,.95)),'p99':float(np.quantile(x,.99)),'max':float(np.max(x))})
    return pd.DataFrame(rows)

def rejection_table(df, reason_col='reason'):
    r=df[df['safe_rejection']==1][reason_col].fillna('').replace('', 'UNSPECIFIED').value_counts().rename_axis('rejection_reason').reset_index(name='count')
    r['percentage']=r['count']/r['count'].sum() if len(r) else 0
    return r
