# Claim Boundaries

## Claims allowed if supported by generated results

- Selected stateful workflows require semantic information beyond ordinary application variables for safe continuation across the tested runtimes.
- Specific PCC components improve hard-invariant preservation for specific workflow classes.
- Full PCC v0 improves SCR over tested baselines if the actual result shows this.
- Effect receipts reduce duplicate side-effect failures if the actual side-effect rows show this.

## Claims NOT allowed

Do not claim:

- universal cross-framework migration;
- arbitrary mid-instruction migration;
- that a raw LangGraph checkpoint can be directly deserialized by CrewAI or MAF;
- that all agent frameworks have identical semantics;
- that PCC is minimal until the ablation supports minimality;
- that PCC is state of the art before external baselines/literature comparison;
- that 216 deterministic rows are 216 independent statistical samples;
- that GPT-OSS-120B was evaluated in this experiment;
- that framework-native checkpoint blobs are part of PCC.

## Best proposal wording

"We evaluate a framework-neutral semantic continuation representation at declared safe boundaries across LangGraph, CrewAI and Microsoft Agent Framework. The experiment measures which continuation categories are sufficient to preserve hard behavioral invariants, rather than claiming binary/native checkpoint compatibility."
