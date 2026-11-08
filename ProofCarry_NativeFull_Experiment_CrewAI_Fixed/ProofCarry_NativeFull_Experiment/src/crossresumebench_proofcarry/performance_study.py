from __future__ import annotations
import json,socket,threading,time,tracemalloc,psutil,traceback,shutil
from pathlib import Path
from .cases import CASES
from .runner import PAIRS,write_csv
from .evidence import generate
from .baselines import build_and_lower
from .native import get_runtime
from .infra.isolated_runtime import isolated_runtime_factory
from .store import SemanticStore
from .evaluator import evaluate
from .semantics import expected_final

def loopback_transfer(payload_bytes:bytes):
    ready=threading.Event(); result={}
    def server():
        s=socket.socket(); s.bind(('127.0.0.1',0)); s.listen(1); result['port']=s.getsockname()[1]; ready.set(); c,_=s.accept(); data=b''
        while True:
            z=c.recv(65536)
            if not z: break
            data+=z
        result['bytes']=len(data); c.close(); s.close()
    th=threading.Thread(target=server,daemon=True); th.start(); ready.wait(); t0=time.perf_counter_ns(); c=socket.create_connection(('127.0.0.1',result['port'])); c.sendall(payload_bytes); c.shutdown(socket.SHUT_WR); c.close(); th.join(); return (time.perf_counter_ns()-t0)/1e6,result.get('bytes',0)

def selected_cases():
    # 24 stratified cases: 3 per family.
    out=[]
    for fam in sorted({c.family for c in CASES}): out.extend([c for c in CASES if c.family==fam][:3])
    return out

def run(results,repeats=5):
    results=Path(results); rows=[]; methods=['proofcarry','proofcarry_no_auth']
    for case in selected_cases():
      exp=expected_final(case)
      for source,target in PAIRS:
        for rep in range(repeats):
          capture_id=f'perf_capture|{case.case_id}|{source}->{target}|{rep}'
          base=results/'perf_work'/capture_id.replace('|','_').replace('>','')
          shutil.rmtree(base,ignore_errors=True); base.mkdir(parents=True)
          try:
            t=time.perf_counter_ns(); native=isolated_runtime_factory(source).capture_case_pause(case,base/'source'); capture_ms=(time.perf_counter_ns()-t)/1e6
            t=time.perf_counter_ns(); cap=generate(case,native,source,target,'enough_evidence'); evidence_ms=(time.perf_counter_ns()-t)/1e6
            cpdir=base/'source'/'checkpoints'; checkpoint_bytes=sum(p.stat().st_size for p in cpdir.rglob('*') if p.is_file()) if cpdir.exists() else 0
            pause_metadata_bytes=len(json.dumps(native.to_dict(),sort_keys=True,separators=(',',':'),default=str).encode())
          except Exception:
            for method in methods: rows.append({'run_id':f'{capture_id}|{method}','method':method,'case_id':case.case_id,'family':case.family,'source':source,'target':target,'repeat':rep,'technical_failure':1,'stage':'capture','error':traceback.format_exc()})
            continue
          for method in methods:
            rid=f'{capture_id}|{method}'; rd=base/method; rd.mkdir(parents=True,exist_ok=True)
            try:
              t_total=time.perf_counter_ns(); cpu0=time.process_time_ns()
              tracemalloc.start(); t=time.perf_counter_ns(); payload,plan,reject,report=build_and_lower(method,cap,case,target); proof_ms=(time.perf_counter_ns()-t)/1e6; _,proof_peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
              t=time.perf_counter_ns(); raw=json.dumps(payload,sort_keys=True,separators=(',',':'),default=str).encode(); serialize_ms=(time.perf_counter_ns()-t)/1e6
              network_ms,network_bytes=loopback_transfer(raw)
              if plan is None: raise RuntimeError(f'{method} rejected enough_evidence: {reject}')
              SemanticStore(rd/'semantic_store.json').write(native.source_store)
              t=time.perf_counter_ns(); out=get_runtime(target).run_plan(case,plan,rd); resume_ms=(time.perf_counter_ns()-t)/1e6
              safe,fail=evaluate(exp,out['store']); total_method_ms=(time.perf_counter_ns()-t_total)/1e6; cpu_ms=(time.process_time_ns()-cpu0)/1e6
              rows.append({'run_id':rid,'method':method,'case_id':case.case_id,'family':case.family,'source':source,'target':target,'repeat':rep,'safe':int(safe),'technical_failure':0,'capture_ms':capture_ms,'evidence_ms':evidence_ms,'proof_ms':proof_ms,'serialize_ms':serialize_ms,'loopback_network_ms':network_ms,'resume_ms':resume_ms,'method_path_ms':total_method_ms,'estimated_end_to_end_ms':capture_ms+evidence_ms+total_method_ms,'cpu_ms_parent':cpu_ms,'payload_bytes':len(raw),'network_bytes':network_bytes,'native_checkpoint_bytes':checkpoint_bytes,'native_pause_metadata_bytes':pause_metadata_bytes,'proof_peak_bytes':proof_peak,'failure_types':fail})
            except Exception: rows.append({'run_id':rid,'method':method,'case_id':case.case_id,'family':case.family,'source':source,'target':target,'repeat':rep,'technical_failure':1,'stage':'method','error':traceback.format_exc()})
    write_csv(results/'performance_runs.csv',rows); return rows
