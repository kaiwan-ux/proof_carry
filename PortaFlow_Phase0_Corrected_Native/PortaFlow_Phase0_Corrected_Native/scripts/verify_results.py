from pathlib import Path
import csv,json,sys
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/"results"
errors=[]
p=RES/"native_cross_runtime_runs.csv"
if not p.exists(): errors.append("missing native_cross_runtime_runs.csv")
else:
 rows=list(csv.DictReader(p.open(encoding='utf-8')))
 if len(rows)!=54: errors.append(f"expected 54 rows, got {len(rows)}")
 ids=[r['run_id'] for r in rows]
 if len(ids)!=len(set(ids)): errors.append("run_id values are not unique")
 expected={(s,t,w,c) for s in ['langgraph','crewai','maf'] for t in ['langgraph','crewai','maf'] if s!=t for w in ['retry','approval','side_effect'] for c in ['naive_state','state_history','native_semantic']}
 got={(r['source_framework'],r['target_framework'],r['workflow'],r['condition']) for r in rows}
 if got!=expected: errors.append(f"case matrix mismatch: missing={sorted(expected-got)} extra={sorted(got-expected)}")
 if any(int(r['technical_failure']) for r in rows): errors.append("one or more native migration rows have technical failures")
# all 9 source captures expected
src=list((RES/'native_sources').glob('*.json'))
if len(src)!=9: errors.append(f"expected 9 native source captures, got {len(src)}")
print(json.dumps({"status":"PASS" if not errors else "FAIL","errors":errors},indent=2))
if errors: sys.exit(1)
