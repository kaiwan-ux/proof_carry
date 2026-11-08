# Why This Corrects the Previous Experiment

1. **Real frameworks execute the cases.** Source prefixes and target continuations are run through LangGraph, CrewAI, or Microsoft Agent Framework adapters. Framework names are no longer labels on one abstract executor.
2. **Only cross-framework pairs are primary.** The core is 6 directed source→target pairs × 3 workflows = 18 cases.
3. **No pseudo-replication.** Five cosmetic variants were removed. Phase-0 reports designed-case counts, not confidence intervals pretending deterministic duplicates are independent samples.
4. **Technical failures are separate.** A broken framework adapter is never counted as a semantic migration failure.
5. **MAF is corrected.** The package uses `agent-framework-core` and documented checkpoint hooks; the old `ctx.set_executor_state(...)` call is removed.
6. **UTF-8 is forced on Windows.** This avoids the CrewAI console encoding warnings seen in the earlier run.
7. **The diagnostic upper bound is clearly labeled.** `native_semantic` is not PortaFlow/PCC and cannot be claimed as the proposed research mechanism.
8. **The old abstract model is not used as proposal evidence.** It can remain conceptual background only.
