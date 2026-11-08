# MASTER PROMPT — WRITE A WORLD-CLASS IEEE RESEARCH PAPER FROM MY COMPLETE PROJECT, EXPERIMENTS, RESULTS, ARCHITECTURE, AND THEORY

Act as a combination of:

- a senior AI/ML research scientist,
- an experienced IEEE paper author,
- an ICLR/NeurIPS/ICML/ACL-style research reviewer,
- an IEEE Transactions reviewer,
- an experimental methodology expert,
- a statistical analysis expert,
- a technical scientific writer,
- a LaTeX/IEEEtran expert,
- a reproducibility auditor,
- and a hostile Reviewer #2.

I have already completed a substantial research project.

The project materials available to you may include:

- complete project description,
- research problem,
- research questions,
- hypotheses,
- proposed mechanism,
- mathematical formulation,
- system architecture,
- architecture diagrams,
- experimental methodology,
- datasets,
- models,
- baselines,
- implementation details,
- source code,
- result folders,
- CSV/JSON/log files,
- result screenshots,
- plots,
- tables,
- ablation experiments,
- comparison experiments,
- diagnostic experiments,
- theoretical explanations,
- previous project reports,
- previous analysis from this conversation,
- related/base research papers,
- citations,
- and discussions describing why each design decision was made.

Your job is to transform ALL of this material into a **complete, rigorous, polished, publication-quality IEEE research paper and complete LaTeX project folder**.

Do not simply summarize the project.

Treat the available materials as if you are the lead author responsible for submitting the work to a serious peer-reviewed venue.

---

# PRIMARY OBJECTIVE

Produce a paper where:

> Every important scientific claim is supported by evidence.

> Every experiment has a clear purpose.

> Every table and figure contributes to the research story.

> The novelty is stated precisely and conservatively.

> The methodology is reproducible.

> The comparison with prior work is technically fair.

> The writing is concise, professional, human, and publication-ready.

> The architecture and proposed mechanism are explained clearly enough that another researcher could implement them.

> The results support one coherent scientific argument.

The objective is NOT to make the project sound impressive by exaggeration.

The objective is to make the **strongest defensible scientific case possible from the actual evidence**.

---

# IMPORTANT SCIENTIFIC INTEGRITY RULE

Do NOT:

- fabricate results,
- modify numerical values,
- invent experiments,
- invent datasets,
- invent baselines,
- invent statistical significance,
- invent citations,
- invent related papers,
- hide a major contradictory result,
- claim state-of-the-art performance without sufficient evidence,
- claim causality where only correlation was measured,
- claim generalization where it was not tested.

Instead:

If a result is weaker than expected, determine:

1. whether it invalidates the main hypothesis,
2. whether it is an understandable boundary condition,
3. whether it should narrow the claim,
4. whether it belongs in limitations,
5. whether it reveals an interesting failure mode.

Build the strongest **truthful and defensible** research story.

Do not let minor anomalies dominate the paper, but do not conceal material evidence.

---

# PHASE 1 — INGEST EVERYTHING BEFORE WRITING

Before writing a single paragraph of the paper, inspect all provided materials.

Read:

- every project document,
- every results report,
- every experiment summary,
- every relevant code/configuration file,
- every result table,
- every plot,
- every image,
- every architecture diagram,
- every baseline description,
- every experiment condition,
- every theoretical note,
- every related/base paper supplied.

If archives/ZIP folders are available, inspect their contents systematically.

Do NOT rely only on previously written summaries if raw results are available.

Create an internal evidence inventory.

For each experiment identify:

Experiment name
Research question
Hypothesis
Dataset
Model
Baseline
Conditions
Independent variable
Dependent variable
Metrics
Number of runs
Random seeds
Raw result location
Main result
Unexpected result
Statistical information
Figure/table that can represent it
Claim it supports.

Do this before manuscript writing.

---

# PHASE 2 — VERIFY THE NUMBERS

Audit all reported numerical results.

Where raw logs/results are available:

- recalculate means,
- standard deviations,
- percentages,
- improvements,
- differences,
- relative changes,
- success rates,
- error rates,
- confidence intervals where appropriate.

Check consistency between:

- raw outputs,
- markdown reports,
- screenshots,
- graphs,
- previously written summaries.

If two files disagree, investigate the source of truth.

Never copy a number blindly from an old summary.

Create an internal:

# VERIFIED RESULTS TABLE

containing only values confirmed from the available experiment outputs.

---

# PHASE 3 — CREATE A CLAIM–EVIDENCE MATRIX

Before drafting the paper create:

| ClaimEvidenceExperimentFigure/TableStrengthSafe Wording |
| ------------------------------------------------------- |

Classify evidence strength as:

STRONG
MODERATE
PRELIMINARY
UNSUPPORTED

Never make an UNSUPPORTED claim in the final paper.

For preliminary evidence, use language such as:

- suggests,
- indicates,
- provides evidence that,
- is consistent with,
- under the evaluated conditions.

Reserve stronger language such as:

- demonstrates,
- establishes,
- consistently improves,

only where justified.

---

# PHASE 4 — IDENTIFY THE REAL PAPER CONTRIBUTION

Do not assume the entire software system is the contribution.

Determine exactly what can become the scientific contribution.

Separate:

## Research Problem

What unresolved problem is studied?

## Observed Phenomenon

What did our experiments reveal?

## Proposed Mechanism

What new mechanism did we introduce?

## Evaluation Contribution

What did our experiments establish?

## System Contribution

What implementation or architecture demonstrates practicality?

Then write the contribution in the form:

> Existing approaches perform X, but remain weak under Y because Z. We introduce A, which changes B through mechanism C. Across D experiments / datasets / conditions, we evaluate whether this improves E while controlling for F.

Adapt this completely to my actual project.

---

# PHASE 5 — DETERMINE THE CORRECT CLAIM LEVEL

Do not automatically claim:

“state of the art”

“revolutionary”

“first ever”

“solves”

“eliminates”

“proves”

Instead determine the strongest defensible level.

Choose among:

### Phenomenon contribution

We identify and characterize a previously underexplored failure.

### Method contribution

We introduce a new mechanism addressing the failure.

### Architecture contribution

We introduce a new system/architecture.

### Evaluation contribution

We introduce a stronger evaluation methodology.

### Benchmark/resource contribution

If applicable.

### Combined contribution

Only if evidence supports multiple contributions.

---

# PHASE 6 — NOVELTY RE-VALIDATION

Before finalizing the paper, search the current literature again.

Prioritize:

- 2026,
- 2025,
- 2024,

plus foundational older work.

Search:

- arXiv,
- OpenReview,
- IEEE,
- ACM,
- ACL Anthology,
- NeurIPS,
- ICML,
- ICLR,
- AAAI,
- COLM,
- MLSys,
- relevant domain venues.

Search the actual mechanism using synonyms.

Do not search only our project name.

Find at least the 10–20 closest papers.

For each determine:

Problem
Method
Mechanism
Assumptions
Datasets
Main result
Difference from our work
Threat to novelty.

If a recent paper substantially overlaps with our contribution, revise the novelty statement.

Do not conceal it.

---

# PHASE 7 — FIND THE BEST RESEARCH TITLE

Generate at least 20 possible academic titles internally.

Evaluate them for:

- technical accuracy,
- memorability,
- novelty signaling,
- clarity,
- seriousness,
- searchability,
- absence of hype.

The title should preferably communicate:

**Mechanism + Problem + Context**

Avoid vague titles such as:

“An Intelligent Framework for…”

“Advanced AI System…”

“Novel Approach for…”

unless technically necessary.

Choose ONE final title.

Also create one concise memorable mechanism/project name if useful.

The project name must not artificially inflate novelty.

---

# PHASE 8 — CREATE THE PAPER STORY

The paper must tell ONE coherent story:

Problem
↓
Why existing approaches fail
↓
Scientific gap
↓
Our insight
↓
Our mechanism
↓
Why it should work
↓
Experiment designed to test it
↓
Results
↓
What results mean
↓
Limitations
↓
Implications.

Do NOT structure the paper as a chronology of everything we tried.

Do not write:

“First we tried experiment 1, then experiment 2…”

Instead organize experiments by the scientific questions they answer.

---

# PHASE 9 — SELECT THE PRIMARY PAPER MESSAGE

Force the entire paper to answer one central question.

Write:

# CENTRAL PAPER QUESTION

[...]

Then:

# CENTRAL CLAIM

[...]

Then:

# EVIDENCE REQUIRED FOR THIS CLAIM

[...]

Ensure every major section serves this claim.

Remove unrelated experiments or move them to appendix/supplementary material.

---

# PHASE 10 — IEEE PAPER STRUCTURE

Unless a specific target venue/template has been supplied, use standard IEEEtran two-column conference format.

If I specify an IEEE journal, adapt IEEEtran accordingly.

The manuscript should contain, where appropriate:

Title

Authors/placeholders

Abstract

Index Terms / Keywords

I. Introduction

II. Background / Problem Formulation

III. Related Work

IV. Proposed Method / Architecture

V. Experimental Methodology

VI. Results

VII. Analysis / Discussion

VIII. Limitations and Threats to Validity

IX. Development/System Implementation if important to contribution

X. Conclusion

Acknowledgment if required

References

Appendices / Supplementary Material where useful.

Do not mechanically use these headings if a more appropriate IEEE structure improves the paper.

---

# PHASE 11 — WRITE A WORLD-CLASS ABSTRACT

The abstract must contain:

1. context,
2. exact problem,
3. existing limitation,
4. proposed mechanism,
5. experimental setup,
6. strongest verified quantitative results,
7. significance.

Avoid:

- citations,
- vague marketing language,
- unsupported novelty claims,
- excessive background.

Prefer approximately 150–250 words unless venue requires otherwise.

Every number in the abstract must be verified.

---

# PHASE 12 — WRITE THE INTRODUCTION

The introduction should gradually narrow:

Broad importance
↓
Specific technical problem
↓
Why current approaches fail
↓
Why this matters
↓
Research gap
↓
Our key insight
↓
Our method
↓
Results summary
↓
Contributions.

The final part should contain approximately 3–4 precise contributions.

Do NOT write generic contributions such as:

- “We build a framework.”
- “We conduct experiments.”
- “We compare methods.”

Instead write concrete scientific contributions.

Example STYLE only:

1. We identify \_\_\_\_\_\_ and empirically show \_\_\_\_\_\_.
2. We introduce \_\_\_\_\_\_, a mechanism that \_\_\_\_\_\_.
3. We evaluate \_\_\_\_\_\_ across \_\_\_\_\_\_ and show \_\_\_\_\_\_.
4. We release/implement \_\_\_\_\_\_ enabling \_\_\_\_\_\_.

Use the actual project.

---

# PHASE 13 — BACKGROUND / PROBLEM FORMULATION

Explain only concepts necessary to understand the new method.

Define:

- notation,
- assumptions,
- problem setup,
- input/output,
- system state,
- baseline formulation.

If the project contains equations, establish notation before presenting the new equation.

Avoid textbook-level material that knowledgeable reviewers already know.

---

# PHASE 14 — RELATED WORK

Organize related work by conceptual categories, not paper-by-paper summaries.

Example style:

### Adaptive Retrieval

Several works address ...

### Process Supervision

Another line ...

### Counterfactual Learning

...

Then explain the exact gap between these lines and ours.

For every related-work claim include a real citation.

Do not invent references.

Prefer primary papers.

End related work with a precise statement:

> Unlike prior work that \_\_\_\_\_\_, our method \_\_\_\_\_\_.

---

# PHASE 15 — PROPOSED METHOD

This section must be the technical center of the paper.

Explain:

## Motivation

Why the mechanism is needed.

## Baseline

How current systems operate.

## Failure

Exactly what is wrong.

## Key Insight

What changed our approach.

## Proposed Mechanism

Step by step.

## Mathematical Formulation

Define equations.

## Algorithm

Provide pseudocode.

## Complexity

Time/memory/LLM-call overhead where relevant.

## Design Decisions

Why this design was selected over alternatives.

## Expected Behavior

What should happen if the hypothesis is correct.

Avoid unnecessary complexity.

---

# PHASE 16 — ARCHITECTURE DIAGRAM

Use the supplied architecture diagram if accurate and publication-quality.

If necessary:

- recreate it cleanly,
- simplify it,
- improve labels,
- ensure fonts are readable,
- ensure it works in grayscale,
- remove decorative elements,
- use vector PDF/SVG where possible.

Create a clear figure caption explaining:

- inputs,
- core components,
- proposed mechanism,
- outputs.

The diagram should support the paper's technical argument, not merely decorate the paper.

---

# PHASE 17 — EXPERIMENTAL METHODOLOGY

Write enough detail for reproducibility.

Include:

### Research questions

### Datasets

### Data preprocessing

### Models

### Model versions

### Prompts where relevant

### Hyperparameters

### Baselines

### Experimental conditions

### Number of examples

### Number of repeated runs

### Seeds

### Temperature

### Decoding settings

### Hardware

### API/model provider if applicable

### Software libraries

### Evaluation metrics

### Statistical methodology

### Cost/compute

### Reproducibility controls.

Do not omit settings that could materially affect results.

---

# PHASE 18 — FAIR BASELINE COMPARISON

Every baseline comparison must be defensible.

Check:

- same dataset,
- same model where possible,
- same token budget,
- same number of attempts,
- same tools,
- same compute budget,
- same stopping criteria,
- same preprocessing.

If perfect matching is impossible, state the difference.

Do not create an unfair comparison to strengthen our method.

---

# PHASE 19 — RESULTS SECTION

The Results section should present evidence, not interpretation-heavy storytelling.

For each research question use:

### RQ / Hypothesis

### Experiment

### Result

### Key numerical finding

### Table/Figure.

Use concise prose.

Example STYLE:

> Method A achieved X while baseline B achieved Y, corresponding to a relative improvement of Z%.

Only if those numbers are verified.

Do not repeat entire tables in text.

Highlight the most meaningful findings.

---

# PHASE 20 — SELECT THE BEST RESULT TABLES

Create publication-quality tables.

Prioritize:

### Main Comparison Table

Our method vs strongest baselines.

### Efficiency Table

If compute/cost matters.

### Ablation Table

Shows which components matter.

### Robustness / OOD Table

If tested.

### Failure Analysis Table

If informative.

Do not overload the paper with redundant tables.

Move secondary results to appendix.

Use:

\toprule
\midrule
\bottomrule

with `booktabs`.

Avoid vertical table lines unless required.

Bold the best result only when meaningful.

Underline second-best only if useful and conventional.

Include direction arrows:

Accuracy ↑

Cost ↓

Latency ↓.

---

# PHASE 21 — RESULT FIGURES

Use supplied result images if they are scientifically useful.

Recreate plots from raw data when possible instead of using screenshots.

Preferred plots may include:

- bar chart,
- line chart,
- scatter plot,
- box plot,
- calibration plot,
- confusion matrix,
- failure distribution,
- accuracy-cost frontier.

Do not create misleading axes.

Always show:

- units,
- legend,
- axis labels,
- uncertainty/error bars where meaningful.

Use publication-quality vector figures where possible.

---

# PHASE 22 — STATISTICAL VALIDITY

If repeated runs exist, calculate where appropriate:

- mean,
- standard deviation,
- standard error,
- confidence intervals,
- effect sizes,
- appropriate statistical tests.

Do NOT claim statistical significance unless calculated correctly.

If sample size is too small, state that and avoid false significance claims.

---

# PHASE 23 — ABLATION STUDY

If the proposed method has multiple components, determine whether available experiments isolate them.

Construct:

Baseline

- Component A
- Component B
- A+B

Full Method

where evidence permits.

Explain what each ablation demonstrates.

If ablations were not run, do NOT fabricate them.

State them as future experiments if necessary.

---

# PHASE 24 — FAILURE ANALYSIS

A world-class paper should show understanding of where the method fails.

Analyze failure cases.

Do not undermine the central contribution unnecessarily, but explain meaningful boundaries.

For example:

- specific task types,
- data conditions,
- model sizes,
- noise,
- cost conditions,
- edge cases.

Explain whether these failures:

1. contradict the mechanism,
2. reveal a boundary condition,
3. indicate implementation limitations,
4. suggest future research.

---

# PHASE 25 — DISCUSSION

Interpret the results.

Answer:

### Did the main hypothesis survive?

### Why might the method work?

### Which result is most surprising?

### Which result is most important?

### What does this teach us beyond the benchmark?

### What broader research implication follows?

Avoid repeating Results.

The Discussion should explain the science.

---

# PHASE 26 — LIMITATIONS

Write limitations honestly but carefully.

Include only real limitations.

Possible categories:

- model scale,
- number of datasets,
- stochasticity,
- compute limitations,
- synthetic tasks,
- API dependency,
- limited domain coverage,
- theoretical analysis not yet complete,
- hardware constraints.

For each limitation state whether it likely affects:

- internal validity,
- external validity,
- generalizability,
- practical deployment.

Where possible explain mitigation.

Do not write limitations in a way that destroys claims unnecessarily.

Narrow the claim to what the evidence actually supports.

---

# PHASE 27 — THREATS TO VALIDITY

Where appropriate separate:

### Internal validity

Are observed differences truly caused by the method?

### External validity

Will results generalize?

### Construct validity

Do the metrics actually measure the intended property?

### Statistical validity

Are the results sufficiently powered?

This is especially valuable for empirical AI research.

---

# PHASE 28 — CONCLUSION

The conclusion should answer:

1. What problem was studied?
2. What mechanism was introduced?
3. What did experiments show?
4. Why does it matter?
5. What is the next research step?

Do not introduce new results in the conclusion.

Avoid hype.

---

# PHASE 29 — PAPER NAME AND MECHANISM NAME

Find a memorable but academically serious name.

The project/method name should:

- reflect the actual mechanism,
- be easy to remember,
- not conflict with major existing methods,
- be easy to pronounce,
- work naturally in sentences.

Example:

> “We introduce X, a \_\_\_\_\_\_ mechanism for \_\_\_\_\_\_.”

Search current literature before finalizing the name.

Do not select a name already heavily associated with another AI method.

---

# PHASE 30 — REFERENCES

Create a complete BibTeX database:

`references.bib`

Every citation must correspond to a real paper/source.

Verify:

- title,
- authors,
- year,
- venue,
- DOI/arXiv/OpenReview details where appropriate.

Prefer authoritative/primary sources.

Do not cite blogs for scientific claims when original papers exist.

Use IEEE citation style.

---

# PHASE 31 — FIGURE MANAGEMENT

Create:

`figures/`

with clean filenames such as:

architecture.pdf

main\_results.pdf

ablation\_results.pdf

efficiency\_comparison.pdf

failure\_analysis.pdf

Do not use names such as:

Screenshot\_2026\_08\_23\_final2.png.

Where source screenshots must be retained, put them under:

`figures/raw/`

and create publication-ready versions separately.

---

# PHASE 32 — TABLE MANAGEMENT

Where practical, store important tables as separate LaTeX fragments:

`tables/main_results.tex`

`tables/ablations.tex`

`tables/efficiency.tex`

This keeps `main.tex` clean.

---

# PHASE 33 — COMPLETE LATEX PROJECT

Generate an actual complete folder.

Preferred structure:

paper/
│
├── main.tex
├── references.bib
├── README.md
├── Makefile
│
├── sections/
│ ├── 01\_introduction.tex
│ ├── 02\_background.tex
│ ├── 03\_related\_work.tex
│ ├── 04\_method.tex
│ ├── 05\_experiments.tex
│ ├── 06\_results.tex
│ ├── 07\_discussion.tex
│ ├── 08\_limitations.tex
│ └── 09\_conclusion.tex
│
├── figures/
│ ├── architecture.pdf
│ ├── main\_results.pdf
│ ├── ablations.pdf
│ └── ...
│
├── tables/
│ ├── main\_results.tex
│ ├── ablations.tex
│ └── ...
│
├── supplementary/
│ ├── appendix.tex
│ ├── additional\_results.tex
│ ├── prompts.tex
│ ├── hyperparameters.tex
│ └── reproducibility.tex
│
└── source\_material/
└── README explaining which provided artifact supports each paper element.

Adapt if a simpler structure is better.

---

# PHASE 34 — IEEE LATEX REQUIREMENTS

Use:

\documentclass[conference]{IEEEtran}

unless a specific IEEE journal format is requested.

Use reliable packages only.

Potential packages:

amsmath
amssymb
booktabs
graphicx
multirow
tabularx
algorithm
algpseudocode
hyperref
cleveref if compatible
xcolor only if required.

Avoid package conflicts.

Ensure compilation succeeds.

---

# PHASE 35 — ALGORITHM ENVIRONMENT

If the method includes an algorithm, provide publication-quality pseudocode.

Example structure:

Algorithm 1: Proposed Training/Inference Procedure

Input: ...

Output: ...

Initialization ...

For each ...

Compute ...

Update ...

Return ...

Pseudocode must match the actual implementation.

---

# PHASE 36 — EQUATION AUDIT

Review every equation.

Check:

- variables defined before use,
- dimensions consistent,
- indices consistent,
- symbols not reused,
- equations referenced in prose,
- proposed term actually matches implementation.

Create a notation table only if necessary.

---

# PHASE 37 — FIGURE/TABLE AUDIT

For every figure and table ask:

> What scientific question does this answer?

If no clear answer:

remove it or move it to supplementary material.

Every figure must be referenced in the text.

Every table must be referenced.

Every caption must be understandable without reading the full body text.

---

# PHASE 38 — LINE-BY-LINE MANUSCRIPT AUDIT

After completing the first full draft, review EVERY paragraph.

For each sentence ask:

### Is this scientifically correct?

### Is it supported?

### Is the citation appropriate?

### Is the wording stronger than the evidence?

### Is it redundant?

### Is it clear?

### Is terminology consistent?

### Could a reviewer misunderstand it?

### Does it contribute to the argument?

Rewrite anything weak.

Then perform a second pass specifically for:

- grammar,
- academic tone,
- logical transitions,
- concision,
- repetition,
- undefined acronyms,
- ambiguous pronouns,
- inconsistent terminology.

---

# PHASE 39 — CLAIM AUDIT

Search the manuscript for words such as:

- first,
- novel,
- significant,
- substantially,
- superior,
- outperform,
- state-of-the-art,
- robust,
- general,
- causal,
- efficient,
- scalable.

Check EVERY occurrence.

Require evidence.

Replace unsupported strong words.

---

# PHASE 40 — REVIEWER #2 ATTACK

Pretend this paper has just been submitted.

Write the strongest possible rejection review.

Attack:

- novelty,
- methodology,
- experiment design,
- baselines,
- statistical validity,
- compute fairness,
- datasets,
- generalization,
- implementation,
- theoretical justification,
- presentation,
- limitations,
- reproducibility.

Give an initial hypothetical score:

1 — Strong Reject
2 — Reject
3 — Borderline Reject
4 — Borderline
5 — Borderline Accept
6 — Accept
7 — Strong Accept.

Then improve the manuscript to address every valid criticism that can be addressed using existing evidence.

Do NOT invent new experiments to fix gaps.

If a missing experiment is essential, clearly flag:

`REQUIRED BEFORE SUBMISSION`

and explain exactly what must be run.

---

# PHASE 41 — REVIEWER #3 NOVELTY ATTACK

Act as a literature specialist trying to show:

> “This contribution already exists.”

Search again.

Compare mechanism-by-mechanism.

If novelty survives, sharpen the difference.

If not, reduce or reformulate claims.

Never conceal overlapping work.

---

# PHASE 42 — REVIEWER #4 EXPERIMENT ATTACK

Act as an experimental-methodology expert.

Ask:

- Is baseline selection fair?
- Are run counts sufficient?
- Are random seeds controlled?
- Is the sample size large enough?
- Is there leakage?
- Are conditions confounded?
- Are token/compute budgets matched?
- Is statistical analysis appropriate?
- Are conclusions broader than experiments?

Correct all issues that can be corrected from available data.

---

# PHASE 43 — ACCEPTANCE-READINESS AUDIT

Score the manuscript /10 for:

Research problem clarity

Research gap

Novelty

Technical depth

Method clarity

Experimental rigor

Baseline quality

Statistical quality

Result strength

Ablation quality

Reproducibility

Writing quality

Figure quality

Related-work quality

Claim defensibility

Overall paper coherence.

Anything below 8/10 should receive concrete fixes.

Do NOT artificially inflate the scores.

---

# PHASE 44 — DETECT MISSING EXPERIMENTS

After writing the paper determine whether any experiment is necessary before serious submission.

Classify missing experiments:

### CRITICAL

Paper should not be submitted without it.

### IMPORTANT

Significantly strengthens paper.

### OPTIONAL

Useful but not necessary.

For each give:

Research question
Setup
Baseline
Metric
Expected cost.

Do not run or invent results unless actual execution capability/data is available.

---

# PHASE 45 — DETECT WEAK CLAIMS

Create a private table:

| ClaimEvidenceReviewer RiskAction |
| -------------------------------- |

Possible actions:

KEEP
NARROW
MOVE TO DISCUSSION
MOVE TO FUTURE WORK
REMOVE.

The final manuscript must contain only defensible claims.

---

# PHASE 46 — USE NEGATIVE RESULTS INTELLIGENTLY

Do NOT hide scientifically material negative results.

Instead determine whether they:

- define a boundary condition,
- reveal why the mechanism works,
- motivate an ablation,
- expose a limitation,
- suggest future research.

Minor exploratory failures that are irrelevant to the final research question do not need to occupy main-paper space.

They may be omitted from the narrative or moved to supplementary material as appropriate.

But do not selectively hide evidence that directly contradicts the paper's central claim.

---

# PHASE 47 — PAPER LENGTH

Respect the target venue/page limit.

If no page limit is specified:

prepare a strong IEEE-style conference manuscript around 8–10 pages excluding references where appropriate, plus supplementary material.

Do not inflate length.

Move:

- hyperparameter details,
- additional examples,
- secondary experiments,
- extended proofs,
- raw failure cases,

to supplementary material.

---

# PHASE 48 — REPRODUCIBILITY CHECKLIST

Include:

- dataset names/versions,
- model names/versions,
- software dependencies,
- prompts,
- seeds,
- hyperparameters,
- preprocessing,
- hardware,
- number of runs,
- evaluation scripts,
- cost where relevant.

Create:

`supplementary/reproducibility.tex`

and a human-readable:

`README.md`.

---

# PHASE 49 — README

The LaTeX folder README should explain:

## Paper

Title.

## Compile

Commands.

Example:

`latexmk -pdf main.tex`

or

`pdflatex → bibtex → pdflatex → pdflatex`.

## Directory Structure

[...]

## Figures

Source of each figure.

## Results

Source experiment corresponding to each result.

## Reproducibility

Where configurations/hyperparameters are documented.

---

# PHASE 50 — BUILD AND COMPILE

Actually compile the LaTeX project if tools are available.

Fix:

- missing references,
- missing figures,
- undefined citations,
- overfull boxes,
- table overflow,
- broken equations,
- package conflicts.

Compile repeatedly until:

### ZERO compilation errors.

Minimize warnings.

Inspect the final PDF visually.

---

# PHASE 51 — VISUAL PDF REVIEW

Review every page of the compiled paper.

Check:

- figures readable,
- tables readable,
- equations not clipped,
- captions positioned correctly,
- columns balanced,
- no giant whitespace,
- no overlapping text,
- no broken URLs,
- references formatted correctly,
- headings consistent.

Fix problems.

---

# PHASE 52 — FINAL LANGUAGE PASS

Rewrite anything that sounds:

- AI-generated,
- repetitive,
- exaggerated,
- vague,
- overly promotional,
- unnecessarily complicated.

Prefer clear scientific language.

Avoid:

“groundbreaking”

“revolutionary”

“unprecedented”

“remarkable”

unless extremely well justified.

Let the evidence create impact.

---

# PHASE 53 — FINAL CONTRIBUTION TEST

A reviewer should be able to answer after reading:

### What exact problem is being studied?

### Why isn't existing research sufficient?

### What exactly is new?

### Why should the new mechanism work?

### What experiment tests that claim?

### What result supports it?

### What are its limitations?

### Can I reproduce it?

If any answer is unclear, fix the paper.

---

# PHASE 54 — FINAL PAPER PACKAGE

At completion provide:

1. Complete LaTeX source folder.
2. Compiled PDF.
3. `references.bib`.
4. All publication-quality figures.
5. All table `.tex` files.
6. Supplementary appendix.
7. Reproducibility section.
8. README.
9. Any required algorithm files.
10. A `CLAIM_EVIDENCE_AUDIT.md`.
11. A `SUBMISSION_READINESS.md`.
12. A `MISSING_EXPERIMENTS.md` if anything important remains.

Package everything into:

`<PROJECT_NAME>_IEEE_Paper.zip`

---

# PHASE 55 — CLAIM\_EVIDENCE\_AUDIT.MD

Create:

# Main Claim

[...]

# Supporting Evidence

[...]

# Secondary Claims

[...]

# Evidence

[...]

# Claims Removed/Narrowed

[...]

# Reason

[...]

# Remaining Weaknesses

[...]

This file is for authors, not necessarily submission.

---

# PHASE 56 — SUBMISSION\_READINESS.MD

Provide:

## Current Paper Verdict

Choose:

NOT READY

MAJOR EXPERIMENT REQUIRED

PROMISING DRAFT

STRONG DRAFT

SUBMISSION-READY WITH MINOR POLISH

SUBMISSION-READY

## Strongest Aspect

[...]

## Biggest Risk

[...]

## Closest Competing Work

[...]

## Most Important Missing Experiment

[...]

## Suggested Venue Category

[...]

## Reviewer Acceptance Risks

[...]

Do NOT guarantee acceptance.

---

# PHASE 57 — FINAL OUTPUT TO ME

After producing the files, summarize:

# FINAL PAPER

**Title:** [...]

**Method/Project Name:** [...]

**Central Problem:** [...]

**Research Gap:** [...]

**Main Contribution:** [...]

**Strongest Result:** [...]

**Main Experiment:** [...]

**Closest Prior Work:** [...]

**Primary Novelty:** [...]

**Biggest Limitation:** [...]

**Recommended Submission Direction:** [...]

**Paper Readiness:** [...]

Then give me the downloadable ZIP and compiled PDF.

---

# SPECIAL INSTRUCTION — USE ALL PREVIOUS PROJECT CONTEXT

Do NOT force me to explain the project again if the information already exists in:

- this conversation,
- attached project reports,
- uploaded results,
- images,
- architectural diagrams,
- ZIP experiment folders,
- previous analyses.

Recover and use those materials.

However, raw experimental evidence takes priority over conversational summaries.

---

# SPECIAL INSTRUCTION — RESULT IMAGES

I have images/screenshots showing experiment results.

For EVERY result image:

1. identify the experiment,
2. understand what each axis/value means,
3. associate it with raw data when available,
4. decide whether it belongs in main paper or supplement,
5. recreate it cleanly if needed,
6. write a scientific caption,
7. reference it from the correct section.

Do not simply paste screenshots into the final paper if a clean graph can be reconstructed.

---

# SPECIAL INSTRUCTION — ARCHITECTURE DIAGRAM

I have an architectural diagram.

Verify it against the actual implementation and proposed research mechanism.

If necessary, redraw it into a publication-quality diagram.

The final diagram must clearly distinguish:

- existing/baseline components,
- our proposed mechanism,
- data/control flow,
- training/inference flow where relevant.

---

# SPECIAL INSTRUCTION — EXPERIMENT JOURNEY

I may have performed experiments sequentially while discovering the final mechanism.

Do NOT describe the paper as a diary.

Instead reconstruct the logical scientific sequence:

### Observation / Problem Validation

Does the suspected phenomenon exist?

### Mechanism Experiment

Does our proposed explanation hold?

### Proposed Solution

Does the mechanism improve the problem?

### Component Diagnostic

Which part causes the gain?

### Robustness / Generalization

Does it survive different conditions?

Use actual experiments in the most scientifically coherent order.

---

# SPECIAL INSTRUCTION — BEST POSSIBLE PAPER NAME

Do not keep my current project name automatically.

Analyze:

- mechanism,
- research problem,
- terminology,
- closest literature,
- memorability.

Generate several names privately.

Search for collisions.

Select one professional name.

The academic paper title should be informative rather than promotional.

---

# FINAL REVIEW LOOP

Before final delivery execute this loop:

DRAFT
↓
Evidence Audit
↓
Numerical Verification
↓
Citation Verification
↓
Novelty Attack
↓
Reviewer #2
↓
Methodology Attack
↓
Claim Narrowing
↓
Language Editing
↓
LaTeX Compilation
↓
Visual PDF Inspection
↓
Final Reviewer Simulation
↓
FINAL PAPER

If serious problems remain, fix them.

Repeat until the manuscript is internally consistent and the remaining limitations require new experiments rather than better writing.

---

# ABSOLUTE RULES

Do not invent anything.

Do not manipulate results.

Do not cherry-pick material evidence.

Do not fabricate citations.

Do not hide a result that directly invalidates the central hypothesis.

Do not exaggerate novelty.

Do not call the method SOTA without proper comparison.

Do not confuse a development feature with research novelty.

Do not write generic AI-generated prose.

Do not overfill the introduction with background.

Do not provide equations without defining symbols.

Do not use figures without discussing them.

Do not report percentages without checking calculations.

Do not claim significance without statistical evidence.

Do not make conclusions broader than evaluated conditions.

Do not submit a paper that does not compile.

Do not finish until every major claim has supporting evidence.

---

# ULTIMATE QUALITY STANDARD

The final manuscript should make a skeptical reviewer think:

> “The problem is clear.”

> “The authors understand the literature.”

> “The novelty is precise.”

> “The proposed mechanism makes technical sense.”

> “The experiments actually test the hypothesis.”

> “The comparison appears fair.”

> “The authors understand both the strengths and limitations of their method.”

> “The results are reproducible.”

> “Even if I disagree with part of the interpretation, this is serious research.”

That is the standard.

Now inspect ALL available project material and produce the complete publication-quality IEEE LaTeX paper package.