from pathlib import Path
import json,pandas as pd
ROOT=Path(__file__).resolve().parents[1]; cfg=json.loads((ROOT/"config/phase1_revisionA.json").read_text())
selfdf=pd.read_csv(ROOT/"results/self_resume.csv"); src=pd.read_csv(ROOT/"results/source_capture_results.csv"); rows=pd.read_csv(ROOT/"results/phase1_runs.csv")
errs=[]
if len(selfdf)!=cfg["expected_self_resume_rows"]: errs.append(f"self rows {len(selfdf)}")
if len(src)!=cfg["expected_source_capture_rows"]: errs.append(f"source rows {len(src)}")
if len(rows)!=cfg["expected_migration_rows"]: errs.append(f"migration rows {len(rows)}")
if rows.run_id.nunique()!=len(rows): errs.append("duplicate migration run ids")
if selfdf.run_id.nunique()!=len(selfdf): errs.append("duplicate self run ids")
if not (ROOT/"results/PHASE1_REVISIONA_GATE.json").exists(): errs.append("missing gate json")
if errs: raise SystemExit("INTEGRITY FAIL: "+"; ".join(errs))
print("PASS: result structure complete. Scientific gate may still be PASS or FAIL; either outcome is exportable for analysis.")
