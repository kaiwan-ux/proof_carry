from __future__ import annotations

import csv
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from .baselines import export_capsule, import_capsule
from .evaluator import evaluate, count_replayed, count_skipped
from .models import RunRecord
from .workflows import run_prefix, resume_from_state, restart, spec


def stable_run_id(parts: list[Any]) -> str:
    raw = "|".join(map(str, parts)).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def run_matrix(config: dict[str, Any], root: Path) -> list[RunRecord]:
    results_dir = root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    raw_path = results_dir / "raw_runs.csv"
    trace_path = results_dir / "normalized_traces.jsonl"

    frameworks = config["frameworks"]
    pairs = list(itertools.product(frameworks, frameworks)) if config.get("include_same_runtime_pairs", True) else [p for p in itertools.product(frameworks, frameworks) if p[0] != p[1]]

    records: list[RunRecord] = []
    with trace_path.open("w", encoding="utf-8") as tf:
        for source, target in pairs:
            for workflow in config["workflows"]:
                for condition in config["conditions"]:
                    for variant in config["scenario_variants"]:
                        rid = stable_run_id([config["experiment_name"], source, target, workflow, condition, variant])
                        try:
                            prefix = run_prefix(workflow, variant)
                            capsule = export_capsule(prefix, condition)
                            if condition == "restart":
                                target_final = restart(workflow, variant)
                            else:
                                imported = import_capsule(capsule)
                                target_final = resume_from_state(imported)

                            # Evaluate the whole logical execution (source prefix + target suffix).
                            # Conditions that carry history/full semantics already include the prefix;
                            # naive/restart conditions do not, so combine them explicitly for audit.
                            if condition in {"naive_state", "restart"}:
                                final = target_final.clone()
                                final.completed = list(prefix.completed) + list(target_final.completed)
                                final.trace = list(prefix.trace) + list(target_final.trace)
                                merged_effects = dict(prefix.effects)
                                for k, v in target_final.effects.items():
                                    merged_effects[k] = merged_effects.get(k, 0) + v
                                final.effects = merged_effects
                            elif condition == "state_history":
                                # History carries prior logical events, but not privileged external
                                # commit ground truth. Audit the real source effect plus target effects.
                                final = target_final.clone()
                                merged_effects = dict(prefix.effects)
                                for k, v in target_final.effects.items():
                                    merged_effects[k] = merged_effects.get(k, 0) + v
                                final.effects = merged_effects
                            else:
                                final = target_final

                            ev = evaluate(prefix, final)
                            duplicate_effects = max(0, final.effects.get("mock_payment", 0) - 1)
                            replayed = count_replayed(prefix, final)
                            skipped = count_skipped(final)
                            rec = RunRecord(
                                run_id=rid,
                                evidence_tier="controlled_model",
                                source_framework=source,
                                target_framework=target,
                                workflow=workflow,
                                condition=condition,
                                variant=variant,
                                safe_continuation=int(ev.safe),
                                technical_failure=0,
                                failure_types=";".join(ev.failure_types),
                                invariant_results=json.dumps(ev.invariant_results, sort_keys=True),
                                source_boundary=spec(workflow).boundary,
                                final_outcome=final.outcome or "",
                                duplicate_effects=duplicate_effects,
                                replayed_steps=replayed,
                                skipped_required_steps=skipped,
                                approval_preserved=int(ev.invariant_results.get("approval_preserved", True)),
                                retry_preserved=int(ev.invariant_results.get("retry_preserved", True)),
                                correct_termination=int(ev.invariant_results.get("correct_termination", False)),
                                notes=";".join(ev.notes),
                            )
                            records.append(rec)
                            tf.write(json.dumps({
                                "run_id": rid,
                                "source": source,
                                "target": target,
                                "workflow": workflow,
                                "condition": condition,
                                "variant": variant,
                                "capsule": capsule.to_dict(),
                                "prefix": prefix.to_dict(),
                                "final": final.to_dict(),
                                "evaluation": {
                                    "safe": ev.safe,
                                    "failure_types": ev.failure_types,
                                    "invariants": ev.invariant_results,
                                },
                            }, sort_keys=True) + "\n")
                        except Exception as e:
                            records.append(RunRecord(
                                run_id=rid, evidence_tier="controlled_model", source_framework=source, target_framework=target,
                                workflow=workflow, condition=condition, variant=variant, safe_continuation=0,
                                technical_failure=1, failure_types="TECHNICAL_FAILURE", invariant_results="{}",
                                source_boundary=spec(workflow).boundary, final_outcome="", duplicate_effects=0,
                                replayed_steps=0, skipped_required_steps=0, approval_preserved=0, retry_preserved=0,
                                correct_termination=0, notes=f"{type(e).__name__}: {e}",
                            ))

    if records:
        with raw_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(records[0].to_dict().keys()))
            w.writeheader()
            w.writerows([r.to_dict() for r in records])
    return records
