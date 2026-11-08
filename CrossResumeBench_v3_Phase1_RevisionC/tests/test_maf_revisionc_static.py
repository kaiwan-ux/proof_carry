from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAF = ROOT / "src" / "crossresumebench_v3_revc" / "native" / "maf_runtime.py"


def test_maf_uses_explicit_handler_types():
    txt = MAF.read_text(encoding="utf-8")
    assert "@handler(input=str, output=str)" in txt
    assert "@handler(input=str, workflow_output=str)" in txt
    assert "WorkflowContext[" not in txt
    assert "from agent_framework import Executor, WorkflowBuilder, handler" in txt


def test_maf_uses_documented_checkpoint_boundary():
    txt = MAF.read_text(encoding="utf-8")
    assert "superstep_completed" in txt
    assert "get_latest(workflow_name=workflow.name)" in txt
    assert "checkpoint_id=checkpoint_id" in txt
    assert "checkpoint_storage=storage" in txt
