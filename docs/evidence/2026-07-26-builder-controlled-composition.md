# Experiment: builder-controlled composition

**Status:** Complete

**Date:** 2026-07-26

**Roadmap outcome:** Completed; see the current roadmap.

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

- **Observed result:** The baseline declaration recorded the named
  hunter-first clearing rules and supplied fox and hunter components, their
  separate shown inputs and proposals, authoritative capture resolution,
  feedback, and resulting state. Replacing only the fox supplied a cautious
  `wait` and changed the outcome; replacing only the rules supplied fox-first
  resolution and let the fox reach food. The deliberately invalid fox pairing
  identified the declaration, component, and `set_trap` proposal without a
  semantic or domain claim.
- **Reproducibility evidence:** Focused tests cover the three declarations,
  structural diagnostic, source-state variation, engine-derived actor input,
  and replay rejection for each retained authority field. `.venv/bin/pytest
  tests/test_composition.py`, `make check`, and `git diff --check` passed at
  Implementer handoff.
- **Interpretation and limits:** Within this one bounded clearing turn, the
  declaration, structural validator, value trace, and replay boundary support
  the Horizon 1 hypothesis. The result does not establish temporal execution,
  branching, universal proposal semantics, or semantic-compatibility
  validation.
- **Decision or unresolved question created:** The evidence supports the
  builder-controlled composition boundary within its stated limits. The Product
  Strategist may evaluate whether it is sufficient to carry into stateful
  execution; no future outcome is implied by this record.
- **Canonical follow-up:** [Strategy](../strategy.md) — Product Strategist
  evaluation of the decision unlocked.
