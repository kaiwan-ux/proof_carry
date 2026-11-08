from pathlib import Path
import json,pandas as pd
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/"results"; cfg=json.loads((ROOT/"config"/"experiment.json").read_text())
errors=[]
p=R/"generalization_runs.csv"
if not p.exists(): errors.append("missing generalization_runs.csv")
else:
    df=pd.read_csv(p)
    if len(df)!=cfg["expected_target_rows"]: errors.append(f"expected {cfg['expected_target_rows']} rows, got {len(df)}")
    if df.run_id.nunique()!=len(df): errors.append("run IDs not unique")
    exp=set(cfg["conditions"]); got=set(df.condition.unique())
    if exp!=got: errors.append(f"conditions mismatch: {got}")
    if int(df.technical_failure.sum())>0: errors.append(f"technical failures present: {int(df.technical_failure.sum())}")
sources=list((R/"native_sources").glob("*.json"))
if len(sources)!=cfg["expected_source_captures"]: errors.append(f"expected {cfg['expected_source_captures']} source captures, got {len(sources)}")

for name in ["langgraph","crewai","maf"]:
    pp=R/"probes"/f"{name}.json"
    if not pp.exists(): errors.append(f"missing native probe: {name}")
    else:
        try:
            pobj=json.loads(pp.read_text())
            if pobj.get("status")!="ok": errors.append(f"native probe failed: {name}")
        except Exception as e: errors.append(f"invalid native probe {name}: {e}")
# Anti-leak scan of every capsule.
for f in (R/"capsules").glob("*.json"):
    txt=f.read_text()
    for forbidden in ['"native_snapshot"','"latest_checkpoint"','"checkpoint_id"','"flow_id"']:
        if forbidden in txt: errors.append(f"native leakage in {f.name}: {forbidden}")
obj={"ok":not errors,"errors":errors,"source_captures":len(sources)}; (R/"VERIFY_RESULTS.json").write_text(json.dumps(obj,indent=2)); print(json.dumps(obj,indent=2))
if errors: raise SystemExit(2)
