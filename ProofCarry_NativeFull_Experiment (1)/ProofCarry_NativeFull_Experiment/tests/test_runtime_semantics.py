import json
from pathlib import Path

def test_runtime_semantic_namespaces_are_distinct():
    root=Path(__file__).resolve().parents[1]; d=json.loads((root/'config'/'runtime_semantics.json').read_text()); assert len({v['namespace'] for v in d.values()})==3; assert len({v['pause_status'] for v in d.values()})==3
