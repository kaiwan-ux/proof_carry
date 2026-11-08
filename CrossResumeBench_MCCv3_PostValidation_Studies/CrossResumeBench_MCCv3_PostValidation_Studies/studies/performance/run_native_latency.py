from __future__ import annotations
import argparse, csv, json, shutil, time
from pathlib import Path
import pandas as pd
from studies.common import ROOT, verify_passed_holdout_inputs, environment_metadata
from crossresumebench_mccv3.cases import CASES
from crossresumebench_mccv3.infra.isolated_runtime import isolated_runtime_factory
from crossresumebench_mccv3.evidence import generate
from crossresumebench_mccv3.baselines import build_and_lower
from crossresumebench_mccv3.semantics import expected_final
from crossresumebench_mccv3.evaluator import evaluate

FRAMEWORKS=['langgraph','crewai','maf']
def clean(p):shutil.rmtree(p,ignore_errors=True);Path(p).mkdir(parents=True,exist_ok=True)
def run(out_dir:Path,repeats=3):
    verify_passed_holdout_inputs();out_dir.mkdir(parents=True,exist_ok=True);work=out_dir/'work';clean(work)
    canonical=[next(c for c in CASES if c.family==fam) for fam in sorted({c.family for c in CASES})]
    rows=[]; cache={}
    # Isolated capture once per source/case; timing recorded separately.
    for s in FRAMEWORKS:
        for c in canonical:
            rd=work/f'capture-{s}-{c.case_id}';clean(rd);t0=time.perf_counter_ns();n=isolated_runtime_factory(s).capture_case_pause(c,rd);dt=time.perf_counter_ns()-t0;cache[(s,c.case_id)]=n
            rows.append({'stage':'source_capture','source':s,'target':'','case_id':c.case_id,'family':c.family,'repeat':0,'duration_ms':dt/1e6,'safe':1,'technical':0})
    for rep in range(repeats):
        for c in canonical:
            exp=expected_final(c)
            for s in FRAMEWORKS:
                for t in FRAMEWORKS:
                    if s==t:continue
                    cap=generate(c,cache[(s,c.case_id)],'enough_evidence')
                    t0=time.perf_counter_ns();payload,plan,reject,report=build_and_lower('mcc_v3',cap,c,t);t1=time.perf_counter_ns()
                    if plan is None: raise RuntimeError(f'Enough-evidence native timing unexpectedly rejected {c.case_id}: {reject}')
                    rd=work/f'target-{rep}-{s}-to-{t}-{c.case_id}';clean(rd)
                    # Seed target semantic store from source pause store.
                    from crossresumebench_mccv3.store import SemanticStore
                    SemanticStore(rd/'semantic_store.json').write(cache[(s,c.case_id)].source_store)
                    t2=time.perf_counter_ns();out=isolated_runtime_factory(t).run_plan(c,plan,rd);t3=time.perf_counter_ns();safe,fail=evaluate(exp,out['store'])
                    rows.append({'stage':'translation','source':s,'target':t,'case_id':c.case_id,'family':c.family,'repeat':rep,'duration_ms':(t1-t0)/1e6,'safe':int(safe),'technical':0,'payload_bytes':len(json.dumps(payload,sort_keys=True,separators=(',',':'),default=str).encode())})
                    rows.append({'stage':'target_resume','source':s,'target':t,'case_id':c.case_id,'family':c.family,'repeat':rep,'duration_ms':(t3-t2)/1e6,'safe':int(safe),'technical':0,'failure_types':json.dumps(fail)})
    df=pd.DataFrame(rows);df.to_csv(out_dir/'native_latency_runs.csv',index=False)
    summary=df.groupby(['stage'])['duration_ms'].agg(['count','mean','median',lambda x:x.quantile(.95)]);summary.columns=['count','mean_ms','median_ms','p95_ms'];summary.to_csv(out_dir/'native_latency_summary.csv')
    (out_dir/'environment.json').write_text(json.dumps(environment_metadata(),indent=2),encoding='utf-8')
    (out_dir/'NATIVE_LATENCY_REPORT.md').write_text('# Native Latency Study\n\n'+summary.to_markdown()+'\n\nThis study uses 8 canonical enough-evidence cases, all six directed pairs, and is performance evidence only—not additional safety-validation evidence.\n',encoding='utf-8')
    return {'rows':len(df),'canonical_cases':len(canonical),'repeats':repeats}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(ROOT/'results'/'performance_native'));ap.add_argument('--repeats',type=int,default=3);a=ap.parse_args();print(json.dumps(run(Path(a.out),a.repeats),indent=2))
