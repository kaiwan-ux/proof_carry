from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/"config/phase1_revisionC.json").read_text(encoding="utf-8"))
selfdf=pd.read_csv(ROOT/"results/self_resume.csv")
src=pd.read_csv(ROOT/"results/source_capture_results.csv")
rows=pd.read_csv(ROOT/"results/phase1_runs.csv")
errs=[]

if len(selfdf)!=cfg["expected_self_resume_rows"]: errs.append(f"self rows {len(selfdf)} != 3")
if len(src)!=cfg["expected_source_capture_rows"]: errs.append(f"source rows {len(src)} != 6")
if len(rows)!=cfg["expected_migration_rows"]: errs.append(f"migration rows {len(rows)} != 72")
if rows.run_id.nunique()!=len(rows): errs.append("duplicate migration run ids")
if selfdf.run_id.nunique()!=len(selfdf): errs.append("duplicate self run ids")
if src.source_id.nunique()!=len(src): errs.append("duplicate source ids")

for col in ["safe_completion","safe_rejection","unsafe_violation","technical_failure"]:
    if col not in rows.columns: errs.append(f"missing column {col}")
if not errs:
    sums=rows[["safe_completion","safe_rejection","unsafe_violation","technical_failure"]].fillna(0).astype(int).sum(axis=1)
    bad=(sums!=1)
    if bad.any(): errs.append(f"{int(bad.sum())} migration rows do not have exactly one terminal outcome")

expected_methods={"mcc_v2":24,"oracle":24,"explicit_minimal":24}
if not errs:
    got=rows.method.value_counts().to_dict()
    for k,v in expected_methods.items():
        if int(got.get(k,0))!=v: errs.append(f"method {k} rows {got.get(k,0)} != {v}")

for source in cfg["frameworks"]:
    for target in cfg["frameworks"]:
        if source==target: continue
        pair=rows[(rows.source==source)&(rows.target==target)]
        if len(pair)!=12: errs.append(f"pair {source}->{target} rows {len(pair)} != 12")

if not (ROOT/"results/PHASE1_REVISIONC_GATE.json").exists(): errs.append("missing PHASE1_REVISIONC_GATE.json")
if errs: raise SystemExit("INTEGRITY FAIL: "+"; ".join(errs))
print("PASS: complete, internally consistent result structure. Scientific gate may be PASS or FAIL; either outcome is exportable.")
