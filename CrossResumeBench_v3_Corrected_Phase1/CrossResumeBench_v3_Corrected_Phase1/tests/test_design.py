import json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def test_maf_is_not_autogen():
    text=(ROOT/'src/crossresumebench_v3/native/maf_runtime.py').read_text().lower()
    assert 'from autogen' not in text and 'import autogen' not in text
    assert 'agent_framework' in text

def test_phase1_has_all_six_pairs():
    c=json.loads((ROOT/'config/phase1.json').read_text()); assert len(c['pairs'])==6

def test_evidence_applicability_not_cartesian():
    a=json.loads((ROOT/'benchmark/evidence_applicability.json').read_text())
    assert 'ambiguous_external_commit' not in a['retry_only_default']
    assert 'ambiguous_external_commit' in a['effect_committed_ack_pending']

def test_native_self_resume_is_separate():
    c=json.loads((ROOT/'config/phase1.json').read_text()); assert c['self_resume_control'] is True
    assert 'framework_native_checkpoint' not in c['migration_methods']

def test_full_scope_disabled():
    c=json.loads((ROOT/'config/full_scope.json').read_text()); assert c['status'].startswith('PLANNED_NOT_ENABLED')
