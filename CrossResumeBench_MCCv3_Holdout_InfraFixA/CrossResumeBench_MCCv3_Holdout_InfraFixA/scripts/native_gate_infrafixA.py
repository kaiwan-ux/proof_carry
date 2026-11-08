from __future__ import annotations
import csv,json,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/'src'),str(ROOT/'frozen_v2'/'src'),str(ROOT)]
from crossresumebench_mccv3.cases import CASES
from crossresumebench_mccv3.infra.isolated_runtime import isolated_runtime_factory
FRAMEWORKS=['langgraph','crewai','maf']
OUT=ROOT/'native_gate_results'

def write_csv(path,rows):
    keys=['framework','family','case_id','pass','restore_completed','semantic_safe','lifecycle_returned','timeout','technical_failure','duration_sec','isolated_status','error']
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp')
    with tmp.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows([{k:r.get(k,'') for k in keys} for r in rows])
    tmp.replace(path)

def write_state(rows,done=False):
    ok=bool(rows) and len(rows)==24 and all(int(r.get('pass',0))==1 for r in rows)
    obj={'pass':ok,'probe_count_expected':24,'probe_count_completed':len(rows),'done':done,'rows_passed':sum(int(r.get('pass',0)) for r in rows),'rows_failed':sum(1-int(r.get('pass',0)) for r in rows),'infra_revision':'InfraFixA'}
    tmp=OUT/'NATIVE_FAMILY_GATE.json.tmp'; tmp.write_text(json.dumps(obj,indent=2,sort_keys=True),encoding='utf-8'); tmp.replace(OUT/'NATIVE_FAMILY_GATE.json')

def main():
    import shutil
    shutil.rmtree(OUT,ignore_errors=True); OUT.mkdir(parents=True,exist_ok=True)
    fams=sorted({c.family for c in CASES}); rows=[]
    for fw in FRAMEWORKS:
        for fam in fams:
            c=next(x for x in CASES if x.family==fam); rd=OUT/'work'/f'probe-{fw}-{c.case_id}'; rd.mkdir(parents=True,exist_ok=True)
            t0=time.monotonic(); row={'framework':fw,'family':fam,'case_id':c.case_id,'pass':0,'restore_completed':0,'semantic_safe':0,'lifecycle_returned':0,'timeout':0,'technical_failure':0,'duration_sec':0,'isolated_status':'','error':''}
            try:
                o=isolated_runtime_factory(fw).self_resume_case(c,rd)
                row.update({'restore_completed':int(bool(o.get('restore_completed'))),'semantic_safe':int(bool(o.get('semantic_safe',o.get('safe')))),'lifecycle_returned':int(bool(o.get('lifecycle_returned',True))),'isolated_status':o.get('isolated_status','ok')})
                row['pass']=int(bool(o.get('restore_completed')) and bool(o.get('safe')) and bool(o.get('lifecycle_returned',True)))
            except Exception as e:
                s=traceback.format_exc(); row['technical_failure']=1; row['error']=s
                if 'timed out' in str(e).lower(): row['timeout']=1
            row['duration_sec']=round(time.monotonic()-t0,6); rows.append(row)
            write_csv(OUT/'native_family_gate.csv',rows); write_state(rows,done=False)
            print(f"[{len(rows):02d}/24] {fw:10s} {fam:24s} PASS={row['pass']} timeout={row['timeout']} lifecycle={row['lifecycle_returned']}",flush=True)
    write_state(rows,done=True); final=json.loads((OUT/'NATIVE_FAMILY_GATE.json').read_text(encoding='utf-8')); print(json.dumps(final,indent=2)); return 0 if final['pass'] else 2
if __name__=='__main__': raise SystemExit(main())
