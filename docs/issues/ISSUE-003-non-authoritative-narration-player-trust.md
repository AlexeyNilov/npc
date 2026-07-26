# ISSUE-003: Free-form narration can mislead the player

**Status:** Open

**Observed:** 2026-07-26

**Scope:** Player-facing non-authoritative fox narration

## Problem

The configured narrator may produce arbitrary concise text from only the
completed fox action. `NARRATOR_INSTRUCTION` protects canonical authority but
does not explicitly discourage invented claims. Although narration cannot
change action, distance, outcome, or feedback, a player can still understand
its flavour as a statement of world fact.

`sample/fox_chat.py` also presents this text with the `Fox:` label, which can
make non-authoritative narration appear to be an authoritative fox utterance.

## Evidence

- The accepted narration decision intentionally permits arbitrary concise
  presentation for expressiveness and implementation simplicity.
- `NARRATOR_INSTRUCTION` says not to choose an action or change world state,
  outcome, or feedback; it does not say to avoid unsupported factual claims.
- The interactive sample prints `Fox: {trace.rendered_text}` without labelling
  the text as narration.

## Impact

Canonical simulation state remains protected, but player trust and
understanding can be harmed by plausible but unsupported narration.

## Open question

What lightest-weight combination of narrator guidance and presentation label
reduces misleading claims without losing the intentionally free-form, concise
player experience?

## Routing

- **Requirements:** [Non-authoritative rendering of completed fox outcomes](../requirements.md#non-authoritative-rendering-of-completed-fox-outcomes).
- **Architecture:** [Non-authoritative rendering of completed fox outcomes](../architecture.md#non-authoritative-rendering-of-completed-fox-outcomes).
- **Decision:** [Render completed actor outcomes with a non-authoritative LLM narrator](../decisions.md#2026-07-25-render-completed-actor-outcomes-with-a-non-authoritative-llm-narrator).
- **Roadmap:** None.
- **Task:** None.

## Resolution

Pending.
