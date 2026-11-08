# CrossResumeBench v3 - Implementation Roadmap

**Goal**: Build publication-ready true mid-execution migration benchmark in ~7 weeks

**Start Date**: 2026-08-26  
**Target Completion**: 2026-10-14

---

## 🎯 SUCCESS CRITERIA

Before starting implementation, confirm:

✅ **MCC v2 is FROZEN** - No modifications allowed, v2 results archived  
✅ **v2 Results validated** - 0 unsafe violations baseline established  
✅ **Design approved** - DESIGN_SPEC.md reviewed and accepted  
✅ **Resources available** - LangGraph/CrewAI/MAF environments ready  

---

## 📅 PHASE 1: Infrastructure (Week 1)

**Goal**: Build native state extraction and resumption infrastructure

### Tasks

#### 1.1 Native State Extractors
- [ ] **LangGraph extractor** (`benchmark/native_extractors/langgraph_extractor.py`)
  - Extract checkpoint from paused LangGraph StateGraph
  - Capture: graph_state, checkpoint_metadata, pending_nodes, thread_id
  - Test: Can extract mid-execution state without modifying workflow
  
- [ ] **CrewAI extractor** (`benchmark/native_extractors/crewai_extractor.py`)
  - Extract state from paused CrewAI Crew execution
  - Capture: task_outputs, agent_states, pending_tasks, crew_metadata
  - Test: Handles CrewAI's task delegation model
  
- [ ] **MAF extractor** (`benchmark/native_extractors/maf_extractor.py`)
  - Extract state from paused AutoGen conversation
  - Capture: message_history, agent_states, pending_replies, group_chat_state
  - Test: Handles MAF's agent-to-agent communication

**Validation**: Each extractor tested on simple "hello world" paused workflow

---

#### 1.2 Native Resume Handlers
- [ ] **LangGraph resumer** (`benchmark/native_resumers/langgraph_resumer.py`)
  - Reconstruct LangGraph checkpoint from MCC v2 payload
  - Resume StateGraph from checkpoint using LangGraph's native API
  - Test: Can resume simple workflow from MCC v2 state
  
- [ ] **CrewAI resumer** (`benchmark/native_resumers/crewai_resumer.py`)
  - Reconstruct CrewAI crew state from MCC v2 payload
  - Resume crew execution using CrewAI's task restart API
  - Test: Handles task dependencies correctly
  
- [ ] **MAF resumer** (`benchmark/native_resumers/maf_resumer.py`)
  - Reconstruct AutoGen conversation state from MCC v2 payload
  - Resume conversation using MAF's message injection
  - Test: Agent roles and turn-taking preserved

**Validation**: Round-trip test (extract → MCC v2 → resume) on simple workflows

---

#### 1.3 Frozen MCC v2 Translator
- [ ] **Copy MCC v2 from v2 benchmark** (`baselines/mcc_v2_frozen.py`)
  - Use EXACT code from CrossResumeBench_v2
  - Add assertion: "MCC_V2_FROZEN = True" at module level
  - No modifications allowed (any change = benchmark invalid)
  
- [ ] **Integration with native extractors**
  - Native state → MCC v2 schema mapper
  - Only allowed fields: app_state, history, certificates
  - Test: Rejects attempts to add new fields
  
- [ ] **Integration with native resumers**
  - MCC v2 schema → Native state reconstructor
  - Must use only frozen schema fields
  - Test: Cannot rely on fields not in v2

**Validation**: Frozen assertion passes, schema validation strict

---

#### 1.4 Framework Native Checkpoint Baseline
- [ ] **Implement self-resume baseline** (`baselines/framework_native_checkpoint.py`)
  - LangGraph pauses → LangGraph resumes (no translation)
  - CrewAI pauses → CrewAI resumes (no translation)
  - MAF pauses → MAF resumes (no translation)
  - Test: Validates pause points are real and resumable

**Validation**: All 28 cases can self-resume in each framework

---

### Deliverables (Week 1)
- ✅ 3 native extractors working
- ✅ 3 native resumers working
- ✅ Frozen MCC v2 translator integrated
- ✅ Framework native checkpoint baseline passes
- ✅ Round-trip test passes on "hello world" workflow

---

## 📅 PHASE 2: Test Case Implementation (Week 2-3)

**Goal**: Implement 28 base test cases with real workflows

### Tasks

#### 2.1 Retry Pause Points (4 cases)
- [ ] **mid_retry_after_failure** (`benchmark/cases/retry_pause_points/mid_retry_after_failure.json`)
  - Workflow: Task with 3 retry attempts
  - Pause: After 2nd failure, before 3rd attempt
  - Workflows: LangGraph version, CrewAI version, MAF version
  - Oracle: Next action = "retry_attempt_3_with_count_2"
  - Unsafe if: Retry count reset, failures lost, attempt skipped

- [ ] **mid_retry_success_partial**
  - Pause: After partial success in retry block
  - Oracle: Next action = "continue_with_partial_result"

- [ ] **mid_retry_backoff_wait**
  - Pause: During exponential backoff delay (after 2s, before 4s)
  - Oracle: Next action = "resume_retry_after_4s_backoff"

- [ ] **mid_retry_exhausted_boundary**
  - Pause: Just hit max_retries limit
  - Oracle: Next action = "trigger_max_retry_handler"

**Per case**: Create 3 workflows (LangGraph/CrewAI/MAF), validate pause point is real

---

#### 2.2 Approval Wait Points (4 cases)
- [ ] **waiting_for_approval**
- [ ] **approval_with_context**
- [ ] **approval_after_effect**
- [ ] **multi_approval_cascade**

---

#### 2.3 Parallel Branch Points (4 cases)
- [ ] **one_branch_done_two_pending**
- [ ] **all_branches_done_join_pending**
- [ ] **branch_with_effect_uncommitted**
- [ ] **parallel_branch_failure_mid_execution**

---

#### 2.4 Effect Acknowledgment Points (4 cases)
- [ ] **effect_committed_ack_pending**
- [ ] **multiple_effects_partial_ack**
- [ ] **effect_commit_callback_pending**
- [ ] **effect_rollback_triggered**

---

#### 2.5 Loop Iteration Points (4 cases)
- [ ] **mid_loop_after_iteration_n**
- [ ] **loop_with_accumulator**
- [ ] **loop_break_condition_met**
- [ ] **nested_loop_inner_paused**

---

#### 2.6 Compensation Pending Points (4 cases)
- [ ] **error_detected_compensation_pending**
- [ ] **partial_compensation**
- [ ] **compensation_with_nested_scope**
- [ ] **compensation_timeout_pending**

---

#### 2.7 Async Callback Points (4 cases)
- [ ] **tool_call_pending_result**
- [ ] **webhook_callback_pending**
- [ ] **async_subtask_pending**
- [ ] **timeout_callback_race**

---

### Workflow Implementation Strategy

For each case, create 3 equivalent workflows:

**LangGraph version** (`workflows/langgraph/{case_id}.py`):
```python
from langgraph.graph import StateGraph

def create_workflow():
    graph = StateGraph(WorkflowState)
    # Define nodes, edges
    # Include pause injection point
    return graph.compile()

def inject_pause_point(graph, pause_id):
    # Pause at specific execution point
    # Return paused checkpoint
    pass
```

**CrewAI version** (`workflows/crewai/{case_id}.py`):
```python
from crewai import Crew, Agent, Task

def create_workflow():
    # Define agents and tasks
    # Include pause injection point
    return Crew(agents=[...], tasks=[...])

def inject_pause_point(crew, pause_id):
    # Pause at specific task boundary
    pass
```

**MAF version** (`workflows/maf/{case_id}.py`):
```python
from autogen import ConversableAgent, GroupChat

def create_workflow():
    # Define agents and conversation
    # Include pause injection point
    return GroupChat(agents=[...])

def inject_pause_point(chat, pause_id):
    # Pause at specific message exchange
    pass
```

---

### Validation per Case
- [ ] All 3 framework versions have equivalent semantics
- [ ] Pause point is real (framework actually pauses there)
- [ ] Native checkpoint can self-resume
- [ ] Oracle behavior is well-defined
- [ ] Unsafe conditions are testable

---

### Deliverables (Week 2-3)
- ✅ 28 test case definitions (JSON)
- ✅ 84 real workflows (28 × 3 frameworks)
- ✅ All pause points validated as real
- ✅ Oracle behavior defined for each
- ✅ Self-resume passes for all 84 workflows

---

## 📅 PHASE 3: Evidence Variants (Week 4)

**Goal**: Implement 5 evidence degradation variants per case

### Tasks

#### 3.1 Evidence Variant Generator
- [ ] **enough_evidence** (baseline)
  - Full MCC v2 certificate with all required fields
  - Expected: Safe completion with correct continuation
  
- [ ] **missing_semantic_completion**
  - Remove semantic boundary markers from certificate
  - Example: Retry count present, max_retries missing
  - Expected: Safe rejection (ambiguous)
  
- [ ] **ambiguous_external_commit**
  - Remove or obscure external effect commit evidence
  - Example: Effect executed, but idempotency token unclear
  - Expected: Safe rejection (cannot certify)
  
- [ ] **partially_observable_progress**
  - Hide derived state, only keep explicit progress markers
  - Example: Iteration count present, loop condition missing
  - Expected: Safe rejection OR completion if reconstructable
  
- [ ] **conflicting_granularity**
  - Mismatch source/target semantic unit granularity
  - Example: Source step-level, target task-level
  - Expected: Safe rejection OR completion if translatable

---

#### 3.2 Variant Generator Implementation
```python
# benchmark/evidence_variants.py

def generate_variant(case, baseline_state, variant_type):
    if variant_type == "enough_evidence":
        return baseline_state  # Full certificate
    
    elif variant_type == "missing_semantic_completion":
        state = baseline_state.copy()
        # Remove boundary markers
        state.certificates.pop("semantic_completion_marker")
        return state
    
    elif variant_type == "ambiguous_external_commit":
        state = baseline_state.copy()
        # Obscure effect commit evidence
        state.certificates["effect_committed"] = "unknown"
        return state
    
    # ... other variants
```

---

#### 3.3 Validation Logic per Variant
- [ ] **Safety checker** (`benchmark/safety_checker.py`)
  - Given: case, variant, actual_action
  - Returns: safe_completion | safe_rejection | unsafe_violation
  - Logic: Compare actual vs oracle, check unsafe_if conditions

---

### Deliverables (Week 4)
- ✅ Evidence variant generator working
- ✅ 5 variants per case (28 × 5 = 140 total variants)
- ✅ Safety checker validates outcomes correctly
- ✅ Test: MCC v2 should complete "enough" and reject degraded

---

## 📅 PHASE 4: Baseline Implementation (Week 5)

**Goal**: Port v2 baselines to v3 and validate

### Tasks

#### 4.1 Port v2 Baselines
- [ ] **oracle** (`baselines/oracle.py`)
  - Perfect translation with full framework knowledge
  - Has access to case definition and expected behavior
  
- [ ] **explicit_minimal** (`baselines/explicit_minimal.py`)
  - Only transfers explicitly marked safe boundaries
  - Rejects anything ambiguous
  
- [ ] **history_inference** (`baselines/history_inference.py`)
  - Infer semantic state from execution history alone
  - No certificates, no explicit markers

---

#### 4.2 Port Independent Baselines
- [ ] **aaif_reference** (`baselines/aaif_reference.py`)
  - AAIF-inspired: Focus on effect commitments
  - Independent implementation (not MCC)
  
- [ ] **caplease_reference** (`baselines/caplease_reference.py`)
  - CapLease-inspired: Focus on capability leases
  - Independent implementation (not MCC)
  
- [ ] **aaif_plus_caplease_reference** (`baselines/aaif_plus_caplease_reference.py`)
  - Combination of both approaches
  - Primary comparison target for MCC v2

---

#### 4.3 Integration Testing
For each baseline:
- [ ] Test on 2-3 simple cases first
- [ ] Validate against oracle on "enough_evidence"
- [ ] Confirm outputs match expected schema
- [ ] Run on 1 full case (all 5 variants, all 6 pairs)

---

### Deliverables (Week 5)
- ✅ 8 baselines working (7 from v2 + 1 new framework_native)
- ✅ Integration tests pass
- ✅ Ready for full benchmark run

---

## 📅 PHASE 5: Full Benchmark Execution (Week 6)

**Goal**: Run complete 6,720 test suite and generate results

### Tasks

#### 5.1 Benchmark Execution Script
- [ ] **run_v3_benchmark.py** (`scripts/run_v3_benchmark.py`)
  ```bash
  # Full run: 28 cases × 5 variants × 6 pairs × 8 baselines = 6,720 tests
  python scripts/run_v3_benchmark.py --full
  
  # Estimated time: 8-12 hours (depends on framework speed)
  ```

#### 5.2 Parallel Execution
- [ ] Run framework pairs in parallel (6 workers)
- [ ] Run baselines in parallel per pair (8 workers)
- [ ] Save individual run artifacts as generated
- [ ] Progress bar and ETA display

#### 5.3 Results Collection
- [ ] **v3_runs.csv** - All 6,720 run outcomes
- [ ] **artifacts/** - Individual run JSON payloads
- [ ] **RESEARCH_VERDICT.json** - Statistical summary
- [ ] **ANALYSIS_SUMMARY.md** - Human-readable analysis

#### 5.4 Kill Criteria Checking
- [ ] **Check #1**: MCC v2 unsafe violations on "enough_evidence"
  - MUST BE 0 - if >0, benchmark fails
  
- [ ] **Check #2**: Framework native checkpoint self-resume
  - MUST succeed for all 84 cases - validates pause points are real
  
- [ ] **Check #3**: MCC v2 SCC > 0%
  - MUST have some completions - validates usefulness
  
- [ ] **Check #4**: MCC v2 vs aaif_plus_caplease
  - MUST show clear separation - no statistical tie
  
- [ ] **Check #5**: Cross-framework consistency
  - Variance MUST be <50% - validates framework-agnostic

#### 5.5 Analysis Scripts
- [ ] **analyze_v3_results.py** - Statistical analysis
- [ ] **verify_v3_results.py** - Schema and integrity checks
- [ ] **export_v3_results.py** - Generate results ZIP

---

### Deliverables (Week 6)
- ✅ All 6,720 tests complete
- ✅ v3_runs.csv with all results
- ✅ 6,720 individual artifacts saved
- ✅ Kill criteria checked (all MUST pass)
- ✅ RESEARCH_VERDICT.json generated
- ✅ CrossResumeBench_v3_results.zip ready

---

## 📅 PHASE 6: Analysis & Iteration (Week 7)

**Goal**: Analyze results, document boundaries, prepare for publication

### Tasks

#### 6.1 Kill Criteria Analysis
If any kill criterion fails:
- [ ] **Identify root cause** - Which cases? Which variants? Which pairs?
- [ ] **Document failure mode** - Why did MCC v2 fail?
- [ ] **Determine if fixable** - Test case issue or MCC v2 limitation?
- [ ] **Iterate if possible** - Fix test cases (NOT MCC v2), re-run

If all kill criteria pass:
- [ ] **Document success** - MCC v2's true boundaries validated
- [ ] **Proceed to publication prep**

---

#### 6.2 MCC v2 Capability Boundary Documentation
- [ ] **MCC_V2_TRUE_BOUNDARIES.md**
  - What MCC v2 CAN safely handle
  - What MCC v2 CANNOT handle (safe rejections)
  - Evidence requirements for safe completion
  - Granularity translation limits

---

#### 6.3 Cross-Framework Consistency Analysis
- [ ] **CROSS_FRAMEWORK_CONSISTENCY_ANALYSIS.md**
  - Variance analysis across 6 framework pairs
  - Cases where outcomes differ by pair
  - Framework-specific quirks vs semantic issues

---

#### 6.4 Evidence Degradation Study
- [ ] **EVIDENCE_DEGRADATION_STUDY.md**
  - Performance curves: enough → missing → ambiguous → partial → conflicting
  - MCC v2's safe rejection strategy validation
  - Comparison with baselines' degradation curves

---

#### 6.5 Baseline Comparison Report
- [ ] **V3_BASELINE_COMPARISON.md**
  - MCC v2 vs all 7 baselines
  - Statistical significance tests
  - Per-family performance breakdown
  - Publication-ready tables and figures

---

#### 6.6 v2 vs v3 Comparison
- [ ] **V2_VS_V3_RESULTS.md**
  - Semantic certification (v2) vs true mid-execution (v3)
  - Did v3 expose new MCC v2 limitations?
  - Combined evidence for publication

---

### Deliverables (Week 7)
- ✅ Root cause analysis (if kill criteria failed)
- ✅ MCC v2 capability boundaries documented
- ✅ Cross-framework consistency validated
- ✅ Evidence degradation curves analyzed
- ✅ Baseline comparison complete
- ✅ v2+v3 combined analysis ready
- ✅ Publication-ready results package

---

## 📦 FINAL DELIVERABLES

### For Publication
1. **CrossResumeBench_v3_results.zip** - Complete benchmark results
2. **RESEARCH_VERDICT.json** - Statistical evidence
3. **MCC_V2_TRUE_BOUNDARIES.md** - Empirical capability boundaries
4. **CROSS_FRAMEWORK_CONSISTENCY_ANALYSIS.md** - Framework pair validation
5. **EVIDENCE_DEGRADATION_STUDY.md** - Ambiguity handling validation
6. **V3_BASELINE_COMPARISON.md** - Comparative performance
7. **V2_VS_V3_RESULTS.md** - Combined semantic + mid-execution evidence

### For Reproducibility
- [ ] Complete source code (Apache 2.0 or MIT license)
- [ ] Requirements and setup instructions
- [ ] Docker container for isolated execution
- [ ] GitHub repo with CI/CD for validation
- [ ] Zenodo DOI for benchmark artifact

---

## 🎯 DEFINITION OF DONE

v3 is complete when:

✅ **All 6,720 tests executed successfully**  
✅ **All 5 kill criteria PASSED** (no invalid results)  
✅ **MCC v2 shows 0 unsafe on "enough_evidence"**  
✅ **MCC v2 clearly outperforms aaif_plus_caplease**  
✅ **Cross-framework consistency <20% variance**  
✅ **All documentation complete**  
✅ **Results package ready for publication**  

---

## 🚀 NEXT STEPS AFTER V3

If v3 succeeds:

### Immediate (Weeks 8-10)
1. **Official baselines** - Contact AAIF/CapLease authors
2. **Performance testing** - Latency, overhead, scale
3. **Cryptographic certificates** - Signature verification

### Short-term (Weeks 11-16)
4. **LLM study** - Human evaluation, usability testing
5. **Real-world case studies** - Industry validation
6. **Paper writing** - Draft, revisions, submission

### Publication Target
- **Venue**: SOSP, OSDI, PLDI, or FSE (top-tier)
- **Timeline**: Submit 3-4 months after v3 completion
- **Expected impact**: High (solves real problem, strong empirical evidence)

---

## 📊 RESOURCE REQUIREMENTS

### Compute
- **Development**: 1 machine with Python 3.10+, LangGraph/CrewAI/MAF
- **Benchmark run**: 6-8 core machine, 16GB+ RAM, 8-12 hours
- **Optional**: Cluster for parallel execution (reduces to 2-3 hours)

### Time
- **Implementation**: 5 weeks (Phases 1-5)
- **Analysis**: 1-2 weeks (Phase 6)
- **Iteration**: 0-2 weeks (if kill criteria fail)
- **Total**: 6-9 weeks to publication-ready

### Personnel
- **Primary**: 1 researcher/engineer full-time
- **Advisor**: Code reviews, design feedback
- **Optional**: 1 additional for parallel workflow implementation

---

## 📞 CONTACT

**Status**: Implementation Phase 1 Starting  
**Next Update**: End of Week 1 (Phase 1 deliverables)

---

**END OF ROADMAP**

Let's start Phase 1: Infrastructure implementation.
