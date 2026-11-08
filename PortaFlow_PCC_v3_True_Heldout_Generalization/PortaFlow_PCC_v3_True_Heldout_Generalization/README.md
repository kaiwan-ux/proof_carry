# PortaFlow PCC v3 — True Held-out Generalization + Optional GPT-OSS-120B Stress Test

This experiment **freezes** the two minimal candidates discovered in PCC v2 *before* evaluating a completely new workflow suite.

## Frozen candidates

- **Hybrid minimum:** semantic history + certified effect receipts, with generic reconstruction from the portable static workflow specification.
- **Explicit minimum:** control frontier + pending obligations + certified effect receipts + continuation contract.

The candidates must not be changed after viewing v3 results and still be called hold-out generalization.

## Stage A — required, deterministic, native

Runs 10 new workflows × 6 directed framework pairs × 8 frozen conditions = **480 native target executions** across LangGraph, CrewAI, and Microsoft Agent Framework.

The reconstruction engine is generic: it parses a common event vocabulary and declarative static workflow specs. It contains no workflow-name-specific inference rules.

## Stage B — optional LLM stress

After Stage A, copy `.env.example` to `.env`, add `GROQ_API_KEY`, and run `run_llm_stage.ps1`. It uses `openai/gpt-oss-120b` to choose continuation actions from the imported semantics. This stage tests representation usefulness under model reasoning; it is **not** a pure framework-effect experiment.

## Run

Windows:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.un_true_holdout.ps1
```

Then upload `PortaFlow_PCC_v3_true_holdout_results.zip` for analysis.
