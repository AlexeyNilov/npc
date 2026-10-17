# Tool assessment evaluation: 17 October 2026

The assessor did not improve first-step accuracy in this initial evaluation.
Both methods passed all four development cases and three of four held-out
cases. The assessor avoided the baseline's blocked download recommendation,
but abstained on a useful choice that the baseline selected correctly. Its
reported input-token cost was 2.44 times the baseline's.

Keep the current relevance ranker unchanged. These results do not justify
promoting tool assessment into an execution policy or claiming that readiness
judgments improve recommendations.

## Method and cutoff selection

Evaluate the eight [fixture cases](../../../tests/fixtures/tool_assessment/cases.json)
using `tool-assessment-v1` and unchanged `action-relevance-v2`. Development uses
the token and destination families; held-out evaluation uses trade comparison,
research cost, and unavailable preparation. Each state is assessed independently;
no tools execute and no state updates occur. Expected answers stay outside
model requests.

[protocol.json](protocol.json) records the procedure before model evaluation.
Start with usefulness cutoff 0.6 and readiness cutoff 0.7. Sweep all 121 pairs
from `{0.0, 0.1, ..., 1.0}` using saved development scores, without further model
requests. Maximize correct recommendations, then minimize blocked recommendations
and unnecessary preparation. Break remaining ties by squared distance from the
initial cutoffs, then ascending usefulness and readiness cutoffs.

The original 0.6/0.7 pair achieved four correct recommendations with no blocked
or unnecessary preparation recommendations and was retained.
[cutoff-selection.json](cutoff-selection.json) preserves every candidate and the
frozen choice, saved before requesting held-out scores. This establishes a
choice for this experiment, not calibrated probabilities or validated production
thresholds. For example, finding an unknown destination scored readiness
0.7023, only 0.0023 above the selected readiness cutoff.

Run 16 successful model requests: assessment followed by relevance per case,
with fixed tool order, one run per input, and no model retries or prompt changes.
Eight earlier development connection attempts failed inside the sandbox before
receiving model responses; preserve these separately in
[sandbox-development-errors.json](sandbox-development-errors.json). The authorized
local-server run had no assessment or transport errors.

## Results

| Split | Method | Correct first steps | Blocked recommendations | Unnecessary preparation | Abstentions | Readiness labels correct | Input tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Development | Assessment | 4/4 | 0 | 0 | 0 | 6/8 | 1,916 |
| Development | Relevance | 4/4 | 0 | 0 | 0 | — | 774 |
| Held out | Assessment | 3/4 | 0 | 0 | 2 | 4/7 | 1,970 |
| Held out | Relevance | 3/4 | 1 | 0 | 0 | — | 816 |

The assessor used 3,886 reported input tokens overall versus 1,590 for relevance.
Reported output tokens were zero for all responses. Summed elapsed times were
1.200 seconds for assessment and 0.641 seconds for relevance. These timings
include client overhead and reflect this local run, not a latency benchmark.

Held-out recommendations:

| Case | Expected | Assessment | Relevance |
| --- | --- | --- | --- |
| Comparison not completed | `calculate_outcomes` | `calculate_outcomes` | `calculate_outcomes` |
| Verified comparison supplied | `choose_better_trade` | `choose_better_trade` | `choose_better_trade` |
| Research costs more than it can help | `keep_position` | No recommendation | `keep_position` |
| Download blocked, no preparation available | No recommendation | No recommendation | `download_snapshot` |

### Abstention trades one error for another

For costly research, the assessor correctly assigned research low usefulness
(0.1885), but assigned keeping the position even lower usefulness (0.1781)
and insufficient readiness (0.5264). Both cutoffs exclude the correct choice.
Lowering readiness alone cannot fix this failure at the frozen usefulness cutoff.
The baseline preferred keeping the position (0.5174) over research (0.1286).

For the blocked download, assessment usefulness was 0.2431 and readiness 0.1245;
either gate excludes it. The baseline returned its only tool despite its low
relevance score (0.2397), because its contract has no abstention threshold.
Avoiding this recommendation does not by itself establish a benefit from readiness.

### Readiness and usefulness may overlap

Assessment matched 10 of 15 readiness labels. All five disagreements were
false negatives relative to the fixture: refreshing a valid token, looking up
a known destination, repeating a completed calculation, costly research, and
keeping the position. The first four are available but unhelpful preparation;
labeling them unready suggests the model may conflate readiness with usefulness.
This is an interpretation of the observed scores, not a demonstrated internal
mechanism. The wording "justify using" also leaves room for this interpretation.

A post-hoc check removed the readiness gate while retaining the saved usefulness
scores and cutoff 0.6. It changed **zero of eight recommendations**. This check
used no additional model requests and is recorded in [summary.json](summary.json).
It does not isolate how asking readiness questions or sharing the catalog
influenced usefulness scores.

## Limits and next experiment

These are eight synthetic, author-labeled cases on one quantized model, with
one run per case and fixed tool/strategy order. Four held-out cases cannot
establish statistical significance, calibration, variance, position robustness,
or performance on other models. The trading case explicitly states that a
verified comparison is required; it tests recognition of supplied preparation
requirements, not discovery of an unstated arithmetic dependency.

The assessor receives the full catalog as shared context; the baseline retains
its original request shape. The comparison measures the complete assessor
rather than the isolated contribution of readiness questions. The baseline's
lack of abstention is another material difference.

A subsequent experiment should separate these effects: compare a usefulness-only
assessor with the same catalog context and abstention policy against the two-score
assessor, clarify readiness labels and wording, and include cases where the most
useful tool is blocked while a less useful preparation tool is ready. Use new
held-out families after tuning; these held-out results have now been inspected.
No such follow-up model calls were made in this run.

## Audit and reproduction

- [development.json](development.json): exact development requests, responses, scores, and metrics.
- [held-out.json](held-out.json): corresponding held-out evidence with frozen cutoffs.
- [cutoff-selection.json](cutoff-selection.json): development-only cutoff sweep and freeze timestamp.
- [summary.json](summary.json): aggregate counts, readiness disagreements, and post-hoc gate check.
- [server-props.json](server-props.json): server configuration observed before held-out evaluation.
- [reproduction.json](reproduction.json): source/fixture hashes, git revision, model hash, and server build.

The endpoint was `http://127.0.0.1:12346/v1/systemone`, reporting
`ggml-org/Kev-4B-GGUF:Q4_K_M`, server build `b11706-f74e2fa6a`, and model file
SHA-256 `33ae6b18926502b2209a1bf7d3b61a350d65938441515c686bb87d226a19eff9`.
The driver sends only state and questions. Saved `/props` generation settings
are evidence of server configuration; their applicability to typed-question
probabilities was not established here.

Use `python -m npc.tool_assessment_experiment --help` for replay arguments.
Replaying consumes additional model calls. Preserve this run's artifacts and
write subsequent runs to separate output paths.
