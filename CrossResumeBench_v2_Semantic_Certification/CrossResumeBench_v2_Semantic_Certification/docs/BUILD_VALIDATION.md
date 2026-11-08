# Build Validation

This package was validated before delivery with **synthetic/fake native adapters only**. These validation outputs are not research evidence and are removed from `results/` before packaging.

Validated:
- Python compilation of source, scripts, tests, and probes
- 9 unit/invariant tests
- MCC v2 JSON-Schema conformance and recursive native-state leak rejection
- meaningful evidence variation across the five hold-out variants
- mechanism-before-suite freeze ordering and hash verification
- 700-row semantic pipeline shape
- 588-row fake-native source→target orchestration shape
- source adapter invocation (source framework is not merely a label)
- independent history/AAIF/CapLease reference modules do not import MCC reconstruction
- analysis pipeline and result verifier
- zero fake-native technical failures

The real LangGraph/CrewAI/MAF runs were **not** executed in the packaging environment because those framework packages are unavailable there. `preflight.py` therefore fails closed on a machine missing any required runtime.
