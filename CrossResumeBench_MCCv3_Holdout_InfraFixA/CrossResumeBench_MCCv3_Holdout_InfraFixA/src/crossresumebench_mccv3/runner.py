from __future__ import annotations
import csv,hashlib,json,shutil,traceback
from pathlib import Path
from .cases import CASES
from .native import get_runtime
from .evidence import generate
from .semantics import expected_source,expected_final,apply_plan
from .baselines import METHODS,build_and_lower
from .store import SemanticStore,clone_store
from .evaluator import evaluate
from .models import Row
FRAMEWORKS=['langgraph','crewai','maf']
def _clean(p): p=Path(p); shutil.rmtree(p,ignore_errors=True); p.mkdir(parents=True,exist_ok=True)
def _sha(o): return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def _csv(path,rows):
    rows=list(rows); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    keys=[]
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader()
        for r in rows: w.writerow({k:(json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v) for k,v in r.items()})
def native_gate(results,runtime_factory=get_runtime):
    fams=sorted({c.family for c in CASES}); probes=[]; ok=True
    for fw in FRAMEWORKS:
        for fam in fams:
            c=next(x for x in CASES if x.family==fam); rd=Path(results)/'work'/f'probe-{fw}-{c.case_id}'; _clean(rd)
            try: out=runtime_factory(fw).self_resume_case(c,rd); good=bool(out.get('restore_completed') and out.get('safe')); err=''
            except Exception: out={}; good=False; err=traceback.format_exc()
            probes.append({'framework':fw,'family':fam,'case_id':c.case_id,'pass':int(good),'error':err}); ok &= good
    _csv(Path(results)/'native_family_gate.csv',probes); (Path(results)/'NATIVE_FAMILY_GATE.json').write_text(json.dumps({'pass':bool(ok),'probe_count':len(probes)},indent=2),encoding='utf-8'); return bool(ok)
def run(results,runtime_factory=get_runtime,skip_native_gate=False):
    results=Path(results); _clean(results)
    for d in ['artifacts','native_sources','native_targets','native_controls','work','probes']: (results/d).mkdir(exist_ok=True)
    if not skip_native_gate and not native_gate(results,runtime_factory): return {'native_gate_pass':False}
    self_rows=[]; src_rows=[]; rows=[]; cache={}; errs={}
    for fw in FRAMEWORKS:
        for c in CASES:
            rd=results/'work'/f'self-{fw}-{c.case_id}'; _clean(rd)
            try: o=runtime_factory(fw).self_resume_case(c,rd); tech=int(not o.get('restore_completed',False)); safe=int(bool(o.get('safe')) and not tech); err=''
            except Exception: o={};tech=1;safe=0;err=traceback.format_exc()
            self_rows.append({'framework':fw,'case_id':c.case_id,'family':c.family,'restore_completed':int(not tech),'self_resume_safe':safe,'technical_failure':tech,'error':err})
            sd=results/'work'/f'source-{fw}-{c.case_id}'; _clean(sd)
            try:
                n=runtime_factory(fw).capture_case_pause(c,sd); a=dict(n.source_store); e=dict(expected_source(c)); a.pop('trace',None);e.pop('trace',None)
                if a!=e: raise RuntimeError(f'source boundary mismatch expected={e} actual={a}')
                cache[(fw,c.case_id)]=n; tech=0;err=''; (results/'native_sources'/f'{fw}-{c.case_id}.json').write_text(json.dumps(n.to_dict(),indent=2,default=str),encoding='utf-8')
            except Exception: n=None;tech=1;err=traceback.format_exc();errs[(fw,c.case_id)]=err
            src_rows.append({'framework':fw,'case_id':c.case_id,'family':c.family,'capture_success':int(not tech),'technical_failure':tech,'checkpoint_ref':'' if n is None else n.checkpoint_ref,'native_kind':'' if n is None else n.native_kind,'error':err})
    for c in CASES:
        exp=expected_final(c)
        for variant in c.variants:
            for s in FRAMEWORKS:
                for t in FRAMEWORKS:
                    if s==t: continue
                    for method in METHODS:
                        rid=f'{c.case_id}-{variant}-{s}-to-{t}-{method}'; rd=results/'work'/rid; _clean(rd)
                        if (s,c.case_id) in errs:
                            rows.append(Row(rid,s,t,c.case_id,c.family,variant,method,technical_failure=1,failure_types=['SOURCE_CAPTURE_FAILURE'],expected_plan=c.oracle_plan,error=errs[(s,c.case_id)]).to_dict()); continue
                        try:
                            cap=generate(c,cache[(s,c.case_id)],variant); payload,plan,reject,report=build_and_lower(method,cap,c,t); ph=_sha(payload); pb=len(json.dumps(payload,sort_keys=True,separators=(',',':'),default=str).encode())
                            if plan is None:
                                r=Row(rid,s,t,c.case_id,c.family,variant,method,safe_rejection=1,reject_reason=reject,payload_bytes=pb,payload_sha256=ph,expected_plan=c.oracle_plan); art={'row':r.to_dict(),'payload':payload,'report':report}
                            else:
                                srcp=results/'work'/f'source-{s}-{c.case_id}'/'semantic_store.json'; clone_store(srcp,rd/'semantic_store.json'); out=runtime_factory(t).run_plan(c,plan,rd); safe,fail=evaluate(exp,out['store']); r=Row(rid,s,t,c.case_id,c.family,variant,method,safe_completion=int(safe),unsafe_violation=int(not safe),failure_types=fail,payload_bytes=pb,payload_sha256=ph,expected_plan=c.oracle_plan,actual_plan=plan); art={'row':r.to_dict(),'payload':payload,'report':report,'plan':plan,'expected':exp,'actual':out['store']}; (results/'native_targets'/f'{rid}.json').write_text(json.dumps(out,indent=2,default=str),encoding='utf-8')
                            rows.append(r.to_dict()); (results/'artifacts'/f'{rid}.json').write_text(json.dumps(art,indent=2,default=str),encoding='utf-8')
                        except Exception:
                            err=traceback.format_exc(); r=Row(rid,s,t,c.case_id,c.family,variant,method,technical_failure=1,failure_types=['TARGET_OR_TRANSLATION_FAILURE'],expected_plan=c.oracle_plan,error=err); rows.append(r.to_dict()); (results/'artifacts'/f'{rid}.json').write_text(json.dumps({'row':r.to_dict(),'traceback':err},indent=2),encoding='utf-8')
    _csv(results/'self_resume.csv',self_rows); _csv(results/'source_captures.csv',src_rows); _csv(results/'migration_runs.csv',rows)
    return {'native_gate_pass':True,'self_rows':len(self_rows),'source_rows':len(src_rows),'migration_rows':len(rows)}
