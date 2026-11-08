# Build Validation — ProofCarry NativeFull

## Completed in the packaging environment

- Python source compilation: PASS
- Unit tests: 7/7 PASS
- Case shape: 120 cases, 8 families, 15 cases/family
- Five evidence conditions present: PASS
- Six directed runtime pairs: PASS
- NativeFull count generator:
  - ProofCarry-only / all120: 3,600 migration rows
  - Core / all120: 14,400 migration rows
  - Full / all120: 36,000 migration rows
  - Plus 24 family gates, 360 self-resume controls, 360 source captures
- Environment doctor fail-closed behavior: PASS

## Native execution status in this packaging environment

Fresh native execution was **not possible here** because `langgraph`, `crewai`, and `agent_framework` were absent. An attempted dependency installation could not reach PyPI because the container had no outbound package-network access.

No native success rows have therefore been fabricated. The generated experiment is designed to run in a clean Python 3.12 environment after `pip install -r requirements.txt`.

The local doctor evidence is retained under `build_validation/current_container_doctor/`.
