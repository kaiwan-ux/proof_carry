import copy
from crossresumebench_proofcarry.cases import CASES
from crossresumebench_proofcarry.runner import fake_native
from crossresumebench_proofcarry.evidence import generate,target_contract,workflow_hash,VERIFICATION_TIME
from crossresumebench_proofcarry.baselines import PUBLIC_KEYS
from mechanism.proofcarry import build_payload,resolve
from mechanism.crypto import ReplayCache

def test_valid_and_replay_rejected():
    c=CASES[0]; cap=generate(c,fake_native(c,'langgraph'),'langgraph','crewai','enough_evidence'); con=target_contract(c,'crewai'); p=build_payload(cap,'crewai',workflow_hash(c),con)
    ps,r=resolve(p,con,PUBLIC_KEYS,VERIFICATION_TIME,ReplayCache()); assert r['admissible']
    q=copy.deepcopy(p); q['execution_id']+='-other'; ps,r=resolve(q,con,PUBLIC_KEYS,VERIFICATION_TIME,ReplayCache()); assert not r['admissible']; assert 'INVALID_ATTESTATION' in r['reason']
