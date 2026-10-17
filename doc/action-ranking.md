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

The [benchmark cases](../tests/fixtures/action_ranking/cases.json) use the same
`intent`, `state`, and `actions` inputs as `npc-rank-actions`. Each case adds an
`id` and `relevant_actions`. Listed actions are labeled useful now; all other
available actions are labeled not useful. Labels never enter model requests.

The benchmark calls `rank_actions` once per case, preserving its single batch of
one question per action. It reports the ranking, labels, timing, model metadata,
and a Brier score: the mean of `(probability - label) ** 2`, where useful is 1 and
not useful is 0. A score of 0 is perfect; 1 is maximally wrong. The overall score
weights every evaluated action equally. Empty catalogs and failed requests have
no score; failures are counted separately.

The report's `elapsed_seconds` measures total evaluation and scoring time,
including failed requests. Each result also has its own `elapsed_seconds`.
Total time excludes loading the fixture and writing the report.

There are no ordering tiers or usefulness cutoffs. Multiple actions can be useful,
even when their costs or expected benefits differ. Cases where every action is
useless measure whether scores stay near zero, including singleton catalogs.

The scenarios probe prerequisites, uncertain retries, stale evidence, deadlines,
budgets, disclosure constraints, misleading names, and embedded instructions.
The labels are human judgments about the supplied context. Inspect individual
rankings and repeat runs to assess failures and model variability.

### Model comparison

User-supplied runs use `tests/fixtures/action_ranking/cases.json` and prompt
version `action-relevance-v3`. Compare Brier scores and total times only across
runs with the same evaluated actions. Lower values are better.
Times describe individual runs, not averages. Hardware and server versions were
not recorded. Each run has 40 cases. Complete runs evaluate 119 actions.

| Model | Run time (UTC) | Errors | Brier score | Total time (s) |
| --- | --- | ---: | ---: | ---: |
| `ggml-org/Laya-GGUF:Q8_0` | 2026-10-17 21:33:09 | 0 | 0.459959 | 2.165 |
| `ggml-org/Clef-Flash-GGUF:Q4_K_M` | 2026-10-17 21:36:49 | 0 | 0.026349 | 11.024 |
| `LiquidAI/d1-3B-GGUF:Q8_0` | 2026-10-17 21:37:57 | 0 | 0.049221 | 3.322 |
| `ggml-org/Kev-4B-GGUF:Q4_K_M` | 2026-10-17 21:38:32 | 0 | 0.028099 | 5.905 |
| `ggml-org/lev-GGUF:Q4_K_M` | 2026-10-17 21:40:03 | 0 | 0.050921 | 6.362 |

The first Clef-Flash run failed on 36 cases. Its Brier score covers only 5 actions,
so its score and total time do not establish better accuracy or speed than Laya.
The server reported an 830-token input exceeding its 512-token physical batch.
The [Clef-Flash launch script](../scripts/start_clef_flash.sh) now sets both
`--batch-size` and `--ubatch-size` to 2048. The second Clef-Flash run uses this
configuration and completes without errors.

Among complete runs, Clef-Flash has the lowest Brier score at 0.026349.
Kev-4B is close at 0.028099 and takes about 46% less total time.
d1-3B has a higher Brier score of 0.049221 but finishes in 3.322 seconds.
Laya is fastest at 2.165 seconds, with the highest Brier score of 0.459959.
lev has a higher Brier score and takes longer than both Kev-4B and d1-3B in these
runs.
