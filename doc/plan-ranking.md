# Plan suitability ranking

## Problem

Action ranking asks whether an action is a useful next step. Plan ranking asks
whether a complete proposed course of action suits the intent and current state.
A useful opening step alone cannot establish that a plan is feasible.

## Usage (caller's view)

Use the same injected evaluator as action ranking:

```python
from npc.plan_ranking import rank_plans

ranking = rank_plans(
    "Restore checkout",
    "The latest release introduced errors. Rollback is available.",
    [
        "Roll back the release, then verify checkout.",
        "Inspect logs, fix the cause, deploy, then verify checkout.",
    ],
    evaluator=system_one,
)
best_plan = ranking[0].plan
```

The same interface accepts plans from another domain:

```python
ranking = rank_plans(
    "Equip the office",
    "Budget is 3000. Desks have already been purchased.",
    [
        "Order chairs within budget and arrange delivery.",
        "Purchase desks and chairs, then seek budget approval.",
    ],
    evaluator=system_one,
)
scores = [(item.plan, item.probability) for item in ranking]
```

The evaluator can be a caller-owned `SystemOneClient`; connection configuration
belongs to [installation](install.md). The API docstring owns the input and error
contract.

`npc-rank-plans` exposes the same ranking through JSON files or standard input.
Run `npc-rank-plans --help` for its request format, options, and exit codes.

## Shape

`plan_ranking.py` owns `rank_plans` and immutable `RankedPlan(plan, probability)`.
It treats each supplied text as an alternative complete plan. Its question
considers feasibility, step order, prerequisites, costs, completed work, and
the likely final outcome. Text remains opaque to code.

One call hides input validation, question construction, batching, answer mapping,
and stable descending sorting. The shared evaluator contract and response decoder
have one owner in `_evaluation.py`, per single-source-of-truth and
boundary-discipline. Transport stays in `SystemOneClient`; callers own its HTTP
client. Action ranking retains its public imports and next-step semantics.

The planned signature is:

```python
def rank_plans(
    intent: str,
    state: str,
    plans: Sequence[str],
    *,
    evaluator: SystemOneEvaluator,
) -> list[RankedPlan]:
    # Validate, build whole-plan questions, evaluate once, decode, and sort.
    raise NotImplementedError
```

## Synthesis decision

Candidate A, produced by `gpt-6.1-sol`, is the base: a dedicated plan ranker and
minimal shared response decoding. Candidate B, produced by `gpt-6-astra`, puts
both domains behind a shared engine with an action-or-plan selector. Both hide
ranking mechanics from callers, but B adds result adaptation and couples prompt
ownership to the engine. Adopt its emphasis on identical batching guarantees;
keep domain validation and semantics in their respective modules.
An independent `gpt-6.1-sol` judge selected A for its domain ownership and smaller
action-regression risk. Both requested design models were available. The red-flag
review found no selector, intermediate result type, or public coordination steps
necessary in the selected design. Python underscores mark the shared helper as
internal without adding machinery to enforce private imports.

## Tradeoffs accepted

- We accept small repeated domain validation in exchange for independent action
  and plan contracts.
- We accept compatibility imports in `action_ranking` to preserve existing callers
  while giving shared evaluation checks one owner.
- We accept opaque text and model judgment in exchange for avoiding a step schema
  and execution simulator.
- We retain the ten-candidate limit without imposing an unsupported text-length
  limit. Scores remain raw model judgments of suitability, without normalization.

## Alternatives considered

A shared ranking engine removes more repetition but adds an internal policy
selector and thin domain facades. Its larger refactor brings little benefit for
two operations. Passing plans directly to `rank_actions` hides the wrong question.
Copying response decoding creates two owners of the evaluator response contract.

## Open questions and risks

Does the model reliably distinguish a useful first step from an infeasible full
plan? Deterministic tests verify requests and ranking behavior. A model benchmark
with paired plans is needed to measure judgment quality.

## Next implementation step

Implement the public plan contract against failing behavior tests, then verify
existing action behavior and inspect scoped mutation results.
