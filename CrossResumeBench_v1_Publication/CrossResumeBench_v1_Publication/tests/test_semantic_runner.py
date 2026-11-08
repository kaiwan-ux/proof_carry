from pathlib import Path
import tempfile
from crossresumebench.generator import generate_suite
from crossresumebench.semantic_runner import run_suite
def test_small_semantic_run():
    p=Path(tempfile.mkdtemp())/'semantic'; rows=run_suite(generate_suite()[:2],['state_only','history_inference','mcc','oracle'],p); assert len(rows)==8
