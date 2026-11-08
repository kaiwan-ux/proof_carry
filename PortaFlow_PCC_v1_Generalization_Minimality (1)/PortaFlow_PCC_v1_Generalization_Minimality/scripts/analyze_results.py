from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/"results"; G=R/"graphs"; G.mkdir(exist_ok=True)
df=pd.read_csv(R/"generalization_runs.csv")
valid=df[df.technical_failure==0].copy()
summary=valid.groupby("condition").agg(
    cases=("run_id","count"), safe_completions=("safe_completion","sum"), rejections=("migration_rejected","sum"), unsafe_violations=("unsafe_violation","sum"),
    mean_ambiguities=("ambiguity_count","mean"), mean_inferred_fields=("inferred_fields","mean"), mean_capsule_bytes=("capsule_bytes","mean")
).reset_index()
summary["safe_completion_rate"]=summary.safe_completions/summary.cases
summary["rejection_rate"]=summary.rejections/summary.cases
summary["unsafe_violation_rate"]=summary.unsafe_violations/summary.cases
summary.to_csv(R/"condition_summary.csv",index=False)
wf=valid.groupby(["workflow","condition"]).agg(cases=("run_id","count"),safe=("safe_completion","sum"),rejected=("migration_rejected","sum"),unsafe=("unsafe_violation","sum")).reset_index(); wf["safe_rate"]=wf.safe/wf.cases; wf.to_csv(R/"workflow_condition_summary.csv",index=False)
pair=valid.groupby(["source_framework","target_framework","condition"]).agg(cases=("run_id","count"),safe=("safe_completion","sum"),rejected=("migration_rejected","sum"),unsafe=("unsafe_violation","sum")).reset_index(); pair["safe_rate"]=pair.safe/pair.cases; pair.to_csv(R/"framework_pair_summary.csv",index=False)
# Leave-one-out minimality relative to full PCC.
full=float(summary.loc[summary.condition=="full_pcc_v1","safe_completion_rate"].iloc[0]) if (summary.condition=="full_pcc_v1").any() else 0
loo=summary[summary.condition.str.startswith("pcc_minus_")].copy(); loo["drop_vs_full"]=full-loo.safe_completion_rate; loo.to_csv(R/"leave_one_out_summary.csv",index=False)
# Failure taxonomy.
fail=[]
for x in valid.failure_types.fillna(""):
    for y in str(x).split(";"):
        if y and y!="nan": fail.append(y)
pd.Series(fail).value_counts().rename_axis("failure_type").reset_index(name="count").to_csv(R/"failure_taxonomy.csv",index=False)
# Charts, one figure each and no custom colors/styles.
order=list(json.loads((ROOT/"config"/"experiment.json").read_text())["conditions"])
s=summary.set_index("condition").reindex(order).reset_index()
fig,ax=plt.subplots(figsize=(10,5)); ax.bar(s.condition,s.safe_completion_rate); ax.set_ylim(0,1.05); ax.set_ylabel("Safe completion rate"); ax.set_title("Safe continuation coverage by representation"); ax.tick_params(axis="x",rotation=35); fig.tight_layout(); fig.savefig(G/"safe_completion_by_condition.png",dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(10,5)); ax.bar(s.condition,s.rejection_rate); ax.set_ylim(0,1.05); ax.set_ylabel("Rejection rate"); ax.set_title("Safe rejection / ambiguity by representation"); ax.tick_params(axis="x",rotation=35); fig.tight_layout(); fig.savefig(G/"rejection_by_condition.png",dpi=180); plt.close(fig)
fig,ax=plt.subplots(figsize=(10,5)); ax.bar(s.condition,s.unsafe_violation_rate); ax.set_ylim(0,1.05); ax.set_ylabel("Unsafe violation rate"); ax.set_title("Unsafe continuation violations by representation"); ax.tick_params(axis="x",rotation=35); fig.tight_layout(); fig.savefig(G/"unsafe_violation_by_condition.png",dpi=180); plt.close(fig)
if not loo.empty:
    fig,ax=plt.subplots(figsize=(9,5)); ax.bar(loo.condition,loo.drop_vs_full); ax.set_ylabel("Safe-completion drop vs full PCC"); ax.set_title("Leave-one-component-out minimality test"); ax.tick_params(axis="x",rotation=35); fig.tight_layout(); fig.savefig(G/"leave_one_out_drop.png",dpi=180); plt.close(fig)
# Research verdict with deliberately conservative language.
hist=summary[summary.condition=="history_inference"].iloc[0]
verdict={"full_pcc_safe_rate":full,"history_inference_safe_rate":float(hist.safe_completion_rate),"history_inference_rejection_rate":float(hist.rejection_rate),"history_inference_unsafe_rate":float(hist.unsafe_violation_rate),"minimality":{r.condition:float(r.drop_vs_full) for r in loo.itertuples()},"interpretation_rules":[]}
if full<0.9: verdict["interpretation_rules"].append("PCC_V1_GENERALIZATION_WEAK")
else: verdict["interpretation_rules"].append("PCC_V1_GENERALIZATION_SUPPORTED_ON_HOLDOUT_SUITE")
if float(hist.safe_completion_rate)>=full-0.05 and float(hist.rejection_rate)<=0.05: verdict["interpretation_rules"].append("HISTORY_INFERENCE_MATCHES_PCC__SIMPLIFY_OR_PIVOT")
elif float(hist.unsafe_violation_rate)==0 and float(hist.rejection_rate)>0: verdict["interpretation_rules"].append("PCC_VALUE_MAY_BE_SAFE_COVERAGE_OVER_CONSERVATIVE_INFERENCE")
if loo.drop_vs_full.max()<=0.01: verdict["interpretation_rules"].append("NO_COMPONENT_MINIMALITY_EVIDENCE__PCC_MAY_BE_OVER_SPECIFIED")
(R/"RESEARCH_VERDICT.json").write_text(json.dumps(verdict,indent=2),encoding="utf-8")
lines=["# PCC v1 Generalization + Minimality Results","",f"Total configured rows: {len(df)}",f"Technical failures: {int(df.technical_failure.sum())}","","## Condition summary","",summary.to_markdown(index=False),"","## Leave-one-out minimality","",loo.to_markdown(index=False) if not loo.empty else "No LOO data.","","## Conservative verdict","","- "+"\n- ".join(verdict["interpretation_rules"]),"","**Do not claim universal portability or mathematical minimality from this experiment alone.**"]
(R/"ANALYSIS_SUMMARY.md").write_text("\n".join(lines),encoding="utf-8")
print("Analysis complete.")
