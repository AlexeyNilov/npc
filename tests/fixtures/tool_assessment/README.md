# Tool assessment experiment

`cases.json` contains eight synthetic cases covering the architecture's scenarios.
Token and destination pairs are development cases; trade comparisons, costly
research, and unavailable preparation are held out by scenario family. These
small sets support an initial experiment, not a reliable generalization claim.

Only `intent`, `state`, and `tools` enter assessment requests. The relevance
baseline receives the same inputs through its existing public interface, which
does not include the full catalog in each question's context. This comparison
therefore measures the complete proposed assessor, not the isolated effect of
adding readiness questions.

Local annotations:

- `id`: unique case identifier.
- `family`: scenario family, confined to one split.
- `split`: `development` or `held-out`.
- `expected`: acceptable first-tool recommendations; `null` means abstention.
- `ready_tools`: names with sufficient information and preparation to use now.
- `preparation_tools`: research or prerequisite tools, including ones already completed.

Tune prompts and cutoffs using development cases, then freeze both before
held-out evaluation. Consult `python -m npc.tool_assessment_experiment --help`
for invocation. Each case consumes one assessment call and one baseline call;
empty catalogs consume neither. The driver uses fixed catalog and strategy
order, with no retries or execution. Keep failures in the saved report.

The report saves inputs and annotations, exact requests and decoded responses,
prompt versions, reported model identifiers, cutoffs, raw scores, recommendations,
elapsed time, and reported input-token usage. A model identifier alone does not
specify its weights, quantization, server build, or sampling configuration;
record those externally when comparing live runs. Responses containing invalid
nonfinite numbers are preserved as serialized text under `nonfinite_response`
so they cannot prevent saving the surrounding strict JSON error report.

Metrics are counts: divide `correct_recommendations`, `blocked_recommendations`,
`unnecessary_preparation`, and `abstentions` by `successful_cases`; divide
`readiness_correct` by `readiness_judgments`. Inspect `error_cases` separately.
Baseline readiness has zero judgments because the ranker does not assess it.
Baseline always recommends its first ranked tool for nonempty catalogs.

`model_calls` includes failed requests. `input_tokens` sums reported usage only;
`calls_with_reported_tokens` indicates its coverage. Missing usage is unknown,
not a measured zero. Latency includes failed requests. These are cost proxies,
not currency estimates.

`prompt.json` pins the exact request for one example to its prompt version.
Update the version and fixture together when intentionally changing wording.

## Implementation verification

`make check` passes with 252 tests. Scoped mutation testing with
`make mutation SCOPE='npc.tool_assessment*'` detected 572 of 726 mutations.
The 154 reviewed survivors change diagnostic/help wording, JSON presentation,
encoding aliases or locale defaults equivalent in the UTF-8 test environment,
and behaviorally equivalent initialization/configuration values. Initial timing
values are overwritten on every returned result; the empty-catalog validation
request consumes neither its evaluator nor the particular nonblank placeholder
text. Prompt wording is pinned separately by the versioned request fixture.
These mutation results check implementation contracts, not model decision quality.
