# Roadmap

This document owns incomplete future outcomes. It orders evidence-bearing
outcomes, not coding activities or a list of possible abstractions.

## Product frame

**Target user:** the project's developer, learning whether a deterministic
actor model can turn natural-language player input into grounded NPC behavior
without losing expressive conversation.

**Relevant evidence:** [the deterministic trader offer evaluator record](evidence/2026-07-25-trader-offer-evaluator.md)
owns the observed result and limits of the current scenario.

**Problem:** a language model is the practical semantic interpreter for varied
player input, but it must not invent trader facts, commitments, state changes,
or durable history. The current offer evaluator has no language-facing
perception boundary and no room for safe, free small talk.

**Evidence milestone:** a developer can send one player message to a trader;
the system discovers one primary intent and routes it either through a grounded
authoritative path or an expressive, side-effect-free path.

**Constraints:** start with one player and one primary intent per turn. The one
supported authoritative intent is a player offer to sell one healing herb for a
stated gold price. General world simulation, multiple simultaneous intents,
additional authoritative actions, and durable memory from expressive dialogue
are out of scope.

## Ordered future outcomes

### 1. Establish the grounded primary-intent boundary

**Hypothesis:** an LLM can propose one useful primary intent from player text
while deterministic grounding can prevent unsupported interpretations from
becoming trader facts, commitments, state changes, or durable memory.

**Outcome:** a developer can send one player message and inspect its candidate
intent, text evidence, route, validation result, and authoritative outcome if
one exists. The message has one of three safe results: a grounded trade offer,
an expressive turn, or an unresolved turn with no state change.

**Smallest test:** use the planned
[grounded-primary-intent experiment record](evidence/2026-07-25-trader-grounded-primary-intent.md).
Its fixed corpus includes valid trade-offer paraphrases, ordinary small talk,
mentions that are not offers, invented trader facts, and messages with more
than one meaningful intent. Keep the perception contract bounded to this
primary-intent experiment; do not build a general natural-language framework.

**Support criterion:** a valid trade offer is grounded in exact player text and
authoritative trader/player context before the deterministic evaluator can act.
Small talk and unsupported or multi-intent messages change no authoritative
state or durable memory. Expressive replies may be free-form, but cannot assert
canonical trader facts, a commitment, or a completed action.

**Rejection criterion:** the model can cause an unsupported authoritative
interpretation, the system must turn all dialogue into templates to remain safe,
or a mixed message is silently treated as though the system understood only one
part. Record the result; do not expand the model's authority to compensate.

**Decision unlocked:** how to broaden the supported authoritative intent set or
expressive freedom without weakening grounding.

### 2. Demonstrate stateful trader choices across primary-intent turns

**Precondition:** Outcome 1 has support evidence and a completed experiment
record.

**Hypothesis:** the grounded primary-intent boundary can serve a short
conversation in which authoritative trader state and relevant completed actions
affect a later deterministic choice, while expressive turns remain
non-authoritative.

**Outcome:** a developer can run a repeatable sequence of single-intent player
turns: expressive small talk, an accepted offer, and a later offer whose result
reflects the trader's updated state or goals.

**Smallest test:** retain only authoritative state and completed outcomes needed
for the later decision. Do not promote free-form small-talk content into memory
or require the model to summarize the conversation as fact.

**Support criterion:** the same validated primary intents reproduce the same
authoritative transitions; the later trade decision can be explained from
trader state and goals; expressive turns neither alter state nor introduce
facts that the trader later treats as true.

**Rejection criterion:** relevant history cannot be represented without letting
the model create canonical facts, or the required behavior depends on multiple
intents in a single message. Keep the evidence and defer that expansion.

**Decision unlocked:** whether to add factual queries, another transaction
shape, or multi-intent handling as the next bounded capability.

### 3. Add multi-intent input deliberately

**Precondition:** Outcome 2 has support evidence and the product has chosen the
next authoritative capability to combine with expressive conversation.

**Outcome:** determine whether one message containing an authoritative intent
and expressive content can be split into separately grounded and free-form
paths without silently discarding meaning.

**Smallest test:** use a small corpus of mixed messages. Require an inspectable
intent list, text evidence for each authoritative component, and a clear
unresolved path for ambiguity.

**Pass criterion:** authoritative components remain grounded; expressive
components retain useful freedom; no supported component is silently ignored;
and ambiguity produces no state change.

### 4. Extend the trader's authoritative capability deliberately

**Precondition:** prior outcomes identify a specific player-facing capability
whose value cannot be achieved by the existing sell-offer contract.

**Outcome:** add one bounded authoritative capability, such as a factual query
or a second transaction contract, while preserving the grounded perception
boundary and expressive dialogue policy.

**Smallest test:** define the authoritative facts, player-text evidence, and
state transition or deterministic reply that the new capability requires.

**Pass criterion:** the capability expands useful interaction without granting
the model a new path to invent facts, commitments, or state transitions.

## Recommended next outcome

Start with **Outcome 1**. The planned experiment record gives it a falsifiable,
bounded definition; prepare implementation work only from that record. Do not
add multi-intent interpretation, new authoritative actions, or model-authored
durable memory before the grounded primary-intent boundary is reviewed.
