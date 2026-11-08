from __future__ import annotations
import csv,hashlib,json,shutil,time,traceback
from pathlib import Path
from .cases import CASES
from .evidence import generate,target_contract,workflow_hash
from .semantics import expected_source,expected_final,apply_source_pause,apply_plan
from .store import SemanticStore,clone_store
from .evaluator import evaluate
from .baselines import METHODS,build_and_lower
from .native import get_runtime
from .infra.isolated_runtime import isolated_runtime_factory
FRAMEWORKS=['langgraph','crewai','maf']; PAIRS=[(a,b) for a in FRAMEWORKS for b in FRAMEWORKS if a!=b]

def write_csv(path,rows):
    rows=list(rows); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); keys=[]
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader();
        for r in rows: w.writerow({k:(json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v) for k,v in r.items()})

def fake_native(case,source):
    from .models import NativePause
    return NativePause(source,case.case_id,f'synthetic:{source}:{case.case_id}',f'{source}_semantic_capture',['resume'],{'phase':'mid_execution'},{'framework':source,'runtime_alias_model':True,'semantic_namespace':{'langgraph':'lg.node','crewai':'crew.task','maf':'maf.activity'}[source],'pause_status':{'langgraph':'waiting','crewai':'pending','maf':'suspended'}[source]},expected_source(case))

def semantic_study(results,methods=None):
    methods=methods or METHODS; rows=[]; results=Path(results); (results/'semantic').mkdir(parents=True,exist_ok=True)
    for case in CASES:
      exp=expected_final(case)
      for source,target in PAIRS:
       native=fake_native(case,source)
       for variant in case.variants:
        cap=generate(case,native,source,target,variant)
        for method in methods:
          rid=f'{case.case_id}|{source}->{target}|{variant}|{method}'; t0=time.perf_counter_ns()
          try:
            payload,plan,reject,report=build_and_lower(method,cap,case,target); pb=len(json.dumps(payload,sort_keys=True,separators=(',',':'),default=str).encode())
            if plan is None: row={'run_id':rid,'study':'semantic','source':source,'target':target,'case_id':case.case_id,'family':case.family,'condition':variant,'method':method,'safe_completion':0,'safe_rejection':1,'unsafe_violation':0,'technical_failure':0,'reject_reason':reject,'payload_bytes':pb,'latency_ms':(time.perf_counter_ns()-t0)/1e6}
            else:
              tmp=results/'semantic'/'tmp'/hashlib.sha256(rid.encode()).hexdigest(); shutil.rmtree(tmp,ignore_errors=True); tmp.mkdir(parents=True); store=tmp/'store.json'; apply_source_pause(case,store); actual=apply_plan(plan,store); safe,fail=evaluate(exp,actual)
              row={'run_id':rid,'study':'semantic','source':source,'target':target,'case_id':case.case_id,'family':case.family,'condition':variant,'method':method,'safe_completion':int(safe),'safe_rejection':0,'unsafe_violation':int(not safe),'technical_failure':0,'reject_reason':'','failure_types':fail,'payload_bytes':pb,'latency_ms':(time.perf_counter_ns()-t0)/1e6}
            rows.append(row)
          except Exception: rows.append({'run_id':rid,'study':'semantic','source':source,'target':target,'case_id':case.case_id,'family':case.family,'condition':variant,'method':method,'safe_completion':0,'safe_rejection':0,'unsafe_violation':0,'technical_failure':1,'error':traceback.format_exc()})
    write_csv(results/'semantic_runs.csv',rows); shutil.rmtree(results/'semantic'/'tmp',ignore_errors=True); return rows

def native_gate(results,runtime_factory=None):
    if runtime_factory is None:
        from .infra.isolated_runtime import isolated_runtime_factory as runtime_factory
    results=Path(results); rows=[]; ok=True
    # 24 family probes + 104*3 self-resume/capture controls are intentionally separated in run_native.
    for fw in FRAMEWORKS:
      for fam in sorted({c.family for c in CASES}):
        case=next(c for c in CASES if c.family==fam); rd=results/'native_work'/f'probe-{fw}-{case.case_id}'; shutil.rmtree(rd,ignore_errors=True); rd.mkdir(parents=True)
        try: out=runtime_factory(fw).self_resume_case(case,rd); good=bool(out.get('restore_completed') and out.get('safe')); err=''
        except Exception: good=False; err=traceback.format_exc()
        rows.append({'framework':fw,'family':fam,'case_id':case.case_id,'pass':int(good),'error':err}); ok &= good
    write_csv(results/'native_family_gate.csv',rows); return bool(ok)

def native_study(results,runtime_factory=None,methods=('proofcarry','proofcarry_no_auth','always_reject')):
    if runtime_factory is None:
        from .infra.isolated_runtime import isolated_runtime_factory as runtime_factory
    results=Path(results); (results/'native_work').mkdir(parents=True,exist_ok=True); rows=[]; source_rows=[]; self_rows=[]; cache={}; source_errors={}
    if not native_gate(results,runtime_factory): return {'native_gate_pass':False}
    # Capture each of 104 cases in each source runtime once, and validate self-resume.
    for fw in FRAMEWORKS:
      for case in CASES:
        rd=results/'native_work'/f'self-{fw}-{case.case_id}'; shutil.rmtree(rd,ignore_errors=True); rd.mkdir(parents=True)
        try: out=runtime_factory(fw).self_resume_case(case,rd); tech=0; safe=int(bool(out.get('restore_completed') and out.get('safe'))); err=''
        except Exception: tech=1; safe=0; err=traceback.format_exc()
        self_rows.append({'framework':fw,'case_id':case.case_id,'family':case.family,'safe':safe,'technical_failure':tech,'error':err})
        rd=results/'native_work'/f'capture-{fw}-{case.case_id}'; shutil.rmtree(rd,ignore_errors=True); rd.mkdir(parents=True)
        try:
          n=runtime_factory(fw).capture_case_pause(case,rd); cache[(fw,case.case_id)]=n; tech=0; err=''; cpdir=rd/'checkpoints'; checkpoint_bytes=sum(p.stat().st_size for p in cpdir.rglob('*') if p.is_file()) if cpdir.exists() else 0; pause_metadata_bytes=len(json.dumps(n.to_dict(),sort_keys=True,separators=(',',':'),default=str).encode()); measurement_kind='checkpoint_files' if checkpoint_bytes>0 else 'in_memory_or_unavailable'
        except Exception: tech=1; err=traceback.format_exc(); source_errors[(fw,case.case_id)]=err; checkpoint_bytes=0; pause_metadata_bytes=0; measurement_kind='technical_failure'
        source_rows.append({'framework':fw,'case_id':case.case_id,'family':case.family,'capture_success':int(not tech),'technical_failure':tech,'native_checkpoint_bytes':checkpoint_bytes,'native_pause_metadata_bytes':pause_metadata_bytes,'checkpoint_measurement_kind':measurement_kind,'error':err})
    for case in CASES:
      exp=expected_final(case)
      for source,target in PAIRS:
        for method in methods:
          rid=f'native|{case.case_id}|{source}->{target}|{method}'; rd=results/'native_work'/hashlib.sha256(rid.encode()).hexdigest(); shutil.rmtree(rd,ignore_errors=True); rd.mkdir(parents=True)
          if (source,case.case_id) in source_errors:
            rows.append({'run_id':rid,'study':'native','source':source,'target':target,'case_id':case.case_id,'family':case.family,'condition':'enough_evidence','method':method,'technical_failure':1,'error':source_errors[(source,case.case_id)]}); continue
          try:
            cap=generate(case,cache[(source,case.case_id)],source,target,'enough_evidence'); payload,plan,reject,report=build_and_lower(method,cap,case,target); pb=len(json.dumps(payload,sort_keys=True,separators=(',',':'),default=str).encode())
            if plan is None: rows.append({'run_id':rid,'study':'native','source':source,'target':target,'case_id':case.case_id,'family':case.family,'condition':'enough_evidence','method':method,'safe_completion':0,'safe_rejection':1,'unsafe_violation':0,'technical_failure':0,'reject_reason':reject,'payload_bytes':pb}); continue
            # Seed target with source semantic store then execute target-native flow.
            from .store import SemanticStore
            SemanticStore(rd/'semantic_store.json').write(cache[(source,case.case_id)].source_store)
            out=runtime_factory(target).run_plan(case,plan,rd); safe,fail=evaluate(exp,out['store'])
            rows.append({'run_id':rid,'study':'native','source':source,'target':target,'case_id':case.case_id,'family':case.family,'condition':'enough_evidence','method':method,'safe_completion':int(safe),'safe_rejection':0,'unsafe_violation':int(not safe),'technical_failure':0,'failure_types':fail,'payload_bytes':pb})
          except Exception: rows.append({'run_id':rid,'study':'native','source':source,'target':target,'case_id':case.case_id,'family':case.family,'condition':'enough_evidence','method':method,'technical_failure':1,'error':traceback.format_exc()})
    write_csv(results/'native_runs.csv',rows); write_csv(results/'native_source_captures.csv',source_rows); write_csv(results/'native_self_resume.csv',self_rows); return {'native_gate_pass':True,'rows':len(rows)}
