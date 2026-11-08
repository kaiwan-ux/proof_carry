from __future__ import annotations
from pathlib import Path
from ..models import NativePause
from ..native import get_runtime
from .process_guard import run_json_worker, IsolatedCallError, IsolatedCallTimeout

ROOT=Path(__file__).resolve().parents[3]
WORKER=ROOT/'scripts'/'native_operation_worker.py'

class IsolatedRuntime:
    """Infrastructure wrapper.

    self_resume_case() and capture_case_pause() execute in a disposable Python
    subprocess with a hard timeout. run_plan() remains in-process because the
    earlier full-v3 run already validated target-runtime lifecycle stability and
    spawning thousands of target subprocesses would add avoidable experimental
    overhead. No MCC/holdout/evaluator code is changed.
    """
    def __init__(self,name:str,self_timeout:float=90,capture_timeout:float=75):
        self.name=name; self.self_timeout=float(self_timeout); self.capture_timeout=float(capture_timeout)
    def capability_probe(self):
        return get_runtime(self.name).capability_probe()
    def _call(self,op,case,run_dir,timeout):
        req={'operation':op,'framework':self.name,'case_id':case.case_id,'run_dir':str(Path(run_dir).resolve())}
        return run_json_worker(root=ROOT,worker=WORKER,request=req,run_dir=Path(run_dir),timeout_seconds=timeout)
    def capture_case_pause(self,case,run_dir):
        d=self._call('capture',case,run_dir,self.capture_timeout)
        if d.get('status')!='ok': raise IsolatedCallError(d.get('error') or f'capture failed: {d}')
        p=d['result']
        return NativePause(p['framework'],p['case_id'],p['checkpoint_ref'],p['native_kind'],list(p['pending_work']),dict(p['app_state']),dict(p['native_observation']),dict(p['source_store']))
    def self_resume_case(self,case,run_dir):
        d=self._call('self_resume',case,run_dir,self.self_timeout)
        if d.get('status') not in {'ok','semantic_complete_lifecycle_hang'}:
            raise IsolatedCallError(d.get('error') or f'self resume failed: {d}')
        r=dict(d.get('result') or {})
        r['isolated_status']=d.get('status')
        r['lifecycle_returned']=bool(d.get('lifecycle_returned', d.get('status')=='ok'))
        r['duration_sec']=d.get('duration_sec')
        # Lifecycle return is part of the native self-resume control. A semantically
        # complete but non-returning runtime is diagnosed, not silently passed.
        if not r['lifecycle_returned']:
            r['semantic_safe']=bool(r.get('safe'))
            r['safe']=False
        return r
    def run_plan(self,case,plan,run_dir):
        return get_runtime(self.name).run_plan(case,plan,run_dir)

def isolated_runtime_factory(name):
    return IsolatedRuntime(name)
