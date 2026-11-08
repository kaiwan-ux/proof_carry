# Package Validation Report

Completed before delivery:

- Python source compilation: PASS
- frozen MCC v2 SHA-256 verification: PASS
- experiment suite/applicability/evaluation freeze verification: PASS
- structural/unit tests: 6/6 PASS
- synthetic full orchestration: PASS
  - 84 self-resume rows
  - 84 source-capture rows
  - 3,360 migration rows
  - 0 synthetic technical failures
  - frozen MCC enough-evidence: 168/168 safe completions
- evidence applicability count: 80 case×variant instances
- expected MCC rows: 480
- expected full migration rows: 3,360

The synthetic run uses fake runtimes only to validate orchestration, row accounting, evidence generation, lowering, target planning, evaluation, and analysis. It is **not scientific evidence**. Real LangGraph/CrewAI/MAF execution must occur on the user's pinned environment. Degraded evidence cases are intentionally capable of falsifying frozen MCC v2.
