# Action ranking prompt experiments: 17 October 2026

Retain `action-relevance-v2`. Five alternative prompts changed scores but did
not improve the tested development ordering. The example-based candidate
regressed on the held-out set. No production prompt change is justified by
these experiments.

## Method

Run 100 successful, sequential model evaluations against
`http://127.0.0.1:12346/v1/systemone`, using the public `rank_actions` function
and `SystemOneClient`. An injected evaluator replaced question instructions
for each candidate. The comparative candidate also supplied `available_actions`
in the state; the other candidates changed only instructions.

The endpoint reported `ggml-org/Kev-4B-GGUF:Q4_K_M`. Server build, model file
hash, and temperature settings were not recorded, so the model identifier alone
does not fully specify reproduction. All responses reported zero output tokens;
the pipeline requested probability judgments without generated reasoning or a
calculator. This does not reveal whether the model internally represents
arithmetic.

The initial sandbox connection attempts failed before receiving model responses.
They were excluded from the model-evaluation budget; the 100 successful
evaluations followed approval for local server access. No evaluation errors
occurred in the recorded run. Total reported input tokens: 55,792.

Use six prompts, preserved verbatim in [prompts.json](prompts.json):

| Variant | Change |
| --- | --- |
| baseline | Existing v2 relevance question |
| outcome | Explicit horizon, final outcomes, feasibility, and research value |
| research | Research before irreversible choices when its benefit exceeds cost |
| comparative | Compare alternatives and reject dominated choices; include catalog |
| net_benefit | Shorter wording emphasizing benefits exceeding costs |
| examples | Concrete examples of losing purchases, costly research, and prerequisites |

Allocate the budget as follows:

1. Baseline and four revisions on 12 development cases: 60 evaluations.
2. Adaptively add the example-based prompt on eight development cases: 8.
3. Freeze baseline and example-based prompts; evaluate each on eight existing
   non-trading cases and eight new held-out cases: 32.

The held-out cases were written before collecting development results and were
not evaluated during tuning. Existing non-trading fixtures are regression
checks, not an unseen test set. They include diagnosis, approved recovery,
authorization prerequisites, expired credentials, ticket injection, and an
already completed goal.

## Labels and metrics

[cases.json](cases.json) contains all 28 evaluated scenarios and expected tiers.
Only intent, state, and actions enter the ranker. Labels stay outside requests.
Earlier tiers should score strictly above later tiers; ties fail strict
comparisons. Average pairwise accuracy per case, then across cases. Top-tier
accuracy measures whether the returned first action belongs to the best tier.

These labels deliberately test decision quality more strictly than broad
relevance: an inferior trade can still be relevant under the production contract.
An ordering failure here is not necessarily an API contract violation.

For free calculation with all numerical facts available, accept either the
best trade or calculation in the top tier. Preferring research is not required
merely because the catalog offers it. When a decision-relevant price or fee is
unknown, prefer the available free lookup. Completed or excessively costly
research belongs below a useful trade.

The completed-invoice case has no relevant action and no strict tier comparisons.
Exclude it from pairwise and top-tier metrics; report its maximum score instead.

## Results

| Evaluation set | Prompt | Mean pairwise accuracy | Top tier correct |
| --- | --- | ---: | ---: |
| Development, 12 cases | baseline | 69.4% | 9/12 |
| Development, 12 cases | outcome | 69.4% | 9/12 |
| Development, 12 cases | research | 69.4% | 9/12 |
| Development, 12 cases | comparative | 69.4% | 9/12 |
| Development, 12 cases | net_benefit | 69.4% | 9/12 |
| Matched development subset, 8 cases | baseline | 60.4% | 5/8 |
| Matched development subset, 8 cases | examples | 60.4% | 5/8 |
| Existing cases, 7 comparable | baseline | 100% | 7/7 |
| Existing cases, 7 comparable | examples | 100% | 7/7 |
| Held-out cases, 8 cases | baseline | 62.5% | 5/8 |
| Held-out cases, 8 cases | examples | 56.3% | 4/8 |

The maximum score for the completed-invoice case was 0.025 with baseline and
0.016 with examples. This is one favorable abstention example, not a calibrated
execution threshold.

The example-based prompt used 10,228 input tokens across the 16 final cases,
versus 5,713 for baseline, without improving accuracy.

### Numerical preference can fail without complex arithmetic

With 100 gold, one sack, today's buy/sell price of 10, and tomorrow's guaranteed
price of 3, buying leaves 96 gold and selling leaves 110. Baseline nevertheless
scored buying 0.649 and selling 0.307. The example-based prompt also preferred
buying. A shorter scenario alone does not establish numerical reliability.

The held-out fee case similarly preferred buying despite final gold of 97,
versus 107 for selling. The liquidity case preferred buying despite final gold
of 20 after the debt and penalty, versus 60 for selling.

### Research labels can outweigh research costs

In the development cost case, buying yields 130 final gold, selling yields 110,
and paying 50 for a calculation leaves at most 80 even if followed by the best
trade. Baseline still put calculation first: 0.745 versus 0.744 for buying.
Every revision also put calculation first; examples widened the gap to 0.747
versus 0.698. Making research available does not guarantee sensible valuation
of its cost.

### Explicit prerequisites worked better in this sample

Both baseline and examples preferred looking up an unknown future price and an
unknown purchase fee. Both also passed the seven comparable non-trading checks.
This supports using the ranker to recognize explicit missing information and
prerequisites, within the limits of this small sample.

### Prompt additions can regress a correct decision

When the state supplied verified final outcomes of 90 for buying and 120 for
selling, baseline put selling first, 0.819 versus 0.793. Examples reversed that
ordering, 0.763 versus 0.769. Adding seemingly helpful instructions is not a
monotonic improvement.

## Decision and next experiment

Keep the existing prompt and probability contract. Longer instructions about
arithmetic do not add a verified calculation stage. For numeric decisions,
calculate feasible outcomes in ordinary code, then choose by the objective;
use contextual ranking for remaining information needs and prerequisites.

A useful next experiment would compare raw numerical state with the same state
plus externally calculated outcomes, and with an explicit tool-backed planning
stage. Include reversed preferences, research costs, and completed calculations.
The single favorable supplied-outcomes case here is insufficient evidence for
that approach. No extra model calls were made after experiment 100.

This study uses synthetic, author-labeled cases, one quantized model, one run per
prompt/case, and fixed action order. It does not estimate run-to-run variance,
position sensitivity, calibration, statistical significance, or other models'
performance. Development and held-out failure counts are descriptive.

## Audit and reproduction

[results.jsonl](results.jsonl) preserves every exact request, raw response,
model identifier, elapsed time, scores, labels, and metrics.
[summary.json](summary.json) aggregates the metrics. No endpoint version was
inferred. To replay one model request from the repository root:

```sh
jq -c 'select(.experiment == 78) | .request' \
  doc/experiments/action-ranking-2026-10-17/results.jsonl |
  curl -sS http://127.0.0.1:12346/v1/systemone \
    -H 'Content-Type: application/json' --data-binary @-
```

Replaying makes an additional model call and requires the same server/model
configuration for a meaningful comparison.
