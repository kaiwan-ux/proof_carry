# Preliminary Experiment Section for the Proposal

## Preliminary Research Objective

Before developing PortaFlow, we will first determine whether the proposed problem exists empirically. The experiment asks whether a partially executed logical agent workflow can be continued after crossing a framework boundary using only ordinary application state, or whether correctness depends on additional runtime-specific execution semantics.

## Experimental Design

Equivalent deterministic workflows will be represented using LangGraph, CrewAI Flows and Microsoft Agent Framework. The use of deterministic logic in the first phase isolates runtime and continuation semantics from LLM stochasticity. Six workflow patterns are included: linear execution, conditional branching, loops, retry after failure, human approval, and an irreversible external side effect.

At a predefined migration boundary, four continuation strategies are compared: ordinary state transfer, state plus observable execution history, complete restart, and a full-information oracle used only as an experimental upper bound. The oracle is not the proposed PortaFlow method.

## Correctness

Correctness is contract-based rather than based only on final output. A continuation is safe only if all required workflow invariants hold, including preservation of the completed prefix, no repeated irreversible side effects, no skipped required steps, correct branch/loop progress, retry preservation, human-approval preservation and correct termination.

## Main Metric

The primary metric is Safe Continuation Rate (SCR):

`SCR = safe migrations / technically successful migration attempts`

Secondary measures include duplicate-effect rate, completed-step replay, skipped-step rate, approval preservation, retry preservation, termination correctness and technical failure rate.

## Falsification Rule

The research direction will be reconsidered if ordinary application state achieves approximately 95% or higher safe continuation across representative workflows and additional execution semantics provide negligible benefit. If repeatable failures are observed across multiple semantic categories, the missing information will be used to derive the first Portable Continuation Capsule rather than deciding its fields in advance.

## Optional LLM Extension

Only after the deterministic phase will selected workflows be repeated with the same LLM across frameworks. The package is already configured for Groq-hosted `openai/gpt-oss-120b`; this extension is disabled in the primary preliminary experiment.
