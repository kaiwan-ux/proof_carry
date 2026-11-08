from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; G=R/'graphs'; G.mkdir(exist_ok=True)
S=pd.read_csv(R/'subset_summary.csv'); N=pd.read_csv(R/'native_confirmation.csv'); sel=json.loads((R/'selected_native_conditions.json').read_text())
# Native condition summary
valid=N[N.technical_failure==0].copy()
ns=valid.groupby('condition').agg(cases=('run_id','count'),safe=('safe_completion','sum'),rejected=('migration_rejected','sum'),unsafe=('unsafe_violation','sum'),mean_bytes=('capsule_bytes','mean')).reset_index()
ns['safe_rate']=ns.safe/ns.cases; ns['rejection_rate']=ns.rejected/ns.cases; ns['unsafe_rate']=ns.unsafe/ns.cases
ns.to_csv(R/'native_condition_summary.csv',index=False)
wf=valid.groupby(['workflow','condition']).agg(cases=('run_id','count'),safe=('safe_completion','sum'),rejected=('migration_rejected','sum'),unsafe=('unsafe_violation','sum')).reset_index(); wf['safe_rate']=wf.safe/wf.cases; wf.to_csv(R/'native_workflow_summary.csv',index=False)
pair=valid.groupby(['source_framework','target_framework','condition']).agg(cases=('run_id','count'),safe=('safe_completion','sum'),rejected=('migration_rejected','sum'),unsafe=('unsafe_violation','sum')).reset_index(); pair['safe_rate']=pair.safe/pair.cases; pair.to_csv(R/'native_pair_summary.csv',index=False)
# candidate verdict
cand=json.loads((R/'minimal_candidates.json').read_text())
def row(name):
    x=ns[ns.condition==name]
    return None if x.empty else x.iloc[0]
hm=row('hybrid_minimal'); em=row('explicit_minimal'); full=row('full_pcc'); hist=row('history_inference')
verdict={'stage_a':cand,'native':{},'interpretation_rules':[],'claim_boundary':'Minimal on the current component vocabulary + benchmark only; not universal mathematical minimality.'}
for name,r in [('hybrid_minimal',hm),('explicit_minimal',em),('full_pcc',full),('history_inference',hist)]:
    if r is not None: verdict['native'][name]={'safe_rate':float(r.safe_rate),'rejection_rate':float(r.rejection_rate),'unsafe_rate':float(r.unsafe_rate),'mean_bytes':float(r.mean_bytes)}
if hm is not None and hm.safe_rate==1 and hm.unsafe_rate==0 and hm.rejection_rate==0:
    verdict['interpretation_rules'].append('HYBRID_MINIMAL_CONFIRMED_ON_NATIVE_HOLDOUT_MATRIX')
else: verdict['interpretation_rules'].append('HYBRID_MINIMAL_NOT_CONFIRMED__DO_NOT_CLAIM_MINIMALITY')
if em is not None and em.safe_rate==1 and em.unsafe_rate==0: verdict['interpretation_rules'].append('EXPLICIT_MINIMAL_CONFIRMED_ON_NATIVE_HOLDOUT_MATRIX')
if hm is not None and full is not None and hm.safe_rate==full.safe_rate and hm.unsafe_rate==0:
    verdict['interpretation_rules'].append('COMPACT_HYBRID_MATCHES_FULL_PCC_ON_TESTED_CASES')
if hist is not None and hist.rejection_rate>0 and hist.unsafe_rate==0: verdict['interpretation_rules'].append('HISTORY_INFERENCE_IS_SAFE_BUT_COVERAGE_LIMITED')
(R/'MINIMALITY_VERDICT.json').write_text(json.dumps(verdict,indent=2),encoding='utf-8')
# Graph 1: all 128 subsets size vs safe coverage, one figure.
fig,ax=plt.subplots(figsize=(9,6))
for mode,g in S.groupby('inference_mode'):
    ax.scatter(g.component_count,g.safe_rate,label=mode,alpha=.65)
ax.set_xlabel('Number of stored semantic component families'); ax.set_ylabel('Canonical safe completion rate'); ax.set_ylim(-.03,1.05); ax.set_title('Exhaustive 64-subset search in explicit vs hybrid modes'); ax.legend(); fig.tight_layout(); fig.savefig(G/'subset_size_vs_coverage.png',dpi=180); plt.close(fig)
# Graph 2 native selected conditions
order=[x['name'] for x in sel]; q=ns.set_index('condition').reindex(order).reset_index()
fig,ax=plt.subplots(figsize=(10,5)); ax.bar(q.condition,q.safe_rate); ax.set_ylim(0,1.05); ax.set_ylabel('Native safe completion rate'); ax.set_title('Native confirmation of minimal candidates and controls'); ax.tick_params(axis='x',rotation=35); fig.tight_layout(); fig.savefig(G/'native_safe_completion.png',dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(10,5)); ax.bar(q.condition,q.rejection_rate); ax.set_ylim(0,1.05); ax.set_ylabel('Safe rejection rate'); ax.set_title('Conservative rejection by selected conditions'); ax.tick_params(axis='x',rotation=35); fig.tight_layout(); fig.savefig(G/'native_rejections.png',dpi=180); plt.close(fig)
# Human-readable summary
lines=['# PortaFlow PCC v2 Minimal-Subset Search Results','',f"Stage-A subset/workflow rows: {8*64*2}",f"Native confirmation rows: {len(N)}",f"Technical failures: {int(N.technical_failure.sum())}",'','## Stage-A minimal candidates','',json.dumps(cand,indent=2),'','## Native condition summary','',ns.to_markdown(index=False),'','## Conservative interpretation','']
lines += [f'- {x}' for x in verdict['interpretation_rules']]
lines += ['','**Do not generalize minimality beyond the tested component vocabulary, workflows, migration boundaries, and framework versions.**']
(R/'ANALYSIS_SUMMARY.md').write_text('\n'.join(lines),encoding='utf-8')
print('Analysis complete.')
