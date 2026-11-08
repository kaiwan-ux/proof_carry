from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _sum(df, col):
    return int(df[col].fillna(0).astype(int).sum()) if col in df else 0


def analyze(results_dir):
    results_dir = Path(results_dir)
    rows = pd.read_csv(results_dir / "phase1_runs.csv")
    selfdf = pd.read_csv(results_dir / "self_resume.csv")
    src = pd.read_csv(results_dir / "source_capture_results.csv")
    root = Path(__file__).resolve().parents[2]
    cfg = json.loads((root / "config" / "phase1_revisionB.json").read_text(encoding="utf-8"))

    m = rows[rows.method == "mcc_v2"].copy()
    enough = m[m.variant == "enough_evidence"]
    amb = m[m.variant == "ambiguous_external_commit"]
    controls = rows[rows.method != "mcc_v2"]

    payload_identity = []
    enough_disambiguation = []
    pair_facts = []
    for source in cfg["frameworks"]:
        for target in cfg["frameworks"]:
            if source == target:
                continue
            pair = rows[(rows.source == source) & (rows.target == target)]
            a = amb[(amb.source == source) & (amb.target == target) & (amb.world == "committed")]
            b = amb[(amb.source == source) & (amb.target == target) & (amb.world == "not_committed")]
            same = (
                len(a) == 1
                and len(b) == 1
                and a.iloc[0].technical_failure == 0
                and b.iloc[0].technical_failure == 0
                and isinstance(a.iloc[0].payload_sha256, str)
                and bool(a.iloc[0].payload_sha256)
                and a.iloc[0].payload_sha256 == b.iloc[0].payload_sha256
            )
            payload_identity.append({
                "source": source,
                "target": target,
                "ambiguous_payloads_identical": bool(same),
                "committed_sha256": str(a.iloc[0].payload_sha256) if len(a) == 1 else "",
                "not_committed_sha256": str(b.iloc[0].payload_sha256) if len(b) == 1 else "",
            })

            ec = enough[(enough.source == source) & (enough.target == target) & (enough.world == "committed")]
            en = enough[(enough.source == source) & (enough.target == target) & (enough.world == "not_committed")]
            disambiguates = (
                len(ec) == 1 and len(en) == 1
                and ec.iloc[0].technical_failure == 0 and en.iloc[0].technical_failure == 0
                and ec.iloc[0].safe_completion == 1 and en.iloc[0].safe_completion == 1
                and ec.iloc[0].actual_effect_decision == "skip_effect"
                and en.iloc[0].actual_effect_decision == "execute_effect"
            )
            enough_disambiguation.append({"source": source, "target": target, "certified_worlds_correct": bool(disambiguates)})

            pair_facts.append({
                "source": source,
                "target": target,
                "rows": len(pair),
                "safe_completion": _sum(pair, "safe_completion"),
                "safe_rejection": _sum(pair, "safe_rejection"),
                "unsafe": _sum(pair, "unsafe_violation"),
                "technical": _sum(pair, "technical_failure"),
            })

    self_resume = []
    for _, r in selfdf.iterrows():
        self_resume.append({
            "framework": r.framework,
            "restore_completed": bool(r.restore_completed),
            "safe": bool(r.self_resume_safe),
            "unsafe_native_replay": bool(r.native_unsafe_replay),
            "technical_failure": bool(r.technical_failure),
        })

    # Gate separates infrastructure validity from native-baseline safety. A runtime may
    # technically restore yet replay an effect; that is a meaningful baseline result.
    gates = {
        "self_resume_all_restorable": len(selfdf) == cfg["expected_self_resume_rows"]
        and _sum(selfdf, "technical_failure") == 0
        and _sum(selfdf, "restore_completed") == cfg["expected_self_resume_rows"],
        "all_source_captures_success": len(src) == cfg["expected_source_capture_rows"]
        and _sum(src, "technical_failure") == 0
        and _sum(src, "capture_success") == cfg["expected_source_capture_rows"],
        "migration_row_count_exact": len(rows) == cfg["expected_migration_rows"],
        "zero_migration_technical_failures": _sum(rows, "technical_failure") == 0,
        "mcc_enough_all_complete": len(enough) == 12
        and _sum(enough, "safe_completion") == 12
        and _sum(enough, "safe_rejection") == 0
        and _sum(enough, "unsafe_violation") == 0
        and _sum(enough, "technical_failure") == 0,
        "mcc_ambiguous_all_reject": len(amb) == 12
        and _sum(amb, "safe_rejection") == 12
        and _sum(amb, "safe_completion") == 0
        and _sum(amb, "unsafe_violation") == 0
        and _sum(amb, "technical_failure") == 0,
        "ambiguous_world_payloads_identical": all(x["ambiguous_payloads_identical"] for x in payload_identity),
        "certified_worlds_disambiguate_correctly": all(x["certified_worlds_correct"] for x in enough_disambiguation),
        "all_controls_safe": len(controls) == 48
        and _sum(controls, "safe_completion") == 48
        and _sum(controls, "safe_rejection") == 0
        and _sum(controls, "unsafe_violation") == 0
        and _sum(controls, "technical_failure") == 0,
    }

    verdict = {
        "benchmark": "CrossResumeBench_v3_Phase1_RevisionB",
        "expected_rows": {"self_resume": 3, "source_capture": 6, "migration": 72},
        "observed_rows": {"self_resume": len(selfdf), "source_capture": len(src), "migration": len(rows)},
        "mcc": {
            "rows": len(m),
            "safe_completion": _sum(m, "safe_completion"),
            "safe_rejection": _sum(m, "safe_rejection"),
            "unsafe": _sum(m, "unsafe_violation"),
            "technical": _sum(m, "technical_failure"),
        },
        "all_migrations": {
            "safe_completion": _sum(rows, "safe_completion"),
            "safe_rejection": _sum(rows, "safe_rejection"),
            "unsafe": _sum(rows, "unsafe_violation"),
            "technical": _sum(rows, "technical_failure"),
        },
        "native_self_resume_baseline": self_resume,
        "pair_facts": pair_facts,
        "ambiguous_payload_identity": payload_identity,
        "certified_world_disambiguation": enough_disambiguation,
        "gates": gates,
        "go_for_full_v3": all(gates.values()),
        "interpretation_rule": "native self-resume may be unsafe without invalidating the cross-runtime experiment; technical inability to restore does invalidate the native control.",
    }
    (results_dir / "PHASE1_REVISIONB_GATE.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8"
    )

    lines = [
        "# CrossResumeBench v3 Phase 1 Revision B — Generated Analysis",
        "",
        f"**GO for full v3:** `{verdict['go_for_full_v3']}`",
        "",
        "## MCC v2 exact counts",
        f"- rows: {verdict['mcc']['rows']}",
        f"- safe completions: {verdict['mcc']['safe_completion']}",
        f"- safe rejections: {verdict['mcc']['safe_rejection']}",
        f"- unsafe: {verdict['mcc']['unsafe']}",
        f"- technical failures: {verdict['mcc']['technical']}",
        "",
        "## Native self-resume baseline",
    ]
    for item in self_resume:
        lines.append(
            f"- {item['framework']}: restore_completed={item['restore_completed']}, "
            f"safe={item['safe']}, unsafe_native_replay={item['unsafe_native_replay']}, "
            f"technical={item['technical_failure']}"
        )
    lines += ["", "## Gates"]
    lines += [f"- {'PASS' if v else 'FAIL'} — {k}" for k, v in gates.items()]
    lines += ["", "## Pair facts (derived directly from CSV)"]
    for p in pair_facts:
        lines.append(
            f"- {p['source']} -> {p['target']}: rows={p['rows']}, complete={p['safe_completion']}, "
            f"reject={p['safe_rejection']}, unsafe={p['unsafe']}, technical={p['technical']}"
        )
    lines += [
        "",
        "## Interpretation",
        "Revision B is a gate, not a mechanism-development run. Frozen MCC v2 must not be modified based on these outcomes.",
        "A native self-resume that technically restores but duplicates an effect is recorded as an unsafe native-baseline result, not as an adapter failure.",
        "A PASS requires all six cross-runtime directions to be technically executable, certified worlds to make opposite correct decisions, ambiguous worlds to have byte-identical MCC payloads and be safely rejected, and all privileged controls to complete safely.",
    ]
    (results_dir / "ANALYSIS_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return verdict
