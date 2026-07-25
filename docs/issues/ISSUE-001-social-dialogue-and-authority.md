# ISSUE-001: Social dialogue is repetitive after authority hardening

**Status:** Routed

**Observed:** 2026-07-25

**Scope:** Terminal trader playtest, non-economic conversation turns

## Problem

The player cannot receive meaningfully responsive social dialogue while the
playtest prevents unsupported player-facing claims about economic state or
completed actions.

## Evidence

- In a live trader playtest, both a greeting and `whats your name?` produced
  `A warm, patient expression.`
- The player-visible response therefore did not distinguish two basic social
  questions or provide the trader's identity.
- In the follow-up playtest, `What is your name?` returned `The trader's name
  is Mara.` with no trade trace, while a greeting still returned the closed
  atmospheric reply `A warm, patient expression.` The supported identity path
  therefore works, but greeting remains non-responsive beyond atmosphere.

## Impact

The first trader demonstration cannot yet show the engaging social interaction
in the project vision, even when its authoritative economic behavior is safe.

## Open question

Will the established reusable authority flow make the trader's bounded social
responses meaningfully distinct in a repeatable player-facing playtest?

## Routing

- **Requirements:** [Stateful conversational trader playtest](../requirements.md#stateful-conversational-trader-playtest)
  defines the currently accepted observable behavior.
- **Architecture:** [Conversational trader playtest](../architecture.md#conversational-trader-playtest)
  records the verified shared authority flow.
- **Decision:** Pending; a player-facing trust model is consequential only when
  an approach is selected.
- **Roadmap:** [Outcome 2: Re-run the bounded trader playtest](../roadmap.md#2-re-run-the-bounded-trader-playtest)
  follows the actor-loop model experiment and remains the social-dialogue
  learning outcome.
- **Task:** None.

## Resolution

Partially addressed: the exact supported name question now has an
authoritative, state-preserving response. The issue remains open because the
reported greeting is still indistinguishable from any other no-extraction turn
with the same flavor, and the complete bounded playtest in the roadmap has not
yet been evidenced.
