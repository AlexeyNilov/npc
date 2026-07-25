# Experiment: grounded primary intent

**Status:** Inconclusive

**Date:** 2026-07-25

**Roadmap outcome:** [Outcome 1: Establish the grounded primary-intent boundary](../roadmap.md#1-establish-the-grounded-primary-intent-boundary)

## Decision unlocked

How to broaden authoritative trader capabilities or expressive dialogue without
letting an LLM become a source of trader facts, commitments, state changes, or
durable history.

## Hypothesis

An LLM can propose one useful primary intent from a player message, with
supporting text evidence, while deterministic grounding can route it safely as
authoritative, expressive, or unresolved.

**Assumptions:** a single player message has at most one supported primary
intent in this experiment; the initial authoritative capability is a player
offer to sell one healing herb for a stated price; general small talk can be
expressive without becoming canonical memory.

## Observable behavior

A developer submits one player message and can inspect the candidate primary
intent, evidence, route, validation result, and authoritative outcome when one
exists. One turn results in exactly one of the following:

- a validated sell offer evaluated by the deterministic trader policy;
- an expressive reply with no authoritative state or durable-memory change; or
- an unresolved result with no authoritative state change.

## Design

- **Authoritative inputs and initial state:** the player message; authoritative
  trader and player state; the supported healing-herb offer contract; and the
  defined expressive-dialogue policy.
- **Scenario timeline or action contracts:** one independent player turn. The
  LLM proposes one primary intent and exact supporting text. Deterministic code
  validates the intended capability and any referenced canonical entities before
  evaluating a trade. It routes a purely expressive turn to bounded free-form
  dialogue; unsupported or ambiguous input has no action.
- **Expected trace or outputs:** candidate intent, text evidence, route,
  grounding/validation result, deterministic decision and state transition when
  applicable, and rendered response.
- **Deliberate exclusions:** multiple intents in one message; factual queries;
  other transaction shapes; player-created world facts; general world
  simulation; and durable memory created from expressive dialogue.
- **Candidate durable elements and disposable scaffolding:** candidate elements
  are the primary-intent contract, evidence provenance, authoritative-context
  grounding, route, and audit trace. The initial intent labels, item, prices,
  prompts, response wording, and corpus examples are disposable.

## Signals and stop rule

- **Support signal:** valid trade-offer paraphrases produce only a grounded
  offer; small-talk examples produce no authoritative change; and invented
  trader facts, non-offer mentions, unsupported requests, and multi-intent
  inputs cannot cause a trade or create durable facts. Free-form expressive
  replies do not assert canonical facts, commitments, or completed actions.
- **Rejection signal:** a model interpretation can produce an unsupported
  authoritative action or fact; safety requires all small talk to become
  templates; or multi-intent input is silently treated as fully understood.
- **Inconclusive condition:** the selected LLM cannot produce structured
  candidate intents reliably enough to evaluate the deterministic grounding
  contract.
- **Stop rule:** record the evidence and stop. Do not grant the model more
  authority, add multi-intent parsing, or add a broad world model to compensate.

## Result

Complete at Review.

- **Observed result:** The five-case corpus routed the valid offer through the
  deterministic evaluator, which accepted it and transferred one healing herb
  and four gold. Small talk was expressive with unchanged authoritative state.
  The non-offer mention, invented trader commitment, and mixed message were
  unresolved with unchanged authoritative state. The model initially returned
  JSON in Markdown fences; the experiment parser was corrected to accept one
  enclosing JSON fence before this recorded run.
- **Reproducibility evidence:** Run `python -m npc.primary_intent_experiment`
  with the configured local model and
  `scenarios/grounded_primary_intent.yaml`; the captured 2026-07-25 trace has
  one result for each corpus message. Offline validation tests cover fenced
  JSON, grounded offers, malformed output, ungrounded prices, invented trader
  commitments, multi-intent candidates, and unsafe expressive replies.
- **Interpretation and limits:** The run supports the limited authoritative
  boundary: an LLM-proposed trade did not reach the evaluator without grounded
  player text, and unsupported or multi-intent messages made no authoritative
  change. It does not establish the expressive-dialogue policy. The small-talk
  response asserted that the day was volatile and its momentum promising,
  neither of which came from authoritative context; the lexical policy check
  passed that response. No durable state was created, but the experiment cannot
  yet show that free-form replies avoid unsourced canonical claims.
- **Decision or unresolved question created:** What bounded, non-template
  expressive-output policy can prevent unsourced factual assertions reliably
  enough for this experiment?
- **Canonical follow-up:** [ISSUE-001](../issues/ISSUE-001-expressive-output-unsourced-facts.md).
