from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

def run(root: Path, out: Path):
    src=root/'legacy_evidence/sealed_holdout_32/migration_runs.csv'
    df=pd.read_csv(src)
    summary=(df.groupby('method',dropna=False).agg(rows=('run_id','size'),safe_completion=('safe_completion','sum'),safe_rejection=('safe_rejection','sum'),unsafe=('unsafe_violation','sum'),technical=('technical_failure','sum')).reset_index())
    summary['unsafe_rate']=summary['unsafe']/summary['rows']
    summary['completion_rate']=summary['safe_completion']/summary['rows']
    summary['rejection_rate']=summary['safe_rejection']/summary['rows']
    out.parent.mkdir(parents=True,exist_ok=True); summary.to_csv(out,index=False)
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--out',required=True); a=ap.parse_args(); run(Path(a.root),Path(a.out))
