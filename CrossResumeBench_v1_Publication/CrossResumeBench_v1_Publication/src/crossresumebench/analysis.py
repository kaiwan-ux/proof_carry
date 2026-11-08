from __future__ import annotations
from pathlib import Path
import pandas as pd, json

def summarize(root:Path):
    R=root/'results'; graphs=R/'graphs'; graphs.mkdir(parents=True,exist_ok=True)
    sem=pd.read_csv(R/'semantic_runs.csv')
    summary=sem.groupby('baseline',as_index=False).agg(runs=('run_id','count'),safe_completion=('safe_completion','sum'),safe_rejection=('safe_rejection','sum'),unsafe=('unsafe_violation','sum'),mean_bytes=('payload_bytes','mean'))
    summary['safe_completion_rate']=summary.safe_completion/summary.runs
    summary['safe_resolution_rate']=(summary.safe_completion+summary.safe_rejection)/summary.runs
    summary.to_csv(R/'semantic_condition_summary.csv',index=False)
    fam=sem.groupby(['family','baseline'],as_index=False).agg(runs=('run_id','count'),safe_completion=('safe_completion','sum'),safe_rejection=('safe_rejection','sum'),unsafe=('unsafe_violation','sum'))
    fam.to_csv(R/'semantic_family_summary.csv',index=False)
    native_path=R/'native_runs.csv'
    nat_summary=None
    if native_path.exists():
        nat=pd.read_csv(native_path); good=nat[nat.technical_failure==0]
        nat_summary=good.groupby('baseline',as_index=False).agg(runs=('run_id','count'),safe_completion=('safe_completion','sum'),safe_rejection=('safe_rejection','sum'),unsafe=('unsafe_violation','sum'))
        nat_summary['safe_completion_rate']=nat_summary.safe_completion/nat_summary.runs
        nat_summary.to_csv(R/'native_condition_summary.csv',index=False)
        pair=good.groupby(['source_framework','target_framework','baseline'],as_index=False).agg(runs=('run_id','count'),safe_completion=('safe_completion','sum'),safe_rejection=('safe_rejection','sum'),unsafe=('unsafe_violation','sum'))
        pair.to_csv(R/'native_pair_summary.csv',index=False)
    verdict={"semantic":summary.to_dict(orient='records'),"native":nat_summary.to_dict(orient='records') if nat_summary is not None else None,"interpretation_rules":["AAIF and CapLease named conditions are reference abstractions unless replaced with official artifacts.","Safe rejection is not a safe completion.","No universal migration claim follows from this benchmark alone."]}
    (R/'RESEARCH_VERDICT.json').write_text(json.dumps(verdict,indent=2),encoding='utf-8')
    lines=['# CrossResumeBench v1 analysis','', '## Semantic condition summary','', summary.to_markdown(index=False)]
    if nat_summary is not None: lines += ['', '## Native confirmation summary','', nat_summary.to_markdown(index=False)]
    (R/'ANALYSIS_SUMMARY.md').write_text('\n'.join(lines),encoding='utf-8')
    # plots
    import matplotlib.pyplot as plt
    ax=summary.set_index('baseline')['safe_completion_rate'].plot(kind='bar',title='Semantic safe-completion rate'); ax.set_ylabel('rate'); plt.tight_layout(); plt.savefig(graphs/'semantic_safe_completion.png'); plt.close()
    if nat_summary is not None:
        ax=nat_summary.set_index('baseline')['safe_completion_rate'].plot(kind='bar',title='Native safe-completion rate'); ax.set_ylabel('rate'); plt.tight_layout(); plt.savefig(graphs/'native_safe_completion.png'); plt.close()
    return verdict
