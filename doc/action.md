# Action relevance ranking

Given an intent, a textual state, and available action names, return every action
ranked by how relevant it is as the next action toward the intent.

## Flow

1. Validate the inputs.
2. Ask System One one `noul` question per action in a single request:
   “Is this action a relevant next action toward the intent in this situation?”
   Include actions that gather needed information or establish a prerequisite.
3. Validate every returned probability and associate it with its original action.
4. Return all actions sorted by descending probability.

For example, if the intent is to restore checkout and the cause of its failures
is unknown, reading logs is useful. If the state instead confirms a faulty
release and a ready rollback, rolling back becomes the useful next action.

The caller decides what to execute and can rerank after the state changes.

## Contracts

**Inputs:** nonblank intent and state, plus unique, nonblank action names.
Preserve supplied text and exact names. Names must convey enough meaning for a
contextual judgment; opaque identifiers alone provide little evidence.

**Output:** every supplied action appears exactly once, with its original name
and a finite numeric probability in `[0, 1]`. Sort descending and retain input
order for equal probabilities. Preserve scores without normalization or rounding.
An empty action list returns an empty ranking without contacting System One;
intent and state must still be valid.

**Score meaning:** probability that the action is relevant now, including useful
information gathering and prerequisites. It is not the probability of achieving
the goal. Several actions may be relevant, or none; scores need not sum to one.
System One supplies probabilities, with no generated explanation.

**Failures:** reject invalid inputs before evaluation. Reject the whole ranking
if a request fails or any answer is missing, unexpected, incorrectly typed, or
has an invalid probability. Keep input errors, dependency failures, and invalid
responses distinguishable. Return failures explicitly rather than substituting
zero scores or silently truncating inputs.

**Scope:** recommend actions. The caller owns execution, arguments, permissions,
and selection or abstention policy. Input text is context to evaluate, including
any instructions quoted within it; it does not redefine the evaluation task.

## Why this design

Follow the [semantic classification approach](system-one-semantic-classification.md):
System One handles contextual judgment, while ordinary code owns identity,
validation, and ordering. This keeps the result predictable and testable.

Independent yes/no questions allow multiple useful actions and catalogs where
nothing is useful. A forced choice would always select something. Asking about
the next action makes the current state matter, including completed work and
unmet prerequisites. Explicitly including information gathering avoids favoring
premature fixes over useful diagnosis.

Return the full ranking without a default cutoff because relevance probabilities
are not guaranteed to be calibrated. First place alone is insufficient grounds
for execution. A partial ranking is also misleading: an unscored action might
have outranked the returned choices.

Use the [benchmark scenarios](../tests/fixtures/action_ranking/README.md) to compare
rankings with labeled expectations, especially when changing only the state
should change the preferred action. Establish a selection threshold using
representative evaluation data before relying on scores for execution.

## Limitations

Relevance scoring does not reliably optimize numerical outcomes. The ranking
pipeline performs no explicit calculation of costs, profit, or expected value;
it asks the model for a contextual judgment. A score does not establish that the
model calculated or compared the outcomes correctly.

In a grain-trader experiment, buying yielded 235 expected gold and selling
yielded 205. Buying tied selling at the lower future price and beat it at the
higher price, yet the model ranked selling above buying (about 0.82 versus 0.53).
This illustrates how a plausible action can outrank the mathematically better
choice even when the state supplies all necessary numbers and an explicit goal.

When decisions depend on arithmetic, calculate outcomes in ordinary code and
select by the stated objective. Use relevance ranking for contextual judgments
that remain after those calculations.

The [100-evaluation prompt study](experiments/action-ranking-2026-10-17/README.md)
compares the current prompt with five revisions, including research guidance,
outcome comparisons, and examples. None improved the tested development ordering;
the example-based revision regressed on held-out cases. The current prompt is
retained. Explicit missing prerequisites worked better than numerical tradeoffs
in this sample; offering calculation actions alone did not resolve the failures.

See the [System One API contract](system-one-api.md) for protocol details and
[installation](install.md) for configuration.
