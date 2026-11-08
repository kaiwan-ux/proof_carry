# Build validation

Validation performed before packaging:
- Python compilation: PASS.
- Unit tests: 9/9 PASS.
- Frozen MCC hash verification: PASS.
- Frozen suite hash verification: PASS.
- Frozen benchmark/evaluator hash verification: PASS.
- Full semantic pipeline: 660 rows PASS.
- Fake-adapter native pipeline: 504 rows, 504 unique run IDs, 0 technical failures PASS.
- Analysis + verification pipeline: PASS.
- SQLite post-commit-timeout durability test: PASS.

The build environment does not contain LangGraph/CrewAI/Microsoft Agent Framework, so the real native stage was **not** executed during packaging. The delivered main run script requires those packages and will fail preflight if they are unavailable. Validation artifacts were deleted before packaging.
