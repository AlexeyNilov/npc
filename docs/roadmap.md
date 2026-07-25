# Roadmap

This document owns incomplete future outcomes. It orders evidence-bearing
outcomes, not coding activities or a list of possible abstractions.

## Product frame

**Target user:** the project's developer, learning whether a deterministic
actor model can produce autonomous behavior that survives meaningful change.

**Relevant evidence:** [the deterministic trader offer evaluator record](evidence/2026-07-25-trader-offer-evaluator.md)
owns the observed result and limits of the current scenario.

**Problem:** the project cannot yet decide whether the vision's actor loop is a
useful model or merely labels around scenario-specific rules. A paired decision
test alone cannot answer that question.

**Evidence milestone:** a developer can run and inspect a deterministic trader
simulation in which an explicit goal and perceived world event cause an action
without a player request; the action's outcome becomes feedback that changes a
later decision.

**Constraints:** use checked-in, deterministic inputs and authoritative state.
Do not add chat, an LLM boundary, persistence, or a general simulation framework
until evidence from the milestones below justifies one.

## Ordered future outcomes

### 1. Demonstrate one autonomous goal-feedback loop

**Hypothesis:** an explicit trader goal, authoritative perception, deterministic
choice, action outcome, and retained feedback can produce a replayable,
actor-initiated decision that materially affects the trader's next decision.

**Outcome:** a developer can inspect a fixed, multi-step trader timeline. At
least one action is triggered by an authoritative world event or time step, not
by a player proposal. Its outcome is retained, and replaying the later decision
with and without that feedback yields different deterministic choices.

**Smallest test:** use the planned
[autonomous-restock experiment record](evidence/2026-07-25-trader-autonomous-restock.md).
It uses one trader goal and a minimal world event—an inventory shortage that
causes a restock attempt—then makes the result of that attempt relevant to a
later restock choice. Keep the precise event and action contract in the record
rather than prematurely standardizing them in a framework.

**Support criterion:** identical checked-in inputs reproduce the full causal
trace: reality, perception, goal or intent, action, outcome, feedback, and the
changed later choice. The trace makes clear why the actor acted without a player
request.

**Rejection criterion:** the scenario requires hidden or ad hoc state, feedback
does not affect a later choice, or the only meaningful decision remains a
player-request evaluator. Record the result; do not add an actor-loop
abstraction merely to preserve its labels.

**Decision unlocked:** whether there is evidence to apply reuse pressure to a
small candidate actor model, or whether the project should change the hypothesis
before building further.

### 2. Apply reuse pressure with a contrasting decision contract

**Precondition:** Outcome 1 has support evidence and a completed experiment
record.

**Hypothesis:** the minimum elements that made the autonomous loop observable—
authoritative reality, goal-relevant state, perception, choice, outcome, and
feedback—also serve a contrasting trader decision without trader-action
branches in any proposed shared boundary.

**Outcome:** a developer can compare the autonomous action with a contrasting
contract, such as responding to a player offer, and identify exactly which
model elements both use and which belong only to a scenario.

**Smallest test:** run the existing offer-evaluation behavior or another bounded
reactive decision through the candidate model only after Outcome 1. Retain only
elements that both traces require. Do not require the two scenarios to share a
policy or domain vocabulary.

**Support criterion:** both traces are deterministic and inspectable; shared
elements need no trader-action-specific branches; scenario policy and rendering
remain outside the shared candidate.

**Rejection criterion:** reuse requires a general framework, hidden coupling,
or branches that exist only to make the second case fit. Keep the evidence and
return to a narrower experiment or explicitly retain two scenario-specific
flows.

**Decision unlocked:** whether to retain a small, evidence-backed actor-model
candidate or stop treating the common structure as durable.

### 3. Make the model-direction decision

**Precondition:** the first two experiment records are complete, including
negative or inconclusive results.

**Outcome:** make one explicit choice: retain the smallest supported actor
model, run a changed hypothesis, or narrow the project to deterministic
scenario engines.

**Smallest test:** compare the two traces and records. Name the observed common
elements, unsupported assumptions, and the next falsifiable question.

**Pass criterion:** the decision cites experiment evidence, has a stated scope
and rejection condition, and does not preserve code or expand scope because of
prior effort.

### 4. Introduce a player-facing boundary only when it tests the model

**Precondition:** Outcome 3 retains a supported actor-model candidate and
identifies a player-facing question that deterministic traces cannot answer.

**Outcome:** determine whether conversation or another interface makes the
actor's goal-driven, state-grounded choices understandable and engaging without
becoming an authority path.

**Smallest test:** define a repeatable playtest whose authoritative actions and
state transitions use the validated model. Treat language-model output only as
untrusted input or bounded presentation.

**Pass criterion:** the interface makes a specific actor behavior more
observable to the developer; it neither authors authoritative choices nor hides
whether the underlying model succeeded.

## Recommended next outcome

Start with **Outcome 1**. The planned experiment record gives it a falsifiable,
bounded definition; prepare implementation work only from that record. Do not
code a reusable loop, add a second interface, or revive chat before the first
autonomous goal-feedback demonstration is reviewed.
