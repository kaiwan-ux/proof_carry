# Proposal-ready description of the next experiment

Our earlier PCC v0 ablation showed that explicit continuation semantics could eliminate controlled failures, but the benchmark was intentionally aligned with individual PCC components. The next experiment therefore attacks two threats to validity: benchmark overfitting and representational over-specification.

We evaluate PCC v1 on eight previously unseen workflows that combine multiple continuation hazards such as branching with committed effects and pending approval, loop progress with external effects, partial parallel execution with retry state, saga compensation, and uncertain external commits. Each workflow is executed through all six directed migration pairs among LangGraph, CrewAI, and Microsoft Agent Framework.

The key baseline is not a deliberately weakened history representation. It receives the benchmark's non-redacted framework-neutral event history plus the static workflow structure and uses a reconstruction algorithm to infer retry progress, branch decisions, loop position, pending approvals/retries, effect commitments when explicitly observable, and join/dependency structure. When an external commit is fundamentally ambiguous, the inference baseline may conservatively reject migration rather than guess.

Full PCC is compared with state-only, raw-history, history-inference, and leave-one-component-out PCC variants. Leave-one-out variants are allowed to reconstruct omitted semantics from history, so a component is only supported as explicitly useful when reconstruction cannot safely replace it.

The experiment therefore asks a stronger question than whether PCC can work: **which semantics actually need explicit portable representation, which can be reconstructed, and where explicit semantics increase safe continuation coverage over conservative inference?**
