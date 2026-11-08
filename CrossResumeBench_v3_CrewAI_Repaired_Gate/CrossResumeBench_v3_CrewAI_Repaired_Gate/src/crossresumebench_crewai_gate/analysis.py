
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd


def _sum(df, col):
    return int(df[col].fillna(0).astype(int).sum()) if col in df else 0


def analyze(results_dir: Path):
    results_dir = Path(results_dir)
    root = Path(__file__).resolve().parents[2]
    cfg = json.loads((root/"config"/"crewai_gate.json").read_text(encoding="utf-8"))
    rows = pd.read_csv(results_dir/"crewai_gate_runs.csv")
    selfdf = pd.read_csv(results_dir/"self_resume.csv")
    src = pd.read_csv(results_dir/"source_capture_results.csv")

    mcc = rows[rows.method == "mcc_v2"].copy()
    enough = mcc[mcc.variant == "enough_evidence"]
    amb = mcc[mcc.variant == "ambiguous_external_commit"]
    controls = rows[rows.method != "mcc_v2"]

    def one(df, world):
        x = df[df.world == world]
        return x.iloc[0] if len(x) == 1 else None

    ac = one(amb, "committed")
    an = one(amb, "not_committed")
    ambiguous_identical = bool(
        ac is not None and an is not None and
        int(ac.technical_failure) == 0 and int(an.technical_failure) == 0 and
        isinstance(ac.payload_sha256, str) and bool(ac.payload_sha256) and
        ac.payload_sha256 == an.payload_sha256
    )

    ec = one(enough, "committed")
    en = one(enough, "not_committed")
    certified_correct = bool(
        ec is not None and en is not None and
        int(ec.safe_completion) == 1 and int(en.safe_completion) == 1 and
        ec.actual_effect_decision == "skip_effect" and
        en.actual_effect_decision == "execute_effect"
    )

    committed_src = src[src.world == "committed"]
    not_src = src[src.world == "not_committed"]
    source_boundaries_correct = bool(
        len(committed_src) == 1 and len(not_src) == 1 and
        int(committed_src.iloc[0].capture_success) == 1 and
        int(not_src.iloc[0].capture_success) == 1 and
        int(committed_src.iloc[0].source_effect_count) == 1 and
        int(not_src.iloc[0].source_effect_count) == 0 and
        int(committed_src.iloc[0].source_ack_count) == 0 and
        int(not_src.iloc[0].source_ack_count) == 0 and
        int(committed_src.iloc[0].source_finish_count) == 0 and
        int(not_src.iloc[0].source_finish_count) == 0
    )

    terminal_exact = bool(len(rows) and all(
        int(r.safe_completion)+int(r.safe_rejection)+int(r.unsafe_violation)+int(r.technical_failure) == 1
        for _,r in rows.iterrows()
    ))

    gates = {
        "self_resume_restorable": len(selfdf) == 1 and _sum(selfdf,"technical_failure") == 0 and _sum(selfdf,"restore_completed") == 1,
        "both_source_captures_success": len(src) == 2 and _sum(src,"technical_failure") == 0 and _sum(src,"capture_success") == 2,
        "source_pause_boundaries_correct": source_boundaries_correct,
        "migration_row_count_exact": len(rows) == cfg["expected_migration_rows"],
        "one_terminal_outcome_per_row": terminal_exact,
        "zero_migration_technical_failures": _sum(rows,"technical_failure") == 0,
        "zero_unsafe_migrations": _sum(rows,"unsafe_violation") == 0,
        "mcc_enough_both_complete": len(enough) == 2 and _sum(enough,"safe_completion") == 2 and _sum(enough,"safe_rejection") == 0 and _sum(enough,"unsafe_violation") == 0 and _sum(enough,"technical_failure") == 0,
        "mcc_ambiguous_both_reject": len(amb) == 2 and _sum(amb,"safe_rejection") == 2 and _sum(amb,"safe_completion") == 0 and _sum(amb,"unsafe_violation") == 0 and _sum(amb,"technical_failure") == 0,
        "ambiguous_world_payloads_identical": ambiguous_identical,
        "certified_worlds_choose_opposite_correct_actions": certified_correct,
        "all_privileged_controls_safe": len(controls) == 8 and _sum(controls,"safe_completion") == 8 and _sum(controls,"safe_rejection") == 0 and _sum(controls,"unsafe_violation") == 0 and _sum(controls,"technical_failure") == 0,
    }

    verdict = {
        "benchmark": cfg["benchmark"],
        "scope": "CrewAI only; CrewAI source and CrewAI target",
        "expected_rows": {"self_resume":1,"source_capture":2,"migration":12},
        "observed_rows": {"self_resume":len(selfdf),"source_capture":len(src),"migration":len(rows)},
        "native_self_resume": {
            "restore_completed": _sum(selfdf,"restore_completed"),
            "safe": _sum(selfdf,"self_resume_safe"),
            "unsafe_native_replay": _sum(selfdf,"native_unsafe_replay"),
            "technical": _sum(selfdf,"technical_failure"),
            "note": "Native self-resume safety is reported separately; technical restorable behavior is the infrastructure gate."
        },
        "mcc": {
            "rows": len(mcc),
            "safe_completion": _sum(mcc,"safe_completion"),
            "safe_rejection": _sum(mcc,"safe_rejection"),
            "unsafe": _sum(mcc,"unsafe_violation"),
            "technical": _sum(mcc,"technical_failure"),
        },
        "all_migrations": {
            "safe_completion": _sum(rows,"safe_completion"),
            "safe_rejection": _sum(rows,"safe_rejection"),
            "unsafe": _sum(rows,"unsafe_violation"),
            "technical": _sum(rows,"technical_failure"),
        },
        "ambiguous_payload_sha256": {
            "committed": str(ac.payload_sha256) if ac is not None else "",
            "not_committed": str(an.payload_sha256) if an is not None else "",
            "identical": ambiguous_identical,
        },
        "gates": gates,
        "crewai_repaired_gate_pass": all(gates.values()),
    }
    (results_dir/"CREWAI_REPAIRED_GATE.json").write_text(json.dumps(verdict,indent=2,sort_keys=True), encoding="utf-8")

    lines = [
        "# CrewAI Repaired Gate — Generated Analysis", "",
        f"**CrewAI repaired gate PASS:** `{verdict['crewai_repaired_gate_pass']}`", "",
        "## Exact outcomes",
        f"- migration rows: {len(rows)}/12",
        f"- safe completions: {verdict['all_migrations']['safe_completion']}",
        f"- safe rejections: {verdict['all_migrations']['safe_rejection']}",
        f"- unsafe migrations: {verdict['all_migrations']['unsafe']}",
        f"- technical failures: {verdict['all_migrations']['technical']}",
        f"- MCC: {verdict['mcc']['safe_completion']} complete, {verdict['mcc']['safe_rejection']} reject, {verdict['mcc']['unsafe']} unsafe, {verdict['mcc']['technical']} technical",
        "",
        "## Gate checks",
    ]
    lines += [f"- {'PASS' if v else 'FAIL'} — {k}" for k,v in gates.items()]
    lines += [
        "", "## Interpretation",
        "This is a CrewAI adapter/integration gate, not a new MCC mechanism experiment.",
        "PASS means the repaired CrewAI checkpoint path is technically usable for the two-world continuation experiment and frozen MCC v2 behaves as preregistered on the focused CrewAI->CrewAI matrix.",
        "A FAIL must not be repaired by changing frozen MCC v2; diagnose CrewAI integration separately.",
    ]
    (results_dir/"ANALYSIS_SUMMARY.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    return verdict
