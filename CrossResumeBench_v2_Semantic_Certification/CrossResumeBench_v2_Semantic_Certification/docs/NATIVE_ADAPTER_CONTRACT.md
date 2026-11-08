# Native Adapter Contract

Every runtime adapter implements two distinct operations:

1. `capture_source(case)` — invoke the source runtime, persist a framework-specific state/checkpoint envelope, then extract a portable SourceCapture.
2. `run_target(case, continuation, ledger)` — invoke the target runtime using target-side reconstructed continuation.

The native runner first materializes `(source framework, case)` captures and reuses each capture across its two target frameworks. A source-capture failure is a technical failure and cannot be silently replaced by the abstract semantic source.

The deterministic benchmark action semantics are shared across frameworks so that framework behavior—not task meaning—is the variable. Future v3 can compile each action into finer-grained native control structures.

## v2 implementation detail
LangGraph and MAF lower benchmark actions into native graph/executor nodes. CrewAI executes the action sequence inside a native Flow state transition because its decorator graph is static at class definition time in this benchmark implementation. All source actions execute *inside* the selected source runtime; no native runner precomputes `simulate_source()` and then merely labels it with a framework name.
