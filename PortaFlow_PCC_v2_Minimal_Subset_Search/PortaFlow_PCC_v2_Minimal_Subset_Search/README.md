# PortaFlow PCC v2 — Minimal Subset Search

## Purpose
PCC v1 showed that full framework-neutral continuation semantics can safely complete the tested hold-out migrations, while rich history inference safely rejects ambiguous external commits. It also showed that several PCC fields are individually redundant.

This experiment asks the next question:

> **What is the smallest stored semantic representation that preserves safe cross-runtime continuation on the current hold-out suite?**

It does **not** claim universal mathematical minimality. Minimality is searched only over six declared semantic component families and eight deterministic hold-out workflows.

## Two-stage design

### Stage A — exhaustive semantic search
All 64 subsets of six component families are tested in two regimes:

1. `explicit`: only stored fields may be used.
2. `hybrid`: stored history may be combined with static workflow structure to safely reconstruct missing semantics. Ambiguous critical effects must be rejected unless explicit evidence resolves them.

This creates 64 × 2 × 8 = **1,024 logical mechanism evaluations**. These are representation-search results, not framework-effect claims.

### Stage B — native confirmation
The smallest zero-unsafe, full-coverage candidates found in Stage A are then confirmed across LangGraph, CrewAI, and Microsoft Agent Framework in all six directed source→target pairs. Controls and immediate ablations are included automatically.

## Component vocabulary
- `progress`: completed steps, retry counts, branch decisions, loop counters
- `history`: portable event history
- `frontier`: next/control position
- `obligations`: unresolved approvals/retries/compensations
- `receipts`: certified external-effect commitment/replay facts
- `contract`: joins, dependency and continuation constraints

## Key outputs
- `subset_workflow_results.csv` — all 1,024 Stage-A workflow evaluations
- `subset_summary.csv` — all 128 subset/mode summaries
- `pareto_frontier.csv`
- `minimal_candidates.json`
- `selected_native_conditions.json`
- `native_confirmation.csv`
- `MINIMALITY_VERDICT.json`
- graphs, native artifacts, capsules, manifests and checksums

## Run
Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_minimal_subset.ps1
```

or double-click `run_minimal_subset.bat`.

No LLM/API key is used.
