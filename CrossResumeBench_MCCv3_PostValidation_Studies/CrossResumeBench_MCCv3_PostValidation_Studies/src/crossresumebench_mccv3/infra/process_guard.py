from __future__ import annotations
import json, os, signal, subprocess, sys, time
from pathlib import Path

class IsolatedCallError(RuntimeError):
    pass
class IsolatedCallTimeout(IsolatedCallError):
    pass

def _kill_tree(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == 'nt':
            subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        else:
            os.killpg(proc.pid, signal.SIGKILL)
    except Exception:
        try: proc.kill()
        except Exception: pass

def run_json_worker(*, root: Path, worker: Path, request: dict, run_dir: Path, timeout_seconds: float) -> dict:
    run_dir=Path(run_dir); run_dir.mkdir(parents=True,exist_ok=True)
    req=run_dir/'isolated_request.json'; resp=run_dir/'isolated_response.json'
    outp=run_dir/'isolated_worker.stdout.txt'; errp=run_dir/'isolated_worker.stderr.txt'
    req.write_text(json.dumps(request,indent=2,sort_keys=True),encoding='utf-8')
    if resp.exists(): resp.unlink()
    env=os.environ.copy()
    env.update({
        'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8','PYTHONUNBUFFERED':'1',
        'CREWAI_TRACING_ENABLED':'false','CREWAI_DISABLE_TELEMETRY':'true',
        'CREWAI_DISABLE_TRACKING':'true','OTEL_SDK_DISABLED':'true'
    })
    creationflags=0
    kwargs={}
    if os.name=='nt':
        creationflags=getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0)
    else:
        kwargs['start_new_session']=True
    t0=time.monotonic()
    with outp.open('wb') as fo, errp.open('wb') as fe:
        proc=subprocess.Popen([sys.executable,'-u',str(worker),str(req),str(resp)],cwd=str(root),env=env,stdout=fo,stderr=fe,creationflags=creationflags,**kwargs)
        deadline=t0+float(timeout_seconds)
        while True:
            # A response file is authoritative: the requested method returned or the worker
            # detected semantic completion + lifecycle hang and wrote a diagnostic result.
            if resp.exists():
                try:
                    data=json.loads(resp.read_text(encoding='utf-8'))
                    # Give clean runtimes a short grace period to exit. If they leave helper
                    # threads behind, terminate only this isolated worker tree after result capture.
                    try: proc.wait(timeout=2)
                    except subprocess.TimeoutExpired: _kill_tree(proc)
                    data.setdefault('duration_sec',round(time.monotonic()-t0,6))
                    return data
                except json.JSONDecodeError:
                    pass
            rc=proc.poll()
            if rc is not None:
                if resp.exists():
                    data=json.loads(resp.read_text(encoding='utf-8')); data.setdefault('duration_sec',round(time.monotonic()-t0,6)); return data
                raise IsolatedCallError(f'isolated worker exited rc={rc} without response; see {outp.name} / {errp.name}')
            if time.monotonic()>=deadline:
                _kill_tree(proc)
                raise IsolatedCallTimeout(f'isolated operation timed out after {timeout_seconds}s; see {outp.name} / {errp.name}')
            time.sleep(0.05)
