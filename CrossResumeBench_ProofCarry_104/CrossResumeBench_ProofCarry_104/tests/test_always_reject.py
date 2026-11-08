from crossresumebench_proofcarry.cases import CASES
from crossresumebench_proofcarry.runner import fake_native
from crossresumebench_proofcarry.evidence import generate
from crossresumebench_proofcarry.baselines import build_and_lower

def test_always_reject_has_zero_coverage():
    c=CASES[0]; cap=generate(c,fake_native(c,'crewai'),'crewai','maf','enough_evidence'); _,plan,reason,_=build_and_lower('always_reject',cap,c,'maf'); assert plan is None and reason=='ALWAYS_REJECT'
