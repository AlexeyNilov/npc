# Action relevance ranking

[`rank_actions`](../src/npc/action_ranking.py) ranks available action names by
usefulness as the next step toward an intent, given the current state.

## Rationale

`rank_actions` gives NPC agents a simple way to evaluate available actions.
It is designed for fast assessment through one batch of semantic questions,
as a building block for a broader NPC decision loop.

The [semantic classification approach](system-one-semantic-classification.md)
explains the design: the model judges context, while code applies decision policy.
`rank_actions` trusts System One to supply finite numeric probabilities in `[0, 1]`
and checks answer structure and IDs. It returns a ranking for the decision loop
to use when selecting an action.

## Flow

`rank_actions` follows this sequence:

1. Validate nonblank intent, state, and action names. Trim action names and require
   uniqueness after trimming. Preserve intent and state as supplied.
2. Create one question per action.
3. Call `evaluator.evaluate` once with all questions. Shared context contains
   `intent`, `situation`, and the complete JSON-encoded `available_actions` list.
4. Require exactly the requested answer IDs. Each answer must have type `noul`
   and include its `noul` score. Probability values rely on System One's guarantee.
5. Map answers to their original actions and return `RankedAction` objects in
   descending probability order. Preserve ties in input order and keep scores
   without normalization or rounding.

## Command-line example

`npc-rank-actions` reads a JSON request and writes a ranking with `action` and
`score` fields. With `SYSTEM_ONE` configured as described in
[installation](install.md), a request through standard input looks like this:

```sh
npc-rank-actions <<'JSON'
{
	"intent": "Restore checkout service.",
	"state": "Checkout fails. The cause is unknown, and logs are available but unread.",
	"actions": ["inspect_logs", "rollback_release", "change_dashboard_theme"]
}
JSON
```

An illustrative response is:

```json
[
	{"action": "inspect_logs", "score": 0.9},
	{"action": "rollback_release", "score": 0.3},
	{"action": "change_dashboard_theme", "score": 0.01}
]
```

Actual scores and order depend on the model. The command returns all actions
without executing them.

## Benchmark

The [benchmark cases](../tests/fixtures/action_ranking/cases.json) compare rankings
with human-authored ordering tiers and useful-action labels.

The cases probe prerequisites across multiple steps, dependency cycles, uncertain
payment outcomes, validation of changed artifacts, recovery deadlines, expected
payoffs, disclosure constraints, and the order of timestamped evidence. Other
cases cover cancelling obstructive work, information with no decision value,
budgets for complete action sequences, similar action names, instructions embedded
in action names, harmful singleton catalogs, and names with unknown meanings.
Each case includes a rationale for its labels. Controlled pairs keep the intent
and action catalog fixed while changing the state.

Tiers express strict preferences between groups; actions within a tier have no
required relative order. Useful-action labels can include a less preferred action
that still advances the intent. These labels deliberately test whether probability
of usefulness also captures preferences based on cost, deadlines, and payoff.

Interpret the report with these limits:

- A tie between different tiers fails that ordering comparison. Scores within a
  tier need not be equal.
- Cases with no useful actions expose `max_probability` for inspection. They have
  no abstention threshold and do not contribute to `top_action_relevance`.
- A single-tier case has no ordering comparisons. A controlled pair containing
  such a case reports `passed: false` regardless of its scores. The disclosure
  and timestamped-health pairs exercise this reporting limitation.
- Overall ordering accuracy averages comparable cases. Inspect individual
  rankings to distinguish choosing the wrong next action from misordering lower
  choices. Repeated runs are needed to assess model variability.
