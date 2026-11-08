from __future__ import annotations
import csv,json,uuid,traceback,shutil
from pathlib import Path
from .native import get_runtime
from .phase1_case import case_spec,spec_hash
from .evidence import source_capture_from_native
from .frozen import build_mcc_v2,reconstruct_mcc_v2,admissibility,ROOT
from .models import RunOutcome

SAFE_LEDGER={"effect_count":1,"ack_count":1,"finish_count":1}

def _clean(p):
    if p.exists(): shutil.rmtree(p)
    p.mkdir(parents=True,exist_ok=True)

def run(results_dir:Path):
    cfg=json.loads((ROOT/'config/phase1.json').read_text())
    results_dir=Path(results_dir); results_dir.mkdir(parents=True,exist_ok=True)
    artifacts=results_dir/'artifacts'; sources=results_dir/'native_sources'; targets=results_dir/'native_targets'
    for d in [artifacts,sources,targets]: d.mkdir(parents=True,exist_ok=True)
    self_rows=[]; rows=[]
    # Self-resume prerequisite controls.
    for fw in cfg['frameworks']:
        rid=f"self-{fw}-{uuid.uuid4().hex[:8]}"; rdir=results_dir/'work'/rid; _clean(rdir)
        try:
            out=get_runtime(fw).self_resume_effect_ack(rdir); ok=bool(out['safe']); err=''
            (artifacts/f"{rid}.json").write_text(json.dumps(out,indent=2,default=str))
        except Exception as e:
            ok=False; err=traceback.format_exc(); out={"error":str(e)}
        self_rows.append({"run_id":rid,"framework":fw,"case_id":"effect_committed_ack_pending","self_resume_safe":int(ok),"technical_failure":int(not ok),"error":err})
    # Capture each source once per variant and run all directed pairs.
    c=case_spec(); wh=spec_hash()
    for variant in cfg['variants']:
      for source in cfg['frameworks']:
        srid=f"src-{source}-{variant}-{uuid.uuid4().hex[:8]}"; sdir=results_dir/'work'/srid; _clean(sdir)
        try:
            native=get_runtime(source).capture_effect_ack_pause(sdir)
            capture=source_capture_from_native(native,variant)
            (sources/f"{srid}.json").write_text(json.dumps({"native":native.to_dict(),"capture":capture.to_dict()},indent=2,default=str))
        except Exception:
            # Emit a technical failure for every target pair from this source/variant.
            err=traceback.format_exc()
            for target in cfg['frameworks']:
                if target==source: continue
                rows.append(RunOutcome(f"fail-{source}-{target}-{variant}",source,target,c.case_id,variant,"mcc_v2",technical_failure=1,failure_types=["SOURCE_CAPTURE_FAILURE"],artifact={"traceback":err}).to_dict())
            continue
        for target in cfg['frameworks']:
          if target==source: continue
          for method in cfg['migration_methods']:
            rid=f"{source}-to-{target}-{variant}-{method}-{uuid.uuid4().hex[:8]}"; tdir=results_dir/'work'/rid; _clean(tdir)
            try:
                if method=='mcc_v2':
                    pkg=build_mcc_v2(capture,target,wh,ROOT/'frozen_v2')
                    rc,report=reconstruct_mcc_v2(pkg.payload,c,ROOT/'frozen_v2')
                    accepted,reason=admissibility(rc)
                    if not accepted:
                        row=RunOutcome(rid,source,target,c.case_id,variant,method,safe_rejection=1,reject_reason=reason,payload_bytes=pkg.byte_size(),artifact={"inference":report,"payload":pkg.payload})
                    else:
                        out=get_runtime(target).run_ack_finish_from_mcc(rc,tdir); d=out['ledger']; safe=(d==SAFE_LEDGER)
                        row=RunOutcome(rid,source,target,c.case_id,variant,method,safe_completion=int(safe),unsafe_violation=int(not safe),failure_types=[] if safe else ["LEDGER_OR_ACK_MISMATCH"],payload_bytes=pkg.byte_size(),artifact={"inference":report,"payload":pkg.payload,"target":out})
                elif variant!='enough_evidence':
                    continue
                else:
                    # Smoke controls intentionally receive exact source truth; no claims of portability novelty.
                    class RC: pass
                    rc=RC(); rc.completed_units=['commit_effect']; rc.effect_facts={'effect':{'status':'committed'}}
                    out=get_runtime(target).run_ack_finish_from_mcc(rc,tdir); d=out['ledger']; safe=(d==SAFE_LEDGER)
                    row=RunOutcome(rid,source,target,c.case_id,variant,method,safe_completion=int(safe),unsafe_violation=int(not safe),failure_types=[] if safe else ["CONTROL_FAILED"],artifact={"target":out,"control":"privileged"})
                rows.append(row.to_dict()); (artifacts/f"{rid}.json").write_text(json.dumps(row.to_dict(),indent=2,default=str))
                if row.artifact and 'target' in row.artifact: (targets/f"{rid}.json").write_text(json.dumps(row.artifact['target'],indent=2,default=str))
            except Exception:
                rows.append(RunOutcome(rid,source,target,c.case_id,variant,method,technical_failure=1,failure_types=["TARGET_OR_TRANSLATION_FAILURE"],artifact={"traceback":traceback.format_exc()}).to_dict())
    # CSVs
    import pandas as pd
    pd.DataFrame(self_rows).to_csv(results_dir/'self_resume.csv',index=False)
    pd.DataFrame(rows).to_csv(results_dir/'phase1_runs.csv',index=False)
    return self_rows,rows
