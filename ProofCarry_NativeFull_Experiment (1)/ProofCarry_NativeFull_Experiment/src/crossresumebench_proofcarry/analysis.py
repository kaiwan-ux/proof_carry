from __future__ import annotations
import json,math
from pathlib import Path
import pandas as pd
from scipy.stats import wilcoxon
import numpy as np

def method_summary(df):
    if df.empty: return pd.DataFrame()
    g=df.groupby('method',dropna=False).agg(rows=('run_id','count'),safe_completion=('safe_completion','sum'),safe_rejection=('safe_rejection','sum'),unsafe=('unsafe_violation','sum'),technical=('technical_failure','sum')).reset_index()
    for c in ['safe_completion','safe_rejection','unsafe','technical']: g[c+'_rate']=g[c]/g['rows']
    return g

def block_bootstrap_diff(df,a,b,metric='unsafe_violation',B=5000,seed=104):
    piv=df[df.method.isin([a,b])].groupby(['case_id','method'])[metric].mean().unstack('method').dropna(); cases=piv.index.to_numpy(); rng=np.random.default_rng(seed); vals=[]
    for _ in range(B):
        sm=rng.choice(cases,size=len(cases),replace=True); vals.append(float((piv.loc[sm,a]-piv.loc[sm,b]).mean()))
    return {'difference':float((piv[a]-piv[b]).mean()),'ci95':[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))],'n_cases':int(len(cases))}

def paired_case_test(df,a,b,metric):
    piv=df[df.method.isin([a,b])].groupby(['case_id','method'])[metric].mean().unstack('method').dropna()
    if len(piv)==0: return None
    diff=(piv[a]-piv[b]).to_numpy()
    nz=diff[diff!=0]
    if len(nz)==0: p=1.0
    else:
        try: p=float(wilcoxon(diff,zero_method='wilcox',alternative='two-sided').pvalue)
        except ValueError: p=1.0
    boot=block_bootstrap_diff(df,a,b,metric)
    return {'method_a':a,'method_b':b,'metric':metric,'n_cases':int(len(piv)),'mean_difference':float(diff.mean()),'ci95_low':boot['ci95'][0],'ci95_high':boot['ci95'][1],'p_raw':p}

def holm_adjust(records):
    valid=[(i,r['p_raw']) for i,r in enumerate(records) if r is not None]
    m=len(valid); order=sorted(valid,key=lambda x:x[1]); running=0.0
    adjusted=[None]*len(records)
    for rank,(idx,p) in enumerate(order):
        val=min(1.0,(m-rank)*p); running=max(running,val); adjusted[idx]=running
    for i,r in enumerate(records):
        if r is not None: r['p_holm']=adjusted[i]
    return [r for r in records if r is not None]

def analyze(results):
    results=Path(results); out={}
    sem=results/'semantic_runs.csv'
    if sem.exists():
        df=pd.read_csv(sem).fillna(0); ms=method_summary(df); ms.to_csv(results/'method_summary.csv',index=False); out['methods']=ms.to_dict(orient='records')
        planned=[]
        contrasts=[('proofcarry','legacy_permissive','unsafe_violation'),('proofcarry','history_only','unsafe_violation'),('proofcarry','always_reject','safe_completion')]
        for a,b,m in contrasts:
            if set([a,b]).issubset(set(df.method)): planned.append(paired_case_test(df,a,b,m))
        out['planned_case_level_tests']=holm_adjust(planned)
        if out['planned_case_level_tests']: pd.DataFrame(out['planned_case_level_tests']).to_csv(results/'case_level_contrasts.csv',index=False)
    sec=results/'security_runs.csv'
    if sec.exists():
        d=pd.read_csv(sec).fillna(0); out['security']={'rows':len(d),'by_method':d.groupby('method').agg(rows=('case_id','count'),unsafe=('unsafe','sum'),technical=('technical_failure','sum') if 'technical_failure' in d else ('unsafe','sum')).reset_index().to_dict(orient='records'),'by_method_attack':d.groupby(['method','attack']).agg(rows=('case_id','count'),unsafe=('unsafe','sum')).reset_index().to_dict(orient='records')}
    abl=results/'ablation_runs.csv'
    if abl.exists():
        d=pd.read_csv(abl).fillna(0);
        if 'technical_failure' not in d: d['technical_failure']=0
        out['ablations']=d.groupby('ablation').agg(rows=('run_id','count'),safe_completion=('safe_completion','sum'),safe_rejection=('safe_rejection','sum'),unsafe=('unsafe','sum'),technical=('technical_failure','sum')).reset_index().to_dict(orient='records')
    perf=results/'performance_runs.csv'
    if perf.exists():
        d=pd.read_csv(perf).fillna(0); good=d[d['technical_failure']==0] if 'technical_failure' in d else d; cols=['capture_ms','evidence_ms','proof_ms','serialize_ms','loopback_network_ms','resume_ms','method_path_ms','estimated_end_to_end_ms','payload_bytes','native_checkpoint_bytes','native_pause_metadata_bytes','proof_peak_bytes']; out['performance']={};
        for method,g in good.groupby('method'):
            out['performance'][method]={c:{'median':float(g[c].median()),'p95':float(g[c].quantile(.95))} for c in cols if c in g and len(g)}
    nat=results/'native_runs.csv'; src=results/'native_source_captures.csv'
    if nat.exists() and src.exists():
        nd=pd.read_csv(nat).fillna(0); sd=pd.read_csv(src).fillna(0); pc=nd[nd.method=='proofcarry'].groupby(['source','case_id'],as_index=False).agg(proofcarry_payload_bytes=('payload_bytes','median')); eff=pc.merge(sd[['framework','case_id','native_checkpoint_bytes','native_pause_metadata_bytes','checkpoint_measurement_kind']],left_on=['source','case_id'],right_on=['framework','case_id'],how='left'); eff['payload_to_checkpoint_ratio']=eff.apply(lambda r:(r.proofcarry_payload_bytes/r.native_checkpoint_bytes) if r.native_checkpoint_bytes>0 else float('nan'),axis=1); eff['payload_to_pause_metadata_ratio']=eff.apply(lambda r:(r.proofcarry_payload_bytes/r.native_pause_metadata_bytes) if r.native_pause_metadata_bytes>0 else float('nan'),axis=1); eff.to_csv(results/'evidence_efficiency.csv',index=False); out['evidence_efficiency']={'rows':int(len(eff)),'median_payload_bytes':float(eff.proofcarry_payload_bytes.median()),'checkpoint_comparable_rows':int((eff.native_checkpoint_bytes>0).sum()),'median_payload_to_checkpoint_ratio':float(eff.loc[eff.native_checkpoint_bytes>0,'payload_to_checkpoint_ratio'].median()) if (eff.native_checkpoint_bytes>0).any() else None}
    (results/'ANALYSIS_SUMMARY.json').write_text(json.dumps(out,indent=2,sort_keys=True),encoding='utf-8')
    lines=['# ProofCarry-120 Analysis','']
    if 'methods' in out:
        lines += ['## Main method summary','',pd.DataFrame(out['methods']).to_markdown(index=False),'']
    if 'planned_case_level_tests' in out and out['planned_case_level_tests']: lines += ['## Planned case-level contrasts','',pd.DataFrame(out['planned_case_level_tests']).to_markdown(index=False),'']
    if 'security' in out: lines += ['## Security','',pd.DataFrame(out['security']['by_method']).to_markdown(index=False),'']
    if 'ablations' in out: lines += ['## Ablations','',pd.DataFrame(out['ablations']).to_markdown(index=False),'']
    if 'performance' in out:
        lines += ['## Performance','']
        for method,vals in out['performance'].items(): lines += [f'### {method}',pd.DataFrame(vals).T.to_markdown(),'']
    (results/'ANALYSIS_SUMMARY.md').write_text('\n'.join(lines),encoding='utf-8'); return out
