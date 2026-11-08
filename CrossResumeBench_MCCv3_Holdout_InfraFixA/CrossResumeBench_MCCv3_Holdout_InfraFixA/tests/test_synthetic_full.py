from pathlib import Path
from crossresumebench_mccv3.cases import CASES
from crossresumebench_mccv3.evidence import generate
from crossresumebench_mccv3.baselines import build_and_lower
from crossresumebench_mccv3.semantics import expected_final, apply_source_pause, apply_plan
from crossresumebench_mccv3.store import SemanticStore
from .fakes import factory


def _eq(a,b):
    a=dict(a); b=dict(b); a.pop('trace',None); b.pop('trace',None); return a==b


def test_all_128_holdout_variants_mccv3(tmp_path):
    # Fast mechanism-level smoke test: all sealed case/variant combinations once,
    # without multiplying across six framework pairs or eight baselines.
    for c in CASES:
        srcdir=tmp_path/c.case_id
        native=factory('langgraph').capture_case_pause(c,srcdir)
        for variant in c.variants:
            cap=generate(c,native,variant)
            payload,plan,reject,report=build_and_lower('mcc_v3',cap,c,'crewai')
            exp=c.variant_expectations[variant]
            if exp=='safe_rejection':
                assert plan is None and reject
            else:
                assert plan is not None and not reject
                run=tmp_path/f"run-{c.case_id}-{variant}"; run.mkdir(parents=True,exist_ok=True)
                store=run/'semantic_store.json'; apply_source_pause(c,store); apply_plan(plan,store)
                assert _eq(expected_final(c),SemanticStore(store).read())
