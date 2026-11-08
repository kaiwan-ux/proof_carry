from pathlib import Path
import csv,json,sys
ROOT=Path(__file__).resolve().parents[1]; r=ROOT/"results"; verdict=json.loads((r/"RESEARCH_VERDICT.json").read_text(encoding="utf-8")); probs=[]
for k,v in [("migration_rows",(verdict["actual_migration_rows"],verdict["expected_migration_rows"])),("self_rows",(verdict["actual_self_rows"],84)),("source_rows",(verdict["actual_source_rows"],84))]:
    if v[0]!=v[1]: probs.append(f"{k}: {v[0]} != {v[1]}")
# Technical failures make the benchmark infrastructure invalid; MCC unsafe is a scientific result and does not block export.
if verdict["native"]["self_technical"] or verdict["native"]["source_technical"]: probs.append("native technical failures present")
if verdict["mcc"]["technical"]: probs.append("MCC technical failures present")
if verdict["all"]["technical"]: probs.append("migration technical failures present in one or more methods")
print(json.dumps({"ok":not probs,"problems":probs,"scientific_gate":verdict["gate"]},indent=2)); raise SystemExit(0 if not probs else 5)
