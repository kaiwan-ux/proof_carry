# CrossResumeBench v3 - True Mid-Execution Native Migration

**Research Question**: Can frozen MCC v2 safely translate genuinely paused in-flight executions between frameworks that represent execution state differently?

## Overview

CrossResumeBench v3 tests **real mid-execution checkpoint migration** across LangGraph, CrewAI, and MAF. Unlike v2's semantic certification, v3 extracts actual native runtime state from paused workflows and attempts cross-framework resumption.

### Key Differences from v2

| Aspect | v2 (Semantic) | v3 (True Mid-Execution) |
|--------|---------------|-------------------------|
| **State Source** | Benchmark-defined semantic state | Real framework internal state |
| **Pause Points** | Semantic boundaries | Mid-retry, mid-loop, callback pending |
| **Extraction** | Synthetic source adapters | Native framework state extractors |
| **Resumption** | Target semantic reconstruction | Target framework's own control flow |
| **MCC v2** | Tested during development | **FROZEN - no modifications** |
| **Goal** | Validate semantic approach | Validate real-world applicability |

## Quick Start

### Prerequisites
```bash
# Python 3.10+
pip install -r requirements.txt
```

### Run Full Benchmark
```bash
# All 6,720 tests (28 cases × 5 variants × 6 pairs × 8 baselines)
python scripts/run_v3_benchmark.py

# Results in: results/v3_runs.csv
# Artifacts in: results/artifacts/
```

### Run Single Framework Pair
```bash
# Just LangGraph → CrewAI
python scripts/run_v3_benchmark.py --source langgraph --target crewai

# ~1,120 tests (28 cases × 5 variants × 8 baselines)
```

### Run Single Test Family
```bash
# Just retry pause points
python scripts/run_v3_benchmark.py --family retry_pause_points

# ~960 tests (4 cases × 5 variants × 6 pairs × 8 baselines)
```

## Test Families

### 1. Retry Pause Points (4 cases)
Real workflows paused during retry logic:
- After Nth failure, before (N+1)th attempt
- During exponential backoff delay
- At max_retries boundary

### 2. Approval Wait Points (4 cases)
Human-in-loop approval pending:
- Approval request pending
- Approval with context data
- After effect, before approval check

### 3. Parallel Branch Points (4 cases)
Parallel execution incomplete:
- One branch done, others pending
- All branches done, join not executed
- Branch with uncommitted effect

### 4. Effect Acknowledgment Points (4 cases)
External effect committed, ack pending:
- Effect committed, not yet acknowledged
- Multiple effects, partial acknowledgment
- Effect commit, callback pending

### 5. Loop Iteration Points (4 cases)
Loop paused between iterations:
- After iteration N, before N+1
- Loop with partial accumulated result
- Break condition met, exit not executed

### 6. Compensation Pending Points (4 cases)
Error detected, compensation not executed:
- Error caught, rollback queued
- Partial compensation (step 1 done, step 2 pending)
- Compensation with nested scope

### 7. Async Callback Points (4 cases)
Async operation in-flight:
- Tool call pending result
- Webhook callback pending
- Async subtask completion pending

**Total**: 28 base cases

## Evidence Variants

Each case tested with 5 evidence difficulty levels:

1. **Enough Evidence**: Certificate has sufficient info for safe resumption
2. **Missing Semantic Completion**: Boundary markers unclear
3. **Ambiguous External Commit**: External effect commit state unclear
4. **Partially Observable Progress**: Critical state hidden/derived
5. **Conflicting Granularity**: Source/target represent state differently

**Expected**: MCC v2 safe completion on (1), safe rejection on (2-5) when unsafe

## Framework Pairs

All 6 bidirectional pairs tested:

1. LangGraph → CrewAI
2. LangGraph → MAF
3. CrewAI → LangGraph
4. CrewAI → MAF
5. MAF → LangGraph
6. MAF → CrewAI

## Baselines

### Frozen Baseline (Under Test)
- **mcc_v2** - Frozen from v2, no modifications allowed

### Control Baselines
- **oracle** - Perfect translation with full framework knowledge
- **explicit_minimal** - Only explicitly marked safe boundaries
- **framework_native_checkpoint** - Framework's own checkpoint (no translation)

### Independent Baselines
- **history_inference** - Infer from execution history alone
- **aaif_reference** - AAIF-inspired implementation
- **caplease_reference** - CapLease-inspired implementation
- **aaif_plus_caplease_reference** - Combination approach

## Success Metrics

### Primary Metrics
- **SCC** (Safe Completion Count): Successful safe continuations
- **Safe Rejection Count**: Correctly refused ambiguous states
- **Unsafe Violation Count**: Incorrect/unsafe continuations (MUST BE 0)
- **Technical Failure Count**: Translation infrastructure errors

### v3-Specific Metrics
- **Native State Capture Success Rate**: % pause points successfully extracted
- **Native Resume Success Rate**: % translations target could resume
- **Cross-Framework Consistency**: Outcome variance across framework pairs
- **Evidence Variant Degradation**: Performance curve from "enough" → "conflicting"

## Kill Criteria

Benchmark fails if ANY of these occur:

1. **MCC v2 shows unsafe violations** on "enough_evidence" variant
2. **Framework native checkpoint fails** to resume its own paused state
3. **MCC v2 achieves 0% SCC** (all rejections, no useful completions)
4. **MCC v2 statistically tied** with aaif_plus_caplease_reference
5. **>50% outcome variance** across framework pairs for same semantic case

## Architecture

### Native State Extraction
```python
# Real framework state → MCC v2 schema
source_state = extract_langgraph_state(paused_workflow)
# Returns: {checkpoint, metadata, pending_nodes, retry_state, ...}

mcc_payload = translate_to_mcc_v2(source_state)
# Only: app_state + history + certificates (frozen schema)
```

### Native Resumption
```python
# MCC v2 schema → Target framework resumption
target_state = translate_from_mcc_v2(mcc_payload)
# Reconstruct target framework's internal state

result = resume_crewai_workflow(target_state)
# Use CrewAI's own control flow (not shared continuation)
```

### Validation
```python
# Compare actual vs oracle expected behavior
oracle_action = get_oracle_next_action(case)
actual_action = get_actual_next_action(result)

if actual_action != oracle_action:
    if is_unsafe(actual_action, case):
        mark_unsafe_violation()
    else:
        mark_safe_rejection()  # Conservative correct
```

## Results Structure

### v3_runs.csv
```csv
run_id,source_framework,target_framework,case_id,family,evidence_variant,
baseline,safe_completion,safe_rejection,unsafe_violation,technical_failure,
native_extraction_success,native_resume_success,pause_point,
expected_next_action,actual_next_action,payload_bytes,reject_reason
```

### RESEARCH_VERDICT.json
```json
{
  "benchmark": "CrossResumeBench v3",
  "mcc_v2_frozen": true,
  "total_tests": 6720,
  "kill_criteria_passed": true,
  "mcc_v2_results": {
    "enough_evidence": {
      "scc": 0.X,
      "unsafe_violations": 0,
      "safe_rejections": Y
    },
    "cross_framework_consistency": 0.XX,
    "evidence_degradation_curve": [...]
  },
  "baseline_comparison": {...},
  "publication_ready": true/false
}
```

## File Structure

```
CrossResumeBench_v3_True_MidExecution_Migration/
├── README.md (this file)
├── DESIGN_SPEC.md (detailed design)
├── pyproject.toml
├── requirements.txt
├── config/
│   └── benchmark.json
├── benchmark/
│   ├── cases/ (28 test cases)
│   ├── native_extractors/ (LangGraph/CrewAI/MAF)
│   ├── native_resumers/ (LangGraph/CrewAI/MAF)
│   └── generated_suite.json
├── baselines/
│   ├── mcc_v2_frozen.py ⚠️ NO MODIFICATIONS
│   └── [7 other baselines]
├── workflows/
│   ├── langgraph/ (28 real workflows)
│   ├── crewai/ (28 real workflows)
│   └── maf/ (28 real workflows)
├── scripts/
│   ├── run_v3_benchmark.py
│   ├── analyze_v3_results.py
│   └── verify_v3_results.py
└── results/
    ├── v3_runs.csv
    ├── RESEARCH_VERDICT.json
    └── artifacts/
```

## Development Roadmap

### Phase 1: Infrastructure ⏳ Current
- [ ] Native state extractors
- [ ] Native resume handlers
- [ ] Frozen MCC v2 translator
- [ ] Validation with 1-2 simple cases

### Phase 2: Test Cases
- [ ] Implement 28 base cases
- [ ] Create 84 real workflows (3 frameworks × 28)
- [ ] Validate pause points are real

### Phase 3: Evidence Variants
- [ ] Implement 5 variants per case
- [ ] Create evidence degradation logic

### Phase 4: Baselines
- [ ] Port v2 baselines to v3
- [ ] Implement framework_native_checkpoint

### Phase 5: Execution
- [ ] Run full 6,720 test suite
- [ ] Check kill criteria
- [ ] Generate research verdict

### Phase 6: Analysis
- [ ] Document MCC v2's true boundaries
- [ ] Prepare results for publication

## Expected Timeline

- **Weeks 1-3**: Infrastructure + test cases
- **Weeks 4-5**: Evidence variants + baselines
- **Week 6**: Full execution + analysis
- **Week 7**: Iteration if needed

**Total**: ~7 weeks to publication-ready results

## Key Research Insights Expected

If v3 succeeds (0 unsafe, >50% SCC, beats baselines):

1. **MCC v2 works for real mid-execution migration** (not just semantic)
2. **Safe rejection strategy is correct** (evidence degradation handled properly)
3. **Framework-agnostic abstraction is sound** (consistent across pairs)
4. **Publication claims are empirically validated** (v2 + v3 together)

## Next Steps After v3

1. Official baseline implementations (contact AAIF/CapLease authors)
2. Performance testing (latency, overhead, scale)
3. Cryptographic certificates (signature verification)
4. LLM study (human evaluation, usability)
5. Paper submission (SOSP, OSDI, PLDI, or FSE)

## Contact & Citation

**Status**: Design Phase (not yet published)

When citing this work:
```
CrossResumeBench v3: True Mid-Execution Native Migration Benchmark
for Agentic Workflow Checkpoint Portability
[Year TBD] - [Venue TBD]
```

## License

[TBD - likely MIT or Apache 2.0 for benchmark, research paper separate]

---

**Current Status**: 📋 Design Complete → 🏗️ Phase 1 Implementation Starting

See `DESIGN_SPEC.md` for full technical details.
