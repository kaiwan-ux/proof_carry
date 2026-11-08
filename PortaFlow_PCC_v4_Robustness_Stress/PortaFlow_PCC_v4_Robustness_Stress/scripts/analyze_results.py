from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from portaflow_robust.benchmark import split_case
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; G=R/'graphs'; G.mkdir(parents=True,exist_ok=True)
N=pd.read_csv(R/'native_confirmation.csv'); valid=N[N.technical_failure==0].copy(); valid[['base_workflow','profile']]=valid['workflow'].apply(lambda x:pd.Series(split_case(x)))
cs=valid.groupby('condition').agg(cases=('run_id','count'),safe=('safe_completion','sum'),rejected=('migration_rejected','sum'),unsafe=('unsafe_violation','sum'),mean_bytes=('capsule_bytes','mean')).reset_index(); cs['safe_rate']=cs.safe/cs.cases; cs['rejection_rate']=cs.rejected/cs.cases; cs['unsafe_rate']=cs.unsafe/cs.cases; cs['safety_rate']=(cs.safe+cs.rejected)/cs.cases; cs.to_csv(R/'condition_summary.csv',index=False)
ps=valid.groupby(['profile','condition']).agg(cases=('run_id','count'),safe=('safe_completion','sum'),rejected=('migration_rejected','sum'),unsafe=('unsafe_violation','sum')).reset_index(); ps['safe_rate']=ps.safe/ps.cases; ps['rejection_rate']=ps.rejected/ps.cases; ps['unsafe_rate']=ps.unsafe/ps.cases; ps['safety_rate']=(ps.safe+ps.rejected)/ps.cases; ps.to_csv(R/'profile_condition_summary.csv',index=False)
ws=valid.groupby(['base_workflow','profile','condition']).agg(cases=('run_id','count'),safe=('safe_completion','sum'),rejected=('migration_rejected','sum'),unsafe=('unsafe_violation','sum')).reset_index(); ws['safe_rate']=ws.safe/ws.cases; ws.to_csv(R/'workflow_profile_summary.csv',index=False)
pair=valid.groupby(['source_framework','target_framework','condition']).agg(cases=('run_id','count'),safe=('safe_completion','sum'),rejected=('migration_rejected','sum'),unsafe=('unsafe_violation','sum')).reset_index(); pair['safe_rate']=pair.safe/pair.cases; pair.to_csv(R/'pair_summary.csv',index=False)
# Failure taxonomy
fails=[]
for _,r in valid.iterrows():
    if isinstance(r.failure_types,str) and r.failure_types:
        for f in r.failure_types.split(';'): fails.append({'condition':r.condition,'profile':r.profile,'failure_type':f})
pd.DataFrame(fails).to_csv(R/'failure_events.csv',index=False)

def cell(cond,profile):
    q=ps[(ps.condition==cond)&(ps.profile==profile)]; return None if q.empty else q.iloc[0]
verdict={'experiment':'v4 robustness stress','native_rows':len(N),'technical_failures':int(N.technical_failure.sum()),'frozen_candidates':True,'rules':[],'claim_boundary':'Robustness to these pre-registered evidence perturbations and workflow families only; not universal portability.'}
for cond in ['history_inference','hybrid_minimal','explicit_minimal','full_pcc']:
    verdict[cond]={}
    for prof in sorted(valid.profile.unique()):
        r=cell(cond,prof)
        if r is not None: verdict[cond][prof]={'safe_rate':float(r.safe_rate),'rejection_rate':float(r.rejection_rate),'unsafe_rate':float(r.unsafe_rate),'safety_rate':float(r.safety_rate)}
# Rules focus on safety, not forced completion.
for cond in ['hybrid_minimal','explicit_minimal','full_pcc']:
    q=ps[ps.condition==cond]
    if (q.unsafe==0).all(): verdict['rules'].append(f'{cond.upper()}__ZERO_UNSAFE_ACROSS_ALL_PROFILES')
    else: verdict['rules'].append(f'{cond.upper()}__UNSAFE_FAILURES_PRESENT')
# Expected robust behavior: hybrid survives noise/order; explicit survives all history corruption; receipt conflicts should be rejected by receipt-bearing candidates.
for prof in ['baseline','noise_duplicate','out_of_order']:
    r=cell('hybrid_minimal',prof)
    if r is not None and r.safe_rate==1: verdict['rules'].append(f'HYBRID_COMPLETES_{prof.upper()}')
r=cell('history_inference','partial_history_loss')
if r is not None and r.unsafe_rate==0: verdict['rules'].append('PARTIAL_HISTORY_LOSS_IS_FAIL_CLOSED_FOR_INFERENCE')
for cond in ['hybrid_minimal','explicit_minimal','full_pcc']:
    r=cell(cond,'receipt_conflict')
    if r is not None and r.unsafe_rate==0 and r.rejection_rate>0: verdict['rules'].append(f'{cond.upper()}_DETECTS_RECEIPT_CONFLICT')
(R/'ROBUSTNESS_VERDICT.json').write_text(json.dumps(verdict,indent=2),encoding='utf-8')
# graphs
pivot=ps.pivot(index='profile',columns='condition',values='safe_rate').fillna(0)
fig,ax=plt.subplots(figsize=(12,5)); pivot.plot(kind='bar',ax=ax); ax.set_ylim(0,1.05); ax.set_ylabel('Safe completion rate'); ax.set_title('PortaFlow v4 robustness: safe completion by evidence perturbation'); fig.tight_layout(); fig.savefig(G/'safe_completion_by_profile.png',dpi=180); plt.close(fig)
pivot=ps.pivot(index='profile',columns='condition',values='rejection_rate').fillna(0)
fig,ax=plt.subplots(figsize=(12,5)); pivot.plot(kind='bar',ax=ax); ax.set_ylim(0,1.05); ax.set_ylabel('Safe rejection rate'); ax.set_title('PortaFlow v4 robustness: conservative rejection'); fig.tight_layout(); fig.savefig(G/'rejection_by_profile.png',dpi=180); plt.close(fig)
pivot=ps.pivot(index='profile',columns='condition',values='unsafe_rate').fillna(0)
fig,ax=plt.subplots(figsize=(12,5)); pivot.plot(kind='bar',ax=ax); ax.set_ylim(0,1.05); ax.set_ylabel('Unsafe rate'); ax.set_title('PortaFlow v4 robustness: unsafe continuation'); fig.tight_layout(); fig.savefig(G/'unsafe_by_profile.png',dpi=180); plt.close(fig)
lines=['# PortaFlow PCC v4 Robustness Stress Results','',f'Native rows: {len(N)}',f'Technical failures: {int(N.technical_failure.sum())}','','## Overall condition summary','',cs.to_markdown(index=False),'','## Profile × condition summary','',ps.to_markdown(index=False),'','## Verdict rules','']+[f'- {x}' for x in verdict['rules']]
(R/'ANALYSIS_SUMMARY.md').write_text('\n'.join(lines),encoding='utf-8'); print('Analysis complete.')
