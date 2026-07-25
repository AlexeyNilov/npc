# ISSUE-001: Social dialogue is repetitive after authority hardening

**Status:** Deferred

**Observed:** 2026-07-25

**Scope:** Deferred terminal trader playtest, non-economic conversation turns

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
- After the actor-loop milestone, a live playtest repeated `What is your
  name?` three times and received `A warm, patient expression. No supported
  trade was completed.` each time. This rendering proves that the local model
  supplied a non-null candidate that failed deterministic validation; it did
  not reach the supported identity response. The capability therefore works
  with a supplied valid candidate but is not yet repeatable through the live
  language-model boundary.

## Impact

The first trader demonstration cannot yet show the engaging social interaction
in the project vision, even when its authoritative economic behavior is safe.

## Open question

Will the established reusable authority flow make the trader's bounded social
responses meaningfully distinct in a repeatable player-facing playtest?

## Routing

- **Decision:** [Start evolution testing with paired deterministic decisions](../decisions.md#2026-07-25-start-evolution-testing-with-paired-deterministic-decisions)
  defers the conversational runtime.
- **Roadmap:** [Outcome 1: Choose the paired decision experiment](../roadmap.md#1-choose-the-paired-decision-experiment)
  must identify the next evidence-bearing decision work before conversation is
  reconsidered.
- **Task:** None.

## Resolution

Deferred, not resolved. The conversational runtime was removed because it did
not provide useful evidence about whether the decision model can evolve. Reopen
this issue only after the paired decision experiment identifies a justified
player-facing boundary.
