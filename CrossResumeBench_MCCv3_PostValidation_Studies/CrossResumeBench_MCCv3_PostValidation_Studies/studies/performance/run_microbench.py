from __future__ import annotations
import argparse, json, statistics, time, platform
from pathlib import Path
import pandas as pd
from studies.common import ROOT, verify_passed_holdout_inputs, environment_metadata
from crossresumebench_mccv3.cases import CASES
from crossresumebench_mccv3.models import NativePause
from crossresumebench_mccv3.evidence import generate
from crossresumebench_mccv3.semantics import expected_source, proof_plan
from crossresumebench_mccv3.baselines import _workflow_hash, build_and_lower
from crossresumebench_mccv3.legacy import v2_case_spec
from mechanism.mcc_v3 import build_mcc_v3, resolve_proofs

FRAMEWORKS=['langgraph','crewai','maf']
def fake_native(fw,c): return NativePause(fw,c.case_id,f'perf://{fw}/{c.case_id}','microbench',[],{'phase':'mid_execution'},{'framework':fw},expected_source(c))
def stats(xs):
    xs=sorted(xs); n=len(xs)
    def q(p): return xs[min(n-1,max(0,int(round((n-1)*p))))]
    return {'n':n,'mean_us':statistics.fmean(xs)/1000,'median_us':statistics.median(xs)/1000,'p95_us':q(.95)/1000,'p99_us':q(.99)/1000,'stdev_us':(statistics.pstdev(xs)/1000 if n>1 else 0)}
def run(out_dir:Path,repeats=20,warmup=2):
    verify_passed_holdout_inputs();out_dir.mkdir(parents=True,exist_ok=True)
    instances=[]
    for c in CASES:
        wh=_workflow_hash(v2_case_spec(c))
        for v in c.variants:
            for s in FRAMEWORKS:
                for t in FRAMEWORKS:
                    if s==t:continue
                    cap=generate(c,fake_native(s,c),v);instances.append((c,v,s,t,wh,cap))
    # warm-up
    for _ in range(warmup):
        for c,v,s,t,wh,cap in instances[:32]: build_and_lower('mcc_v3',cap,c,t)
    timings={'mcc_v3_build':[],'mcc_v3_resolve':[],'mcc_v3_lower_total':[],'mcc_v2_total':[]}; sizes={'mcc_v3':[],'mcc_v2':[]}
    for _ in range(repeats):
        for c,v,s,t,wh,cap in instances:
            t0=time.perf_counter_ns(); p=build_mcc_v3(cap,t,wh,c.continuation_contract,ROOT/'mechanism'); t1=time.perf_counter_ns(); ps,rep=resolve_proofs(p,c.continuation_contract,ROOT/'mechanism'); t2=time.perf_counter_ns();
            if rep['admissible']: proof_plan(ps,c)
            t3=time.perf_counter_ns(); p2,pl2,r2,rep2=build_and_lower('mcc_v2_frozen',cap,c,t); t4=time.perf_counter_ns()
            timings['mcc_v3_build'].append(t1-t0);timings['mcc_v3_resolve'].append(t2-t1);timings['mcc_v3_lower_total'].append(t3-t0);timings['mcc_v2_total'].append(t4-t3)
            if _==0:
                sizes['mcc_v3'].append(len(json.dumps(p,sort_keys=True,separators=(',',':'),default=str).encode()));sizes['mcc_v2'].append(len(json.dumps(p2,sort_keys=True,separators=(',',':'),default=str).encode()))
    report={'environment':environment_metadata(),'instances_per_repeat':len(instances),'repeats':repeats,'warmup':warmup,'timings':{k:stats(v) for k,v in timings.items()},'payload_bytes':{k:{'n':len(v),'mean':statistics.fmean(v),'median':statistics.median(v),'p95':sorted(v)[int(.95*(len(v)-1))]} for k,v in sizes.items()}}
    (out_dir/'microbench.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    lines=['# Mechanism Microbenchmark','',f"Instances per repeat: {len(instances)}; repeats: {repeats}.",'','| Stage | Median (µs) | p95 (µs) | Mean (µs) |','|---|---:|---:|---:|']
    for k,v in report['timings'].items(): lines.append(f"| {k} | {v['median_us']:.2f} | {v['p95_us']:.2f} | {v['mean_us']:.2f} |")
    lines += ['','## Payload bytes',f"- MCC v3 median: {report['payload_bytes']['mcc_v3']['median']:.0f} B",f"- MCC v2 median: {report['payload_bytes']['mcc_v2']['median']:.0f} B",'', 'Timing is mechanism-only and excludes native runtime scheduling/network/tool latency.']
    (out_dir/'MICROBENCH_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return report
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(ROOT/'results'/'performance_micro'));ap.add_argument('--repeats',type=int,default=20);ap.add_argument('--warmup',type=int,default=2);a=ap.parse_args();r=run(Path(a.out),a.repeats,a.warmup);print(json.dumps({'instances':r['instances_per_repeat'],'repeats':r['repeats']},indent=2))
