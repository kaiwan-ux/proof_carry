# Benchmark Card

**Name:** CrossResumeBench v2 — Semantic Certification

**Purpose:** Falsify or support Minimal Certified Cross-Runtime Continuation after the v1 semantic-completion failure.

**Suite:** 70 deterministic cases, 14 new families, 5 variants/family.

**Native:** LangGraph, CrewAI, Microsoft Agent Framework; source adapter is invoked before target adapter for every directed pair.

**Proposed mechanism:** MCC v2 = application state + portable history + typed semantic certificates + target-side reconstruction + reject-on-unknown.

**Not claimed:** universal migration, direct checkpoint-format interchange, official AAIF/CapLease comparison, stochastic LLM behavior.
