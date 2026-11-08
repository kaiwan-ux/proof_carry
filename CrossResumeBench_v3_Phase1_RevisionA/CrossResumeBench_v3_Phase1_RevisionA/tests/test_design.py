import json
from pathlib import Path
from crossresumebench_v3_reva.case import case_spec

ROOT = Path(__file__).resolve().parents[1]


def test_exact_matrix():
    c = json.loads((ROOT / "config/phase1_revisionA.json").read_text())
    assert len(c["frameworks"]) * 2 * 2 * 2 * 3 == 72
    assert c["expected_migration_rows"] == 72
    assert c["full_v3_enabled"] is False


def test_target_contains_effect_guard():
    c = case_spec()
    assert any(a["kind"] == "effect" and a["operation"] == "effect" for a in c.target_actions)


def test_no_autogen_confusion():
    txt = "\n".join(p.read_text(errors="ignore") for p in (ROOT / "src").rglob("*.py"))
    assert "from autogen" not in txt and "GroupChat" not in txt
