# Experiment: YAML-declared LLM perception for one beast

**Status:** Complete

**Date:** 2026-07-28

**Roadmap outcome:** Completed; see the current roadmap.

## Decision unlocked

Determine whether the next roadmap outcome may build observer inspection on a
working mediated-perception proof, while keeping the tested YAML shapes and
LLM contract explicitly non-general.

## Hypothesis

A YAML profile can use two LLM-derived binary actor-owned answers from an
engine-enforced actor-accessible view to select an ordinary beast proposal,
without granting the LLM authority over action details or canonical state.

Assumptions: a deterministic test double can represent the LLM response, and
the initial proof's scenario can explicitly name its visible entity subset.

## Observable behavior

A developer can run automated fixtures that inspect one model request
containing the full question list and only accessible world content. Valid
answers change a rule-selected intent/choice and then reach authoritative
resolution; invalid answers stop before choice, action, outcome, feedback, or
canonical transition. The proof retains no subjective history for later turns.

## Design

- **Authoritative inputs and initial state:** a beast profile with two binary
  questions; a scenario whose visibility declaration names visible entities and
  whose entity list includes an inaccessible fixture entity.
- **Scenario timeline or action contracts:** per turn, engine derives the
  accessible view, sends it and all questions once, validates an exact JSON
  boolean mapping, selects an existing rule, builds an ordinary proposal, and
  calls the existing resolver.
- **Expected trace or outputs:** captured requests exclude hidden content;
  valid answers select perception-dependent rules; rejected, malformed, or
  incomplete responses give a diagnostic perception failure before resolution.
- **Deliberate exclusions:** sensing inference, retries, fallback, subjective
  persistence, LLM action selection, reusable schema, replay, and multi-actor
  behavior.
- **Candidate durable elements and disposable scaffolding:** the verified
  engine mediation and authoritative resolver boundary may be documented in
  Architecture; visible entity lists, exact prompts, strict JSON mapping, and
  `perception_answer` are disposable proof scaffolding.

## Signals and stop rule

- **Support signal:** focused tests prove the full information and authority
  boundary, and the repository check passes.
- **Rejection signal:** a valid proof requires hidden data, model-supplied
  action details, canonical mutation outside `resolve`, or more than one call
  per turn.
- **Inconclusive condition:** the test double cannot establish the request and
  failure contracts without a live external service.
- **Stop rule:** stop when any rejection or inconclusive condition occurs;
  record the observed evidence and route the unaccepted choice rather than
  expanding the proof.

## Result

At task Review, complete every field and set the evidence status to `Review`.
The Technical Lead sets the final status after required review and roadmap
closure.

- **Observed result:** The focused test module passed 17 tests. Captured mocked
  completions receive both profile questions and a view containing `wolf` and
  `berry` but not `hidden_cache`; the prompt excludes action and resolution
  details. Valid boolean mappings select the YAML `perception_answer` rules,
  and an unsupported perception-informed proposal reaches the existing
  resolver and is rejected without state transition. Unavailable, malformed,
  missing, extra, and non-boolean responses produce a diagnostic perception
  failure before selection or resolution.
- **Reproducibility evidence:** `.venv/bin/python -m pytest -q
  tests/test_yaml_beast_proof.py` passes. The tests mock
  `npc.simulation.complete_text`; no network or live LLM is used.
- **Interpretation and limits:** This supports the bounded mediated-perception
  hypothesis only. The visibility entity list, JSON contract, question wording,
  and predicate remain disposable scaffolding; the evidence establishes no
  sensing model, retry policy, subjective state, or reusable interface.
- **Decision or unresolved question created:** No new durable decision. The
  Simplifier review identified that static perception inputs had initially been
  placed in canonical `State`; the accepted correction keeps them in immutable
  noncanonical `PerceptionConfig` input.
- **Canonical follow-up:** Requirements and Architecture record the verified
  behavior, and roadmap outcome 2 is completed.
