from pathlib import Path
import json,sys,time
import pytest
from crossresumebench_mccv3.infra.process_guard import run_json_worker,IsolatedCallTimeout

def _worker(tmp_path, body):
    p=tmp_path/'worker.py'; p.write_text(body,encoding='utf-8'); return p

def test_response_survives_worker_that_does_not_exit_cleanly(tmp_path):
    w=_worker(tmp_path,"""import json,sys,time\nfrom pathlib import Path\nreq,resp=Path(sys.argv[1]),Path(sys.argv[2])\nresp.write_text(json.dumps({'status':'ok','result':{'value':7}}),encoding='utf-8')\ntime.sleep(30)\n""")
    d=run_json_worker(root=tmp_path,worker=w,request={'x':1},run_dir=tmp_path/'run',timeout_seconds=5)
    assert d['status']=='ok' and d['result']['value']==7

def test_timeout_is_bounded_and_diagnostic_files_exist(tmp_path):
    w=_worker(tmp_path,"""import time\ntime.sleep(30)\n""")
    rd=tmp_path/'run2'
    with pytest.raises(IsolatedCallTimeout):
        run_json_worker(root=tmp_path,worker=w,request={'x':1},run_dir=rd,timeout_seconds=.35)
    assert (rd/'isolated_worker.stdout.txt').exists()
    assert (rd/'isolated_worker.stderr.txt').exists()
