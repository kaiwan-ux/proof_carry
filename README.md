# ProofCarry

Research artifacts for **ProofCarry: Closed-World Proof Contracts for Cross-Runtime Agent Continuation**.

ProofCarry checks portable evidence against a target-defined continuation contract. Continuation is admitted only when every declared continuation-critical obligation has an admissible, consistent proof. Missing or conflicting evidence causes rejection.

## Paper experiments: reading and presentation order

Most top-level packages contain an inner directory with the same name. Evidence paths below are relative to the inner package directory.

| Order | Experiment | Top-level folder | Evidence |
| --- | --- | --- | --- |
| 1 | Sealed 32-case holdout | [Closed-world holdout](CrossResumeBench_MCCv3_ClosedWorld_Holdout/) | `results/migration_runs.csv` |
| 2 | Paired holdout statistics | [Post-validation](CrossResumeBench_MCCv3_PostValidation_Studies/) | `results/statistics/` |
| 3 | Expanded 104-case semantic study | [ProofCarry 104](CrossResumeBench_ProofCarry_104/) | `results/semantic_runs.csv` |
| 4 | Expanded ablation | [ProofCarry 104](CrossResumeBench_ProofCarry_104/) | `results/ablation_runs.csv` |
| 5 | Authenticated security | [ProofCarry 104](CrossResumeBench_ProofCarry_104/) | `results/security_runs.csv` |
| 6 | Native-family re-check | [ProofCarry 104](CrossResumeBench_ProofCarry_104/) | `results/native_family_gate.csv` |
| 7 | Mechanism overhead | [Post-validation](CrossResumeBench_MCCv3_PostValidation_Studies/) | `results/performance_micro/` |

Supporting packages:

- `CrossResumeBench_MCCv3_Holdout_InfraFixA`: holdout infrastructure corrections and native-runtime diagnostics.
- `CrossResumeBench_MCCv3_Security_PaperFigures`: earlier security studies, publication figures, and figure source data. Match each figure to its experiment; the expanded security matrix comes from ProofCarry 104.

## Paper results

The following headline counts were checked against the local raw CSV files when preparing this repository.

| Study | Observed results |
| --- | --- |
| Holdout | 6,144 rows across eight methods. ProofCarry (`mcc_v3`): 486 safe completions, 282 safe rejections, 0 unsafe and 0 technical outcomes in 768 conditions. |
| Expanded semantic | 31,200 rows across ten methods. ProofCarry: 1,872 safe completions, 1,248 safe rejections, 0 unsafe and 0 technical outcomes in 3,120 conditions. |
| Expanded ablation | 17,472 total rows. Removing the closed-world gate introduces 768 unsafe outcomes in 2,496 conditions. |
| Expanded security | 11,232 rows across two methods. ProofCarry completes 624 valid controls and rejects 4,992 attack rows; the unkeyed-hash control has 3,744 unsafe rows. |
| Native-family re-check | LangGraph: 8/8; Microsoft Agent Framework: 8/8; CrewAI: 0/8. |

These are controlled benchmark observations, not unconditional safety guarantees. Semantic runtime-pair matrices do not establish universal native checkpoint interoperability. Expanded rows from the same base case are not independent samples. Authentication establishes provenance/context under trust assumptions; it does not independently prove evidence truth or contract completeness.

## Earlier CrossResumeBench research

These packages preserve development history and are not interchangeable with the final paper datasets:

| Folder | Purpose |
| --- | --- |
| `CrossResumeBench_v1_Publication` | Prototype benchmark. |
| `CrossResumeBench_v2_Semantic_Certification` | MCC v2 baseline development and certification. |
| `CrossResumeBench_v3_True_MidExecution_Migration` | Initial design and roadmap. |
| `CrossResumeBench_v3_Corrected_Phase1` | Corrected phase-1 design and native validation. |
| `CrossResumeBench_v3_Phase1_RevisionA` | Phase-1 revision and diagnostics. |
| `CrossResumeBench_v3_Phase1_RevisionB` | Native-runtime corrections. |
| `CrossResumeBench_v3_Phase1_RevisionC` | Later phase-1 revision and frozen-baseline material. |
| `CrossResumeBench_v3_CrewAI_Repaired_Gate` | CrewAI checkpoint/resume repair experiments. |
| `CrossResumeBench_v3_True_MidExecution_Full` | Full mid-execution discovery experiments. |

This is a development reading order, not a timestamp-verified execution chronology. Preserve failed and technical outcomes as research evidence.

## Related PortaFlow studies

These investigate the same continuation problem and runtimes. Their exact contribution to the supplied paper's lineage is unconfirmed; they are related background, not sources for its headline tables.

1. `PortaFlow_Phase0_Experiment`: problem-existence study.
2. `PortaFlow_Phase0_Corrected_Native`: corrected native study.
3. `PortaFlow_PCC_v0_Ablation`: Portable Continuation Capsule components.
4. `PortaFlow_PCC_v1_Generalization_Minimality (1)`: generalization and history reconstruction.
5. `PortaFlow_PCC_v2_Minimal_Subset_Search`: component subset search.
6. `PortaFlow_PCC_v3_True_Heldout_Generalization`: frozen representations on new workflows.
7. `PortaFlow_PCC_v4_Robustness_Stress`: noisy, missing, reordered, and conflicting evidence.

## Separate ProofCarry extensions

| Folder | Purpose |
| --- | --- |
| `ProofCarry_Final_Experimental_120` | Separate 120-case semantic extension and preserved legacy evidence. The paper's expanded study has 104 cases. |
| `ProofCarry_NativeFull_Experiment (1)` | Additional native execution experiments and diagnostics. |
| `ProofCarry_NativeFull_Experiment_CrewAI_Fixed` | CrewAI fixes and further native runs. |

Keep these results separate from the paper's semantic matrices and reported native re-check.

## Reproduction

There is no shared root runner for all packages. Open the selected inner package and follow its own `README.md`, requirements, `RESEARCH_PROTOCOL.md`, and `QUICKSTART_WINDOWS.md` where provided.

1. Create a fresh Python environment appropriate to that package; several native experiments require Python 3.12.
2. Install the selected package's pinned dependencies.
3. Run its documented preflight and verification commands before its experiment runner.
4. Preserve frozen mechanisms, sealed suites, and original raw runs. Write new runs separately.

Installed environments, dependencies, caches, credentials, and machine-local `.env` files are excluded. Example environment files are templates. Deterministic experiments often require no API key; optional model-based extensions may require credentials. Follow each package's instructions.

### Oversized result CSVs

Two `expanded120.csv` files exceed GitHub's regular-file size limit. Their complete contents are uploaded as lossless `expanded120.csv.gz` files alongside their original locations. The original CSV files remain locally and are ignored by Git.

After cloning, restore them before running consumers that expect CSV:

```bash
python tools/restore_large_results.py
```

The script verifies an existing CSV against the compressed data and refuses to overwrite different content.

## Scope and licensing

All 24 top-level research folders are represented, including scientific code, raw results, configurations, diagnostics, and package documentation, subject to the exclusions and lossless compression above. The paper PDF was supplied separately and is not copied automatically from outside this workspace.

Repository preparation did not rerun the experiments or independently validate every historical claim. No new project-wide license is asserted. Review existing package licenses and third-party notices before reuse.
