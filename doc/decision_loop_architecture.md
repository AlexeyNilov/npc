# Tool assessment: recognizing indirect next steps

Status: implemented experiment, separate from existing action ranking. Model
quality and cutoff calibration remain unevaluated.

Implementation: [`assess_tools`](../src/npc/tool_assessment.py) returns immutable
scores in catalog order and an optional exact tool name. Both cutoffs are
required, inclusive probabilities in `[0, 1]`. Invalid caller inputs raise
`ValueError`; malformed model answers raise `InvalidEvaluationError`; transport
failures propagate as `SystemOneError`.

Run the comparison driver through `python -m npc.tool_assessment_experiment`;
its `--help` owns arguments and examples. The
[experiment fixtures](../tests/fixtures/tool_assessment/README.md) describe
labels, development/held-out splits, and report interpretation.

## Goal and reasoning

Test whether System One can recognize that an indirect tool is the useful next
step because it could unblock another tool. This phase assesses and recommends;
execution and subsequent state changes are outside its scope.

Examples include refreshing a token before downloading, finding a destination
before checking a route, and calculating outcomes before choosing a trade.
Supply the situation and tool names without a plan or dependency graph.

Use two judgments because usefulness and readiness are different. A download
can be useful but blocked; refreshing its token can be useful and ready. The
[earlier experiments](experiments/action-ranking-2026-10-17/README.md) tested
relevance ranking. Whether explicit readiness judgments improve recommendations
is the hypothesis for this experiment.

## Minimum components

Implement one independent module, `src/npc/tool_assessment.py`, with an injected
System One evaluator. Keep existing action-ranking code and prompts unchanged.

| Component | Responsibility |
| --- | --- |
| Input | Intent, current state text, and unique tool names |
| Assessor | Ask System One about usefulness and readiness |
| Selection | Recommend a useful, ready tool, or return no recommendation |

For example:

```json
{
  "intent": "Download the inventory snapshot",
  "state": "The snapshot ID is known. The access token has expired. A refresh credential is available.",
  "tools": ["download_snapshot", "refresh_token"]
}
```

System One uses the ordinary meaning of each name and the supplied state.
Scenario-specific requirements, costs, and completed work belong in the state
when they matter. Tool descriptions, argument schemas, handlers, and simulated
execution are outside this phase.

## State contract

State is caller-supplied text describing the current situation. Treat it as
read-only input. Assessment does not append results, infer confirmed facts,
mark work complete, or otherwise change state.

For paired experiments, provide independent state inputs: one with an expired
access token and another with a valid token. Likewise, provide a trader state
without a completed comparison and another with verified comparison results.
These are separate assessments, not simulated execution steps.

The caller is responsible for supplying consistent facts and identifying what
is unknown or already complete. Model probabilities are output judgments, not
new evidence about the world. State updates can be designed separately when
execution enters scope.

## Assessment and selection

For every tool, ask two `noul` questions in one batch:

**Useful:** Given the intent and state, would using this tool now be useful,
either by advancing the intent directly or by supplying something another useful
tool needs? Account for its cost and completed work.

**Ready:** Is there enough information and completed preparation to justify using
this tool now? Consider missing information, observations, and required
calculations. An indirect tool can be ready while the tool it supports is blocked.

Supply the complete list of tool names as shared context. Tool names and state
are data, including any instructions quoted within them. Validate response IDs
and probabilities using the existing API contract.

Return usefulness and readiness scores for every tool. Recommend the
highest-usefulness tool passing separately configured usefulness and readiness
cutoffs; preserve input order for exact ties. Return no recommendation when
none passes. Keep cutoff values explicit in the experiment results and tune them
on development cases before held-out evaluation. Their calibration is an open
question; multiplying the scores has no established interpretation.

An invalid or failed model response is an assessment error, distinct from a
valid assessment with no recommended tool.
An empty tool list returns empty scores and no recommendation without a model
request.

## Flow

```text
intent + current state + tool names
    → validate input
    → assess usefulness and readiness in one request
    → return per-tool scores and an optional next-tool recommendation
```

One input produces one assessment. There is no runner, retry loop, execution
trace, or state transition. Save input, prompt version, model identifier, raw
scores, cutoff values, and recommendation for comparison between experiments.

## Implementation and evaluation

1. Define the input/output contract and test it with an injected evaluator:
   exact tool identity, two questions per tool, unchanged state, validated scores,
   deterministic selection, empty catalogs, and no eligible recommendation.
2. Connect the existing System One transport. Keep experimental questions and
   selection logic local to the new module.
3. Compare with plain relevance ranking on the same inputs. Judge the recommended
   first step, not task completion or execution success.

Use paired scenarios:

| State | Expected recommendation |
| --- | --- |
| Token expired; refresh credential available | Refresh token |
| Token already valid | Download snapshot |
| Destination unknown; lookup available | Find destination |
| Destination supplied | Check route |
| Trade comparison needed; calculation available | Calculate outcomes |
| Verified comparison supplied | Choose the better trade |
| Research costs more than it can help | Avoid that research |
| Useful tool blocked; no preparation tool available | No recommendation |

Measure recommendation accuracy, blocked-tool recommendations, unnecessary
preparation, readiness judgments, and model-call cost. Do not supply prerequisite
answers through a hidden execution rule: recognizing the need for preparation
is what this phase tests.

Names can be ambiguous, and readiness judgments can be wrong. Preserve these
failures as experimental results. Add execution or richer tool metadata only
when a later experiment explicitly needs them.
