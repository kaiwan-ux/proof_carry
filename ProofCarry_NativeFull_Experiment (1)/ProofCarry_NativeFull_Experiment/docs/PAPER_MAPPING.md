# Paper Mapping

| Paper claim | Experiment artifact |
|---|---|
| ProofCarry is not equivalent to reject-all | `semantic_runs.csv`: ProofCarry vs `always_reject` |
| Closed-world proof is safety-critical | `ablation_runs.csv`: full vs `minus_closed_world_gate` |
| Cross-runtime semantic identities matter | `semantic_runs.csv`: binding complete vs missing |
| Authenticated context binding blocks attacks | `security_runs.csv` |
| Mechanism overhead is small/large (whatever data shows) | `performance_runs.csv` |
| Evidence is more compact than available native artifacts (only if measured) | `performance_runs.csv` payload/native artifact columns |
| 3-runtime applicability | `native_family_gate.csv`, `native_self_resume.csv`, `native_source_captures.csv`, `native_runs.csv` |

Do not claim any row until the corresponding artifact exists and passes verification.
