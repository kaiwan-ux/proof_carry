from __future__ import annotations
import json,hashlib,shutil,traceback
from pathlib import Path
from .cases import CASES
from .runner import PAIRS,fake_native,write_csv
from .evidence import generate
from .baselines import ABLATIONS,run_ablation
from .semantics import expected_final,apply_source_pause,apply_plan
from .evaluator import evaluate

def run(results):
    results=Path(results); rows=[]
    # All 120 cases, all 6 pairs, four diagnostic conditions.
    conditions=['enough_evidence','missing_critical_fact','runtime_binding_complete','runtime_binding_missing']
    for case in CASES:
      exp=expected_final(case)
      for source,target in PAIRS:
       for cond in conditions:
        cap=generate(case,fake_native(case,source),source,target,cond)
        for ab in ABLATIONS:
          rid=f'ab|{case.case_id}|{source}->{target}|{cond}|{ab}'
          try:
            payload,plan,reject,rep=run_ablation(ab,cap,case,target); pb=len(json.dumps(payload,sort_keys=True,separators=(',',':'),default=str).encode())
            if plan is None: row={'run_id':rid,'case_id':case.case_id,'family':case.family,'source':source,'target':target,'condition':cond,'ablation':ab,'safe_completion':0,'safe_rejection':1,'unsafe':0,'payload_bytes':pb,'reason':reject}
            else:
              td=results/'ablation_tmp'/hashlib.sha256(rid.encode()).hexdigest(); shutil.rmtree(td,ignore_errors=True); td.mkdir(parents=True); sp=td/'s.json'; apply_source_pause(case,sp); actual=apply_plan(plan,sp); safe,fail=evaluate(exp,actual); row={'run_id':rid,'case_id':case.case_id,'family':case.family,'source':source,'target':target,'condition':cond,'ablation':ab,'safe_completion':int(safe),'safe_rejection':0,'unsafe':int(not safe),'payload_bytes':pb,'failure_types':fail}
            rows.append(row)
          except Exception: rows.append({'run_id':rid,'case_id':case.case_id,'family':case.family,'source':source,'target':target,'condition':cond,'ablation':ab,'technical_failure':1,'error':traceback.format_exc()})
    write_csv(results/'ablation_runs.csv',rows); shutil.rmtree(results/'ablation_tmp',ignore_errors=True); return rows
