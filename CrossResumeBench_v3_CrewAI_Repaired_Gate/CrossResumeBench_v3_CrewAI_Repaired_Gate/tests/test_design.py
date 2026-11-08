
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_crewai_only_config():
    cfg=json.loads((ROOT/"config/crewai_gate.json").read_text())
    assert cfg["framework"]=="crewai"
    assert cfg["expected_migration_rows"]==12
    assert cfg["worlds"]==["committed","not_committed"]
    assert set(cfg["evidence_variants"])=={"enough_evidence","ambiguous_external_commit"}
    assert set(cfg["migration_methods"])=={"mcc_v2","oracle","explicit_minimal"}

def test_no_other_runtime_sources():
    native=ROOT/"src/crossresumebench_crewai_gate/native"
    names={p.name for p in native.glob("*_runtime.py")}
    assert names=={"crewai_runtime.py"}
