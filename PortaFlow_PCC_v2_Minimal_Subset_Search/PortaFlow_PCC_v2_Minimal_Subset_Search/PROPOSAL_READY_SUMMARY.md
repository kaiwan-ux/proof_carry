# Proposal-ready description

After PCC v1 demonstrated safe continuation on unseen composite workflows, leave-one-out analysis showed substantial redundancy: several semantic families could be removed individually without loss, while effect receipts remained important. The next experiment therefore performs an exhaustive minimal-subset search rather than adding more fields.

We enumerate all 64 subsets of six framework-neutral semantic families—progress, history, control frontier, pending obligations, effect receipts, and continuation contracts—and evaluate each under explicit-only and history-reconstruction regimes on eight hold-out workflows. A conservative inference algorithm may reject migration when a critical continuation fact cannot be proven. The smallest full-coverage, zero-unsafe candidate from each regime is then validated on real LangGraph, CrewAI, and Microsoft Agent Framework executions across all six directed runtime pairs.

The experiment is designed to discover whether PortaFlow should remain a broad PCC or collapse into a smaller **Minimal Certified Continuation** representation that stores only non-reconstructable facts while deriving the rest safely.
