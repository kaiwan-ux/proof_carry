from crossresumebench_v3_full.runner import run
from crossresumebench_v3_full.analysis import analyze
from .fakes import factory
def test_full_orchestration_fake(tmp_path):
    out=run(tmp_path,runtime_factory=factory,skip_native_family_gate=True); assert out["migration_rows"]==3360
    a=analyze(tmp_path); assert a["actual_migration_rows"]==3360; assert a["mcc"]["enough_complete"]==168; assert a["mcc"]["enough_unsafe"]==0; assert a["mcc"]["technical"]==0
