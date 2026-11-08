from __future__ import annotations
import pandas as pd, json
from pathlib import Path

def summarize(root:Path):
    r=root/'results'; out={}
    for fn,prefix in [(r/'semantic_runs.csv','semantic'),(r/'native_runs.csv','native')]:
        if not fn.exists(): continue
        df=pd.read_csv(fn)
        g=df.groupby('baseline').agg(runs=('run_id','count'),safe_completion=('safe_completion','sum'),safe_rejection=('safe_rejection','sum'),unsafe=('unsafe_violation','sum'),technical_failure=('technical_failure','sum'),mean_payload=('payload_bytes','mean')).reset_index()
        g['scc']=g.safe_completion/g.runs; g['safe_resolution']=(g.safe_completion+g.safe_rejection)/g.runs; g.to_csv(r/f'{prefix}_condition_summary.csv',index=False); out[prefix]=g.to_dict('records')
        if prefix=='native':
            p=df.groupby(['source_framework','target_framework','baseline']).agg(runs=('run_id','count'),safe_completion=('safe_completion','sum'),safe_rejection=('safe_rejection','sum'),unsafe=('unsafe_violation','sum'),technical_failure=('technical_failure','sum')).reset_index(); p.to_csv(r/'native_pair_summary.csv',index=False)
        else:
            f=df.groupby(['family','baseline']).agg(runs=('run_id','count'),safe_completion=('safe_completion','sum'),safe_rejection=('safe_rejection','sum'),unsafe=('unsafe_violation','sum')).reset_index(); f.to_csv(r/'semantic_family_summary.csv',index=False)
    (r/'RESEARCH_VERDICT.json').write_text(json.dumps({"benchmark":"CrossResumeBench v2","interpretation_rules":["MCC v2 transfers only schema-valid evidence; target reconstructs state.","AAIF/CapLease named baselines are independent concept-level reference implementations, not official artifacts.","Native source framework must be actually invoked; source capture failures are technical failures.","Safe rejection is distinct from safe completion.","No universal interoperability claim follows from this benchmark alone."],"summaries":out},indent=2),encoding='utf-8')
    return out
