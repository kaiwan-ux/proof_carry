from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; G=R/'graphs'; G.mkdir(parents=True,exist_ok=True)
N=pd.read_csv(R/'native_confirmation.csv'); valid=N[N.technical_failure==0].copy()
cs=valid.groupby('condition').agg(cases=('run_id','count'),safe=('safe_completion','sum'),rejected=('migration_rejected','sum'),unsafe=('unsafe_violation','sum'),mean_bytes=('capsule_bytes','mean')).reset_index(); cs['safe_rate']=cs.safe/cs.cases; cs['rejection_rate']=cs.rejected/cs.cases; cs['unsafe_rate']=cs.unsafe/cs.cases; cs.to_csv(R/'condition_summary.csv',index=False)
wf=valid.groupby(['workflow','condition']).agg(cases=('run_id','count'),safe=('safe_completion','sum'),rejected=('migration_rejected','sum'),unsafe=('unsafe_violation','sum')).reset_index(); wf['safe_rate']=wf.safe/wf.cases; wf.to_csv(R/'workflow_summary.csv',index=False)
pair=valid.groupby(['source_framework','target_framework','condition']).agg(cases=('run_id','count'),safe=('safe_completion','sum'),rejected=('migration_rejected','sum'),unsafe=('unsafe_violation','sum')).reset_index(); pair['safe_rate']=pair.safe/pair.cases; pair.to_csv(R/'pair_summary.csv',index=False)
def row(n):
    x=cs[cs.condition==n]; return None if x.empty else x.iloc[0]
h=row('hybrid_minimal'); e=row('explicit_minimal'); f=row('full_pcc'); hi=row('history_inference')
verdict={"true_holdout":True,"frozen_candidates":True,"native_rows":len(N),"technical_failures":int(N.technical_failure.sum()),"rules":[],"claim_boundary":"Generalization only to this pre-registered hold-out suite and framework versions; not universal portability."}
for name,r in [('hybrid_minimal',h),('explicit_minimal',e),('full_pcc',f),('history_inference',hi)]:
    if r is not None: verdict[name]={"safe_rate":float(r.safe_rate),"rejection_rate":float(r.rejection_rate),"unsafe_rate":float(r.unsafe_rate),"mean_bytes":float(r.mean_bytes)}
if h is not None and h.safe_rate==1 and h.unsafe_rate==0 and h.rejection_rate==0: verdict['rules'].append('HYBRID_MINIMAL_GENERALIZES_TO_TRUE_HOLDOUT')
else: verdict['rules'].append('HYBRID_MINIMAL_FAILS_TRUE_HOLDOUT__DO_NOT_CLAIM_GENERALIZATION')
if e is not None and e.safe_rate==1 and e.unsafe_rate==0 and e.rejection_rate==0: verdict['rules'].append('EXPLICIT_MINIMAL_GENERALIZES_TO_TRUE_HOLDOUT')
else: verdict['rules'].append('EXPLICIT_MINIMAL_FAILS_TRUE_HOLDOUT__DO_NOT_CLAIM_GENERALIZATION')
if hi is not None and hi.unsafe_rate==0 and hi.rejection_rate>0: verdict['rules'].append('HISTORY_INFERENCE_REMAINS_CONSERVATIVE')
(R/'GENERALIZATION_VERDICT.json').write_text(json.dumps(verdict,indent=2),encoding='utf-8')
order=['state_only','raw_history','history_inference','hybrid_minimal','explicit_minimal','full_pcc','hybrid_minus_receipts','explicit_minus_receipts']; q=cs.set_index('condition').reindex(order).reset_index()
fig,ax=plt.subplots(figsize=(11,5)); ax.bar(q.condition,q.safe_rate); ax.set_ylim(0,1.05); ax.set_ylabel('Safe completion rate'); ax.set_title('True held-out native generalization'); ax.tick_params(axis='x',rotation=30); fig.tight_layout(); fig.savefig(G/'true_holdout_safe_completion.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(11,5)); ax.bar(q.condition,q.rejection_rate); ax.set_ylim(0,1.05); ax.set_ylabel('Safe rejection rate'); ax.set_title('True held-out conservative rejection'); ax.tick_params(axis='x',rotation=30); fig.tight_layout(); fig.savefig(G/'true_holdout_rejection.png',dpi=180); plt.close(fig)
lines=['# PortaFlow PCC v3 True Held-out Generalization Results','',f'Native rows: {len(N)}',f'Technical failures: {int(N.technical_failure.sum())}','','## Condition summary','',cs.to_markdown(index=False),'','## Verdict rules','']+[f'- {x}' for x in verdict['rules']]+['','**Candidates were frozen before this hold-out run. Do not tune them after seeing these results and still call this a hold-out test.**']
(R/'ANALYSIS_SUMMARY.md').write_text('\n'.join(lines),encoding='utf-8')
print('Analysis complete.')
