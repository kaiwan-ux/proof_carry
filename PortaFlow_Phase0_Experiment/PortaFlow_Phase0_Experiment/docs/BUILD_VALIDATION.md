# Build Validation

The package was validated before delivery as follows:

- Python source compiled successfully with `compileall`.
- 6/6 core unit tests passed.
- The controlled experiment pipeline completed a full 1,080-record matrix during build validation.
- CSV, JSONL, Markdown report, graph and checksum generation completed successfully.
- Generated validation outputs were removed before delivery so the user's `results/` directory begins clean.

## Native probe limitation during package construction

The build container could not install the external framework packages because outbound package installation was unavailable. Therefore the LangGraph, CrewAI and Microsoft Agent Framework native probe scripts were syntax-validated and designed against the current official documentation, but they were not falsely marked as executed native evidence in the delivered package.

`run_native_probes.py` is intentionally fault-tolerant: if a framework has changed API shape by the time the user runs it, the full error is stored as a technical failure and the other probes continue.
