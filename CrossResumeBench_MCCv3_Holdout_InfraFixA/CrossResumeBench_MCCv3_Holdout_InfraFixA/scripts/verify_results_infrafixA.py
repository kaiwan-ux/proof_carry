import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'
def read(name):
    with (R/name).open(encoding='utf-8') as f:return list(csv.DictReader(f))
rows=read('migration_runs.csv'); selfr=read('self_resume.csv'); srcr=read('source_captures.csv')
gate=json.loads((R/'native_gate'/'NATIVE_FAMILY_GATE.json').read_text(encoding='utf-8'))
structure={'migration_rows':len(rows),'self_resume_rows':len(selfr),'source_capture_rows':len(srcr),'native_gate_rows':gate.get('probe_count_completed'),'migration_exact':len(rows)==6144,'self_exact':len(selfr)==96,'source_exact':len(srcr)==96,'native_gate_exact':gate.get('probe_count_completed')==24}
structure['structure_ok']=all(structure[k] for k in ['migration_exact','self_exact','source_exact','native_gate_exact'])
(R/'INFRAFIXA_STRUCTURE_VERIFICATION.json').write_text(json.dumps(structure,indent=2,sort_keys=True),encoding='utf-8')
print(json.dumps(structure,indent=2))
if not structure['structure_ok']: raise SystemExit(2)
