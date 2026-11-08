from crossresumebench_proofcarry.cases import CASES
from crossresumebench_proofcarry.runner import fake_native
from crossresumebench_proofcarry.evidence import generate
from crossresumebench_proofcarry.baselines import build_and_lower

def test_missing_binding_rejects():
    c=CASES[3]; cap=generate(c,fake_native(c,'langgraph'),'langgraph','maf','runtime_binding_missing'); _,plan,reason,_=build_and_lower('proofcarry',cap,c,'maf'); assert plan is None; assert 'UNPROVEN_REQUIRED_FACT' in reason or 'INVALID' in reason
