from __future__ import annotations
import argparse, json, shutil
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from analysis.summarize import rate_summary, describe_perf, rejection_table
from analysis.statistics import paired_method_comparisons

def save_bar(df,x,y,path,title,ylabel):
    fig,ax=plt.subplots(figsize=(6.4,3.8)); ax.bar(df[x].astype(str),df[y]); ax.set_title(title); ax.set_ylabel(ylabel); ax.tick_params(axis='x',rotation=35); fig.tight_layout(); fig.savefig(path); plt.close(fig)

def run(root: Path, rawdir: Path, processed: Path):
    processed.mkdir(parents=True,exist_ok=True)
    top_tables=root/'results/tables'; top_figs=root/'results/figures'; top_tables.mkdir(parents=True,exist_ok=True); top_figs.mkdir(parents=True,exist_ok=True)
    # sealed
    sealed=pd.read_csv(rawdir/'sealed_summary.csv'); sealed.to_csv(processed/'table_1_sealed_baselines.csv',index=False); sealed.to_csv(top_tables/'table_1_baselines.csv',index=False)
    # expanded
    exp=pd.read_csv(rawdir/'expanded120.csv')
    ms=rate_summary(exp,'method'); ms.to_csv(processed/'table_2_expanded_results.csv',index=False); ms.to_csv(top_tables/'table_2_expanded_results.csv',index=False)
    fam=rate_summary(exp,['method','workflow_family']); fam.to_csv(processed/'expanded_by_family.csv',index=False)
    rej=rejection_table(exp[exp['method']=='proofcarry']); rej.to_csv(processed/'rejection_reasons.csv',index=False); rej.to_csv(top_tables/'table_7_rejection_reasons.csv',index=False)
    stats=paired_method_comparisons(exp,'unsafe_violation','proofcarry'); stats.to_csv(processed/'paired_safety_statistics.csv',index=False)
    comp=paired_method_comparisons(exp,'safe_completion','proofcarry'); comp.to_csv(processed/'paired_completion_statistics.csv',index=False)
    # ablation
    abl=pd.read_csv(rawdir/'ablation.csv'); abls=rate_summary(abl,'ablation'); abls.to_csv(processed/'table_3_ablation.csv',index=False); abls.to_csv(top_tables/'table_3_ablation.csv',index=False)
    # security
    sec=pd.read_csv(rawdir/'security.csv'); secs=rate_summary(sec,['security_mode','attack']); secs.to_csv(processed/'table_4_security.csv',index=False); secs.to_csv(top_tables/'table_4_security.csv',index=False)
    # runtime mapping
    rt=pd.read_csv(rawdir/'runtime_identity.csv'); rts=rate_summary(rt,['mapping_mode']); rts.to_csv(processed/'table_5_runtime.csv',index=False); rts.to_csv(top_tables/'table_5_runtime.csv',index=False)
    # performance
    perf=pd.read_csv(rawdir/'performance.csv'); ps=describe_perf(perf); ps.to_csv(processed/'table_6_performance.csv',index=False); ps.to_csv(top_tables/'table_6_performance.csv',index=False)
    # figures, deliberately simple and regenerated from raw data
    save_bar(ms,'method','unsafe_rate',processed/'fig_1_safety.pdf','Unsafe continuation rate','Unsafe rate')
    save_bar(ms,'method','completion_rate',processed/'fig_2_completion.pdf','Safe completion rate','Completion rate')
    save_bar(abls,'ablation','unsafe_rate',processed/'fig_3_ablation.pdf','Ablation: unsafe continuation rate','Unsafe rate')
    auth=secs[secs.security_mode=='authenticated_proofcarry']; save_bar(auth,'attack','unsafe_rate',processed/'fig_4_security.pdf','Authenticated ProofCarry under attacks','Unsafe rate')
    ptotal=ps[ps.metric=='total_ms'];
    fig,ax=plt.subplots(figsize=(4.8,3.5)); ax.bar(['median','p95','p99'],[float(ptotal['median'].iloc[0]),float(ptotal['p95'].iloc[0]),float(ptotal['p99'].iloc[0])]); ax.set_ylabel('ms'); ax.set_title('Semantic end-to-end latency'); fig.tight_layout(); fig.savefig(processed/'fig_5_latency.pdf'); plt.close(fig)
    pbytes=ps[ps.metric=='total_transferred_bytes']; fig,ax=plt.subplots(figsize=(4.8,3.5)); ax.bar(['median','p95','max'],[float(pbytes['median'].iloc[0]),float(pbytes['p95'].iloc[0]),float(pbytes['max'].iloc[0])]); ax.set_ylabel('bytes'); ax.set_title('Transferred payload size'); fig.tight_layout(); fig.savefig(processed/'fig_6_payload.pdf'); plt.close(fig)
    for i in range(1,7):
        src=processed / (f"fig_{i}_" + {1:'safety',2:'completion',3:'ablation',4:'security',5:'latency',6:'payload'}[i] + '.pdf')
        shutil.copy2(src,top_figs/src.name)
    return processed
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--rawdir',required=True); ap.add_argument('--processed',required=True); a=ap.parse_args(); run(Path(a.root),Path(a.rawdir),Path(a.processed))
