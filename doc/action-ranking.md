# Action relevance ranking

[`rank_actions`](../src/npc/action_ranking.py) ranks available action names by
usefulness as the next step toward an intent, given the current state.
The caller decides whether to execute an action.

## Rationale

System One judges contextual usefulness. Python owns input validation, action
identity, response validation, and ordering. 

Each action gets a `noul` question, which asks for the probability that a statement
is true. The statement asks whether the action advances the intent directly or
supplies something another useful action needs. The full catalog gives the model
context for those dependencies. The prompt includes costs, completed work,
information gathering, and prerequisites.

For example, inspecting logs can help when a service failure has an unknown
cause. Once the state confirms a faulty release and a ready rollback, rollback
can become the useful next step.

Separate questions allow several useful actions, or none. Scores need not sum
to one. Returning every score leaves selection and abstention policy to the
caller instead of imposing an untested cutoff.

## Flow

`rank_actions` follows this sequence:

1. Validate nonblank intent, state, and action names. Reject duplicate names
   and preserve the supplied text. An empty action sequence returns `[]`
   after validation, without evaluation.
2. Create one question per action with a positional ID such as `action_0`.
   Quote each action name with JSON encoding.
3. Call `evaluator.evaluate` once with all questions. Shared context contains
   `intent`, `situation`, and the complete JSON-encoded `available_actions` list.
4. Require exactly the requested answer IDs. Each answer must have type `noul`
   and a finite numeric probability in `[0, 1]`. Booleans are invalid.
5. Map answers to their original actions and return `RankedAction` objects in
   descending probability order. Preserve ties in input order and keep scores
   without normalization or rounding.

Invalid inputs raise `ValueError`. Invalid answers raise `InvalidEvaluationError`
and prevent the entire ranking from returning. Evaluator failures propagate.
Missing answers never become zero scores or partial results.

## Limitations

Scores estimate next-step relevance, not execution success or the best final
outcome. The module performs no calculations, executes no actions, and verifies
no results. A caller that reassesses after execution must supply updated state.
Action names and supplied context are the model's evidence, so opaque names
and missing facts limit the judgment.

First place does not prove usefulness. Probabilities are not guaranteed to be
calibrated, and the caller owns permissions, arguments, selection, and abstention.
The prompt treats supplied content as data, but that wording does not guarantee
resistance to embedded instructions.

The [benchmark cases](../tests/fixtures/action_ranking/cases.json) compare rankings
with human-authored ordering tiers and useful-action labels. Paired states test
changed prerequisites and completed work. Labels stay outside model requests.
These synthetic development cases do not establish general accuracy or score
calibration. Earlier experiments also found that recognizing useful calculation
did not guarantee the correct numerical decision. The current
`action-relevance-v3` prompt still needs evaluation against those results.
