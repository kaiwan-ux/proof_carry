from pathlib import Path
import csv, json, sys
from collections import Counter, defaultdict
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/"results"; GR=RES/"graphs"; GR.mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader((RES/"native_cross_runtime_runs.csv").open(encoding="utf-8")))
for r in rows:
    for k in ["safe_continuation","technical_failure","duplicate_effects","replayed_steps","approval_preserved","retry_preserved","correct_termination"]: r[k]=int(r[k])
valid=[r for r in rows if not r["technical_failure"]]

def group(keys):
    d=defaultdict(list)
    for r in valid: d[tuple(r[k] for k in keys)].append(r)
    return d

# summaries
for name,keys in [("condition_summary.csv",["condition"]),("pair_condition_summary.csv",["source_framework","target_framework","condition"]),("workflow_condition_summary.csv",["workflow","condition"])]:
    g=group(keys)
    with (RES/name).open("w",newline="",encoding="utf-8") as f:
        fields=keys+["n","safe","scr","duplicate_effects","replayed_steps"]
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for kk,rr in sorted(g.items()):
            vals=list(kk); n=len(rr); safe=sum(x["safe_continuation"] for x in rr)
            w.writerow(dict(zip(keys,vals),n=n,safe=safe,scr=round(safe/n,6),duplicate_effects=sum(x["duplicate_effects"] for x in rr),replayed_steps=sum(x["replayed_steps"] for x in rr)))

fails=Counter()
for r in valid:
    for x in filter(None,r["failure_types"].split(";")): fails[x]+=1
with (RES/"failure_taxonomy.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["failure_type","count"]); w.writerows(sorted(fails.items(),key=lambda x:(-x[1],x[0])))

# deterministic evidence: descriptive counts only, intentionally no confidence intervals.
cond=group(["condition"])
lines=["# PortaFlow Corrected Phase-0 — Native Evidence Summary","",f"Total configured rows: **{len(rows)}**",f"Valid native target runs: **{len(valid)}**",f"Technical-failure rows: **{len(rows)-len(valid)}**","","## Safe Continuation Rate (descriptive; no CI)",""]
for (c,),rr in sorted(cond.items()):
    safe=sum(x["safe_continuation"] for x in rr); lines.append(f"- **{c}**: {safe}/{len(rr)} = {safe/len(rr):.1%}")
lines += ["","## Failure taxonomy",""]+[f"- **{k}**: {v}" for k,v in fails.most_common()]
naive=[r for r in valid if r["condition"]=="naive_state"]
naive_safe=sum(r["safe_continuation"] for r in naive)
lines += ["","## Gate decision",""]
if len(naive)==18 and naive_safe>=17:
    lines.append(f"**NO-GO / PIVOT trigger:** naive_state passed {naive_safe}/18 core cases; the strong information-gap claim is not supported.")
elif len(naive)==18:
    lines.append(f"**PRELIMINARY GO:** naive_state passed {naive_safe}/18 core cases. Inspect failure mechanisms before designing PCC.")
else:
    lines.append(f"**INCOMPLETE:** expected 18 valid naive cases, observed {len(naive)}. Fix technical failures before proposal claims.")
lines += ["","## Claim boundary","","These are native framework executions at declared migration-safe boundaries. They test whether selected state representations are sufficient to continue equivalent workflows in another runtime. They do **not** yet prove arbitrary mid-instruction process migration, universal framework incompatibility, or PortaFlow/PCC effectiveness. `native_semantic` is a diagnostic privileged upper bound, not the proposed method."]
(RES/"PROPOSAL_EVIDENCE_SUMMARY.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

# plots
try:
 import matplotlib.pyplot as plt
 labels=[]; vals=[]
 for (c,),rr in sorted(cond.items()): labels.append(c); vals.append(sum(x["safe_continuation"] for x in rr)/len(rr))
 fig=plt.figure(figsize=(7,4)); ax=fig.add_subplot(111); ax.bar(labels,vals); ax.set_ylim(0,1.05); ax.set_ylabel("Safe Continuation Rate"); ax.set_title("Native Cross-Runtime Continuation by State Condition"); ax.tick_params(axis='x',rotation=20); fig.tight_layout(); fig.savefig(GR/"native_scr_by_condition.png",dpi=180); plt.close(fig)
 if fails:
  names=[x[0] for x in fails.most_common()]; counts=[x[1] for x in fails.most_common()]
  fig=plt.figure(figsize=(8,4)); ax=fig.add_subplot(111); ax.bar(names,counts); ax.set_ylabel("Failed runs"); ax.set_title("Native Failure Taxonomy"); ax.tick_params(axis='x',rotation=25); fig.tight_layout(); fig.savefig(GR/"native_failure_taxonomy.png",dpi=180); plt.close(fig)
except Exception as e:
 (RES/"graph_error.txt").write_text(str(e),encoding="utf-8")
print("Analysis complete.")
