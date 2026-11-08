from portaflow_native.models import SourceCapture,LogicalState
from portaflow_native.scenarios import initial_state,source_prefix_transition,continuation_transition
from portaflow_native.capsules import export_capsule,import_capsule
from portaflow_native.evaluator import evaluate

def cap(w):
    led={}; s=source_prefix_transition(initial_state(w),led)
    return SourceCapture("test",w,s.to_dict(),{"kind":"test"},led)

def test_naive_expected_failures():
    for w in ["retry","approval","side_effect"]:
        c=cap(w); led=dict(c.external_ledger); t=continuation_transition(import_capsule(export_capsule(c,"naive_state")),led)
        assert not evaluate(LogicalState.from_dict(c.state),t,led)["safe"]

def test_history_recovers_retry_and_approval_but_not_effect_commit():
    for w,expected in [("retry",True),("approval",True),("side_effect",False)]:
        c=cap(w); led=dict(c.external_ledger); t=continuation_transition(import_capsule(export_capsule(c,"state_history")),led)
        assert evaluate(LogicalState.from_dict(c.state),t,led)["safe"] is expected

def test_native_semantic_upper_bound():
    for w in ["retry","approval","side_effect"]:
        c=cap(w); led=dict(c.external_ledger); t=continuation_transition(import_capsule(export_capsule(c,"native_semantic")),led)
        assert evaluate(LogicalState.from_dict(c.state),t,led)["safe"]
