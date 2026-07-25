# ISSUE-001: Expressive replies can make unsourced factual assertions

**Status:** Open

**Observed:** 2026-07-25

**Scope:** Grounded primary-intent experiment expressive route

## Problem

The expressive route's generated reply can assert a market condition that is
not supplied by authoritative context, while the current lexical policy check
allows it.

## Evidence

- Run `python -m npc.primary_intent_experiment` with the checked-in corpus.
- For `Good afternoon. How is the market treating you?`, the route preserved
  trader and player state but returned: `It's a volatile day, but the momentum
  feels promising. How about you?` The policy check reported `passed`.
- The experiment requires free-form expressive replies not to assert canonical
  facts, commitments, or completed actions.

## Impact

The authoritative trade boundary is demonstrated for the fixed corpus, but the
experiment cannot support its full expressive-dialogue criterion or unlock
Roadmap Outcome 2.

## Open question

What bounded, non-template expressive-output policy can reliably prevent
unsourced factual assertions without making ordinary small talk unusable?

## Routing

- **Requirements:** [grounded primary-intent experiment](../requirements.md#grounded-primary-intent-experiment)
- **Architecture:** [grounded primary-intent experiment](../architecture.md#grounded-primary-intent-experiment)
- **Decision:** [separate LLM semantic interpretation from NPC authority](../decisions.md#2026-07-25-separate-llm-semantic-interpretation-from-npc-authority)
- **Roadmap:** [Outcome 1](../roadmap.md#1-establish-the-grounded-primary-intent-boundary)
- **Task:** `None`

## Resolution

Pending.
