from __future__ import annotations
import csv, hashlib, itertools, json, traceback
from pathlib import Path
from typing import Any, Callable
from .registry import adapter as default_adapter
from .models import SourceCapture, RunRecord, LogicalState
from .pcc import build_capsule, lower_capsule
from .evaluator import evaluate


def _rid(parts) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:16]


def _json_default(x):
    if hasattr(x, "to_dict"):
        return x.to_dict()
    return str(x)


def run(config: dict[str, Any], root: Path, adapter_getter: Callable[[str], Any] = default_adapter) -> list[RunRecord]:
    res = root / "results"
    for d in ["native_sources", "native_targets", "capsules"]:
        (res / d).mkdir(parents=True, exist_ok=True)

    frameworks = config["frameworks"]
    workflows = config["workflows"]
    conditions = config["conditions"]
    source_cache: dict[tuple[str, str], SourceCapture] = {}
    technical: list[dict[str, Any]] = []

    for src in frameworks:
        for wf in workflows:
            try:
                cap = adapter_getter(src).run_source(wf)
                source_cache[(src, wf)] = cap
                (res / "native_sources" / f"{src}__{wf}.json").write_text(
                    json.dumps(cap.to_dict(), indent=2, default=_json_default), encoding="utf-8"
                )
            except Exception as e:
                technical.append({
                    "stage": "source", "framework": src, "workflow": wf,
                    "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc(),
                })

    records: list[RunRecord] = []
    details: list[dict[str, Any]] = []
    pairs = [p for p in itertools.product(frameworks, frameworks) if p[0] != p[1]]
    for src, tgt in pairs:
        for wf in workflows:
            source = source_cache.get((src, wf))
            for cond in conditions:
                rid = _rid([config["experiment_name"], src, tgt, wf, cond])
                if source is None:
                    records.append(RunRecord(rid, src, tgt, wf, cond, 0, 1, "SOURCE_TECHNICAL_FAILURE", 0, 0, 0, 0, 0, 0, 0, 0, "missing", 0, notes="source capture unavailable"))
                    continue
                source_state = LogicalState.from_dict(source.state)
                ledger = dict(source.external_ledger)
                try:
                    capsule = build_capsule(source, cond)
                    cap_dict = capsule.to_dict()
                    # Anti-cheating assertion: native checkpoint contents must never be embedded in PCC.
                    if "source_native_snapshot" in json.dumps(cap_dict):
                        raise AssertionError("PCC payload illegally contains source_native_snapshot")
                    imported = lower_capsule(capsule)
                    target_state, target_native = adapter_getter(tgt).run_target(wf, imported, ledger)
                    ev = evaluate(source_state, target_state, ledger)
                    rec = RunRecord(
                        rid, src, tgt, wf, cond, int(ev["safe"]), 0, ";".join(ev["failure_types"]),
                        ev["duplicate_effects"], ev["replayed_steps"], int(ev["approval_preserved"]),
                        int(ev["retry_preserved"]), int(ev["branch_preserved"]), int(ev["loop_preserved"]),
                        int(ev["parallel_preserved"]), int(ev["correct_termination"]),
                        source.native_snapshot.get("kind", "unknown"), capsule.byte_size(),
                    )
                    records.append(rec)
                    detail = {
                        "run_id": rid, "source": source.to_dict(), "capsule": cap_dict,
                        "target_framework": tgt, "target_state": target_state.to_dict(),
                        "target_native": target_native, "final_ledger": ledger, "evaluation": ev,
                    }
                    details.append(detail)
                    (res / "native_targets" / f"{rid}.json").write_text(json.dumps(detail, indent=2, default=_json_default), encoding="utf-8")
                    (res / "capsules" / f"{rid}.json").write_text(json.dumps(cap_dict, indent=2), encoding="utf-8")
                except Exception as e:
                    records.append(RunRecord(rid, src, tgt, wf, cond, 0, 1, "TARGET_TECHNICAL_FAILURE", 0, 0, 0, 0, 0, 0, 0, 0, source.native_snapshot.get("kind", "unknown"), 0, notes=f"{type(e).__name__}: {e}"))
                    technical.append({
                        "stage": "target", "source": src, "target": tgt, "workflow": wf, "condition": cond,
                        "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc(),
                    })

    if records:
        with (res / "pcc_ablation_runs.csv").open("w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=list(records[0].to_dict()))
            wr.writeheader(); wr.writerows([r.to_dict() for r in records])
    (res / "technical_failures.json").write_text(json.dumps(technical, indent=2), encoding="utf-8")
    (res / "normalized_pcc_runs.jsonl").write_text(
        "\n".join(json.dumps(x, sort_keys=True, default=_json_default) for x in details) + ("\n" if details else ""),
        encoding="utf-8",
    )
    return records
