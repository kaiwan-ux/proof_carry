# CrossResumeBench v3 - True Mid-Execution Native Migration
## Design Specification

**Version**: 3.0.0  
**Created**: 2026-08-26  
**Status**: Initial Design  
**Purpose**: Test MCC v2 (frozen) with real paused in-flight executions across frameworks

---

## 🎯 RESEARCH QUESTION

**Can frozen MCC v2 safely translate a genuinely paused in-flight execution between frameworks that represent execution state differently?**

If MCC v2 achieves 0 unsafe continuations with useful completion coverage on **real mid-execution pauses**, we have strong evidence for publication.

---

## 🔒 CONSTRAINTS

### 1. MCC v2 is FROZEN
- No new fields added to MCC v2 schema
- No modifications to certification logic
- Use exactly: `app_state + history + certificates`
- Any v3 failures = evidence of MCC v2's true boundaries

### 2. Real Native Runtime State
- Extract **actual framework internal state** (not benchmark-defined state)
- Source framework must be **genuinely paused** mid-execution
- No shared Python continuation functions
- Target framework resumes using **its own control flow**

### 3. True Mid-Execution Pause Points
Test workflows paused at **unresolved execution states**:
- ✅ Mid-retry (after failure, before next attempt)
- ✅ Waiting for approval (human-in-loop pending)
- ✅ After one parallel branch finishes (others still running)
- ✅ After external effect commits but before acknowledgment
- ✅ Mid-loop (after iteration N, before N+1)
- ✅ Before compensation (error detected, rollback pending)
- ✅ Pending callback/tool result (async operation in-flight)

---

## 🏗️ ARCHITECTURE

### Test Case Structure

Each test case represents a **real workflow paused mid-execution**:

```python
{
  "case_id": "crb3-mid_retry_after_failure-v01",
  "family": "retry_pause_points",
  "description": "Workflow paused after 2nd retry failure, before 3rd attempt",
  
  # Real source framework execution
  "source_framework": "langgraph",
  "source_workflow": "three_retry_approval_workflow.py",
  "pause_point": "after_retry_2_fail_before_retry_3",
  
  # Native state extraction
  "native_state_extractor": "extract_langgraph_mid_retry_state",
  "expected_native_fields": [
    "graph_state",
    "checkpoint_metadata", 
    "pending_nodes",
    "retry_count",
    "last_error"
  ],
  
  # MCC v2 translation (frozen schema)
  "mcc_v2_translator": "translate_via_frozen_mcc_v2",
  "allowed_mcc_fields": ["app_state", "history", "certificates"],
  
  # Target framework resumption
  "target_framework": "crewai",
  "target_workflow": "three_retry_approval_workflow_crewai.py",
  "resume_point": "continue_from_mcc_v2_state",
  
  # Oracle behavior
  "oracle_next_action": "retry_attempt_3_with_count_2",
  "oracle_expected_state": {
    "retry_count": 2,
    "previous_failures": ["timeout", "invalid_response"],
    "next_action": "execute_task_with_retry_3"
  },
  
  # Evidence difficulty
  "evidence_variant": "enough_evidence",
  
  # Safety criteria
  "unsafe_if": [
    "retry_count_reset_to_0",
    "previous_failures_lost",
    "retry_3_skipped",
    "compensation_triggered_incorrectly"
  ]
}
```

### Framework Pairs (All 6 Directions)

1. **LangGraph → CrewAI**
2. **LangGraph → MAF**
3. **CrewAI → LangGraph**
4. **CrewAI → MAF**
5. **MAF → LangGraph**
6. **MAF → CrewAI**

---

## 🧪 TEST FAMILIES

### 1. **Retry Pause Points** (retry_pause_points)
**Real scenarios**: Workflow paused during retry logic

Test cases:
- `mid_retry_after_failure`: Paused after Nth failure, before (N+1)th attempt
- `mid_retry_success_partial`: Paused after partial success in retry block
- `mid_retry_backoff_wait`: Paused during exponential backoff delay
- `mid_retry_exhausted_boundary`: Paused at max_retries boundary (just hit limit)

**Key evidence**: `retry_count`, `failure_history`, `backoff_state`, `max_retries`

**Unsafe if**: Retry count reset, failures lost, retry logic bypassed

---

### 2. **Approval Wait Points** (approval_wait_points)
**Real scenarios**: Human-in-loop approval pending

Test cases:
- `waiting_for_approval`: Paused with approval request pending
- `approval_with_context`: Paused with approval + context data pending
- `approval_after_effect`: Paused after effect commits, before approval check
- `multi_approval_cascade`: Paused between approval step 1 and 2

**Key evidence**: `pending_approval_id`, `approval_context`, `requester`, `timeout`

**Unsafe if**: Approval bypassed, context lost, double-approval triggered

---

### 3. **Parallel Branch Points** (parallel_branch_points)
**Real scenarios**: Parallel execution with incomplete branches

Test cases:
- `one_branch_done_two_pending`: Branch A finished, B and C still running
- `all_branches_done_join_pending`: All branches complete, join not executed
- `branch_with_effect_uncommitted`: Branch A done with uncommitted effect
- `parallel_branch_failure_mid_execution`: Branch A failed, B succeeded, C running

**Key evidence**: `completed_branches`, `pending_branches`, `branch_results`, `join_state`

**Unsafe if**: Incomplete branches re-executed, join triggered prematurely, results lost

---

### 4. **Effect Acknowledgment Points** (effect_acknowledgment_points)
**Real scenarios**: External effect committed, acknowledgment pending

Test cases:
- `effect_committed_ack_pending`: Effect committed, workflow not yet acknowledged
- `multiple_effects_partial_ack`: 2 effects committed, only 1 acknowledged
- `effect_commit_callback_pending`: Effect committed, callback not received
- `effect_rollback_triggered`: Effect committed, rollback initiated but not complete

**Key evidence**: `committed_effects`, `acknowledged_effects`, `pending_callbacks`, `rollback_state`

**Unsafe if**: Committed effect re-executed, acknowledgment lost, rollback skipped

---

### 5. **Loop Iteration Points** (loop_iteration_points)
**Real scenarios**: Loop paused between iterations

Test cases:
- `mid_loop_after_iteration_n`: Completed N iterations, N+1 not started
- `loop_with_accumulator`: Loop paused with partial accumulated result
- `loop_break_condition_met`: Break condition just met, exit not executed
- `nested_loop_inner_paused`: Outer loop iteration 2, inner loop iteration 3, inner paused

**Key evidence**: `iteration_count`, `accumulator_state`, `loop_condition`, `break_triggered`

**Unsafe if**: Iteration count reset, accumulator lost, loop restarted, double iteration

---

### 6. **Compensation Pending Points** (compensation_pending_points)
**Real scenarios**: Error detected, compensation not yet executed

Test cases:
- `error_detected_compensation_pending`: Error caught, rollback queued but not started
- `partial_compensation`: Compensation step 1 done, step 2 pending
- `compensation_with_nested_scope`: Parent scope compensation pending, child scope closed
- `compensation_timeout_pending`: Compensation triggered, timeout handler not invoked

**Key evidence**: `error_type`, `compensation_scope`, `completed_compensations`, `pending_compensations`

**Unsafe if**: Compensation skipped, error cleared incorrectly, scope mismatch

---

### 7. **Async Callback Points** (async_callback_points)
**Real scenarios**: Async operation in-flight, callback pending

Test cases:
- `tool_call_pending_result`: Tool invoked, result not yet returned
- `webhook_callback_pending`: Webhook registered, callback not received
- `async_subtask_pending`: Async subtask started, completion pending
- `timeout_callback_race`: Operation pending, timeout callback also pending

**Key evidence**: `pending_callbacks`, `callback_ids`, `timeout_state`, `async_handles`

**Unsafe if**: Callback lost, duplicate callback triggered, timeout mishandled

---

## 🔬 EVIDENCE VARIANTS

Each test case tested across **5 evidence difficulty levels**:

### 1. **Enough Evidence** (enough_evidence)
MCC v2 certificate contains sufficient information to resume safely.

**Expected**: Safe completion with correct continuation

---

### 2. **Missing Semantic Completion Evidence** (missing_semantic_completion)
Certificate lacks clear semantic completion boundary markers.

**Examples**:
- Retry count present, but max_retries boundary unclear
- Loop iteration count present, but exit condition missing
- Effect committed marker present, but acknowledgment state unclear

**Expected**: Safe rejection (MCC v2 refuses to certify ambiguous state)

---

### 3. **Ambiguous External Commit** (ambiguous_external_commit)
External effect may or may not have committed; evidence is unclear.

**Examples**:
- Effect commit acknowledged but idempotency token missing
- HTTP POST to external API, response unclear
- Database write with unclear transaction boundary

**Expected**: Safe rejection (cannot certify without clear commit evidence)

---

### 4. **Partially Observable Progress** (partially_observable_progress)
Some execution progress visible, but critical state hidden.

**Examples**:
- Framework internal state not exposed in checkpoint
- Derived state calculable but not explicitly captured
- Progress markers present but incomplete

**Expected**: Safe rejection OR safe completion if MCC v2 can reconstruct from available evidence

---

### 5. **Conflicting Granularity** (conflicting_granularity)
Source and target frameworks represent state at different granularities.

**Examples**:
- Source: Fine-grained step-level state
- Target: Coarse-grained task-level state
- Mismatch in what constitutes a "semantic unit"

**Expected**: Safe rejection OR safe completion if MCC v2 can translate granularity safely

---

## 🎲 BASELINE COMPARISONS

Test **frozen MCC v2** against same baselines as v2:

1. **mcc_v2** (frozen) - No changes allowed
2. **oracle** - Perfect translation with full framework knowledge
3. **explicit_minimal** - Only explicitly marked safe boundaries
4. **history_inference** - Infer from execution history alone
5. **aaif_reference** - Independent AAIF-inspired implementation
6. **caplease_reference** - Independent CapLease-inspired implementation
7. **aaif_plus_caplease_reference** - Combination approach

**New baseline for v3**:

8. **framework_native_checkpoint** - Each framework's own native checkpoint/resume (no translation)
   - Tests if framework can resume its own paused state
   - Validates that pause points are real and resumable

---

## 📏 SUCCESS METRICS

### Primary Metrics (Same as v2)
- **Safe Completion Count (SCC)**: Successful safe continuations
- **Safe Rejection Count**: Correctly refused ambiguous states
- **Unsafe Violation Count**: Incorrect/unsafe continuations
- **Technical Failure Count**: Translation errors

### v3-Specific Metrics

1. **Native State Capture Success Rate**
   - % of pause points where source framework state extracted successfully
   - Validates pause points are real

2. **Native Resume Success Rate**
   - % of MCC v2 translations that target framework could resume
   - Validates target framework compatibility

3. **Cross-Framework Consistency**
   - For same case across 6 framework pairs, how consistent are outcomes?
   - Validates MCC v2 is framework-agnostic

4. **Evidence Variant Degradation**
   - How does performance degrade from "enough" → "conflicting"?
   - Validates MCC v2's safe rejection strategy

---

## 🚨 KILL CRITERIA (v3)

Any of these = benchmark invalid, must fix before publication:

### Kill #1: MCC v2 Shows Unsafe Violations
If frozen MCC v2 has **any unsafe violations** in "enough_evidence" variant.

**Why**: v2 proved 0 unsafe with semantic certification. True mid-execution should not introduce new unsafety with sufficient evidence.

---

### Kill #2: Framework Native Checkpoint Fails
If framework's **own native checkpoint** cannot resume its own paused state.

**Why**: Proves pause points are fake, not real mid-execution states.

---

### Kill #3: No Safe Completions
If frozen MCC v2 achieves **0% SCC** (all rejections, no completions).

**Why**: MCC v2 is too conservative to be useful for real migration.

---

### Kill #4: Baseline Equivalence
If frozen MCC v2 is **statistically tied** with aaif_plus_caplease_reference in both SCC and unsafe count.

**Why**: No clear advantage over independent baseline.

---

### Kill #5: Framework Pair Inconsistency
If frozen MCC v2 shows **>50% outcome variance** across framework pairs for the same semantic case.

**Example**: LangGraph→CrewAI safe, but CrewAI→LangGraph unsafe for identical semantic scenario.

**Why**: Proves MCC v2 is framework-specific, not semantic-level abstraction.

---

## 🏗️ IMPLEMENTATION PLAN

### Phase 1: Infrastructure (Week 1)
- [ ] Create v3 benchmark directory structure
- [ ] Implement native state extractors for LangGraph/CrewAI/MAF
- [ ] Implement native resume handlers for each framework
- [ ] Build MCC v2 frozen translator (no modifications)
- [ ] Create framework_native_checkpoint baseline

### Phase 2: Test Case Implementation (Week 2-3)
- [ ] Implement 7 test families (28 base cases)
- [ ] Create real workflows for each framework (3 × 28 = 84 workflows)
- [ ] Implement pause point injection for each scenario
- [ ] Validate that native checkpoints can self-resume

### Phase 3: Evidence Variants (Week 4)
- [ ] Implement 5 evidence variants per case
- [ ] Create evidence degradation logic
- [ ] Validate unsafe conditions for each variant
- [ ] Test oracle behavior across all variants

### Phase 4: Baseline Implementation (Week 5)
- [ ] Port v2 baselines to v3 architecture
- [ ] Implement framework_native_checkpoint baseline
- [ ] Validate all baselines against simple cases first

### Phase 5: Full Benchmark Execution (Week 6)
- [ ] Run full benchmark: 28 cases × 5 variants × 6 pairs × 8 baselines = 6,720 tests
- [ ] Generate results CSV and artifacts
- [ ] Run analysis scripts
- [ ] Check kill criteria
- [ ] Generate research verdict

### Phase 6: Analysis & Iteration (Week 7)
- [ ] If kill criteria hit: analyze root cause
- [ ] Document MCC v2's true boundaries
- [ ] Iterate on test cases (not MCC v2) if needed
- [ ] Prepare results for paper

---

## 📊 EXPECTED RESULTS STRUCTURE

### File Structure
```
CrossResumeBench_v3_True_MidExecution_Migration/
├── README.md
├── DESIGN_SPEC.md (this file)
├── pyproject.toml
├── requirements.txt
├── config/
│   └── benchmark.json
├── benchmark/
│   ├── cases/
│   │   ├── retry_pause_points/
│   │   ├── approval_wait_points/
│   │   ├── parallel_branch_points/
│   │   ├── effect_acknowledgment_points/
│   │   ├── loop_iteration_points/
│   │   ├── compensation_pending_points/
│   │   └── async_callback_points/
│   ├── native_extractors/
│   │   ├── langgraph_extractor.py
│   │   ├── crewai_extractor.py
│   │   └── maf_extractor.py
│   ├── native_resumers/
│   │   ├── langgraph_resumer.py
│   │   ├── crewai_resumer.py
│   │   └── maf_resumer.py
│   └── generated_suite.json
├── baselines/
│   ├── mcc_v2_frozen.py
│   ├── oracle.py
│   ├── explicit_minimal.py
│   ├── history_inference.py
│   ├── aaif_reference.py
│   ├── caplease_reference.py
│   ├── aaif_plus_caplease_reference.py
│   └── framework_native_checkpoint.py
├── workflows/
│   ├── langgraph/
│   ├── crewai/
│   └── maf/
├── scripts/
│   ├── run_v3_benchmark.py
│   ├── analyze_v3_results.py
│   ├── verify_v3_results.py
│   └── export_v3_results.py
├── results/
│   ├── v3_runs.csv
│   ├── RESEARCH_VERDICT.json
│   └── artifacts/
└── docs/
    ├── NATIVE_STATE_SPEC.md
    ├── PAUSE_POINT_VALIDATION.md
    └── V3_VS_V2_COMPARISON.md
```

### Results CSV Schema
```csv
run_id,source_framework,target_framework,case_id,family,evidence_variant,baseline,
safe_completion,safe_rejection,unsafe_violation,technical_failure,failure_types,
native_extraction_success,native_resume_success,
pause_point,expected_next_action,actual_next_action,
payload_bytes,reject_reason
```

---

## 🔬 RESEARCH PROTOCOL

### Hypothesis
**H1**: Frozen MCC v2 achieves **0 unsafe violations** on "enough_evidence" variants across all 6 framework pairs.

**H2**: Frozen MCC v2's safe rejection rate increases appropriately as evidence degrades from "enough" → "conflicting".

**H3**: Frozen MCC v2 outperforms aaif_plus_caplease_reference in both SCC and safety across real mid-execution migrations.

### Data Collection
- Automated test execution (no manual intervention)
- All results timestamped and frozen with SHA256
- Individual run artifacts saved as JSON
- Framework-specific logs captured for debugging

### Analysis Plan
1. Verify kill criteria (must pass all 5)
2. Compare MCC v2 vs baselines (SCC, unsafe, safe rejection)
3. Analyze evidence variant degradation curves
4. Check cross-framework consistency (variance analysis)
5. Identify MCC v2's true capability boundaries
6. Document failure modes for paper

---

## 📋 DELIVERABLES FOR PAPER

If v3 succeeds (no kill criteria hit):

1. **CrossResumeBench_v3_results.zip** - Complete benchmark results
2. **V3_RESEARCH_VERDICT.json** - Statistical evidence
3. **MCC_V2_TRUE_BOUNDARIES.md** - Empirical capability boundaries
4. **CROSS_FRAMEWORK_CONSISTENCY_ANALYSIS.md** - Framework pair comparison
5. **EVIDENCE_DEGRADATION_STUDY.md** - How MCC v2 handles ambiguity

These form the empirical evidence for publication claims.

---

## 🎯 NEXT STEPS AFTER V3

If v3 shows strong results:

1. **Official Baseline Implementations**
   - Contact AAIF/CapLease authors for official implementations
   - Replace reference implementations with authoritative versions

2. **Performance Testing**
   - Measure translation latency (microseconds)
   - Measure payload overhead (bytes)
   - Test at scale (1000s of concurrent migrations)

3. **Cryptographic Certificates**
   - Add signature verification to MCC v2
   - Test tamper-detection
   - Measure crypto overhead

4. **LLM Study**
   - Human evaluation of failure modes
   - Developer usability testing
   - Real-world case studies

5. **Paper Writing**
   - Use v2 + v3 results as empirical evidence
   - Submit to top-tier venue (SOSP, OSDI, PLDI, or FSE)

---

## ✅ ACCEPTANCE CRITERIA

v3 is ready for publication evidence if:

- ✅ All 5 kill criteria passed
- ✅ MCC v2 (frozen) shows 0 unsafe violations on "enough_evidence"
- ✅ MCC v2 achieves >50% SCC (useful completion coverage)
- ✅ MCC v2 clearly outperforms aaif_plus_caplease_reference
- ✅ Cross-framework consistency <20% variance
- ✅ Evidence degradation curves are monotonic and appropriate
- ✅ All 6,720 tests complete without technical infrastructure failures

---

**END OF DESIGN SPEC**

Next: Implement Phase 1 infrastructure and validate with 1-2 simple cases before full build-out.
