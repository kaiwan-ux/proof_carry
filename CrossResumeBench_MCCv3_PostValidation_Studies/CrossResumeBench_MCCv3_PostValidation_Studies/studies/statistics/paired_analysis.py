from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import binomtest, wilcoxon
from studies.common import ROOT, INPUT, verify_passed_holdout_inputs

SEED=20260828
PRIMARY=['mcc_v2_frozen','history_inference','aaif_reference','caplease_reference','aaif_plus_caplease_reference']

def wilson(k,n,z=1.959963984540054):
    if n==0:return [float('nan'),float('nan')]
    p=k/n; den=1+z*z/n; center=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0,center-half),min(1,center+half)]

def block_bootstrap(case_table, metric, comparator, reps=10000):
    # Vectorized base-case block bootstrap: fast and preserves the case as the sampling unit.
    rng=np.random.default_rng(SEED)
    a=case_table[f'mcc_v3_{metric}'].to_numpy(dtype=float)
    b=case_table[f'{comparator}_{metric}'].to_numpy(dtype=float)
    d=a-b; n=len(d)
    idx=rng.integers(0,n,size=(int(reps),n))
    diffs=d[idx].mean(axis=1)
    q=np.quantile(diffs,[.025,.5,.975])
    return {'lower':float(q[0]),'median':float(q[1]),'upper':float(q[2]),'reps':int(reps),'unit':'base_case'}

def exact_mcnemar(a,b):
    # a,b are binary arrays; b10 means MCC v3=1, comparator=0.
    b10=int(((a==1)&(b==0)).sum()); b01=int(((a==0)&(b==1)).sum()); n=b10+b01
    p=1.0 if n==0 else float(binomtest(min(b10,b01),n,.5,alternative='two-sided').pvalue)
    return {'mcc3_1_other_0':b10,'mcc3_0_other_1':b01,'discordant':n,'p_exact':p}

def holm(pairs):
    ordered=sorted(pairs,key=lambda x:x[1]); m=len(ordered); out={}
    running=0.0
    for rank,(name,p) in enumerate(ordered,1):
        adj=min(1.0,(m-rank+1)*p); running=max(running,adj); out[name]=running
    return out

def run(out_dir:Path, bootstrap_reps=10000):
    verify_passed_holdout_inputs(); out_dir.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(INPUT/'migration_runs.csv')
    required=6144
    if len(df)!=required: raise RuntimeError(f'Expected {required} migration rows, got {len(df)}')
    key=['source','target','case_id','evidence_variant']
    if df.duplicated(key+['method']).any(): raise RuntimeError('Duplicate paired migration rows detected')
    summaries=[]
    for method,g in df.groupby('method'):
        n=len(g); sc=int(g.safe_completion.sum()); sr=int(g.safe_rejection.sum()); u=int(g.unsafe_violation.sum()); tech=int(g.technical_failure.sum())
        summaries.append({'method':method,'n':n,'safe_completion':sc,'safe_completion_rate':sc/n,'safe_completion_wilson95':wilson(sc,n),'safe_rejection':sr,'unsafe':u,'unsafe_rate':u/n,'unsafe_wilson95':wilson(u,n),'technical':tech})
    pd.DataFrame(summaries).to_csv(out_dir/'method_summary.csv',index=False)
    piv=df.pivot(index=key,columns='method',values=['safe_completion','unsafe_violation'])
    # Base-case cluster table: each case contributes equally, preventing 768 rows being treated as independent cases.
    case_rows=[]
    for case_id,g in df.groupby('case_id'):
        r={'case_id':case_id}
        for method in ['mcc_v3']+PRIMARY:
            gm=g[g.method==method]
            r[f'{method}_unsafe']=gm.unsafe_violation.mean(); r[f'{method}_completion']=gm.safe_completion.mean()
        case_rows.append(r)
    case_table=pd.DataFrame(case_rows).set_index('case_id')
    case_table.to_csv(out_dir/'case_level_rates.csv')
    comparisons=[]; pvals_unsafe=[]; pvals_comp=[]
    for other in PRIMARY:
        a_u=piv[('unsafe_violation','mcc_v3')].astype(int).to_numpy(); b_u=piv[('unsafe_violation',other)].astype(int).to_numpy()
        a_c=piv[('safe_completion','mcc_v3')].astype(int).to_numpy(); b_c=piv[('safe_completion',other)].astype(int).to_numpy()
        mcu=exact_mcnemar(a_u,b_u); mcc=exact_mcnemar(a_c,b_c)
        # Case-level paired Wilcoxon is primary inferential test.
        du=case_table['mcc_v3_unsafe']-case_table[f'{other}_unsafe']; dc=case_table['mcc_v3_completion']-case_table[f'{other}_completion']
        wu=float(wilcoxon(du,zero_method='wilcox',alternative='two-sided').pvalue) if np.any(du!=0) else 1.0
        wc=float(wilcoxon(dc,zero_method='wilcox',alternative='two-sided').pvalue) if np.any(dc!=0) else 1.0
        pvals_unsafe.append((other,wu)); pvals_comp.append((other,wc))
        comparisons.append({'comparator':other,
            'unsafe_rate_diff_mcc3_minus_other':float(du.mean()),'unsafe_bootstrap95':block_bootstrap(case_table,'unsafe',other,bootstrap_reps),'unsafe_case_wilcoxon_p':wu,'unsafe_row_mcnemar':mcu,
            'completion_rate_diff_mcc3_minus_other':float(dc.mean()),'completion_bootstrap95':block_bootstrap(case_table,'completion',other,bootstrap_reps),'completion_case_wilcoxon_p':wc,'completion_row_mcnemar':mcc})
    hu=holm(pvals_unsafe); hc=holm(pvals_comp)
    for r in comparisons:
        r['unsafe_case_wilcoxon_holm_p']=hu[r['comparator']]; r['completion_case_wilcoxon_holm_p']=hc[r['comparator']]
    (out_dir/'paired_comparisons.json').write_text(json.dumps(comparisons,indent=2),encoding='utf-8')
    # Family and evidence tables.
    m3=df[df.method=='mcc_v3']
    m3.groupby('family')[['safe_completion','safe_rejection','unsafe_violation','technical_failure']].sum().to_csv(out_dir/'mccv3_by_family.csv')
    m3.groupby('evidence_variant')[['safe_completion','safe_rejection','unsafe_violation','technical_failure']].sum().to_csv(out_dir/'mccv3_by_evidence.csv')
    # Human report.
    ms={r['method']:r for r in summaries}; lines=['# Paired Statistical Validation','',f'Primary clustering unit: **base case (n={len(case_table)})**, not individual migration rows.','', '## MCC v3 holdout estimate',f"- Safe completion: {ms['mcc_v3']['safe_completion']}/{ms['mcc_v3']['n']} ({100*ms['mcc_v3']['safe_completion_rate']:.2f}%)",f"- Unsafe: {ms['mcc_v3']['unsafe']}/{ms['mcc_v3']['n']} ({100*ms['mcc_v3']['unsafe_rate']:.2f}%)",f"- Wilson 95% CI for unsafe rate: {100*ms['mcc_v3']['unsafe_wilson95'][0]:.3f}% to {100*ms['mcc_v3']['unsafe_wilson95'][1]:.3f}%",'', '## Paired comparisons']
    for r in comparisons:
        lines += [f"### MCC v3 vs {r['comparator']}",f"- Unsafe-rate difference: {100*r['unsafe_rate_diff_mcc3_minus_other']:.2f} percentage points (MCC v3 - comparator)",f"- Case-block bootstrap 95% CI: {100*r['unsafe_bootstrap95']['lower']:.2f} to {100*r['unsafe_bootstrap95']['upper']:.2f} pp",f"- Case-level Wilcoxon Holm-adjusted p: {r['unsafe_case_wilcoxon_holm_p']:.6g}",f"- Safe-completion-rate difference: {100*r['completion_rate_diff_mcc3_minus_other']:.2f} pp",f"- Completion block-bootstrap 95% CI: {100*r['completion_bootstrap95']['lower']:.2f} to {100*r['completion_bootstrap95']['upper']:.2f} pp",'']
    lines += ['## Interpretation boundary','These tests quantify the completed benchmark. Base-case block bootstrap/Wilcoxon are primary to reduce pseudo-replication; row-level McNemar tests are supplementary. Statistical significance does not establish external generalization beyond this benchmark.']
    (out_dir/'STATISTICAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return {'rows':len(df),'cases':len(case_table),'comparisons':len(comparisons)}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default=str(ROOT/'results'/'statistics')); ap.add_argument('--bootstrap-reps',type=int,default=10000); a=ap.parse_args(); print(json.dumps(run(Path(a.out),a.bootstrap_reps),indent=2))
