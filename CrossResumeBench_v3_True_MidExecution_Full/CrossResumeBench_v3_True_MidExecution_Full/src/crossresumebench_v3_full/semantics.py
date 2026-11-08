from __future__ import annotations
import copy
from pathlib import Path
from .store import SemanticStore

SAFE_APP_STATE={"phase":"mid_execution"}

def source_actions(case):
    p=case.params; f=case.family; a=[]
    if f=="effect_commitment":
        if p["effect_status"]=="committed": a.append({"kind":"effect","operation":p["operation"],"unit":"effect_attempt"})
        else: a.append({"kind":"unit","unit":"effect_attempt"})
    elif f=="retry_pause":
        for i in range(1,p["current_attempt"]+1): a.append({"kind":"unit","unit":f"retry_attempt_{i}"})
        a.append({"kind":"counter","key":"retry:retry_task","value":p["current_attempt"]})
    elif f=="approval_wait":
        a.append({"kind":"unit","unit":"approval_requested"})
    elif f=="parallel_join":
        for b in p["completed"]: a.append({"kind":"unit","unit":b})
    elif f=="loop_pause":
        for i in range(1,p["current"]+1): a.append({"kind":"unit","unit":f"loop_iter_{i}"})
        a.append({"kind":"counter","key":p["counter_key"],"value":p["current"]})
        if p.get("break"): a.append({"kind":"decision","key":"break","value":True})
    elif f=="compensation_pending":
        if p["effect_status"]=="committed": a.append({"kind":"effect","operation":p["operation"],"unit":"effect_attempt"})
        else: a.append({"kind":"unit","unit":"effect_attempt"})
        a.append({"kind":"unit","unit":"error_detected"})
    elif f=="async_callback":
        a.append({"kind":"unit","unit":"callback_requested"})
    else: raise KeyError(f)
    return a

def oracle_plan(case):
    p=case.params; f=case.family; a=[]
    if f=="effect_commitment":
        if p["effect_status"]=="not_committed": a.append({"kind":"effect","operation":p["operation"],"unit":"effect_attempt"})
        a += [{"kind":"unit","unit":"ack"},{"kind":"finish"}]
    elif f=="retry_pause":
        cur,mx=p["current_attempt"],p["max_attempts"]
        if cur < mx:
            a += [{"kind":"unit","unit":f"retry_attempt_{cur+1}"},{"kind":"counter","key":"retry:retry_task","value":cur+1}]
        else: a.append({"kind":"unit","unit":"retry_exhausted_handler"})
        a.append({"kind":"finish"})
    elif f=="approval_wait":
        a += [{"kind":"approval","id":p["request_id"],"unit":p["approval_unit"]},{"kind":"finish"}]
    elif f=="parallel_join":
        for b in p["branches"]:
            if b not in p["completed"]: a.append({"kind":"unit","unit":b})
        a += [{"kind":"unit","unit":p["join"]},{"kind":"finish"}]
    elif f=="loop_pause":
        if not p.get("break"):
            for i in range(p["current"]+1,p["total"]+1):
                a += [{"kind":"unit","unit":f"loop_iter_{i}"},{"kind":"counter","key":p["counter_key"],"value":i}]
        a += [{"kind":"unit","unit":"loop_exit"},{"kind":"finish"}]
    elif f=="compensation_pending":
        if p["effect_status"]=="committed": a.append({"kind":"compensation","action":p["compensation"],"unit":"compensation"})
        else: a.append({"kind":"unit","unit":"compensation_skipped"})
        a.append({"kind":"finish"})
    elif f=="async_callback":
        a += [{"kind":"callback","id":p["callback_id"],"unit":p["callback_unit"]},{"kind":"finish"}]
    else: raise KeyError(f)
    return a

def apply_source_pause(case,store_path):
    s=SemanticStore(store_path)
    for a in source_actions(case): s.apply(a)
    return s.read()

def apply_plan(plan,store_path):
    s=SemanticStore(store_path)
    for a in plan: s.apply(a)
    return s.read()


def expected_source(case):
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"store.json"
        apply_source_pause(case,p)
        return SemanticStore(p).read()

def expected_final(case):
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"store.json"; apply_source_pause(case,p); apply_plan(oracle_plan(case),p); return SemanticStore(p).read()

def truth_projection(case):
    p=case.params; f=case.family
    completed=[]; pending=[]; effects={}; deps={}; decisions={}; counters={}
    if f=="effect_commitment":
        completed=["effect_attempt"]; effects[p["operation"]]=p["effect_status"]; pending=[{"type":"ack","id":"ack","blocks":"finish"}]
    elif f=="retry_pause":
        completed=[f"retry_attempt_{i}" for i in range(1,p["current_attempt"]+1)]
        counters["retry:retry_task"]=p["current_attempt"]
        pending=[{"type":"retry","step":"retry_task","next_attempt":p["current_attempt"]+1,"max_attempts":p["max_attempts"]}]
    elif f=="approval_wait": pending=[{"type":"approval","id":p["request_id"],"blocks":p["approval_unit"]}]
    elif f=="parallel_join": completed=list(p["completed"]); deps[p["join"]]=list(p["branches"])
    elif f=="loop_pause":
        completed=[f"loop_iter_{i}" for i in range(1,p["current"]+1)]; counters[p["counter_key"]]=p["current"]
        if p.get("break"): decisions["break"]=True
    elif f=="compensation_pending":
        completed=["effect_attempt","error_detected"]; effects[p["operation"]]=p["effect_status"]
        if p["effect_status"]=="committed": pending=[{"type":"compensation","action":p["compensation"],"effect":p["operation"]}]
    elif f=="async_callback": pending=[{"type":"callback","id":p["callback_id"],"operation":p["operation"],"blocks":p["callback_unit"]}]
    return {"completed":completed,"pending":pending,"effects":effects,"dependencies":deps,"decisions":decisions,"counters":counters}

def derive_plan(rc,case):
    p=case.params; f=case.family; a=[]
    if f=="effect_commitment":
        status=rc.effect_facts.get(p["operation"],{}).get("status","unknown")
        if status=="not_committed": a.append({"kind":"effect","operation":p["operation"],"unit":"effect_attempt"})
        elif status=="committed": pass
        else: a.append({"kind":"effect","operation":p["operation"],"unit":"effect_attempt"})  # optimistic baseline replay
        a += [{"kind":"unit","unit":"ack"},{"kind":"finish"}]
    elif f=="retry_pause":
        obs=None
        for o in rc.pending_obligations:
            if o.get("type")=="retry" and o.get("step")=="retry_task": obs=o; break
        if obs:
            nxt=int(obs.get("next_attempt",1)); mx=int(obs.get("max_attempts",0))
            if nxt<=mx and mx>0: a += [{"kind":"unit","unit":f"retry_attempt_{nxt}"},{"kind":"counter","key":"retry:retry_task","value":nxt}]
            else: a.append({"kind":"unit","unit":"retry_exhausted_handler"})
        else:
            a += [{"kind":"unit","unit":"retry_attempt_1"},{"kind":"counter","key":"retry:retry_task","value":1}]
        a.append({"kind":"finish"})
    elif f=="approval_wait":
        aps=[o for o in rc.pending_obligations if o.get("type")=="approval"]
        if aps: a.append({"kind":"approval","id":p["request_id"],"unit":p["approval_unit"]})
        a.append({"kind":"finish"})
    elif f=="parallel_join":
        req=list(rc.dependencies.get(p["join"],p["branches"])); done=set(rc.completed_units)
        for b in req:
            if b not in done: a.append({"kind":"unit","unit":b})
        a += [{"kind":"unit","unit":p["join"]},{"kind":"finish"}]
    elif f=="loop_pause":
        br=rc.decisions.get("break",False)
        if isinstance(br,str): br=br.lower()=="true"
        cur=int(rc.counters.get(p["counter_key"],0))
        if not br:
            for i in range(cur+1,p["total"]+1): a += [{"kind":"unit","unit":f"loop_iter_{i}"},{"kind":"counter","key":p["counter_key"],"value":i}]
        a += [{"kind":"unit","unit":"loop_exit"},{"kind":"finish"}]
    elif f=="compensation_pending":
        status=rc.effect_facts.get(p["operation"],{}).get("status","unknown")
        pending=any(o.get("type")=="compensation" and o.get("action")==p["compensation"] for o in rc.pending_obligations)
        if status=="committed" and pending: a.append({"kind":"compensation","action":p["compensation"],"unit":"compensation"})
        elif status=="not_committed": a.append({"kind":"unit","unit":"compensation_skipped"})
        elif status=="committed" and not pending: a.append({"kind":"unit","unit":"compensation_skipped"})
        else: a.append({"kind":"unit","unit":"compensation_skipped"})
        a.append({"kind":"finish"})
    elif f=="async_callback":
        ok=any(o.get("type")=="callback" and o.get("operation")==p["operation"] for o in rc.pending_obligations)
        if ok: a.append({"kind":"callback","id":p["callback_id"],"unit":p["callback_unit"]})
        a.append({"kind":"finish"})
    return a

def v2_case_spec(case):
    from crossresumebench_v2.models import CaseSpec
    p=case.params; f=case.family; actions=[]; deps={}
    if f=="effect_commitment": actions=[{"action_id":"effect_guard","semantic_unit":"effect_guard","kind":"effect","operation":p["operation"]},{"action_id":"ack","semantic_unit":"ack","kind":"step"},{"action_id":"finish","semantic_unit":"finish","kind":"finish"}]
    elif f=="retry_pause": actions=[{"action_id":"retry_task","semantic_unit":"retry_task","kind":"step"},{"action_id":"finish","semantic_unit":"finish","kind":"finish"}]
    elif f=="approval_wait": actions=[{"action_id":"approval","semantic_unit":p["approval_unit"],"kind":"approval"},{"action_id":"finish","semantic_unit":"finish","kind":"finish"}]
    elif f=="parallel_join":
        actions=[{"action_id":b,"semantic_unit":b,"kind":"step"} for b in p["branches"]]+[{"action_id":p["join"],"semantic_unit":p["join"],"kind":"join"},{"action_id":"finish","semantic_unit":"finish","kind":"finish"}]; deps[p["join"]]=list(p["branches"])
    elif f=="loop_pause": actions=[{"action_id":"loop_body","semantic_unit":"loop_body","kind":"step"},{"action_id":"finish","semantic_unit":"finish","kind":"finish"}]
    elif f=="compensation_pending": actions=[{"action_id":"effect_guard","semantic_unit":"effect_guard","kind":"effect","operation":p["operation"]},{"action_id":"compensation","semantic_unit":"compensation","kind":"compensation"},{"action_id":"finish","semantic_unit":"finish","kind":"finish"}]
    elif f=="async_callback": actions=[{"action_id":"callback","semantic_unit":p["callback_unit"],"kind":"callback"},{"action_id":"finish","semantic_unit":"finish","kind":"finish"}]
    return CaseSpec(case.case_id,case.family,case.index,SAFE_APP_STATE,[],actions,deps,[],{},[],"native_pause","target_resume",{"description":case.description})
