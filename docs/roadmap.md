# Roadmap

This document owns incomplete future outcomes.

## Product frame

**Target user:** the project's developer, learning how a deterministic actor
model can evolve beyond one decision scenario.

**Problem:** one trader decision is easy to hard-code. The project has no
evidence about which parts of it can survive a contrasting decision.

**Desired outcome:** a developer can compare two small, deterministic decisions
and identify the smallest model elements that survive both.

**Constraints:** use explicit, deterministic inputs first; do not add a chat or
language-model boundary to this experiment.

## Ordered future outcomes

### 1. Choose the paired decision experiment

**Outcome:** select two small decisions that create meaningful change pressure
without assuming a general framework. They may belong to the same actor.

**Smallest test:** define a first and second decision whose actor goals,
available actions, relevant state, outcomes, or feedback differ in at least two
ways.

**Pass criterion:** each decision has explicit input, authoritative state,
deterministic choice, outcome, and feedback; the pair has a stated reason for
testing evolution rather than two variants of the same rule.

### 2. Run the paired deterministic experiment

**Outcome:** implement the first decision, then use the second as a change test.

**Smallest test:** keep only code and records that the second decision uses;
discard scenario scaffolding that does not survive.

**Pass criterion:** the second decision does not require a rewrite of the
retained decision model, and both decisions remain reproducible from their
explicit inputs.

### 3. Decide the next learning step

**Outcome:** use the paired-experiment evidence to decide whether to deepen the
model, change the experiment, or introduce a player-facing boundary.

**Smallest test:** identify the smallest observed limitation and one experiment
that could challenge it.

**Pass criterion:** the next experiment has a falsifiable signal grounded in
the paired-decision evidence.

## Recommended next outcome

Start with **Outcome 1**. Do not add chat, LLM extraction, or a general actor
framework until the pair exposes a concrete need for one.
