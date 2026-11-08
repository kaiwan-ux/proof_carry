from __future__ import annotations
import json, os, sys, threading, time, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/'src'),str(ROOT/'frozen_v2'/'src'),str(ROOT)]
from crossresumebench_proofcarry.cases import CASE_BY_ID
from crossresumebench_proofcarry.native import get_runtime
from crossresumebench_proofcarry.semantics import expected_final
from crossresumebench_proofcarry.store import SemanticStore

def _same(a,b):
    a=dict(a); b=dict(b); a.pop('trace',None); b.pop('trace',None); return a==b

def atomic_json(path,obj):
    path=Path(path); tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True,default=str),encoding='utf-8'); os.replace(tmp,path)

def main(req_path,resp_path):
    req=json.loads(Path(req_path).read_text(encoding='utf-8')); resp=Path(resp_path)
    case=CASE_BY_ID[req['case_id']]; runtime=get_runtime(req['framework']); run_dir=Path(req['run_dir'])
    op=req['operation']; t0=time.monotonic()
    try:
        if op=='capture':
            out=runtime.capture_case_pause(case,run_dir)
            atomic_json(resp,{'status':'ok','operation':op,'result':out.to_dict(),'lifecycle_returned':True,'worker_duration_sec':time.monotonic()-t0}); return
        if op!='self_resume': raise KeyError(op)
        box={}
        def target():
            try: box['result']=runtime.self_resume_case(case,run_dir)
            except BaseException as e: box['exc']=traceback.format_exc()
        th=threading.Thread(target=target,daemon=True); th.start()
        semantic_since=None
        while th.is_alive():
            store=SemanticStore(run_dir/'semantic_store.json').read()
            sem=_same(expected_final(case),store)
            if sem and semantic_since is None: semantic_since=time.monotonic()
            if semantic_since is not None and time.monotonic()-semantic_since>=8.0:
                # The semantic continuation completed but framework lifecycle did not return.
                # Preserve this as a diagnostic failure and terminate this disposable worker.
                atomic_json(resp,{'status':'semantic_complete_lifecycle_hang','operation':op,'lifecycle_returned':False,'result':{'restore_completed':True,'safe':True,'store':store},'worker_duration_sec':time.monotonic()-t0})
                os._exit(0)
            time.sleep(0.05)
        if 'exc' in box: atomic_json(resp,{'status':'error','operation':op,'error':box['exc'],'lifecycle_returned':True,'worker_duration_sec':time.monotonic()-t0}); return
        atomic_json(resp,{'status':'ok','operation':op,'result':box.get('result',{}),'lifecycle_returned':True,'worker_duration_sec':time.monotonic()-t0})
    except BaseException:
        atomic_json(resp,{'status':'error','operation':op,'error':traceback.format_exc(),'lifecycle_returned':True,'worker_duration_sec':time.monotonic()-t0})
if __name__=='__main__': main(sys.argv[1],sys.argv[2])
