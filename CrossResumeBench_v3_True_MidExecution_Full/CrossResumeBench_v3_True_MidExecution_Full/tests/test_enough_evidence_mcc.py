from pathlib import Path
from crossresumebench_v3_full.cases import CASES
from crossresumebench_v3_full.evidence import source_capture
from crossresumebench_v3_full.semantics import v2_case_spec,derive_plan,oracle_plan,expected_final
from crossresumebench_v3_full.baselines import build_and_lower
from crossresumebench_v3_full.frozen import FROZEN
from .fakes import FakeRuntime

def strip(d): x=dict(d); x.pop("trace",None); return x

def test_all_enough_evidence_cases_are_mcc_completable(tmp_path):
    for c in CASES:
        rt=FakeRuntime("langgraph"); rd=tmp_path/c.case_id; rd.mkdir(); n=rt.capture_case_pause(c,rd); cap=source_capture(c,n,"enough_evidence"); pkg,rc,reject=build_and_lower("mcc_v2",cap,c,v2_case_spec(c),"crewai",FROZEN)
        assert rc is not None, (c.case_id,reject)
        assert derive_plan(rc,c)==oracle_plan(c), c.case_id
