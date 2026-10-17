# Action relevance ranking

[`rank_actions`](../src/npc/action_ranking.py) ranks available action names by
usefulness as the next step toward an intent, given the current state.

## Rationale

System One judges contextual usefulness. `rank_actions` validates inputs and
responses, preserves action identity, and sorts the results.

## Flow

`rank_actions` follows this sequence:

1. Validate nonblank intent, state, and action names.
2. Create one question per action.
3. Call `evaluator.evaluate` once with all questions. Shared context contains
   `intent`, `situation`, and the complete JSON-encoded `available_actions` list.
4. Require exactly the requested answer IDs. Each answer must have type `noul`
   and a finite numeric probability in `[0, 1]`.
5. Map answers to their original actions and return `RankedAction` objects in
   descending probability order. Preserve ties in input order and keep scores
   without normalization or rounding.

## Benchmark

The [benchmark cases](../tests/fixtures/action_ranking/cases.json) compare rankings
with human-authored ordering tiers and useful-action labels. 
