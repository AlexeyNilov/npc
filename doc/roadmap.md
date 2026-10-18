# Project roadmap

Updated 18 October 2026.

The next development priority is a small decision loop that reaches observable
outcomes. Use it to learn when action ranking is sufficient, when planning helps,
and when the agent should stop. Improve ranking in response to failures observed
in those episodes.

This roadmap assumes that `npc` aims to explore goal-directed agents across
several domains. The first environment is a controlled simulation. Real service
integration follows only after the decision behavior is measurable.

## Starting point

The project already has [action ranking](action-ranking.md),
[plan suitability ranking](plan-ranking.md), injected evaluators, and
[benchmarks](benchmarks.md). These judge supplied candidates. They do not execute
actions, maintain a changing world state, or establish that an intent was achieved.

The [book research review](action-ranking-research.md) explains the main evidence
gaps, including the distinction between useful actions and better outcomes.
This roadmap owns development priorities. API contracts and benchmark methodology
remain in their existing documentation.

## Milestones

The order reflects dependencies rather than calendar commitments. Each milestone
ends with evidence that determines the next investment.

| Milestone | Main question | Deliverable | Completion criterion |
| --- | --- | --- | --- |
| 1. Define the decision problem | What does progress, success, and stopping mean? | One scenario specification and a short comparison of loop designs | The scenario has explicit actions, observations, costs, objectives, and terminal outcomes |
| 2. Complete one decision loop | Can repeated decisions reach the intended outcome? | A trader simulation with an observable episode trace | The loop completes representative variants and terminates predictably on failure cases |
| 3. Evaluate complete episodes | Where does behavior break? | An episode benchmark with independent expected outcomes | Reports distinguish decision quality, execution failures, and stopping errors |
| 4. Compare actions and plans | Does planning justify its cost? | Paired action, plan, and hybrid experiments | A documented policy choice follows from outcome and cost measurements |
| 5. Improve the limiting component | Which change produces the largest benefit? | Targeted changes plus evaluation on unseen scenarios | Improvements persist beyond the cases used to develop them |
| 6. Apply the loop elsewhere | Which assumptions depend on the domain? | A second environment, followed by one bounded integration | The same control structure handles different actions and failure modes without domain-specific branches throughout the loop |

## 1. Define the decision problem and study loop designs

Keep research bounded to decisions needed for the first implementation. Compare
the approaches below through the same trader example. Identify what each adds to
state interpretation, action selection, commitment, and recovery.

| Approach | Idea to investigate | Question for `npc` |
| --- | --- | --- |
| [OODA](https://www.airuniversity.af.edu/AUPress/Display/Article/1528758/a-discourse-on-winning-and-losing/), observe, orient, decide, act | Separate incoming observations from their interpretation and decision context | Does an explicit orientation step improve decisions with stale, incomplete, or conflicting evidence? |
| [ReAct](https://arxiv.org/abs/2210.03629) | Interleave reasoning with actions and new observations | When does an information-gathering step improve the next decision enough to justify its cost? |
| [BDI](https://aaai.org/papers/icmas95-042-bdi-agents-from-theory-to-practice/), beliefs, desires, intentions | Represent beliefs and commitment to a course of action explicitly | When should the agent continue a plan, reconsider it, or abandon it? |
| Receding-horizon planning | Consider a future sequence, execute its first action, and reconsider after observation | Does short lookahead avoid poor local choices without committing to stale assumptions? |

OODA is a conceptual reference, rather than a requirement to make four model calls.
For the initial implementation, orientation can be ordinary code that constructs
the decision state from observations, constraints, and remaining resources.
Only add a model-based interpretation step when a scenario demonstrates a need.

Define one observable contract for the first scenario:

- The objective, including time horizon and risk preference.
- The environment state and the observations available to the agent.
- Executable actions, their preconditions, effects, and costs.
- How information gathering consumes time, turns, or computation.
- What evidence establishes success, failure, or an unresolved outcome.

Start with maximizing a trader's gold at a fixed horizon. Specify prices,
inventory, storage costs, and trade opportunities so that the best outcome can
be calculated independently. Keep actual environment state separate from what
the agent knows, even if the first scenario exposes the full state.

Completion means another developer can describe correct outcomes without
consulting a model's scores. Research should produce implementation choices and
test scenarios, rather than a general survey of agent architectures.

## 2. Build the smallest complete loop

Use the existing ranker inside a caller that owns the episode:

1. Observe the environment and update the decision state.
2. Check the goal, terminal conditions, and remaining budgets.
3. Obtain applicable actions and rank them.
4. Apply an explicit selection or abstention policy.
5. Execute one action and record its observed result.
6. Repeat with the updated state.

Keep the environment, selection policy, and evaluator independently replaceable.
Domain code owns exact preconditions and effects. The ranker supplies semantic
judgments. The loop owns scheduling, budgets, and terminal outcomes.

Begin with one action policy. A reasonable baseline uses relevance to determine
whether any candidate is useful and selects the highest-ranked accepted action.
Its threshold is an experimental policy, not a production guarantee. Compare
choice later without assuming that a high relative score establishes usefulness.

Record observations, candidate actions, scores, the selected action, its actual
result, resource changes, and the reason the episode stopped. Preserve the prompt,
model, policy, and scenario identities needed to interpret a run. A failed or
timed-out execution must leave its effect explicitly uncertain until reconciled.

The first milestone includes stopping behavior. It is incomplete if the loop
reaches the right outcome only when an external observer manually interrupts it.

## Stopping is part of the decision contract

The following outcomes are proposed semantics, not existing API types.

| Outcome | Required evidence or policy | Meaning |
| --- | --- | --- |
| Success | The environment's goal predicate holds at the required time | The intent has been achieved according to the scenario contract |
| Environment failure | A defined terminal failure occurs | This episode cannot succeed under its rules |
| No applicable action | The environment provides no executable action or observation path | The agent is blocked in the current state; global impossibility is a separate claim |
| Abstention | The selection policy accepts no candidate | The model and policy do not support acting; this does not prove that the goal is impossible |
| No progress | A bounded policy detects repeated ineffective behavior | The controller stops or requests reconsideration; the detection can be mistaken |
| Budget exhausted | A step, model-call, time, or resource limit is reached | The episode ended without verified success |
| Execution unresolved or failed | An action result cannot be established or recovery is exhausted | The final report preserves the uncertainty or error |
| Cancelled | The caller requests cancellation | The controller starts no further work and accounts for actions already in flight |

Check success before beginning more work and after receiving new observations.
Interpret success against the scenario's horizon. Holding enough gold now is
different from maximizing gold tomorrow. A maintenance goal such as preserving
inventory requires a duration or an explicit handoff condition.

Waiting can be a productive action when a known event is pending. It needs an
observable wake-up condition and a deadline. Waiting alone is not completion.

Bound deliberation as well as execution. Model calls, planning, and repeated
analysis consume a finite allowance even when they do not change world state.
Every pending operation also needs a bounded wait. A timeout stops waiting; it
does not establish that an external side effect was cancelled.

Evaluate stopping errors in both directions. Premature stopping loses achievable
benefit. Late stopping repeats work, spends resources, or damages a completed goal.

## 3. Evaluate episodes before expanding the architecture

Extend the trader environment with paired cases that change one consequential
fact. Cover storage fees, limited buyer capacity, completed calculations,
information that changes a decision, and research that consumes the only trade
opportunity. Include an initially satisfied goal and a deliberately unreachable
goal with an independently known explanation.

Then introduce uncertainty and changing conditions. Useful cases include a
pending result, stale evidence, an action failure, and a prerequisite that becomes
invalid after the agent chooses a plan.

Measure final outcome, goal completion, constraint violations, action count,
model calls, elapsed time, and stopping correctness. Where utilities are known,
report regret relative to the best achievable outcome. Use a hand-written policy
or exhaustive search in the small simulation as an independent baseline.

Keep the existing ranking benchmarks. They diagnose individual judgments,
while episode evaluation measures their consequences. Separate failures caused
by missing information, ranking, selection policy, execution, and state updates.

Use controlled evaluator outputs to test the loop's behavior contracts. Use real
model runs to measure decision quality. Reserve scenarios for evaluation after
prompt development, and repeat paired comparisons before interpreting small
differences. [Contributing](../CONTRIBUTING.md) owns development checks and TDD.

## 4. Compare action, plan, and hybrid decisions

Run each approach against the same environments, initial states, observation
access, and resource accounting. Count the cost of planning and reconsideration.

| Approach | Behavior | Main tradeoff |
| --- | --- | --- |
| Action selection | Choose the next action from the current state | Low commitment and overhead, with a risk of poor local choices or repetition |
| Plan selection | Rank supplied complete plans and follow a selected executable sequence | Explicit dependencies and future outcomes, with a risk of stale assumptions |
| Hybrid | Choose a plan, execute one step, and reconsider when observations invalidate it | Some continuity with adaptation, at the cost of more policy decisions |

Start with environment-supplied plans whose executable steps are known.
`rank_plans` currently judges opaque text. Its score does not create an executable
plan or verify that each effect occurs. Keep plan descriptions connected to
known steps in the experiment. Candidate generation is a separate research
question once selection among supplied plans is understood.

Compare continuing a valid plan with reconsidering on every step. Define triggers
such as execution failure, changed preconditions, new evidence, or budget changes.
All approaches recheck applicability before an action and use the same stopping
rules. Higher plan suitability is not a substitute for episode success.

Adopt the least complex approach that meets the observed needs. Planning earns
its place when better completion or outcomes justify its total cost. Preserve
action selection for scenarios where planning adds no measurable benefit.

## 5. Improve the component that limits outcomes

Choose ranking work from the episode failure analysis:

| Observed failure | Next investigation |
| --- | --- |
| Useful but inferior actions repeatedly win | Comparative choice, clearer objectives, and outcome-value evaluation |
| Blocked actions win | Applicability checks and missing preconditions in context |
| The agent repeats completed analysis | State updates, progress detection, and the cost of deliberation |
| The agent abandons good plans or follows stale ones | Commitment and reconsideration policy |
| Paraphrases or candidate order change decisions without a reason | Ranking sensitivity and prompt robustness |
| The agent accepts harmful candidates or rejects useful ones | Abstention policy and probability calibration |
| Opaque action names prevent sound choices | Action descriptions with explicit preconditions and effects |

Make one consequential change at a time and evaluate it on held-out episodes.
Prefer better state, action contracts, or deterministic checks when those solve
the failure. Consider knowledge graphs, learned policies, or additional agents
only when a measured problem requires them.

## 6. Test transfer, then integrate

Use release recovery as a second simulated domain. It introduces prerequisites,
artifact identity, invalidated validation, and completion evidence different from
the trader's numerical objective. Reuse the loop while replacing domain actions,
observations, and goal checks.

Once both domains work, choose one bounded real integration. Define how it
reconciles uncertain effects, validates completion, and recovers from partial
failure before enabling consequential actions. Add persistence or asynchronous
coordination when that integration requires them.

The immediate development task is milestone 1's trader contract followed by
milestone 2's complete loop. Loop research informs those tasks. Broader architecture
work depends on the episode evidence they produce.

