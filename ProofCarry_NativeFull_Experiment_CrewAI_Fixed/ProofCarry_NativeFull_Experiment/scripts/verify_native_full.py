from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def rows(p):
    with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def I(x):
    try:return int(x)
    except:return 0

def main():
    ap=argparse.ArgumentParser();ap.add_argument('run_dir');args=ap.parse_args();d=Path(args.run_dir)
    meta=json.loads((d/'NATIVE_RUN_META.json').read_text()); exp=meta['expected']; checks={}
    nr=rows(d/'native_runs.csv'); sr=rows(d/'native_self_resume.csv'); cr=rows(d/'native_source_captures.csv'); gr=rows(d/'native_family_gate.csv')
    checks['migration_row_count']=len(nr)==exp['migration_rows']
    checks['self_resume_row_count']=len(sr)==exp['self_resume_rows']
    checks['source_capture_row_count']=len(cr)==exp['source_capture_rows']
    checks['family_gate_row_count']=len(gr)==exp['family_gate_rows']
    checks['exclusive_outcome_flags']=all(sum(I(r.get(k)) for k in ['safe_completion','safe_rejection','unsafe_violation','technical_failure'])==1 for r in nr)
    checks['technical_not_safe']=all(not(I(r.get('technical_failure')) and (I(r.get('safe_completion')) or I(r.get('safe_rejection')) or I(r.get('unsafe_violation')))) for r in nr)
    checks['all_run_ids_unique']=len({r['run_id'] for r in nr})==len(nr)
    report={'passed':all(checks.values()),'checks':checks,'expected':exp,'actual':{'migration_rows':len(nr),'self_resume_rows':len(sr),'source_capture_rows':len(cr),'family_gate_rows':len(gr)}}
    (d/'NATIVE_VERIFICATION.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps(report,indent=2)); return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
