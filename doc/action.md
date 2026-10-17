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

Ranking estimates whether an action looks useful as the next step. It does not
establish that the action has the best outcome, can execute successfully, or
will achieve the intent. The pipeline has no explicit calculation or verification
stage. Its scores do not show whether the model performed arithmetic internally.

### What the experiments showed

**Recognizing useful preparation and choosing the best final action are separate
capabilities.** In the latest simple trader test, buying leaves 130 gold and
selling leaves 110. The usefulness-only assessor recommended calculating final
gold first (0.761), yet still scored selling (0.601) above buying (0.579).
Selecting a calculator is promising, but does not demonstrate a correct trade
decision. That run assessed tool names without executing the calculation or
reassessing its result.

**More detailed instructions did not reliably fix numerical decisions.** The
[100-evaluation prompt study](experiments/action-ranking-2026-10-17/README.md)
compared the existing prompt with five revisions covering outcomes, research,
costs, and examples. None improved aggregate development ordering accuracy;
the example-based revision regressed on held-out cases. Some runs also preferred
research costing more than its possible benefit. The original ranking prompt
remains unchanged.

**A separate readiness judgment has not demonstrated additional value.** The
[initial tool-assessment study](experiments/tool-assessment-2026-10-17/README.md)
tied relevance ranking's accuracy, with different abstention behavior. In the
[controlled follow-up](experiments/tool-assessment-controlled-2026-10-17/README.md),
usefulness-only and usefulness-plus-readiness received identical state, tool
catalogs, usefulness questions, and usefulness cutoffs. Both scored 8/8 on
development and 8/8 on held-out cases. Removing the readiness gate changed
0/16 recommendations; usefulness-only used about 51% fewer input tokens.
Readiness wording can also overlap with usefulness: an unnecessary tool may
still be executable.

**State and catalog context can support indirect tool selection.** In the
controlled study, both methods preferred calculation for raw supplier costs and
travel times, then direct action when verified results were supplied. They also
selected preparation when a printer was off or an invoice was not local. These
examples support testing contextual usefulness for prerequisite recognition;
they do not establish general planning or mathematical reliability.

These results concern small, synthetic sets on one quantized model, with fixed
tool order and one run per input. Correct first-step labels do not establish
execution success, probability calibration, or robustness. The studies' selected
cutoffs are experimental settings, not general defaults. The trader failure
remains relevant despite perfect scores on the smaller controlled set.

### Direction for a decision-making framework

The simplest candidate is one contextual usefulness question per available tool:
would using it now advance the intent directly, or supply something another
useful tool needs? Supply the intent, current state, and complete tool-name
catalog. Account for costs and completed work, and allow no recommendation when
the catalog cannot help. Keep the original ranker's return-all contract separate
from this experimental selection and abstention policy.

The current scope is a single read-only assessment. The
[tool-assessment design](decision_loop_architecture.md) describes the implemented
two-score experiment; the controlled results favor usefulness-only as the
simpler candidate to test next. Execution, argument generation, and automatic
state updates remain outside this phase.

A complete framework would also need to handle the following boundaries:

- **Identify the needed operation.** Having all facts does not mean they have
  been evaluated. Missing information, an unresolved comparison, and an already
  verified result should lead to different next steps.
- **Formulate and validate tool inputs.** Adding a calculator does not explain
  when to call it or how to extract operands, units, assumptions, and the
  objective from prose. A trip may require route time rather than straight-line
  distance. Structured domain data can supply these inputs; free-form text still
  requires an extraction and validation mechanism that these tests do not cover.
- **Update state from evidence.** If execution is introduced, actual tool results
  should establish new facts and completed calculations. Model scores alone
  cannot establish completion. Subsequent assessments need those results so
  they can prefer the newly unblocked tool over repeated research. Changed inputs
  can make earlier findings stale; supplied results are not permanently valid.
- **Verify the resulting decision.** Test whether preparation actually improves
  the final choice, including its cost. Recognition of a useful research step
  is only one part of successful decision-making.

Evaluate these capabilities with paired states: information missing versus
known, calculation unresolved versus verified, research worthwhile versus too
costly, and prerequisites available versus impossible to obtain. Compare methods
with the same context and resource budget, freeze selection settings before
held-out evaluation, and retain failures. Add a separate judgment or component
only when it demonstrably improves the decisions being tested.

See the [System One API contract](system-one-api.md) for protocol details and
[installation](install.md) for configuration.
