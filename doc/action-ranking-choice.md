# Choice-based action ranking

## Problem

Compare actions through one System One `choice` question while preserving the
working independent `noul` ranking. Choice probabilities describe relative
preference among the supplied actions and sum to one. They do not measure each
action's independent usefulness. Existing relevance thresholds and binary-label
benchmark calibration metrics therefore do not apply directly.

## Usage (caller's view)

```python
import httpx2

from npc.choice_action_ranking import rank_actions_by_choice
from npc.system_one_choice import SystemOneChoiceClient

state = {"intent": "Restore service", "situation": "Cause unknown; logs available"}
with httpx2.Client() as client:
    evaluator = SystemOneChoiceClient(endpoint, client=client)
    ranking = rank_actions_by_choice(
        state, ["inspect_logs", "restart_service"], evaluator=evaluator
    )
    best_action = ranking[0].action
```

Applications can inject a `ChoiceEvaluator` instead of using HTTP. A validated
empty catalog returns `[]` without calling the evaluator.

`npc-rank-actions-choice --input request.json` accepts the same JSON input as
`npc-rank-actions` and returns all actions as `action`/`score` objects. Run
`npc-rank-actions-choice --help` for arguments, defaults, errors, and examples.
Use the existing [System One configuration](install.md#system-one).

## Shape

`choice_action_ranking.py` owns `ChoiceQuestion`, `ChoiceEvaluator`, and
`rank_actions_by_choice`. The immutable question contains instructions and an
ordered tuple of names. The ranker reuses the existing public action validator
and `RankedAction` record. It copies state, adds `available_actions`, asks which
action is the best next step, and sorts all returned probabilities without
rounding or normalization. Ties preserve input order.

The chosen sketch has these signatures; implementation fills in their bodies:

```python
@dataclass(frozen=True)
class ChoiceQuestion:
    instructions: str
    options: tuple[str, ...]


class ChoiceEvaluator(Protocol):
    def evaluate_choice(
        self, state: State, question: ChoiceQuestion
    ) -> dict[str, float]: ...


def rank_actions_by_choice(
    state: State, actions: Sequence[str], *, evaluator: ChoiceEvaluator
) -> list[RankedAction]: ...
```

`system_one_choice.py` owns choice encoding and decoding. It derives opaque
`action_i` option IDs from the tuple, supplies names as descriptions, and maps
the response back to names. It requires exactly the requested question and
option IDs and a choice answer type. It trusts upstream numeric guarantees,
as the existing adapter does. Winner and confidence fields are unused.

`cli/action_ranking_choice.py` owns JSON presentation and client lifetime.
The public ranking function hides prompting and ordering; the adapter hides
provider IDs, encoding, decoding, and dependency failures. These boundaries
follow boundary-discipline without changing the existing evaluator contract.

## Synthesis decision

Two independent sketches used `gpt-6.1-sol` and `gpt-6-astra`; an independent
`gpt-6.1-sol` judge selected candidate A, the separate adapter. Candidate B
extended `SystemOneClient` with batch choice evaluation and extracted shared
transport. The selected design avoids changing the established execution path
and exposes only the single-choice capability this experiment needs. Adopted
immutable ordered options and private wire IDs from A. Rejected B's batch API,
transport refactor, and duplicate result record. Broadened `RankedAction`'s
description so each ranker can define its probability semantics accurately.

## Tradeoffs accepted

- We accept a small repeated HTTP and CLI boundary in exchange for isolation
  from the working ranking path.
- We accept the existing ten-action limit in exchange for the same input policy
  across experiments, even though model option limits can be larger.
- We accept shared stateless validation and result types in exchange for one
  owner of action input policy and output structure.

## Alternatives considered

A shared adapter would centralize transport but change the existing path to
save a short request block. A strategy flag would make one function expose two
score meanings. A mixed-question evaluator would force existing callers to
handle unrelated answer types. Separate public paths keep each contract small.

## Open questions and risks

How well does each deployed model distinguish the action descriptions? Every
nonempty catalog is evaluated. A local smoke request accepted both three options
and a singleton, but quality across models needs a broader experiment.

## Verification

Run `make check` and `make mutation SCOPE='npc.*choice*'`. Tests use controlled
HTTP transports; model quality remains a separate experimental question.
