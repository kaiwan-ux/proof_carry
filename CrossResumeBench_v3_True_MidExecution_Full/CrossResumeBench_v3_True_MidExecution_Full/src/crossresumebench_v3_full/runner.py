from __future__ import annotations
import csv,hashlib,json,shutil,traceback
from pathlib import Path
from .cases import CASES,suite_hash
from .frozen import ROOT,FROZEN
from .native import get_runtime
from .evidence import source_capture
from .semantics import v2_case_spec,derive_plan,oracle_plan,expected_final,expected_source
from .baselines import METHODS,build_and_lower
from .store import SemanticStore,clone_store
from .evaluator import evaluate
from .models import MigrationRow

FRAMEWORKS=["langgraph","crewai","maf"]

def _clean(p): p=Path(p); shutil.rmtree(p,ignore_errors=True); p.mkdir(parents=True,exist_ok=True)
def _sha(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
def _write_csv(path,rows):
    rows=list(rows); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if not rows: path.write_text("",encoding="utf-8"); return
    keys=[]
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader()
        for r in rows:
            rr={k:(json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v) for k,v in r.items()}; w.writerow(rr)

def native_family_gate(results_dir,runtime_factory=get_runtime):
    results_dir=Path(results_dir); probes=[]
    canonical=[]
    for fam in sorted({c.family for c in CASES}): canonical.append(next(c for c in CASES if c.family==fam))
    ok=True
    for fw in FRAMEWORKS:
        for c in canonical:
            rid=f"probe-{fw}-{c.case_id}"; rdir=results_dir/"work"/rid; _clean(rdir)
            try:
                out=runtime_factory(fw).self_resume_case(c,rdir); good=bool(out.get("restore_completed") and out.get("safe")); err=""
            except Exception: good=False; err=traceback.format_exc(); out={"error":err}
            probes.append({"framework":fw,"family":c.family,"case_id":c.case_id,"pass":int(good),"error":err}); (results_dir/"probes"/f"{rid}.json").write_text(json.dumps(out,indent=2,default=str),encoding="utf-8"); ok &= good
    _write_csv(results_dir/"native_family_gate.csv",probes); (results_dir/"NATIVE_FAMILY_GATE.json").write_text(json.dumps({"pass":bool(ok),"probe_count":len(probes)},indent=2),encoding="utf-8"); return bool(ok)

def run(results_dir:Path,runtime_factory=get_runtime,skip_native_family_gate=False):
    results_dir=Path(results_dir); results_dir.mkdir(parents=True,exist_ok=True)
    for d in ["artifacts","native_sources","native_targets","native_controls","work","probes"]: (results_dir/d).mkdir(parents=True,exist_ok=True)
    if not skip_native_family_gate and not native_family_gate(results_dir,runtime_factory): return {"native_gate_pass":False}
    self_rows=[]; source_rows=[]; migration=[]; source_cache={}; source_err={}
    # All 28 x 3 native self-resume controls and captures.
    for fw in FRAMEWORKS:
        for c in CASES:
            rid=f"self-{fw}-{c.case_id}"; rdir=results_dir/"work"/rid; _clean(rdir)
            try:
                out=runtime_factory(fw).self_resume_case(c,rdir); tech=int(not out.get("restore_completed",False)); safe=int(bool(out.get("safe",False)) and not tech); err=""
            except Exception: tech=1; safe=0; err=traceback.format_exc(); out={"error":err}
            self_rows.append({"run_id":rid,"framework":fw,"case_id":c.case_id,"family":c.family,"restore_completed":int(not tech),"self_resume_safe":safe,"native_unsafe_replay":int((not tech) and (not safe)),"technical_failure":tech,"error":err}); (results_dir/"native_controls"/f"{rid}.json").write_text(json.dumps(out,indent=2,default=str),encoding="utf-8")
            sid=f"source-{fw}-{c.case_id}"; sdir=results_dir/"work"/sid; _clean(sdir)
            try:
                native=runtime_factory(fw).capture_case_pause(c,sdir); exp_src=expected_source(c); a=dict(native.source_store); e=dict(exp_src); a.pop("trace",None); e.pop("trace",None)
                if a!=e: raise RuntimeError(f"native source boundary mismatch for {fw}/{c.case_id}: expected={e}, actual={a}")
                source_cache[(fw,c.case_id)]=native; err=""; tech=0
                (results_dir/"native_sources"/f"{sid}.json").write_text(json.dumps(native.to_dict(),indent=2,default=str),encoding="utf-8")
            except Exception: err=traceback.format_exc(); source_err[(fw,c.case_id)]=err; tech=1; native=None; (results_dir/"native_sources"/f"{sid}.json").write_text(json.dumps({"error":err},indent=2),encoding="utf-8")
            source_rows.append({"source_id":sid,"framework":fw,"case_id":c.case_id,"family":c.family,"capture_success":int(not tech),"technical_failure":tech,"checkpoint_ref":"" if native is None else native.checkpoint_ref,"native_kind":"" if native is None else native.native_kind,"pending_work":"" if native is None else json.dumps(native.pending_work),"error":err})
    # Migration grid = 80 applicable case-variant instances * 6 directed pairs * 7 methods = 3360 rows.
    for c in CASES:
        v2c=v2_case_spec(c); exp=expected_final(c)
        for variant in c.applicable_variants:
            for source in FRAMEWORKS:
                for target in FRAMEWORKS:
                    if source==target: continue
                    for method in METHODS:
                        rid=f"{c.case_id}-{variant}-{source}-to-{target}-{method}"; rdir=results_dir/"work"/rid; _clean(rdir); expected_plan=oracle_plan(c)
                        if (source,c.case_id) in source_err:
                            row=MigrationRow(rid,source,target,c.case_id,c.family,variant,method,technical_failure=1,failure_types=["SOURCE_CAPTURE_FAILURE"],expected_plan=expected_plan,error=source_err[(source,c.case_id)]); migration.append(row.to_dict()); continue
                        try:
                            native=source_cache[(source,c.case_id)]; cap=source_capture(c,native,variant); pkg,rc,reject=build_and_lower(method,cap,c,v2c,target,FROZEN)
                            ph=_sha(pkg.payload); pbytes=len(json.dumps(pkg.payload,sort_keys=True,separators=(",",":"),default=str).encode())
                            if rc is None:
                                row=MigrationRow(rid,source,target,c.case_id,c.family,variant,method,safe_rejection=1,reject_reason=reject,payload_bytes=pbytes,payload_sha256=ph,expected_plan=expected_plan)
                                art={"row":row.to_dict(),"payload":pkg.payload,"reject_reason":reject}
                            else:
                                plan=derive_plan(rc,c); source_store_path=results_dir/"work"/f"source-{source}-{c.case_id}"/"semantic_store.json"; clone_store(source_store_path,rdir/"semantic_store.json"); tout=runtime_factory(target).run_plan(c,plan,rdir); actual=tout["store"]; safe,fail=evaluate(exp,actual); row=MigrationRow(rid,source,target,c.case_id,c.family,variant,method,safe_completion=int(safe),unsafe_violation=int(not safe),failure_types=fail,payload_bytes=pbytes,payload_sha256=ph,expected_plan=expected_plan,actual_plan=plan); art={"row":row.to_dict(),"payload":pkg.payload,"reconstructed":rc.to_dict(),"plan":plan,"expected":exp,"actual":actual,"target":tout}
                                (results_dir/"native_targets"/f"{rid}.json").write_text(json.dumps(tout,indent=2,default=str),encoding="utf-8")
                            migration.append(row.to_dict()); (results_dir/"artifacts"/f"{rid}.json").write_text(json.dumps(art,indent=2,default=str),encoding="utf-8")
                        except Exception:
                            err=traceback.format_exc(); row=MigrationRow(rid,source,target,c.case_id,c.family,variant,method,technical_failure=1,failure_types=["TARGET_OR_TRANSLATION_FAILURE"],expected_plan=expected_plan,error=err); migration.append(row.to_dict()); (results_dir/"artifacts"/f"{rid}.json").write_text(json.dumps({"row":row.to_dict(),"traceback":err},indent=2),encoding="utf-8")
    _write_csv(results_dir/"self_resume.csv",self_rows); _write_csv(results_dir/"source_captures.csv",source_rows); _write_csv(results_dir/"migration_runs.csv",migration)
    return {"native_gate_pass":True,"self_rows":len(self_rows),"source_rows":len(source_rows),"migration_rows":len(migration),"suite_hash":suite_hash()}
