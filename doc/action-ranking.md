# Action ranking

[`action_ranking.py`](../src/npc/action_ranking.py) provides two approaches for
ranking available actions toward an intent:

- `rank_actions_by_relevance` asks whether each action is a useful next step.
- `rank_actions_by_choice` asks which action is the best next step among the
  supplied candidates.

Both return every candidate as a `RankedAction`, sorted by descending probability
with ties in input order. They preserve raw scores without rounding or
normalization. Neither function executes an action or applies a selection policy.

## Which approach to use

| Decision needed | Preferred approach | Reason |
| --- | --- | --- |
| Determine whether any action is useful | Relevance | All candidates can receive low scores. |
| Identify several useful actions | Relevance | Each candidate has its own usefulness probability. |
| Apply a usefulness threshold or abstain | Relevance | The decision loop can reject every candidate. |
| Select one action from known suitable candidates | Choice | Candidates compete directly within one question. |
| Reduce evaluation latency | Choice | It took about half the time in the measured Kev and Clef runs below. |

Relevance is the default recommendation when the NPC can encounter a catalog
with no useful action. The [semantic classification approach](system-one-semantic-classification.md)
explains the policy boundary: the model judges context, while code decides what
to do with its probabilities. Abstention belongs to the caller; the ranker still
returns every action.

Choice fits a decision where taking one of the supplied actions is already
appropriate. Its probabilities sum to one, even when every action is unsuitable.
A high choice score means preference within this catalog and cannot establish
that the action is useful. Adding or removing candidates can change the scores.
For a singleton, the choice distribution assigns its sole action probability one.

## Relevance evaluation

`rank_actions_by_relevance` constructs one System One `noul` question per action
and sends all questions through one `evaluator.evaluate` call. Each question
asks whether the action advances the intent directly or supplies a prerequisite
for another useful action, considering costs and completed work.

The evaluator returns one probability per question ID. The ranker maps those
IDs back to names and sorts the results. Several actions can score highly;
the scores need not sum to one. A caller can apply a threshold to select several
actions or select none. The benchmark uses 0.5, which is an evaluation policy
rather than a threshold built into the ranker.

## Choice evaluation

`rank_actions_by_choice` constructs one `ChoiceQuestion` containing instructions
and all action names, then calls `evaluator.evaluate_choice` once. The question
asks for the best next step, including information gathering and prerequisites.

The System One adapter derives `action_i` option IDs and supplies action names as
option descriptions. It maps the returned distribution back to names. The ranker
sorts the complete distribution; it does not use the separate winner or confidence
fields. Choice scores express relative preference, so the relevance threshold
and binary Brier score do not apply to them.

Both prompts treat the supplied context and action names as data. Prompt versions
remain separate: `RELEVANCE_PROMPT_VERSION` and `CHOICE_PROMPT_VERSION` identify
`action-relevance-v3` and `action-choice-v1` in benchmark reports.

## Shared inputs and implementation

[`State`](../src/npc/model/evaluation.py) maps string keys to string values.
`intent` describes the goal and `situation` describes current circumstances.
Additional fields, including empty strings, reach the evaluator unchanged.

Both rankers use the same validation, copy state, and add the JSON-encoded
`available_actions` catalog. They leave caller inputs unchanged. Empty catalogs
still require valid context but avoid evaluation. Nonempty catalogs, including
singletons, make one request. The ranking API docstrings own the full input and
error contracts.

`action_ranking.py` owns both public rankers, validation, state preparation,
and stable sorting. [`model/evaluation.py`](../src/npc/model/evaluation.py) owns
the separate `Evaluator` and `ChoiceEvaluator` contracts. This keeps injected
implementations responsible only for the evaluation method their caller needs.

[`SystemOneClient`](../src/npc/system_one.py) implements both contracts, sharing
HTTP configuration, requests, dependency errors, and latest-response model
metadata. Each approach retains its own answer decoder. The adapter requires
exact question and option identities and trusts documented upstream numeric
guarantees. The caller owns and closes the injected HTTP client.

## Python usage

Both APIs use the same inputs and client:

```python
import os

import httpx2

from npc.action_ranking import rank_actions_by_choice, rank_actions_by_relevance
from npc.system_one import SystemOneClient

state = {
    "intent": "Restore checkout service.",
    "situation": "Checkout fails. The cause is unknown; logs are available but unread.",
    "recent_events": "A release just completed.",
}
actions = ["inspect_logs", "rollback_release", "change_dashboard_theme"]

with httpx2.Client() as http:
    evaluator = SystemOneClient(os.environ["SYSTEM_ONE"], client=http)
    relevance = rank_actions_by_relevance(state, actions, evaluator=evaluator)
    choice = rank_actions_by_choice(state, actions, evaluator=evaluator)
```

The output shape is the same, but consumers interpret `probability` according
to the ranking function they called. For relevance, thresholding can return
no candidates. For choice, the first result is the preferred candidate when
the catalog is nonempty.

## Command-line interfaces

`npc-rank-actions-by-relevance` and `npc-rank-actions-by-choice` share one
[CLI implementation](../src/npc/cli/action_ranking.py). Each reads a JSON object
with `state` and `actions` and returns all candidates as `action` and `score`
objects. Their `--help` output owns arguments, defaults, examples, and exit codes.
[Installation](install.md) owns System One endpoint configuration.

For the Python example's inputs, illustrative relevance output is:

```json
[
	{"action": "inspect_logs", "score": 0.9},
	{"action": "rollback_release", "score": 0.3},
	{"action": "change_dashboard_theme", "score": 0.01}
]
```

Illustrative choice output is:

```json
[
	{"action": "inspect_logs", "score": 0.70},
	{"action": "rollback_release", "score": 0.28},
	{"action": "change_dashboard_theme", "score": 0.02}
]
```

Actual scores and order depend on the model.

## Benchmark observations

The [action dataset](../benchmarks/action_ranking.json) contains 60 cases with
local `relevant_actions` labels. [Benchmark documentation](benchmarks.md) owns
methodology and links to the comparison experiment. Command help owns usage.

### Relevance versus choice

These paired runs use the same dataset, with prompts `action-relevance-v3` and
`action-choice-v1`. Top-action accuracy and mean reciprocal rank include the
52 cases with at least one useful action. All requests succeeded.

| Model | Approach | Useful action first | Mean reciprocal rank | Total time (s) |
| --- | --- | ---: | ---: | ---: |
| `ggml-org/Kev-4B-GGUF:Q4_K_M` | Relevance | 50/52 | 0.9744 | 9.49 |
| `ggml-org/Kev-4B-GGUF:Q4_K_M` | Choice | 49/52 | 0.9679 | 4.23 |
| `ggml-org/Clef-Flash-GGUF:Q4_K_M` | Relevance | 49/52 | 0.9647 | 18.22 |
| `ggml-org/Clef-Flash-GGUF:Q4_K_M` | Choice | 49/52 | 0.9615 | 9.10 |

The dataset also has eight cases with no useful action, including one empty
catalog. In both model runs, relevance supports correct abstention at the
benchmark threshold in six of the seven nonempty cases. Choice assigns a
preferred action in all seven. On Kev, its additional top-action miss was
`exact_target_forbids_overshoot`, where it preferred adding three liters over
draining one liter. Clef's two approaches had the same top-action success cases.

Choice took about half the time with similar top-action accuracy in these runs.
Each result is one sequential run, relevance before choice. Server load, warmup,
and model variability can affect timing and scores. The dataset and these small
accuracy differences do not establish a general quality winner. The comparison
report hashes normalized inputs; these runs used dataset hash
`9d941cb72f6a9757087f1648d7a53726887aa9223546036da7aa009675ffc5d2`.

### Historical relevance model comparison

These earlier runs measure binary usefulness, including all labeled actions.
Their Brier scores compare relevance models and do not apply to choice scores.

| Model | Request errors | Failed cases | Failed actions | Brier score | Total time (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ggml-org/Clef-Flash-GGUF:Q4_K_M` | 0 | 13 | 17 | 0.063012 | 18.620 |
| `ggml-org/vllm-d3-mini-GGUF:Q4_K_M` | 0 | 12 | 22 | 0.072490 | 15.233 |
| `ggml-org/Kev-4B-GGUF:Q4_K_M` | 0 | 14 | 22 | 0.078522 | 9.759 |
| `ggml-org/lev-GGUF:Q4_K_M` | 0 | 15 | 24 | 0.102554 | 10.450 |
| `LiquidAI/d1-3B-GGUF:Q8_0` | 0 | 19 | 34 | 0.113632 | 5.450 |
| `ggml-org/Laya-GGUF:Q8_0` | 0 | 58 | 119 | 0.467099 | 4.678 |
