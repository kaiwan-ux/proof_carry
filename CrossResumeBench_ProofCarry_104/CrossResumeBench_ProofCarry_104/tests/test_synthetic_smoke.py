from crossresumebench_proofcarry.cases import CASES
from crossresumebench_proofcarry.runner import fake_native
from crossresumebench_proofcarry.evidence import generate
from crossresumebench_proofcarry.baselines import build_and_lower
from crossresumebench_proofcarry.semantics import expected_final,apply_source_pause,apply_plan
from crossresumebench_proofcarry.evaluator import evaluate
from tempfile import TemporaryDirectory
from pathlib import Path

def test_all_104_enough_evidence_complete_synthetically():
    for c in CASES:
        cap=generate(c,fake_native(c,'langgraph'),'langgraph','crewai','enough_evidence'); _,plan,reason,_=build_and_lower('proofcarry',cap,c,'crewai'); assert plan is not None,(c.case_id,reason)
        with TemporaryDirectory() as td:
            p=Path(td)/'s.json'; apply_source_pause(c,p); actual=apply_plan(plan,p); safe,fail=evaluate(expected_final(c),actual); assert safe,(c.case_id,fail,plan,c.oracle_plan)
