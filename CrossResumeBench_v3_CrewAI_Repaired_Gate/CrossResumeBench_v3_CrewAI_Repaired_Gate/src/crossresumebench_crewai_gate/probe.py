
from __future__ import annotations
import json, shutil, traceback
from pathlib import Path
from .ledger import FileLedger
from .native import get_runtime

SAFE_LEDGER = {"effect_count":1,"ack_count":1,"finish_count":1}


def _clean(p):
    p=Path(p)
    if p.exists(): shutil.rmtree(p)
    p.mkdir(parents=True,exist_ok=True)


def run_probe(results_dir: Path, runtime_factory=get_runtime):
    results_dir=Path(results_dir); work=results_dir/"work"/"probe"; work.mkdir(parents=True,exist_ok=True)
    checks={}; details={}
    try:
        cap=runtime_factory("crewai").capability_probe(); details["capability"]=cap
        checks["capability_ready"]=bool(cap.get("ready"))
    except Exception:
        details["capability"]={"error":traceback.format_exc()}; checks["capability_ready"]=False

    # Self restore: must be technically executable. Safety is reported separately.
    try:
        d=work/"self"; _clean(d); out=runtime_factory("crewai").self_resume_committed(d); details["self_resume"]=out
        checks["self_resume_restorable"]=bool(out.get("restore_completed",True))
    except Exception:
        details["self_resume"]={"error":traceback.format_exc()}; checks["self_resume_restorable"]=False

    for world,expected in [("committed",1),("not_committed",0)]:
        key=f"capture_{world}_before_ack"
        try:
            d=work/f"capture_{world}"; _clean(d); n=runtime_factory("crewai").capture_effect_pause(d,world); details[f"capture_{world}"]=n.to_dict()
            checks[key]=n.source_ledger=={"effect_count":expected,"ack_count":0,"finish_count":0} and n.pending_work==["ack"]
        except Exception:
            details[f"capture_{world}"]={"error":traceback.format_exc()}; checks[key]=False

    for world,initial,decision in [
        ("committed",{"effect_count":1,"ack_count":0,"finish_count":0},"skip_effect"),
        ("not_committed",{"effect_count":0,"ack_count":0,"finish_count":0},"execute_effect"),
    ]:
        key=f"target_{world}_correct"
        try:
            d=work/f"target_{world}"; _clean(d); FileLedger(d/"ledger.json").write(initial)
            out=runtime_factory("crewai").run_from_effect_decision(world,d); details[f"target_{world}"]=out
            checks[key]=out.get("effect_decision")==decision and out.get("ledger")==SAFE_LEDGER
        except Exception:
            details[f"target_{world}"]={"error":traceback.format_exc()}; checks[key]=False

    report={"checks":checks,"details":details,"probe_pass":all(checks.values()) and len(checks)==6}
    (results_dir/"CREWAI_REPAIR_PROBE.json").write_text(json.dumps(report,indent=2,default=str), encoding="utf-8")
    return report
