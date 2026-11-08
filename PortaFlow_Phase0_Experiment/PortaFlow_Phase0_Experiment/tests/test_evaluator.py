from portaflow_phase0.baselines import export_capsule, import_capsule
from portaflow_phase0.evaluator import evaluate
from portaflow_phase0.workflows import run_prefix, resume_from_state


def test_oracle_all_workflows_safe():
    for name in ("linear","branch","loop","retry","approval","side_effect"):
        p=run_prefix(name,0)
        f=resume_from_state(import_capsule(export_capsule(p,"oracle_full")))
        ev=evaluate(p,f)
        assert ev.safe, (name,ev.failure_types,ev.invariant_results)
