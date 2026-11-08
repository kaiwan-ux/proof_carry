import json, unittest
from pathlib import Path
from proofcarry.contracts import contract_from_case
from proofcarry.evidence import build_evidence
from proofcarry.engine import ProofCarryEngine
from proofcarry.security import make_attack

ROOT=Path(__file__).resolve().parents[1]
CASES=[json.loads(x) for x in (ROOT/'benchmark/cases/all_cases.jsonl').read_text().splitlines() if x.strip()]
class TestCore(unittest.TestCase):
    def test_case_count(self):
        self.assertEqual(len(CASES),120)
        self.assertEqual({c['workflow_family'] for c in CASES},{'effect_commitment','retry','approval','parallel','loop','compensation','callback','composite'})
    def test_full_continue_enough(self):
        c=CASES[0]; co=contract_from_case(c); ev=build_evidence(c,'langgraph','crewai','enough'); r=ProofCarryEngine().resolve(c,co,ev); self.assertEqual(r.decision.value,'CONTINUE')
    def test_missing_rejects(self):
        c=CASES[1]; co=contract_from_case(c); ev=build_evidence(c,'langgraph','maf','missing_critical'); r=ProofCarryEngine().resolve(c,co,ev); self.assertEqual(r.decision.value,'REJECT')
    def test_wrong_mapping_rejects(self):
        c=CASES[2]; co=contract_from_case(c); ev=build_evidence(c,'crewai','maf','identity_missing'); r=ProofCarryEngine().resolve(c,co,ev); self.assertEqual(r.reason,'IDENTITY_MISMATCH')
    def test_rehashed_forgery_rejected_authenticated(self):
        c=CASES[0]; co=contract_from_case(c); ev=make_attack(c,'langgraph','crewai','rehashed_forgery'); r=ProofCarryEngine(authentication=True).resolve(c,co,ev); self.assertEqual(r.decision.value,'REJECT'); self.assertEqual(r.reason,'INVALID_SIGNATURE')
    def test_rehashed_forgery_can_bypass_hash_only(self):
        c=CASES[0]; co=contract_from_case(c); ev=make_attack(c,'langgraph','crewai','rehashed_forgery'); r=ProofCarryEngine(authentication=False).resolve(c,co,ev); self.assertEqual(r.decision.value,'CONTINUE'); self.assertNotEqual(r.plan,c['safe_plan'])
if __name__=='__main__': unittest.main()
