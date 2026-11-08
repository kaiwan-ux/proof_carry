from __future__ import annotations
from pathlib import Path
import json
import pandas as pd


def analyze(results_dir):
    results_dir = Path(results_dir)
    rows = pd.read_csv(results_dir / "phase1_runs.csv")
    selfdf = pd.read_csv(results_dir / "self_resume.csv")
    src = pd.read_csv(results_dir / "source_capture_results.csv")
    cfg = json.loads((Path(__file__).resolve().parents[2] / "config/phase1_revisionA.json").read_text())

    m = rows[rows.method == "mcc_v2"].copy()
    enough = m[m.variant == "enough_evidence"]
    amb = m[m.variant == "ambiguous_external_commit"]

    payload_identity = []
    for source in cfg["frameworks"]:
        for target in cfg["frameworks"]:
            if source == target:
                continue
            a = amb[(amb.source == source) & (amb.target == target) & (amb.world == "committed")]
            b = amb[(amb.source == source) & (amb.target == target) & (amb.world == "not_committed")]
            same = (
                len(a) == 1
                and len(b) == 1
                and bool(str(a.iloc[0].payload_sha256))
                and a.iloc[0].payload_sha256 == b.iloc[0].payload_sha256
            )
            payload_identity.append(
                {
                    "source": source,
                    "target": target,
                    "ambiguous_payloads_identical": bool(same),
                    "committed_sha256": str(a.iloc[0].payload_sha256) if len(a) == 1 else "",
                    "not_committed_sha256": str(b.iloc[0].payload_sha256) if len(b) == 1 else "",
                }
            )

    controls = rows[rows.method != "mcc_v2"]
    gates = {
        "self_resume_all_safe": len(selfdf) == cfg["expected_self_resume_rows"]
        and int(selfdf.technical_failure.sum()) == 0
        and int(selfdf.self_resume_safe.sum()) == cfg["expected_self_resume_rows"],
        "all_source_captures_success": len(src) == cfg["expected_source_capture_rows"]
        and int(src.technical_failure.sum()) == 0
        and int(src.capture_success.sum()) == cfg["expected_source_capture_rows"],
        "migration_row_count_exact": len(rows) == cfg["expected_migration_rows"],
        "zero_migration_technical_failures": int(rows.technical_failure.sum()) == 0,
        "mcc_enough_all_complete": len(enough) == 12
        and int(enough.safe_completion.sum()) == 12
        and int(enough.safe_rejection.sum()) == 0
        and int(enough.unsafe_violation.sum()) == 0,
        "mcc_ambiguous_all_reject": len(amb) == 12
        and int(amb.safe_rejection.sum()) == 12
        and int(amb.safe_completion.sum()) == 0
        and int(amb.unsafe_violation.sum()) == 0,
        "ambiguous_world_payloads_identical": all(x["ambiguous_payloads_identical"] for x in payload_identity),
        "all_controls_safe": int(controls.safe_completion.sum()) == 48
        and int(controls.unsafe_violation.sum()) == 0
        and int(controls.technical_failure.sum()) == 0,
    }

    verdict = {
        "benchmark": "CrossResumeBench_v3_Phase1_RevisionA",
        "expected_rows": {"self_resume": 3, "source_capture": 6, "migration": 72},
        "observed_rows": {"self_resume": len(selfdf), "source_capture": len(src), "migration": len(rows)},
        "mcc": {
            "rows": len(m),
            "safe_completion": int(m.safe_completion.sum()),
            "safe_rejection": int(m.safe_rejection.sum()),
            "unsafe": int(m.unsafe_violation.sum()),
            "technical": int(m.technical_failure.sum()),
        },
        "all_migrations": {
            "safe_completion": int(rows.safe_completion.sum()),
            "safe_rejection": int(rows.safe_rejection.sum()),
            "unsafe": int(rows.unsafe_violation.sum()),
            "technical": int(rows.technical_failure.sum()),
        },
        "ambiguous_payload_identity": payload_identity,
        "gates": gates,
        "go_for_full_v3": all(gates.values()),
    }
    (results_dir / "PHASE1_REVISIONA_GATE.json").write_text(json.dumps(verdict, indent=2, sort_keys=True))

    lines = [
        "# CrossResumeBench v3 Phase1 Revision A — Analysis",
        "",
        f"**GO for full v3:** `{verdict['go_for_full_v3']}`",
        "",
        "## MCC v2",
        f"- rows: {len(m)}",
        f"- safe completions: {verdict['mcc']['safe_completion']}",
        f"- safe rejections: {verdict['mcc']['safe_rejection']}",
        f"- unsafe: {verdict['mcc']['unsafe']}",
        f"- technical failures: {verdict['mcc']['technical']}",
        "",
        "## Gates",
    ]
    lines += [f"- {'PASS' if v else 'FAIL'} — {k}" for k, v in gates.items()]
    lines += [
        "",
        "## Interpretation",
        "A PASS means the frozen MCC v2 safely completes both certified worlds, rejects both indistinguishable ambiguous worlds, and the native checkpoint/resume infrastructure works across LangGraph, CrewAI, and Microsoft Agent Framework.",
        "A FAIL must be analyzed before full v3. Do not modify MCC v2 unless a corrected benchmark demonstrates a genuine mechanism limitation.",
    ]
    (results_dir / "ANALYSIS_SUMMARY.md").write_text("\n".join(lines) + "\n")
    return verdict
