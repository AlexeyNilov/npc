# Controlled usefulness/readiness experiment: 17 October 2026

Both methods selected an accepted first step in **8/8 development and 8/8
held-out cases**. Removing the readiness gate changed **0/16 recommendations**.
Usefulness-only used 5,048 input tokens versus 10,368 for the two-score method,
about 51% fewer. This experiment provides no recommendation benefit from the
additional readiness judgment.

Usefulness-only is the simpler candidate for the next prototype. Existing
production prompts and APIs remain unchanged. These small synthetic sets do not
establish general reliability or make the selected cutoffs production defaults.

## What this experiment isolates

The [previous evaluation](../tool-assessment-2026-10-17/README.md) compared methods
with different context and abstention behavior. This follow-up controls those
differences:

- Both methods receive identical intent, state, and complete tool-name catalog.
- Both use the exact v1 usefulness instructions and question IDs.
- Both use the same usefulness cutoff, inclusive comparisons, and stable ties.
- Only the two-score method additionally asks readiness questions and applies
  its readiness cutoff.

There is no tool execution, state mutation, argument generation, or dependency
graph. Inputs contain only tool names; labels never enter model requests.

Keep the v1 readiness wording unchanged to isolate the effect of adding that
existing judgment. Operational availability labels are diagnostic: the wording
also asks whether use is justified, which may overlap with usefulness. This run
does not test a revised readiness definition.

## Protocol and calibration

Save [cases.json](cases.json) and [protocol.json](protocol.json) before model
evaluation. Use eight development cases across approval, scheduling, inspection
cost, and archive access. Hold out eight cases across supplier costs, travel
times, printer power, and invoice availability. Keep each family in one split.
Held-out inputs and labels were written before collecting development results.

Run each method once per case, alternating method order by case index and keeping
tool order fixed: **32 successful model requests**. No prompt changes, retries,
or extra live threshold searches were used. One earlier sandbox connection
failed without a model response; its request and error are preserved separately.

Sweep the 121 cutoff pairs on saved development scores only. Select one common
usefulness cutoff and one readiness cutoff for the two-score method. Optimize
combined development accuracy, then blocked recommendations and unnecessary
preparation; resolve ties by proximity to 0.6/0.7 and then lower cutoffs.

Freeze **0.3 usefulness / 0.6 readiness** in
[cutoff-selection.json](cutoff-selection.json) before requesting held-out scores.
Both methods get 8/8 development cases correct at these settings. No held-out
retuning occurred.

Calibration matters: at the initial settings, both methods abstained on the
useful `keep_position` choice. Its usefulness was 0.346 for usefulness-only and
0.313 for two-score assessment; the selected common cutoff admits both.
The latter is only 0.013 above the frozen cutoff, illustrating a fragile margin.

## Results

| Split | Method | Correct | Blocked recommendations | Unnecessary preparation | Abstentions | Input tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Development | Usefulness only | 8/8 | 0 | 0 | 1 | 1,769 |
| Development | Usefulness + readiness | 8/8 | 0 | 0 | 1 | 3,650 |
| Held out | Usefulness only | 8/8 | 0 | 0 | 0 | 3,279 |
| Held out | Usefulness + readiness | 8/8 | 0 | 0 | 0 | 6,718 |

The development abstention is correct: archive access is absent and the catalog
has no tool capable of obtaining it. Both methods abstained. All other accepted
recommendations are actual tool names.

Both methods returned identical held-out recommendations:

| State | Recommendation |
| --- | --- |
| Supplier prices and fees supplied without totals | `calculate_total_cost` |
| Verified supplier totals supplied | `buy_from_B` |
| Route distances, speeds, and waits supplied without totals | `calculate_trip_times` |
| Verified journey times supplied | `take_route_B` |
| Printer off | `power_on_printer` |
| Printer already on | `start_print_job` |
| Invoice not downloaded | `download_invoice` |
| Invoice already local | `extract_invoice_total` |

### Unstated calculation needs

The supplier case gives A's price of 49 per item plus one 20-gold delivery fee,
and B's price of 55 with free delivery, for three items. The totals are 167 and
165. The journey case gives distance, speed, and waiting time; the totals are
120 minutes for A and 82 for B.

Neither raw state says a verified calculation is required before acting. Accept
either the better direct choice or the free calculation in raw cases. After
verified results are supplied, accept only the better direct choice.

Both methods preferred calculation for raw inputs and direct action for the
supplied-result inputs. This is evidence of recognizing a useful preparatory
step in these examples. It does not demonstrate successful calculation, correct
tool arguments, or general discovery of mathematical dependencies. The catalog
and state explicitly make a free calculation available.

### Readiness did not change the selected actions

Post-hoc removal of the readiness gate changed no recommendations in either
split. This uses saved scores and requires no additional model calls.

Diagnostic readiness labels matched 10/14 development and 16/20 held-out
judgments at the frozen cutoff. These labels describe operational availability,
independent of whether a tool is worthwhile. The v1 question's reference to
justification makes the distinction imperfect; classification errors are not
direct evidence about the model's internal mechanism.

Usefulness scores were not identical across methods despite identical questions
and state. Maximum absolute differences were 0.0331 in development and 0.0396
held out. Thus the study measures the complete extra-question-plus-gate treatment;
the saved-score gate removal separately checks the gate's contribution. No
run-to-run variance was measured, so the score differences have no established
cause.

## Limits and decision

Prefer the single usefulness judgment for continued experimentation: it matched
recommendations at about half the input-token cost. Preserve readiness as a
testable alternative rather than adding it to the default architecture on this
evidence. No production behavior changed in this run.

These are 16 author-labeled cases on one quantized model, one run per input, and
fixed tool order. Cases are short and explicit; the abstention-only example is
in development, not a new held-out abstention family. The tests do not establish
calibration, statistical significance, robustness to paraphrase or tool order,
execution success, or performance on other models. The numerical cases offer
free calculation, so they do not test choosing when calculation is worth a
nonzero cost. The inspection cases test research cost separately.

A useful follow-up would stress usefulness-only with paraphrases, catalog
permutations, distractor tools, new unavailable-prerequisite cases, and
calculations with costs. These held-out examples are now inspected and should
not be reused as unseen validation for tuned prompts. No such follow-up calls
were made here.

## Audit and reproduction

- [development.json](development.json) and [held-out.json](held-out.json): exact
  requests, raw responses, input labels, scores, timestamps, and elapsed time.
- [summary.json](summary.json): per-method metrics, recommendations, and gate
  removal checks.
- [cutoff-selection.json](cutoff-selection.json): all development candidates,
  frozen selection timestamp, and development-file hash.
- [reproduction.json](reproduction.json): source and fixture hashes, git revision,
  model identifier, and observed server build.
- [server-props.json](server-props.json): observed server configuration.
- [run.py](run.py): experiment driver; its `--help` owns replay instructions.

The model reported `ggml-org/Kev-4B-GGUF:Q4_K_M`; the observed server build was
`b11706-f74e2fa6a`. Model file content was not independently hashed in this run.
All 32 successful responses reported zero output tokens; total input tokens were
15,416. Saved generation properties do not establish their applicability to
typed-question probabilities.

The driver reuses the public assessor for validation and identity mapping. For
usefulness-only requests it removes readiness questions before transmission and
adapts the returned data with internal constant readiness values. Those values
are neither model judgments nor reported scores and do not affect selection.
Both methods' actual wire requests and raw answers are retained and audited.

Replaying consumes additional model calls. Use a new artifact directory and
freeze cutoffs before invoking its held-out phase.
