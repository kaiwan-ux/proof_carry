
from __future__ import annotations

import hashlib
import json
import shutil
import traceback
from pathlib import Path

from .case import case_spec, spec_hash
from .evidence import source_capture_from_native
from .frozen import ROOT, admissibility, build_mcc_v2, reconstruct_mcc_v2
from .ledger import FileLedger
from .models import RunOutcome
from .native import get_runtime

SAFE_LEDGER = {"effect_count": 1, "ack_count": 1, "finish_count": 1}


def _clean(p: Path) -> None:
    p = Path(p)
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)


def _id(*parts) -> str:
    return "crewai-gate-" + "-".join(str(x) for x in parts)


def _sha(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def _decision_for_world(world: str) -> str:
    return "skip_effect" if world == "committed" else "execute_effect"


def run(results_dir: Path, runtime_factory=get_runtime):
    cfg = json.loads((ROOT / "config" / "crewai_gate.json").read_text(encoding="utf-8"))
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    for d in [results_dir/"artifacts", results_dir/"native_sources", results_dir/"native_targets", results_dir/"work"]:
        d.mkdir(parents=True, exist_ok=True)

    c = case_spec()
    wh = spec_hash()
    runtime = runtime_factory("crewai")

    # Native self-resume control.
    self_rows = []
    rid = _id("self", "crewai")
    rdir = results_dir / "work" / rid
    _clean(rdir)
    try:
        out = runtime.self_resume_committed(rdir)
        restore_completed = bool(out.get("restore_completed", True))
        safe = bool(out.get("safe", False)) if restore_completed else False
        technical = int(not restore_completed)
        native_unsafe = int(restore_completed and not safe)
        err = ""
    except Exception:
        restore_completed = False
        safe = False
        technical = 1
        native_unsafe = 0
        err = traceback.format_exc()
        out = {"error": err}
    (results_dir/"artifacts"/f"{rid}.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    self_rows.append({
        "run_id": rid, "framework": "crewai", "case_id": c.case_id, "world": "committed",
        "restore_completed": int(restore_completed), "self_resume_safe": int(safe),
        "native_unsafe_replay": native_unsafe, "technical_failure": technical, "error": err,
    })

    # Native source captures, one for each hidden world.
    source_rows = []
    source_cache = {}
    source_errors = {}
    for world in cfg["worlds"]:
        sid = _id("source", "crewai", world)
        sdir = results_dir / "work" / sid
        _clean(sdir)
        try:
            native = runtime_factory("crewai").capture_effect_pause(sdir, world)
            source_cache[world] = native
            source_rows.append({
                "source_id": sid, "framework": "crewai", "world": world,
                "capture_success": 1, "technical_failure": 0,
                "checkpoint_ref": native.checkpoint_ref, "native_kind": native.native_kind,
                "source_effect_count": native.source_ledger["effect_count"],
                "source_ack_count": native.source_ledger["ack_count"],
                "source_finish_count": native.source_ledger["finish_count"],
                "pending_work": json.dumps(native.pending_work), "error": "",
            })
            (results_dir/"native_sources"/f"{sid}.json").write_text(
                json.dumps(native.to_dict(), indent=2, default=str), encoding="utf-8")
        except Exception:
            err = traceback.format_exc()
            source_errors[world] = err
            source_rows.append({
                "source_id": sid, "framework": "crewai", "world": world,
                "capture_success": 0, "technical_failure": 1,
                "checkpoint_ref": "", "native_kind": "", "source_effect_count": "",
                "source_ack_count": "", "source_finish_count": "", "pending_work": "", "error": err,
            })
            (results_dir/"native_sources"/f"{sid}.json").write_text(json.dumps({"error": err}, indent=2), encoding="utf-8")

    # Focused CrewAI -> CrewAI matrix: 2 worlds x 2 evidence variants x 3 methods = 12 rows.
    rows = []
    for world in cfg["worlds"]:
        for variant in cfg["evidence_variants"]:
            for method in cfg["migration_methods"]:
                rid = _id("crewai", "to", "crewai", world, variant, method)
                tdir = results_dir / "work" / rid
                _clean(tdir)
                expected_decision = _decision_for_world(world)

                if world in source_errors:
                    row = RunOutcome(
                        rid, "crewai", "crewai", c.case_id, world, variant, method,
                        technical_failure=1, failure_types=["SOURCE_CAPTURE_FAILURE"],
                        expected_effect_decision=expected_decision,
                        artifact={"traceback": source_errors[world]},
                    )
                    rows.append(row.to_dict())
                    (results_dir/"artifacts"/f"{rid}.json").write_text(json.dumps(row.to_dict(), indent=2, default=str), encoding="utf-8")
                    continue

                try:
                    native = source_cache[world]
                    capture = source_capture_from_native(native, variant)
                    FileLedger(tdir / "ledger.json").write(native.source_ledger)

                    if method == "mcc_v2":
                        pkg = build_mcc_v2(capture, "crewai", wh, ROOT / "frozen_v2")
                        ph = _sha(pkg.payload)
                        rc, report = reconstruct_mcc_v2(pkg.payload, c, ROOT / "frozen_v2")
                        accepted, reason = admissibility(rc)

                        if not accepted:
                            row = RunOutcome(
                                rid, "crewai", "crewai", c.case_id, world, variant, method,
                                safe_rejection=1, reject_reason=reason,
                                payload_bytes=pkg.byte_size(), payload_sha256=ph,
                                expected_effect_decision=expected_decision,
                                artifact={"payload": pkg.payload, "inference": report},
                            )
                        else:
                            fact = rc.effect_facts.get("effect", {}).get("status")
                            if fact not in {"committed", "not_committed"}:
                                row = RunOutcome(
                                    rid, "crewai", "crewai", c.case_id, world, variant, method,
                                    unsafe_violation=1, failure_types=["ACCEPTED_WITHOUT_EFFECT_DECISION"],
                                    payload_bytes=pkg.byte_size(), payload_sha256=ph,
                                    expected_effect_decision=expected_decision,
                                    artifact={"payload": pkg.payload, "inference": report},
                                )
                            else:
                                out = runtime_factory("crewai").run_from_effect_decision(fact, tdir)
                                actual = out.get("effect_decision", "")
                                safe = out["ledger"] == SAFE_LEDGER and actual == expected_decision
                                row = RunOutcome(
                                    rid, "crewai", "crewai", c.case_id, world, variant, method,
                                    safe_completion=int(safe), unsafe_violation=int(not safe),
                                    failure_types=[] if safe else ["LEDGER_OR_EFFECT_DECISION_MISMATCH"],
                                    payload_bytes=pkg.byte_size(), payload_sha256=ph,
                                    expected_effect_decision=expected_decision,
                                    actual_effect_decision=actual,
                                    artifact={"payload": pkg.payload, "inference": report, "target": out},
                                )
                    else:
                        # Privileged controls receive evaluator-only world truth.
                        out = runtime_factory("crewai").run_from_effect_decision(world, tdir)
                        actual = out.get("effect_decision", "")
                        safe = out["ledger"] == SAFE_LEDGER and actual == expected_decision
                        row = RunOutcome(
                            rid, "crewai", "crewai", c.case_id, world, variant, method,
                            safe_completion=int(safe), unsafe_violation=int(not safe),
                            failure_types=[] if safe else ["CONTROL_FAILED"],
                            expected_effect_decision=expected_decision,
                            actual_effect_decision=actual,
                            artifact={"target": out, "control": "privileged_truth", "world": world},
                        )

                    rows.append(row.to_dict())
                    (results_dir/"artifacts"/f"{rid}.json").write_text(json.dumps(row.to_dict(), indent=2, default=str), encoding="utf-8")
                    if row.artifact and "target" in row.artifact:
                        (results_dir/"native_targets"/f"{rid}.json").write_text(
                            json.dumps(row.artifact["target"], indent=2, default=str), encoding="utf-8")
                except Exception:
                    row = RunOutcome(
                        rid, "crewai", "crewai", c.case_id, world, variant, method,
                        technical_failure=1, failure_types=["TARGET_OR_TRANSLATION_FAILURE"],
                        expected_effect_decision=expected_decision,
                        artifact={"traceback": traceback.format_exc()},
                    )
                    rows.append(row.to_dict())
                    (results_dir/"artifacts"/f"{rid}.json").write_text(json.dumps(row.to_dict(), indent=2, default=str), encoding="utf-8")

    import pandas as pd
    pd.DataFrame(self_rows).to_csv(results_dir/"self_resume.csv", index=False)
    pd.DataFrame(source_rows).to_csv(results_dir/"source_capture_results.csv", index=False)
    pd.DataFrame(rows).to_csv(results_dir/"crewai_gate_runs.csv", index=False)
    return self_rows, source_rows, rows
