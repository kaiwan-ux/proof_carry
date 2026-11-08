from __future__ import annotations
import json, math, sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT=Path(__file__).resolve().parents[2]
IN=ROOT/'inputs/postvalidation'; SEC=ROOT/'results/security'; OUT=ROOT/'figures/generated'; DATA=ROOT/'figures/data'
OUT.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
plt.rcParams['pdf.fonttype']=42; plt.rcParams['ps.fonttype']=42; plt.rcParams['svg.fonttype']='none'

def save(fig,name):
    for ext in ['pdf','svg','png']:
        fig.savefig(OUT/f'{name}.{ext}',bbox_inches='tight',dpi=600 if ext=='png' else None)
    plt.close(fig)

def label_clean(s):
    m={'mcc_v3':'MCC v3','mcc_v2_frozen':'MCC v2','history_inference':'History inference','aaif_reference':'AAIF reference','caplease_reference':'CapLease reference','aaif_plus_caplease_reference':'AAIF+CapLease reference','explicit_minimal':'Explicit minimal*','oracle':'Oracle*'}
    return m.get(s,s.replace('_',' ').title())

# Fig 1: conceptual mechanism (not architecture)
fig,ax=plt.subplots(figsize=(12,5)); ax.set_xlim(0,12); ax.set_ylim(0,5); ax.axis('off')
ax.text(3,4.65,'MCC v2 failure mode',ha='center',va='center',fontsize=15,fontweight='bold')
ax.text(9,4.65,'MCC v3 closed-world proof rule',ha='center',va='center',fontsize=15,fontweight='bold')
left=[('Critical fact missing',3.9),('Interpreted as “nothing pending”',2.8),('Continue anyway',1.7),('Unsafe continuation',0.6)]
right=[('Identify facts that can change next safe action',3.9),('Prove each fact from history / attestation',2.8),('All required facts proven?',1.7)]
for x,items in [(3,left),(9,right)]:
    for txt,y in items:
        box=FancyBboxPatch((x-2.15,y-0.35),4.3,0.7,boxstyle='round,pad=0.03',fill=False,linewidth=1.4)
        ax.add_patch(box); ax.text(x,y,txt,ha='center',va='center',fontsize=10.5)
    for (_,y1),(_,y2) in zip(items[:-1],items[1:]):
        ax.add_patch(FancyArrowPatch((x,y1-0.36),(x,y2+0.36),arrowstyle='-|>',mutation_scale=13,linewidth=1.2))
# branch on right
ax.add_patch(FancyArrowPatch((9,1.34),(7.8,0.75),arrowstyle='-|>',mutation_scale=13,linewidth=1.2))
ax.add_patch(FancyArrowPatch((9,1.34),(10.2,0.75),arrowstyle='-|>',mutation_scale=13,linewidth=1.2))
for x,txt in [(7.5,'YES → continue'),(10.5,'NO → reject')]:
    box=FancyBboxPatch((x-1.25,0.25),2.5,0.75,boxstyle='round,pad=0.03',fill=False,linewidth=1.4)
    ax.add_patch(box); ax.text(x,0.625,txt,ha='center',va='center',fontsize=11,fontweight='bold')
ax.plot([6,6],[0.2,4.45],linestyle='--',linewidth=1)
save(fig,'fig01_core_mechanism')

# Fig 2: unsafe rate by method
ms=pd.read_csv(IN/'method_summary.csv')
plot=ms[~ms.method.isin(['explicit_minimal','oracle'])].copy(); plot['unsafe_pct']=plot.unsafe_rate*100
plot['label']=plot.method.map(label_clean); plot=plot.sort_values('unsafe_pct')
plot[['method','unsafe','unsafe_rate']].to_csv(DATA/'fig02_unsafe_rate_methods.csv',index=False)
fig,ax=plt.subplots(figsize=(8.5,5.2)); ax.barh(plot.label,plot.unsafe_pct)
ax.set_xlabel('Unsafe continuation rate (%)'); ax.set_title('MCC v3 eliminates observed unsafe continuations on the sealed holdout')
ax.set_xlim(0,max(52,plot.unsafe_pct.max()+5));
for y,v in enumerate(plot.unsafe_pct): ax.text(v+0.8,y,f'{v:.1f}%',va='center',fontsize=9)
ax.grid(axis='x',alpha=.25); save(fig,'fig02_unsafe_rate_methods')

# Fig 3: MCC v2 -> v3 transition
runs=pd.read_csv(IN/'holdout_migration_runs.csv')
key=['case_id','evidence_variant','source','target']
def olab(d):
    return np.where(d.unsafe_violation.astype(bool),'Unsafe',np.where(d.safe_rejection.astype(bool),'Safe rejection',np.where(d.safe_completion.astype(bool),'Safe completion','Technical')))
a=runs[runs.method=='mcc_v2_frozen'][key].copy(); a['v2']=olab(runs[runs.method=='mcc_v2_frozen'])
b=runs[runs.method=='mcc_v3'][key].copy(); b['v3']=olab(runs[runs.method=='mcc_v3'])
m=a.merge(b,on=key); trans=pd.crosstab(m.v2,m.v3).reindex(index=['Safe completion','Safe rejection','Unsafe'],columns=['Safe completion','Safe rejection'],fill_value=0)
trans.to_csv(DATA/'fig03_v2_to_v3_transition.csv')
fig,ax=plt.subplots(figsize=(10,5.5)); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,6)
left={'Safe completion':4.8,'Safe rejection':3.0,'Unsafe':1.2}; right={'Safe completion':4.2,'Safe rejection':1.8}
for lab,y in left.items():
    ax.add_patch(FancyBboxPatch((.5,y-.38),2.4,.76,boxstyle='round,pad=.03',fill=False,linewidth=1.4)); ax.text(1.7,y,f'MCC v2\n{lab}',ha='center',va='center',fontsize=10)
for lab,y in right.items():
    ax.add_patch(FancyBboxPatch((7.1,y-.38),2.4,.76,boxstyle='round,pad=.03',fill=False,linewidth=1.4)); ax.text(8.3,y,f'MCC v3\n{lab}',ha='center',va='center',fontsize=10)
for l,yl in left.items():
    for r,yr in right.items():
        n=int(trans.loc[l,r])
        if n:
            lw=1+4*n/trans.values.max(); rad=.12 if yl>yr else -.12
            ax.add_patch(FancyArrowPatch((2.9,yl),(7.1,yr),arrowstyle='-|>',connectionstyle=f'arc3,rad={rad}',mutation_scale=11,linewidth=lw,alpha=.65))
            ax.text(5,(yl+yr)/2+(.25 if rad>0 else -.25),str(n),ha='center',va='center',fontsize=9)
ax.text(1.7,5.65,'Frozen MCC v2',ha='center',fontsize=13,fontweight='bold'); ax.text(8.3,5.65,'Closed-world MCC v3',ha='center',fontsize=13,fontweight='bold')
ax.text(5,.25,'All 294 MCC v2 unsafe cases become either safe completion (120) or safe rejection (174).',ha='center',fontsize=10)
save(fig,'fig03_v2_to_v3_transition')

# Fig 4 ablation stacked counts
ab=pd.read_csv(IN/'ablation_summary.csv'); order=['full_mcc_v3','minus_closed_world_gate','minus_integrity_verification','minus_identity_binding','minus_complete_snapshots','history_only','certificates_only']; ab=ab.set_index('ablation').loc[order].reset_index()
ab.to_csv(DATA/'fig04_ablation.csv',index=False)
fig,ax=plt.subplots(figsize=(10,6)); x=np.arange(len(ab)); bottom=np.zeros(len(ab))
for col,label in [('safe_completion','Safe completion'),('safe_rejection','Safe rejection'),('unsafe','Unsafe')]:
    vals=ab[col].to_numpy(); ax.bar(x,vals,bottom=bottom,label=label); bottom+=vals
ax.set_xticks(x); ax.set_xticklabels([s.replace('_','\n') for s in ab.ablation],rotation=0,fontsize=8.5); ax.set_ylabel('Evaluations (n=768 per ablation)'); ax.set_title('Ablation identifies the closed-world gate as the core safety mechanism'); ax.legend(frameon=False); ax.grid(axis='y',alpha=.2)
save(fig,'fig04_ablation_core_mechanism')

# Fig 5 forest plot unsafe-rate difference
pc=json.loads((IN/'paired_comparisons.json').read_text()); rows=[]
for r in pc:
    rows.append({'comparator':label_clean(r['comparator']),'diff_pp':100*r['unsafe_rate_diff_mcc3_minus_other'],'lo_pp':100*r['unsafe_bootstrap95']['lower'],'hi_pp':100*r['unsafe_bootstrap95']['upper'],'holm_p':r['unsafe_case_wilcoxon_holm_p']})
pd.DataFrame(rows).to_csv(DATA/'fig05_safety_forest.csv',index=False)
fig,ax=plt.subplots(figsize=(8.5,5)); y=np.arange(len(rows)); vals=np.array([r['diff_pp'] for r in rows]); lo=np.array([r['lo_pp'] for r in rows]); hi=np.array([r['hi_pp'] for r in rows]);
ax.errorbar(vals,y,xerr=[vals-lo,hi-vals],fmt='o',capsize=4); ax.axvline(0,linestyle='--',linewidth=1); ax.set_yticks(y); ax.set_yticklabels([r['comparator'] for r in rows]); ax.invert_yaxis(); ax.set_xlabel('Unsafe-rate difference: MCC v3 − comparator (percentage points)'); ax.set_title('Base-case bootstrap intervals show robust safety reduction'); ax.grid(axis='x',alpha=.2)
save(fig,'fig05_statistical_safety_forest')

# Fig 6 evidence behavior 100% stacked
ev=pd.read_csv(IN/'mccv3_by_evidence.csv'); ev['total']=ev[['safe_completion','safe_rejection','unsafe_violation','technical_failure']].sum(axis=1); ev['completion_pct']=ev.safe_completion/ev.total*100; ev['rejection_pct']=ev.safe_rejection/ev.total*100; ev['unsafe_pct']=ev.unsafe_violation/ev.total*100
ev.to_csv(DATA/'fig06_evidence_behavior.csv',index=False)
fig,ax=plt.subplots(figsize=(10,5.6)); y=np.arange(len(ev)); left=np.zeros(len(ev))
for col,label in [('completion_pct','Safe completion'),('rejection_pct','Safe rejection'),('unsafe_pct','Unsafe')]:
    v=ev[col].to_numpy(); ax.barh(y,v,left=left,label=label); left+=v
ax.set_yticks(y); ax.set_yticklabels([s.replace('_',' ') for s in ev.evidence_variant]); ax.set_xlim(0,100); ax.set_xlabel('Outcome share (%)'); ax.set_title('MCC v3 continues only when continuation-critical evidence is provable'); ax.legend(frameon=False); ax.grid(axis='x',alpha=.2)
save(fig,'fig06_evidence_behavior')

# Fig 7 family behavior
fam=pd.read_csv(IN/'mccv3_by_family.csv'); fam['total']=fam[['safe_completion','safe_rejection','unsafe_violation','technical_failure']].sum(axis=1); fam['completion_pct']=fam.safe_completion/fam.total*100; fam['rejection_pct']=fam.safe_rejection/fam.total*100; fam['unsafe_pct']=fam.unsafe_violation/fam.total*100
fam.to_csv(DATA/'fig07_family_behavior.csv',index=False)
fig,ax=plt.subplots(figsize=(9,5.6)); y=np.arange(len(fam)); left=np.zeros(len(fam))
for col,label in [('completion_pct','Safe completion'),('rejection_pct','Safe rejection'),('unsafe_pct','Unsafe')]:
    v=fam[col].to_numpy(); ax.barh(y,v,left=left,label=label); left+=v
ax.set_yticks(y); ax.set_yticklabels([s.replace('_',' ') for s in fam.family]); ax.set_xlim(0,100); ax.set_xlabel('Outcome share (%)'); ax.set_title('Zero unsafe continuation across all eight semantic families'); ax.legend(frameon=False); ax.grid(axis='x',alpha=.2)
save(fig,'fig07_family_behavior')

# Fig 8 latency
mb=json.loads((IN/'microbench.json').read_text()); perf=[]
for k,label in [('mcc_v2_total','MCC v2'),('mcc_v3_lower_total','MCC v3')]:
    t=mb['timings'][k]; perf.append({'method':label,'median_ms':t['median_us']/1000,'p95_ms':t['p95_us']/1000})
pd.DataFrame(perf).to_csv(DATA/'fig08_latency.csv',index=False)
fig,ax=plt.subplots(figsize=(6.5,4.7)); x=np.arange(2); w=.35; ax.bar(x-w/2,[r['median_ms'] for r in perf],w,label='Median'); ax.bar(x+w/2,[r['p95_ms'] for r in perf],w,label='p95'); ax.set_xticks(x); ax.set_xticklabels([r['method'] for r in perf]); ax.set_ylabel('Mechanism latency (ms)'); ax.set_title('Closed-world proof adds small absolute mechanism latency'); ax.legend(frameon=False); ax.grid(axis='y',alpha=.2)
save(fig,'fig08_latency_overhead')

# Fig 9 payload
payload=[]
for k,label in [('mcc_v2','MCC v2'),('mcc_v3','MCC v3')]:
    p=mb['payload_bytes'][k]; payload.append({'method':label,'median_bytes':p['median'],'p95_bytes':p['p95']})
pd.DataFrame(payload).to_csv(DATA/'fig09_payload.csv',index=False)
fig,ax=plt.subplots(figsize=(6.5,4.7)); ax.bar(x-w/2,[r['median_bytes'] for r in payload],w,label='Median'); ax.bar(x+w/2,[r['p95_bytes'] for r in payload],w,label='p95'); ax.set_xticks(x); ax.set_xticklabels([r['method'] for r in payload]); ax.set_ylabel('Payload size (bytes)'); ax.set_title('Safety comes with explicit proof-information overhead'); ax.legend(frameon=False); ax.grid(axis='y',alpha=.2)
save(fig,'fig09_payload_overhead')

# Fig 10 framework-pair invariance
mv=runs[runs.method=='mcc_v3'].copy(); grp=mv.groupby(['source','target'])[['safe_completion','safe_rejection','unsafe_violation']].sum().reset_index(); grp['pair']=grp.source.str.title()+' → '+grp.target.str.upper().replace({'LANGGRAPH':'LangGraph','CREWAI':'CrewAI','MAF':'MAF'})
grp.to_csv(DATA/'fig10_framework_pairs.csv',index=False)
fig,ax=plt.subplots(figsize=(8.3,5)); y=np.arange(len(grp)); left=np.zeros(len(grp))
for col,label in [('safe_completion','Safe completion'),('safe_rejection','Safe rejection'),('unsafe_violation','Unsafe')]:
    v=grp[col].to_numpy(); ax.barh(y,v,left=left,label=label); left+=v
ax.set_yticks(y); ax.set_yticklabels(grp.pair); ax.set_xlabel('MCC v3 evaluations (n=128 per directed pair)'); ax.set_title('Identical MCC v3 outcome profile across all six runtime directions'); ax.legend(frameon=False); ax.grid(axis='x',alpha=.2)
save(fig,'fig10_framework_pair_invariance')

# Fig 11 security boundary if available
secfile=SEC/'security_runs.csv'
if secfile.exists():
    sd=pd.read_csv(secfile); sg=sd.groupby(['variant','attack_class','outcome']).size().unstack(fill_value=0).reset_index(); sg.to_csv(DATA/'fig11_security_boundary.csv',index=False)
    order=['valid_control','value_tamper_no_rehash','subject_tamper_no_rehash','evidence_tamper_no_rehash','contract_hash_tamper','conflicting_valid_certificates','cross_context_replay','forged_rehash_wrong_value']; sg=sg.set_index('variant').reindex(order).fillna(0).reset_index(); y=np.arange(len(sg)); left=np.zeros(len(sg)); fig,ax=plt.subplots(figsize=(10,6))
    for col,label in [('safe_completion','Safe completion'),('safe_rejection','Safe rejection'),('unsafe','Unsafe / trust boundary')]:
        if col not in sg: sg[col]=0
        v=sg[col].to_numpy(); ax.barh(y,v,left=left,label=label); left+=v
    ax.set_yticks(y); ax.set_yticklabels([s.replace('_',' ') for s in sg.variant]); ax.set_xlabel('Security evaluations (n=96 per variant)'); ax.set_title('Integrity hashes detect mutation but do not provide issuer authentication or replay binding'); ax.legend(frameon=False, loc='center left', bbox_to_anchor=(1.01,0.5)); ax.grid(axis='x',alpha=.2); save(fig,'fig11_security_trust_boundary')

# captions
caps='''# Paper Figure Captions\n\n**Figure 1 — Core mechanism.** Conceptual contrast between MCC v2’s failure mode and MCC v3’s closed-world continuation proof rule. The figure is a mechanism schematic, not the system architecture.\n\n**Figure 2 — Unsafe continuation by method.** Unsafe continuation rates on the sealed holdout. MCC v3 observed 0/768 unsafe continuations; non-privileged reference methods retain substantial unsafe rates.\n\n**Figure 3 — MCC v2 to MCC v3 transition.** Outcome transitions for the same 768 conditions. All 294 MCC v2 unsafe outcomes are resolved by MCC v3: 120 become safe completions and 174 become safe rejections.\n\n**Figure 4 — Ablation.** Removing the closed-world proof gate reintroduces 174 unsafe continuations, while other component removals mainly reduce useful completion coverage. This is the strongest mechanism-level ablation for the core contribution.\n\n**Figure 5 — Statistical safety effect.** Base-case block-bootstrap 95% intervals for the unsafe-rate difference between MCC v3 and each non-privileged comparator. Intervals remain below zero.\n\n**Figure 6 — Evidence behavior.** MCC v3 completes evidence-sufficient, noisy-but-valid, identity-bound, and complete-negative-snapshot cases; it safely rejects missing, tampered, or semantically unbound evidence.\n\n**Figure 7 — Semantic-family behavior.** Outcome composition across eight continuation families; no unsafe MCC v3 continuation was observed in any family.\n\n**Figure 8 — Mechanism latency.** Median and p95 local mechanism latency. MCC v3 increases median processing from about 1.07 ms to 1.35 ms in the measured environment.\n\n**Figure 9 — Payload overhead.** Median and p95 transfer-payload sizes. MCC v3 carries more explicit proof information than MCC v2.\n\n**Figure 10 — Runtime-pair invariance.** All six directed LangGraph/CrewAI/MAF pairs show the same MCC v3 completion/rejection profile and zero unsafe outcomes on the sealed holdout.\n\n**Figure 11 — Security trust boundary.** Security stress test distinguishing in-model integrity corruption from out-of-model authenticated forgery/replay. Hash validation rejects non-rehashed mutations, while forged rehashed or cross-context replayed certificates expose the trusted-witness/context-binding limitation. Do not use this figure to claim cryptographic security.\n'''
(ROOT/'figures/PAPER_FIGURE_CAPTIONS.md').write_text(caps,encoding='utf-8')
print('generated figures:',len(list(OUT.glob('*.png'))))
