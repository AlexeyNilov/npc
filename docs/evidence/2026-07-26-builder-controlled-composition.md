# Experiment: builder-controlled composition

**Status:** Planned

**Date:** 2026-07-26

**Roadmap outcome:** [Builder-controlled composition](../roadmap.md#1-builder-controlled-composition)

## Decision unlocked

Whether the demonstrated builder-facing composition, compatibility, replacement, trace, and replay boundary is sufficient to carry through time into Horizon 2, or whether observed composition failures require the Product Strategist to reconsider the capability sequence or constraints.

## Hypothesis

A builder can compose supplied actor and simulation components through one structurally validated declaration, replace an actor and a rule set separately, and retain a causally complete record that replays without new mediation, without generic engine machinery interpreting clearing-domain meaning.

Assumption: the existing fox/hunter state, proposal, resolution, and feedback meanings are sufficient for the baseline and the hunter-first/fox-first rule contrast.

## Observable behavior

The developer creates a readable baseline declaration for supplied fox, hunter, and hunter-first clearing-rules components; validates, runs, inspects, and replays it. The trace records component names, actor-specific observations and proposals, simulation resolution, feedback, and resulting state. A cautious fox replacement changes only its supplied component and declaration, and a fox-first rules replacement changes only its supplied simulation component and declaration. Each produces an inspectable difference. An invalid pairing names the declaration, relevant actor component, and unpaired known proposal without attempting a semantic diagnosis.

## Design

- **Authoritative inputs and initial state:** the accepted fox/hunter clearing state; supplied actor descriptions and mediation; a supplied simulation that owns filtering, accepted proposal pairings, resolution, transitions, and feedback.
- **Scenario timeline or action contracts:** builder declares components and pairings; engine validates structural contracts; simulation derives separate observations; actors form bounded proposals; simulation resolves; engine records; replay re-derives authority without mediation.
- **Expected trace or outputs:** declaration and component identities, actor-visible inputs and proposals, authoritative decisions/transitions, actor-specific feedback, canonical result, and actionable structural failure provenance.
- **Deliberate exclusions:** semantic compatibility diagnosis, domain-validity checking by the engine, universal proposal/world schemas, persistent time, branching, transport, GUI, CLI, and live-model cost/latency claims.
- **Candidate durable elements and disposable scaffolding:** the generic composition declaration, structural validator, causal recorder, and replay boundary are candidate durable foundation; the clearing actors and two clearing rule sets are supplied experiment components.

## Signals and stop rule

- **Support signal:** all three declarations run and replay with the stated local substitutions, structural failures preserve provenance without semantic inference, and source-variation/withheld-fact tests close the derivation path.
- **Rejection signal:** a substitution needs generic-engine or unrelated actor changes, the engine must interpret domain policy to validate, or replay needs mediation or cannot detect changed recorded authority.
- **Inconclusive condition:** fixtures only show literal final outputs, or the run lacks a local actor or rules substitution, source-variation evidence, or withheld-fact boundary evidence.
- **Stop rule:** evaluate one bounded clearing composition with exactly the baseline and two required substitutions. Do not generalize time, world, proposal, or compatibility semantics.

## Result

At task Review, complete every field and set the evidence status to `Review`. The Technical Lead sets the final status after required review and roadmap closure.

- **Observed result:** Pending.
- **Reproducibility evidence:** Pending.
- **Interpretation and limits:** Pending.
- **Decision or unresolved question created:** Pending.
- **Canonical follow-up:** Pending.
