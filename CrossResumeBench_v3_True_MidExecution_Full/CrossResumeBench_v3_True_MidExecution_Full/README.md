# CrossResumeBench v3 — True Mid-Execution Full Benchmark

**Status:** publication-strength experimental package, designed after the Revision C Phase-1 PASS.

## Research question
Can frozen MCC v2 safely continue or safely reject genuinely paused cross-runtime executions across multiple continuation families when LangGraph, CrewAI, and Microsoft Agent Framework expose different native checkpoint representations?

## What is frozen
- MCC v2 source, schema, certificate logic and admissibility rules are copied byte-for-byte from the successful Revision C package.
- The 28-case suite and evidence-applicability matrix are generated and SHA-256 frozen before execution.
- If MCC v2 is unsafe on a degraded case, **do not patch MCC v2 and rerun this same suite**. That is a result. A redesigned MCC requires a new version and a fresh holdout.

## Seven continuation families
1. effect commitment / acknowledgement
2. retry after failure
3. approval waiting
4. parallel completion / join
5. loop continuation
6. compensation pending
7. async callback pending

There are 28 base cases (4 per family). Evidence variants are **not** blindly Cartesian: only semantically applicable variants are run. This produces 80 case×variant instances.

## Framework coverage
- LangGraph 1.2.11
- CrewAI 1.15.17
- Microsoft Agent Framework (`agent-framework-core`) 1.15.0
- all 6 directed cross-runtime pairs

## Evaluation grid
- 80 applicable case×variant instances
- 6 directed runtime pairs
- 7 migration methods
- **3,360 migration rows**
- 84 native self-resume controls
- 84 native source captures
- 21 native family pre-gate probes

Migration methods: frozen MCC v2; independent history-only; concept-level AAIF reference; concept-level CapLease reference; AAIF+CapLease reference; explicit-minimal privileged control; oracle privileged control.

## Important methodological boundary
The family micro-workflows are deterministic, framework-native checkpoint/control-flow implementations. They test preservation of continuation semantics, not LLM quality and not every proprietary/built-in retry or orchestration feature of each framework. No API key or LLM is required.

## Run
On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-ExecutionPolicy -Scope Process Bypass
.un_full_v3.ps1
```

If the 21-case native family gate fails, the runner stops and exports `CrossResumeBench_v3_Full_NATIVE_GATE_diagnostics.zip`.
If infrastructure is valid, the full run exports `CrossResumeBench_v3_Full_results.zip` even if MCC fails scientifically.
