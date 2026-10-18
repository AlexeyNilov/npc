# What the local books suggest for action ranking

The most useful next step is to measure whether the rankers choose the better
outcome among useful actions. The existing separation between relevance, choice,
and caller policy is sound. The books suggest extending the evidence around that
design before adding an agent framework, a knowledge graph, or model training.

This note separates source ideas from proposed applications. The experiments
below are recommendations, not measured improvements. No model benchmark was run
for this review.

## The findings that matter most

### Usefulness probability does not measure outcome value

*Grokking AI Algorithms*, chapter 10, distinguishes actions from their expected
long-term rewards. Its discussion of Q-values is a useful contrast with this
project's probability that an action is a useful next step. [B2]

The distinction exposes a concrete limitation in
[`benchmarks/action_ranking.json`](../benchmarks/action_ranking.json).
Both `power_expected_value_large_repair` and
`power_expected_value_small_repair` label both generator actions as useful.
Consequently, either generator can rank first without hurting top-action
accuracy or mean reciprocal rank.

If the objective is expected households powered, the preferred action reverses:

| Case | Primary generator | Backup generator | Better expected outcome |
| --- | ---: | ---: | --- |
| Large repair | 0.40 × 100 = 40 households | 0.95 × 20 = 19 households | Primary |
| Small repair | 0.40 × 10 = 4 households | 0.95 × 20 = 19 households | Backup |

The intent currently says to supply power, without specifying risk preference.
Expected-value superiority is therefore an explicit assumption for a new
experiment, not a reason to silently change the current labels. An intent that
prioritizes the probability of supplying any power could prefer the backup in
both cases.

My recommendation is a separate experiment with explicit objectives and either
preferred-action labels or known outcome values. Report expected regret, the
gap between the best available expected outcome and the selected outcome.
Keep usefulness labels for their existing purpose. A high relevance probability
can correctly describe a small benefit, so relevance scores alone cannot be
treated as utilities. Choice asks a comparative question, but its distribution
also does not quantify the size of the resulting benefit.

### Separate applicability from preference

*Agents and Multi-Agent Systems Development*, chapter 5, sections 5.2 and 5.3,
describes a loop that revises beliefs, activates plans through conditions, and
produces actions. Chapter 6, section 6.5.2, discusses explicit cognitive modules
with selective use of language models. [B1]

*Agentic Architectural Patterns*, chapter 5, "The Agent Router pattern",
separates semantic intent extraction from a capability lookup that can reject
unsupported requests. [B6] The related
[SayCan research](https://say-can.github.io/) combines language-based task
usefulness with a separate estimate of skill feasibility in the environment.

For `npc`, this suggests a caller that checks known prerequisites, permissions,
and resource limits before choosing an executable action. The ranker remains
useful where applicability itself requires semantic judgment. Known arithmetic
and known permissions can be checked by code.

The release cases already illustrate the distinction. `publish_release` can
name the desired result while `build_release` is the executable next step.
Filtering must retain executable prerequisite actions. Filtering only for direct
goal completion would remove the actions that make progress possible.

The simplest experiment supplies allowed actions from a small deterministic
environment and compares that caller with a caller that relies entirely on
textual constraints. It does not require changing the public ranking API.
SayCan's multiplication of scores depends on its particular quantities and
modeling assumptions. Multiplying two `noul` judgments here would not establish
a calibrated joint probability.

### State needs observed outcomes and evidence freshness

The belief-revision step in chapter 5 of *Agents and Multi-Agent Systems
Development* distinguishes incoming observations from the agent's existing
beliefs. [B1] *Context Engineering*, section 1.5.5, describes application state
outside the LLM, with the relevant slice supplied for each turn. [B4]

The current `State` can already carry additional string fields. A caller can
experiment with `last_action`, `last_result`, `remaining_budget`, and
`current_evidence` without introducing a new ranking data model. The caller
should update these from observations after execution. Requesting a payment
does not establish that a payment succeeded.

This matters for `payment_timeout_unknown_outcome`,
`validation_stale_after_edit`, and
`revocation_evidence_out_of_narrative_order`. They test distinct failure modes:
an uncertain effect, evidence invalidated by a change, and evidence whose
chronological authority differs from its position in the narrative.

My proposed experiment pairs full histories with concise state summaries that
retain timestamps, artifact identity, and unresolved outcomes. Measure decision
agreement and constraint violations. Compression is useful only if it preserves
the facts that can change the decision.

### Repeated ranking needs a completion rule

The classical reasoning loop provides the action, observation, and state-update
structure. [B1] *Grokking AI Algorithms*, chapter 10, supplies the reason to
evaluate cumulative outcomes. [B2] These ideas also agree with
[CoALA's explicit memory, action space, and decision process](https://arxiv.org/abs/2309.02427).

The current rankers are deliberately stateless and do not execute actions.
That boundary fits the literature. However, a caller that repeatedly chooses
the highest score can keep researching, repeat completed work, or oscillate
between plausible actions. Whole-plan suitability from `rank_plans` is another
judgment, rather than evidence that execution succeeds.

A small episode benchmark would expose these failures. The environment applies
one action, returns its observed effect, and supplies the updated state for the
next ranking. Goal checks and step limits belong to the caller.

Start with deterministic release, payment, and trader scenarios. Report goal
completion, actions taken, budget spent, repeated ineffective actions, and
constraint violations. Include a case where waiting preserves an in-flight
success and a case where the goal already holds. These are meaningful outcomes
even when no further productive action is needed.

Chapters 2 and 3 of *Grokking AI Algorithms* provide a simpler baseline when
states, action effects, and costs are known. Exhaustively search a tiny bounded
environment to establish the best achievable outcome, then compare ranking
policies against it. This gives the episode benchmark an independent answer.
It also reveals where ordinary search solves the problem more reliably than
semantic judgment. Opaque natural-language plans do not provide the transition
model needed for that guarantee. [B2]

### Information gathering has value only through a later decision

*Grokking AI Algorithms* explains delayed rewards. *Agents and Multi-Agent
Systems Development* includes information gathering in its examples of plan
activation and action choice. [B1], [B2] My application of those ideas is to
evaluate research by the downstream decision it can improve, including its cost.

This is more precise than rewarding information merely because it concerns the
goal. The dataset already has `information_with_no_decision_value`,
`trader_research_uses_trade_opportunity`, and
`trader_analysis_already_complete`. These cases are valuable foundations.

An idealized value-of-information calculation compares the expected best
decision after observing a result with the best decision now, then subtracts
the observation cost. The relevant quantity is improved outcome, not how much
uncertainty disappears.

Add paired episodes where the same diagnostic changes the optimal action in one
case and cannot change it in another. Include a diagnostic that is informative
but misses the deadline. Treat repeated analysis with no new evidence as an
episode failure when it prevents completion.

### Ranking stability needs context-sensitive expectations

In *Innovative Approaches to Decision Making*, chapter 3, section 3, Thomas L.
Saaty and Daji Ergu discuss scales, rank preservation, rank reversal, and
sensitivity analysis. They explicitly argue that rank changes require an
explanation in the decision context. This is a methodological argument from
multi-criteria decision making, not a theorem about LLM rankers. [B3]

It suggests several useful checks for both ranking approaches:

- Permute the candidate order and compare the preferred action. Preserve the
  documented input-order rule when scores tie.
- Paraphrase an action without changing its effects.
- Add a clearly irrelevant candidate while staying within the ten-action limit.
- Add a genuinely useful prerequisite, where a preference change can be correct.
- Change one cost or deadline across the point where the preferred action changes.

Choice probabilities must change when the denominator changes, so score equality
is the wrong expectation. Relevance scores can also change because every question
receives the whole catalog and asks about prerequisites. Compare decisions and
the expected direction of change rather than demanding catalog independence.

### Calibration and abstention require their own evidence

*Cracking the AI Agent Interview*, Q115, distinguishes a confidence score from
empirical calibration and discusses held-out calibration data. Its examples
concern RAG, so their transfer to action usefulness needs testing. [B8]

The project already reports a binary Brier score and uses 0.5 as a benchmark
threshold. Those are useful starting points. A low average Brier score alone
does not establish acceptable behavior around a deployment threshold, especially
when false acceptance and false rejection have different consequences.

My recommendation is to report false acceptance on catalogs with no useful
action alongside rejection of useful actions. With more labeled cases, inspect
observed usefulness rates in score bands and evaluate threshold choices on data
held apart from prompt development. Separate numerical correctness guaranteed
by `SystemOneClient` from empirical probability calibration.

Adding a "none" candidate to choice is an experiment worth considering, but its
relative probability would still need validation as an abstention signal.
Thresholding choice scores at the relevance threshold has no such justification.

### Explicit knowledge helps when its abstractions preserve the decision

Niklas R. Höpner's thesis, chapter 4, studies class abstractions from knowledge
graphs and residual policy learning. It reports benefits in commonsense games
whose structure supports those abstractions, and problems when classes aggregate
objects incorrectly. [B5] The
[original IJCAI paper](https://www.ijcai.org/proceedings/2022/423)
also identifies noisy knowledge and weak class structure as failure modes.

For `npc`, a useful near-term question is whether concise action descriptions
reduce ambiguity. *Context Engineering*, section 4.2.1, treats a tool's name,
description, usage conditions, and schema as its contract with the model. [B4]
That is more directly actionable than adopting a graph database.

An experiment can encode descriptions in an extra string field of `State`,
then compare names alone with descriptions containing preconditions and effects.
Use opaque names and misleading names as controls. A description may help the
`opaque_actions_insufficient_context` case, while an incorrect description can
make the result worse.

The thesis concerns trained RL policies, not a plug-in upgrade for System One.
Its lesson is conditional. Keep the details that distinguish actions in this
environment, and test abstractions on unfamiliar objects and domains before
investing in graph construction or training.

## An order for the experiments

These experiments can initially live outside the production ranking API. Each
addresses a different uncertainty, so a combined score would hide useful evidence.

| Priority | Experiment | Baseline and comparison | Evidence to collect |
| --- | --- | --- | --- |
| 1 | Preference among useful actions | Relevance first action versus choice first action on explicitly valued alternatives | Expected regret, preferred-action accuracy, constraint violations |
| 2 | Candidate and context perturbations | Original cases versus permutations, paraphrases, distractors, and cost changes | Decision changes, expected preference reversals, repeated-run variation |
| 3 | Closed decision episodes | Repeated ranking with observations versus a simple deterministic policy | Completion rate, steps, wasted actions, remaining resources |
| 4 | Caller-owned applicability | Text-only constraints versus known preconditions checked by code | Blocked-action selection, retained prerequisites, completion |
| 5 | Context and action descriptions | Names and narrative versus concise state and explicit effects | Decision quality, input size, latency, failures caused by omitted facts |
| 6 | Abstention policy | Existing threshold versus thresholds selected on separate data | False acceptance, false rejection, coverage, Brier score |

For model comparisons, preserve the existing prompt versions and dataset
identity. Alternate execution order and repeat paired runs before interpreting
small latency or accuracy differences. Use a separate evaluation set for final
claims after prompt changes.

The first experiment has the best immediate return. It can reveal whether the
faster choice approach is better at the decision actually needed, even when both
approaches already place a useful action first.

## Reading priorities and source locations

| Source | Book | Selected reading |
| --- | --- | --- |
| [B1] | Agents and Multi-Agent Systems Development | Chapter 5, sections 5.2 and 5.3; chapter 6, section 6.5.2; chapter 10 for later learning work. |
| [B2] | Grokking AI Algorithms, second edition | Chapters 2 and 3 on state and search; chapter 10, pp. 347–386, on rewards and action value. |
| [B3] | Innovative Approaches to Decision Making | Chapter 3 by Thomas L. Saaty and Daji Ergu, section 3; rank preservation and sensitivity, pp. 109–110. |
| [B4] | Context Engineering, MEAP V01 | Sections 1.1.3, 1.5.5, and 4.2.1 on context cost, state, and tool contracts. |
| [B5] | Algorithms for knowledge-guided sequential decision-making | Chapter 4, pp. 49–64, on class abstraction and residual policy learning. |
| [B6] | Agentic Architectural Patterns for Building Multi-Agent Systems | Chapter 5, Agent Router and tool routing; chapter 7, robustness metrics. |
| [B7] | Build an AI Agent (From Scratch) | Chapters 7 and 10 as reading leads. Extracted body text is partly garbled. |
| [B8] | Cracking the AI Agent Interview | Q115 on confidence scoring, calibration, and auditability in RAG. |

Start with B1 chapter 5, B2 chapter 10, and B3's rank and sensitivity discussion.
B4 is next for improvements to supplied context. B5 is valuable when deciding
whether explicit knowledge or learning is justified. B6 offers selected patterns
to borrow once a concrete execution problem appears.

## The rest of the collection

The following screening judgments concern this project's current ranking work,
rather than the books' general value.

| Book or group | Relevance to this task |
| --- | --- |
| *Event-Database Architecture for Computer Games*, Rodney Quaye, `Event_Games.pdf` | Sections 3.1 and 3.2 distinguish event chains from stored game data. Useful background for a future episode environment. Its full architecture is larger than this ranking experiment needs. |
| *Context Engineering for Multi-Agent Systems*, Denis Rothman | Structured context and selected evidence are relevant. Its broader multi-agent orchestration is a later concern. |
| *Beyond Code*, Jeremy McEntire | "Mechanical Gates Over Advisory Review" and "The Goodhart Trap" are relevant reading for deterministic checks and benchmark incentives. Coding-process evidence does not establish ranking quality. |
| *AI Agents: The Definitive Guide*, Nicole Koenigstein | Available chapters explain agent architectures. Promised evaluation chapters cannot support conclusions from this copy. |
| *Building AI Agent Platforms*, Ben O'Mahony and Fabian Nonnenmacher | Available observability and execution chapters may help after a decision loop exists. Platform construction is premature for the present API. |
| *Hermes Agent*, Tamer Ahmed | Sections on the decision loop and hard step limits repeat useful control ideas. Product-specific implementation detail has less value here. |
| *Reliability Technology for Complex Software Systems*, Yichen Wang, Yikun Wang, and Fuqun Huang | Fault propagation and correlated failures matter for a larger execution system. Less direct than measuring action outcomes now. |
| *Hybrid Intelligence*, Kevin Holt | Criteria definition and human review are relevant to label adjudication. Most material concerns facilitated group decisions. |
| *Grokking* chapters on evolutionary and swarm algorithms | Possible search methods when candidate generation becomes a problem. The current API receives at most ten candidates, so candidate search is not the immediate bottleneck. |
| *Deep Learning with Python*, third edition, François Chollet and Matthew Watson | Background for later training and generalization work. Full text extraction was stopped during screening. No chapter-specific recommendation relies on it. |
| *Graph Mining*, Riju Bhattacharya and coeditors | Conditional value if graphs become an actual input or learning representation. No need demonstrated by the present rankers. |
| *Complex Systems, Artificial Intelligence, and Emerging Technologies*, Klaus Mainzer, `Complex_emerging.pdf` | Broad systems background with little direct guidance for the next ranking experiment. |
| *Lean-AI*, Adil Dalal and Elizabeth A. Cudney | Process improvement and error prevention are indirect influences. Lower priority than decision-specific sources. |
| *Agentic Coding with OpenAI Codex CLI*, Daniel Vaughan; *Modern Software Engineering with Codex*, Derrick M. Newman; *Claude AI Bible*, Stephen Clear | Mostly development-tool workflows, rather than the runtime action-selection problem. |
| *Information Visualization*, Sougata Mukherjea, `Info_visual.epub` | Potentially useful for displaying experiment results, rather than choosing actions. |
