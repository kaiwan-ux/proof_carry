# What the final experiment MUST test

## 1. Sealed controlled experiment

Keep your original controlled experiment.

It should reproduce the comparison between:

-  ProofCarry/MCCv3 
-  MCCv2 
-  history-only 
-  AAIF 
-  CapLease 

It should report:

```
```

```
total cases
safe completions
safe rejections
unsafe continuations
unsafe rate
completion rate
rejection rate
```

And the statistical comparison:

-  paired/block-level analysis 
-  confidence intervals 
-  effect size 
-  corrected p-values 

**This is your main baseline experiment.**

---

# 2. Expanded semantic benchmark

Your final folder should contain the **104 base cases**.

Across the eight families:

1.  Effect commitment 
2.  Retry 
3.  Approval 
4.  Parallel 
5.  Loop 
6.  Compensation 
7.  Callback 
8.  Composite 

For every case, the experiment should record:

```
```

```
case_id
workflow_family
source_runtime
target_runtime
contract
required_facts
available_evidence
expected_decision
actual_decision
safe/unsafe
reason
```

This is extremely important.

The benchmark should not just produce:

```
```

```
PASS
FAIL
```

It should preserve **why** the decision was made.

---

# 3. Three runtime identities

The final experiment should retain:

### LangGraph

### CrewAI

### Microsoft Agent Framework

And evaluate the runtime-pair directions:

```
```

```
LangGraph → CrewAI
LangGraph → MAF

CrewAI → LangGraph
CrewAI → MAF

MAF → LangGraph
MAF → CrewAI
```

But there should be a very clear distinction between:

### Semantic runtime evaluation

and

### Native runtime evaluation.

Do **not** make the experiment pretend that CrewAI is natively validated if it isn't.

---

# 4. Runtime-specific cases

This is important for a strong conference paper.

Don't simply label the same abstract workflow:

```
```

```
LangGraph
CrewAI
MAF
```

The experiment should contain runtime-specific representations such as:

```
```

```
task identifiers
checkpoint identifiers
pending states
retry state
callback state
branch state
approval state
execution identity
```

Then ProofCarry must establish the semantic identity between source and target representations.

Test:

### Correct mapping

→ CONTINUE

### Missing mapping

→ REJECT

### Wrong mapping

→ REJECT

### Ambiguous mapping

→ REJECT

This makes the cross-runtime experiment much more convincing.

---

# 5. Security experiment

This must be part of the final folder.

Test at minimum:

### A. Certificate forgery

Modify a valid certificate.

Expected:

**REJECT**

### B. Rehashed forgery

Change the fact and calculate a new hash without the signing key.

Expected:

**REJECT**

### C. Replay

Take a valid certificate from execution A and use it for execution B.

Expected:

**REJECT**

### D. Wrong workflow

Certificate from workflow A → workflow B.

Expected:

**REJECT**

### E. Wrong execution

Certificate from execution A → execution B.

Expected:

**REJECT**

### F. Runtime substitution

Certificate for runtime A → runtime B.

Expected:

**REJECT**

### G. Unauthorized identity binding

Expected:

**REJECT**

### H. Expired certificate

Expected:

**REJECT**

### I. Nonce reuse

Expected:

**REJECT**

The final experiment should compare:

```
```

```
Authenticated ProofCarry
vs
Unkeyed/hash-only control
```

and produce the final security numbers.

---

# 6. Ablation experiment

This MUST remain.

Test removal of individual mechanisms:

```
```

```
Full ProofCarry
- closed-world gate
- authentication
- identity binding
- complete snapshot
- dependency reasoning
- certificate verification
```

For each one measure:

```
```

```
safe completion
safe rejection
unsafe continuation
```

The most important one is:

> **Full ProofCarry vs ProofCarry without closed-world reasoning**

because your existing experiment showed a dramatic safety difference.

---

# 7. "Always reject" control

Absolutely include this.

This is important because otherwise a reviewer can say:

> "You achieved zero unsafe outcomes by simply rejecting everything."

Therefore:

```
```

```
Always Reject
```

must have:

```
```

```
Unsafe = 0
Useful completion = 0
```

while ProofCarry should have:

```
```

```
Unsafe = 0
Useful completion > 0
```

This demonstrates **selective safety**, not trivial refusal.

---

# 8. End-to-end migration experiment

For the final folder, I would require this.

Measure:

```
```

```
Source capture
      ↓
Evidence generation
      ↓
Certificate generation/signing
      ↓
Serialization
      ↓
Transfer
      ↓
Verification
      ↓
Proof resolution
      ↓
Identity mapping
      ↓
Target reconstruction
      ↓
Resume
```

For every run record:

```
```

```
capture_ms
evidence_ms
signing_ms
serialization_ms
transfer_ms
verification_ms
proof_ms
translation_ms
resume_ms
total_ms
payload_bytes
decision
```

Then calculate:

-  median 
-  p95 
-  p99 
-  mean 
-  standard deviation 
-  minimum 
-  maximum 

This is much stronger than reporting only the old proof-engine latency.

---

# 9. Payload experiment

Measure certificate/evidence size.

At minimum:

```
```

```
raw checkpoint size
ProofCarry evidence size
certificate size
total transferred size
```

Report:

-  median 
-  p95 
-  min 
-  max 

And ideally compression/transfer overhead if you actually use it.

---

# 10. Failure/rejection reasons

This is very important for analyzing the system.

Every rejection should have a machine-readable reason:

```
```

```
MISSING_FACT
CONTRADICTORY_FACT
INVALID_SIGNATURE
EXPIRED_CERTIFICATE
NONCE_REUSE
WRONG_EXECUTION
WRONG_WORKFLOW
WRONG_RUNTIME
IDENTITY_MISMATCH
INCOMPLETE_SNAPSHOT
DEPENDENCY_UNRESOLVED
```

Then generate a table:

| Rejection reasonCountPercentage |     |     |
| ------------------------------- | --- | --- |
| Missing fact                    | ... | ... |
| Identity mismatch               | ... | ... |
| Expired evidence                | ... | ... |
| ...                             | ... | ... |

This gives you much more insight into **why ProofCarry rejects**.

---

# 11. Repeated runs

Don't run each case once for performance.

For performance experiments, use multiple repetitions, for example:

```
```

```
warm-up runs
+
30–100 measured runs
```

depending on available compute.

Then report:

> median + p95

rather than relying on one execution.

For correctness/security, each logically distinct case can be evaluated once if deterministic, but the implementation should support deterministic seeds and reproducible reruns.

---

# 12. Reproducibility

This is **mandatory** for the final folder.

The folder must have:

```
```

```
seed
configuration
package versions
Python version
OS information
runtime versions
model versions, if any
```

And ideally:

```
```

```
run_id
timestamp
git commit/hash
```

Every result row should be traceable back to:

```
```

```
experiment
case
configuration
seed
runtime
```

---

# 13. Raw results must NEVER be overwritten

The agent should generate:

```
```

```
results/raw/
```

first.

Then analysis scripts generate:

```
```

```
results/processed/
results/tables/
results/figures/
```

This is important because you want to be able to say:

> "These numbers came directly from these raw experimental runs."

Don't hard-code results into Python.

---

# 14. Automatic generation of paper tables/figures

This is something I strongly recommend.

The final folder should have one command such as:

```
```

```
python reproduce_all.py
```

which runs the experiments and produces:

```
```

```
results/tables/

table_1_baselines.csv
table_2_expanded_results.csv
table_3_ablation.csv
table_4_security.csv
table_5_runtime.csv
table_6_performance.csv
```

and:

```
```

```
results/figures/

fig_1_safety.pdf
fig_2_completion.pdf
fig_3_ablation.pdf
fig_4_security.pdf
fig_5_latency.pdf
fig_6_payload.pdf
```

Then your paper can use the **actual generated numbers**.

---

# 15. Statistical analysis

The final folder should automatically calculate:

### Safety

-  unsafe rate 
-  absolute difference 
-  relative difference 
-  95% CI 

### Completion

-  completion rate 
-  difference 
-  95% CI 

### Statistical tests

Use the same methodology you already established rather than changing the statistical method simply to obtain a better result.

Include:

-  paired/block-level test 
-  effect size 
-  confidence intervals 
-  multiple-comparison correction where applicable 

And importantly:

> **Do not treat runtime-pair repetitions as independent samples if they aren't.**

Your current methodology already handles this correctly.

---

# 16. Expected final headline results

The final folder should be capable of generating the following kinds of claims:

### Controlled experiment

```
```

```
ProofCarry:
0 unsafe
```

and statistically compare it against the baselines.

### Expanded semantic evaluation

```
```

```
104 base cases
3,120 ProofCarry conditions
0 unsafe
```

### Security

```
```

```
4,992 attack cases
0 unsafe with authenticated ProofCarry
```

### Ablation

```
```

```
Full ProofCarry
vs
without closed-world gate
```

showing the safety degradation.

### Native runtime

Clearly report:

```
```

```
LangGraph → validated
MAF → validated
CrewAI → validated OR explicitly not reproduced
```

### Performance

Report:

```
```

```
median
p95
p99
payload
end-to-end latency
```

---

# 17. The most important requirement: NO fabricated results

Tell the other agent this explicitly.

The agent **must not**:

-  invent successful CrewAI runs 
-  fabricate latency 
-  fabricate security attacks 
-  duplicate cases just to reach a target number 
-  randomly alter results 
-  hard-code expected outcomes as actual outcomes 
-  claim native runtime execution when only semantic simulation occurred 
-  silently remove failed runs 
-  silently remove unsafe outcomes 

The experiment should report failures honestly.

That is **much more valuable for a top conference paper**.

---

# 18. Your final experimental package should answer these 6 questions

If the folder can answer these six questions clearly, your experimental section is strong:

### Q1.

**Is ProofCarry safer than the baselines?**

→ Sealed holdout.

### Q2.

**Does the result persist on broader cases?**

→ 104-case expanded benchmark.

### Q3.

**Why is it safe?**

→ Ablation.

### Q4.

**Can an attacker bypass the evidence mechanism?**

→ Authenticated security evaluation.

### Q5.

**Does it actually work across different runtime representations?**

→ Runtime-specific + native-runtime evaluation.

### Q6.

**What does it cost?**

→ End-to-end latency + payload evaluation.

---

## The exact instruction I would give your other agent

You can give the other agent this requirement:

> **Build a final, fully reproducible ProofCarry experimental package that replaces the old MCCv3 experimental implementation/results while preserving the original controlled 32-case sealed evaluation and adding the final expanded 104-case semantic benchmark, authenticated security evaluation, component ablations, runtime-specific cross-runtime evaluation, native runtime validation, and end-to-end migration performance measurement. The package must contain raw reproducible data, deterministic seeds, configurations, baseline implementations, statistical analysis, generated tables/figures, rejection reasons, and a single reproducibility entry point. Do not fabricate, hard-code, duplicate, or silently discard results. Clearly distinguish semantic benchmark results from native runtime results. Preserve all experimentally supported claims and explicitly report failures/limitations.**

### In short, your **final experimental folder needs 6 major experiments**:

**1. Sealed baseline comparison**

**2. Expanded 104-case semantic benchmark**

**3. Ablation study**

**4. Authenticated security/attack study**

**5. Runtime-specific + native runtime validation**

**6. End-to-end performance/migration study**

That's the package I would consider the **final experimental foundation** for this paper.